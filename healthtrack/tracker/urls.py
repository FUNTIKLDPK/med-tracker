from django.urls import path
from . import views

urlpatterns = [
    path('', views.measurement_list, name='measurement_list'),
    path('add/', views.measurement_add, name='measurement_add'),
    path('<int:pk>/delete/', views.measurement_delete, name='measurement_delete'),
    path('export/', views.export_csv, name='export_csv'),
    path('signup/', views.signup, name='signup'),
]