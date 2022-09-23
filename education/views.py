from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from education.models import Course, Lesson
from education.serializers import CourseSerializer, LessonSerializer


class TaskPagination(PageNumberPagination):
    page_size = 1
    page_query_param = 'page'
    page_size_query_param = 'page_size'


    # def get_paginated_response(self, data):
    #     return Response({
    #         'next': self.get_next_link() if self.page.has_next() else
    #     })
    #
    # def get_next_theme(self):
    #     self.page.


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(methods=['get'], detail=True, url_name='tasks')
    def get_paginated_task(self, request, pk=None):
        paginator = TaskPagination()
        tasks = Lesson.objects.filter(theme__course=pk).order_by('theme__position', 'position')
        result_page = paginator.paginate_queryset(tasks, request)
        serializer = LessonSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)




