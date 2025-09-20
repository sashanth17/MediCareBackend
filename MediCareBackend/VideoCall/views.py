# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import json
from collections import deque

User = get_user_model()

# --- In-memory storage for simple signaling (Not for production with multiple workers) ---
# Queue for patients waiting for a doctor
offer_queue = deque()
# Dictionary to hold a doctor's answer, keyed by the patient's user_id
answer_dict = {}
# --------------------------------------------------------------------------------------


# -------------------- 1. Patient creates an offer --------------------
@api_view(["POST"])
def create_offer(request):
    """
    Patient sends their SDP offer and ICE candidates.
    The offer is added to a queue for a doctor to pick up.
    """
    user_id = request.data.get("user_id")
    sdp = request.data.get("sdp")
    ice_candidates = request.data.get("ice_candidates", [])

    if not all([user_id, sdp]):
        return Response({"error": "user_id and sdp are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the user exists
    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # NOTE: Removed the unnecessary database save. The in-memory queue is sufficient.

    # Add the patient's offer to the queue
    offer_queue.append({
        "user_id": user_id,
        "sdp": sdp,
        "ice_candidates": ice_candidates
    })
    return Response({"status": "queued", "user_id": user_id}, status=status.HTTP_201_CREATED)


# -------------------- 2. Doctor polls for offers and sends answers --------------------
@api_view(["GET", "POST"])
def doctor_poll_view(request):
    """
    GET: Doctor polls this endpoint to get the next patient's offer from the queue.
    POST: Doctor sends back an SDP answer and ICE candidates for a specific patient.
    """
    if request.method == "GET":
        if not offer_queue:
            # No patients are waiting
            return Response({"status": "empty"}, status=status.HTTP_200_OK)

        # Get the next patient from the queue
        patient_offer = offer_queue.popleft()
        return Response(patient_offer, status=status.HTTP_200_OK)

    elif request.method == "POST":
        patient_id = request.data.get("patient_id")
        sdp = request.data.get("sdp")
        ice_candidates = request.data.get("ice_candidates", [])

        if not all([patient_id, sdp]):
            return Response({"error": "patient_id and sdp are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Store the answer in our dictionary, ensuring the key is a string for consistency.
        answer_dict[str(patient_id)] = {
            "sdp": sdp,
            "ice_candidates": ice_candidates
        }
        return Response({"status": "answer stored"}, status=status.HTTP_200_OK)


# -------------------- 3. Patient polls for the answer --------------------
@api_view(["GET"])
def patient_get_answer(request):
    """
    Patient polls this endpoint with their user_id to see if a doctor has
    responded with an answer yet.
    """
    user_id = request.query_params.get("user_id")

    if not user_id:
        return Response({"error": "user_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    # **FIXED LOGIC HERE**
    # Atomically get and remove the answer for the user_id.
    # Using .pop() with a default value of None is clean and safe.
    answer = answer_dict.pop(str(user_id), None)

    if answer:
        # If an answer was found, return it
        return Response(answer, status=status.HTTP_200_OK)
    else:
        # If no answer is ready for this user_id, let them know.
        return Response({"status": "no answer yet"}, status=status.HTTP_200_OK)