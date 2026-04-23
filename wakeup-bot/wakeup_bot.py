"""
웨이크업 봇 - Render에서 24시간 실행
텔레그램 /wake 명령 → GitHub API로 Codespace 깨우기
"""

import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["WAKEUP_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
CODESPACE_NAME = os.environ["CODESPACE_NAME"]
ALLOWED_USER_IDS = list(map(int, os.environ.get("ALLOWED_USER_IDS", "").split(",")))


def get_codespace_status() -> dict:
    """Codespace 현재 상태 조회"""
    url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    return {}


def start_codespace() -> bool:
    """Codespace 시작 요청"""
    url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    res = requests.post(url, headers=headers)
    return res.status_code in (200, 202)


async def wake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """"/wake 명령 처리"""
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("❌ 권한이 없어요.")
        return

    await update.message.reply_text("🔍 Codespace 상태 확인 중...")

    data = get_codespace_status()
    state = data.get("state", "Unknown")

    if state == "Available":
        await update.message.reply_text(
            f"✅ Codespace가 이미 실행 중이에요!\n\n"
            f"🤖 메인 봇이 꺼져 있다면 Codespace에서 직접 재시작해 주세요."
        )
        return

    if state == "Shutdown":
        await update.message.reply_text(f"💤 현재 상태: `{state}`\n⏳ 깨우는 중...", parse_mode="Markdown")
        success = start_codespace()
        if success:
            await update.message.reply_text(
                "🚀 Codespace 시작 요청 완료!\n\n"
                "⏱ 1~2분 후 메인 봇이 자동으로 켜져요.\n"
                "안 켜지면 `/status` 로 상태 확인해 보세요."
            )
        else:
            await update.message.reply_text("❌ 시작 요청 실패. GitHub Token을 확인해 주세요.")
    else:
        await update.message.reply_text(f"⚠️ 현재 상태: `{state}`\n잠시 후 다시 시도해 주세요.", parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status 명령 처리"""
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("❌ 권한이 없어요.")
        return

    data = get_codespace_status()
    state = data.get("state", "Unknown")
    name = data.get("name", CODESPACE_NAME)
    machine = data.get("machine", {}).get("display_name", "Unknown")

    state_emoji = {
        "Available": "✅",
        "Shutdown": "💤",
        "Starting": "🔄",
        "Rebuilding": "🔧",
    }.get(state, "❓")

    await update.message.reply_text(
        f"{state_emoji} *Codespace 상태*\n\n"
        f"📛 이름: `{name}`\n"
        f"🖥 머신: {machine}\n"
        f"📊 상태: `{state}`",
        parse_mode="Markdown"
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start 명령"""
    await update.message.reply_text(
        "👋 안녕하세요! 웨이크업 봇이에요.\n\n"
        "📋 명령어:\n"
        "/wake — Codespace 깨우기\n"
        "/status — 현재 상태 확인"
    )


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("wake", wake_command))
    app.add_handler(CommandHandler("status", status_command))

    logger.info("웨이크업 봇 시작!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
