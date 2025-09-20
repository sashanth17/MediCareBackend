from django.urls import path,include
from .views import MedicineListView,MedicineDetailView
urlpatterns=[
    path('', MedicineListView.as_view(), name='medicine-list'),
    path("<str:medicine_id>/", MedicineDetailView.as_view(), name="medicine-detail")
]