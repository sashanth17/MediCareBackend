from django.urls import path
from .views import patient_get_answer,doctor_poll_view,create_offer
urlpatterns = [
    path('CreateOffer/', create_offer, name='CreateOffer'),
    path('DoctorPoll/', doctor_poll_view, name='DoctorPoll'),
    path('patient_get_answer/', patient_get_answer, name='patient_get_answer'),   
]
