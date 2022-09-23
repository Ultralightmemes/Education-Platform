from django.urls import path, include
from rest_framework.routers import SimpleRouter

from education import views

router = SimpleRouter()
router.register(r'course', views.CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls))
]