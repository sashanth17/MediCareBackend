from django.db import models
from django.conf import settings



class Hospital(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital_id = models.CharField(max_length=45, unique=True)
    hospital_name = models.CharField(max_length=45)
    bio = models.TextField()
    contact = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=45)

    def __str__(self):
        return self.hospital_name
