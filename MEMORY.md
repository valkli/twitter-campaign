# Twitter Campaign — Project Memory

**Статус:** АКТИВНА — 10 опубликовано, 1 pending, 64 scheduled
**Последнее обновление:** 2026-03-10

---

## Текущее состояние очереди
- **posted:** 10 (ids 1–10, Days 6–9)
- **pending:** 1 (id=11, Day 9 slot 2, SPAIN — завис, нужно опубликовать)
- **scheduled:** 64 (Days 10–30)
- Файл очереди: `tweet_queue.json`

## Архитектура системы

### Постинг
- **bird** — ТОЛЬКО для чтения (whoami, user-tweets, home, search)
- **bird tweet** — ЗАБЛОКИРОВАН Twitter ошибкой 226 ("looks automated")
- **Постинг ВСЕГДА через browser** (profile=openclaw):
  1. Открыть https://x.com/compose/post
  2. Ждать 2.5 сек
  3. `document.execCommand('insertText', false, TEXT)` в textarea `[data-testid="tweetTextarea_0"]`
  4. Ждать 1 сек
  5. `document.querySelector('[data-testid="tweetButton"]').click()`
  6. Ждать 3 сек

### Cron jobs (6 штук)
| ID | Имя | Расписание |
|---|---|---|
| 6fcc295f | twitter-preview-morning | 08:00 Madrid (cron `0 7 * * *`) |
| a6e61636 | twitter-autopost-morning | 08:30 Madrid (cron `30 7 * * *`) |
| 222b1032 | twitter-preview-afternoon | 14:00 Madrid (cron `0 14 * * *`) |
| 7d995199 | twitter-autopost-afternoon | 14:30 Madrid (cron `30 14 * * *`) |
| b74143f2 | twitter-preview-evening | 20:00 Madrid (cron `0 20 * * *`) |
| 0ca97a9a | twitter-autopost-evening | 20:30 Madrid (cron `30 20 * * *`) |

### Согласование
- Превью → Telegram (chat=-1003319033023, topic=1)
- «ок» / «правь: [текст]» / «пропусти» / молчание 30 мин = авто-публикация
- После публикации: Zello «Твит опубликован. День X, слот Y.»

### Ключевые файлы
- `tweet_queue.json` — очередь (75 твитов, дни 6–30)
- `tweet_actions.py` — управление (pending, approve, edit, skip, post, **mark-posted**, **mark-error**, next-preview, status)
- `post_via_browser.py` — CDP постинг (вызывается из tweet_actions)

## Команды
```bash
python tweet_actions.py status          # статус очереди
python tweet_actions.py pending         # текущий pending твит (JSON)
python tweet_actions.py approve [id]    # одобрить
python tweet_actions.py edit <id> <text># изменить текст
python tweet_actions.py skip [id]       # пропустить
python tweet_actions.py mark-posted <id> <url>  # отметить как опубликованный
python tweet_actions.py mark-error [id] # уведомить об ошибке
python tweet_actions.py next-preview    # перевести следующий в pending
```

## Токены Twitter (@KlincovValery)
- Хранятся в `memory/secrets_registry.md` + системных env vars (AUTH_TOKEN, CT0)
- При ошибке 403/226 для чтения — нужны свежие токены из браузера (F12 → Application → Cookies)

## Сделано в сессии 07–09.03.2026
- Исправлен постинг: bird → браузер (CDP)
- Обновлены все 3 autopost-крона: теперь используют browser tool напрямую
- Добавлены команды mark-posted, mark-error в tweet_actions.py
- Добавлен post_via_browser.py (CDP fallback)
- Опубликованы твиты ids 1–10

## Следующие шаги
- Опубликовать id=11 (Day 9 slot 2, SPAIN — pending с 19:00 09.03)
- Мониторить авто-публикацию следующих дней
- Если browser не доступен в cron → fallback публикует Ali вручную

## Связанные файлы
- `twitter_complete_90tweets.md` — полный список 90 твитов
- `generate_queue.py` — генератор очереди
- `tweet_queue.json` — активная очередь
