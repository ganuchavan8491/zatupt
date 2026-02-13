import asyncio
import random
import os
import http.server
import socketserver
import threading
from groq import Groq
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- RENDER HEALTH CHECK SERVER ---
# Render free tier needs a port to be bound to stay alive
def start_health_check():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"📡 Health check server running on port {port}")
        httpd.serve_forever()

# --- CONFIG ---
TELEGRAM_TOKEN = "8565416877:AAE05O7hcuquFtUKpiB0Ej4gMEvozAntjmo"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
MODEL_ID = "llama-3.3-70b-versatile"

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

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    intro = (
        "That sounds like a fantastic plan! 🌟\n\n"
        "I'll be your **'Friendly Editor'**. I won't just correct you; I'll explain *why* so you can improve every day.\n\n"
        "**How we’ll do this:**\n"
        "✅ **Your Line:** What you sent.\n"
        "✍️ **Correction:** The natural way.\n"
        "💡 **Note:** The grammar rule explained simply.\n"
        "💬 **My Reply:** Our actual conversation.\n\n"
        "Ready? Tell me, what's on your mind today?"
    )
    await update.message.reply_text(intro, parse_mode='Markdown')

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if not user_text: return

    # "Typing..." status
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING)
    
    # Real-chat delay
    await asyncio.sleep(random.uniform(1.5, 3.0))

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        
        bot_response = completion.choices[0].message.content
        await update.message.reply_text(bot_response, parse_mode='Markdown')

    except Exception as e:
        print("Groq Error:", e)
        await update.message.reply_text(f"❌ Groq Error: {e}")

# --- MAIN ---

def main():
    # Start the background health check for Render
    threading.Thread(target=start_health_check, daemon=True).start()

    # Build the Application
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🚀 Teacher Bot is LIVE and Ready for Deployment!")
    app.run_polling()

if __name__ == "__main__":
    main()