from django.contrib import admin
from django.db.models import Max
from django.db.models.functions import Coalesce
from django.views import View
from rest_framework.response import Response

from education.models import Theme, Lesson, Task


class SaveThemeMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.position:
            obj.position = Theme.objects.filter(course=obj.course).aggregate(position=Coalesce(Max('position'), 0)) \
                               .get('position') + 1
        super().save_model(request, obj, form, change)


class SaveLessonMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.position:
            obj.position = Lesson.objects.filter(theme=obj.theme).aggregate(position=Coalesce(Max('position'), 0))\
                .get('position') + 1
        super().save_model(request, obj, form, change)


class SaveTaskMixin(admin.ModelAdmin):
    exclude = ('position', 'classname')

    def save_model(self, request, obj, form, change):
        if not obj.position:
            obj.classname = obj.__class__.__name__
            obj.position = Task.objects.filter(lesson=obj.lesson).aggregate(position=Coalesce(Max('position'), 0)) \
                               .get('position') + 1
        super().save_model(request, obj, form, change)


class ExceptionHandlerMixin(View):

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, *kwargs)
        except Exception as e:
            return self._response({'errorMessage': e.message}, status=400)

        if isinstance(response, (dict, list)):
            return self._response(response)
        else:
            return response

    @staticmethod
    def _response(data, *, status=200):
        return Response(data, status=status)
