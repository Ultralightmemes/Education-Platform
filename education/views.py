from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from education.models import Course, Lesson, Theme, Category, ExerciseTask, TestTask
from education.serializers import CourseSerializer, ThemeWithLessonSerializer, MultipleCourseSerializer, \
    CategorySerializer, LessonDetailSerializer, AnswerSerializer, RateSerializer
from education.service import calculate_course_rate, annotate_themes, annotate_courses, count_exercise_percents
from education.tasks import send_subscribe_mail
from user.models import User, UserCourse, UserLesson


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    permission_classes = [AllowAny]

    action_serializers = {
        'retrieve': CourseSerializer,
        'list': MultipleCourseSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            return self.action_serializers.get(self.action, self.serializer_class)

        return super(CourseViewSet, self).get_serializer_class()

    def retrieve(self, request, pk=None):
        try:
            course = Course.objects.prefetch_related('themes').get(pk=pk)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        course.rating = calculate_course_rate(course)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='themes')
    def get_themes_with_lessons(self, request, pk=None):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        themes = annotate_themes(user, pk)
        serializer = ThemeWithLessonSerializer(themes, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path='follow')
    def follow_course(self, request, pk=None):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user = User.objects.get(email=user.email)
        user_course_obj, created = UserCourse.objects.get_or_create(user=user, course_id=pk)
        if not created:
            return Response()
        user_course_obj.save()
        send_subscribe_mail.delay(user.email, user.first_name, user_course_obj.course.name)
        return Response()

    @action(methods=['get'], detail=False, url_path='my')
    def get_user_courses(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        courses = annotate_courses(user)
        serializer = MultipleCourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def rate(self, request, pk=None):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        instance = UserCourse.objects.get(course_id=pk, user=user)
        serializer = RateSerializer(data=request.data, instance=instance)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Lesson.objects.filter(theme__course=self.kwargs['course_pk'], is_published=True).order_by(
            'theme__position', 'position')

    def list(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset().first()
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        next_lesson = Lesson.objects.filter(theme=instance.theme,
                                            position__gt=instance.position).first() or Theme.objects.filter(
            position__gt=instance.theme.position).first().lessons.first() or None
        instance.next_lesson = next_lesson.id if next_lesson else None
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

    @action(methods=['post'], detail=True)
    def answer(self, request, pk=None, course_pk=None):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = AnswerSerializer(request.data)
        user_lesson, created = UserLesson.objects.get_or_create(user=user,
                                                                lesson_id=pk)
        user_lesson.percents = count_exercise_percents(serializer.data, user_lesson)
        user_lesson.is_done = True
        user_lesson.save()
        return Response()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        objects = Course.objects.filter(categories=pk)
        serializer = MultipleCourseSerializer(objects, many=True, context={'request': request})
        return Response(serializer.data)
