"""
URL configuration for ASTRAE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ASTRAE.views import landingpage, loginn, register, user_login, user_registration, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ASTRAEUser/', include('ASTRAEUser.urls')),
    path('ASTRAEAdmin/', include('ASTRAEAdmin.urls')),

    path('', landingpage, name='landingpage'),
    path('loginn/', loginn, name='loginn'),
    path('register/', register, name='register'),
    path('landingpage/', landingpage, name='landingpage'),
    path('user_logout/', user_logout, name='user_logout'),
    path('user_login/', user_login, name='user_login'),
    path('user_registration/', user_registration, name='user_registration')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)