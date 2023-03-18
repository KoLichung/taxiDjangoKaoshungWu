from lib2to3.pgen2 import driver
from time import time
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.http import HttpResponseRedirect

from modelCore.models import Customer, User, Case, UserCaseShip
from dotenv import dotenv_values
import requests
from datetime import datetime, timezone
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
from django.db.models import Q
import logging
from django.conf import settings
# Create your views here.

logger = logging.getLogger(__file__)

def booking(request):
    return render(request, 'web/booking.html')


def direct_call(request):
    if request.GET.get('back') != None and request.GET.get('back') == "true":
        print("direct call!")
        return render(request, 'web/direct_call.html', {'back':"true"})
    return render(request, 'web/direct_call.html')

def map(request):
    print(request)
    if request.GET.get('line_id')!=None:
        # direct call
        print("here!")
        line_id = request.GET.get('line_id')
        name = request.GET.get('name')
        phone = request.GET.get('phone')

        if Customer.objects.filter(line_id=line_id).count() == 0:
            customer = Customer()
            customer.name = name
            customer.line_id = line_id
            customer.phone = phone
            customer.save()
        else:
            customer = Customer.objects.filter(line_id=line_id).first()
            
        if Case.objects.filter(customer=customer).filter(~Q(case_state="canceled")).filter(~Q(case_state="finished")).count() != 0:
            case = Case.objects.filter(customer=customer).filter(~Q(case_state="canceled")).filter(~Q(case_state="finished")).first()
            if case.user != None:
                driver = case.user
                return render(request, 'web/map.html', {'case': case, 'driver': driver})
        else:
            case = Case()
            case.case_state = 'wait'
            case.customer = customer
            case.customer_name = customer.name
            if(phone!=None):
                case.customer_phone = phone
            else:
                case.customer_phone = customer.phone
            case.create_time = datetime.now()
            case.save()
        
        return render(request, 'web/map.html', {'case': case, 'direct_call':"true", 'line_id':line_id})

    case_id = request.GET.get('case_id')
    print( f"case_id {case_id}")
    case = Case.objects.get(id=case_id)
    driver = case.user

    return render(request, 'web/map.html', {'case': case, 'driver': driver, 'key':settings.API_KEY})


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

# 傳taxi_id到前台以及接前臺收到的line_id
def ajax_call_and_wait(request):

    if is_ajax(request=request):
        print("This is ajax")

        lineID = request.GET.get('line_id')
        name = request.GET.get('name')
        phone = request.GET.get('phone')
        fromLoc = request.GET.get('fromLoc')
        toLoc = request.GET.get('toLoc')
        memo = request.GET.get('memo')

        if Customer.objects.filter(line_id=lineID).count() == 0:
            customer = Customer()
            customer.name = name
            customer.phone = phone
            customer.line_id = lineID
            customer.save()
        else:
            customer = Customer.objects.filter(line_id=lineID).first()
        
        if Case.objects.filter(customer=customer).filter(~Q(case_state="canceled")).filter(~Q(case_state="finished")).count() != 0:
            print("alreay got case")
            case = Case.objects.filter(customer=customer).filter(~Q(case_state="canceled")).filter(~Q(case_state="finished")).first()
        else:
            # 如果最近 120 秒內有取消單, 請稍後再試
            print("here to check")
            logger.info("line call new case")
            if Case.objects.filter(customer=customer).filter(case_state="canceled").count() != 0:
                latest_user_case = Case.objects.filter(customer=customer).filter(case_state="canceled").order_by('-id').first()
                now = datetime.utcnow()
                seconds = (now - latest_user_case.create_time.replace(tzinfo=None)).total_seconds()
                print(f'different seconds {seconds}')
                if seconds < 120:
                    obj = {"cancel": "canceled"}
                    return HttpResponse(json.dumps(obj))

            case = Case()
            case.case_state = 'wait'
            case.customer = customer
            case.customer_name = customer.name
            case.customer_phone = customer.phone

            #need to change
            path = 'https://maps.googleapis.com/maps/api/geocode/json?address='

            # config = dotenv_values(".env")
            # key = config['geoCodingKey']

            case.on_address = fromLoc
            onUrl = path+fromLoc+"&key="+settings.API_KEY
            logger.info(onUrl)
            response = requests.get(onUrl)
            logger.info(response.text)

            resp_json_payload = response.json()
            case.on_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
            case.on_lng = resp_json_payload['results'][0]['geometry']['location']['lng']

            if toLoc != None and toLoc != '':
                case.off_address = toLoc
                onUrl = path+toLoc+"&key="+settings.API_KEY
                logger.info(response.text)
                response = requests.get(onUrl)
                logger.info(response.text)

                resp_json_payload = response.json()
                case.off_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
                case.off_lng = resp_json_payload['results'][0]['geometry']['location']['lng']

            case.memo = memo
            case.create_time = datetime.now()
            
            # need to be modify
            # case.user = User.objects.get(id=2)

            case.save()

        #### new user case ship, need to do on celery, here is for test and demo
        # if UserCaseShip.objects.filter(case= case).count() == 0 and case.user == None:
        #     ref_location = Point(case.on_lng, case.on_lat, srid=4326)
        #     user = User.objects.filter(is_online=True).filter(is_passed=True).order_by(GeometryDistance("location", ref_location)).first()

        #     userCaseShip = UserCaseShip()
        #     userCaseShip.user = user
        #     userCaseShip.case = case
        #     userCaseShip.save()

        #     from fcmNotify.tasks import sendTaskMessage
        #     sendTaskMessage(user)

        if (case.user != None):
            obj = {"case_id": case.id, "driver": case.user.id}
        else:
            obj = {"case_id": case.id}
        

        return HttpResponse(json.dumps(obj))
    else:
        print("Not ajax")
        return HttpResponse("error")

