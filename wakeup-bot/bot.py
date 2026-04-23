import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
CODESPACE_NAME = os.environ["CODESPACE_NAME"]
ALLOWED_CHAT_ID = int(os.environ["ALLOWED_CHAT_ID"])

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_codespace_state():
    url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json().get("state", "Unknown")
    return f"Error {res.status_code}"

def start_codespace():
    url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    res = requests.post(url, headers=HEADERS)
    return res.status_code

async def wake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("❌ 권한 없음")
        return

    await update.message.reply_text("🔍 코드스페이스 상태 확인 중...")
    state = get_codespace_state()

    if state == "Available":
        await update.message.reply_text("✅ 코드스페이스 이미 실행 중이에요!")
    elif state in ("Shutdown", "Stopped"):
        await update.message.reply_text(f"😴 현재 상태: {state}\n⏳ 깨우는 중...")
        code = start_codespace()
        if code == 202:
            await update.message.reply_text("🚀 깨우기 요청 완료!\n1~2분 후 코드스페이스가 켜져요.")
        else:
            await update.message.reply_text(f"❌ 실패 (HTTP {code})")
    else:
        await update.message.reply_text(f"현재 상태: {state}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("❌ 권한 없음")
        return
    state = get_codespace_state()
    await update.message.reply_text(f"📊 코드스페이스 상태: `{state}`", parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 웨이크업 봇이에요!\n\n"
        "/wake - 코드스페이스 깨우기\n"
        "/status - 현재 상태 확인"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wake", wake))
    app.add_handler(CommandHandler("status", status))
    print("웨이크업 봇 시작!")
    app.run_polling()
