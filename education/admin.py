from adminsortable2.admin import SortableAdminBase, SortableTabularInline
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.utils.text import format_lazy

from education.mixins import SaveTaskMixin, SaveThemeMixin, SaveLessonMixin
from education.models import Lesson, ExerciseTask, Course, Theme, TestTask, TestOption, Category, Task


class LessonInline(SortableTabularInline):
    model = Lesson
    exclude = ['text', 'video']
    extra = 1


class TaskInline(SortableTabularInline):
    model = Task
    fk_name = 'lesson'
    fields = ['title', 'is_published']
    extra = 1
    max_num = 10

    def has_add_permission(self, request, obj):
        return False


class TestOptionInline(admin.TabularInline):
    model = TestOption
    extra = 2
    max_num = 5


class ThemeInline(SortableTabularInline):
    model = Theme
    extra = 1
    exclude = ('description',)


class CategoryInline(admin.StackedInline):
    model = Category
    filter_horizontal = ('courses',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    filter_horizontal = ['courses']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        db = kwargs.get('using')

        if db_field.name == 'courses':
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        if 'queryset' not in kwargs:
            queryset = Course.objects.all()
            if queryset is not None:
                kwargs['queryset'] = queryset
        form_field = db_field.formfield(**kwargs)
        msg = 'Hold down “Control”, or “Command” on a Mac, to select more than one.'
        help_text = form_field.help_text
        form_field.help_text = (
            format_lazy('{} {}', help_text, msg) if help_text else msg
        )
        return form_field


class CourseAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Категории',
            is_stacked=False
        )
    )

    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CourseAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['categories'].initial = self.instance.categories.all()

    def save(self, commit=True):
        course = super(CourseAdminForm, self).save(commit=False)

        if commit:
            course.save()

        if course.pk:
            course.categories.set(self.cleaned_data['categories'])
            self.save_m2m()

        return course


@admin.register(Course)
class CourseAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['name', 'is_published', 'publish_date', 'update_date']
    inlines = [ThemeInline]
    search_fields = ['name__icontains']
    filter_horizontal = ['categories']
    list_filter = ('categories',)
    form = CourseAdminForm


@admin.register(Theme)
class ThemeAdmin(SaveThemeMixin, SortableAdminBase, admin.ModelAdmin):
    list_display = ['title', 'course', 'is_published', 'lesson_counter']
    inlines = [LessonInline]
    list_filter = ('course',)
    search_fields = ['title__icontains']
    exclude = ('position',)

    def lesson_counter(self, obj):
        return obj.lessons.count()

    lesson_counter.short_description = 'Количество заданий'


@admin.register(Lesson)
class LessonAdmin(SaveLessonMixin, SortableAdminBase, admin.ModelAdmin):
    list_display = ['title', 'theme', 'is_published', 'update_date']
    exclude = ('position', )
    list_filter = ['theme']
    search_fields = ['title__icontains']
    inlines = [TaskInline]


@admin.register(TestTask)
class TestTaskAdmin(SaveTaskMixin, admin.ModelAdmin):
    list_display = ['title', 'lesson', 'is_published']
    inlines = [TestOptionInline]
    list_filter = ['lesson']
    search_fields = ['title__icontains']


@admin.register(ExerciseTask)
class ExerciseTaskAdmin(SaveTaskMixin, admin.ModelAdmin):
    list_display = ['title', 'lesson', 'is_published']
    search_fields = ['title__icontains']
    list_filter = ['lesson']
