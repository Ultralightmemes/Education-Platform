import functools

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied

from common.service import get_object
from education.decorators import error_response
from education.models import Course, Theme, Lesson, Task, TestOption


def check_is_lesson_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            if 'theme_pk' in kwargs.keys():
                course = get_object(Theme.objects, select_related=('course',), pk=kwargs.get('theme_pk')).course
            else:
                course = get_object(Lesson.objects, select_related=('theme',),
                                    pk=kwargs.get('pk')).theme.course
        except ObjectDoesNotExist as e:
            return error_response(e, 404)
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner


def check_is_theme_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            if 'course_pk' in kwargs.keys():
                course = get_object(Course.objects, pk=kwargs.get('course_pk'))
            else:
                course = get_object(Theme.objects, select_related=('course',), pk=kwargs.get('pk')).course
        except ObjectDoesNotExist as e:
            return error_response(e, 404)
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner


def check_is_course_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            course = get_object(Course.objects, pk=kwargs.get('pk'))
        except Course.DoesNotExist as e:
            return error_response(e, 404)
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner


def check_is_task_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            if 'lesson_pk' in kwargs:
                course = get_object(Lesson.objects, select_related=('theme',), pk=kwargs.get('lesson_pk')).theme.course
            else:
                course = get_object(Task.objects, select_related=('lesson',), pk=kwargs.get('pk')).lesson.theme.course
        except ObjectDoesNotExist as e:
            return error_response(e, 404)
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner


def check_if_option_author(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            course = get_object(TestOption.objects, select_related=('test',),
                                pk=kwargs.get('pk')).test.lesson.theme.course
        except ObjectDoesNotExist as e:
            return error_response(e, 404)
        if request.user == course.author:
            return fn(request, *args, **kwargs)
        else:
            return error_response(PermissionDenied, 403)

    return inner
