# user/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import MyUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from datetime import date
# from django.contrib.gis.db import models as gis_models

# Create your models here.
class ZodiacSign(models.TextChoices):
    ARIES = 'aries', 'aries'
    TAURUS = 'taurus', 'taurus'
    GEMINI = 'gemini', 'gemini'
    CANCER = 'cancer', 'cancer'
    LEO = 'leo', 'leo'
    VIRGO = 'virgo', 'virgo'
    LIBRA = 'libra', 'libra'
    SCORPIO = 'scorpio', 'scorpio'
    SAGITTARIUS = 'sagittarius', 'sagittarius'
    CAPRICORN = 'capricorn', 'capricorn'
    AQUARIUS = 'aquarius', 'aquarius'
    PISCES = 'pisces', 'pisces'

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
    REQUIRED_FIELDS = ['phone_no']

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()

        super().save(*args, **kwargs)

    def __str__(self):
        if self.email:
            return f"{self.email} (id: {self.id})"
        elif self.phone_no:
            return f"{self.phone_no} (id: {self.id})"
        return f"Unnamed User (id: {self.id})"

    
# hobbies
class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class LifestyleChoice(models.Model):
    name = models.CharField(max_length=40, unique=True)

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
    show_orientation = models.BooleanField(default=False)
    interests = models.ManyToManyField(Interest, blank=True, related_name='profiles')
    lifestyle_choices = models.ManyToManyField(LifestyleChoice, related_name='profiles_with_lifestyle')
    zodiac_sign = models.CharField(max_length=20, choices=ZodiacSign.choices, null=True, blank=True)
    show_zodiac = models.BooleanField(default=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["latitude", "longitude"]),  # for geo/location queries
        ]

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
        return f"{self.first_name} {self.last_name}, profile_id : {self.id} and user_id: {self.user.id}"

class Image(models.Model):
    profile = models.ForeignKey(Profile, related_name='images', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"photo of {self.profile.user.email}"

class SocialLink(models.Model):
    profile = models.ForeignKey(Profile, related_name='social_links', on_delete=models.CASCADE)
    link_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'link_url')
        
    def __str__(self):
        return f"social link of {self.profile.user.email}"

    



