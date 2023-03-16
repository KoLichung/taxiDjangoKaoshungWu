from __future__ import absolute_import, unicode_literals

from celery import shared_task
from modelCore.models import User, UserCaseShip, Case, UserStoreMoney, CarTeam
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
from django.db.models import Q

from datetime import date, datetime, timedelta
import requests
import logging
import json

TOKEN = '5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0'
logger = logging.getLogger(__file__)

@shared_task
def countDownUserCaseShip():

    cases = Case.objects.filter(case_state='wait')
    for case in cases:
        ref_location = Point(float(case.on_lng), float(case.on_lat), srid=4326)

        asking_user_ids = list(UserCaseShip.objects.filter(~Q(user=None)).values_list('user',flat=True).distinct())
        print(f'asking_user_ids {asking_user_ids}')

        if UserCaseShip.objects.filter(case=case).count() == 0:
            # 先 new 一個 user_case_ship 且 user == None
            # 用 user == None 來檢查(並表示) 目前有 tasker 正在派單
            userCaseShip = UserCaseShip()
            userCaseShip.case = case
            userCaseShip.save() 
            
            # 1.要在線 2.要通過審核 3.非任務中 4.非詢問案件中
            qulified_users = User.objects.filter(is_online=True, is_passed=True, is_on_task=False).filter(~Q(id__in=asking_user_ids))
            print(f'qulified_users {qulified_users}')
            if qulified_users.count() != 0:
                user = qulified_users.order_by(GeometryDistance("location", ref_location)).first()
                
                timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)

                if timePredict < 900:
                    userCaseShip.user = user
                    userCaseShip.expect_second = timePredict
                    userCaseShip.save()

                    from fcmNotify.tasks import sendTaskMessage
                    sendTaskMessage(user)
                else:
                    case.case_state = 'canceled'
                    case.save()
                    userCaseShip.delete()

                    if case.telegram_id != None and case.telegram_id != '':
                        tel_send_message(case.telegram_id, f'{case.case_number}\n抱歉目前附近無符合駕駛!\n-----------------\n上車:{case.on_address}')
            else:
                case.case_state = 'canceled'
                case.save()
                userCaseShip.delete()

                if case.telegram_id != None and case.telegram_id != '':
                    tel_send_message(case.telegram_id, f'{case.case_number}\n抱歉目前附近無符合駕駛!\n-----------------\n上車:{case.on_address}')
                
        else:
            userCaseShip = UserCaseShip.objects.filter(case=case).first()

            if userCaseShip.user != None:
                if userCaseShip.countdown_second != 0:
                    userCaseShip.countdown_second = userCaseShip.countdown_second - 2
                    userCaseShip.save()
                else:
                    # 司機未接單
                    # countdown_second == 0,         
                    # 把此 user 加入排除名單
                    # 如果司機已加入排除名單, 則此為司機拒絕接單
                    if userCaseShip.exclude_ids_text != '':
                        exclude_ids_array = userCaseShip.exclude_ids_text.split(',')
                    else:
                        exclude_ids_array = []

                    if str(userCaseShip.user.id) not in exclude_ids_array:
                        user = userCaseShip.user
                        car_teams_string = user.car_teams_string()
                        if case.telegram_id != None and case.telegram_id != '':
                            tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n{user.nick_name} 駕駛人未接單\n-----------------------\n上車:{case.on_address}')

                        if len(userCaseShip.exclude_ids_text) == 0:
                            userCaseShip.exclude_ids_text = str(userCaseShip.user.id)
                        else:
                            userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{userCaseShip.user.id}'

                    userCaseShip.user = None
                    userCaseShip.save()

                    # 尋找下一位
                    qulified_users = User.objects.filter(is_online=True, is_passed=True, is_on_task=False).filter(~Q(id__in=asking_user_ids)).filter(~Q(id__in=exclude_ids_array))
                    if qulified_users.count() != 0:
                        user = qulified_users.order_by(GeometryDistance("location", ref_location)).first()

                        timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)

                        if timePredict < 900:
                            userCaseShip.user = user
                            userCaseShip.countdown_second = 16
                            userCaseShip.expect_second = timePredict
                            userCaseShip.save()

                            from fcmNotify.tasks import sendTaskMessage
                            sendTaskMessage(user)
                        else:
                            case.case_state = 'canceled'
                            case.save()
                            userCaseShip.delete()

                            if case.telegram_id != None and case.telegram_id != '':
                                tel_send_message(case.telegram_id, f'{case.case_number}\n抱歉目前附近無符合駕駛!\n-----------------\n上車:{case.on_address}')
                    else:
                        case.case_state = 'canceled'
                        case.save()
                        userCaseShip.delete()

                        if case.telegram_id != None and case.telegram_id != '':
                            tel_send_message(case.telegram_id, f'{case.case_number}\n抱歉目前附近無符合駕駛!\n-----------------\n上車:{case.on_address}')
                    
def car_team_count_return_to_zero():
    car_teams = CarTeam.objects.all()
    for car_team in car_teams:
        car_team.day_case_count = 0
        car_team.save()

# https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=AIzaSyCdP86OffSMXL82nbHA0l6K0W2xrdZ5xLk
# https://maps.googleapis.com/maps/api/directions/json?origin=24.131111816506685,120.6426299846543&destination=24.028106564811345,120.69707448525111&key=AIzaSyCdP86OffSMXL82nbHA0l6K0W2xrdZ5xLk
def getTimePredict(on_lat, on_long, off_lat, off_long):
    key='AIzaSyCdP86OffSMXL82nbHA0l6K0W2xrdZ5xLk'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={on_lat},{on_long}&destination={off_lat},{off_long}&key={key}'
    response = requests.get(url)
    # logger.info(response)
    resp_json_payload = response.json()
    time_predict = resp_json_payload['routes'][0]['legs'][0]['duration']['value']
    # return secs
    return time_predict

def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
    r = requests.post(url,json=payload)
    logger.info(r)

# @shared_task
# def add(x, y):
#     print("x+y=")
#     print(x+y)
#     return x + y

# @shared_task
# def getUserCount():
#     print("current user count =")
#     print(User.objects.all().count()) 