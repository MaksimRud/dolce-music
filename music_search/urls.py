from django.urls import path

from . import views

app_name = 'music_search'
urlpatterns = [
    path('', views.index, name='index'),
    # periods path
    path('periods/', views.PeriodView.as_view(), name='period'),
    path('periods/<int:pk>/details',
         views.DetailView.as_view(), name='detail_period'),
    path('periods/<int:pk>/edit',
         views.PeriodUpdate.as_view(), name='edit_period'),
    path('periods/create', views.PeriodCreate.as_view(), name='create_period'),
    # compousers path
    path('compousers/', views.CompousersView.as_view(), name='compouser'),
    path('compousers/<int:pk>/details',
         views.CompousersDetailView.as_view(), name='detail_compouser'),
    path('compousers/<int:pk>/edit',
         views.CompousersUpdate.as_view(), name='edit_compouser'),
    path('compousers/create_compouser', views.CompousersCreate.as_view(),
         name='create_compouser')
]
