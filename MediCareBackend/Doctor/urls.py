from django.urls import path
from .views import ListDoctorView, DoctorDetailView, SearchDoctorsAPIView
# SearchDoctorByDesignationAPIView,DoctorDetailByNameAPIView

urlpatterns = [
    # Search route MUST be first
    # path("search/", SearchDoctorByDesignationAPIView.as_view(), name="doctor-search"),

    # List all doctors
    path("", ListDoctorView.as_view(), name='doctor-list'),

    # Doctor detail
    path("<int:pk>/", DoctorDetailView.as_view(), name='doctor-detail'),

    #  path('by-name/', DoctorDetailByNameAPIView.as_view(), name='doctor-by-name'),

     path("search/", SearchDoctorsAPIView.as_view(), name="search-doctors"),
]
