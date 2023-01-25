from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from education import views
from education.views import user_lesson_api_view

router = SimpleRouter()
router.register(r'course', views.CourseViewSet, basename='course')
router.register(r'category', views.CategoryViewSet, basename='category')

course_router = NestedSimpleRouter(router, r'course', lookup='course')
course_router.register(r'lesson', views.LessonViewSet, basename='course-lesson')

urlpatterns = [
    path('', include(router.urls)),
    path(r'', include(course_router.urls)),
    path('course/<int:course_pk>/lesson/', user_lesson_api_view, name='lesson-list'),
]
