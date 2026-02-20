import tkinter as tk
import json
import os


def log(msg, output):
    output.insert(tk.END, msg + "\n")
    output.see(tk.END)


def tamper_payload(output):
    if not os.path.exists("secure_payload.json"):
        log("[ERROR] secure_payload.json not found", output)
        return

    with open("secure_payload.json", "r") as f:
        payload = json.load(f)

    # Flip one hex character in ciphertext
    ct = payload["ciphertext"]
    payload["ciphertext"] = ct[:-1] + ("0" if ct[-1] != "0" else "1")

    with open("secure_payload.json", "w") as f:
        json.dump(payload, f, indent=2)

    log("[ATTACK] Payload tampered (ciphertext modified)", output)


def tamper_audit_log(output):
    if not os.path.exists("audit.log"):
        log("[ERROR] audit.log not found", output)
        return

    with open("audit.log", "a") as f:
        f.write("\n[ATTACK] Unauthorized audit log modification\n")

    log("[ATTACK] Audit log tampered (hash chain broken)", output)


def reset_system(output):
    removed_any = False

    for file in ["secure_payload.json", "audit.log"]:
        if os.path.exists(file):
            os.remove(file)
            removed_any = True

    if removed_any:
        log("[RESET] System state reset (payload & audit log removed)", output)
    else:
        log("[RESET] Nothing to reset (system already clean)", output)


def main():
    root = tk.Tk()
    root.title("Tampering Simulation Console (Red Team)")
    root.geometry("700x480")

    tk.Label(
        root,
        text="Tampering Simulation (For Security Testing Only)",
        font=("Arial", 11, "bold"),
        fg="red"
    ).pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    output = tk.Text(
        root,
        height=15,
        bg="black",
        fg="orange",
        font=("Consolas", 10)
    )
    output.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Button(
        btn_frame,
        text="Tamper Secure Payload",
        width=25,
        bg="#aa0000",
        fg="white",
        command=lambda: tamper_payload(output)
    ).grid(row=0, column=0, padx=10, pady=5)

    tk.Button(
        btn_frame,
        text="Tamper Audit Log",
        width=25,
        bg="#aa0000",
        fg="white",
        command=lambda: tamper_audit_log(output)
    ).grid(row=0, column=1, padx=10, pady=5)

    tk.Button(
        btn_frame,
        text="Reset System State",
        width=52,
        bg="#003366",
        fg="white",
        command=lambda: reset_system(output)
    ).grid(row=1, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
