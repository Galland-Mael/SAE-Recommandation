from .models import *
from django.db.models import Avg

NB_CARROUSEL = 10


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


def updateNoteMoyenneRestaurant(restaurant):
    """ Fonction de mise à jour de la note moyenne d'un restaurant passé en paramètres

    @param nomRestaurant: le nom du restaurant
    @return: /
    """
    avis_resto = Avis.objects.filter(restaurant_fk=restaurant)
    if avis_resto.count() != 0:
        note = avis_resto.aggregate(Avg("note"))
        Restaurant.objects.filter(nom=restaurant.nom).update(note=round(note['note__avg'], 2))
    else:
        Restaurant.objects.filter(nom=restaurant.nom).update(note=-1)


def listeAffichageDejaVisiter(user):
    """ Renvoie une liste de taille max NB_CARROUSEL contenant les restaurants que l'utilisateur
    a déjà noté, et qu'il a apprécié (note >= 3.5)

    @param user: l'utilisateur
    @return: une liste de restaurants
    """
    return Avis.objects.filter(adherant_fk=user, note__gte=3.5)[:NB_CARROUSEL]