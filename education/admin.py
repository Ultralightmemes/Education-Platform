from django.contrib import admin

from education.models import Lesson, VideoTask, ExerciseTask, Course, Theme, TestTask, TestOption


class LessonInline(admin.TabularInline):
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
    extra = 4


class ThemeInline(admin.TabularInline):
    model = Theme
    extra = 1


class TestTaskAdmin(admin.ModelAdmin):
    inlines = [
        TestOptionInline
    ]


class CourseAdmin(admin.ModelAdmin):
    inlines = [
        ThemeInline
    ]


class ThemeAdmin(admin.ModelAdmin):
    inlines = [
        LessonInline
    ]


admin.site.register(Course, CourseAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(VideoTask)
admin.site.register(ExerciseTask)
admin.site.register(TestTask, TestTaskAdmin)
