from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from education.models import Course, Lesson, Theme, Category, ExerciseTask, TestOption, TestTask, CourseCategories
from user.models import UserCourse


class ThemeInCourseSerializer(ModelSerializer):
    class Meta:
        model = Theme
        exclude = ('course',
                   'is_published')


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id',
                  'name'
                  )


class MultipleCourseSerializer(ModelSerializer):
    categories = CategorySerializer(many=True)
    image = serializers.SerializerMethodField()
    percents = serializers.IntegerField(required=False)

    class Meta:
        model = Course
        fields = ('id',
                  'name',
                  'categories',
                  'image',
                  'percents',
                  )

    def get_image(self, course):
        request = self.context.get('request')
        return request.build_absolute_uri(course.image.url)


class CategoryDetailSerializer(ModelSerializer):
    courses = MultipleCourseSerializer(many=True)

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


class CourseSerializer(ModelSerializer):
    themes = ThemeInCourseSerializer(many=True)
    categories = CategorySerializer(many=True)
    rating = serializers.FloatField()

    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(ModelSerializer):
    is_done = serializers.BooleanField()
    is_auto_done = serializers.BooleanField()

    class Meta:
        model = Lesson
        fields = ['id',
                  'title',
                  'position',
                  'is_done',
                  'is_auto_done',
                  ]


class ThemeWithLessonSerializer(ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = Theme
        fields = ['id',
                  'title',
                  'position',
                  'lessons',
                  'course'
                  ]


class ExerciseTaskSerializer(ModelSerializer):
    class Meta:
        model = ExerciseTask
        exclude = ['lesson',
                   'is_published',
                   'answer'
                   ]


class TestOptionSerializer(ModelSerializer):
    class Meta:
        model = TestOption
        fields = ['id',
                  'text'
                  ]


class TestTaskSerializer(ModelSerializer):
    radio = serializers.SerializerMethodField('get_radio')
    options = TestOptionSerializer(many=True)

    def get_radio(self, test_task):
        return True if sum(option.is_true for option in test_task.options.all()) == 1 else False

    class Meta:
        model = TestTask
        exclude = ['lesson',
                   'is_published'
                   ]


class LessonDetailSerializer(ModelSerializer):
    exercises = ExerciseTaskSerializer(many=True)
    tests = TestTaskSerializer(many=True)
    next_lesson = serializers.CharField()
    previous_lesson = serializers.CharField()

    class Meta:
        model = Lesson
        exclude = ['position',
                   'is_published'
                   ]


class LessonPaginationSerializer(ModelSerializer):

    class Meta:
        model = Lesson
        exclude = ['update_date', 'is_published']


class ExerciseAnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    answer = serializers.CharField()


class TestAnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    answers = serializers.ListField(child=serializers.CharField())


class AnswerSerializer(serializers.Serializer):
    lesson = serializers.IntegerField()
    exercises = ExerciseAnswerSerializer(many=True)
    tests = TestAnswerSerializer(many=True)


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        fields = ('rating',
                  )
