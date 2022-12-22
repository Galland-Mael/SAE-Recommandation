from django.forms import ModelForm
from appsae.model.models import RestaurantType
from appsae.model.models import Adherant
from django import forms


class RestaurantTypeForm(ModelForm):
    class Meta:
        model = RestaurantType

        fields = ['nom']


class AdherantForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Adherant
        fields = ['prenom','nom','birthDate','pseudo','mail','password']


class verifLogin(ModelForm):
    class Meta:
        model = Adherant
        fields =['mail','password']


