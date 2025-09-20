from rest_framework import serializers
from .models import Medicine,MedicineInstance
from Pharmacy.serializers import PharmacySerializer

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
class MedicineInstanceSerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer(read_only=True)
    class Meta:
        model = MedicineInstance
        fields = ["instance_id", "pharmacy"]