from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.service import filter_objects, get_object, delete_object
from education.decorators import catch_does_not_exist
from education.models import Course, Theme, Lesson, ExerciseTask, TestTask, TestOption
from education.service import calculate_course_rating
from teacher.decorators import check_is_theme_author, check_is_course_author, check_is_lesson_author, \
    check_is_task_author, check_if_option_author
from teacher.serializers import CourseListSerializer, CreateCourseSerializer, CourseDetailSerializer, \
    ThemeUpdateSerializer, ThemeSerializer, CreateLessonSerializer, LessonSerializer, ExerciseSerializer, \
    CreateExerciseSerializer, TestTaskSerializer, CreateTestTaskSerializer, TestOptionSerializer
from teacher.service import TeacherPermission, get_themes_with_lessons_counted


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, TeacherPermission])
@catch_does_not_exist
def course_api_view(request):
    if request.method == 'GET':
        courses = filter_objects(Course.objects, author=request.user)
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CreateCourseSerializer(data=request.data)
        if serializer.is_valid() and request.data:
            serializer.save(author=request.user)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated, TeacherPermission])
@check_is_course_author
@catch_does_not_exist
def course_detail_api_view(request, pk=None):
    if request.method == 'GET':
        course = get_object(Course.objects, pk=pk)
        course.rating = calculate_course_rating(course)
        serializer = CourseDetailSerializer(course)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        delete_object(Course.objects, pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PATCH':
        course = get_object(Course.objects, pk=pk)
        serializer = CreateCourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@catch_does_not_exist
@check_is_theme_author
def theme_api_view(request, course_pk=None):
    if request.method == 'GET':
        themes = get_themes_with_lessons_counted(course_pk)
        serializer = ThemeSerializer(themes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ThemeSerializer(data=request.data)
        course = get_object(Course.objects, pk=course_pk)
        if serializer.is_valid():
            serializer.save(course=course)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@catch_does_not_exist
@check_is_theme_author
def theme_detail_api_view(request, pk=None):
    if request.method == 'GET':
        theme = get_object(Theme.objects, pk=pk)
        serializer = ThemeSerializer(theme)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        theme = get_object(Theme.objects, prefetch_related=('course',), pk=pk)
        serializer = ThemeUpdateSerializer(theme, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        delete_object(Theme.objects, pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@catch_does_not_exist
@check_is_lesson_author
def lesson_api_view(request, theme_pk=None):
    if request.method == 'GET':
        lessons = filter_objects(Lesson.objects, theme_id=theme_pk)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        theme = get_object(Theme.objects, pk=theme_pk)
        serializer = CreateLessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(theme=theme)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@catch_does_not_exist
@check_is_lesson_author
def lesson_detail_api_view(request, pk=None):
    if request.method == 'GET':
        lesson = get_object(Lesson.objects, pk=pk)
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        lesson = get_object(Lesson.objects, pk=pk)
        serializer = CreateLessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        delete_object(Lesson.objects, pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@catch_does_not_exist
@check_is_task_author
def exercise_task_api_view(request, lesson_pk=None):
    if request.method == 'GET':
        exercises = filter_objects(ExerciseTask.objects, lesson_id=lesson_pk)
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        lesson = get_object(Lesson.objects, pk=lesson_pk)
        serializer = CreateExerciseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@catch_does_not_exist
@check_is_task_author
def exercise_task_detail_api_view(request, pk=None):
    if request.method == 'GET':
        exercise = get_object(ExerciseTask.objects, pk=pk)
        serializer = ExerciseSerializer(exercise)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        exercise = get_object(ExerciseTask.objects, pk=pk)
        serializer = CreateExerciseSerializer(exercise, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        delete_object(ExerciseTask.objects, pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@catch_does_not_exist
@check_is_task_author
def task_test_api_view(request, lesson_pk=None):
    if request.method == 'GET':
        tests = filter_objects(TestTask.objects, lesson_id=lesson_pk)
        serializer = TestTaskSerializer(tests, many=True)
        return Response(serializer.data)
# TODO decide what to do with options(better to create different view for post delete and update)
    elif request.method == 'POST':
        lesson = get_object(Lesson.objects, pk=lesson_pk)
        serializer = CreateTestTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@catch_does_not_exist
@check_is_task_author
def task_test_detail_api_view(request, pk=None):
    if request.method == 'GET':
        test = get_object(TestTask.objects, pk=pk)
        serializer = TestTaskSerializer(test)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        test = get_object(TestTask.objects, pk=pk)
        serializer = CreateTestTaskSerializer(test, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        delete_object(TestTask.objects, pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH', 'DELETE'])
@catch_does_not_exist
@check_if_option_author
def option_api_view(request, pk=None):
    if request.method == 'DELETE':
        delete_object(TestOption.objects, pk=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PATCH':
        option = get_object(TestOption.objects, pk=pk)
        serializer = TestOptionSerializer(option, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)
