from django.urls import path
from . import views

urlpatterns = [
    path('tree/input', views.input_data, name='input'),
    path('tree/<int:husband_id>/', views.family_tree, name='tree'),
    path('person/<int:person_id>/', views.person_detail, name='person_detail'),
    path('profile/', views.user_profile, name='profile'),

]
