from django.urls import path

from . import views


app_name = 'weather'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new-list/', views.NewList.as_view(), name='new_list'),
    path('remove-city/', views.RemoveCity.as_view(), name='remove_city')
]
