from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.html, name='html'),
    path('login',views.html2,name='html2'),
]

