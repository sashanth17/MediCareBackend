from django.db import models
import secrets
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    sdp = models.TextField(blank=True, null=True)
    ice_candidates = models.TextField(blank=True, null=True)
    token = models.CharField(max_length=64,editable=False,blank=True)
    token_created_at = models.DateTimeField(auto_now_add=True)

    def generate_token(self):
        """Generate a new secure token and update timestamp."""
        self.token = secrets.token_urlsafe(32)
        self.token_created_at = timezone.now()
        self.save(update_fields=["token", "token_created_at"])
        return self.token

    def is_token_expired(self, minutes=30):
        """Check if token is expired (default 30 min)."""
        return timezone.now() > self.token_created_at + timedelta(minutes=minutes)

    def __str__(self):
        return self.name