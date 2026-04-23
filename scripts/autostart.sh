#!/bin/bash
# Codespace 시작 시 자동 실행 스크립트

BOT_DIR="/workspaces/harness-100/telegram-bot"
LOG_FILE="$BOT_DIR/codespace_bot.log"

cd "$BOT_DIR"

if pgrep -f "codespace_bot.py" > /dev/null; then
  echo "[autostart] codespace_bot already running"
else
  echo "[autostart] Starting codespace_bot.py..."
  nohup python3 "$BOT_DIR/codespace_bot.py" >> "$LOG_FILE" 2>&1 &
  echo "[autostart] codespace_bot PID: $!"
fi

echo "[autostart] Done!"
