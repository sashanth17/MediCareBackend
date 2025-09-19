from rest_framework import serializers
from .models import Medicine,MedicineInstance

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
class MedicineInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineInstance
        fields = '__all__'