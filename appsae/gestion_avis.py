from appsae.model.models import *
from .gestion import *

def ajoutAvis(user, restaurant, note, avis = ""):
    """ Ajout d'un avis à la base de données,
    Renvoie true s'il a été ajouté, false sinon

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @param note: la note de l'utilisateur sur le restaurant
    @param avis: l'avis de l'utlisateur sur le restaurant
    @return: un booléen en fonction de si l'avis à été ajouté à la base de données ou non
    """
    if (avisExist(user,restaurant)):
        return False
    avis = Avis(adherant_fk=user, restaurant_fk=restaurant, note=note, texte=avis)
    avis.save()
    print(Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user))
    updateNoteMoyenneRestaurant(restaurant)
    return True


def updateAvis(user, restaurant, note, avis):
    """ Mise à jour de l'avis de l'utilisateur user sur le restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @param note: la nouvelle note
    @param avis: le nouvel avis
    @return: /
    """
    if (avisExist(user, restaurant)):
        Avis.objects.filter(adherant_fk=user, restaurant_fk=restaurant).update(note=note, texte=avis)
    updateNoteMoyenneRestaurant(restaurant)


def deleteAvis(user, restaurant):
    """ Supprime l'avis de l'utilsateur user pour le restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    if (avisExist(user, restaurant)):
        Avis.objects.filter(adherant_fk=user, restaurant_fk=restaurant).delete()
    updateNoteMoyenneRestaurant(restaurant)


def avisExist(user, restaurant):
    """ Vérifie si l'utilisateur user a déjà ajouté un avis sur le restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: true si l'avis existe, false sinon
    """
    if Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).count() == 0:
        return False
    return True

def afficherAvis(user, restaurant):
    """ Renvoie l'avis de l'utilisateur s'il existe

    @param restaurant: le restaurant
    @param user: l'utilisateur
    @return: l'avis de l'utilisateur s'il existe, None sinon
    """
    if (avisExist(user, restaurant)):
        return Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user)
    return None

def listeAffichageAvis(restaurant, num, user=""):
    """ Renvoie une liste d'avis 10 par 10 ne contenant pas l'avis de l'utilisateur user,
    si num vaut 0, on renvoie de 0 à 9 dans la liste des avis, etc...

    @param restaurant: le restaurant
    @param user: l'utilisateur
    @param num: le numéro de la page
    @return: une liste (QuerySet) d'avis
    """
    taille_list = 2
    if user == "":
        avis = Avis.objects.filter(restaurant_fk=restaurant)
    else:
        avis = Avis.objects.filter(restaurant_fk=restaurant).exclude(adherant_fk=user)
    return avis[num*taille_list:(num + 1)*taille_list]


def afficherVoirPlus(restaurant, num, user=""):
    """Renvoie true s'il faut afficher le bouton "Voir Plus", false sinon

    @param restaurant: le restaurant concerné
    @param num: le numéro de la page actuelle
    @param user: l'utilisateur concerné
    @return: booléen en fonction de s'il faut afficher ou non "Voir Plus"
    """
    return listeAffichageAvis(restaurant, num + 1, user).count() != 0