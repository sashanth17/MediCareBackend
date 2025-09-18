from django.urls import path,include
from .views import ListDoctorView,DoctorDetailView
urlpatterns=[
    path('',ListDoctorView.as_view()),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail')
    ]