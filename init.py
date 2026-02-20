#!/usr/bin/env python3
"""
Initialization script for Healthcare Crypto System
Generates required RSA keys for encryption/decryption
"""
import os
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

# Directories
KEY_DIR = "keys"
RECIPIENT_KEYS_DIR = "recipient_keys"

# Default recipients with their emails
RECIPIENTS = [
    "chintu01032005@gmail.com",
    "doctor@example.com",
    "test@example.com"
]


def generate_system_keys():
    """Generate system RSA key pair for AES key wrapping"""
    os.makedirs(KEY_DIR, exist_ok=True)
    
    # Check if keys already exist
    if os.path.exists(f"{KEY_DIR}/private.pem") and os.path.exists(f"{KEY_DIR}/public.pem"):
        print(f"[INFO] System keys already exist in {KEY_DIR}")
        return
    
    print("[INFO] Generating system RSA-2048 keys...")
    key = RSA.generate(2048)
    
    with open(f"{KEY_DIR}/private.pem", "wb") as f:
        f.write(key.export_key())
    
    with open(f"{KEY_DIR}/public.pem", "wb") as f:
        f.write(key.publickey().export_key())
    
    print(f"[OK] System keys generated in {KEY_DIR}")


def generate_recipient_keys():
    """Generate RSA key pairs for all recipients"""
    os.makedirs(RECIPIENT_KEYS_DIR, exist_ok=True)
    
    for email in RECIPIENTS:
        safe_email = email.replace("@", "_").replace(".", "_")
        priv_path = f"{RECIPIENT_KEYS_DIR}/{safe_email}_private.pem"
        pub_path = f"{RECIPIENT_KEYS_DIR}/{safe_email}_public.pem"
        
        if os.path.exists(priv_path) and os.path.exists(pub_path):
            print(f"[INFO] Keys already exist for {email}")
            continue
        
        print(f"[INFO] Generating RSA-2048 keys for {email}...")
        key = RSA.generate(2048)
        
        with open(priv_path, "wb") as f:
            f.write(key.export_key())
        
        with open(pub_path, "wb") as f:
            f.write(key.publickey().export_key())
        
        print(f"[OK] Keys generated for {email}")


def initialize_aes_keys():
    """Initialize AES keys storage"""
    os.makedirs(KEY_DIR, exist_ok=True)
    aes_keys_file = f"{KEY_DIR}/aes_keys.json"
    
    if os.path.exists(aes_keys_file):
        print(f"[INFO] AES keys already initialized")
        return
    
    # Create empty AES keys file
    with open(aes_keys_file, "w") as f:
        json.dump([], f)
    
    print(f"[OK] AES keys storage initialized")


def main():
    print("=" * 60)
    print("🔐 Healthcare Crypto System - Initialization")
    print("=" * 60)
    
    generate_system_keys()
    generate_recipient_keys()
    initialize_aes_keys()
    
    print("=" * 60)
    print("[OK] System initialized successfully!")
    print("=" * 60)
    print("\nYou can now run the web interface:")
    print("  python app.py")
    print("\nOr use the CLI:")
    print("  python main.py encrypt")
    print("  python main.py decrypt doctor")


if __name__ == "__main__":
    main()

