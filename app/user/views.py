from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from user.serializers import UserSerializer, AuthTokenSerializer, UpdateUserSerializer
from modelCore.models import CarTeam, UserCarTeamShip, User

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save(user=self.request.user)

        car_team_id = self.request.data.get('car_team')
        car_team = CarTeam.objects.get(id=car_team_id)
        user_car_team_ship = UserCarTeamShip()
        user_car_team_ship.carTeam = car_team
        user_car_team_ship.user = user
        user_car_team_ship.save()

        return user

#http://localhost:8000/api/user/token/  要用 post, 並帶參數
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

#http://localhost:8000/api/user/me/  要有 token
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UpdateUserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class UpdateUserLineIdView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    def put(self, request, format=None):
        try:
            # print(self.request.user)
            # print(self.request.data.get('line_id'))
            user = self.request.user
            user.line_id = self.request.data.get('line_id')
            user.save()
            return Response({'message': 'success update!'})
        except Exception as e:
            raise APIException("wrong token or null line_id")

class GetUserLeftMoney(APIView):
    authentication_classes = (authentication.TokenAuthentication,)

    def get(self, request, format=None):
        user = self.request.user
        left_money = user.left_money
        return Response({'left_money': left_money})
    
class DeleteUser(generics.DestroyAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # lookup_field = 'pk'
    def delete(self, request, pk, format=None):
        
        auth_user = self.request.user
        user = User.objects.get(id=pk)
        if user == auth_user:
            user.delete()
            return Response('delete user')
        else:
            return Response('not auth')