import json
import os.path
import sqlite3
import csv
from sqlite3 import OperationalError
import os, tempfile, zipfile, mimetypes
from urllib.request import Request
from wsgiref.util import FileWrapper
from django.conf import settings
from django.utils.dateformat import format

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.encoding import smart_str

from .models import *
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
import time
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader

from .test import StreamJson

PAGE = 0


def modifPAGE():
    global PAGE
    PAGE += 1

def register(request):
    if request.method == "POST":
        '''Remplissage de la base de données'''
        form = AdherantForm(request.POST).save()
        print(request.POST["mail"])
        return redirect('login')
    form = AdherantForm()
    return render(request, 'user/register.html', {'form': form, 'info': Adherant.objects.all})
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
            user = Adherant.objects.get(mail=request.POST['mail'])
            '''Création de la session ou je récupère que le mail de l'utilisateur'''
            request.session['mailUser'] = user.mail
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
    #inserttype()
    #insertresto()
    #insertuser()
    #Restaurant.objects.all().delete()
    #Adherant.objects.all().delete()
    #Avis.objects.all().delete()
    #insertreview()
    liste = carrousel();
    return render(request, 'index/index.html', {'list': liste})


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


def randomValue():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
        print(value_random);
    return value_random


def meilleurs_resto(request):
    ''' Renvoie les restaurants les mieux notés '''
    liste = carrousel();
    return render(request, 'testMatteo.html', {'list': liste});


def carrousel():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(10):
        list.append(restaurant[i]);
    return list


def recommandation():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(3):
        list.append(restaurant[i]);
    return list

'''Fonction qui detruit la session et redirige sur la page index'''


def logoutUser(request):
    try:
        del request.session['mailUser']
    except KeyError:
        pass
    return redirect('index')


def search(request):
    print("kerkekeke")
    if request.GET["search"] != "":
        restaurants = Restaurant.objects.filter(nom__icontains=request.GET["search"])[:3]
        return render(request, 'restaurants/searchRestaurants.html', context={'restaurants': restaurants})
    return HttpResponse('')


def vueRestaurant(request, pk):
    print("vuerestaurant")
    restaurant = Restaurant.objects.filter(pk=pk)
    imgRestaurants=ImageRestaurant.objects.filter
    return render(request, 'restaurants/vueRestaurant.html', context={'restaurant': restaurant})

def matteo(request):
    adherant = Adherant.objects.filter(mail="matteo.miguelez@gmail.com")[0]
    resto = Restaurant.objects.filter(nom="Burger King")[0]
    print(afficherAvis(adherant, resto))
    print("------------------------------------------------")
    print(listeAffichageAvis(resto, adherant, PAGE))
    print(afficherVoirPlus(Restaurant.objects.filter(nom="Burger King")[0], Adherant.objects.filter(mail="matteo.miguelez@gmail.com")[0], PAGE))
    modifPAGE()
    print("------------------------------------------------")
    print(listeAffichageAvis(resto, adherant, PAGE))
    print(afficherVoirPlus(Restaurant.objects.filter(nom="Burger King")[0], Adherant.objects.filter(mail="matteo.miguelez@gmail.com")[0], PAGE))
    modifPAGE()
    print("------------------------------------------------")
    return redirect('index')


def export_restaurant(request):
    file = str(settings.BASE_DIR) + '/' + "restaurant.csv"
    f = open(file, "w")
    f.writelines("id ,nom ,pays, telephone ,image_front ,note")
    f.write('\n')

    for restaurant in Restaurant.objects.all().values_list('id', 'nom', 'pays', 'telephone', 'image_front', 'note'):
        f.write(str(restaurant)[1:-1])
        f.write('\n')
    print(file)
    return redirect('index')


def export_ratings(request):
    file = str(settings.BASE_DIR) + '/' + "ratings.csv"
    f = open(file, "w")
    f.writelines("restaurant_id,user_id,note,timestamp")
    f.write('\n')
    for ratings in Avis.objects.all():
        dt = ratings.created_date
        print(dt)
        unix_dt = datetime.datetime.timestamp(dt) * 1000
        print(unix_dt)
        unix_str = str(unix_dt)
        Avis.objects.filter(created_date=dt).update(unix_date=unix_str)

    for rating in Avis.objects.all().values_list('restaurant_fk', 'adherant_fk', 'note','unix_date'):
        f.write(str(rating)[1:-1])
        f.write('\n')
    print(file)
    return redirect('index')

def split_string(string):
    # Split the string based on space delimiter
    list_string = string.split(',')

    return list_string

