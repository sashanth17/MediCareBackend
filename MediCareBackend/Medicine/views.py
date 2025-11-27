# views.py

# ============================================
# Imports
# ============================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Medicine, MedicineInstance
from .serializers import MedicineSerializer, MedicineInstanceSerializer


# ============================================
# Medicine List View
# ============================================
class MedicineListView(APIView):
    def get(self, request):
        medicines = Medicine.objects.all()
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)


# ============================================
# Medicine Detail View
# ============================================
class MedicineDetailView(APIView):
    def get(self, request, medicine_id):
        try:
            medicine = Medicine.objects.get(medicine_id=medicine_id)
        except Medicine.DoesNotExist:
            return Response(
                {"error": "Medicine not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        instances = MedicineInstance.objects.filter(medicine=medicine)

        return Response({
            "medicine": MedicineSerializer(medicine).data,
            "instances": MedicineInstanceSerializer(instances, many=True).data
        })


# ============================================
# Search Medicine by Name API
# ============================================
class SearchMedicineByNameAPIView(APIView):
    """
    GET /medicines/search/?q=paracetamol
    Returns first matching medicine (case-insensitive contains) and its instances.
    """
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()

        if not q:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = Medicine.objects.filter(medicine_name__icontains=q)

        if not qs.exists():
            return Response(
                {"detail": f"No medicine found matching '{q}'"},
                status=status.HTTP_404_NOT_FOUND
            )

        medicine = qs.first()
        med_data = MedicineSerializer(medicine).data

        instances = MedicineInstance.objects.filter(medicine=medicine)
        med_data["instances"] = MedicineInstanceSerializer(instances, many=True).data

        return Response(
            {"searched_for": q, "medicine_found": med_data},
            status=status.HTTP_200_OK
        )
