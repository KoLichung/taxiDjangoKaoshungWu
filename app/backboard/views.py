from calendar import month
from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from modelCore.models import User, Customer, Case, UserStoreMoney, UserCaseShip, UserCarTeamShip, CarTeam
from django.db.models import Q, Sum
from django.core.paginator import Paginator
import requests
from dotenv import dotenv_values
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib import auth

import json
from datetime import datetime, date, time, timedelta

def index(request):
    return render(request, 'backboard/index.html')

def logout(request):
    auth.logout(request)
    return redirect('/backboard/login/')

def home(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/backboard/login/')
    # config = dotenv_values(".env")
    # key = config['geoCodingKey']
    # print(config.items())
    # print(config['geoCodingKey'])
    if request.method == 'POST':
        phone = request.POST.get("passengerPhone", "")
        name = request.POST.get("passengerName", "")
        depature = request.POST.get("departure", "")
        destination = request.POST.get("destination", "")
        memo = request.POST.get("memo", "")
        # numberOfCars = request.POST.get("numberOfCars", "")
        print(f"{phone} {name} {depature} {destination} {memo}")

        if Customer.objects.filter(phone=phone).count() == 0:
            customer = Customer()
            customer.name = name
            customer.phone = phone
            customer.save()
        else:
            customer = Customer.objects.filter(phone=phone).first()

        case = Case()
        case.case_state = 'wait'
        case.customer = customer
        case.customer_name = customer.name
        case.customer_phone = customer.phone

        #need to change
        path = 'https://maps.googleapis.com/maps/api/geocode/json?address='

        case.on_address = depature
        onUrl = path+depature+"&key="+"AIzaSyCrzmspoFyEFYlQyMqhEkt3x5kkY8U3C-Y"
        # print(onUrl)
        response = requests.get(onUrl)
        resp_json_payload = response.json()
        case.on_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
        case.on_lng = resp_json_payload['results'][0]['geometry']['location']['lng']

        case.off_address = destination
        onUrl = path+depature+"&key="+"AIzaSyCrzmspoFyEFYlQyMqhEkt3x5kkY8U3C-Y"
        response = requests.get(onUrl)
        resp_json_payload = response.json()
        case.off_lat = resp_json_payload['results'][0]['geometry']['location']['lat']
        case.off_lng = resp_json_payload['results'][0]['geometry']['location']['lng']

        case.memo = memo
        case.create_time = datetime.now()

        case.save()

        #### new user case ship, need to do on celery, here is for test and demo
        # ref_location = Point(case.on_lng, case.on_lat, srid=4326)
        # user = User.objects.filter(is_online=True).filter(is_passed=True).order_by(GeometryDistance("location", ref_location)).first()

        # userCaseShip = UserCaseShip()
        # userCaseShip.user = user
        # userCaseShip.case = case
        # userCaseShip.save()

        # from fcmNotify.tasks import sendTaskMessage
        # sendTaskMessage(user)

        return render(request, 'backboard/home.html', {'message': "新增成功"})

    return render(request, 'backboard/home.html')

def dispatch_inquire(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/backboard/')

    if request.method == 'POST':
        caseId = request.POST.get("cancel_case_id", 0)
        if caseId != 0:
            case = Case.objects.get(id=caseId)
            case.case_state = "canceled"
            case.save()

    carTeams = CarTeam.objects.all()
    q_assigned_car_team = ''
    q_belonged_car_team = ''
    q_start_date_string=''
    q_end_date_string = ''


    # 在 html 選擇 selected 後，要把值傳回 views 
    # 再把 views 的值傳回給 html
    # selected -> views -> value

    if (request.GET.get("qDate") != None and request.GET.get("qDate") != ""):
        q_start_date = request.GET.get("qDate")[:10]
        q_end_date = request.GET.get("qDate")[-10:]
        cases = Case.objects.filter(create_time__gte = q_start_date, create_time__lte = q_end_date).order_by('-id')
        
        q_end_date_string = q_end_date
        q_start_date_string = q_start_date

        #qDate_string = request.GET.get("qDate")
        qDate_string = q_start_date + ' ~ ' + q_end_date
        

        print(cases.count())
    else: 
        #today = datetime.now()
        #thirty_days_before = today - timedelta(days=30)
        q_end_date= datetime.now()
        q_start_date = q_end_date - timedelta(days=30)
        
        cases = Case.objects.filter(create_time__gte=q_start_date, create_time__lte=q_end_date).order_by('-id')
        
        q_end_date_string = q_end_date.strftime('%Y-%m-%d')
        q_start_date_string = q_start_date.strftime('%Y-%m-%d')

        qDate_string = f'{q_start_date_string} ~ {q_end_date_string}'
        print(qDate_string)

    if (request.GET.get("assigned_car_team") != None and request.GET.get("assigned_car_team") != ""):
        q_assigned_car_team = request.GET.get("assigned_car_team")
        cases = cases.filter(carTeam__name = q_assigned_car_team)
        #print(cases)
    
    if (request.GET.get("belonged_car_team") != None and request.GET.get("belonged_car_team") != ""):
        q_belonged_car_team = request.GET.get("belonged_car_team")
        cases = cases.filter(carTeam__name = q_belonged_car_team)
        #print(cases)

    
    total_dispatch_fee = cases.aggregate(Sum('dispatch_fee'))

    # if request.GET.get("qKeyword") != None and request.GET.get("qKeyword") != "" and request.GET.get("qUserId") != None and request.GET.get("qUserId") != "" and request.GET.get("qDate") != None and request.GET.get("qDate") != "" :
    #     print(request.GET.get("qKeyword")) #會印出查詢的內容
    #     print(request.GET.get("qUserId"))
    #     print(request.GET.get("qDate"))
    #     cases = Case.objects.filter(customer_name=request.GET.get("qKeyword")).filter(customer_phone=request.GET.get("qKeyword")).filter(user=request.GET.get("qUserId")).filter(create_time=request.GET.get("qDate")).order_by('-id')
    # else:
    #     cases = Case.objects.order_by('-id')
    
    # paginator = Paginator(cases, 10)
    # if request.GET.get('page') != None:
    #     page_number = request.GET.get('page') 
    # else:
    #     page_number = 1
    # page_obj = paginator.get_page(page_number)

    # page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_number)
    
    # return render(request, 'backboard/dispatch_inquire.html',{'cases':page_obj})

    return render(request, 'backboard/dispatch_inquire.html', {
            # 'qDate':'2023-03-23+~+2023-03-30',
            'qDate':qDate_string,
            'start_date':q_start_date_string,
            'end_Date':q_end_date_string,
            'assigned_car_team':q_assigned_car_team,
            'belonged_car_team':q_belonged_car_team,
            'cases':cases, 
            'carTeams':carTeams, 
            'total_dispatch_fee':total_dispatch_fee, 
        })

def passengers(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/backboard/login/')

    customers = Customer.objects.all()
    print(customers.count())
    if (request.GET.get("qName") != None and request.GET.get("qName") != ""):
        customers = customers.filter(name__contains=request.GET.get("qName"))
        print(customers.count())
     
    if (request.GET.get("qPhone") != None and request.GET.get("qPhone") != ""):
        customers = customers.filter(phone__contains=request.GET.get("qPhone"))
        print(customers.count())

    customers.order_by('-id')
    
    paginator = Paginator(customers, 10)
    if request.GET.get('page') != None:
        page_number = request.GET.get('page') 
    else:
        page_number = 1
    page_obj = paginator.get_page(page_number)

    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_number)

    return render(request, 'backboard/passengers.html',{'customers':page_obj})

def drivers(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/backboard/login/')

    if request.method == 'GET':
        # context = {}
        if request.GET.get("q") != None and request.GET.get("q") != "":
            print(request.GET.get("q"))
            drivers = User.objects.filter(phone=request.GET.get("q")).order_by('-id')
        else:
            drivers = User.objects.filter(~Q(id=1)).order_by('-id')
            # drivers = User.objects.all()

        carTeams = CarTeam.objects.all()

        paginator = Paginator(drivers, 10)
        if request.GET.get('page') != None:
            page_number = request.GET.get('page') 
        else:
            page_number = 1
        page_obj = paginator.get_page(page_number)

        page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_number)
        return render(request, 'backboard/drivers.html', {'drivers': page_obj,'carTeams':carTeams})
    
    elif request.method == 'POST':
        
        user = User.objects.get(id=request.POST.get('userId'))

        if(request.POST.get("isPassed")!= None and request.POST.get("isPassed")=="true"):
            user.is_passed = True
        else:
            user.is_passed = False

        if(request.POST.get("is_telegram_bot_enable")!= None and request.POST.get("is_telegram_bot_enable")=="true"):
            user.is_telegram_bot_enable = True
        else:
            user.is_telegram_bot_enable = False

        # if(request.POST.get("dispatch_fee_percent")!=""):
        #     try:
        #         user.dispatch_fee_percent_integer = int(request.POST.get("dispatch_fee_percent"))
        #     except:
        #         print("parse fee percent error")

        
        carTeams = CarTeam.objects.all() #全部的 carTeam 
        user_car_teams = UserCarTeamShip.objects.filter(user=user) #司機原所屬的carTeam
        user_carTeam_ids = list(user_car_teams.values_list('carTeam',flat=True)) #返回一個用 values_list()讓他不再是 object 的 list 

        selected_carTeams = []
        carTeam_ids = request.POST.getlist('carTeams[]') #前端打勾的 carTeam
        print(carTeam_ids)

        # 確認把所選的 car teams 存起來
        for carTeam_id in carTeam_ids:
            carTeam = CarTeam.objects.get(id=carTeam_id)
            if not UserCarTeamShip.objects.filter(user=user, carTeam=carTeam).exists(): #如果在前端打勾的 carTeam 有在 userCarTeam 的話
                userCarTeam = UserCarTeamShip() #否則 userCarTeam = ??
                userCarTeam.user = user
                userCarTeam.carTeam = carTeam
                userCarTeam.save() 

            selected_carTeams.append(carTeam)

        # 把沒選的 car teams 刪掉
        for user_carTeam in user_car_teams:
            if user_carTeam.carTeam not in selected_carTeams:
                user_carTeam.delete()
        

        user.name = request.POST.get("username")
        #user.userId = request.POST.get("userIdNumber")
        user.vehicalLicence = request.POST.get("vehicalLicenceNumber")
        user.idNumber=request.POST.get("IDNumber")
        user.phone=request.POST.get("phoneNumber")
        user.gender=request.POST.get("driverGender")
        user.car_color=request.POST.get("car-Color")
        user.number_sites=request.POST.get("sitesNumber")
        
        user.save() 
    
        return redirect('/backboard/drivers',{
            'user':user,
            'carTeams':carTeams, 
            'user_car_teams':user_car_teams, 
            'user_carTeam_ids':user_carTeam_ids,
        })

def accounting_records(request):
    userStoreMoneys = UserStoreMoney.objects.order_by('-id')
    print(userStoreMoneys.count())

    paginator = Paginator(userStoreMoneys, 10)
    if request.GET.get('page') != None:
        page_number = request.GET.get('page') 
    else:
        page_number = 1
    page_obj = paginator.get_page(page_number)

    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_number)

    return render(request, 'backboard/accounting_records.html',{'userStoreMoneys': page_obj})

# def accounting_statistics(request):
#     summarys = MonthSummary.objects.all().order_by('-id')[:2]
#     the_day = summarys[0].month_date
#     last_month_day = the_day - timedelta(days=30)
#     last_2_month_day = the_day - timedelta(days=60)

#     return render(request, 'backboard/accounting_statistics.html', {'summarys':summarys, 'last_month_day':last_month_day, 'last_2_month_day':last_2_month_day})

def credit_topup(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/backboard/')
    
    if request.method == 'POST':
        phone = request.POST.get("phone")
        moneyType = request.POST.get("moneyType")
        money = int(request.POST.get("money"))
        
        try:
            user = User.objects.filter(phone=phone).first()
            # today_min = datetime.combine(date.today(), time.min)
            # today_max = datetime.combine(date.today(), time.max)
            # if( UserStoreMoney.objects.filter(user=user, date__range=(today_min, today_max)).count()==0 ):

            userStoreMoney = UserStoreMoney()
            userStoreMoney.user = user
            if moneyType == 'increase':
                userStoreMoney.increase_money = money
                userStoreMoney.user_left_money = user.left_money
                userStoreMoney.sum_money = userStoreMoney.increase_money + userStoreMoney.user_left_money
            else:
                userStoreMoney.increase_money = -money
                userStoreMoney.user_left_money = user.left_money
                userStoreMoney.sum_money = userStoreMoney.increase_money + userStoreMoney.user_left_money
            userStoreMoney.date = datetime.now()
            userStoreMoney.save()
            user.left_money = userStoreMoney.sum_money
            user.save()
            return render(request, 'backboard/credit_topup.html', {'message': "新增成功"})
        
        except:
            return render(request, 'backboard/credit_topup.html', {'message': "找不到這個車號！"})
        
    return render(request, 'backboard/credit_topup.html')

def dispatch_management(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/backboard/login/')
    # online_drivers = User.objects.all().exclude(id=1)
    # on_task_drivers = User.objects.all().exclude(id=1)
    # on_the_way_drivers = User.objects.all().exclude(id=1)
    # pending_drivers = User.objects.filter(id=100)

    # paginator = Paginator(drivers, 10)
    # if request.GET.get('page') != None:
    #     page_number = request.GET.get('page') 
    # else:
    #     page_number = 1
    # page_obj = paginator.get_page(page_number)

    # page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_number)

    #return render(request, 'backboard/dispatch_management.html', {'online_drivers': online_drivers, 'on_task_drivers':on_task_drivers, 'on_the_way_drivers':on_the_way_drivers, 'pending_drivers':pending_drivers})
    return render(request, 'backboard/dispatch_management.html')

def ajax_get_drivers(request):
    online_drivers = User.objects.filter(is_online=True).exclude(id=1)

    on_task_case_condition = Q(case_state='arrived') | Q(case_state='catched') | Q(case_state='on_road')
    on_task_user_ids = Case.objects.filter(on_task_case_condition).values_list('user', flat=True)
    on_task_drivers = User.objects.filter(id__in=on_task_user_ids).exclude(id=1)
    

    on_the_way_user_ids = Case.objects.filter(case_state='way_to_catch').values_list('user', flat=True)
    on_the_way_drivers = User.objects.filter(id__in=on_the_way_user_ids).exclude(id=1)


    pending_drivers = online_drivers.exclude(id__in=on_task_user_ids).exclude(id__in=on_the_way_user_ids)

    # User 列出所有線上的司機
    # UserCaseShip 是有任務在身的司機，不包含閒置的司機
    # 把 UserCaseShip 放進 User 裡

    if request.method == "GET":
        print('ajax get drivers in views')
   
        onlineDrivers = []
        onlineDrivers_ids = []

        # add on task driver
        for online_driver in on_task_drivers:
            data = {
                "id": online_driver.id,
                "belonged_car_team": online_driver.car_teams_string(), #所屬車隊
                "nick_name":online_driver.nick_name,
                "phone":online_driver.phone,
                "vehicalLicence":online_driver.vehicalLicence,
                "current_lat":online_driver.current_lat,
                "current_lng":online_driver.current_lng,
                "state": 'on_task',
            }

            try:
                driver_case = Case.objects.filter(user=online_driver).filter(~Q(case_state='canceled')).filter(~Q(case_state='finished')).order_by('-id').first()
                case_data = {
                    'assigned_by':driver_case.carTeam.name, #派單車隊
                    'on_address': driver_case.on_address,
                    'off_address': driver_case.off_address,
                }
                data['case'] = case_data
                

            except Exception as e:
                print(e)
                print('no case for this driver')

                case_data = {
                    'assigned_by': '',
                    'on_address': '',
                    'off_address': '',
                }
                data['case'] = case_data

            onlineDrivers.append(data)
            onlineDrivers_ids.append(online_driver.id)

        # add on the way driver
        for online_driver in on_the_way_drivers:
            data = {
                "id": online_driver.id,
                "belonged_car_team": online_driver.car_teams_string(), #所屬車隊
                "nick_name":online_driver.nick_name,
                "phone":online_driver.phone,
                "vehicalLicence":online_driver.vehicalLicence,
                "current_lat":online_driver.current_lat,
                "current_lng":online_driver.current_lng,
                "state": 'on_the_way',
            }

            try:
                driver_case = Case.objects.filter(user=online_driver).filter(~Q(case_state='canceled')).filter(~Q(case_state='finished')).order_by('-id').first()
                case_data = {
                    'assigned_by':driver_case.carTeam.name, #派單車隊
                    'on_address': driver_case.on_address,
                    'off_address': driver_case.off_address,
                }
                data['case'] = case_data
                

            except Exception as e:
                print(e)
                print('no case for this driver')

                case_data = {
                    'assigned_by': '',
                    'on_address': '',
                    'off_address': '',
                }
                data['case'] = case_data

            onlineDrivers.append(data)
            onlineDrivers_ids.append(online_driver.id)

        # add pending driver
        for online_driver in pending_drivers:
            data = {
                "id": online_driver.id,
                "belonged_car_team": online_driver.car_teams_string(), #所屬車隊
                "nick_name":online_driver.nick_name,
                "phone":online_driver.phone,
                "vehicalLicence":online_driver.vehicalLicence,
                "current_lat":online_driver.current_lat,
                "current_lng":online_driver.current_lng,
                "state": 'pending',
            }

            onlineDrivers.append(data)
            onlineDrivers_ids.append(online_driver.id)


        print(onlineDrivers)

        return JsonResponse({
                'online_count':online_drivers.count(), 
                'on_task_count':on_task_drivers.count(),
                'on_the_way_count':on_the_way_drivers.count(),
                'pending_count':pending_drivers.count(),
                'onlineDrivers':onlineDrivers,
                'onlineDrivers_ids':onlineDrivers_ids,
                'onlineDrivers_list':onlineDrivers,
            })

    else :
        print('ajax get drivers error')
        return HttpResponse(status=400)