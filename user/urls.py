from django.urls import path, include
from rest_framework.routers import SimpleRouter

from user.views import RegistrationAPIView, UserAPIView

urlpatterns = [
    path('users/', RegistrationAPIView.as_view()),
    # path('answer/', AnswerAPIView.as_view()),
    path('user/', UserAPIView.as_view()),
    # path('image/', ImageAPIView.as_view()),
]
