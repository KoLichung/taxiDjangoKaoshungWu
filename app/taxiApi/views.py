from rest_framework import viewsets, mixins
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modelCore.models import Case, UserCaseShip, UserStoreMoney, AppVersion, CarTeam
from taxiApi import serializers
from django.utils import timezone as datetime
from datetime import timedelta
from django.contrib.gis.geos import Point
import requests
import logging
import json

TOKEN = '5889906798:AAFR2O_uTBq_ZGPaDkqyfsHkWKK7EQ6bxj0'
logger = logging.getLogger(__file__)

#http://localhost:8000/api/user_store_moneys/
class UserStoreMoneyViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = UserStoreMoney.objects.all()
    serializer_class = serializers.UserStoreMoneySerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')[:10]

#http://localhost:8000/api/user_cases/
class UserCaseViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin):
    
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Case.objects.all()
    serializer_class = serializers.CaseSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

#http://localhost:8000/api/car_teams/
class CarTeamViewSet(viewsets.GenericViewSet,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,):
    queryset = CarTeam.objects.all()
    serializer_class = serializers.CarTeamSerializer

    def get_queryset(self):
        return self.queryset.order_by('id')

#http://localhost:8000/api/get_cases/
class GetCaseViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Case.objects.all()
    serializer_class = serializers.CaseSerializer

    def get_queryset(self):
        caseIds = UserCaseShip.objects.filter(user=self.request.user).values_list('case', flat=True)
        queryset = self.queryset.filter(id__in=caseIds)
        
        for i in range(len(queryset)):
            queryset[i].user_left_money = self.request.user.left_money
            user_case_ship = UserCaseShip.objects.filter(user=self.request.user, case = queryset[i]).first()
            # queryset[i].countdown_second = user_case_ship.countdown_second
            queryset[i].expect_second = user_case_ship.expect_second
            queryset[i].carTeamName = queryset[i].carTeam.name

        return queryset
    
    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'cases':serializer.data,'left_money':self.request.user.left_money,'violation_time':self.request.user.violation_time,'penalty_datetime':self.request.user.penalty_datetime})

class CaseDetailView(APIView):

    def get(self, request):
        case_id= self.request.query_params.get('case_id')
        case = Case.objects.get(id=case_id)
        serializer = serializers.CaseSerializer(case)
        return Response(serializer.data)

#http://localhost:8000/api/update_lat_lng?lat=23.23&lng=124.24
class UpdateLatLngView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')

        if lat!=None:
            user = self.request.user
            user.current_lat = lat
            user.current_lng = lng
            user.location = Point(float(lng), float(lat), srid=4326)
            user.save()

            return Response({'message': "success update!"})
        else:
            raise APIException("need update lat lng")

#http://localhost:8000/api/case_confirm
class CaseConfirmView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        
        # try:
        case = Case.objects.get(id=case_id)
        if(case.user != None):
            UserCaseShip.objects.filter(case=case).delete()
            raise APIException("this case already belong to someone")
        else:
            user = self.request.user

            case.case_state = 'way_to_catch'
            case.confirm_time = datetime.now()
            case.user = user
            case.save()
            
            user.is_on_task = True
            user.is_asking = False
            user.save()

            car_teams_string = user.car_teams_string()

            userCaseShip = UserCaseShip.objects.filter(case=case).first()
            expect_minutes = int(userCaseShip.expect_second / 60)
            tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n車輛預估 {expect_minutes}~{expect_minutes+4} 分鐘到達\n駕駛:{user.nick_name}\n車色:{user.car_color}\n車號:{user.vehicalLicence}\n--------------------------\n備註:\n車上禁食、菸、檳榔\n{user.car_memo}\n--------------------------\n上車:{case.on_address}')

            #delete ships
            UserCaseShip.objects.filter(case=case).delete()
            
            return Response({'message': "ok"})
        # except:
        #     raise APIException("no this case")

class CaseArrivedView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        
        try:
            case = Case.objects.get(id=case_id)
            if(case.user != self.request.user):
                raise APIException("this case already belong to someone")
            else:
                case.case_state = 'arrived'
                case.arrived_time = datetime.now()
                case.save()

                car_teams_string = case.user.car_teams_string()
                tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n司機到達地點\n--------------------------\n上車:{case.on_address}')

                #delete ships
                UserCaseShip.objects.filter(case=case).delete()

                return Response({'message': "ok"})
        except:
            raise APIException("no this case")

class CaseCatchedView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        
        try:
            case = Case.objects.get(id=case_id)
            if(case.user != self.request.user):
                raise APIException("this case already belong to someone")
            else:
                case.case_state = 'catched'
                case.catched_time = datetime.now()
                case.save()
                
                car_teams_string = case.user.car_teams_string()
                tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n乘客已上車\n--------------------------\n上車:{case.on_address}')

                #delete ships
                UserCaseShip.objects.filter(case=case).delete()

                return Response({'message': "ok"})
        except:
            raise APIException("no this case")

