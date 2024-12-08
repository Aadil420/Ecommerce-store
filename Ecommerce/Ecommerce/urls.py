from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('dg-admin/', admin.site.urls),
    path('', include('custom_admin.urls')),
    path('', include('user.urls')),
    path('api/user/', include('userapi.urls')),
]
