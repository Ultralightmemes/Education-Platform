import functools
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from user.models import UserCourse


def ret(json_object, status=200):
    return Response(json_object, status=status)


def error_response(exception, status):
    res = {"errorMessage": str(exception),
           "traceback": traceback.format_exc()}
    return ret(res, status=status)


def catch_does_not_exist(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            with transaction.atomic():
                return fn(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            return error_response(e, 404)

    return inner


def check_user_subscription_to_course(fn):
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        try:
            UserCourse.objects.get(course_id=kwargs.get('course_pk'), user=request.user)
        except UserCourse.DoesNotExist:
            return error_response(PermissionDenied, 403)
        else:
            return fn(request, *args, **kwargs)

    return inner
