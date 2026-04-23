#!/bin/bash
# Codespace 시작 시 자동 실행 스크립트

BOT_DIR="/workspaces/harness-100/telegram-bot"
LOG_DIR="$BOT_DIR"

cd "$BOT_DIR"

# 이미 실행 중이면 스킵
if pgrep -f "restart_server.py" > /dev/null; then
  echo "[autostart] restart_server already running"
else
  echo "[autostart] Starting restart_server.py..."
  nohup python3 "$BOT_DIR/restart_server.py" >> "$LOG_DIR/restart_server.log" 2>&1 &
  echo "[autostart] restart_server PID: $!"
fi

sleep 2

if pgrep -f "codespace_bot.py" > /dev/null; then
  echo "[autostart] codespace_bot already running"
else
  echo "[autostart] Starting codespace_bot.py..."
  nohup python3 "$BOT_DIR/codespace_bot.py" >> "$LOG_DIR/codespace_bot.log" 2>&1 &
  echo "[autostart] codespace_bot PID: $!"
fi

echo "[autostart] Done!"
