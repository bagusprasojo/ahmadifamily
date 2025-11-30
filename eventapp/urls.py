from django.urls import path
from .views import (
    event_public_list,
    event_manage_list,
    event_detail,
    event_create,
    event_update,
    event_delete,
)

urlpatterns = [
    path('', event_public_list, name='event_list'),
    path('manage/', event_manage_list, name='event_manage_list'),
    path('add/', event_create, name='event_add'),
    path('<int:pk>/edit/', event_update, name='event_edit'),
    path('<int:pk>/delete/', event_delete, name='event_delete'),
    path('<int:pk>/', event_detail, name='event_detail'),
]
