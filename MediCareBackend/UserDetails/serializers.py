from rest_framework import serializers
from UserDetails.models import CustomUser

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "phone_number", 
            "date_of_birth", 
            "gender", 
            "blood_group", 
            "offer"
        ]
        extra_kwargs = {
            "username": {"read_only": True},  # user cannot change username
            "email": {"required": False},     # make email optional for updates
        }

    def update(self, instance, validated_data):
        """
        Custom update method to update only provided fields.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','first_name','last_name','email','phone_number','date_of_birth','gender','blood_group']

    def validate_username(self, value):
        # Ignore uniqueness check for the current instance
        user = self.instance
        if user and CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        user = self.instance
        if user and CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['username','first_name','last_name']