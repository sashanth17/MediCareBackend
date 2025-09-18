from django.urls import path
from .views import AddMedicineInstanceView,RemoveMedicineInstanceView

urlpatterns = [
    path("addmedicineinstance/", AddMedicineInstanceView.as_view(), name="add-medicine"),
    path("removemedicineinstance/", RemoveMedicineInstanceView.as_view(), name="remove-medicine"),
]
