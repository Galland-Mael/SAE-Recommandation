from .models import Adherant


def updateMdp(mail_user, password):
    """ Fonction de mise à jour du mot de passe d'un utilisateur à partir de son mail

    @param mail_user: le mail de l'utilisateur
    @param password: le nouveau mot de passe de l'utilisateur
    @return: /
    """
    Adherant.objects.filter(mail=mail_user).update(password=password)


def updateNom(mail_user, nom):
    """ Fonction de mise à jour du nom d'un utilsateur à partir de son mail

    @param mail_user: le mail de l'utilisateur
    @param nom: le nouveau nom de l'utilisateur
    @return: /
    """
    Adherant.objects.filter(mail=mail_user).update(nom=nom)


def updatePrenom(mail_user, prenom):
    """ Fonction de mise à jour du nom d'un utilsateur à partir de son mail

    @param mail_user: le mail de l'utilisateur
    @param prenom: le nouveau nom de l'utilisateur
    @return: /
    """
    Adherant.objects.filter(mail=mail_user).update(prenom=prenom)


def updateDate(mail_user, birthdate):
    """ Fonction de mise à jour du nom d'un utilsateur à partir de son mail
    La date est au format AAAA-MM-JJ

    @param mail_user: le mail de l'utilisateur
    @param birthdate: la nouvelle date de naissance de l'utilisateur
    @return: /
    """
    Adherant.objects.filter(mail=mail_user).update(birthDate=birthdate)


def updatePseudo(mail_user, pseudo):
    """ Fonction de mise à jour du nom d'un utilsateur à partir de son mail

    @param mail_user: le mail de l'utilisateur
    @param pseudo: le nouveau pseudo de l'utilisateur
    @return: /
    """
    Adherant.objects.filter(mail=mail_user).update(pseudo=pseudo)


def updateProfilPick(mail_user, profile_picture):
    """ Fonction de mise à jour du nom d'un utilsateur à partir de son mail

    @param mail_user: le mail de l'utilisateur
    @param profile_picture: la nouvelle photo de profil de l'utilisateur
    @return: /
    """
    Adherant.objects.filter(mail=mail_user).update(profile_picture=profile_picture)