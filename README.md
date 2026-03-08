# Twitter Automated Campaign

> AI-powered Twitter/X content campaign with approval workflow and scheduled publishing.

## Overview

An AI-powered agent skill that manages a structured 30-day Twitter campaign — generating content batches, routing tweets through a human-approval workflow, and publishing on schedule via browser automation.

## Features

- **90-tweet campaign** — 3 posts/day × 30 days across 3 content pillars
- **Approval workflow** — previews sent to Telegram 30 min before publishing; human approves, edits, or skips
- **Browser-based posting** — publishes via browser automation (CDP) to avoid API rate limits
- **Cron scheduling** — 3 daily slots: morning / afternoon / evening
- **Queue management** — tracks status per tweet: `scheduled → pending → approved/skipped → posted`
- **Zello voice notifications** — spoken confirmation after each successful post

## Content Pillars

| Topic | Share |
|-------|-------|
| AI Lead Generation | 40% |
| Spain Real Estate Investment | 35% |
| AI / ChatGPT productivity | 25% |

## Architecture

```
tweet_queue.json (90 tweets) → tweet_actions.py (queue manager)
                             → Telegram preview (30 min before)
                             → Human approval (ok / edit / skip)
                             → post_via_browser.py (CDP publish)
                             → Zello voice notification
```

## Usage

```bash
# Show current pending tweet
python tweet_actions.py pending

# Approve tweet for publishing
python tweet_actions.py approve [id]

# Edit tweet text
python tweet_actions.py edit <id> "new text"

# Skip a tweet
python tweet_actions.py skip [id]

# Publish immediately
python tweet_actions.py post [id]

# Show campaign statistics
python tweet_actions.py status
```

## Environment Variables

```
AUTH_TOKEN=your_twitter_auth_token
CT0=your_twitter_csrf_token
```

## Cron Schedule (Madrid time)

| Slot | Preview | Auto-post |
|------|---------|-----------|
| Morning | 08:00 | 08:30 |
| Afternoon | 14:00 | 14:30 |
| Evening | 20:00 | 20:30 |

## Agent Skill

This is an **OpenClaw agent skill** — the full campaign lifecycle (preview → approve → post → notify) runs autonomously with minimal human input.

---

*Part of the personal brand growth strategy for [@KlincovValery](https://x.com/KlincovValery).*
