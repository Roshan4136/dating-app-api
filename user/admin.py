from django.contrib import admin
from .models import MyUser, Image, Interest, Profile
# Register your models here.
admin.site.register(MyUser)
admin.site.register(Image)
admin.site.register(Interest)
admin.site.register(Profile)