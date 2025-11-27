from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from datetime import date

from Doctor.models import Doctor    # CHANGE if your doctor model name/path differs


class DailyAppointmentCounter(models.Model):
    """
    Stores last appointment_number for each doctor on each date.
    This resets daily automatically because date is part of the key.
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointment_counters")
    date = models.DateField()
    last = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("doctor", "date")

    def __str__(self):
        return f"{self.doctor} - {self.date}: {self.last}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")

    appointment_date = models.DateField()
    appointment_number = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="booked")

    created_at = models.DateTimeField(auto_now_add=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("doctor", "appointment_date", "appointment_number")
        ordering = ("appointment_date", "appointment_number")

    def __str__(self):
        return f"{self.doctor} | {self.appointment_date} | #{self.appointment_number} ({self.status})"

    # --- appointment number generator ---
    @classmethod
    def issue_appointment_number(cls, doctor, appointment_date):
        from .models import DailyAppointmentCounter

        with transaction.atomic():
            counter, created = DailyAppointmentCounter.objects.select_for_update().get_or_create(
                doctor=doctor,
                date=appointment_date,
                defaults={"last": 0},
            )
            counter.last += 1
            counter.save(update_fields=["last"])
            return counter.last

    @classmethod
    def appointments_for_date(cls, doctor, the_date=None):
        if the_date is None:
            the_date = timezone.localdate()
        return cls.objects.filter(doctor=doctor, appointment_date=the_date).order_by("appointment_number")
