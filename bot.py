import asyncio
import random
import os
import http.server
import socketserver
import threading
from dotenv import load_dotenv
from groq import Groq
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= LOAD ENV =================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 8080))

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("❌ Missing API keys! Check your .env file.")

# ================= GROQ CLIENT =================
client = Groq(api_key=GROQ_API_KEY)
MODEL_ID = "llama3-8b-8192"

# ================= HEALTH SERVER (FOR RENDER) =================
def start_health_check():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"📡 Health server running on port {PORT}")
        httpd.serve_forever()

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🔥 Bot is LIVE!\n\n"
        "Send me any message and I will reply using AI 🤖"
    )
    await update.message.reply_text(msg)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    if not user_text:
        return

    # typing effect
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=constants.ChatAction.TYPING
    )

    await asyncio.sleep(random.uniform(1, 2))

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )

        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        print("❌ Groq Error:", e)
        await update.message.reply_text("❌ API Error, try again later")

# ================= MAIN =================
def main():
    # start health server (for Render)
    threading.Thread(target=start_health_check, daemon=True).start()

    # telegram app
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()