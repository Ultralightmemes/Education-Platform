from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from common.service import get_object, get_or_create_object, save_object, filter_objects
from education.decorators import catch_does_not_exist, check_user_subscription_to_course, \
    check_user_subscription_to_lesson
from education.models import Course, Lesson, Category
from education.serializers import CourseSerializer, MultipleCourseSerializer, CategorySerializer, \
    LessonPaginationSerializer, ThemeWithLessonSerializer, RateSerializer, AnswerSerializer, \
    CategoryDetailSerializer
from education.service import calculate_course_rating, annotate_courses, count_exercise_percents, annotate_themes
from education.tasks import send_subscribe_mail
from user.models import User, UserCourse, UserLesson


class LessonPagination(PageNumberPagination):
    page_size = 1


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

    @action(methods=['get'], detail=False, url_path='my')
    def get_user_courses(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        courses = annotate_courses(user)
        serializer = MultipleCourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


@api_view(['POST'])
@catch_does_not_exist
@permission_classes([IsAuthenticated])
def follow_course_api_view(request, pk=None):
    user = request.user
    user = get_object(User.objects, email=user.email)
    user_course_obj, created = get_or_create_object(UserCourse.objects, user=user, course_id=pk)
    if not created:
        return Response(status=status.HTTP_204_NO_CONTENT)
    save_object(user_course_obj)
    send_subscribe_mail.delay(user.email, user.first_name, user_course_obj.course.name)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
@catch_does_not_exist
@check_user_subscription_to_course
def rate_course_api_view(request, pk=None):
    user = request.user
    instance = get_object(UserCourse.objects, course_id=pk, user=user)
    serializer = RateSerializer(data=request.data, instance=instance)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@catch_does_not_exist
@check_user_subscription_to_course
def user_theme_api_view(request, course_pk=None):
    user = request.user
    themes = annotate_themes(user, course_pk)
    serializer = ThemeWithLessonSerializer(themes, many=True)
    return Response(serializer.data)


# TODO pagination will perform using count number of lesson
@api_view(['GET'])
@catch_does_not_exist
@check_user_subscription_to_course
@permission_classes([IsAuthenticated])
def user_lesson_api_view(request, course_pk=None):
    if request.method == 'GET':
        paginator = LessonPagination()
        course = get_object(Course.objects, pk=course_pk)
        lessons = filter_objects(Lesson.objects,
                                 select_related=('theme',),
                                 order_by=('theme__position', 'position'),
                                 theme__course=course,
                                 is_published=True,
                                 )
        result_page = paginator.paginate_queryset(lessons, request)
        serializer = LessonPaginationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@catch_does_not_exist
@check_user_subscription_to_lesson
@permission_classes([IsAuthenticated])
def lesson_answer_api_view(request, pk=None):
    user = request.user
    serializer = AnswerSerializer(data=request.data)
    if serializer.is_valid():
        user_lesson, created = UserLesson.objects.get_or_create(user=user, lesson_id=pk)
        user_lesson.percents = count_exercise_percents(serializer.validated_data, user_lesson)
        user_lesson.is_done = True
        user_lesson.save()
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_202_ACCEPTED)


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
