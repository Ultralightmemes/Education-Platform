from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from education.models import TestTask, ExerciseTask
from user.models import User
from user.serializers import RegistrationSerializer, AnswerSerializer, UserSerializer, ImageSerializer


class RegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


# class ImageAPIView(generics.UpdateAPIView):
#     def patch(self, request, *args, **kwargs):
#         user = User.objects.get(email=request.user.email)
#         serializer = ImageSerializer(user, request.data, partial=True)
#         # parser_classes = (MultiPartParser, FormParser)
#         if serializer.is_valid():
#             serializer.save()
#         print(serializer.data)
#         return Response()


class UserAPIView(generics.RetrieveUpdateAPIView):
    def get(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(email=request.user.email)
        serializer = UserSerializer(user)
        print(serializer.data)
        return Response(serializer.data)

    def patch(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(email=request.user.email)
        serializer = UserSerializer(user, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        print(serializer.data)
        return Response()


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            print(token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# class AnswerAPIView(generics.CreateAPIView):
#     serializer_class = AnswerSerializer
#
#     def post(self, request, *args, **kwargs):
#         user = User.objects.get(email=request.user.email)
#         lesson_class = request.data.get('classname')
#         print(lesson_class)
#         if lesson_class == TestTask.__name__:
#             lesson = TestTask.objects.get(pk=request.data.get('lesson_id'))
#             if set(lesson.options.filter(is_true=True)) == set(
#                     lesson.options.filter(pk__in=request.data.get('answer_id'))):
#                 print(1)
#         elif lesson_class == ExerciseTask.__name__:
#             lesson = ExerciseTask.objects.get(pk=request.data.get('lesson_id'))
#         return Response()
