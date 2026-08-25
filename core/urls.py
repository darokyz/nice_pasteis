from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from .auth_views import login_view
from .health import healthcheck

urlpatterns = [
    path('health/', healthcheck, name='healthcheck'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('comandas.urls')),
    path('analytics/', include('analytics.urls')),
]
