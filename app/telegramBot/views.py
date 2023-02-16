from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

# 要有 callback, 要先透過連結設定 webhook：
# https://api.telegram.org/bot5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0/setWebhook?url=https://chinghsien.com/telegram_bot/callback

@csrf_exempt
def callback(request):
    application = ApplicationBuilder().token('5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0').build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()