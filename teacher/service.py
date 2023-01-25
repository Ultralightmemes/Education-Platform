from rest_framework.permissions import BasePermission


class TeacherPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_teacher or request.user.is_superuser:
            return True
