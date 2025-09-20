# queue.py
from collections import deque

# Queue for patients waiting for doctor
offer_queue = deque()

# Temporary storage for doctor answers keyed by patient_id
answer_dict = {}