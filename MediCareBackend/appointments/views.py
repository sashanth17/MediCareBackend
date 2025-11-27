from datetime import date as date_cls
from typing import Optional

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment
from .serializers import AppointmentSerializer
from Doctor.models import Doctor

User = get_user_model()


# -----------------------
# Helper functions
# -----------------------
def _parse_date_param(date_str: Optional[str]) -> date_cls:
    """
    Parse YYYY-MM-DD string to date. If None, return today's local date.
    Raises ValueError on invalid format.
    """
    if date_str:
        return date_cls.fromisoformat(date_str)
    return timezone.localdate()


def _get_patient_from_request(request, data: dict):
    """
    Resolve patient: prefer authenticated user; otherwise expect patient_id in POST data.
    """
    if request.user and request.user.is_authenticated:
        return request.user
    patient_id = data.get("patient_id")
    if not patient_id:
        return None
    return get_object_or_404(User, pk=patient_id)


def _doctor_display_name(doctor: Doctor) -> str:
    if hasattr(doctor, "user") and callable(getattr(doctor.user, "get_full_name", None)):
        return doctor.user.get_full_name() or doctor.user.username
    return getattr(doctor, "id", "Unknown")


def _is_now_within_doctor_time(doctor: Doctor) -> bool:
    now = timezone.localtime().time()
    return doctor.start_time <= now <= doctor.end_time


# -----------------------
# Views
# -----------------------
class BookAppointmentAPIView(APIView):
    """
    Create a new Appointment and return serialized instance.
    """
    def post(self, request):
        data = request.data or {}

        doctor = get_object_or_404(Doctor, pk=data.get("doctor_id"))

        patient = _get_patient_from_request(request, data)
        if not patient:
            return Response(
                {"detail": "Patient not provided and user not authenticated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # parse appointment_date or use today
        try:
            appointment_date = _parse_date_param(data.get("appointment_date"))
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # optional: ensure booking permitted during doctor's hours when booking for today
        if appointment_date == timezone.localdate() and not _is_now_within_doctor_time(doctor):
            return Response({"detail": "Doctor not available at this time"}, status=status.HTTP_400_BAD_REQUEST)

        appointment_number = Appointment.issue_appointment_number(doctor, appointment_date)

        appt = Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            appointment_date=appointment_date,
            appointment_number=appointment_number,
            status="booked",
            notes=data.get("notes", "")
        )

        serializer = AppointmentSerializer(appt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentsForDateAPIView(APIView):
    """
    GET appointments for a doctor on a specific date.
    URL example: /api/doctor/<doctor_id>/appointments/?date=YYYY-MM-DD
    """
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, pk=doctor_id)

        try:
            the_date = _parse_date_param(request.query_params.get("date"))
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        appts = Appointment.appointments_for_date(doctor, the_date)
        serializer = AppointmentSerializer(appts, many=True)
        return Response({"date": str(the_date), "appointments": serializer.data}, status=status.HTTP_200_OK)


class StartAppointmentAPIView(APIView):
    """
    Mark a booked appointment as in_progress and set actual_start.
    """
    def post(self, request, appointment_id):
        appt = get_object_or_404(Appointment, pk=appointment_id)

        if appt.status != "booked":
            return Response({"detail": "Appointment cannot be started"}, status=status.HTTP_400_BAD_REQUEST)

        appt.status = "in_progress"
        appt.actual_start = timezone.now()
        appt.save(update_fields=["status", "actual_start"])

        return Response(AppointmentSerializer(appt).data, status=status.HTTP_200_OK)


class CompleteAppointmentAPIView(APIView):
    """
    Mark appointment as completed and set actual_end.
    """
    def post(self, request, appointment_id):
        appt = get_object_or_404(Appointment, pk=appointment_id)

        if appt.status not in ("booked", "in_progress"):
            return Response({"detail": "Appointment cannot be completed"}, status=status.HTTP_400_BAD_REQUEST)

        appt.status = "completed"
        appt.actual_end = timezone.now()
        appt.save(update_fields=["status", "actual_end"])

        return Response(AppointmentSerializer(appt).data, status=status.HTTP_200_OK)


class NextAppointmentAPIView(APIView):
    """
    Return the next booked appointment for today (lowest appointment_number).
    """
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        today = timezone.localdate()

        next_appt = (
            Appointment.objects
            .filter(doctor=doctor, appointment_date=today, status="booked")
            .order_by("appointment_number")
            .first()
        )

        if not next_appt:
            return Response({"detail": "No more appointments today"}, status=status.HTTP_404_NOT_FOUND)

        return Response(AppointmentSerializer(next_appt).data, status=status.HTTP_200_OK)


class SearchAppointmentsByDoctorNameAPIView(APIView):
    """
    Search appointments by doctor name using ?q= (matches user.username, first_name, last_name).
    Example: /api/appointments/search/?q=kumar&date=YYYY-MM-DD
    """
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"detail": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        doctor_qs = Doctor.objects.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )

        if not doctor_qs.exists():
            return Response({"detail": f"No doctor found matching '{q}'"}, status=status.HTTP_404_NOT_FOUND)

        doctor = doctor_qs.first()

        try:
            the_date = _parse_date_param(request.query_params.get("date"))
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        appts = Appointment.appointments_for_date(doctor, the_date)
        serializer = AppointmentSerializer(appts, many=True)

        return Response({
            "searched_for": q,
            "doctor_found": _doctor_display_name(doctor),
            "date": str(the_date),
            "appointments": serializer.data
        }, status=status.HTTP_200_OK)
