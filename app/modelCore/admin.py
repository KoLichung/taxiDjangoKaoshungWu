from django.contrib import admin
from .models import User, UserStoreMoney, Owner, Customer, Case, UserCaseShip, CaseSummary, MonthSummary, AppVersion


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_online','is_passed','current_lat', 'current_lng')

@admin.register(UserStoreMoney)
class UserStoreMoneyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'increase_money', 'sum_money', 'user_left_money')

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display =  ('id', 'name')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'owner')

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','case_state', 'customer', 'create_time', 'on_address', 'off_time', 'off_address', 'case_money')

@admin.register(UserCaseShip)
class UserCaseShipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'case', 'state', 'countdown_second')

@admin.register(CaseSummary)
class CaseSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'case', 'driver_user_id', 'customer_name', 'increase_money', 'decrease_money')

@admin.register(MonthSummary)
class MonthSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'month_date')

@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('id','iOS_current_version', 'android_current_version')
