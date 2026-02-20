import sys
from hybrid_encrypt import encrypt_workflow
from hybrid_decrypt import decrypt_workflow
from verify_audit_log import verify_log
from secure_email_sender import send_encrypted_email_to_all

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py encrypt")
        print("  python main.py encrypt-email <email>")
        print("  python main.py encrypt-email-all")
        print("  python main.py decrypt <role>")
        print("  python main.py verify")
        return

    command = sys.argv[1].lower()

    if command == "encrypt":
        encrypt_workflow()

    elif command == "encrypt-email":
        if len(sys.argv) != 3:
            print("Provide receiver email")
            return
        encrypt_workflow(
            send_email=True,
            receiver_email=sys.argv[2]
        )

    elif command == "encrypt-email-all":
        # Encrypt and send to all recipients
        encrypt_workflow(send_email_to_all=True)

    elif command == "decrypt":
        role = sys.argv[2] if len(sys.argv) > 2 else "doctor"
        decrypt_workflow(role)

    elif command == "verify":
        verify_log()

    else:
        print("Unknown command")

if __name__ == "__main__":
    main()

