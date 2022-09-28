from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """abstract user class for user authentication"""
    first_name = models.CharField('First Name', blank=True, max_length=100)
    last_name = models.CharField('Last Name', blank=True, max_length=100)
    email = models.CharField('Email', unique=True, max_length=100)
