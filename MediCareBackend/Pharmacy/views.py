from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Medicine.models import MedicineInstance, Medicine
from Pharmacy.models import Pharmacy
from Medicine.serializers import MedicineInstanceSerializer

class AddMedicineInstanceView(APIView):
    def post(self, request):
       
        medicine_id = request.data.get("medicine_id")
        pharmacy_id = request.data.get("pharmacy_id")
        instance_id = request.data.get("instance_id")

        if not all([medicine_id, pharmacy_id, instance_id]):
            return Response({"error": "medicine_id, pharmacy_id and instance_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            medicine = Medicine.objects.get(pk=medicine_id)
            pharmacy = Pharmacy.objects.get(pk=pharmacy_id)
        except (Medicine.DoesNotExist, Pharmacy.DoesNotExist):
            return Response({"error": "Invalid medicine_id or pharmacy_id."}, status=status.HTTP_404_NOT_FOUND)

        # Create MedicineInstance
        instance = MedicineInstance.objects.create(
            instance_id=instance_id,
            medicine=medicine,
            pharmacy=pharmacy
        )
        serializer = MedicineInstanceSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        if created:
            return JsonResponse({"message": "Medicine added successfully!"})
        else:
            return JsonResponse({"message": "Medicine already exists!"})


class RemoveMedicineInstanceView(APIView):
    def delete(self, request):

        instance_id = request.data.get("instance_id")
        if not instance_id:
            return Response({"error": "instance_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = MedicineInstance.objects.get(pk=instance_id)
            instance.delete()
            return Response({"message": f"Medicine instance {instance_id} removed successfully."}, status=status.HTTP_200_OK)
        except MedicineInstance.DoesNotExist:
            return Response({"error": "Medicine instance not found."}, status=status.HTTP_404_NOT_FOUND)
