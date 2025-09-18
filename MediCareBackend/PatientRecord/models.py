from django.db import models
from django.conf import settings

class PatientRecord(models.Model):
    record_id = models.CharField(max_length=45, primary_key=True)
    doctor = models.ForeignKey("Doctor.Doctor", on_delete=models.CASCADE)  # ✅ Use string reference
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor_note = models.TextField(blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"Record {self.record_id} - {self.user.username}"
