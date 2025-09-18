from rest_framework import serializers
from .models import MedicineInstance

class MedicineInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineInstance
        fields = '__all__'
