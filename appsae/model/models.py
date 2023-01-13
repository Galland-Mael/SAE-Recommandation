import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Adherant(models.Model):
    id = models.IntegerField(default=0)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    mail = models.EmailField(primary_key=True)
    birthDate = models.DateField("Date", default=datetime.date.today)
    pseudo = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    profile_picture = models.ImageField(default='img_user/avatar.jpeg', upload_to='img_user/')
    ville = models.CharField(max_length=100, default="none")


class Groupe(models.Model):
    idGroupe = models.IntegerField(default=0, blank=False)
    nom_groupe = models.CharField(max_length=25)
    liste_adherants = models.ManyToManyField(Adherant)
    id_gerant = models.IntegerField(default=-1)

    def __str__(self):
        return self.nom_groupe


class RestaurantType(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom


class ImageRestaurant(models.Model):
    idRestaurant = models.IntegerField(default=0,blank=False)
    image = models.ImageField(upload_to='liste_images')
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.idRestaurant)


class Restaurant(models.Model):
    id_yelp = models.CharField(max_length=150, default='')
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=50)
    ville = models.CharField(max_length=50, default='')
    zip_code = models.CharField(max_length=50, default='')
    pays = models.CharField(max_length=50)
    etat = models.CharField(max_length=50, default='')
    telephone = models.CharField(max_length=10)
    note = models.FloatField(validators=[MaxValueValidator(5), MinValueValidator(0)], default=0)
    image_front = models.ImageField(upload_to='img_restaurant/')
    type = models.ManyToManyField(RestaurantType)
    img = models.ManyToManyField(ImageRestaurant)

    def __str__(self):
        return str(self.nom)


class Horaire(models.Model):

    class Nom_jour(models.IntegerChoices):
        Lundi= 1
        Mardi = 2
        Mercredi = 3
        Jeudi = 4
        Vendredi = 5
        Samedi = 6
        Dimanche = 7

    Nom_jour = models.IntegerField(choices=Nom_jour.choices)
    Debut_Horaire1 = models.TimeField(default='00:00')
    Fin_Horaire1 = models.TimeField(default='00:00')
    Debut_Horaire2 = models.TimeField(default='00:00')
    Fin_Horaire2 = models.TimeField(default='00:00')
    Debut_Horaire3 = models.TimeField(default='00:00')
    Fin_Horaire3 = models.TimeField(default='00:00')

    def __str__(self):
        return self.Nom_jour


class Avis(models.Model):
    note = models.FloatField(validators=[MaxValueValidator(5), MinValueValidator(0)],default=0)
    texte = models.CharField(max_length=1000, default=" ")
    restaurant_fk = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    adherant_fk = models.ForeignKey(Adherant, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Avis'
        constraints = [
            models.UniqueConstraint(fields=['restaurant_fk', 'adherant_fk'], name='unique avis')
        ]

    def __str__(self):
        return str(self.restaurant_fk) + " - " + str(self.adherant_fk)


