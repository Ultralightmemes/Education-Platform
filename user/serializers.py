from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from six import text_type

from user.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    tokens = serializers.SerializerMethodField(method_name='get_tokens')
    email = serializers.CharField()

    class Meta:
        model = User
        fields = ['email',
                  'first_name',
                  'last_name',
                  'password',
                  'tokens',
                  ]

    def get_tokens(self, user):
        tokens = RefreshToken.for_user(user)
        refresh_token = text_type(tokens)
        access_token = text_type(tokens.access_token)
        data = {
            'refresh': refresh_token,
            'access': access_token
        }
        return data

    def validate_email(self, value):
        if value and User.objects.filter(email__exact=value).exists():
            raise serializers.ValidationError('User wih same email is already registered')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['email',
                  'first_name',
                  'last_name',
                  'patronymic',
                  'image',
                  'is_staff'
                  ]


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['image']


class AnswerSerializer(serializers.Serializer):
    classname = serializers.CharField(max_length=255, read_only=True)
    lesson_id = serializers.IntegerField(read_only=True)
    answer_id = serializers.ListField(child=serializers.IntegerField(), required=False)
    answer = serializers.CharField(max_length=255, required=False)


