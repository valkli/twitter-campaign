#!/bin/bash
# Post tweet with Telegram notification
# Usage: ./post_with_notification.sh "tweet text" "notification title"

TWEET_TEXT="$1"
NOTIFICATION_TITLE="$2"

# Post tweet via bird CLI
echo "Posting: $NOTIFICATION_TITLE"
bird tweet "$TWEET_TEXT"

# Send Telegram notification
curl -s -X POST "https://api.telegram.org/bot/sendMessage" \
  -d "chat_id=170488995" \
  -d "text=Posted: $NOTIFICATION_TITLE" \
  > /dev/null

echo "Done"
