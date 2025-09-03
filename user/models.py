# user/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import MyUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from datetime import date
# from django.contrib.gis.db import models as gis_models

# Create your models here.
class Gender(models.TextChoices):
    MALE = 'male', 'male'
    FEMALE = 'female', 'female'
    OTHER = 'other', 'other'

class Relationship(models.TextChoices):
    FRIENDSHIP = 'friendship', 'friendship'
    DATING_ONLY = 'dating_only', 'dating_only'
    MARRIAGE = 'marriage', 'marriage'

class SexualOrientation(models.TextChoices):
    STRAIGHT = 'straight', 'straight'
    GAY = 'gay', 'gay'
    LESBIAN = 'lesbian', 'lesbian'
    BISEXUAL = 'bisexual', 'bisexual'
    ASEXUAL = 'asexual', 'asexual'
    DEMISEXUAL = 'demisexual', 'demisexual'
    PANSEXUAL = 'pansexual', 'pansexual'
    QUEER = 'queer', 'queer'
    QUESTIONING = 'questioning', 'questioning'

class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    phone_no = PhoneNumberField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or f"{self.phone_no}" or "Unnamed User"
    
class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='user_pp/',blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    looking_for = models.CharField(max_length=10, choices=Gender.choices, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    # location = gis_models.PointField(geography=True, blank=True, null=True)
    intention = models.CharField(max_length=20, choices=Relationship.choices, blank=True, null=True)
    sexual_orientation = models.CharField(max_length=20, choices=SexualOrientation.choices, blank=True, null=True)
    interests = models.ManyToManyField(Interest, blank=True, related_name='profiles', null=True)
    
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        age = today.year - self.dob.year
        if (today.month, today.day)<(self.dob.month, self.dob.day):
            age -=1
        return age
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Image(models.Model):
    profile = models.ForeignKey(Profile, related_name='images', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"photo of {self.profile.user.email}"
    

    



