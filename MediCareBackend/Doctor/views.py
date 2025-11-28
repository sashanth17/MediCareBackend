from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Doctor
from .serializers import DoctorSerializer, DoctorDetailSerializer


# ---------------------------------------------------------
# List All Doctors
# ---------------------------------------------------------
class ListDoctorView(APIView):
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------
# Doctor Detail View (Retrieve / Update)
# ---------------------------------------------------------
class DoctorDetailView(APIView):
    """
    View to retrieve or update a doctor's profile.
    """

    def get(self, request, pk, *args, **kwargs):
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorDetailSerializer(doctor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        doctor = get_object_or_404(Doctor, pk=pk)
        serializer = DoctorDetailSerializer(doctor, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------
# Search Doctors by Designation
# ---------------------------------------------------------
class SearchDoctorByDesignationAPIView(APIView):
    """
    GET /Doctors/search/?q=cardio

    Searches doctors by designation (case-insensitive).
    """

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()

        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        doctors = Doctor.objects.filter(designation__icontains=query)


        if not doctors.exists():
            return Response(
                {"detail": f"No doctor found for '{query}'"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DoctorSerializer(doctors, many=True)

        return Response(
            {
                "searched_for": query,
                "count": doctors.count(),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )
