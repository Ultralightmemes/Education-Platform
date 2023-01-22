from django.urls import path

from user.views import RegistrationAPIView, UserAPIView, logout_user

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view(), name='user-registration'),
    path('', UserAPIView.as_view(), name='user-info'),
    path('logout/', logout_user, name='user-logout'),
]
