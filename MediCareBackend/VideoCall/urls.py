from django.urls import path
from .views import AcceptCall,RecieveCall
urlpatterns = [
    path('VideoCall/AcceptCall',AcceptCall),
    path('VideoCall/RecieveCall',RecieveCall),
]
