from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    profile_picture = models.ImageField(default='default_profile_pic.jpg')
