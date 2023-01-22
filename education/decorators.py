import functools
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.response import Response


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
