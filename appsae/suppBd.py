from .models import *


def suppressionAdherant(nb=10):
    """

    @param nb: nombre d'avis minimum pour garder l'adhérant dans la bd
    @return: /
    """
    compteur = 0
    for adherant in Adherant.objects.all():
        if Avis.objects.filter(adherant_fk=adherant).count() < nb:
            adherant.delete()
        compteur+=1
        if compteur%1000 == 0:
            print(compteur)


def majNb_reviewAdherant():
    """

    @return:
    """
    for adherant in Adherant.objects.all():
        nb_review_ = Avis.objects.filter(adherant_fk=adherant).count();
        Adherant.objects.filter(id_yelp=adherant.id_yelp).update(nb_review=nb_review_)
