from .models import *
from .gestion import connect
from django.shortcuts import render, redirect
import hashlib
import datetime
from time import mktime
from .ajoutCSV import add_restaurant_csv
from random import randint


class Horaire:
    def __init__(self, jour, horaire1_deb="00:00", horaire1_fin="00:00", horaire2_deb="00:00", horaire2_fin="00:00"):
        self.jour = jour
        self.horaire1_deb = horaire1_deb
        self.horaire2_deb = horaire2_deb
        self.horaire1_fin = horaire1_fin
        self.horaire2_fin = horaire2_fin


def validation_admin(request, pk):
    if 'mailAdministrateur' in request.session:
        demande = DemandeCreationRestaurant.objects.get(pk=pk)
        context = {
            'demande': demande,
            'pk': demande.pk
        }
        connect(request, context)
        return render(request, 'administrateur/validation.html', context)
    return redirect('index')


def index_administrateur(request):
    if 'mailAdministrateur' in request.session:
        context = {
            'demandes': DemandeCreationRestaurant.objects.filter(traite=False).order_by("-date_creation")
        }
        connect(request, context)
        return render(request, 'administrateur/index.html', context)
    return redirect('index')


def modif_resto(request):
    if 'mailRestaurateur' in request.session:
        if request.method == "POST":
            info = request.POST
            if 'telephone' in info and info['telephone'] != '':
                print("Ajout du téléphone")
            if 'test' in info:
                print(info)
        last_avis = Avis.objects.filter(restaurant_fk=Restaurateur.objects.get(
            mail=request.session['mailRestaurateur']).restaurant_fk).order_by('-unix_date')
        context = {
            'list': [Horaire("Lundi", "11:00", "15:00"), Horaire("Mardi", "11:00", "15:00"),
                     Horaire("Mercredi", "11:00", "15:00"), Horaire("Jeudi", "11:00", "15:00"),
                     Horaire("Vendredi", "11:00", "15:00"), Horaire("Samedi", "11:00", "15:00"),
                     Horaire("Dimanche", "11:00", "15:00")],
            'restaurant': Restaurant.objects.get(
                pk=Restaurateur.objects.get(mail=request.session['mailRestaurateur']).restaurant_fk.pk),
        }
        if last_avis.count() != 0:
            context['lastComments'] = last_avis[:2]
        return render(request, 'restaurateur/modifResto.html', connect(request, context))
    return redirect('index')


def refuser_form(request, pk):
    if 'mailAdministrateur' in request.session:
        context = {}
        if request.method == "POST":
            refus = RefusDemandeRestaurant(
                titre=request.POST['title'],
                message=request.POST['description'],
                restaurateur_fk=DemandeCreationRestaurant.objects.get(pk=pk).restaurateur_fk
            )
            refus.save()
            DemandeCreationRestaurant.objects.filter(pk=pk).update(traite=1)
            return redirect('index_administrateur')
        connect(request, context)
        return render(request, 'administrateur/form_refus.html', context)
    return redirect('index')


def ajouter_resto(request, pk):
    if 'mailAdministrateur' in request.session:
        demande = DemandeCreationRestaurant.objects.get(pk=pk)
        restaurant = Restaurant(
            nom=demande.nom,
            adresse=demande.adresse,
            ville=demande.ville,
            zip_code=demande.zip_code,
            pays=demande.pays,
            etat=demande.etat,
            longitude=demande.longitude,
            latitude=demande.latitude,
        )
        restaurant.save()
        for type_name in demande.type.all():
            type = RestaurantType.objects.get(nom=type_name)
            restaurant.type.add(type)
        add_restaurant_csv(restaurant)
        setImageAleatoireRestaurant(restaurant)
        Restaurateur.objects.filter(pk=demande.restaurateur_fk_id).update(restaurant_fk=restaurant)
        demande.delete()
        return redirect('index_administrateur')
    return redirect('index')


def register_restaurateur(request):
    if request.method == "POST":
        info = request.POST
        if info['password_verif'] == info['password']:
            if info['mail'] != '' and info['password'] != '':
                restaurateur = Restaurateur(
                    mail=info['mail'],
                    password=hashlib.sha256(info['password'].encode('utf-8')).hexdigest()
                )
                restaurateur.save()
                return redirect('../restaurateur/login')
    return render(request, 'restaurateur/register_restaurateur.html')


