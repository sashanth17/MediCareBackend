# urls.py
from django.urls import path
from .views import (
    BookAppointmentByPhoneAPIView,
    AppointmentListAPIView,
    AppointmentsForDoctorAPIView,
    StartAppointmentAPIView,
    CompleteAppointmentAPIView,
    NextAppointmentAPIView,
    SearchAppointmentsByDoctorNameAPIView,
)

urlpatterns = [
    path("book/", BookAppointmentByPhoneAPIView.as_view(), name="appointment-book"),
    path("", AppointmentListAPIView.as_view(), name="appointments-list"),
    # appointments for a doctor by id (path) or by ?name= query param:
    path("doctor/<int:doctor_id>/", AppointmentsForDoctorAPIView.as_view(), name="appointments-for-doctor-by-id"),
    path("doctor/", AppointmentsForDoctorAPIView.as_view(), name="appointments-for-doctor-by-name"),
    path("<int:appointment_id>/start/", StartAppointmentAPIView.as_view(), name="appointment-start"),
    path("<int:appointment_id>/complete/", CompleteAppointmentAPIView.as_view(), name="appointment-complete"),
    path("doctor/<int:doctor_id>/next/", NextAppointmentAPIView.as_view(), name="appointment-next"),
    path("search/", SearchAppointmentsByDoctorNameAPIView.as_view(), name="appointments-search"),
]
