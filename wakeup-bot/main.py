import os
import asyncio
import time
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
    "X-GitHub-Api-Version": "2022-11-28",
}

# start API가 안전하게 동작하는 상태들
STARTABLE_STATES = {"Shutdown", "Unknown"}
# 이미 켜져 있거나 켜지는 중인 상태들
ACTIVE_STATES = {"Available", "Starting", "Queued", "Provisioning", "Awaiting", "Rebuilding"}


async def send_message(client, chat_id, text):
    try:
        await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )
    except Exception as e:
        logger.error("sendMessage 실패: %s", e)


async def get_codespace_state(client):
    res = await client.get(
        f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}", headers=GH_HEADERS
    )
    if res.status_code == 200:
        data = res.json()
        return data.get("state", "Unknown"), data.get("pending_operation", False)
    logger.warning("GitHub GET failed: %s %s", res.status_code, res.text)
    return None, None


async def start_codespace(client):
    res = await client.post(
        f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}/start", headers=GH_HEADERS
    )
    detail = ""
    if res.status_code not in (200, 202):
        try:
            detail = res.json().get("message", "") or res.text
        except Exception:
            detail = res.text
        logger.warning("GitHub start failed: %s %s", res.status_code, detail)
    return res.status_code, detail


async def wait_until_ready(client, chat_id):
    """Poll codespace state until Available, then notify user. Runs as background task."""
    # postStartCommand로 autostart.sh가 실행되어 봇이 떠야 진짜 준비 완료
    READY_GRACE_SECONDS = 15
    POLL_INTERVAL = 8
    TIMEOUT = 240  # 4분

    deadline = time.monotonic() + TIMEOUT
    last_state = None
    while time.monotonic() < deadline:
        await asyncio.sleep(POLL_INTERVAL)
        try:
            state, pending = await get_codespace_state(client)
        except Exception as e:
            logger.warning("wait_until_ready 폴링 실패: %s", e)
            continue

        if state and state != last_state:
            logger.info("코드스페이스 상태 전이: %s -> %s (pending=%s)", last_state, state, pending)
            last_state = state

        if state == "Available" and not pending:
            # 봇 프로세스가 polling 시작할 시간 확보
            await asyncio.sleep(READY_GRACE_SECONDS)
            await send_message(
                client,
                chat_id,
                "✅ 코드스페이스 준비 완료!\n📨 이제 codespace_bot 에게 메시지를 보내세요.",
            )
            return

    await send_message(
        client,
        chat_id,
        "⏰ 4분이 지났는데도 Available 상태가 되지 않았습니다.\n/status 로 다시 확인해주세요.",
    )


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
        state, pending = await get_codespace_state(client)
        if state is None:
            await send_message(client, chat_id, "❌ 코드스페이스 정보를 가져오지 못했습니다.")
            return
        emoji = "✅" if state == "Available" else "💤"
        msg = f"{emoji} 코드스페이스 상태: {state}"
        if pending:
            msg += " (작업 진행 중)"
        await send_message(client, chat_id, msg)
        return

    if text == "/wake":
        await send_message(client, chat_id, "🔍 상태 확인 중...")
        state, pending = await get_codespace_state(client)

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

        # 켜지는 중이면 굳이 start 호출하지 말고 대기 안내
        if state in ACTIVE_STATES or pending:
            await send_message(
                client,
                chat_id,
                f"⏳ 현재 상태: {state}\n이미 깨어나는 중입니다. 1~2분 후 /status 로 확인하세요.",
            )
            return

        # 그 외(Shutdown 등)일 때만 start 호출
        await send_message(client, chat_id, f"💤 현재 상태: {state}\n⏳ 깨우는 중...")
        status_code, detail = await start_codespace(client)

        if status_code in (200, 202):
            await send_message(
                client,
                chat_id,
                "🚀 시작 요청을 보냈습니다.\n준비되면 다시 알려드릴게요. (보통 1~2분)",
            )
            asyncio.create_task(wait_until_ready(client, chat_id))
            return

        # 실패 케이스 친절하게
        if status_code == 409:
            msg = (
                f"⚠️ 지금은 깨울 수 없는 상태입니다 (HTTP 409, state={state}).\n"
                f"이유: {detail or '전이 중이거나 다른 작업 진행 중'}\n\n"
                "잠시 후 /status 로 상태를 확인하고 다시 /wake 해주세요."
            )
        elif status_code in (401, 403):
            msg = (
                f"🔐 GitHub 토큰 권한 문제 (HTTP {status_code})\n"
                f"{detail}\n\n"
                "PAT에 codespaces (write) 권한이 있는지 확인하세요."
            )
        elif status_code == 404:
            msg = (
                f"❓ 코드스페이스를 찾을 수 없습니다 (HTTP 404)\n"
                f"CODESPACE_NAME 환경변수 확인: {CODESPACE_NAME}"
            )
        else:
            msg = f"❌ 실패 (HTTP {status_code})\n{detail}"
        await send_message(client, chat_id, msg)


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
