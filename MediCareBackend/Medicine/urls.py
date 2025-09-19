from django.urls import path,include
from .views import MedicineListView
urlpatterns=[
    path('', MedicineListView.as_view(), name='medicine-list'),
]