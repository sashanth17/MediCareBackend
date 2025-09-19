from django.urls import path
from .views import AcceptCall,RecieveCall
from .views import CreateOffer,RecievePatientOffer
urlpatterns = [
    path('AcceptCall/',AcceptCall),
    path("RecieveCall/", RecieveCall, name="recieve-call"),
    path('CreateOffer/',CreateOffer),
    path('RecievePatientOffer/',RecievePatientOffer),
]
