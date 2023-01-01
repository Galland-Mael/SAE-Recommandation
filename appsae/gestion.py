from .models import *

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


def listeAffichageCarrouselVilles(ville="", type=""):
    """ Renvoie les meilleurs restaurants selon le type de restaurant et la ville donnés en paramètres,
    s'il n'y a pas de de ville et de filtre, on renvoit les meilleurs restaurants de la base de données,
    s'il n'y a pas de ville mais un filtre, on renvoit les meilleurs restaurants de la base de données avec le filtre
    s'il y a une ville mais pas de filtre, on renvoit les meilleurs restaurants dans la ville donnée,
    s'il y a une ville et un filtre, on renvoit les meilleurs restaurants avec le filtre et dans la ville donnée

    @param ville: la ville concernée
    @param type: le type de restaurant recherché
    @return:
    """
    if type != "":
        type_restaurant = RestaurantType.objects.filter(nom=type.lower())  # on stock le type de restaurant correspondant au filtre
        if type_restaurant.count() == 0: # si il n'y a pas de type avec ce nom on arête la fonction
                return []

        if ville != "":
            return Restaurant.objects.filter(ville=ville, type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
        else:
            return Restaurant.objects.filter(type=type_restaurant[0]).order_by('-note')[:NB_CARROUSEL]
    if ville != "" and type == "":
        return Restaurant.objects.filter(ville=ville).order_by('-note')[:NB_CARROUSEL]
    return Restaurant.objects.order_by('-note')[:NB_CARROUSEL]


def listeAffichageDejaVisiter(user):
    """ Renvoie une liste de taille max NB_CARROUSEL contenant les restaurants que l'utilisateur
    a déjà noté, et qu'il a apprécié (note >= 3.5)

    @param user: l'utilisateur
    @return: une liste de restaurants
    """
    return Avis.objects.filter(adherant_fk=user, note__gte=3.5)[:NB_CARROUSEL]