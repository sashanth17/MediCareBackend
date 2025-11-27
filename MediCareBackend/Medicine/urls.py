# medicines/urls.py
from django.urls import path
from .views import MedicineListView, MedicineDetailView, SearchMedicineByNameAPIView

urlpatterns = [
    # MUST be first so "<str:pk>/" doesn't capture "search"
    path("search/", SearchMedicineByNameAPIView.as_view(), name="medicine-search"),

    # list of all medicines
    path("", MedicineListView.as_view(), name="medicine-list"),

    # detail by medicine_id (keep this AFTER the search route)
    path("<str:medicine_id>/", MedicineDetailView.as_view(), name="medicine-detail"),
]
