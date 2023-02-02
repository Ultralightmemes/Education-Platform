from django.urls import path

from teacher.views import theme_api_view, theme_detail_api_view, course_api_view, course_detail_api_view, \
    lesson_api_view, lesson_detail_api_view, exercise_task_api_view, exercise_task_detail_api_view, \
    task_test_detail_api_view, task_test_api_view, option_api_view

urlpatterns = [
    path('course/<int:course_pk>/theme/', theme_api_view, name='teacher-theme-list'),
    path('theme/<int:pk>/', theme_detail_api_view, name='teacher-theme-detail'),
    path('course/', course_api_view, name='teacher-course'),
    path('course/<int:pk>/', course_detail_api_view, name='teacher-course-detail'),
    path('theme/<int:theme_pk>/lesson/', lesson_api_view, name='teacher-lesson'),
    path('lesson/<int:pk>/', lesson_detail_api_view, name='teacher-lesson-detail'),
    path('lesson/<int:lesson_pk>/exercise/', exercise_task_api_view, name='teacher-exercise'),
    path('exercise/<int:pk>/', exercise_task_detail_api_view, name='teacher-exercise-detail'),
    path('lesson/<int:lesson_pk>/test/', task_test_api_view, name='teacher-test'),
    path('test/<int:pk>/', task_test_detail_api_view, name='teacher-test-detail'),
    path('option/<int:pk>/', option_api_view, name='teacher-option-detail'),
]
