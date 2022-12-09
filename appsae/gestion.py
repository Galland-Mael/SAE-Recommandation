
from appsae.model.models import *
from django.db.models import Avg

NB_CARROUSEL = 10
def carrousel():
    restaurant = Restaurant.objects.order_by('-note');
    list = [];
    for i in range(10):
        list.append(restaurant[i]);
    return list;

def connect(request,context):
    if 'mailUser' in request.session:
        user = Adherant.objects.get(mail=request.session['mailUser'])
        context['mail'] = request.session['mailUser']
        context['photo'] = user.profile_picture.url
    return context
def randomValue():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
        print(value_random);
    return value_random

def liste_carrousel(type):
    """ Renvoie les meilleurs restaurants selon le type de restaurant donné en paramètres,
    si il n'y pas de filtre, le paramètre d'entrée est la chaine "tous"

    @param type: le type de restaurant recherché
    @type type : str
    @return: les meilleurs restaurants selon le filtre
    """
    if type != "tous":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
            return []
        restaurant = Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
    else:
        restaurant = Restaurant.objects.order_by('-note')[:NB_CARROUSEL]
    return restaurant


def update_note_moyenne_restaurant(restaurant):
    """ Fonction de mise à jour de la note moyenne d'un restaurant passé en paramètres

    @param nomRestaurant: le nom du restaurant
    @return: /
    """
    if restaurant.count() != 0:
        note = Avis.objects.filter(restaurant=restaurant[0]).aggregate(Avg("note"))
        restaurant.update(note=note['note__avg'])

def listeAffichageCaroussel(type=""):
    """ Renvoie les meilleurs restaurants selon le type de restaurant donné en paramètres,
    si il n'y pas de filtre, le paramètre d'entrée est la chaine "", donnée par défaut

    @param type: le type de restaurant recherché
    @return: les meilleurs restaurants selon le filtre
    """
    if type != "":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
            return []
        return Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
    return Restaurant.objects.order_by('-note')[:NB_CARROUSEL]