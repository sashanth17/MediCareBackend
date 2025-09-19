from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Doctor.models import Doctor
from django.contrib.auth import get_user_model
from collections import deque
import json
import base64

User = get_user_model()
offer_queue = deque()

@api_view(["POST"])
def AcceptCall(request):
    """
    Receives userId (patient), doctorUserId (doctor), sdp, ice_candidates.
    Stores sdp/ice for doctor, generates token, updates patient with token.
    """
    patient_id = request.data.get("userId")
    doctor_user_id = request.data.get("doctorUserId")
    sdp = request.data.get("sdp")
    ice = request.data.get("ice_candidates")

    if not all([patient_id, doctor_user_id, sdp, ice]):
        return Response({"error": "patientId, doctorUserId, sdp, ice_candidates are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        doctor_user = User.objects.get(id=doctor_user_id)
        patient_user = User.objects.get(id=patient_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    doctor_detail, _ = Doctor.objects.get_or_create(user=doctor_user)
    doctor_detail.sdp = sdp
    doctor_detail.ice_candidates = json.dumps(ice)  # ✅ Store as JSON string
    token = doctor_detail.generate_token()
    doctor_detail.save(update_fields=["sdp", "ice_candidates", "token", "token_created_at"])

    patient_user.offer = token
    patient_user.save(update_fields=["offer"])

    return Response({
        "message": "Doctor connection details updated and token linked to patient",
        "doctorUserId": doctor_user.id,
        "patientUserId": patient_user.id,
        "token": token,
    })


@api_view(["GET"])
def RecieveCall(request):
    """
    Patient polls for doctor’s SDP and ICE using stored token.
    """
    user_id = request.query_params.get("userId")
    if not user_id:
        return Response({"error": "userId is required"}, status=400)

    try:
        patient_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)

    if not patient_user.offer:
        return Response({"message": "No offer available"}, status=200)

    try:
        doctor_detail = Doctor.objects.get(token=patient_user.offer)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor details not found"}, status=404)

    return Response({
        "doctorUserId": doctor_detail.user.id,
        "sdp": doctor_detail.sdp,
        "ice_candidates": json.loads(doctor_detail.ice_candidates),  # ✅ Return parsed JSON
    })


@api_view(["POST"])
def CreateOffer(request):
    """
    Receives userId, sdp, ice_candidates.
    Updates user's SDP and ICE, pushes userId into queue.
    """
    user_id = request.data.get("userId")
    sdp = request.data.get("sdp")
    ice = request.data.get("ice_candidates")

    if not all([user_id, sdp, ice]):
        return Response({"error": "userId, sdp, ice_candidates are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.sdp = sdp
    user.ice_candidates = json.dumps(ice)  # ✅ Store as JSON
    user.save(update_fields=["sdp", "ice_candidates"])

    offer_queue.append(user_id)

    return Response({"message": "User SDP and ICE updated", "userId": user.id})


@api_view(["GET"])
def RecievePatientOffer(request):
    """
    Pops userId from queue and returns their SDP + ICE.
    """
    if not offer_queue:
        return Response({"message": "No offers available"}, status=200)

    user_id = offer_queue.popleft()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    return Response({
        "userId": user.id,
        "sdp": user.sdp,
        "ice_candidates": json.loads(user.ice_candidates),  # ✅ Parse JSON before sending
    })