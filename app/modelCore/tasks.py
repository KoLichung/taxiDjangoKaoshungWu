from modelCore.models import User, Case, Owner, Customer, UserCaseShip, UserStoreMoney
from datetime import timedelta
from django.utils import timezone as datetime 
from random import randint
from django.contrib.gis.geos import Point

#from modelCore.tasks import fakeData
def fakeData():    

    print('fake owner 1')
    owner = Owner()
    owner.name = "A業主"
    owner.save()

    print("fake user 1")
    user = User()
    user.phone = "0933123456"
    user.name = "劉先生"
    user.line_id = "user_line_id_1"
    user.vehicalLicence = "test licence"
    user.userId = "12345"
    user.idNumber = "N123456789"
    user.gender = "男"
    user.type = "car"
    user.category =  "taxi"
    user.car_model = "Toyota Wish"
    user.car_color = "白"
    user.number_sites =  "6"
    user.is_online = True
    user.left_money = 300
    user.is_passed = True

    user.current_lat = 24.136477
    user.current_lng = 120.686770
    user.location = Point(user.current_lng, user.current_lat)

    user.dispatch_fee_percent_integer = 10

    user.save()
    
    print('fake user store money')
    userStoreMoney = UserStoreMoney()
    userStoreMoney.user =  user
    userStoreMoney.increase_money = 300
    userStoreMoney.sum_money = 300
    userStoreMoney.user_left_money = 300
    userStoreMoney.date = datetime.now()
    userStoreMoney.save()

    print('fake customer 1')
    customer = Customer()
    customer.name = "消費者1"
    customer.phone = "0911123456"
    customer.owner = owner
    customer.line_id = "customer_line_id_1"
    customer.save()

    print('fake wait case 1')
    case = Case()
    case.case_state = 'wait' #(wait, way_to_catch, arrived, catched, on_road, finished, canceled)

    case.customer = customer
    case.customer_name = customer.name
    case.customer_phone = customer.phone
    
    case.owner =  owner
    
    case.on_lat = 24.127190
    case.on_lng = 120.670372
    case.on_address = "台中國家圖書館"

    case.off_lat = 24.131191
    case.off_lng = 120.643521
    case.off_address = "408台中市南屯區文心南五路一段331號" #豐樂雕塑公園

    case.create_time = datetime.now()
    
    case.save()

    userCaseShip = UserCaseShip()
    userCaseShip.user = user
    userCaseShip.case = case
    userCaseShip.save()

    print('fake finished case 1')
    case = Case()
    case.case_state = 'finished' #(wait, way_to_catch, arrived, catched, on_road, finished, canceled)

    case.customer = customer
    case.customer_name = customer.name
    case.customer_phone = customer.phone
    
    case.owner =  owner
    case.user = user

    case.on_lat = 24.127190
    case.on_lng = 120.670372
    case.on_address = "台中國家圖書館"
    case.on_time = datetime.now()

    case.off_lat = 24.131191
    case.off_lng = 120.643521
    case.off_address = "408台中市南屯區文心南五路一段331號" #豐樂雕塑公園

    case.case_money = 150
    case.memo = "fake case!"

    case.create_time = datetime.now()
    case.confirm_time = datetime.now() + timedelta(minutes=3)
    case.arrived_time = datetime.now() + timedelta(minutes=6)
    case.catched_time = datetime.now() + timedelta(minutes=7)
    case.off_time = datetime.now() + timedelta(minutes=17)

    case.save()

    ############################
    print('fake owner 2')
    owner = Owner()
    owner.name = "B業主"
    owner.save()

    print("fake user 2")
    user = User()
    user.phone = "0944123456"
    user.name = "許先生"
    user.line_id = "user_line_id_2"
    user.vehicalLicence = "test licence"
    user.userId = "12336"
    user.idNumber = "N123456999"
    user.gender = "男"
    user.type = "car"
    user.category =  "taxi"
    user.car_model = "Toyota Wish"
    user.car_color = "白"
    user.number_sites =  "6"
    user.is_online = True
    user.left_money = 200
    user.is_passed = True

    user.current_lat = 24.1338931
    user.current_lng = 120.7005887
    user.location = Point(user.current_lng, user.current_lat)

    user.save()

    print('fake user store money')
    userStoreMoney = UserStoreMoney()
    userStoreMoney.user =  user
    userStoreMoney.increase_money = 200
    userStoreMoney.sum_money = 200
    userStoreMoney.user_left_money = 200
    userStoreMoney.date = datetime.now()
    userStoreMoney.save()

    print('fake customer 2')
    customer = Customer()
    customer.name = "消費者2"
    customer.phone = "0922123456"
    customer.owner = owner
    customer.line_id = "customer_line_id_2"
    customer.save()
    
    print('fake finished case 2')
    case = Case()
    case.case_state = 'finished' #(wait, way_to_catch, arrived, catched, on_road, finished, canceled)

    case.customer = customer
    case.customer_name = customer.name
    case.customer_phone = customer.phone
    
    case.owner =  owner
    case.user = user

    case.on_lat = 24.127190
    case.on_lng = 120.670372
    case.on_address = "台中國家圖書館"
    case.on_time = datetime.now()

    case.off_lat = 24.131191
    case.off_lng = 120.643521
    case.off_address = "408台中市南屯區文心南五路一段331號" #豐樂雕塑公園

    case.case_money = 350
    case.memo = "fake case!"

    case.create_time = datetime.now()
    case.confirm_time = datetime.now() + timedelta(minutes=3)
    case.arrived_time = datetime.now() + timedelta(minutes=6)
    case.catched_time = datetime.now() + timedelta(minutes=7)
    case.off_time = datetime.now() + timedelta(minutes=17)

    case.save()

def random_with_N_digits(n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)

def fake10User():
    for x in range(10):
        user = User()
        user.phone = f"0944{random_with_N_digits(6)}"
        user.name = f"許{random_with_N_digits(2)}"
        user.line_id = f"user_line_id_{random_with_N_digits(3)}"
        user.vehicalLicence = "test licence"
        user.userId = "12345"
        user.idNumber = "N123456789"
        user.gender = "男"
        user.type = "car"
        user.category =  "taxi"
        user.car_model = "Toyota Wish"
        user.car_color = "白"
        user.number_sites =  "6"
        user.is_online = True
        user.left_money = x*100
        user.is_passed = True
        user.save()