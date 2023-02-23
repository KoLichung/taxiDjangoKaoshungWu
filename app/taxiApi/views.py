from rest_framework import viewsets, mixins
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modelCore.models import Case, UserCaseShip, UserStoreMoney, AppVersion, CarTeam
from taxiApi import serializers
from django.utils import timezone as datetime
from django.contrib.gis.geos import Point

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
                    mixins.ListModelMixin,):
    queryset = CarTeam.objects.all()
    serializer_class = serializers.CarTeamSerializer

    def get_queryset(self):
        return self.queryset

#http://localhost:8000/api/get_cases/
class GetCaseViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Case.objects.all()
    serializer_class = serializers.CaseSerializer

    def get_queryset(self):
        caseIds = UserCaseShip.objects.filter(user=self.request.user).values_list('case', flat=True)
        queryset = self.queryset.filter(id__in=caseIds)
        for i in range(len(queryset)):
            queryset[i].user_left_money = self.request.user.left_money
        return queryset

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
            raise APIException("this case already belong to someone")
        else:
            case.case_state = 'way_to_catch'
            case.confirm_time = datetime.now()
            case.user = self.request.user
            case.userId = case.user.userId
            case.save()
            
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

                    dispatch_fee = case_money * case.user.dispatch_fee_percent_integer / 100
                    
                    case.dispatch_fee = int(dispatch_fee) // 10 * 10

                    # case.dispatch_fee = int(case_money * case.user.dispatch_fee_percent_integer / 100)
                    case.save()

                    #delete ships
                    UserCaseShip.objects.filter(case=case).delete()

                    user = self.request.user 
                    user.left_money = user.left_money - case.dispatch_fee
                    user.save()
                    return Response({'message': "ok"})
            else:
                raise APIException("no case money")
        except:
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
        elif (isOnline == 'True' or isOnline == 'true') and user.left_money >= 0:
            user.is_online = True
            user.save()
            return Response({'message': "ok"})
        else:
            print("not sure")
            return Response({'message': "no left money"})


class AppVersionView(APIView):

    def get(self, request, format=None):
        appVersion = AppVersion.objects.all().order_by('-id').first()
        return Response({'ios': appVersion.iOS_current_version, 'android': appVersion.android_current_version})