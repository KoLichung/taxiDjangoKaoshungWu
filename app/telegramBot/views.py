from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import logging
import json

# 要有 callback, 要先透過連結設定 webhook：
# https://api.telegram.org/bot5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0/setWebhook?url=https://chinghsien.com/telegram_bot/callback

TOKEN = '5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0'
logger = logging.getLogger(__file__)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        logger.info(request.body)
        
        message = json.loads(request.body)
        chat_id,txt = parse_message(message)
        if txt == "hi":
            tel_send_message(chat_id,"Hello!!")
        else:
            texts = txt.split('\n')

            if texts[0] == '派單':
                tel_send_message(chat_id,'這是派單!')
            elif texts[0] == '預約單':
                tel_send_message(chat_id,'這是預約單!')
            elif texts[0] == '取消':
                tel_send_message(chat_id,'這是取消單!')
            else:
                tel_send_message(chat_id,'動作不明確!')
       
        return HttpResponse('ok', status=200)
    else:
        return HttpResponse('post only', status=200)

def parse_message(message):
    print("message-->",message)
    logger.info(f'message-->{message}')
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']

    # print("chat_id-->", chat_id)
    # print("txt-->", txt)
    # logger.info(f'chat_id-->{chat_id}')
    # logger.info(f'txt-->{txt}')
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


#格式
# 派單
# 上車:港源街 109 
# 下車:彰化市火車站 
# 時間:XXXX 
# 備註:XXXX

# 取消
# 上車:港源街 109

# 取消
# 極致❤️20230204.0001❤️ 