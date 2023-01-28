from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from common.service import get_object, get_or_create_object, filter_objects
from education.decorators import catch_does_not_exist, check_user_subscription_to_course
from education.models import Course, Lesson, Theme, Category, ExerciseTask, TestTask
from education.serializers import CourseSerializer, MultipleCourseSerializer, CategorySerializer, \
    LessonPaginationSerializer, ThemeWithLessonSerializer, RateSerializer, LessonDetailSerializer, AnswerSerializer, \
    CategoryDetailSerializer
from education.service import calculate_course_rating, annotate_courses, count_exercise_percents, annotate_themes
from education.tasks import send_subscribe_mail
from user.models import User, UserCourse, UserLesson


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.published.all()
    search_fields = ['name']
    ordering_fields = ['name']
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]

    action_serializers = {
        'retrieve': CourseSerializer,
        'list': MultipleCourseSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            return self.action_serializers.get(self.action, self.serializer_class)

        return super(CourseViewSet, self).get_serializer_class()

    @catch_does_not_exist
    def retrieve(self, request, pk=None, *args, **kwargs):
        course = get_object(Course.objects, prefetch_related=('themes', 'categories'), pk=pk)
        course.rating = calculate_course_rating(course)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path='follow')
    @catch_does_not_exist
    def follow_course(self, request, pk=None):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = get_object(User.objects, email=user.email)
        try:
            user_course_obj, created = get_or_create_object(UserCourse.objects, user=user, course_id=pk)
            # user_course_obj, created = UserCourse.objects.get_or_create(user=user, course_id=pk)
            if not created:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except IntegrityError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_course_obj.save()
        send_subscribe_mail.delay(user.email, user.first_name, user_course_obj.course.name)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False, url_path='my')
    def get_user_courses(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        courses = annotate_courses(user)
        serializer = MultipleCourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    @catch_does_not_exist
    def rate(self, request, pk=None):
        get_object(Course.objects, pk=pk)
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        instance = get_object(UserCourse.objects, course_id=pk, user=user)
        serializer = RateSerializer(data=request.data, instance=instance)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# TODO Rewrite to api_view and make teacher api
class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Lesson.objects.filter(theme__course=self.kwargs['course_pk'], is_published=True).order_by(
            'theme__position', 'position')

    def list(self, request, course_pk=None, *args, **kwargs):
        if not filter_objects(Course.objects, pk=course_pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance = self.get_queryset().first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            next_lesson = Lesson.objects.filter(theme=instance.theme,
                                                position__gt=instance.position).first() or Theme.objects.filter(
                position__gt=instance.theme.position).first().lessons.first()
            instance.next_lesson = next_lesson.id if next_lesson else None
        except AttributeError:
            instance.next_lesson = None
        instance.previous_lesson = None
        instance.exercises = ExerciseTask.objects.filter(lesson=instance, is_published=True)
        instance.tests = TestTask.objects.filter(lesson=instance, is_published=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        next_lesson = Lesson.objects.filter(theme=instance.theme,
                                            position__gt=instance.position).first() or Lesson.objects.filter(
            theme__position__gt=instance.theme.position).first() or None
        instance.next_lesson = next_lesson.id if next_lesson else None
        previous_lesson = Lesson.objects.filter(theme=instance.theme,
                                                position__lt=instance.position).last() or Lesson.objects.filter(
            theme__position__lt=instance.theme.position).last() or None
        instance.previous_lesson = previous_lesson.id if previous_lesson else None
        instance.exercises = ExerciseTask.objects.filter(lesson=instance, is_published=True)
        instance.tests = TestTask.objects.filter(lesson=instance, is_published=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # TODO Maybe needed to be rewritten
    @action(methods=['post'], detail=True)
    def answer(self, request, pk=None, course_pk=None):
        if not Course.objects.filter(pk=course_pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = AnswerSerializer(request.data)
        try:
            user_lesson, created = UserLesson.objects.get_or_create(user=user,
                                                                    lesson_id=pk)
        except IntegrityError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            user_lesson.percents = count_exercise_percents(serializer.data, user_lesson)
        except KeyError:
            user_lesson.percents = 100
        user_lesson.is_done = True
        user_lesson.save()
        return Response(status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
@catch_does_not_exist
@check_user_subscription_to_course
def user_theme_api_view(request, course_pk=None):
    user = request.user
    themes = annotate_themes(user, course_pk)
    serializer = ThemeWithLessonSerializer(themes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@catch_does_not_exist
def user_lesson_api_view(request, course_pk=None):
    if request.method == 'GET':
        user = request.user
        paginator = PageNumberPagination()
        paginator.page_size = 1
        course = Course.objects.get(pk=course_pk)
        if course not in user.courses.all():
            return Response(status=status.HTTP_403_FORBIDDEN)
        lessons = Lesson.objects.select_related('theme').order_by('theme__position', 'position').filter(
            theme__course=course,
            is_published=True)
        result_page = paginator.paginate_queryset(lessons, request)
        serializer = LessonPaginationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None, **kwargs):
        try:
            instance = Category.objects.prefetch_related('courses').get(pk=pk)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategoryDetailSerializer(instance, context={'request': request})
        return Response(serializer.data)
