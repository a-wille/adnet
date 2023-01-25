from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """abstract user class for user authentication"""
    firstname = models.CharField('First Name', blank=True, max_length=100)
    lastname = models.CharField('Last Name', blank=True, max_length=100)
    email = models.CharField('Email', unique=True, max_length=100)
    institution = models.CharField('Institution', max_length=100)

    class Meta:
        permissions = (
            ("can_create_jobs", "can make jobs"),
            ("cannot_create_jobs", "cannot make jobs")
        )

