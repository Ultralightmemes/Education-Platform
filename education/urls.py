from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from education import views

router = SimpleRouter()
router.register(r'course', views.CourseViewSet, basename='course')
# router.register(r'category', views.CategoryViewSet, basename='category')

course_lessons_router = NestedSimpleRouter(router, r'course', lookup='course')
course_lessons_router.register(r'lesson', views.LessonViewSet, basename='course-lesson')

urlpatterns = [
    path('', include(router.urls)),
    path(r'', include(course_lessons_router.urls)),
]
