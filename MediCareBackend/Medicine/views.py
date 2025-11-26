# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Medicine
from .serializers import MedicineSerializer,MedicineInstance,MedicineInstanceSerializer

class MedicineListView(APIView):
    def get(self, request):
        medicines = Medicine.objects.all()
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)
    
class MedicineDetailView(APIView):
    def get(self, request, medicine_id):
        try:
            medicine = Medicine.objects.get(medicine_id=medicine_id)
        except Medicine.DoesNotExist:
            return Response({"error": "Medicine not found"}, status=status.HTTP_404_NOT_FOUND)

        instances = MedicineInstance.objects.filter(medicine=medicine)

        return Response({
            "medicine": MedicineSerializer(medicine).data,
            "instances": MedicineInstanceSerializer(instances, many=True).data
        })

class MedicineByNameView(APIView):
    def get(self, request, medicine_name):
        try:
            # Match the correct DB field
            medicine = Medicine.objects.get(medicine_name__iexact=medicine_name)
        except Medicine.DoesNotExist:
            return Response({"error": "Medicine not found"}, status=status.HTTP_404_NOT_FOUND)

        instances = MedicineInstance.objects.filter(medicine=medicine)

        return Response({
            "medicine": MedicineSerializer(medicine).data,
            "instances": MedicineInstanceSerializer(instances, many=True).data
        })
