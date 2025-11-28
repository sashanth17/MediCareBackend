# views.py
from datetime import date as date_cls
from typing import Optional

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateByPhoneSerializer
from Doctor.models import Doctor

User = get_user_model()


# -----------------------
# Helpers (re-used)
# -----------------------
def _parse_date_param(date_str: Optional[str]) -> date_cls:
    """
    Parse YYYY-MM-DD string to date. If None, return today's local date.
    Raises ValueError on invalid format.
    """
    if date_str:
        return date_cls.fromisoformat(date_str)
    return timezone.localdate()


def _doctor_display_name(doctor: Doctor) -> str:
    # flexible display depending on doctor model structure
    if hasattr(doctor, "name"):
        return doctor.name
    if hasattr(doctor, "user") and callable(getattr(doctor.user, "get_full_name", None)):
        return doctor.user.get_full_name() or doctor.user.username
    return str(doctor)


def _is_now_within_doctor_time(doctor: Doctor) -> bool:
    # guard: if doctor model has start_time/end_time, check them; otherwise allow
    if not (hasattr(doctor, "start_time") and hasattr(doctor, "end_time")):
        return True
    now = timezone.localtime().time()
    return doctor.start_time <= now <= doctor.end_time


# -----------------------
# Views
# -----------------------
class BookAppointmentByPhoneAPIView(APIView):
    """
    Book appointment using doctor's name (partial match) and a registered user's phone_number.
    """
    def post(self, request):
        serializer = AppointmentCreateByPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = serializer.save()

        # Optional: prevent same-day booking outside working hours
        if appointment.appointment_date == timezone.localdate() and not _is_now_within_doctor_time(appointment.doctor):
            # rollback created appointment to avoid leaving an invalid booking
            appointment.delete()
            return Response({"detail": "Doctor not available at this time"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = AppointmentSerializer(appointment).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class AppointmentListAPIView(ListAPIView):
    """
    List all appointments. You can add pagination by configuring DRF pagination.
    """
    queryset = Appointment.objects.all().order_by("-created_at")
    serializer_class = AppointmentSerializer


class AppointmentsForDoctorAPIView(APIView):
    """
    Returns all appointments for a doctor.
    Two ways to call:
      - by doctor_id: GET /api/appointments/doctor/<int:doctor_id>/
      - by doctor_name query param: GET /api/appointments/doctor/?name=Dr%20John
    """
    def get(self, request, doctor_id=None):
        name_q = request.query_params.get("name")
        doctor = None

        if doctor_id is not None:
            doctor = get_object_or_404(Doctor, pk=doctor_id)
        elif name_q:
            qs = Doctor.objects.filter(name__icontains=name_q.strip())
            if not qs.exists():
                return Response({"detail": f"No doctor found matching '{name_q}'"}, status=status.HTTP_404_NOT_FOUND)
            doctor = qs.first()
        else:
            return Response({"detail": "Provide doctor_id in path or name query parameter."},
                            status=status.HTTP_400_BAD_REQUEST)

        # optional date filter ?date=YYYY-MM-DD
        try:
            the_date = _parse_date_param(request.query_params.get("date"))
        except ValueError:
            return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        appts = Appointment.appointments_for_date(doctor, the_date)
        serializer = AppointmentSerializer(appts, many=True)
        return Response({
            "doctor": _doctor_display_name(doctor),
            "date": str(the_date),
            "appointments": serializer.data
        }, status=status.HTTP_200_OK)


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

# paste/replace this class in views.py
from django.db.models import Q  # ensure this import exists at top of views.py

class SearchAppointmentsByDoctorNameAPIView(APIView):
    """
    Search appointments by doctor name using ?q= (matches Doctor.user first_name, last_name, username).
    Example: /api/appointments/search/?q=john&date=YYYY-MM-DD
    """
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"detail": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Search doctor by related user fields (first_name, last_name, username)
        doctor_qs = Doctor.objects.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q)
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

