from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from education.decorators import catch_does_not_exist
from education.models import Course, Theme
from education.service import calculate_course_rating
from teacher.decorators import check_is_theme_author, check_is_course_author
from teacher.serializers import CourseListSerializer, CreateCourseSerializer, CourseDetailSerializer, \
    ThemeUpdateSerializer, ThemeSerializer
from teacher.service import TeacherPermission, get_themes_with_lessons_counted


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, TeacherPermission])
@catch_does_not_exist
def course_api_view(request):
    if request.method == 'GET':
        courses = Course.objects.filter(author=request.user)
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CreateCourseSerializer(data=request.data)
        if serializer.is_valid() and request.data:
            serializer.save(author=request.user)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'DELETE', 'PATCH'])
@permission_classes([IsAuthenticated, TeacherPermission])
@check_is_course_author
@catch_does_not_exist
def course_detail_api_view(request, pk=None):
    if request.method == 'GET':
        course = Course.objects.get(pk=pk)
        course.rating = calculate_course_rating(course)
        serializer = CourseDetailSerializer(course)
        return Response(serializer.data)

    if request.method == 'DELETE':
        course = Course.objects.get(pk=pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # TODO add category adding to serializer
    if request.method == 'PATCH':
        course = Course.objects.get(pk=pk)
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
        course = Course.objects.get(pk=course_pk)
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
        theme = Theme.objects.get(pk=pk)
        serializer = ThemeSerializer(theme)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        theme = Theme.objects.select_related('course').get(pk=pk)
        serializer = ThemeUpdateSerializer(theme, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        theme = Theme.objects.select_related('course').get(pk=pk)
        theme.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
