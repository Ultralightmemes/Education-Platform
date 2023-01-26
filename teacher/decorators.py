import functools

from rest_framework.exceptions import PermissionDenied

from education.decorators import error_response
from education.models import Course, Theme


def check_is_theme_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            course = Course.objects.get(pk=kwargs.get('course_pk'))
        except:
            course = Theme.objects.get(pk=kwargs.get('pk')).course
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner


def check_is_course_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            course = Course.objects.get(pk=kwargs.get('pk'))
        except Course.DoesNotExist as e:
            return error_response(e, 403)
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner
