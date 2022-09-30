from itertools import chain

from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from education.models import Course, Lesson, Theme, Category, ExerciseTask, TestTask
from education.serializers import CourseSerializer, LessonSerializer, ThemeWithLessonSerializer, \
    MultipleCourseSerializer, CategorySerializer, LessonDetailSerializer
from user.models import User, UserCourse


class LessonPagination(PageNumberPagination):
    page_size = 1
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer

    action_serializers = {
        'retrieve': CourseSerializer,
        'list': MultipleCourseSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            return self.action_serializers.get(self.action, self.serializer_class)

        return super(CourseViewSet, self).get_serializer_class()

    @action(methods=['get'], detail=True, url_path='themes')
    def get_themes_with_lessons(self, request, pk=None):
        themes = Theme.objects.prefetch_related(Prefetch('lessons', Lesson.objects.filter(is_published=True))) \
            .filter(course=pk, is_published=True)
        serializer = ThemeWithLessonSerializer(themes, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path='follow')
    def follow_course(self, request, pk=None):
        user = User.objects.get(email=request.user.email)
        user_course_obj = UserCourse(user=user, course=pk)
        user_course_obj.save()
        return Response()


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LessonDetailSerializer

    def get_queryset(self):
        return Lesson.objects.filter(theme__course=self.kwargs['course_pk']).order_by('theme__position', 'position')

    def list(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset().first()
        instance.exercises = ExerciseTask.objects.filter(lesson=instance, is_published=True)
        instance.tests = TestTask.objects.filter(lesson=instance, is_published=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.exercises = ExerciseTask.objects.filter(lesson=instance, is_published=True)
        instance.tests = TestTask.objects.filter(lesson=instance, is_published=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(methods=['get'], detail=True, url_path='courses')
    def get_courses(self, request, pk=None):
        courses = Course.objects.filter(categories=pk, is_published=True)
        serializer = MultipleCourseSerializer(courses, many=True)
        return Response(serializer.data)
