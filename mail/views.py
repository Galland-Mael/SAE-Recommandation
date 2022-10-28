from django.shortcuts import render
from django.core.mail import send_mail
import random

def verif_email(request):
    ''' Fonction qui permet l'envoi d'un mail à un utilisateur depuis l'adresse mail du site web '''
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
        "Code de vérification :\n"
        + "         " + random_value()
        + "\n\nL'équipe EatAdvisor",
        "eat_advisor3@outlook.fr",
        ["matteo.miguelez@gmail.com"],
        fail_silently=False);
    except:
        print("test")
    return render(request, 'send/mailtest.html')

def random_value():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
    return value_random