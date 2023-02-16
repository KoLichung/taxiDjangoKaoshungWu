from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import logging

# 要有 callback, 要先透過連結設定 webhook：
# https://api.telegram.org/bot5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0/setWebhook?url=https://chinghsien.com/telegram_bot/callback

TOKEN = '5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0'
logger = logging.getLogger(__file__)

@csrf_exempt
def callback(request):
    logger.info(request)
    if request.method == 'POST':
        msg = request.get_json()
       
        chat_id,txt = parse_message(msg)
        if txt == "hi":
            tel_send_message(chat_id,"Hello!!")
        else:
            tel_send_message(chat_id,'from webhook')
       
        return HttpResponse('ok', status=200)
    else:
        return HttpResponse('post only', status=200)

def parse_message(message):
    print("message-->",message)
    logger.info(f'message-->{message}')
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    logger.info(f'chat_id-->{chat_id}')
    logger.info(f'txt-->{txt}')
    return chat_id,txt
 
def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
    r = requests.post(url,json=payload)
    logger.info(r)
    # return r