from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.exceptions import APIException
from modelCore.models import Customer, User, Case, UserCaseShip, CarTeam
from datetime import datetime

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
                on_address = texts[1].replace('上車','').replace(':','').replace('：','')
                off_address = texts[2].replace('下車','').replace(':','').replace('：','')
                
                case = Case()
                case.case_state = 'wait'

                now = datetime.now()
                now_string = now.strftime('%Y%m%d')
                case.create_time = now
                case.carTeam = CarTeam.objects.all().first()

                car_team_number_string = case.carTeam.get_car_team_number_string
                case.case_number = f'{case.carTeam.name} ❤️{now_string}.{car_team_number_string}❤️'
                
                path = 'https://maps.googleapis.com/maps/api/geocode/json?address='
                
                try:
                    onUrl = path+on_address+"&key="+"AIzaSyCrzmspoFyEFYlQyMqhEkt3x5kkY8U3C-Y"
                    logger.info(onUrl)
                    response = requests.get(onUrl)
                    logger.info(response.text)

                    resp_json_payload = response.json()
                    case.on_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
                    case.on_lng = resp_json_payload['results'][0]['geometry']['location']['lng']
                except Exception as e:
                    print(f'on location error {e}')
                    logger.error(f'on location error {e}')
                    tel_send_message(chat_id,'無法辨識上車地點')
                    raise APIException("error")

                try:
                    offUrl = path+off_address+"&key="+"AIzaSyCrzmspoFyEFYlQyMqhEkt3x5kkY8U3C-Y"
                    logger.info(response.text)
                    response = requests.get(offUrl)
                    logger.info(response.text)

                    resp_json_payload = response.json()
                    case.off_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
                    case.off_lng = resp_json_payload['results'][0]['geometry']['location']['lng']
                except Exception as e:
                    print(f'off location error {e}')
                    logger.error(f'off location error {e}')

                try:
                    case.time_memo = texts[3].replace('時間','').replace(':','').replace('：','')
                    case.memo = texts[4].replace('備註','').replace(':','').replace('：','')
                except Exception as e:
                    print(f'case memo error {e}')
                    logger.error(f'case memo error {e}')

                case.save()

                tel_send_message(chat_id,f'{case.case_number}\n派單成功，正在尋找駕駛\n上車：{case.on_address}\n下車：{case.off_address}\n時間：{case.time_memo}\n備註：{case.momo}')

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