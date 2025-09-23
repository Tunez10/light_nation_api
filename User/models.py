# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
import uuid
import random
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password before saving
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
    



class User(AbstractBaseUser, PermissionsMixin):
   
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=200, unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=200,  blank=False, null=True)
    last_name = models.CharField(max_length=200,  blank=False, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # ✅ Allows leading zeros
    title = models.CharField(max_length=100, blank=True, null=True)
    datejoined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    social_links = models.CharField(max_length=300, blank=True)


    USERNAME_FIELD = 'email'  # <--- Primary login field
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Fields prompted when running createsuperuser

    objects = CustomUserManager()

    def __str__(self):
        return self.username if self.username else self.email or "Unknown User"  # ✅ Always returns a string

    # ✅ Add this method
    def has_perm(self, perm, obj=None):
        return self.is_superuser  # Superusers have all permissions

    # ✅ Add this method
    def has_module_perms(self, app_label):
        return self.is_superuser  # Superusers have all module permissions
    


# models.py



class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=6, unique=True)  # 6-digit numeric token
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(random.randint(100000, 999999))  # generate 6-digit code
        super().save(*args, **kwargs)

    

