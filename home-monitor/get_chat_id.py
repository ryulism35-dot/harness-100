#!/usr/bin/env python3
"""
부모의 Telegram chat_id를 얻기 위한 헬퍼 스크립트.
봇에게 메시지를 보내면 chat_id를 출력합니다.
"""

import os
import sys
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or input("Telegram 봇 토큰 입력: ").strip()

print("\n1. Telegram에서 본인의 봇(@your_bot_name)에게 /start 메시지를 보내세요.")
print("2. 그 후 Enter를 누르세요...\n")
input()

resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
data = resp.json()

if not data.get("ok") or not data.get("result"):
    print("메시지를 받지 못했습니다. 봇에게 /start 를 보낸 후 다시 실행하세요.")
    sys.exit(1)

seen = set()
for update in data["result"]:
    msg = update.get("message") or update.get("channel_post")
    if not msg:
        continue
    chat = msg["chat"]
    chat_id = chat["id"]
    if chat_id in seen:
        continue
    seen.add(chat_id)
    name = chat.get("first_name") or chat.get("title") or "알 수 없음"
    print(f"이름: {name}  |  chat_id: {chat_id}")

print("\n위 chat_id를 메모해 두세요. 아이들 폰 설정에 사용됩니다.")
