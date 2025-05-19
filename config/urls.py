from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.views import LogoutView

schema_view = get_schema_view(
    openapi.Info(
        title="QuickNote API",
        default_version='v1',
        description="API documentation for Notes application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact( email="aryansharma4844@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    
    # Swagger URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Auth URLs for Swagger
    path('accounts/login/', admin.site.login, name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)