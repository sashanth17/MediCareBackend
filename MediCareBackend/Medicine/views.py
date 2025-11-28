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
    GET /medicines/search/?q=paracetamol[&location=gandhipuram]
    Returns first matching medicine (case-insensitive contains) and its instances.
    If `location` is provided, only instances whose pharmacy.location contains
    the location substring (case-insensitive) are returned.
    """
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        location = (request.query_params.get("location") or "").strip()

        if not q:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # find medicine (same behaviour as your working code)
        qs = Medicine.objects.filter(medicine_name__icontains=q)

        if not qs.exists():
            return Response(
                {"detail": f"No medicine found matching '{q}'"},
                status=status.HTTP_404_NOT_FOUND
            )

        medicine = qs.first()
        med_data = MedicineSerializer(medicine).data

        # get all instances for this medicine
        instances_qs = MedicineInstance.objects.filter(medicine=medicine).select_related('pharmacy')

        # if location provided, filter instances where pharmacy.location contains the location (case-insensitive)
        if location:
            # some pharmacies/instances may have location stored with different casing or formats
            # so we filter in Python to be safe (alternatively you can use __icontains on related field)
            filtered_instances = []
            for inst in instances_qs:
                pharmacy = getattr(inst, "pharmacy", None)
                # try nested pharmacy object first
                if pharmacy:
                    loc_val = getattr(pharmacy, "location", "") or ""
                else:
                    # fallback to instance-level location field if present
                    loc_val = getattr(inst, "location", "") or ""
                if location.lower() in str(loc_val).lower():
                    filtered_instances.append(inst)
            instances = filtered_instances
        else:
            # no location filter -> return all instances
            instances = list(instances_qs)

        # serialize instances (reuse your serializer)
        med_data["instances"] = MedicineInstanceSerializer(instances, many=True).data

        return Response(
            {"searched_for": q, "medicine_found": med_data},
            status=status.HTTP_200_OK
        )
