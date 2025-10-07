"""
URL configuration for runnershive project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from events import views
from django.contrib import admin
from django.urls import path, include
from .views import handler400, handler403, handler404, handler500

# URL Paths ordered alphabetically
urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('events/', include("events.urls")),
    path('summernote/', include('django_summernote.urls')),
    path('', views.TodaysEventsListView.as_view(), name="home"),
]

handler400 = "runnershive.views.handler400"
handler403 = "runnershive.views.handler403"
handler404 = "runnershive.views.handler404"
handler500 = "runnershive.views.handler500"
