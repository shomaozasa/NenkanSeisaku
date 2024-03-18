from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    address = models.TextField()  # 顧客の住所
    phone_number = models.CharField(max_length=20)