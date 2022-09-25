from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from education.models import Course, Lesson


class UserAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Пользователь должен иметь электронную почту')
        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, password):
        if password is None:
            raise TypeError('Суперпользователь должен иметь пароль.')
        user = self.create_user(email, password=password, first_name=first_name, last_name=last_name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    username = None
    courses = models.ManyToManyField(Course, through='UserCourse', related_name='users')
    lessons = models.ManyToManyField(Lesson, through='UserLesson', related_name='users')
    image = models.ImageField(upload_to='profile/%Y/%m/%d', null=True, blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'surname']

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'course')


class UserLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'lesson')
