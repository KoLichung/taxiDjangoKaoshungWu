from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from telegram.ext import Updater, CommandHandler

def hello(bot, update):
    update.message.reply_text(
        'hello, {}'.format(update.message.from_user.first_name))

@csrf_exempt
def callback(request):
    updater = Updater('5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0')

    updater.dispatcher.add_handler(CommandHandler('hello', hello))

    updater.start_polling()
    updater.idle()