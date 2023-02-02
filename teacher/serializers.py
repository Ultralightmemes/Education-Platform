from django.db.models import Max
from django.db.models.functions import Coalesce
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from education.models import Course, CourseCategories, Category, Theme, Lesson, ExerciseTask, Task, TestTask, TestOption
from education.serializers import CategorySerializer


class CourseListSerializer(ModelSerializer):
    num_themes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        exclude = ('text',
                   'author'
                   )


class CategoryDetailSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CourseCategorySerializer(serializers.ModelSerializer):
    category = CategoryDetailSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(),
                                                     source='category',
                                                     write_only=True,
                                                     )

    class Meta:
        model = CourseCategories
        fields = ('category',
                  'category_id',
                  )


class CreateCourseSerializer(ModelSerializer):
    publish_date = serializers.DateField(read_only=True)
    update_date = serializers.DateField(read_only=True)
    categories = CourseCategorySerializer(many=True)

    class Meta:
        model = Course
        fields = '__all__'

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        course = Course.objects.create(**validated_data)
        for category in categories_data:
            CourseCategories.objects.create(
                course=course,
                category=category.get('category'),
            )
        return course

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories')
        instance = super(CreateCourseSerializer, self).update(instance, validated_data)
        course_category = CourseCategories.objects.filter(course=instance)
        course_category.delete()
        for category in categories_data:
            CourseCategories.objects.create(
                course=instance,
                category=category.get('category'),
            )
        return instance


class CourseDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    rating = serializers.FloatField(read_only=True)
    publish_date = serializers.DateField(read_only=True)
    update_date = serializers.DateField(read_only=True)

    class Meta:
        model = Course
        exclude = ('author',)


class ThemeUpdateSerializer(ModelSerializer):
    position = serializers.IntegerField(required=False)

    class Meta:
        model = Theme
        fields = ['title',
                  'description',
                  'position',
                  'is_published'
                  ]


class ThemeSerializer(ModelSerializer):
    position = serializers.IntegerField(required=False)
    num_lessons = serializers.IntegerField(required=False, read_only=True)

    def create(self, validated_data):
        obj = Theme.objects.create(**validated_data)
        obj.position = Theme.objects.filter(course=obj.course).aggregate(position=Coalesce(Max('position'), 0)).get(
            'position') + 1
        obj.save()
        return obj

    class Meta:
        model = Theme
        fields = ['title',
                  'description',
                  'position',
                  'is_published',
                  'num_lessons',
                  ]


class CreateLessonSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        obj = Lesson.objects.create(**validated_data)
        obj.position = Lesson.objects.filter(theme=obj.theme).aggregate(position=Coalesce(Max('position'), 0)).get(
            'position') + 1
        obj.save()
        return obj

    class Meta:
        model = Lesson
        exclude = ('theme',
                   'update_date',
                   )


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseTask
        fields = '__all__'


class CreateExerciseSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        obj = ExerciseTask.objects.create(**validated_data)
        obj.classname = obj.__class__.__name__
        obj.position = Task.objects.filter(lesson=obj.lesson).aggregate(position=Coalesce(Max('position'), 0)) \
                           .get('position') + 1
        obj.save()
        return obj

    class Meta:
        model = ExerciseTask
        exclude = ('classname',
                   'lesson',
                   'position',
                   )


class TestTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestTask
        fields = '__all__'


class CreateOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestOption
        exclude = ('test',)


class CreateTestTaskSerializer(serializers.ModelSerializer):
    options = CreateOptionSerializer(many=True, required=False)

    def create(self, validated_data):
        try:
            options = validated_data.pop('options')
        except KeyError:
            options = None
        obj = TestTask.objects.create(**validated_data)
        obj.classname = obj.__class__.__name__
        obj.position = Task.objects.filter(lesson=obj.lesson).aggregate(position=Coalesce(Max('position'), 0)) \
                           .get('position') + 1
        if options:
            option_serializer = CreateOptionSerializer(data=options, many=True)
            if option_serializer.is_valid():
                option_serializer.save(test=obj)
            else:
                raise ValidationError
        obj.save()
        return obj

    def update(self, instance, validated_data):
        try:
            options = validated_data.pop('options')
        except KeyError:
            options = None
        instance = super(CreateTestTaskSerializer, self).update(instance, validated_data)
        if options:
            option_serializer = CreateOptionSerializer(data=options, many=True)
            if option_serializer.is_valid():
                option_serializer.save(test=instance)
            else:
                raise ValidationError
        instance.save()
        return instance

    class Meta:
        model = TestTask
        exclude = ('classname',
                   'position',
                   'lesson',
                   )


class TestOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestOption
        fields = '__all__'
