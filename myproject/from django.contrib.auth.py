from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female')), null=True, blank=True)


