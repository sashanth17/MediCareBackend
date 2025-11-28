# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=8, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ], blank=True, null=True)
    blood_group = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], blank=True, null=True)
    offer= models.CharField(max_length=64,blank=True)
    sdp = models.TextField(blank=True, null=True)
    ice_candidates = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def get_id(self):
        return self.id 
    @property
    def age(self):
        """Return age based on date_of_birth"""
        if self.date_of_birth:
            today = date.today()
            return (
                today.year - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return None