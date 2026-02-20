🔐 Secure Healthcare Data Protection System

Hybrid RSA–AES Encryption with Secure Email, RBAC & Tamper Detection

📌 Overview

This project implements a production-inspired secure healthcare data protection system using a hybrid cryptographic model.
It demonstrates how sensitive healthcare records can be encrypted, securely shared via email, access-controlled, audited, and protected against tampering.

The system follows real-world security design principles used in enterprise systems (PGP / S-MIME style envelope encryption).

🧠 Core Security Model (Hybrid Encryption)

AES-256-GCM

Encrypts healthcare data

Provides confidentiality and integrity (authenticated encryption)

RSA-2048 (Envelope Encryption)

Encrypts the AES session key per recipient

Enables secure key distribution via email

Digital Identity = RSA Key Pair

Each recipient has a public/private key pair

Email is treated as a transport channel, not a trust mechanism

🔁 Key Lifecycle & Rotation

AES keys:
✔ Automatically generated per encryption (session keys)
✔ Never reused

RSA keys:
✔ Long-term identity keys
✔ Rotated manually (by design, like real secure email systems)

🔐 Features Implemented

Hybrid RSA–AES encryption

Authenticated encryption (AES-GCM)

Per-recipient public-key envelope encryption

Secure email transmission of encrypted payloads

Cryptographic Role-Based Access Control (RBAC)

Doctor / Nurse / Admin

Hash-chained audit logging

Audit log integrity verification

Tamper detection (payload & logs)

Separate Blue Team (normal operations) and Red Team (attack simulation) GUIs

Full system reset for repeatable security testing

📂 Project Structure (Final)
healthcare_crypto_project/
│
├── main.py                     # CLI entry point
├── main_gui.py                 # Blue team GUI (normal operations)
├── tamper_gui.py               # Red team GUI (attack simulation)
│
├── hybrid_encrypt.py           # Encryption workflow
├── hybrid_decrypt.py           # Decryption + RBAC
├── aes_gcm_utils.py            # AES-GCM utilities
├── rsa_utils.py                # RSA key handling
├── rsa_envelope.py             # Envelope encryption (AES key wrapping)
│
├── secure_email_sender.py      # Encrypted email sender
├── secure_email_receiver.py    # Email payload verification & decryption
│
├── recipient_keygen.py         # RSA key generation per recipient
├── rbac_crypto.py              # Cryptographic RBAC enforcement
│
├── audit.log                   # Hash-chained audit log
├── audit_logger.py             # Audit logging
├── verify_audit_log.py         # Audit integrity verification
│
├── secure_payload.json         # Encrypted email payload (generated)
├── recipient_keys/             # RSA keys per recipient
│
└── README.md

▶️ How to Run (CLI)
Encrypt data
python main.py encrypt

Decrypt data (RBAC enforced)
python main.py decrypt

Send encrypted email
python main.py encrypt-email recipient@gmail.com

Verify audit log
python main.py verify

▶️ Email Receiver (Integrity + RBAC)
python secure_email_receiver.py secure_payload.json recipient@gmail.com doctor
python secure_email_receiver.py secure_payload.json recipient@gmail.com nurse
python secure_email_receiver.py secure_payload.json recipient@gmail.com admin


Each role receives only authorized fields, enforced cryptographically.

🖥️ GUIs
🔵 Main GUI (Blue Team)
python main_gui.py


Used for:

Encryption / Decryption

Secure email sending

RBAC verification

Audit verification

🔴 Tampering GUI (Red Team)
python tamper_gui.py


Used for:

Payload tampering (AES-GCM MAC failure)

Audit log tampering (hash chain break)

Full system reset for clean re-tests

🧪 Security Testing & Tamper Detection
Payload Tampering

Modifies encrypted ciphertext

Decryption fails with:

MAC check failed

Audit Log Tampering

Modifies audit log post-event

Verification fails with:

[FAIL] Log tampering detected


These failures prove integrity enforcement, not system errors.

🔁 System Reset (Recommended After Each Demo)

The tampering GUI includes a Reset System State button that removes:

secure_payload.json

audit.log

This ensures repeatable and clean security testing.

🧠 Design Decisions (Why This Is Correct)

Email is treated as untrusted transport

Security relies on cryptography, not trust

AES keys rotate automatically

RSA keys represent identity

No silent key generation or insecure defaults

Attack simulation is separated from normal operations

This mirrors real enterprise security systems.

🎯 Conclusion

This project demonstrates a complete, verifiable, and attack-resilient healthcare data security system.
It goes beyond basic encryption to include secure key exchange, access control, auditing, tamper detection, and adversarial testing, all backed by real cryptographic guarantees.