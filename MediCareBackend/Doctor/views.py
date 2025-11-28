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


from django.db.models import Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Doctor
from .serializers import DoctorDetailSerializer


class SearchDoctorsAPIView(APIView):
    """
    GET /doctors/search/?q=<query>
    Search doctors by related user name (first/last/username) OR by designation.
    Returns all matching doctors with appointment_count annotated.
    """
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"detail": "Query parameter 'q' is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Annotate each doctor with the number of related appointments
        qs = (
            Doctor.objects
            .annotate(appointment_count=Count("appointments"))
            .filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(designation__icontains=q)
            )
            .distinct()
        )

        if not qs.exists():
            return Response({"detail": f"No doctors found matching '{q}'."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = DoctorDetailSerializer(qs, many=True)
        serialized_data = serializer.data

        # Inject appointment_count (comes from annotation on each model instance)
        results = []
        for doctor_obj, doc_data in zip(qs, serialized_data):
            doc_data = dict(doc_data)  # make mutable copy
            doc_data["appointment_count"] = getattr(doctor_obj, "appointment_count", 0)
            results.append(doc_data)

        return Response({
            "searched_for": q,
            "count": qs.count(),
            "results": results
        }, status=status.HTTP_200_OK)