class CaseFinishedView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        data = self.request.data
        try:
            off_address = data['off_address']
            case_money = int(data['case_money'])
        except:
            raise APIException("need off_address and case_money body data")

        try:
            if(case_money!= None):
                case = Case.objects.get(id=case_id)
                if(case.user != self.request.user):
                    raise APIException("this case already belong to someone")
                else:
                    case.case_state = 'finished'
                    case.off_time = datetime.now()
                    case.off_address = off_address
                    case.case_money = case_money

                    # 派遣金是 10%
                    dispatch_fee = case_money * 10 / 100
                    # 除以 10 取 整數部分, 並 x 10
                    # ex. 25//10 = 2, 2*10=20, dispatch_fee = 20 
                    case.dispatch_fee = int(dispatch_fee) // 10 * 10

                    case.save()

                    #delete ships
                    UserCaseShip.objects.filter(case=case).delete()

                    user = self.request.user 

                    before_left_money = user.left_money
                    final_dispatch_fee = case.dispatch_fee

                    user.left_money = user.left_money - case.dispatch_fee
                    user.is_on_task = False
                    user.violation_time = 0

                    after_left_money = user.left_money
                    user.save()
                    
                    car_teams_string = case.user.car_teams_string()
                    tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n任務結束\n實際車資：{case.case_money}\n該趟回金：{case.dispatch_fee}\n剩餘餘額：{user.left_money}\n駕駛人員：{user.nick_name}')

                    return Response({
                        'message':'ok', 
                        'before_left_money':before_left_money,
                        'dispatch_fee':final_dispatch_fee,
                        'after_left_money':after_left_money,
                    })
            else:
                raise APIException("no case money")
        except Exception as e:
            logger.error(e)
            raise APIException("no this case")

class CaseCanceledView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        data = self.request.data
        memo = ''
        if data['memo']!=None:
            memo = data['memo']

        try:
            case = Case.objects.get(id=case_id)
            if(case.user != self.request.user):
                raise APIException("this case already belong to someone")
            else:
                case.case_state = 'canceled'
                case.memo = memo
                case.save()
                return Response({'message': "ok"})
        except:
            raise APIException("no this case")

class UpdateUserOnlineState(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        isOnline = self.request.data.get('is_online')
        user = self.request.user

        if isOnline == 'False' or isOnline == 'false':
            user.is_online = False
            user.save()
            return Response({'message': "ok"})
        elif (isOnline == 'True' or isOnline == 'true') and user.left_money > -100 and user.is_in_penalty == False:
            user.is_online = True
            user.save()
            return Response({'message': "ok"})
        else:
            print("not sure")
            return Response({'message': "no left money or in penalty"})

class AppVersionView(APIView):

    def get(self, request, format=None):
        appVersion = AppVersion.objects.all().order_by('-id').first()
        return Response({'ios': appVersion.iOS_current_version, 'android': appVersion.android_current_version})

# 司機拒絕接單回傳
class CaseRefuseView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        case = Case.objects.get(id=case_id)
        user = self.request.user

        try:
            car_teams_string = user.car_teams_string()

            if case.telegram_id != None and case.telegram_id != '':
                tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n{user.nick_name} 駕駛人放棄接單\n-----------------------\n上車:{case.on_address}')

            # userCaseShip = UserCaseShip.objects.filter(case=case).first()
            # userCaseShip.countdown_second = 0

            # if len(userCaseShip.exclude_ids_text) == 0:
            #     userCaseShip.exclude_ids_text = str(userCaseShip.user.id)
            # else:
            #     userCaseShip.exclude_ids_text = userCaseShip.exclude_ids_text + f',{userCaseShip.user.id}'

            # userCaseShip.save()

            if len(case.exclude_ids_text) == 0:
                case.exclude_ids_text = str(user.id)
            else:
                case.exclude_ids_text = case.exclude_ids_text + f',{user.id}'
            case.save()

            if user.violation_time < 4:
                user.violation_time = user.violation_time + 1
                user.is_asking = False
                user.save()
            else:
                user.violation_time = 5
                user.penalty_datetime = datetime.now() + timedelta(minutes=15)
                user.is_in_penalty = True
                user.is_asking = False
                user.save()

            return Response({'message': "ok"})
        except:
            raise APIException("no this case")

class CaseNotifyCustomerView(APIView):
    
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        case_id = self.request.query_params.get('case_id')
        
        try:
            case = Case.objects.get(id=case_id)
            if(case.user != self.request.user):
                raise APIException("this case already belong to someone")
            else:   
                car_teams_string = case.user.car_teams_string()
                if case.telegram_id != None and case.telegram_id != '':
                    tel_send_message(case.telegram_id, f'{case.case_number}-{car_teams_string}\n駕駛通知已抵達上車點\n請乘客盡快上車\n--------------------------\n上車:{case.on_address}')
                return Response({'message': "ok"})
        except:
            raise APIException("no this case")

def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
    r = requests.post(url,json=payload)
    logger.info(r)