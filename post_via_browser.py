"""
post_via_browser.py — публикует твит через CDP подключение к openclaw браузеру.
Использование: python post_via_browser.py "текст твита"
Возвращает URL или EXIT 1 при ошибке.
"""
import sys
import json
import time
import asyncio
import websockets
import urllib.request

CDP_HTTP = "http://127.0.0.1:18800"

async def get_twitter_tab():
    """Находит вкладку с x.com или открывает новую."""
    with urllib.request.urlopen(f"{CDP_HTTP}/json", timeout=5) as r:
        tabs = json.loads(r.read())
    for tab in tabs:
        url = tab.get("url", "")
        if "x.com" in url or "twitter.com" in url:
            return tab["webSocketDebuggerUrl"], tab["id"]
    return None, None

async def cdp_eval(ws, expression, timeout=10):
    """Выполняет JavaScript в браузере через CDP."""
    msg_id = int(time.time() * 1000) % 999999
    await ws.send(json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expression,
            "awaitPromise": True,
            "returnByValue": True,
            "timeout": timeout * 1000
        }
    }))
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=5)
            resp = json.loads(raw)
            if resp.get("id") == msg_id:
                result = resp.get("result", {})
                exc = result.get("exceptionDetails")
                if exc:
                    raise RuntimeError(exc.get("text", str(exc)))
                val = result.get("result", {})
                return val.get("value")
        except asyncio.TimeoutError:
            continue
    raise TimeoutError("CDP eval timeout")

async def open_tab(target_url):
    """Открывает новую вкладку через CDP."""
    with urllib.request.urlopen(
        f"{CDP_HTTP}/json/new?{urllib.request.quote(target_url)}", timeout=5
    ) as r:
        tab = json.loads(r.read())
    return tab["webSocketDebuggerUrl"], tab["id"]

async def post_tweet(tweet_text):
    # 1. Ищем/открываем вкладку x.com/compose/post
    ws_url, tab_id = await get_twitter_tab()
    
    if not ws_url:
        print("No Twitter tab found, opening new one...")
        ws_url, tab_id = await open_tab("https://x.com/compose/post")
        await asyncio.sleep(3)

    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        # Навигируем к compose
        nav_id = int(time.time() * 1000) % 999998
        await ws.send(json.dumps({
            "id": nav_id,
            "method": "Page.navigate",
            "params": {"url": "https://x.com/compose/post"}
        }))
        await asyncio.sleep(3)

        # Ждём загрузки textarea
        for _ in range(10):
            found = await cdp_eval(ws,
                "!!document.querySelector('[data-testid=\"tweetTextarea_0\"]')"
            )
            if found:
                break
            await asyncio.sleep(1)
        else:
            raise RuntimeError("Tweet textarea not found after 10s")

        # Вводим текст
        escaped = json.dumps(tweet_text)
        await cdp_eval(ws, f"""
            (function() {{
                var el = document.querySelector('[data-testid="tweetTextarea_0"]');
                el.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, {escaped});
                return el.innerText.length;
            }})()
        """)
        await asyncio.sleep(1.5)

        # Жмём кнопку публикации
        clicked = await cdp_eval(ws, """
            (function() {
                var btn = document.querySelector('[data-testid="tweetButton"]');
                if (btn && !btn.disabled) { btn.click(); return 'ok'; }
                var btn2 = document.querySelector('[data-testid="tweetButtonInline"]');
                if (btn2 && !btn2.disabled) { btn2.click(); return 'ok2'; }
                return 'no_button';
            })()
        """)

        if "ok" not in str(clicked):
            raise RuntimeError(f"Publish button not found or disabled: {clicked}")

        await asyncio.sleep(3)
    return "posted"

async def get_latest_tweet_url():
    """Получает URL последнего твита из профиля через API."""
    ws_url, tab_id = await get_twitter_tab()
    if not ws_url:
        return None
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        url = await cdp_eval(ws, """
            (async function() {
                const resp = await fetch(
                    '/i/api/graphql/V7H0Ap3_Hh2FyS75OCDO3Q/UserTweets?variables=' +
                    encodeURIComponent(JSON.stringify({
                        userId:'2765959405',count:1,
                        includePromotedContent:false,withQuickPromoteEligibilityTweetFields:false,
                        withVoice:false,withV2Timeline:true
                    })) + '&features=' + encodeURIComponent(JSON.stringify({
                        rweb_tipjar_consumption_enabled:true,
                        responsive_web_graphql_exclude_directive_enabled:true,
                        verified_phone_label_enabled:false,
                        creator_subscriptions_tweet_preview_api_enabled:true,
                        responsive_web_graphql_timeline_navigation_enabled:true,
                        responsive_web_graphql_skip_user_profile_image_extensions_enabled:false,
                        communities_web_enable_tweet_community_results_fetch:true,
                        c9s_tweet_anatomy_moderator_badge_enabled:true,
                        articles_preview_enabled:true,
                        tweetypie_unmention_optimization_enabled:true,
                        responsive_web_edit_tweet_api_enabled:true,
                        graphql_is_translatable_rweb_tweet_is_translatable_enabled:true,
                        view_counts_everywhere_api_enabled:true,
                        longform_notetweets_consumption_enabled:true,
                        responsive_web_twitter_article_tweet_consumption_enabled:true,
                        tweet_awards_web_tipping_enabled:false,
                        creator_subscriptions_quote_tweet_preview_enabled:false,
                        freedom_of_speech_not_reach_fetch_enabled:true,
                        standardized_nudges_misinfo:true,
                        tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled:true,
                        rweb_video_timestamps_enabled:true,
                        longform_notetweets_rich_text_read_enabled:true,
                        longform_notetweets_inline_media_enabled:true,
                        responsive_web_enhance_cards_enabled:false
                    })),
                    {credentials:'include'}
                );
                const d = await resp.json();
                const entries = d?.data?.user?.result?.timeline_v2?.timeline?.instructions?.find(i=>i.type==='TimelineAddEntries')?.entries || [];
                for (const e of entries) {
                    const tw = e?.content?.itemContent?.tweet_results?.result?.legacy;
                    if (tw?.id_str) return 'https://x.com/KlincovValery/status/' + tw.id_str;
                }
                return null;
            })()
        """, timeout=15)
    return url


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_via_browser.py 'tweet text'")
        sys.exit(1)

    tweet_text = sys.argv[1]
    
    async def main():
        await post_tweet(tweet_text)
        await asyncio.sleep(2)
        # Получаем URL через bird
        import subprocess, os
        env = os.environ.copy()
        # AUTH_TOKEN and CT0 must be set as environment variables
        env["AUTH_TOKEN"] = env.get("AUTH_TOKEN", "")
        env["CT0"] = env.get("CT0", "")
        r = subprocess.run(
            [r"C:\Users\Val\AppData\Roaming\npm\bird.cmd", "user-tweets", "KlincovValery", "--count", "1", "--plain"],
            capture_output=True, text=True, env=env, timeout=10
        )
        for line in r.stdout.split("\n"):
            if "x.com/" in line and "/status/" in line:
                print(line.strip().replace("url: ", "").strip())
                return
        print("posted_no_url")
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
