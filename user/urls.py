from django.urls import path

from user.views import RegistrationAPIView, UserAPIView, LogoutAPIView

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view(), name='user-registration'),
    path('user/', UserAPIView.as_view(), name='user-info'),
    path('logout/', LogoutAPIView.as_view(), name='user-logout'),
]
