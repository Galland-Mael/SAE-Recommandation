from .models import *


def suppressionAdherant(nb=20):
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