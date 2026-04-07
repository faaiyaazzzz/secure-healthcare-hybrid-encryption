import json
from secure_record import decrypt_record
from audit_logger import log_event

ENCRYPTED_FILE = "secure_payload.json"

def decrypt_workflow(role="doctor"):
    with open(ENCRYPTED_FILE, "r") as f:
        encrypted_record = json.load(f)

    decrypted = decrypt_record(encrypted_record, role)

    print("\nDecrypted Record (RBAC enforced):")
    for k, v in decrypted.items():
        print(f"{k}: {v}")

    log_event("DECRYPT", f"Record decrypted for role={role}")

if __name__ == "__main__":
    decrypt_workflow()
