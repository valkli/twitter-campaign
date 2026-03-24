# Twitter Campaign — Project Memory

**Статус:** АКТИВНА — 44 posted, 9 skipped (stale), 22 scheduled
**Последнее обновление:** 2026-03-23

---

## Текущее состояние очереди
- **posted:** 44 (Days 6–19)
- **skipped:** 9 (Days 20-23, застряли в pending из-за бага message tool)
- **scheduled:** 22 (Days 23-30, следующий: id=54, Day 23 slot 3 AI)
- Файл очереди: `tweet_queue.json`

## Архитектура системы (v2 — 23.03.2026)

### Постинг
- **bird** — ТОЛЬКО для чтения (whoami, user-tweets, home, search)
- **bird tweet** — ЗАБЛОКИРОВАН Twitter ошибкой 226 ("looks automated")
- **Постинг ВСЕГДА через browser** (profile=openclaw):
  1. Открыть https://x.com/compose/post
  2. Ждать 2.5 сек
  3. `document.execCommand('insertText', false, TEXT)` в textarea
  4. Ждать 1 сек
  5. Нажать кнопку Post
  6. Ждать 3 сек

### Динамические кроны (v2 — 2 вместо 6)
**Архитектура:** 2 динамических `at` крона которые пересоздают друг друга.
В любой момент времени активен **только 1 крон**.

```
twitter-preview (at: slot - 10мин) → шлёт на согласование → создаёт twitter-publish
twitter-publish (at: slot) → публикует → создаёт twitter-preview для следующего слота
```

- **Согласование:** 10 минут (было 30)
- **Слоты:** 08:00, 14:00, 20:00 Madrid (07:00, 13:00, 19:00 UTC)
- **Delivery:** announce (НЕ message tool — тот падает в изолированных сессиях)
- **deleteAfterRun:** true для обоих
- **Модель:** Sonnet (дешевле и быстрее для рутинной работы)
- **Текущий активный:** twitter-preview на 2026-03-24T18:50:00Z (завтра 19:50 Madrid)
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