def insertresto():
    url = "https://qghub.cloud/assets/yelp_business.json"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    verif = 0

    # read json from url in stream
    for obj in StreamJson(req):
        verif += 1
        check = False
        categories = obj.get('categories')
        city = obj.get('city')
        if categories is not None:
            liste = split_string(categories)
            size = len(liste)
            for i in range(size):
                if i != 0:  # test pour suppression de l'espace devant la chaine
                    alias = liste[i][1:]
                    liste[i] = alias
                else:
                    alias = liste[i]
                if alias.lower() == "restaurants":
                    check = True
        exist=False
        tmp2=0
        if check:
            nb = len(liste)
            for a in range(nb):
                alias = liste[a]
                tmp2 = RestaurantType.objects.filter(nom=alias.lower()).count()
                if tmp2 > 0:
                    exist=True


            if exist:
                id_yelp = obj.get('business_id')
                name = obj.get('name')
                address = obj.get('address')
                zip_code = obj.get('postal_code')
                state = obj.get('state')
                latitude = obj.get('latitude')
                longitude = obj.get('longitude')
                rating = obj.get('stars')
                nb_review = obj.get('review_count')

                restaurant = Restaurant(id_yelp=id_yelp, nom=name, adresse=address, ville=city, zip_code=zip_code,
                                        etat=state, latitude=latitude, longitude=longitude,
                                        note=rating, nb_review=nb_review)
                restaurant.save()

                liste.remove('Restaurants')
                try:
                    liste.remove('Food')
                except:
                    print('no food')

                nb = len(liste)
                for a in range(nb):
                    alias = liste[a]
                    tmp = RestaurantType.objects.filter(nom=alias.lower())
                    if tmp:
                        restaurant.type.add(tmp[0])
        print(verif)

def inserttype():
    url = "https://qghub.cloud/assets/yelp_business.json"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    verif = 0

    # read json from url in stream
    for obj in StreamJson(req):
        verif += 1
        check = False
        categories = obj.get('categories')
        if categories is not None:
            liste = split_string(categories)
            size = len(liste)
            for i in range(size):
                if i != 0:  # test pour suppression de l'espace devant la chaine
                    alias = liste[i][1:]
                else:
                    alias = liste[i]
                if alias.lower() == "restaurants":
                    check = True

            if check:
                for j in range(size):
                    if j != 0:  # test pour suppression de l'espace devant la chaine
                        alias = liste[j][1:]
                        nb = RestaurantType.objects.filter(nom=alias.lower()).count()
                        if nb == 0:
                            b = RestaurantType(nom=alias.lower())
                            b.save()
                    else:
                        alias = liste[j]
                        nb = RestaurantType.objects.filter(nom=alias.lower()).count()
                        if nb == 0:
                            b = RestaurantType(nom=alias.lower())
                            b.save()
        print(verif)
    RestaurantType.objects.filter(nom="restaurants").delete()
    RestaurantType.objects.filter(nom="food").delete()

def insertuser():
    url = "https://qghub.cloud/assets/yelp.json"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    verif = 0

    # read json from url in stream
    for obj in StreamJson(req):
        verif += 1
        nb_review = obj.get('review_count')
        if nb_review >= 20:
            id_yelp = obj.get('user_id')
            prenom = obj.get('name')
            nb_review = obj.get('review_count')

            user = Adherant(id_yelp=id_yelp, prenom=prenom, nom='',mail='',password='',pseudo='', nb_review=nb_review)
            user.save()
        print('iteration ' + str(verif))

def insertreview():
    file = 14
    url = "https://qghub.cloud/assets/review"+str(file)+".json"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    verif = 0
    # read json from url in stream
    for obj in StreamJson(req):
        verif += 1
        user_id=obj.get('user_id')
        resto_id = obj.get('business_id')
        obj_re = Restaurant.objects.filter(id_yelp=resto_id)
        if obj_re.count() != 0:
            obj_ad = Adherant.objects.filter(id_yelp=user_id)
            if obj_ad.count() != 0:
                # test5=Avis.objects.filter(adherant_fk=obj_ad[0], restaurant_fk=obj_re[0]).count()
                # if test5 == 0:
                date = obj.get('date')
                unix_dt = (time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple()))
                note=obj.get('stars')
                text=obj.get('text')
                fk_user=obj_ad[0]
                fk_resto=obj_re[0]
                avis = Avis(note=note, texte=text, unix_date=unix_dt,restaurant_fk=fk_resto, adherant_fk=fk_user)
                avis.save()
                print('iteration ' + str(verif))