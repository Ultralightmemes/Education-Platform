from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from education.decorators import catch_does_not_exist
from education.models import Course, Theme
from education.serializers import ThemeWithLessonSerializer, ThemeSerializer, ThemeUpdateSerializer
from education.service import annotate_themes
from teacher.decorators import check_is_author
from teacher.service import TeacherPermission


@api_view(['GET', 'POST'])
@catch_does_not_exist
@check_is_author
# @permission_classes([TeacherPermission, ])
def theme_api_view(request, course_pk=None):
    if request.method == 'GET':
        user = request.user
        themes = annotate_themes(user, course_pk)
        # TODO Need to choose what serializer to use: Theme or ThemeWithLesson
        serializer = ThemeWithLessonSerializer(themes, many=True)
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
@check_is_author
# @permission_classes([TeacherPermission, ])
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