def ajax_check_user_phone_and_direct_call(request):
    lineID = request.GET.get('line_id')
    name = request.GET.get('name')
    phone = request.GET.get('phone')

    if Customer.objects.filter(line_id=lineID).count() == 0:
        if(phone!=None):
            customer = Customer()
            customer.name = name
            customer.phone = phone
            customer.line_id = lineID
            customer.save()
        else:
            obj = {"message": "need_phone"}
            return HttpResponse(json.dumps(obj))
    else:
        customer = Customer.objects.filter(line_id=lineID).first()

    obj = {"phone": customer.phone}
    return HttpResponse(json.dumps(obj))

def ajax_direct_call_wait(request):
    case_id = request.GET.get('case_id')
    case = Case.objects.get(id=case_id)

    print(case.on_lng)
    print(case.on_lat)

    # if UserCaseShip.objects.filter(case=case).count() == 0 and case.user == None:
    #     ref_location = Point(float(case.on_lng), float(case.on_lat), srid=4326)
    #     user = User.objects.filter(is_online=True).filter(is_passed=True).order_by(GeometryDistance("location", ref_location)).first()

    #     userCaseShip = UserCaseShip()
    #     userCaseShip.user = user
    #     userCaseShip.case = case
    #     userCaseShip.save()

    #     from fcmNotify.tasks import sendTaskMessage
    #     sendTaskMessage(user)

    if (case.user != None):
        obj = {"case_id": case.id, "driver": case.user.id}
    else:
        if case.case_state != 'canceled':
            obj = {"case_id": case.id}
        else:
            obj = {"cancel": "canceled"}
    
    return HttpResponse(json.dumps(obj))

def ajax_cancel_case_by_case_id(request):
    caseId = request.GET.get('case_id')
    if Case.objects.get(id=caseId) != None:
        case = Case.objects.get(id=caseId)
        case.case_state="canceled"
        case.save()
        return HttpResponse("success")
    return HttpResponse("error")

def ajax_cancel_case(request):
    lineID = request.GET.get('line_id')
    customer = Customer.objects.filter(line_id=lineID).first()
    if Case.objects.filter(customer=customer, case_state="wait").count() != 0:
        queryset = Case.objects.filter(customer=customer, case_state="wait")
        queryset.update(case_state="canceled")

def ajax_update_lat_lng(request):
    print("update lat lng")
    onLat = request.GET.get('lat')
    onLng = request.GET.get('lng')
    case_id = request.GET.get('case_id')

    case = Case.objects.get(id=case_id)
    case.on_lat = onLat
    case.on_lng = onLng

    # config = dotenv_values(".env")
    # key = config['geoCodingKey']

    path = "https://maps.googleapis.com/maps/api/geocode/json?language=zh-TW&latlng="
    onUrl = path+f'{onLat},{onLng}&key={settings.API_KEY}'
    response = requests.get(onUrl)
    resp_json_payload = response.json()
    address = resp_json_payload['results'][0]['formatted_address']

    case.on_address = address
    case.save()

    obj = {"address": address}

    return HttpResponse(json.dumps(obj))

def intervalCheck(request):
    if is_ajax(request=request):
        # message = {"state": "waiting"}
        message = {"state": "arrived"}

        taxi_id = request.GET.get('taxi_id')
        
        print(taxi_id)
        print("This is interval check")
    else:
        print("Not ajax")
    return HttpResponse(json.dumps(message))

# json.dumps 将 Python 对象编码成 JSON 字符串
# json.loads 将已编码的 JSON 字符串解码为 Python 对象

