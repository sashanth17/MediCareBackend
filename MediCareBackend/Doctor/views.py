from rest_framework.views  import APIView
from .models import Doctor
from .serializers import DoctorSerializer,DoctorDetailSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
class ListDoctorView(APIView):
    def get(self,request):
        doctors=Doctor.objects.all()
        serializer=DoctorSerializer(doctors,many=True)
        return Response(serializer.data)

class DoctorDetailView(APIView):
    """
    Retrieve or update the doctor profile
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