from __future__ import absolute_import, unicode_literals

from celery import shared_task
from modelCore.models import User, UserCaseShip, Case, UserStoreMoney, CarTeam
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
from django.db.models import Q

from datetime import date, datetime, timedelta
import requests
import json
from django.conf import settings

TOKEN = '5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0'

# 在 celery task 裡面, 要看 log 要用 print, 然後在 celery log 裡面看~
@shared_task
def countDownUserCaseShip():

    cases = Case.objects.filter(case_state='wait')
    for case in cases:
        ref_location = Point(float(case.on_lng), float(case.on_lat), srid=4326)

        # 如果司機已經有詢問中的案件了,就不要重複詢問
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
                
                # a.如果 is_staff 在線上, 先派給 is_staff
                # b.再來派給派單車隊的司機
                # c.再來派給派單車隊以外的司機
                # d.再來派給無車隊的司機
                adminUsersIds = list(User.objects.filter(is_staff=True, is_online=True, is_on_task=False).filter(~Q(id__in=asking_user_ids)).order_by(GeometryDistance("location", ref_location)).values_list('id',flat=True))
            
                teamUsersIds = []
                otherTeamUsersIds = []
                noneTeamUsersIds = []
                for user in User.objects.filter(is_online=True, is_passed=True, is_on_task=False, is_staff=False).filter(~Q(id__in=asking_user_ids)).order_by(GeometryDistance("location", ref_location)):
                    if case.carTeam == None or user.main_car_team_string() == case.carTeam.name:
                        teamUsersIds.append(user.id)
                    elif user.main_car_team_string() == '無車隊':
                        noneTeamUsersIds.append(user.id)
                    else:
                        otherTeamUsersIds.append(user.id)
                
                print(f'adminUsersIds {adminUsersIds}')
                print(f'teamUsersIds {teamUsersIds}')
                print(f'otherTeamUsersIds {otherTeamUsersIds}')
                print(f'noneTeamUsersIds {noneTeamUsersIds}')

                # usersList = list(dict.fromkeys(adminUsersIds+teamUsersIds+otherTeamUsersIds+noneTeamUsersIds))
                # print(f'usersList {usersList}')
                # userCaseShip.ask_ranking_ids_text = ','.join(str(x) for x in usersList)
                # print(f'ask_ranking_ids_text {userCaseShip.ask_ranking_ids_text}')

                userCaseShip.ask_manager_ids_text = ','.join(str(x) for x in adminUsersIds)
                userCaseShip.ask_same_car_team_ids_text = ','.join(str(x) for x in teamUsersIds)
                userCaseShip.ask_not_same_car_team_ids_text = ','.join(str(x) for x in otherTeamUsersIds)
                userCaseShip.ask_no_car_team_ids_text = ','.join(str(x) for x in noneTeamUsersIds)

                print(f'ask_manager_ids_text {userCaseShip.ask_manager_ids_text }')
                print(f'ask_same_car_team_ids_text {userCaseShip.ask_same_car_team_ids_text }')
                print(f'ask_not_same_car_team_ids_text {userCaseShip.ask_not_same_car_team_ids_text }')
                print(f'ask_no_car_team_ids_text {userCaseShip.ask_no_car_team_ids_text }')

                userCaseShip.save()
                
                # 詢問 ask_manager_ids_text => ask_same_car_team_ids_text => ask_no_car_team_ids_text, 一條線處理
                if userCaseShip.ask_manager_ids_text != '':
                    qulified_user_ids = userCaseShip.ask_manager_ids_text.split(',')
                    rankUsers = []
                    for id in qulified_user_ids:
                        rankUsers.append(User.objects.get(id=id))

                    for user in rankUsers:
                        timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                        if timePredict < 900:
                            userCaseShip.user = user
                            userCaseShip.expect_second = timePredict
                            userCaseShip.save()

                            from fcmNotify.tasks import sendTaskMessage
                            sendTaskMessage(user)
                            break
                        else:
                            # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                            if len(userCaseShip.exclude_ids_text) == 0:
                                userCaseShip.exclude_ids_text = str(user.id)
                            else:
                                userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                            userCaseShip.ask_manager_ids_text = ''
                            userCaseShip.save()
                            break
                                
                if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text != '':
                    qulified_user_ids = userCaseShip.ask_same_car_team_ids_text.split(',')
                    rankUsers = []
                    for id in qulified_user_ids:
                        rankUsers.append(User.objects.get(id=id))

                    for user in rankUsers:
                        timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                        if timePredict < 900:
                            userCaseShip.user = user
                            userCaseShip.expect_second = timePredict
                            userCaseShip.save()

                            from fcmNotify.tasks import sendTaskMessage
                            sendTaskMessage(user)
                            break
                        else:
                            # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                            if len(userCaseShip.exclude_ids_text) == 0:
                                userCaseShip.exclude_ids_text = str(user.id)
                            else:
                                userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                            userCaseShip.ask_same_car_team_ids_text = ''
                            userCaseShip.save()
                            break
                
                if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text == '' and userCaseShip.ask_not_same_car_team_ids_text != '':
                    qulified_user_ids = userCaseShip.ask_not_same_car_team_ids_text.split(',')
                    rankUsers = []
                    for id in qulified_user_ids:
                        rankUsers.append(User.objects.get(id=id))

                    for user in rankUsers:
                        timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                        if timePredict < 900:
                            userCaseShip.user = user
                            userCaseShip.expect_second = timePredict
                            userCaseShip.save()

                            from fcmNotify.tasks import sendTaskMessage
                            sendTaskMessage(user)
                            break
                        else:
                            # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                            if len(userCaseShip.exclude_ids_text) == 0:
                                userCaseShip.exclude_ids_text = str(user.id)
                            else:
                                userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                            userCaseShip.ask_not_same_car_team_ids_text = ''
                            userCaseShip.save()
                            break

                if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text == '' and userCaseShip.ask_not_same_car_team_ids_text == '' and userCaseShip.ask_no_car_team_ids_text != '':
                    qulified_user_ids = userCaseShip.ask_no_car_team_ids_text.split(',')
                    rankUsers = []
                    for id in qulified_user_ids:
                        rankUsers.append(User.objects.get(id=id))

                    for user in rankUsers:
                        timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                        if timePredict < 900:
                            userCaseShip.user = user
                            userCaseShip.expect_second = timePredict
                            userCaseShip.save()

                            from fcmNotify.tasks import sendTaskMessage
                            sendTaskMessage(user)
                            break
                        else:
                            # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                            if len(userCaseShip.exclude_ids_text) == 0:
                                userCaseShip.exclude_ids_text = str(user.id)
                            else:
                                userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                            userCaseShip.ask_no_car_team_ids_text = ''
                            userCaseShip.save()
                            break


                # 都問完了, 則表示無適合駕駛
                if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text == '' and userCaseShip.ask_not_same_car_team_ids_text == '' and userCaseShip.ask_no_car_team_ids_text == '':
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

                    print(f'user {userCaseShip.user} second left {userCaseShip.countdown_second}')
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
                    # qulified_users = User.objects.filter(is_online=True, is_passed=True, is_on_task=False).filter(~Q(id__in=asking_user_ids)).filter(~Q(id__in=exclude_ids_array))
                    # if qulified_users.count() != 0:
                    
                    print(f'exclude_ids_text {userCaseShip.exclude_ids_text}')
                    exclude_ids_array = userCaseShip.exclude_ids_text.split(',')

                    if userCaseShip.ask_manager_ids_text != '':
                        print('=============asking admin drivers ===============')
                        qulified_user_ids = userCaseShip.ask_manager_ids_text.split(',')
                        rankUsers = []
                        for id in qulified_user_ids:
                            if id not in exclude_ids_array:
                                rankUsers.append(User.objects.get(id=id))
                            else:
                                qulified_user_ids.remove(id)
                                userCaseShip.ask_manager_ids_text = ','.join(str(x) for x in qulified_user_ids)
                                userCaseShip.save()

                        for user in rankUsers:
                            timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                            if timePredict < 900:
                                userCaseShip.user = user
                                userCaseShip.countdown_second = 18
                                userCaseShip.expect_second = timePredict
                                userCaseShip.save()

                                from fcmNotify.tasks import sendTaskMessage
                                sendTaskMessage(user)
                                break
                            else:
                                # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                                if len(userCaseShip.exclude_ids_text) == 0:
                                    userCaseShip.exclude_ids_text = str(user.id)
                                else:
                                    userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                                userCaseShip.ask_manager_ids_text = ''
                                userCaseShip.save()
                                break
                 

                    if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text != '':
                        print('=============asking same team drivers ===============')
                        qulified_user_ids = userCaseShip.ask_same_car_team_ids_text.split(',')
                        rankUsers = []
                        for id in qulified_user_ids:
                            if id not in exclude_ids_array:
                                rankUsers.append(User.objects.get(id=id))
                            else:
                                qulified_user_ids.remove(id)
                                userCaseShip.ask_same_car_team_ids_text = ','.join(str(x) for x in qulified_user_ids)
                                userCaseShip.save()

                        for user in rankUsers:
                            timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                            print(f'=============time predict {timePredict} ===============')
                            if timePredict < 900:
                                userCaseShip.user = user
                                userCaseShip.countdown_second = 18
                                userCaseShip.expect_second = timePredict
                                userCaseShip.save()

                                from fcmNotify.tasks import sendTaskMessage
                                sendTaskMessage(user)
                                break
                            else:
                                # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                                if len(userCaseShip.exclude_ids_text) == 0:
                                    userCaseShip.exclude_ids_text = str(user.id)
                                else:
                                    userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                                userCaseShip.ask_same_car_team_ids_text = ''
                                userCaseShip.save()
                                break
                    
                    if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text == '' and userCaseShip.ask_not_same_car_team_ids_text != '':
                        print('=============asking not same team drivers ===============')
                        qulified_user_ids = userCaseShip.ask_not_same_car_team_ids_text.split(',')
                        rankUsers = []
                        for id in qulified_user_ids:
                            if id not in exclude_ids_array:
                                rankUsers.append(User.objects.get(id=id))
                            else:
                                qulified_user_ids.remove(id)
                                userCaseShip.ask_not_same_car_team_ids_text = ','.join(str(x) for x in qulified_user_ids)
                                userCaseShip.save()

                        for user in rankUsers:
                            timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                            print(f'=============time predict {timePredict} ===============')
                            if timePredict < 900:
                                userCaseShip.user = user
                                userCaseShip.countdown_second = 18
                                userCaseShip.expect_second = timePredict
                                userCaseShip.save()

                                from fcmNotify.tasks import sendTaskMessage
                                sendTaskMessage(user)
                                break
                            else:
                                # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                                if len(userCaseShip.exclude_ids_text) == 0:
                                    userCaseShip.exclude_ids_text = str(user.id)
                                else:
                                    userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                                userCaseShip.ask_not_same_car_team_ids_text = ''
                                userCaseShip.save()
                                break

                    if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text == '' and userCaseShip.ask_not_same_car_team_ids_text == '' and userCaseShip.ask_no_car_team_ids_text != '':
                        qulified_user_ids = userCaseShip.ask_no_car_team_ids_text.split(',')
                        rankUsers = []
                        for id in qulified_user_ids:
                            if id not in exclude_ids_array:
                                rankUsers.append(User.objects.get(id=id))
                            else:
                                qulified_user_ids.remove(id)
                                userCaseShip.ask_no_car_team_ids_text = ','.join(str(x) for x in qulified_user_ids)
                                userCaseShip.save()

                        for user in rankUsers:
                            timePredict = getTimePredict(user.current_lat, user.current_lng, case.on_lat, case.on_lng)
                            if timePredict < 900:
                                userCaseShip.user = user
                                userCaseShip.countdown_second = 18
                                userCaseShip.expect_second = timePredict
                                userCaseShip.save()

                                from fcmNotify.tasks import sendTaskMessage
                                sendTaskMessage(user)
                                break
                            else:
                                # 按照順序排, 有一個大於 15 分鐘, 後面就不用問了
                                if len(userCaseShip.exclude_ids_text) == 0:
                                    userCaseShip.exclude_ids_text = str(user.id)
                                else:
                                    userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{user.id}'
                                userCaseShip.ask_no_car_team_ids_text = ''
                                userCaseShip.save()
                                break


                    # 都問完了, 則表示無適合駕駛
                    if userCaseShip.ask_manager_ids_text == '' and userCaseShip.ask_same_car_team_ids_text == '' and userCaseShip.ask_not_same_car_team_ids_text == '' and userCaseShip.ask_no_car_team_ids_text == '':
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

# https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=
# https://maps.googleapis.com/maps/api/directions/json?origin=24.131111816506685,120.6426299846543&destination=24.028106564811345,120.69707448525111&key=
def getTimePredict(on_lat, on_long, off_lat, off_long):
    key=settings.API_KEY
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={on_lat},{on_long}&destination={off_lat},{off_long}&key={key}'
    response = requests.get(url)
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
    requests.post(url,json=payload)


# @shared_task
# def add(x, y):
#     print("x+y=")
#     print(x+y)
#     return x + y

# @shared_task
# def getUserCount():
#     print("current user count =")
#     print(User.objects.all().count()) 