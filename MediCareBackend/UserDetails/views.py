from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from UserDetails.models import CustomUser
from UserDetails.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer
)

class UserListCreateView(APIView):
    """
    GET: List all users
    POST: Create a new user
    """

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """
    GET: Retrieve a user by pk
    PUT: Update a user by pk
    """

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
