from django.urls import path
from .views import ListDoctorView, DoctorDetailView, SearchDoctorByDesignationAPIView

urlpatterns = [
    # Search route MUST be first
    path("search/", SearchDoctorByDesignationAPIView.as_view(), name="doctor-search"),

    # List all doctors
    path("", ListDoctorView.as_view(), name='doctor-list'),

    # Doctor detail
    path("<int:pk>/", DoctorDetailView.as_view(), name='doctor-detail'),
]
