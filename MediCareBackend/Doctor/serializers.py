# serializers.py
from rest_framework import serializers
from .models import Doctor
from UserDetails.serializers import UserListSerializer, UserUpdateSerializer

class DoctorSerializer(serializers.ModelSerializer):
    # for list endpoints: show basic user info
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'designation']


class DoctorDetailSerializer(serializers.ModelSerializer):
    # nested user serializer for read (and for write if you want nested updates)
    user = UserListSerializer(read_only=True)
    # include appointment_count when annotated in the view
    appointment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Doctor
        # list the explicit fields you want returned
        fields = [
            'id', 'user',  'designation',
            'appointment_count'
        ]
