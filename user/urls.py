from django.urls import path

from user.views import UserAPIView, logout_user, register_user

urlpatterns = [
    path('registration/', register_user, name='user-registration'),
    path('', UserAPIView.as_view(), name='user-info'),
    path('logout/', logout_user, name='user-logout'),
]
