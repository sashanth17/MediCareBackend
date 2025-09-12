from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Doctor.models import Doctor
from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(["POST"])
def AcceptCall(request):
    """
    Receives userId (patient), doctorUserId (doctor), sdp, ice_candidates.
    Stores sdp/ice for doctor, generates token, updates patient with token, returns success.
    """
    patient_id = request.data.get("userId")
    doctor_user_id = request.data.get("doctorUserId")
    sdp = request.data.get("sdp")
    ice = request.data.get("ice_candidates")

    if not all([patient_id, doctor_user_id, sdp, ice]):
        return Response(
            {"error": "patientId, doctorUserId, sdp, ice_candidates are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        doctor_user = User.objects.get(id=doctor_user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Doctor user not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        patient_user = User.objects.get(id=patient_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Patient user not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    doctor_detail, _ = Doctor.objects.get_or_create(user=doctor_user)
    doctor_detail.sdp = sdp
    doctor_detail.ice_candidates = ice
    token = doctor_detail.generate_token()
    doctor_detail.save(
        update_fields=["sdp", "ice_candidates", "token", "token_created_at"]
    )
    patient_user.offer= token
    patient_user.save(update_fields=["offer"])

    return Response(
        {
            "message": "Doctor connection details updated and token linked to patient",
            "doctorUserId": doctor_user.id,
            "patientUserId": patient_user.id,
            "token": token,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def RecieveCall(request):
    """
    Patient requests their offer.
    If user has an offer, fetch the Doctor details linked to that token.
    Return SDP and ICE candidates.
    """
    user_id = request.query_params.get("userId")

    if not user_id:
        return Response({"error": "userId is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        patient_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    if not patient_user.offer:
        return Response({"message": "No offer available for this patient"}, status=status.HTTP_200_OK)
    try:
        doctor_detail = Doctor.objects.get(token=patient_user.offer)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor details not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "doctorUserId": doctor_detail.user.id,
            "sdp": doctor_detail.sdp,
            "ice_candidates": doctor_detail.ice_candidates,
        },
        status=status.HTTP_200_OK,
    )