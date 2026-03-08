"""
tweet_actions.py - управление очередью твитов
Использование:
  python tweet_actions.py pending           - показать текущий pending твит
  python tweet_actions.py approve [id]      - одобрить pending твит (или конкретный id)
  python tweet_actions.py edit <id> <text>  - изменить текст твита
  python tweet_actions.py skip [id]         - пропустить твит
  python tweet_actions.py post [id]         - опубликовать через bird
  python tweet_actions.py next-preview      - показать следующий твит для превью (по расписанию)
  python tweet_actions.py status            - статистика очереди
"""
import json
import sys
import subprocess
import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path

# Путь к очереди нотификаций Zello (бот читает, мы пишем)
ZELLO_QUEUE = Path(r"C:\Users\Val\.openclaw\skills\zello\notify_queue.json")

def notify_zello(message: str):
    """Добавляет сообщение в очередь нотификаций Zello.
    Бот zello_skill.py читает очередь и отправляет голосом через уже открытое соединение.
    """
    try:
        if ZELLO_QUEUE.exists():
            existing = json.loads(ZELLO_QUEUE.read_text(encoding="utf-8"))
        else:
            existing = []
        existing.append(message)
        ZELLO_QUEUE.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
        print(f"[Zello] Queued: {message[:60]}")
    except Exception as e:
        print(f"[Zello] WARN: {e}")

QUEUE_FILE = Path(__file__).parent / "tweet_queue.json"

def load_queue():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def now_utc():
    return datetime.now(timezone.utc)

def get_pending(queue):
    return [t for t in queue if t["status"] == "pending"]

def get_scheduled_due(queue):
    now = now_utc()
    due = []
    for t in queue:
        if t["status"] == "scheduled":
            sched = datetime.fromisoformat(t["scheduled_utc"].replace("Z", "+00:00"))
            if sched <= now:
                due.append(t)
    return due

BIRD_CMD = r"C:\Users\Val\AppData\Roaming\npm\bird.cmd"
BIRD_AUTH = os.environ.get("AUTH_TOKEN", "")  # Set AUTH_TOKEN env variable
BIRD_CT0  = os.environ.get("CT0", "")          # Set CT0 env variable

def post_tweet_via_browser(tweet_text):
    """
    Публикует твит через CDP (openclaw browser).
    Работает даже когда bird API блокируется ошибкой 226.
    """
    browser_script = Path(__file__).parent / "post_via_browser.py"
    try:
        result = subprocess.run(
            [sys.executable, str(browser_script), tweet_text],
            capture_output=True, text=True, timeout=45
        )
        output = result.stdout.strip()
        if result.returncode == 0 and output:
            return True, output.split("\n")[-1].strip()
        err = (result.stderr + result.stdout).strip()
        return False, err[:200]
    except Exception as e:
        return False, str(e)


def post_tweet(tweet_text):
    """Публикует твит: сначала пробует bird API, если 226 — через браузер."""
    env = os.environ.copy()
    env["AUTH_TOKEN"] = BIRD_AUTH
    env["CT0"] = BIRD_CT0
    result = subprocess.run(
        [BIRD_CMD, "tweet", tweet_text],
        capture_output=True, text=True, env=env, timeout=20
    )
    if result.returncode == 0:
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            if "x.com/" in line or "twitter.com/" in line:
                parts = line.split()
                for p in parts:
                    if "x.com/" in p or "twitter.com/" in p:
                        return True, p.strip()
        return True, "posted (url not found)"
    else:
        err = result.stderr.strip()
        if "226" in err or "automated" in err.lower() or "403" in err:
            print(f"[post_tweet] bird API blocked (226), switching to browser...")
            return post_tweet_via_browser(tweet_text)
        return False, err

def cmd_pending():
    queue = load_queue()
    pending = get_pending(queue)
    if not pending:
        print("NO_PENDING")
        return
    t = pending[0]
    print(json.dumps(t, ensure_ascii=False))

def cmd_approve(tweet_id=None):
    queue = load_queue()
    if tweet_id:
        targets = [t for t in queue if t["id"] == int(tweet_id) and t["status"] in ("pending", "scheduled")]
    else:
        targets = get_pending(queue)
    
    if not targets:
        print("ERROR: No pending tweet found")
        return
    
    t = targets[0]
    t["status"] = "approved"
    save_queue(queue)
    print(f"OK: Tweet id={t['id']} approved")

def cmd_edit(tweet_id, new_text):
    queue = load_queue()
    targets = [t for t in queue if t["id"] == int(tweet_id)]
    if not targets:
        print(f"ERROR: Tweet id={tweet_id} not found")
        return
    t = targets[0]
    t["approved_text"] = new_text
    t["status"] = "edited"
    save_queue(queue)
    print(f"OK: Tweet id={t['id']} edited")

