from django.urls import path
from . import views

urlpatterns = [
    path('', views.gallery_list, name='gallery_list'),
    path('manage/', views.gallery_manage_list, name='gallery_manage_list'),
    path('add/', views.gallery_create, name='gallery_add'),
    path('<int:pk>/edit/', views.gallery_update, name='gallery_edit'),
    path('<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),
    path('<int:pk>/', views.gallery_detail, name='gallery_detail'),
]
