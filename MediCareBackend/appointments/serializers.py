# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Appointment
from Doctor.models import Doctor

User = get_user_model()


class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
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
            "created_at",
            "actual_start",
            "actual_end",
            "status"
        ]


class AppointmentCreateByPhoneSerializer(serializers.Serializer):
    """
    Create an appointment using:
    - doctor_name (matches doctor.user first_name, last_name, or username)
    - phone_number (must belong to a registered user)
    """
    doctor_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    appointment_date = serializers.DateField(input_formats=["%Y-%m-%d"])
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_doctor_name(self, value):
        value = value.strip()

        # Search doctor by user fields, NOT doctor.name (which doesn't exist)
        qs = Doctor.objects.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__username__icontains=value)
        )

        if not qs.exists():
            raise serializers.ValidationError("No doctor found matching that name.")

        return qs.first()  # simple: pick first match

    def validate_phone_number(self, value):
        phone = value.strip()

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this phone number.")

        return user

    def validate(self, attrs):
        attrs["doctor_instance"] = attrs.pop("doctor_name")
        attrs["patient_instance"] = attrs.pop("phone_number")
        return attrs

    def create(self, validated_data):
        doctor = validated_data["doctor_instance"]
        patient = validated_data["patient_instance"]
        appointment_date = validated_data["appointment_date"]
        notes = validated_data.get("notes", "")

        appointment_number = Appointment.issue_appointment_number(doctor, appointment_date)

        return Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            appointment_date=appointment_date,
            appointment_number=appointment_number,
            status="booked",
            notes=notes
        )
