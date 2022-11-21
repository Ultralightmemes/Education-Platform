from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from education.models import Course, Lesson, Theme, Category, ExerciseTask, TestTask
from education.serializers import CourseSerializer, ThemeWithLessonSerializer, MultipleCourseSerializer, \
    CategorySerializer, LessonDetailSerializer, AnswerSerializer
from education.tasks import send_subscribe_mail
from user.models import User, UserCourse, UserLesson


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
        courses = Course.objects.filter(usercourse__user__email=user.email)
        for course in courses:
            lesson_num = Lesson.objects.filter(theme__course=course).count()
            if lesson_num == 0:
                course.percents = 0
            else:
                course.percents = int((Lesson.objects.filter(users__email=user.email, theme__course=course,
                                                             userlesson__is_done=True).count() / lesson_num) * 100)
            print(course.percents)
        serializer = MultipleCourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LessonDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Lesson.objects.filter(theme__course=self.kwargs['course_pk'], is_published=True).order_by(
            'theme__position', 'position')

    def list(self, request, pk=None, *args, **kwargs):
        instance = self.get_queryset().first()
        next_lesson = Lesson.objects.filter(theme=instance.theme,
                                            position__gt=instance.position).first() or Theme.objects.filter(
            position__gt=instance.theme.position).first().lessons.first() or None
        # print(Lesson.objects.all())
        # print(next_lesson)
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
    def answer(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = AnswerSerializer(request.data)
        user_lesson, created = UserLesson.objects.get_or_create(user=user,
                                                                lesson_id=serializer.data.get('lesson'))
        answer_counter = 0
        for test in serializer.data.get('tests'):
            if [option.id for option in TestTask.objects.get(pk=test.get('id')).options.filter(is_true=True)] == list(
                    map(int, test.get('answers'))):
                answer_counter += 1
        for exercise in serializer.data.get('exercises'):
            if ExerciseTask.objects.get(pk=exercise.get('id')).answer == exercise.get('answer'):
                answer_counter += 1
        try:
            user_lesson.percents = float(answer_counter / user_lesson.lesson.tasks.count()) * 100
        except:
            user_lesson.percents = 0
        user_lesson.is_done = True
        user_lesson.save()
        return Response()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, pk=None):
        objects = Course.objects.filter(categories=pk)
        serializer = MultipleCourseSerializer(objects, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='courses')
    def get_courses(self, request, pk=None):
        courses = Course.objects.filter(categories=pk, is_published=True)
        serializer = MultipleCourseSerializer(courses, many=True)
        return Response(serializer.data)
