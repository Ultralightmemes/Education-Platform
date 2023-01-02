from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from EducationPlatform import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('education/', include('education.urls')),
    path('users/', include('user.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('__debug__/', include('debug_toolbar.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
