from key_manager import get_active_key

ROLE_FIELD_MAP = {
    "doctor": ["patient_id", "diagnosis", "prescription", "lab_results"],
    "nurse": ["patient_id", "prescription", "lab_results"],
    "admin": ["audit_info"],
    "patient": ["patient_id", "diagnosis", "prescription", "lab_results"]
}

def allowed_fields(role):
    if role not in ROLE_FIELD_MAP:
        raise PermissionError("Invalid role")
    return ROLE_FIELD_MAP[role]
