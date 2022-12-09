from django.contrib import admin
from django.urls import path
from appsae.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', register, name='register'),
    path('user/login/', login, name='login'),
    path('modifuser/', modifUser, name='modifUser'),
    path('verificationEmail/', verificationEmail, name='verificationEmail'),
    path('', index, name='index'),
    path('carrousel/', meilleurs_resto, name='meilleurs_resto'),
    path('logout/', logoutUser, name='logout'),
    path('addCommentaires/(<pk>)', addCommentaires, name='addCommentaires'),
    path('vueRestaurant/(<pk>)', vueRestaurant, name='vueRestaurant'),
    path('search/', search, name='search'),
    path('export_restaurant/', export_restaurant, name='export'),
    path('export_ratings/', export_ratings, name='export'),
    path('addAvis/(<pk>)', addAvis, name='addAvis'),
]
'''Utile pour afficher les images de la base de données'''
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
