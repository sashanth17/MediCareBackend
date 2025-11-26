from django.urls import path,include
from .views import MedicineListView,MedicineDetailView,MedicineByNameView
urlpatterns=[
    path('', MedicineListView.as_view(), name='medicine-list'),
    path("<str:medicine_id>/", MedicineDetailView.as_view(), name="medicine-detail"),
    path('name/<str:medicine_name>/', MedicineByNameView.as_view(), name='medicine-by-name'),
]