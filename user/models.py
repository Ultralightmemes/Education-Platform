from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
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
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name='Почтовый адрес')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=255, blank=True, verbose_name='Отчество')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Работник')
    username = None
    courses = models.ManyToManyField(Course, through='UserCourse', related_name='users', verbose_name='Курсы')
    lessons = models.ManyToManyField(Lesson, through='UserLesson', related_name='users', verbose_name='Занятия')
    image = models.ImageField(upload_to='profile/%Y/%m/%d', blank=True, verbose_name='Аватар')

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email


class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, default=None, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'course')


class UserLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    percents = models.PositiveSmallIntegerField(validators=(MinValueValidator(0), MaxValueValidator(100)), default=0)
    is_done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'lesson')
