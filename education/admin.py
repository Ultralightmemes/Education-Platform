from adminsortable2.admin import SortableStackedInline, SortableAdminMixin, SortableAdminBase, SortableTabularInline
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.utils.text import format_lazy

from education.models import Lesson, VideoTask, ExerciseTask, Course, Theme, TestTask, TestOption, Category


class LessonInline(SortableTabularInline):
    model = Lesson
    fk_name = 'theme'
    exclude = ['text']
    extra = 1


class VideoTaskInline(admin.TabularInline):
    model = VideoTask
    fk_name = 'theme'
    exclude = ['text', 'video']
    extra = 1


class ExerciseTaskInline(admin.TabularInline):
    model = ExerciseTask
    fk_name = 'theme'
    exclude = ['text', 'answer']
    extra = 1


class TestTaskInline(admin.TabularInline):
    model = TestTask
    fk_name = 'theme'
    exclude = ['text']
    extra = 1


class TestOptionInline(admin.TabularInline):
    model = TestOption
    extra = 2


class ThemeInline(SortableTabularInline):
    model = Theme
    extra = 1


class CategoryInline(admin.StackedInline):
    model = Category
    filter_horizontal = ('courses',)


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = ['theme', 'title', 'update_date']
    inlines = [TestOptionInline]
    list_filter = ['theme']
    search_fields = ['title__icontains']


class CourseAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=('Категории'),
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
class ThemeAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_counter']
    inlines = [LessonInline]
    list_filter = ('course',)
    search_fields = ['title__icontains']

    def lesson_counter(self, obj):
        return obj.lessons.count()

    lesson_counter.short_description = 'Количество занятий'


@admin.register(VideoTask)
class VideoTaskAdmin(admin.ModelAdmin):
    list_display = ['theme', 'title', 'file_is_uploaded', 'update_date']
    list_filter = ('theme',)
    search_fields = ['title__icontains']

    def file_is_uploaded(self, obj):
        return True if obj.video else False

    file_is_uploaded.boolean = True
    file_is_uploaded.short_description = 'Видео загружено'


@admin.register(ExerciseTask)
class ExerciseTaskAdmin(admin.ModelAdmin):
    list_display = ['theme', 'title', 'update_date']
    search_fields = ['title__icontains']
    list_filter = ('theme',)


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
