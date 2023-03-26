from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from education import views
from education.views import user_lesson_api_view, user_theme_api_view, follow_course_api_view, rate_course_api_view, \
    lesson_answer_api_view, task_test_api_view, exercise_api_view

router = SimpleRouter()
router.register(r'course', views.CourseViewSet, basename='education-course')
router.register(r'category', views.CategoryViewSet, basename='education-category')

course_router = NestedSimpleRouter(router, r'course', lookup='course')

urlpatterns = [
    path('', include(router.urls)),
    path(r'', include(course_router.urls)),
    path('course/<int:course_pk>/lesson/', user_lesson_api_view, name='education-lesson-list'),
    path('course/<int:course_pk>/theme/', user_theme_api_view, name='education-theme-list'),
    path('course/<int:pk>/follow/', follow_course_api_view, name='education-follow-course'),
    path('course/<int:pk>/rate/', rate_course_api_view, name='education-course-rate'),
    path('lesson/<int:pk>/answer/', lesson_answer_api_view, name='education-lesson-answer'),
    path('lesson/<int:pk>/tests/', task_test_api_view, name='education-test-task'),
    path('lesson/<int:pk>/exercises/', exercise_api_view, name='education-exercise-task'),
]
