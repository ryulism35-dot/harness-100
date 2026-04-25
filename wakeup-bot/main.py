import os
import asyncio
import httpx
import logging
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["WAKEUP_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
CODESPACE_NAME = os.environ["CODESPACE_NAME"]
ALLOWED_CHAT_ID = int(os.environ["ALLOWED_CHAT_ID"])
PORT = int(os.environ.get("PORT", "10000"))

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GITHUB_API = "https://api.github.com"

GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


async def send_message(client, chat_id, text):
    await client.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
    )


async def get_codespace_state(client):
    res = await client.get(
        f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}", headers=GH_HEADERS
    )
    if res.status_code == 200:
        return res.json().get("state", "Unknown")
    logger.warning("GitHub GET failed: %s %s", res.status_code, res.text)
    return None


async def start_codespace(client):
    res = await client.post(
        f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}/start", headers=GH_HEADERS
    )
    return res.status_code


async def handle_update(client, update):
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        await send_message(
            client,
            chat_id,
            "👋 코드스페이스 웨이크업 봇입니다.\n\n"
            "/wake - 코드스페이스 깨우기\n"
            "/status - 현재 상태 확인",
        )
        return

    if text not in ("/wake", "/status"):
        return

    if chat_id != ALLOWED_CHAT_ID:
        await send_message(client, chat_id, "❌ 권한이 없습니다.")
        return

    if text == "/status":
        state = await get_codespace_state(client)
        emoji = "✅" if state == "Available" else "💤"
        await send_message(client, chat_id, f"{emoji} 코드스페이스 상태: {state}")
        return

    if text == "/wake":
        await send_message(client, chat_id, "🔍 상태 확인 중...")
        state = await get_codespace_state(client)

        if state is None:
            await send_message(client, chat_id, "❌ 코드스페이스 정보를 가져오지 못했습니다.")
            return

        if state == "Available":
            await send_message(
                client,
                chat_id,
                "✅ 이미 실행 중입니다.\n🔗 https://github.com/codespaces",
            )
            return

        await send_message(client, chat_id, f"💤 현재 상태: {state}\n⏳ 깨우는 중...")
        status_code = await start_codespace(client)

        if status_code in (200, 202):
            await send_message(
                client,
                chat_id,
                "🚀 깨우기 요청 완료!\n1~2분 후 codespace_bot 에게 메시지를 보내보세요.",
            )
        else:
            await send_message(client, chat_id, f"❌ 실패 (HTTP {status_code})")


async def polling_loop():
    offset = 0
    async with httpx.AsyncClient(timeout=60) as client:
        # clear pending updates on start
        await client.get(f"{TELEGRAM_API}/getUpdates", params={"offset": -1, "timeout": 0})
        logger.info("웨이크업 봇 시작 (polling)")

        while True:
            try:
                res = await client.get(
                    f"{TELEGRAM_API}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                )
                updates = res.json().get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    await handle_update(client, update)
            except Exception as e:
                logger.error("polling 에러: %s", e)
                await asyncio.sleep(5)


async def health(_request):
    return web.Response(text="ok")


async def main():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("HTTP 헬스 서버 포트 %d 바인딩 완료", PORT)

    await polling_loop()


if __name__ == "__main__":
    asyncio.run(main())
