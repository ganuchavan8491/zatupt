import asyncio
import random
import os
from dotenv import load_dotenv
from groq import Groq
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= LOAD ENV =================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

MODEL_ID = "llama3-8b-8192"

# ================= YOUR ORIGINAL PROMPT =================
SYSTEM_PROMPT = """
You are a warm and expert English Teacher. 
Follow this EXACT response structure with double spacing between sections:

(Start with an encouraging opening sentence like: 'That is a great thought!' or 'I like how you expressed that!')

**✅ Your Line:**
"(user's exact original sentence)"

**✍️ Correction:**
"(natural and grammatically correct version)"

**💡 Note:**
(Briefly explain WHY the change was made, like a teacher. Focus on 1 key grammar rule. Be friendly like a peer.)

**💬 My Reply:**
(Answer the user's content naturally + ask ONE engaging follow-up question to keep the chat moving.)

Rules:
- Keep the tone peer-like, witty, and supportive.
- Use bold headers as shown above.
- Always add empty lines between sections for readability.
"""

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 I am your English Teacher Bot!\n\nSend any sentence ✍️"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=constants.ChatAction.TYPING
    )

    await asyncio.sleep(random.uniform(1, 2))

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )

        reply = completion.choices[0].message.content
        await update.message.reply_text(reply, parse_mode="Markdown")

    except Exception as e:
        print("Groq Error:", e)
        await update.message.reply_text("❌ API Error, try again later")

# ================= MAIN =================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🚀 Teacher Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()