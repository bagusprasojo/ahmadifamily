from django.urls import path
from .views import event_list, event_detail, event_create

urlpatterns = [
    path('', event_list, name='event_list'),
    path('add/', event_create, name='event_add'),
    path('<int:pk>/', event_detail, name='event_detail'),
]
