from rest_framework import serializers
from modelCore.models import User, Case, Owner, Customer, UserCaseShip, UserStoreMoney, AppVersion

class UserStoreMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStoreMoney
        fields = '__all__'
        read_only_fields = ('id',)


class CaseSerializer(serializers.ModelSerializer):
    ship_state = serializers.CharField(read_only=True, default='')

    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ('id',)

class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = '__all__'
        read_only_fields = ('id',)