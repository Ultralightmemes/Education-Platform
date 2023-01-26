from django.db.models import Count
from rest_framework.permissions import BasePermission

from education.models import Theme


class TeacherPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_teacher or request.user.is_superuser:
            return True


def get_themes_with_lessons_counted(course_pk):
    return Theme.objects.filter(course_id=course_pk).annotate(num_lessons=Count('lessons'))
