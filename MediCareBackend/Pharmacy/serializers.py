from Pharmacy.models import Pharmacy
from rest_framework import serializers
class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ["pharmacy_id", "pharmacy_name", "location", "contact_no"]