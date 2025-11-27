from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    patient_username = serializers.CharField(source="patient.username", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor", "doctor_name",
            "patient", "patient_username",
            "appointment_date", "appointment_number",
            "status",
            "created_at", "actual_start", "actual_end",
            "notes"
        ]
        read_only_fields = [
            "appointment_number",
            "appointment_date",
            "created_at",
            "actual_start",
            "actual_end",
            "status"
        ]
