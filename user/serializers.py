from rest_framework import serializers

from user.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['email',
                  'first_name',
                  'last_name',
                  'password'
                  ]

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


