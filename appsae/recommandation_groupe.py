from .models import *
from statistics import mean
from operator import itemgetter

NB_AFFICHAGE = 10

def tri_selection(listNote, listType):
    for i in range(len(listNote)):
        # Trouver le min
        min = i
        for j in range(i + 1, len(listNote)):
            if listNote[min] > listNote[j]:
                min = j

        tmp = listNote[i]
        listNote[i] = listNote[min]
        listNote[min] = tmp

        tmp = listType[i]
        listType[i] = listType[min]
        listType[min] = tmp

    return listNote, listType


def recommandationGroupeAvisGroupeComplet(groupe, ville):
    """ Renvoie tous les restaurants avec des types qui ont plus aux membres du groupe

    @param groupe: le groupe
    @param ville: la ville où veut manger le groupe
    @return: une liste de restaurants
    """
    list_user = groupe.liste_adherants.all()
    taille = list_user.count()
    dico_type = {} # dictionnaire de la forme {type : [note1, note2,...]}
    list_resto = [] # liste contenant les restaurants déjà visités par au moins un des membres du groupe
    # parcours les membres du groupe
    for i in range(taille):
        # parcours des restaurants de la ville concernée
        for resto in Restaurant.objects.filter(ville=ville):
            # parcours les avis postés par les utilisateurs dans les restaurants de la ville
            for avis in Avis.objects.filter(adherant_fk=list_user[i], restaurant_fk=resto):
                # ajout du restaurant de l'avis dans la liste des restaurants déjà visités
                if (avis.restaurant_fk not in list_resto):
                    list_resto.append(avis.restaurant_fk)

                # parcours les types de restaurants où l'utilisateur à enregistré un avis
                for types in avis.restaurant_fk.type.all():
                    # et ajout de la note du restaurant aux types correspondant
                    if (types not in dico_type.keys()):
                        dico_type[types] = []
                        dico_type[types].append(avis.note)
                    else:
                        dico_type[types].append(avis.note)
    list_type = [] # liste avec les types
    list_note = [] # liste avec les notes correspondant aux types

    for cle, valeur in dico_type.items():
        moyenne = round(mean(valeur), 2)
        # if moyenne >= 3.5:
        list_type.append(cle)
        list_note.append(moyenne)

    list_note, list_type = tri_selection(list_note, list_type)
    list_note.reverse()
    list_type.reverse()
    # les listes sont ordonnées de la meilleure à la pire note

    list_nom = []
    for i in range(len(list_resto)):
        list_nom.append(list_resto[i].id_yelp)

    restaurants_par_type = []

    for i in range(len(list_type)):
        list_temp = Restaurant.objects.filter(ville=ville, type=list_type[i]).exclude(id_yelp__in=list_nom).order_by()
        list_temp_sans_doublons = []
        for j in range(len(list_temp)):
            if (i > 0):
                if (list_temp[j] not in restaurants_par_type[i-1]):
                    list_temp_sans_doublons.append(list_temp[j])
            else:
                list_temp_sans_doublons.append(list_temp[j])
        restaurants_par_type.append(list_temp_sans_doublons)
    taille_list = restaurants_par_type
    return restaurants_par_type


def recommandationGroupeAvisGroupeCarrousel(groupe, ville):
    """ Renvoie une liste avec NB_AFFICHAGE éléments pour l'affichage des meilleurs recommandations
    et une liste avec tous les éléments

    @param groupe: le groupe d'utilisateurs
    @return: liste avec NB_AFFICHAGE éléments, liste avec tous les restaurants
    """
    liste_complete = recommandationGroupeAvisGroupeComplet(groupe, ville)
    taille = len(liste_complete)
    if taille == 0:
        return [], liste_complete
    if taille == 1:
        return liste_complete[0][:NB_AFFICHAGE], liste_complete
    if taille == 2:
        return liste_complete[0][:NB_AFFICHAGE//2 + 1] + liste_complete[1][:NB_AFFICHAGE//2 - 1], liste_complete
    if taille > 2:
        nb_trois = NB_AFFICHAGE - (NB_AFFICHAGE//2 + 1 + NB_AFFICHAGE//4 + 1)
        return liste_complete[0][:NB_AFFICHAGE//2 + 1] + liste_complete[1][:NB_AFFICHAGE//4 + 1] + liste_complete[2][:nb_trois], liste_complete