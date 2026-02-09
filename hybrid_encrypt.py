from secure_record import encrypt_record
from secure_email_sender import send_encrypted_email
from audit_logger import log_event

def encrypt_workflow(send_email=False, receiver_email=None):
    record = {
        "patient_id": "P1023",
        "diagnosis": "Hypertension",
        "prescription": "Amlodipine",
        "lab_results": "BP 150/90"
    }

    encrypted_record, key_id = encrypt_record(record)
    log_event("ENCRYPT", f"Encrypted using key {key_id}")

    if send_email and receiver_email:
        send_encrypted_email(receiver_email, encrypted_record)

    print("Healthcare record encrypted with hybrid envelope encryption.")
