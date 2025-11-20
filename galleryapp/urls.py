from django.urls import path
from . import views

urlpatterns = [
    path('', views.gallery_list, name='gallery_list'),
    path('add/', views.gallery_create, name='gallery_add'),
    path('<int:pk>/', views.gallery_detail, name='gallery_detail'),
]
