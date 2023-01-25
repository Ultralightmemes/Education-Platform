from django.urls import path

from teacher.views import theme_api_view, theme_detail_api_view

urlpatterns = [
    path('course/<int:course_pk>/theme/', theme_api_view, name='theme-list'),
    path('theme/<int:pk>/', theme_detail_api_view, name='theme-detail'),
]