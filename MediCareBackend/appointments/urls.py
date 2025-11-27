from django.urls import path
from .views import (
    BookAppointmentAPIView,
    AppointmentsForDateAPIView,
    StartAppointmentAPIView,
    CompleteAppointmentAPIView,
    NextAppointmentAPIView,
    SearchAppointmentsByDoctorNameAPIView
)

urlpatterns = [
    path("book/", BookAppointmentAPIView.as_view()),
    path("doctor/<int:doctor_id>/", AppointmentsForDateAPIView.as_view()),
    path("<int:appointment_id>/start/", StartAppointmentAPIView.as_view()),
    path("<int:appointment_id>/complete/", CompleteAppointmentAPIView.as_view()),
    path("doctor/<int:doctor_id>/next/", NextAppointmentAPIView.as_view()),
    path("search/", SearchAppointmentsByDoctorNameAPIView.as_view(), name="appointments-search"),

]
