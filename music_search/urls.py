from django.urls import path

from . import views

app_name = 'music_search'
urlpatterns = [
    path('', views.index, name='index'),
    path('periods/', views.PeriodView.as_view(), name='period'),
    path('periods/<int:pk>/details',
         views.DetailView.as_view(), name='detail'),
    path('periods/<int:pk>/edit',
         views.PeriodUpdate.as_view(), name='edit'),
]