def cmd_skip(tweet_id=None):
    queue = load_queue()
    if tweet_id:
        targets = [t for t in queue if t["id"] == int(tweet_id)]
    else:
        targets = get_pending(queue)
    if not targets:
        print("ERROR: No tweet found")
        return
    t = targets[0]
    t["status"] = "skipped"
    save_queue(queue)
    print(f"OK: Tweet id={t['id']} skipped")

def cmd_post(tweet_id=None):
    queue = load_queue()
    if tweet_id:
        targets = [t for t in queue if t["id"] == int(tweet_id) and t["status"] in ("pending", "approved", "edited", "scheduled")]
    else:
        # Берём первый approved/edited, или первый pending с истёкшим временем ожидания
        targets = [t for t in queue if t["status"] in ("approved", "edited")]
        if not targets:
            pending = get_pending(queue)
            for t in pending:
                if t["pending_since"]:
                    since = datetime.fromisoformat(t["pending_since"].replace("Z", "+00:00"))
                    elapsed = (now_utc() - since).total_seconds()
                    if elapsed >= 1800:  # 30 минут
                        targets.append(t)
                        break
    
    if not targets:
        print("NO_ACTION: No tweet ready to post")
        return
    
    t = targets[0]
    text_to_post = t.get("approved_text") or t["text"]
    
    ok, result = post_tweet(text_to_post)
    if ok:
        t["status"] = "posted"
        t["posted_at"] = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
        t["tweet_url"] = result
        save_queue(queue)
        print(f"POSTED: id={t['id']} day={t['day']} slot={t['slot']}")
        print(f"URL: {result}")
        print(f"TEXT: {text_to_post[:100]}")
        # Zello: короткое уведомление
        notify_zello(f"Твит опубликован. День {t['day']}, слот {t['slot']}.")
    else:
        print(f"ERROR: Failed to post - {result}")
        notify_zello(f"Ошибка твита. День {t['day']}, слот {t['slot']}.")

def cmd_next_preview():
    """Показывает следующий твит по расписанию для отправки на согласование"""
    queue = load_queue()
    scheduled = [t for t in queue if t["status"] == "scheduled"]
    if not scheduled:
        print("NO_MORE: Queue empty")
        return
    # Следующий по времени
    t = min(scheduled, key=lambda x: x["scheduled_utc"])
    # Помечаем как pending
    t["status"] = "pending"
    t["pending_since"] = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    save_queue(queue)
    print(json.dumps(t, ensure_ascii=False))

def cmd_status():
    queue = load_queue()
    by_status = {}
    for t in queue:
        by_status[t["status"]] = by_status.get(t["status"], 0) + 1
    print("=== Tweet Queue Status ===")
    for s, c in sorted(by_status.items()):
        print(f"  {s}: {c}")
    print(f"  TOTAL: {len(queue)}")
    
    pending = get_pending(queue)
    if pending:
        t = pending[0]
        print(f"\nCurrent PENDING (id={t['id']}):")
        print(f"  Day {t['day']} slot {t['slot']} | {t['topic']}")
        print(f"  Pending since: {t['pending_since']}")
        print(f"  Text: {t['text'][:80]}...")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    
    cmd = args[0]
    if cmd == "pending":
        cmd_pending()
    elif cmd == "approve":
        cmd_approve(args[1] if len(args) > 1 else None)
    elif cmd == "edit" and len(args) >= 3:
        cmd_edit(args[1], " ".join(args[2:]))
    elif cmd == "skip":
        cmd_skip(args[1] if len(args) > 1 else None)
    elif cmd == "post":
        cmd_post(args[1] if len(args) > 1 else None)
    elif cmd == "next-preview":
        cmd_next_preview()
    elif cmd == "status":
        cmd_status()
    elif cmd == "mark-posted" and len(args) >= 2:
        # mark-posted <id> [url]
        tweet_id = int(args[1])
        url = args[2] if len(args) > 2 else "posted"
        queue = load_queue()
        for t in queue:
            if t["id"] == tweet_id:
                t["status"] = "posted"
                t["posted_at"] = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
                t["tweet_url"] = url
                save_queue(queue)
                notify_zello(f"Твит опубликован. День {t['day']}, слот {t['slot']}.")
                print(f"OK: id={tweet_id} marked as posted, url={url}")
                break
        else:
            print(f"ERROR: tweet id={tweet_id} not found")
    elif cmd == "mark-error" and len(args) >= 1:
        # mark-error <id>
        tweet_id = int(args[1]) if len(args) > 1 else None
        queue = load_queue()
        pending = [t for t in queue if t["status"] in ("pending", "approved", "edited")]
        if tweet_id:
            pending = [t for t in pending if t["id"] == tweet_id]
        if pending:
            t = pending[0]
            notify_zello(f"Ошибка твита. День {t['day']}, слот {t['slot']}.")
            print(f"OK: error notification sent for id={t['id']}")
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
