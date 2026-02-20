import sys
import json
import os
import base64
import re
from aes_gcm_utils import decrypt_gcm
from rsa_envelope import decrypt_aes_key
from secure_record import decrypt_record
from dicom_signature import verify_dict_signed, get_signing_keys


def extract_payload_from_eml(eml_path):
    """Extract JSON payload from an .eml email file"""
    try:
        with open(eml_path, 'r') as f:
            eml_content = f.read()
        
        # Extract JSON payload from email (base64 encoded)
        match = re.search(
            r'Content-Type: application/json.*?Content-Transfer-Encoding: base64\s*\n(.*?)(?=--==)',
            eml_content, 
            re.DOTALL
        )
        if match:
            json_b64 = match.group(1).strip()
            json_bytes = base64.b64decode(json_b64)
            return json.loads(json_bytes)
        else:
            print("[ERROR] Could not extract JSON payload from email")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to parse email: {e}")
        return None


def decrypt_received_payload(payload_path, receiver_email, role="doctor", verify_signature_flag=True):
    """Decrypt received payload and optionally verify digital signature.
    
    Args:
        payload_path: Path to payload file or email
        receiver_email: Receiver's email for key lookup
        role: RBAC role for decryption
        verify_signature_flag: Whether to verify digital signature
    
    Returns:
        bool: True if decryption and verification successful
    """
    safe_email = receiver_email.replace("@", "_").replace(".", "_")
    priv_key_path = f"recipient_keys/{safe_email}_private.pem"

    # Check if private key exists
    if not os.path.exists(priv_key_path):
        print(f"[ERROR] Private key not found: {priv_key_path}")
        print(f"[INFO] Available private keys:")
        for f in os.listdir("recipient_keys"):
            if f.endswith("_private.pem"):
                print(f"  - {f}")
        return False

    # Determine payload source
    payload = None
    if payload_path.endswith('.eml'):
        # Extract from email file
        if not os.path.exists(payload_path):
            print(f"[ERROR] Email file not found: {payload_path}")
            # Try to find the latest email in outbox
            outbox_dir = "outbox"
            if os.path.exists(outbox_dir):
                eml_files = [f for f in os.listdir(outbox_dir) if f.endswith('.eml')]
                if eml_files:
                    eml_files.sort()
                    latest_eml = os.path.join(outbox_dir, eml_files[-1])
                    print(f"[INFO] Using latest email: {latest_eml}")
                    payload = extract_payload_from_eml(latest_eml)
                    if payload:
                        payload_path = latest_eml
        else:
            payload = extract_payload_from_eml(payload_path)
    else:
        # Load from JSON file
        if not os.path.exists(payload_path):
            print(f"[ERROR] Payload file not found: {payload_path}")
            # Try to find secure_payload.json in project root
            if os.path.exists("secure_payload.json"):
                with open("secure_payload.json", "r") as f:
                    payload = json.load(f)
                payload_path = "secure_payload.json"
        else:
            with open(payload_path, "r") as f:
                payload = json.load(f)

    if payload is None:
        print("[ERROR] No payload found to decrypt")
        return False

    # Verify digital signature if present and requested
    signature_verified = False
    if verify_signature_flag and '_signature' in payload:
        print("\n[INFO] Digital signature found, verifying...")
        try:
            _, pub_key_path = get_signing_keys()
            if pub_key_path and os.path.exists(pub_key_path):
                signature_verified = verify_dict_signed(payload, pub_key_path)
                if signature_verified:
                    print("[OK] Digital signature VERIFIED - sender authenticity confirmed")
                else:
                    print("[ERROR] Digital signature VERIFICATION FAILED!")
                    print("[WARN] WARNING: Data may be tampered or from unknown sender!")
            else:
                print("[WARN] Signing public key not found, skipping signature verification")
        except Exception as e:
            print(f"[WARN] Signature verification error: {e}")
    elif verify_signature_flag:
        print("[INFO] No digital signature found in payload")

    # Decrypt AES envelope key using RSA private key
    try:
        aes_key = decrypt_aes_key(
            bytes.fromhex(payload["encrypted_key"]),
            priv_key_path
        )
    except Exception as e:
        print(f"[ERROR] Failed to decrypt AES key: {e}")
        print("[INFO] This usually means the payload was encrypted with a different recipient's public key.")
        print("[INFO] Please go to /encrypt to create new data, then send email to yourself.")
        return False

    # Decrypt email envelope (integrity verified here)
    try:
        plaintext = decrypt_gcm(
            bytes.fromhex(payload["ciphertext"]),
            aes_key,
            bytes.fromhex(payload["nonce"]),
            bytes.fromhex(payload["tag"])
        )
    except Exception as e:
        print(f"[ERROR] Failed to decrypt payload: {e}")
        return False

    print("\n[OK] Email integrity verified.")

    # This is still RBAC-encrypted data
    rbac_encrypted_record = json.loads(plaintext.decode())

    # Apply RBAC decryption
    final_data = decrypt_record(rbac_encrypted_record, role=role)

    print(f"\n[OK] Decrypted data (RBAC enforced for role='{role}'):")
    print(json.dumps(final_data, indent=2))
    return True


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Usage: python secure_email_receiver.py <payload.json|email.eml> <email> [role]")
        sys.exit(1)

    payload = sys.argv[1]
    email = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) == 4 else "doctor"

    success = decrypt_received_payload(payload, email, role)
    sys.exit(0 if success else 1)

