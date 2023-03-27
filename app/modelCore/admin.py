from django.contrib import admin
from .models import User, UserStoreMoney, Customer, Case, UserCaseShip, CaseSummary, AppVersion, CarTeam, UserCarTeamShip


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone','is_online','is_passed','current_lat', 'current_lng')

@admin.register(UserStoreMoney)
class UserStoreMoneyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'increase_money', 'sum_money', 'user_left_money')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone')

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','', 'create_time', 'on_address', 'off_time', 'off_address', 'case_money')
    list_filter = ['case_state']

@admin.register(UserCaseShip)
class UserCaseShipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'case', 'countdown_second', 'exclude_ids_text')

@admin.register(CaseSummary)
class CaseSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'case', 'driver_user_id', 'customer_name', 'increase_money', 'decrease_money')

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('id','iOS_current_version', 'android_current_version')

@admin.register(CarTeam)
class CarTeamAdmin(admin.ModelAdmin):
    list_display = ('id','name','day_case_count')

@admin.register(UserCarTeamShip)
class UserCarTeamShipAdmin(admin.ModelAdmin):
    list_display = ('id','user','carTeam','is_dispatch')

