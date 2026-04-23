import os
import requests
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["WAKEUP_BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
CODESPACE_NAME = os.environ["CODESPACE_NAME"]
ALLOWED_CHAT_ID = int(os.environ["ALLOWED_CHAT_ID"])

GITHUB_API = "https://api.github.com"

def get_codespace_state():
    url = f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("state", "Unknown")
    return None

def start_codespace():
    url = f"{GITHUB_API}/user/codespaces/{CODESPACE_NAME}/start"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    res = requests.post(url, headers=headers)
    return res.status_code

async def wake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("❌ 권한이 없어요.")
        return

    await update.message.reply_text("🔍 코드스페이스 상태 확인 중...")

    state = get_codespace_state()
    if state is None:
        await update.message.reply_text("❌ 코드스페이스 정보를 가져오지 못했어요.")
        return

    if state == "Available":
        await update.message.reply_text(f"✅ 이미 실행 중이에요!\n\n🔗 https://github.com/codespaces")
        return

    await update.message.reply_text(f"💤 현재 상태: {state}\n⏳ 깨우는 중...")
    status = start_codespace()

    if status in [200, 202]:
        await update.message.reply_text(
            "✅ 코드스페이스를 깨웠어요!\n"
            "1~2분 후 아래 링크에서 확인하세요:\n"
            "🔗 https://github.com/codespaces"
        )
    else:
        await update.message.reply_text(f"❌ 실패했어요. (status: {status})")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("❌ 권한이 없어요.")
        return

    state = get_codespace_state()
    emoji = "✅" if state == "Available" else "💤"
    await update.message.reply_text(f"{emoji} 코드스페이스 상태: **{state}**", parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 안녕하세요! 코드스페이스 웨이크업 봇이에요.\n\n"
        "/wake - 코드스페이스 깨우기\n"
        "/status - 현재 상태 확인"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wake", wake))
    app.add_handler(CommandHandler("status", status))
    print("웨이크업 봇 시작!")
    app.run_polling()
