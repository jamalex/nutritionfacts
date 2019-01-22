"""nutritionfacts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.conf.urls import url
from django.views.generic import TemplateView

from .views import pingback, health_check, countries, timeline, statistics, versions, migrations, chart

urlpatterns = [
    path("admin/", admin.site.urls),
    path('chart/', chart, name="chart"),
    path("api/v1/pingback", pingback, name="pingback"),
    path("api/v1/statistics", statistics, name="statistics"),
    path("api/analytics/countries", countries, name="countries"),
    path("api/analytics/timeline", timeline , name="timeline"),
    path("api/analytics/versions", versions , name="versions"),
    path("api/analytics/migrations", migrations , name="versions "),
    path("health_check", health_check, name="health_check"),
    url(r'^account/', include(('social_django.urls', 'nutritionfacts'), namespace='social')),
    url(r'^account/', include(('django.contrib.auth.urls', 'nutritionfacts'), namespace='auth')),
]
