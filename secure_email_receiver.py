import sys
import json
from aes_gcm_utils import decrypt_gcm
from rsa_envelope import decrypt_aes_key
from secure_record import decrypt_record


def decrypt_received_payload(payload_path, receiver_email, role="doctor"):
    safe_email = receiver_email.replace("@", "_").replace(".", "_")
    priv_key_path = f"recipient_keys/{safe_email}_private.pem"

    # Load encrypted email payload
    with open(payload_path, "r") as f:
        payload = json.load(f)

    # Decrypt AES envelope key using RSA private key
    aes_key = decrypt_aes_key(
        bytes.fromhex(payload["encrypted_key"]),
        priv_key_path
    )

    # Decrypt email envelope (integrity verified here)
    plaintext = decrypt_gcm(
        bytes.fromhex(payload["ciphertext"]),
        aes_key,
        bytes.fromhex(payload["nonce"]),
        bytes.fromhex(payload["tag"])
    )

    print("\n[OK] Email integrity verified.")

    # This is still RBAC-encrypted data
    rbac_encrypted_record = json.loads(plaintext.decode())

    # Apply RBAC decryption
    final_data = decrypt_record(rbac_encrypted_record, role=role)

    print(f"\n[OK] Decrypted data (RBAC enforced for role='{role}'):")
    print(json.dumps(final_data, indent=2))


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Usage: python secure_email_receiver.py <payload.json> <email> [role]")
        sys.exit(1)

    payload = sys.argv[1]
    email = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) == 4 else "doctor"

    decrypt_received_payload(payload, email, role)
