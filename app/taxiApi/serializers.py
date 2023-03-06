from rest_framework import serializers
from modelCore.models import Case, UserStoreMoney, AppVersion, CarTeam

class UserStoreMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStoreMoney
        fields = '__all__'
        read_only_fields = ('id',)

class CaseSerializer(serializers.ModelSerializer):
    ship_state = serializers.CharField(read_only=True, default='')
    user_left_money = serializers.IntegerField(default=0)
    countdown_second = serializers.IntegerField(default=0)
    expect_second = serializers.IntegerField(default=0)

    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ('id',)

class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = '__all__'
        read_only_fields = ('id',)

class CarTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarTeam
        fields = '__all__'
        read_only_fields = ('id',)