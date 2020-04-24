from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
]