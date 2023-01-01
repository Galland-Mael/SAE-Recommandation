from .models import *
from statistics import mean

NB_AFFICHAGE = 10  # Nombre d'éléments à afficher (carrousels)
NB_MAX_RECOMMANDATION = 1000  # Nombre maximum de restaurants à recommandés


def tri(list):
    """ Algorithme de tri sélection par ordre décroissant avec une liste de tuples

    @param list: liste de tuples [(Restaurant1, moyenne1), ...]
    @return: la liste de tuples triée
    """
    for i in range(len(list)):
        # Trouver le max
        max = i
        for j in range(i + 1, len(list)):
            if list[max][1] < list[j][1]:
                max = j

        tmp = list[i]
        list[i] = list[max]
        list[max] = tmp
    return list


def recommandationGroupeAvisGroupeComplet(groupe, ville):
    """ Algorithme de recommandation pour un groupe dans une ville

    @param groupe: le groupe
    @param ville: la ville où veut manger le groupe
    @return: une liste de restaurants limité à NB_MAX restaurants
    """
    list_user = groupe.liste_adherants.all()  # Liste des membres du groupe
    dico_type = {}  # Dictionnaire de la forme {type : [note1, note2,...]}
    list_resto = []  # Liste contenant les restaurants déjà visités par au moins un des membres du groupe
    list = []  # Liste de types de la forme [(type1, moyenne1), (type2, moyenne2), ...]

    # Parcours tous les avis postés par les utilisateurs du groupe où la note est supérieur ou égale à 3.5
    for avis in Avis.objects.filter(adherant_fk__in=list_user).exclude(note__lte=3.5):
        # Ajout du restaurant de l'avis dans la liste des restaurants déjà visités
        if (avis.restaurant_fk.ville == ville and avis.restaurant_fk not in list_resto):
            list_resto.append(avis.restaurant_fk.id_yelp)

        # Parcours les types de restaurants du restaurant de l'avis
        for types in avis.restaurant_fk.type.all():
            # Ajout de la note du restaurant dans le dictionnaire des types
            if (types not in dico_type.keys()):
                dico_type[types] = []
                dico_type[types].append(avis.note)
            else:
                dico_type[types].append(avis.note)

    # Remplit la liste à partir du dictionnaire de types
    for cle, valeur in dico_type.items():
        moyenne = round(mean(valeur), 2) # Moyenne à 10 puissance-2
        # Si la moyenne des notes des utilisateurs sur le types est supérieur ou égale à 3.5
        if moyenne >= 3.5:
            # Ajout du type et de la moyenne à la liste
            list.append((cle, moyenne))

    # S'il n'y a pas de recommandation on renvoie "LISTE VIDE"
    if len(list) == 0:
        return "LISTE VIDE"

    list = tri(list)  # Tri de la liste dans l'odre décroissant des notes

    # Liste de liste [[Resto1, R2, ...],[R3,...], ...], chaque sous-liste = restaurants qui ont un type en commun
    restaurants_par_type = []
    for i in range(len(list)):
        # liste_temp contient tous les restaurants de la ville avec le type demandé, non visité par un des utilisateurs
        # du groupe et trié par ordre décroissant
        list_temp = Restaurant.objects.filter(ville=ville, type=list[i][0]).exclude(id_yelp__in=list_resto).order_by("-note")
        if len(list_temp) != 0:
            restaurants_par_type.append(list_temp)

    liste_best = []; liste_second = []; liste_no_note = [] # Listes des meilleurs recommandations, des secondaires et celles sans note
    nb_elem_1 = 0; nb_elem_2 = 0 # Nombre d'éléments dans les deux premières listes
    num_type = 0 # Le numéro du type dans la liste
    finish = False # Booléen pour savoir s'il y a assez de valeurs dans la liste

    # Parcours de la liste restaurants_par_type
    for liste_elem in restaurants_par_type:
        # Parcours des sous listes de restaurants_par_type
        for elem in liste_elem:
            # Si la note est bonne et que le restaurant n'est pas déjà présent dans la liste
            if elem.note >= (3.75 + 0.05 * num_type) and elem not in liste_best and elem not in liste_second:
                liste_best.append(elem)
                nb_elem_1 += 1
                # Si il y a déjà NB_MAX élements dans la première liste, on arête la recherche de recommandations
                if nb_elem_1 > NB_MAX_RECOMMANDATION:
                    finish = True
                    break
            # Sinon si la note est supérieur et égale à 2.75, pas dans la liste_second et que le nombres d'elements
            # dans les listes 1 et 2 est inférieur au nombre maximum d'éléments à renvoyer
            elif (nb_elem_1 + nb_elem_2) < NB_MAX_RECOMMANDATION and elem.note >= 2.75 and elem not in liste_second:
                liste_second.append(elem)
                nb_elem_2 += 1
            # sinon si le restaurant n'a pas de note
            elif elem.note == -1:
                liste_no_note.append(elem)
        # Si finish vaut True on sort de la boucle car il y a assez de recommandations dans la liste
        if finish:
            break
        if num_type < 10:
            num_type += 1

    nb_elem_3 = NB_MAX_RECOMMANDATION - nb_elem_2 - nb_elem_1  # Nombre d'éléments à mettre dans la liste
    indice = 0  # Indice dans la liste
    taille_last = len(liste_no_note)  # Taille de la liste de restaurants sans notes
    list_last = []  # Nouvelle liste des restaurants sans note pour retirer les doublons

    # Tant que le nombre d'élements nécessaires dans la troisième liste est > à 0 et que la liste à encore des éléments
    while (nb_elem_3 > 0 and indice != taille_last):
        # si l'élément n'est pass déjà dans la liste
        if (liste_no_note[num_type] not in list_last):
            list_last.append(liste_no_note[num_type])
            nb_elem_3 -= 1
        indice += 1

    return liste_best + liste_second + list_last