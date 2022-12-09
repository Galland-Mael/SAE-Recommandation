from appsae.model.models import *
from appsae.gestion import *
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
    return True

def avisExist(user, restaurant):
    """ Vérifie si l'utilisateur user a déjà ajouté un avis sur le restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: true si l'avis existe, false sinon
    """
    if Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).count() == 0:
        return False
    return True

def afficherAvisUser(user, restaurant):
    """ Renvoie l'avis de l'utilisateur s'il existe

    @param restaurant: le restaurant
    @param user: l'utilisateur
    @return: l'avis de l'utilisateur s'il existe, None sinon
    """
    if (avisExist(user, restaurant)):
        return Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user)
    return None


def liste_avis(restaurant, num):
    """ Renvoie une liste d'avis 10 par 10,
    si num vaut 0, on renvoie de 0 à 9 dans la liste des avis, etc...

    @param restaurant: le restaurant où chercher les avis
    @param num: le numero de la liste
    @return: une liste d'avis sous forme de QuerySet
    """
    avis = Avis.objects.filter(restaurant_fk=restaurant)
    taille = avis.count()
    taille_liste= 10 # Taille de la liste à prendre
    if taille < num*taille_liste:
        return []
    elif taille >= (num + 1) *taille_liste:
        return avis[num*taille_liste:(num + 1)*taille_liste]
    elif taille < (num +1 ) *taille_liste:
        return avis[num*taille_liste:taille]

def avisUser(restaurant, user, num = 0):
    """ Renvoie la liste des avis 10 par 10,
    sauf si un des avis appartient à l'utilisateur user,
    dans ce cas, il renvoie seulement 9 avis.
    Si num vaut 0, on renvoie de 0 à 9 dans la liste des avis, etc...

    @param restaurant: le restaurant
    @param user: l'utilisateur
    @param num: le numero de la liste
    @return: une liste d'avis
    """
    list = avisUser(restaurant, num)
    avis_user = afficherAvisUser(user, restaurant)

    if avis_user == None:
        return list

    list_avis = []
    for item in list:
        if item != avis_user[0]:
            list_avis.append(item)
    return list_avis


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