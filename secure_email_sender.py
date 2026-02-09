import os
import json
import smtplib
from email.message import EmailMessage
from aes_gcm_utils import generate_aes_key, encrypt_gcm
from rsa_envelope import encrypt_aes_key

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_encrypted_email(receiver_email, data: dict):
    sender = os.getenv("SECURE_EMAIL")
    password = os.getenv("SECURE_EMAIL_PASSWORD")

    if not sender or not password:
        print("[INFO] Email credentials missing. Skipping email.")
        return

    safe_email = receiver_email.replace("@", "_").replace(".", "_")
    pub_key_path = f"recipient_keys/{safe_email}_public.pem"

    if not os.path.exists(pub_key_path):
        raise FileNotFoundError("Recipient public key not found")

    aes_key = generate_aes_key()
    ciphertext, nonce, tag = encrypt_gcm(
        json.dumps(data).encode(), aes_key
    )

    encrypted_key = encrypt_aes_key(aes_key, pub_key_path)

    payload = {
        "nonce": nonce.hex(),
        "tag": tag.hex(),
        "ciphertext": ciphertext.hex(),
        "encrypted_key": encrypted_key.hex()
    }

    msg = EmailMessage()
    msg["Subject"] = "Encrypted Healthcare Record"
    msg["From"] = sender
    msg["To"] = receiver_email
    msg.set_content("Encrypted record attached. Requires RSA private key.")

    msg.add_attachment(
        json.dumps(payload).encode(),
        maintype="application",
        subtype="json",
        filename="secure_payload.json"
    )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    print(f"[OK] Encrypted envelope emailed to {receiver_email}")
