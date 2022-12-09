import json
import os.path
import sqlite3
import csv
from sqlite3 import OperationalError
import os, tempfile, zipfile, mimetypes
from wsgiref.util import FileWrapper
from django.conf import settings

from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import smart_str

from appsae.model.models import *
from .formulaire import *
from django.core.mail import send_mail
import random
from django.shortcuts import render
from django.http import HttpResponse
from .gestion import *
from .gestion_utilisateur import *
from .gestion_groupes import *
from .gestion_avis import *
import datetime


def register(request):
    if request.method == "POST":
        '''Remplissage de la base de données'''
        form = AdherantForm(request.POST).save()
        return redirect('login')
    form = AdherantForm()
    context = {
        'form': form,
        'info': Adherant.objects.all
    }
    return render(request, 'user/register.html', context)
    # return JsonResponse({"form": list(form.values) })


def login(request):
    if request.method == "POST":
        info = Adherant.objects.all()
        contain = False
        for adherant in info:
            '''Verification'''
            if (request.POST['mail'] == adherant.mail):
                if (request.POST['password'] == adherant.password):
                    contain = True
        if contain:
            user = Adherant.objects.get(mail=request.POST['mail']);
            '''Création de la session ou je récupère que le mail de l'utilisateur'''
            request.session['mailUser'] = user.mail
            sessionMailUser = request.session['mailUser'];
            context = {
                'idUser': user.id,
                'name': user.nom,
                'prenom': user.prenom,
                'mail': user.mail,
                'birthDate': user.birthDate,
                'pseudo': user.pseudo,
                'photo': user.profile_picture.url,
                'list': carrousel()
            }
            return render(request, 'index/index.html', context)
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')


def index(request):
    context = {
        'list': listeAffichageCaroussel()
    }
    connect(request, context)
    return render(request, 'index/index.html', context)


def modifUser(request):
    return render(request, 'user/modifUser.html')


def verificationEmail(request):
    print("apeler")
    ''' Fonction qui permet l'envoi d'un mail à un utilisateur depuis l'adresse mail du site web '''
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
                  "Code de vérification :\n"
                  + "         " + randomValue()
                  + "\n\nL'équipe EatAdvisor",
                  "eat_advisor2@outlook.fr",
                  ["maelgalland.71@gail.com"],
                  fail_silently=False);
        print("reussi")
    except:
        print("fail")
        return HttpResponse("<p>Next</p>")


def meilleurs_resto(request):
    ''' Renvoie les restaurants les mieux notés '''
    liste = carrousel();
    return render(request, 'testMatteo.html', {'list': liste});


'''Fonction qui detruit la session et redirige sur la page index'''


def logoutUser(request):
    try:
        del request.session['mailUser']
    except KeyError:
        pass
    return redirect('index')


def search(request):
    if request.GET["search"] != "":
        context = {
            'restaurants': Restaurant.objects.filter(nom__icontains=request.GET["search"])[:3]
        }
        return render(request, 'restaurants/searchRestaurants.html', context)
    return HttpResponse('')


def vueRestaurant(request, pk):
    context = {
        'restaurant': Restaurant.objects.filter(pk=pk),
        'imgRestaurants': ImageRestaurant.objects.filter(idRestaurant=pk),
        'avis': Avis.objects.filter(restaurant_fk=Restaurant.objects.get(pk=pk))[:10]
    }
    connect(request, context),
    if 'mailUser' in request.session:
        context['commentaire'] = True
    return render(request, 'restaurants/vueRestaurant.html', context)


def addCommentaires(request, pk):
    context = {
        'restaurant': Restaurant.objects.filter(pk=pk),
        'imgRestaurants': ImageRestaurant.objects.filter(idRestaurant=pk),
        'avis': Avis.objects.filter(restaurant_fk=Restaurant.objects.get(pk=pk)),
    }
    if 'mailUser' in request.session:
        context['commentaire'] = True
    if (request.method == 'POST' and 'title-rating' in request.POST and 'comm' in request.POST):
        ajoutAvis(Adherant.objects.get(mail=request.session['mailUser']), Restaurant.objects.get(pk=pk),
                  request.POST['title-rating'],
                  request.POST['comm'])
        updateAvis(Adherant.objects.get(mail=request.session['mailUser']), Restaurant.objects.get(pk=pk),
                   request.POST['title-rating'], request.POST['comm'])
    else:
        del messages
        messages.success(request, 'Les deux champs doivent être remplis.')
    connect(request, context)
    return render(request, 'restaurants/vueRestaurant.html', context)


def export_restaurant(request):
    file = str(settings.BASE_DIR) + '/' + "restaurant.csv"
    f = open(file, "w")
    f.writelines("id ,nom ,pays, telephone ,image_front ,note")
    f.write('\n')

    for restaurant in Restaurant.objects.all().values_list('id', 'nom', 'pays', 'telephone', 'image_front', 'note'):
        f.write(str(restaurant))
        f.write('\n')
    print(file)
    return redirect('index')


def export_ratings(request):
    file = str(settings.BASE_DIR) + '/' + "ratings.csv"
    f = open(file, "w")
    f.writelines("restaurant_id,user_id,note")
    f.write('\n')

    for rating in Avis.objects.all().values_list('restaurant_fk', 'adherant_fk', 'note'):
        f.write(str(rating))
        f.write('\n')
    print(file)
    return redirect('index')


def addAvis(request, pk):
    context = {
        'avis': liste_avis(Restaurant.objects.get(pk=pk), 1)
    }
    connect(request, context)
    return render(request, 'avis/moreAvis.html',context)
