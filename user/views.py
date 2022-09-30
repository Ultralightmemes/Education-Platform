from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from education.models import TestTask, ExerciseTask
from user.models import User
from user.serializers import RegistrationSerializer, AnswerSerializer


class RegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


class AnswerAPIView(generics.CreateAPIView):
    serializer_class = AnswerSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.get(email=request.user.email)
        lesson_class = request.data.get('classname')
        print(lesson_class)
        if lesson_class == TestTask.__name__:
            lesson = TestTask.objects.get(pk=request.data.get('lesson_id'))
            if set(lesson.options.filter(is_true=True)) == set(
                    lesson.options.filter(pk__in=request.data.get('answer_id'))):
                print(1)
        elif lesson_class == ExerciseTask.__name__:
            lesson = ExerciseTask.objects.get(pk=request.data.get('lesson_id'))
        return Response()
