import os
import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["WAKEUP_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
CODESPACE_NAME = os.environ["CODESPACE_NAME"]
ALLOWED_CHAT_ID = int(os.environ["ALLOWED_CHAT_ID"])

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GITHUB_API = "https://api.github.com"

async def send_message(client, chat_id, text):
    await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

async def get_codespace_state(client):
    url = f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    res = await client.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("state", "Unknown")
    return None

async def start_codespace(client):
    url = f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}/start"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    res = await client.post(url, headers=headers)
    return res.status_code

async def handle_update(client, update):
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        await send_message(client, chat_id,
            "👋 안녕하세요! 코드스페이스 웨이크업 봇이에요.\n\n"
            "/wake - 코드스페이스 깨우기\n"
            "/status - 현재 상태 확인"
        )
        return

    if text not in ["/wake", "/status"]:
        return

    if chat_id != ALLOWED_CHAT_ID:
        await send_message(client, chat_id, "❌ 권한이 없어요.")
        return

    if text == "/status":
        state = await get_codespace_state(client)
        emoji = "✅" if state == "Available" else "💤"
        await send_message(client, chat_id, f"{emoji} 코드스페이스 상태: {state}")
        return

    if text == "/wake":
        await send_message(client, chat_id, "🔍 코드스페이스 상태 확인 중...")
        state = await get_codespace_state(client)

        if state is None:
            await send_message(client, chat_id, "❌ 코드스페이스 정보를 가져오지 못했어요.")
            return

        if state == "Available":
            await send_message(client, chat_id, "✅ 이미 실행 중이에요!\n\n🔗 https://github.com/codespaces")
            return

        await send_message(client, chat_id, f"💤 현재 상태: {state}\n⏳ 깨우는 중...")
        status_code = await start_codespace(client)

        if status_code in [200, 202]:
            await send_message(client, chat_id,
                "✅ 코드스페이스를 깨웠어요!\n"
                "1~2분 후 아래 링크에서 확인하세요:\n"
                "🔗 https://github.com/codespaces"
            )
        else:
            await send_message(client, chat_id, f"❌ 실패했어요. (status: {status_code})")

async def main():
    print("웨이크업 봇 시작!")
    offset = 0

    async with httpx.AsyncClient(timeout=60) as client:
        # 기존 pending 업데이트 제거
        await client.get(f"{TELEGRAM_API}/getUpdates", params={"offset": -1, "timeout": 0})

        while True:
            try:
                res = await client.get(
                    f"{TELEGRAM_API}/getUpdates",
                    params={"offset": offset, "timeout": 30}
                )
                data = res.json()
                updates = data.get("result", [])

                for update in updates:
                    offset = update["update_id"] + 1
                    await handle_update(client, update)

            except Exception as e:
                logging.error(f"에러: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
