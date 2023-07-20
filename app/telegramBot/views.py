from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.exceptions import APIException
from modelCore.models import Customer, User, Case, UserCaseShip, CarTeam, UserCarTeamShip
from datetime import datetime

import requests
import logging
import json
from django.conf import settings

# 要有 callback, 要先透過連結設定 webhook：
# https://api.telegram.org/bot5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0/setWebhook?url=https://chinghsien.com/telegram_bot/callback

TOKEN = '5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0'
logger = logging.getLogger(__file__)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        logger.info(json.loads(request.body))
        
        message = json.loads(request.body)
        chat_id,txt = parse_message(message)

        if txt == "hi":
            if User.objects.filter(telegram_id=chat_id).count() != 0:
                user = User.objects.filter(telegram_id=chat_id).first()
                tel_send_message(chat_id, f"Hello!! {user.name}({user.nick_name})")
            else:
                tel_send_message(chat_id,"Hello!!")
        elif txt == 'error':
            tel_send_message(chat_id,"訊息有誤，請聯繫管理員!!")
        else:
            texts = txt.split('\n')
            
            if User.objects.filter(telegram_id=chat_id).count() != 0:
                user = User.objects.filter(telegram_id=chat_id).first()
                if user.is_telegram_bot_enable:
                    try:
                        # 派單
                        if '上車：' in texts[0] or '上車:' in texts[0] or '上：' in texts[0] or '上:' in texts[0]:
                            case = Case()
                            case.case_state = 'wait'

                            for index, text in enumerate(texts):

                                path = 'https://maps.googleapis.com/maps/api/geocode/json?address='

                                if '上車：' in text or '上車:' in text or '上：' in text or '上:' in text:
                                    on_address = text.replace('上車：','').replace('上車:','').replace('上：','').replace('上:','')

                                    try:
                                        onUrl = path+on_address+"&key="+settings.API_KEY
                                        # logger.info(onUrl)
                                        response = requests.get(onUrl)
                                        # logger.info(response.text)

                                        resp_json_payload = response.json()
                                        on_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
                                        on_lng = resp_json_payload['results'][0]['geometry']['location']['lng']
                                    except Exception as e:
                                        print(f'on location error {e}')
                                        logger.error(f'on location error {e}')
                                        tel_send_message(chat_id,'無法辨識上車地點')
                                        raise APIException("error")
                                    
                                    case.on_address = on_address
                                    case.on_lat = on_lat
                                    case.on_lng = on_lng

                                    now = datetime.now()
                                    now_string = now.strftime('%Y%m%d')
                                    case.create_time = now

                                    try:
                                        carTeam = UserCarTeamShip.objects.filter(user=user).order_by('id').first().carTeam
                                        carTeam.day_case_count = carTeam.day_case_count + 1
                                        carTeam.save()

                                        case.carTeam = carTeam
                                        car_team_number_string = carTeam.get_car_team_number_string
                                        case.case_number = f'{case.carTeam.name} ❤️{now_string}.{car_team_number_string}❤️'
                                    except:
                                        tel_send_message(chat_id,'派單者可能未指定車隊')
                                        raise APIException("error")
                                    
                                    case.telegram_id = chat_id
                                    # case.save()

                                if '下車' in text:
                                    off_address = text.replace('下車','').replace(':','').replace('：','')
                                    case.off_address = off_address
                            
                                    try:
                                        offUrl = path+off_address+"&key="+settings.API_KEY
                                        # logger.info(response.text)
                                        response = requests.get(offUrl)
                                        # logger.info(response.text)

                                        resp_json_payload = response.json()
                                        case.off_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
                                        case.off_lng = resp_json_payload['results'][0]['geometry']['location']['lng']
                                    except Exception as e:
                                        print(f'off location error {e}')
                                        logger.error(f'off location error {e}')

                                    # if case.on_lat != None:
                                    #     case.save()

                                if '時間' in text:
                                    case.time_memo = text.replace('時間','').replace(':','').replace('：','')
                                    # if case.on_lat != None:
                                    #     case.save()
                                
                                if '備註' in text:
                                    case.memo = text.replace('備註','').replace(':','').replace('：','')
                                    # if case.on_lat != None:
                                    #     case.save()
                            
                            if case.on_lat != None:
                                case.save()
                                tel_send_message(chat_id,f'{case.case_number}\n派單成功，正在尋找駕駛\n上車：{case.on_address}\n下車：{case.off_address}\n時間：{case.time_memo}\n備註：{case.memo}')
                            else:
                                tel_send_message(chat_id,'派單失敗,無法辨識上車地點')
                                
                        elif texts[0] == '預約單':
                            # 預約單功能尚未完成
                            tel_send_message(chat_id,'這是預約單，預約單功能尚未完成!')
                        elif texts[0] == '取消':
                            # tel_send_message(chat_id,'這是取消單!')
                            if "❤" in texts[1]:
                                # 單號取消
                                if '-' in texts[1]:
                                    theIndex = texts[1].index('-')
                                    case_id = texts[1][:theIndex]
                                else:
                                    case_id = texts[1]

                                if Case.objects.filter(case_number=case_id).count() != 0:
                                    case = Case.objects.filter(case_number=case_id).first()
                                    if case.case_state != 'canceled':
                                        case.case_state = 'canceled'
                                        case.save()
                                        
                                        if case.user != None:
                                            car_teams_string = case.user.car_teams_string()

                                            # 調整 user 的 is_on_task, is_asking 狀態
                                            user = case.user
                                            user.is_on_task = False
                                            user.is_asking = False
                                            user.save()
                                        else:
                                            car_teams_string=''

                                             # 調整 user 的 is_asking 狀態
                                            ship = UserCaseShip.objects.filter(case=case).first()
                                            user = ship.user
                                            user.is_asking = False
                                            user.save()

                                        # 刪除詢問中 ship
                                        UserCaseShip.objects.filter(case=case).delete()

                                        tel_send_message(chat_id,f'{case.case_number}-{car_teams_string}\n--------------------------\n取消成功\n--------------------------\n上車:{case.on_address}')
                                    else:
                                        if case.user != None:
                                            car_teams_string = case.user.car_teams_string()
                                        else:
                                            car_teams_string=''
                                        tel_send_message(chat_id,f'{case.case_number}-{car_teams_string}\n--------------------------\n此單已被取消\n--------------------------\n上車:{case.on_address}')
                                else:
                                    tel_send_message(chat_id,f'取消失敗，找不到此單號')
                            elif "上車" in texts[1]:
                                # 依上車位置取消
                                on_address = texts[1].replace('上車','').replace(':','').replace('：','')

                                if Case.objects.filter(on_address=on_address).count() != 0:
                                    case = Case.objects.filter(on_address=on_address).order_by('-id').first()
                                    if case.case_state != 'canceled':
                                        case.case_state = 'canceled'
                                        case.save()
                                        UserCaseShip.objects.filter(case=case).delete()

                                        if case.user != None:
                                            car_teams_string = case.user.car_teams_string()
                                        else:
                                            car_teams_string=''
                                        tel_send_message(chat_id,f'{case.case_number}-{car_teams_string}\n--------------------------\n取消成功\n--------------------------\n上車:{case.on_address}')
                                    else:
                                        if case.user != None:
                                            car_teams_string = case.user.car_teams_string()
                                        else:
                                            car_teams_string=''
                                        tel_send_message(chat_id,f'{case.case_number}-{car_teams_string}\n--------------------------\n此單已被取消\n--------------------------\n上車:{case.on_address}')
                                else:
                                    tel_send_message(chat_id,f'取消失敗，找不到此上車位置的單')
                        else:
                            tel_send_message(chat_id,'動作不明確!')
                    except Exception as e: 
                        print(e)
                        logger.error(e)
                        tel_send_message(chat_id,'格式錯誤或內容錯誤!')
                else:
                    tel_send_message(chat_id, "您沒有派單的權限~")
            elif texts[0] == '綁定':
                # 用 user phone 綁定
                try:
                    phone = texts[1]
                    if User.objects.filter(phone=phone).count()!=0:
                        user = User.objects.filter(phone=phone).first()
                        user.telegram_id = chat_id
                        user.save()
                        tel_send_message(chat_id, f"綁定成功!!{user.name}({user.nick_name})")
                    else:
                        tel_send_message(chat_id, f"找不到這個使用者, 無法綁定")
                except:
                    tel_send_message(chat_id, "無法綁定，請檢查格式是否正確~")
            else:
                tel_send_message(chat_id, "請先進行身份綁定~")
                

        return HttpResponse('ok', status=200)
    else:
        return HttpResponse('post only', status=200)

def parse_message(message):
    print("message-->",message)
    logger.info(f'message---------->{message}')
    # try:
    #     chat_id = message['message']['chat']['id']
    #     txt = message['message']['text']
    # except Exception as e:
    #     logger.error(e)
    #     try:
    #         chat_id = message['edited_message']['chat']['id']
    #         txt = message['edited_message']['text']
    #     except:
    #         try:
    #             chat_id = message['my_chat_member']['chat']['id']
    #             txt = 'error'
    #         except:
    #             logger('parse error')
    
    if message.get('message') != None:
        chat_id = message['message']['chat']['id']
        try:
            txt = message['message']['text']
        except:
            txt = 'error'
    elif message.get('edited_message') != None:
        chat_id = message['edited_message']['chat']['id']
        try:
            txt = message['edited_message']['text']
        except:
            txt = 'error'
    elif message.get('my_chat_member') != None:
        chat_id = message['my_chat_member']['chat']['id']
        txt = 'error'
    else:
        logger.error('something wrong!')
        chat_id  = 0
        txt = 'error'

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
    # logger.info(r)
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