from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from education.models import Course, CourseCategories, Category, Theme
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
        exclude = ('author', )


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

    class Meta:
        model = Theme
        fields = ['title',
                  'description',
                  'position',
                  'is_published',
                  'num_lessons',
                  ]