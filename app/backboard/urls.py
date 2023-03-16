from django.urls import path, include
from . import views
from django.shortcuts import render
from django.http import HttpResponse 



urlpatterns = [
    # path('', views.home, name = 'index'), 
    path('home', views.home, name = 'home'),
    path('dispatch_inquire', views.dispatch_inquire, name = 'dispatch_inquire'), 
    path('', views.dispatch_management, name = 'dispatch_management'),
    path('passengers', views.passengers, name = 'passengers'), 
    path('drivers', views.drivers, name = 'drivers'),
    path('accounting_records', views.accounting_records, name = 'accounting_records'),
    # path('accounting_statistics', views.accounting_statistics, name = 'accounting_statistics'), 
    path('credit_topup', views.credit_topup, name = 'credit_topup'),
    path('', include('django.contrib.auth.urls')),
    path('logout', views.logout, name='backboard_logout'),
    path('ajax_get_drivers/', views.ajax_get_drivers, name='ajax_get_drivers')
]