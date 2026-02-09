import hashlib

def verify_log():
    with open("audit.log", "r") as f:
        lines = f.readlines()

    prev = "0"
    for line in lines:
        parts = line.strip().split("|")
        raw = "|".join(parts[:-1])
        stored_hash = parts[-1]

        if hashlib.sha256(raw.encode()).hexdigest() != stored_hash:
            print("[FAIL] Log tampering detected")

            return

        if parts[-2] != prev:
            print("❌ Hash chain broken")
            return

        prev = stored_hash

    print("[OK] Audit log integrity verified")


if __name__ == "__main__":
    verify_log()
