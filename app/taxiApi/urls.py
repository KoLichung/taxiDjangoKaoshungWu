from django.urls import path, include
from rest_framework.routers import DefaultRouter

from taxiApi import views

router = DefaultRouter()
router.register('user_store_moneys', views.UserStoreMoneyViewSet)
router.register('user_cases', views.UserCaseViewSet)
router.register('get_cases', views.GetCaseViewSet)
router.register('car_teams', views.CarTeamViewSet)

app_name = 'taxiApi'

urlpatterns = [
    path('', include(router.urls)),
    path('update_lat_lng', views.UpdateLatLngView.as_view()),
    path('case_confirm', views.CaseConfirmView.as_view()),
    path('case_arrived', views.CaseArrivedView.as_view()),
    path('case_catched', views.CaseCatchedView.as_view()),
    path('case_finished', views.CaseFinishedView.as_view()),
    path('case_canceled', views.CaseCanceledView.as_view()),
    path('update_user_online_state', views.UpdateUserOnlineState.as_view()),
    path('get_current_version', views.AppVersionView.as_view()),
]