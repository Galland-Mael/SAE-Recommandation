import os.path
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .formulaire import *
from django.core.mail import send_mail
import random
from django.shortcuts import render
from django.http import HttpResponse


def register(request):
    if request.method == "POST":
        '''Remplissage de la base de données'''
        form = AdherantForm(request.POST).save()
        print(request.POST["mail"])
        return redirect('login')
    form = AdherantForm()
    return render(request, 'user/register.html', {'form': form, 'info': Adherant.objects.all})
    # return JsonResponse({"form": list(form.values) })


def login(request):
    if request.method == "POST":
        mail = request.POST['mail']
        password = request.POST['password']
        '''Récuperation des données'''
        info = Adherant.objects.all()
        contain = False
        for adherant in info:
            '''Verification'''
            if (mail == adherant.mail):
                if (password == adherant.password):
                    contain = True
        if contain:
            return redirect('index')
        else:
            messages.success(request, '*Wrong mail or password')
            return redirect('login')
    else:
        return render(request, 'user/login.html')

def index(request):
    return render(request,'index.html')
def modifUser(request):
    return render(request, 'user/modifUser.html')


def verificationEmail(request):
    print("apeler")
    ''' Fonction qui permet l'envoi d'un mail à un utilisateur depuis l'adresse mail du site web '''
    try:
        send_mail("Vérification de votre compte - Ne pas répondre",
                  "Code de vérification :\n"
                  + "         " + randomValue()
                  + "\n\nL'équipe EatAdvisor",
                  "eat_advisor2@outlook.fr",
                  ["maelgalland.71@gail.com"],
                  fail_silently=False);
        print("reussi")
    except:
        print("fail")
        return HttpResponse("<p>Next</p>")


def randomValue():
    ''' Fonction qui renvoie une chaîne composée de 6 caractères entre 0 et 9 '''
    value_random = ""
    for i in range(6):
        value_random += str(random.randint(0, 9))
    return value_random