def login_restaurateur(request):
    # Déconnexion
    if 'mailUser' in request.session or 'mailAdministrateur' in request.session or 'mailRestaurateur' \
            in request.session:
        return redirect('logout')

    if request.method == "POST":
        info = request.POST

        # Cas restaurateur
        restaurateur = Restaurateur.objects.filter(mail=info['mail'])
        if restaurateur.count() == 1:
            hashed_password = hashlib.sha256(info['password'].encode('utf-8')).hexdigest()
            if hashed_password == restaurateur[0].password:
                request.session['mailRestaurateur'] = restaurateur[0].mail
                return redirect('index_restaurateur')

        # Cas administrateur
        administrateur = Administrateur.objects.filter(mail=info['mail'])
        if administrateur.count() == 1:
            hashed_password = hashlib.sha256(info['password'].encode('utf-8')).hexdigest()
            if hashed_password == administrateur[0].password:
                request.session['mailAdministrateur'] = administrateur[0].mail
                return redirect('index_administrateur')

    return render(request, 'restaurateur/login_restaurateur.html')


def index_restaurateur(request):
    if 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande = DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
        context = {
            'nombre': demande.count(),
            'restaurant_exist': (restaurateur.restaurant_fk_id is not None),
        }
        if restaurateur.restaurant_fk_id is not None:
            context['restaurant'] = restaurateur.restaurant_fk
            return redirect('vueRestaurant', pk=restaurateur.restaurant_fk.pk)
        elif demande.count() == 1:
            refus = RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
            if refus.count() != 0:
                context['refus'] = RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)[0]
            date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
            date_bd = demande[0].date_creation.replace(tzinfo=None).timetuple()
            temps_entre_demande = 400  # replace with 259200
            temps = int(mktime(date_bd) + temps_entre_demande - mktime(date_actuelle))
            context['minutes'] = temps // 60
            context['secondes'] = temps % 60
            if demande[0].traite == 1:
                if mktime(date_bd) + temps_entre_demande < mktime(date_actuelle):
                    DemandeCreationRestaurant.objects.filter(pk=demande[0].pk).update(traite=2)
            context['demande'] = demande[0]
        connect(request, context)
        return render(request, 'restaurateur/index.html', context)
    return redirect('index')


def create_demandecreationrestaurant(info, request):
    """ Crée une DemandeCreationRestaurant dans la base de données avec les infos données en paramètres

    @param info: les informations du formulaire
    @param request: informations utilisateurs
    @return: /
    """
    if info['nom'] != '' and info['adresse'] != '' and info['ville'] != '' and info['postal'] and info['pays'] != '' \
            and info['longitude'] and info['latitude'] != '':
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande_creation = DemandeCreationRestaurant(
            nom=info['nom'],
            adresse=info['adresse'],
            ville=info['ville'],
            zip_code=info['postal'],
            pays=info['pays'],
            etat=info['etat'],
            longitude=info['longitude'],
            latitude=info['latitude'],
            restaurateur_fk=restaurateur,
        )
        demande_creation.save()
        for type_name in info.getlist('type'):
            type = RestaurantType.objects.get(nom=type_name)
            demande_creation.type.add(type)
        RefusDemandeRestaurant.objects.filter(restaurateur_fk=restaurateur.pk).delete()
        return True
    return False


def formulaire_demande_restaurateur(request):
    context = {}
    if 'mailRestaurateur' in request.session:
        restaurateur = Restaurateur.objects.get(mail=request.session['mailRestaurateur'])
        demande = DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk)
        if request.method == "POST":
            info = request.POST
            test = False
            if demande.count() == 0:
                test = create_demandecreationrestaurant(info, request)
            elif demande.count() == 1 and demande[0].traite == 2:
                DemandeCreationRestaurant.objects.filter(restaurateur_fk=restaurateur.pk).delete()
                test = create_demandecreationrestaurant(info, request)
            if test:
                return redirect('index_restaurateur')
        elif demande.count() == 1:
            context['demande'] = demande[0]
        context['types'] = RestaurantType.objects.all()
        connect(request, context)
        return render(request, 'restaurateur/createResto.html', context)
    return redirect('index_restaurateur')


def setImageAleatoireRestaurant(restaurant):
    random_value = randint(1, 4)
    restaurant.image_front = "/img_restaurant/imagefront" + str(random_value) + ".jpg"
    '/img_restaurant/imagefront3.jpg'
    restaurant.save()
    indice_in_list = (random_value - 1) * 4 # Les images des sets sont stockées les unes après les autres et il y en a 4

    imgset = ImageRestaurant.objects.all()
    for index in range(4):
        restaurant.img.add(imgset[indice_in_list + index])