from django.urls import path
from .views import AcceptCall,RecieveCall
urlpatterns = [
    path('AcceptCall',AcceptCall),
    path('RecieveCall',RecieveCall),
]
