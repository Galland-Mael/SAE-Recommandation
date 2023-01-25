from django.http import request
from surprise import Dataset

from .views import *
from .models import *
from .svd import *
from time import mktime
from django.db.models import Avg
from django.conf import settings
from csv import writer


def addavisCSV(avis):
    list = [str(avis.adherant_fk_id), ' ' + str(avis.restaurant_fk_id), ' ' + str(float(avis.note))]

    with open(str(settings.BASE_DIR) + '/' + "ratings.csv", 'a') as f_object:
        f_object.write('\n')
        f_object.write(str(avis.adherant_fk_id)+ ', ' + str(avis.restaurant_fk_id) + ', ' + str(float(avis.note)))
        f_object.close()


def filterNomRestaurant(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789"
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
    return nouveau_nom


def avisExist(user, restaurant):
    """ Vérifie si l'utilisateur user a déjà ajouté un avis sur le restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: true si l'avis existe, false sinon
    """
    return Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).count() != 0


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


def ajoutAvis(user, restaurant, note, avis):
    """ Fonction permettant d'ajouter une note et un avis
    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    if avisExist(user, restaurant) == False:
        nb_review_ad = Adherant.objects.get(pk=user.pk).nb_review
        print("nb review adherannt :" + str(nb_review_ad))
        ajout = Avis(note=note, texte=avis, restaurant_fk=restaurant, adherant_fk=user)
        ajout.save()
        updateNoteMoyenneRestaurant(restaurant)
        if nb_review_ad > 5: # & tps dans la bd < à 200 secondes
            # algorecommendation
            a = 1
        addavisCSV(ajout)


def updateAvis(user, restaurant, note, avis):
    """ Mise à jour de le note (et l'avis) de l'utilisateur user pour le restaurant restaurant
    @param user: l'utilisateur
    @param restaurant: le restaurant
    @param note: la nouvelle note
    @param avis: le nouvel avis
    @return: /
    """
    if avisExist(user,restaurant):
        Avis.objects.filter(restaurant_fk=restaurant, adherant_fk=user).update(note=note, texte=avis)
        updateNoteMoyenneRestaurant(restaurant)


def suppressionAvis(user, restaurant):
    """ Suppression de l'avis de l'utilisateur user sur le restaurant restaurant

    @param user: l'utilisateur
    @param restaurant: le restaurant
    @return: /
    """
    if avisExist(user,restaurant):
        Avis.objects.get(restaurant_fk=restaurant, adherant_fk=user).delete()
        updateNoteMoyenneRestaurant(restaurant)


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


def listRecommandationGroupe(groupe):
    ratings_data = pd.read_csv('./ratings.csv')
    user_idgerant = Groupe.objects.get(pk=groupe.pk).id_gerant
    user = Adherant.objects.filter(pk=user_idgerant)
    restaurant_metadata = pd.read_csv('./restaurant_' + filterNomRestaurant(str(user[0].ville)) + '.csv', delimiter=';', engine='python')
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(ratings_data[['user_id', 'restaurant_id', 'note']], reader)
    trainset, testset = train_test_split(data, test_size=0.20)
    svd = SVD(verbose=False, n_epochs=23, n_factors=7)
    predictions = svd.fit(trainset).test(testset)
    accuracy.rmse(predictions)
    l = algoRecommandationGroupe(groupe, svd, restaurant_metadata, 100)
    liste_complete = []
    for elem in l:
        liste_complete.append(get_restaurant_id(elem[0], restaurant_metadata))
    return liste_complete


def ajoutBDRecommandationGroupe(groupe):
    reco_groupe= RecommandationGroupe.objects.filter(groupe_fk=groupe)
    if reco_groupe.count() == 0:
        reco = RecommandationGroupe(groupe_fk=groupe)
        reco.save()
        list = listRecommandationGroupe(groupe)
        for elem in list:
            reco.recommandation.add(elem)
        RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())
    else:
        date_actuelle = datetime.datetime.today().replace(tzinfo=None).timetuple()
        date_bd = reco_groupe[0].date.replace(tzinfo=None).timetuple()
        if mktime(date_bd) <= mktime(date_actuelle)-200:
            RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())
            list = listRecommandationGroupe(groupe)
            reco = RecommandationGroupe.objects.get(groupe_fk=groupe)
            list_Reco = reco.recommandation.all()
            for elem in list_Reco:
                reco.recommandation.remove(elem)
            reco = RecommandationGroupe.objects.get(groupe_fk=groupe)
            for elem in list:
                reco.recommandation.add(elem)
            RecommandationGroupe.objects.filter(groupe_fk=groupe).update(date=datetime.datetime.now())


