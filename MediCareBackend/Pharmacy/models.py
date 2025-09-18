from django.db import models
from django.conf import settings


class Pharmacy(models.Model):
    pharmacy_id = models.CharField(max_length=45)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=45)
    created_on = models.DateField(auto_now_add=True)
    contact_no = models.CharField(max_length=45, unique=True)

    class Meta:
        unique_together = ('pharmacy_id', 'user')

    def __str__(self):
        return self.pharmacy_name or self.pharmacy_id