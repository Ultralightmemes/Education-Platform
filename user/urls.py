from django.urls import path

from user.views import RegistrationAPIView, AnswerAPIView

urlpatterns = [
    path('users/', RegistrationAPIView.as_view()),
    path('answer/', AnswerAPIView.as_view()),
]