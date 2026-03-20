from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="ALX Travel App API",
        default_version='v1',
        description="API documentation for ALX Travel App",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="godsway702@gmail.com"),
        ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include('listings.urls')),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),#jwt login
    path("api/auth/refresh", TokenRefreshView.as_view(),name="token_refresh"),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
]
