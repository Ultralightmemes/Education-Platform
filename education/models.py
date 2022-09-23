from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    courses = models.ManyToManyField('Course', through='CourseCategories', verbose_name='Курсы',
                                     related_name='categories')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    publish_date = models.DateField(default=timezone.now, verbose_name='Создан')
    update_date = models.DateField(auto_now=True, verbose_name='Обновлён')
    is_published = models.BooleanField(default=False, verbose_name='Опубликован')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.name


class Theme(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс', related_name='themes')
    position = models.IntegerField(verbose_name='Позиция', validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        unique_together = ['position', 'course']
        ordering = ('position',)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    theme = models.ForeignKey(Theme, on_delete=models.PROTECT, verbose_name='Тема', related_name='lessons')
    position = models.IntegerField(verbose_name='Позиция', validators=[MinValueValidator(1)])
    update_date = models.DateField(auto_now=True, verbose_name='Обновлён')
    text = models.TextField(verbose_name='Текст')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        unique_together = ['position', 'theme']
        ordering = ('position',)

    def __str__(self):
        return self.title


class VideoTask(Lesson):
    video = models.FileField(verbose_name='Видео')

    class Meta:
        verbose_name = 'Видеозадание'
        verbose_name_plural = 'Видеозадания'


class ExerciseTask(Lesson):
    answer = models.CharField(max_length=255, verbose_name='Ответ')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class TestOption(models.Model):
    text = models.CharField(max_length=255, verbose_name='Вариант')
    is_true = models.BooleanField(verbose_name='Правильный')
    test = models.ForeignKey('TestTask', on_delete=models.CASCADE, verbose_name='Тест')

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'


class TestTask(Lesson):
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class CourseCategories(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
