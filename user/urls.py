from django.urls import path

from user.views import RegistrationAPIView

urlpatterns = [
    path('users/', RegistrationAPIView.as_view()),
]