from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'music_search'
urlpatterns = [
    path('', views.index, name='index'),
    # periods path
    path('periods/', views.PeriodView.as_view(), name='period'),
    path('periods/downl', views.get_per_file, name='excel_period'),
    path('periods/excel_upd', views.post_per_file, name='post_excel_period'),
    path('periods/<int:pk>/details',
         views.DetailView.as_view(), name='detail_period'),
    path('periods/<int:pk>/edit',
         views.PeriodUpdate.as_view(), name='edit_period'),
    path('periods/create', views.PeriodCreate.as_view(), name='create_period'),
    path('periods/<int:pk>/delete',
         views.CompousersDelete.as_view(), name='delete_period'),
    # compousers path
    path('compousers/downl', views.get_comp_file, name='excel_compouser'),
    path('compousers/excel_upd', views.post_comp_file, name='post_excel_compouser'),
    path('compousers/', views.CompousersView.as_view(), name='compouser'),
    path('compousers/<int:pk>/details',
         views.CompousersDetailView.as_view(), name='detail_compouser'),
    path('compousers/<int:pk>/edit',
         views.CompousersUpdate.as_view(), name='edit_compouser'),
    path('compousers/create_compouser', views.CompousersCreate.as_view(),
         name='create_compouser'),
    path('compousers/<int:pk>/delete',
         views.CompousersDelete.as_view(), name='delete_compouser'),
     # music path
     path('music/downl', views.get_music_file, name='excel_music' ),
     path('music/excel_upd', views.post_music_file, name='post_excel_music'),
     path('music/', views.PieceOfMusicView.as_view(), name='music'),
     path('music/<int:pk>/details', views.MusicDetailView.as_view(), name='detail_music'),
     path('music/<int:pk>/edit', views.PieceOfMusicUpdate.as_view(), name='edit_music'),
     path('music/create_music', views.PieceOfMusicCreate.as_view(), name='create_music'),
     path('music/<int:pk>/edit', views.PieceOfMusicDelete.as_view(), name='delete_music')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)