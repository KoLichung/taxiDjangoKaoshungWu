from __future__ import absolute_import, unicode_literals

from celery import shared_task
from modelCore.models import User, UserCaseShip, Case, UserStoreMoney
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
from django.db.models import Q

from datetime import date, datetime, timedelta
import requests
import logging

logger = logging.getLogger(__file__)

@shared_task
def countDownUserCaseShip():
    # handle ships
    ships = UserCaseShip.objects.distinct('case')
    for ship in ships:
        if ship.case.case_state == 'wait':
            if ship.countdown_second <= 0:
                if ship.state == 'state1':
                    case_user = ship.user
                    case = ship.case
                    ref_location = Point(float(case.on_lng), float(case.on_lat), srid=4326) 
                    new_users = User.objects.filter(~Q(id=case_user.id)).filter(is_online=True, is_passed=True).order_by(GeometryDistance("location", ref_location))[:4]
                    
                    if new_users.count()!=0:
                        for user in new_users:
                            userCaseShip = UserCaseShip()
                            userCaseShip.user = user
                            userCaseShip.case = case
                            userCaseShip.state = 'state2'
                            userCaseShip.countdown_second = 10
                            userCaseShip.save()

                            #正副的推播任務最多一個
                            if UserCaseShip.objects.filter(user=user, state='state2').count() == 1:
                                from fcmNotify.tasks import sendTaskMessage
                                sendTaskMessage(user)
                        ship.delete()
                    else:
                        #如果沒有其他人可接, state 跳到 state3
                        ship.state = 'state3'
                        ship.countdown_second = 10
                        ship.save()

                if ship.state == 'state2':
                    case = ship.case
                    ref_location = Point(float(case.on_lng), float(case.on_lat), srid=4326) 
                    new_users = User.objects.filter(is_online=True, is_passed=True).order_by(GeometryDistance("location", ref_location))[:30]

                    if new_users.count()!=0:
                        for user in new_users:
                            userCaseShip = UserCaseShip()
                            userCaseShip.user = user
                            userCaseShip.case = case
                            userCaseShip.state = 'state3'
                            userCaseShip.countdown_second = 10
                            userCaseShip.save()
                        
                        UserCaseShip.objects.filter(case=ship.case, state='state2').delete()
                    else:
                        #如果沒有其他人可接, state 跳到 state3
                        ship.state = 'state3'
                        ship.countdown_second = 10
                        ship.save()

                if ship.state == 'state3':
                    case = ship.case
                    case.case_state = 'canceled'
                    case.save()
                    UserCaseShip.objects.filter(case=ship.case).delete()   
            else:
                UserCaseShip.objects.filter(case=ship.case).update(countdown_second=ship.countdown_second-5)
                # ship.countdown_second = ship.countdown_second - 5
                # ship.save()
        else:
            UserCaseShip.objects.filter(case=ship.case).delete()

    # for new cases, create new ships
    case_ids = UserCaseShip.objects.all().values_list('case', flat=True).distinct()
    cases = Case.objects.filter(case_state='wait').filter(~Q(id__in=case_ids))
    for case in cases:
        if case.on_lng != None:
            if User.objects.filter(is_online=True, is_passed=True).count() != 0:
                try:
                    ref_location = Point(float(case.on_lng), float(case.on_lat), srid=4326)

                    user = User.objects.filter(is_online=True, is_passed=True).order_by(GeometryDistance("location", ref_location)).first()

                    userCaseShip = UserCaseShip()
                    userCaseShip.user = user
                    userCaseShip.case = case
                    userCaseShip.state = 'state1'
                    userCaseShip.countdown_second = 10
                    userCaseShip.save()

                    #正副的推播任務最多一個
                    if UserCaseShip.objects.filter(user=user, state='state1').count() == 1:
                        from fcmNotify.tasks import sendTaskMessage
                        sendTaskMessage(user)
                except Exception as e: 
                    print(e)
                    # 無法有 point 則 cancel
                    case.case_state = "canceled"
                    case.save()
            else:
                # 無法有 driver 則 cancel
                case.case_state = "canceled"
                case.save()
        #沒有 on_lng 則 cancel
        else:
            case.case_state = "canceled"
            case.save()

# https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=AIzaSyCdP86OffSMXL82nbHA0l6K0W2xrdZ5xLk
def getTimePredict(locationA, locationB):
    key='AIzaSyCdP86OffSMXL82nbHA0l6K0W2xrdZ5xLk'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={locationA}&destination={locationB}&key={key}'
    response = requests.get(url)
    logger.info(response.body)
    resp_json_payload = response.json()
    time_predict = resp_json_payload
    # return secs
    return resp_json_payload['routes'][0]['legs'][0]['duration']['value']
    
@shared_task
def add(x, y):
    print("x+y=")
    print(x+y)
    return x + y

@shared_task
def getUserCount():
    print("current user count =")
    print(User.objects.all().count()) 