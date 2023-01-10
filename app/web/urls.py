from django.urls import path, include
from . import views
from .views import *
from django.shortcuts import render
from django.http import HttpResponse


urlpatterns = [
    path('', views.booking, name='booking'),
    path('direct_call', views.direct_call, name='direct_call'),
    path('map', views.map, name='map'),
    path('ajax_call_and_wait/', views.ajax_call_and_wait, name='ajax_call_and_wait'),
    path('ajax_check_user_phone_and_direct_call/', views.ajax_check_user_phone_and_direct_call, name='ajax_check_user_phone_and_direct_call'),
    path('intervalCheck/', views.intervalCheck, name='intervalCheck'),
    path('ajax_cancel_case/', views.ajax_cancel_case, name='ajax_cancel_case'),
    path('ajax_cancel_case_by_case_id/', views.ajax_cancel_case_by_case_id, name='ajax_cancel_case_by_case_id'),
    path('ajax_update_lat_lng/', views.ajax_update_lat_lng, name='ajax_update_lat_lng'),
    path('ajax_direct_call_wait/', views.ajax_direct_call_wait, name='ajax_direct_call_wait'),
]
