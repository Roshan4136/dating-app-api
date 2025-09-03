from django.contrib.auth.models import BaseUserManager

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email field is required.")
        if not password:
            raise ValueError("Superuser must have a password.")
        
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("superuser must have is_staff=true")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("superuser must have is_superuser=true")
        
        return self.create_user(email, password, **extra_fields)
    