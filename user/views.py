from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from user.models import User
from user.serializers import RegistrationSerializer


class RegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    # def post(self, request, *args, **kwargs):
    #     print(request.data)
    #     user = request.data.get('user', {})
    #
    #     serializer = self.serializer_class(data=user)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
