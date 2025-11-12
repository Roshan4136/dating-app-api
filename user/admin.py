from django.contrib import admin
from .models import MyUser, Image, Hobby, Profile, SocialLink, LifestyleChoice

# Register your models here.
admin.site.register(MyUser)
admin.site.register(Image)
admin.site.register(Hobby)
admin.site.register(Profile)
admin.site.register(LifestyleChoice)
admin.site.register(SocialLink)