#!/usr/bin/env bash
# telegram_notify.sh — Send a Telegram message to Oscar
# Usage: telegram_notify.sh "message text"

BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# No-op if either is unset (allows local runs without notifications)
[[ -z "$BOT_TOKEN" || -z "$CHAT_ID" ]] && exit 0

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  --data-urlencode "text=$1" > /dev/null 2>&1 || true
