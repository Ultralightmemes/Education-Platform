import functools


def prefetch_related_decorator(function):
    @functools.wraps(function)
    def wrapper(objects, prefetch_related=(), **kwargs):
        return function(objects.prefetch_related(*prefetch_related), **kwargs)

    return wrapper


def select_related_decorator(function):
    @functools.wraps(function)
    def wrapper(objects, select_related=(), **kwargs):
        return function(objects.select_related(*select_related), **kwargs)

    return wrapper


@prefetch_related_decorator
@select_related_decorator
def get_object(objects, **kwargs):
    return objects.get(**kwargs)


@prefetch_related_decorator
@select_related_decorator
def get_or_create_object(objects, **kwargs):
    return objects.get_or_create(**kwargs)


def delete_object(objects, **kwargs):
    obj = objects.get(**kwargs)
    obj.delete()


@prefetch_related_decorator
@select_related_decorator
def get_all_objects(objects):
    return objects.all()


@prefetch_related_decorator
@select_related_decorator
def filter_objects(objects, **kwargs):
    return objects.filter(**kwargs)
