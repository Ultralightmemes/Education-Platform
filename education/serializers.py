from rest_framework.serializers import ModelSerializer

from education.models import Course, Lesson, Theme, Category, ExerciseTask, TestOption, TestTask


class ThemeInCourseSerializer(ModelSerializer):
    class Meta:
        model = Theme
        exclude = ('course', 'is_published')


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class CourseSerializer(ModelSerializer):
    themes = ThemeInCourseSerializer(many=True)
    categories = CategorySerializer(many=True)

    class Meta:
        model = Course
        fields = '__all__'


class MultipleCourseSerializer(ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'categories')


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'position']


class ThemeWithLessonSerializer(ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Theme
        fields = ['id', 'title', 'position', 'lessons']


class ExerciseTaskSerializer(ModelSerializer):
    class Meta:
        model = ExerciseTask
        exclude = ['lesson', 'is_published', 'answer']


class TestOptionSerializer(ModelSerializer):
    class Meta:
        model = TestOption
        fields = ['id', 'text']


class TestTaskSerializer(ModelSerializer):
    options = TestOptionSerializer(many=True)

    class Meta:
        model = TestTask
        exclude = ['lesson', 'is_published']


class LessonDetailSerializer(ModelSerializer):
    exercises = ExerciseTaskSerializer(many=True)
    tests = TestTaskSerializer(many=True)

    class Meta:
        model = Lesson
        exclude = ['position', 'is_published']
