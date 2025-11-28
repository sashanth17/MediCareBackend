from rest_framework import serializers
from .models import Doctor   # ✅ Doctor is in the current app's models
from UserDetails.serializers import UserListSerializer,UserUpdateSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    class Meta:
        model = Doctor
        fields = ['id','user','designation']
class DoctorDetailSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()  # nested serializer

    class Meta:
        model = Doctor
        fields = ['user', 'sdp', 'ice_candidates','designation']

    def update(self, instance, validated_data):
        # pop nested user data
        user_data = validated_data.pop('user', None)

        # update doctor fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # update user if provided
        if user_data:
            user_serializer = UserUpdateSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        return instance