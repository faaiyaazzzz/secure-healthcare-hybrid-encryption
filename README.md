# 🔐 Secure Healthcare Crypto System

### **Hybrid RSA–AES Encryption | Role-Based Access Control | Real-Time Audit Monitoring**

A professional, enterprise-grade healthcare data protection platform that implements a hybrid cryptographic model to ensure the confidentiality, integrity, and availability of sensitive medical records.

---

## 🚀 **Overview**

This project demonstrates a production-ready security architecture for healthcare systems. It combines **AES-256-GCM** (Authenticated Encryption) for data confidentiality with **RSA-2048** (Envelope Encryption) for secure key distribution and digital identity management.

The system features a modern, role-based web interface designed for **Doctors, Nurses, Administrators, and Patients**, each with tailored dashboards and cryptographic permissions.

---

## ✨ **Key Features**

### **1. Advanced Cryptography**
- **Hybrid Encryption**: Combines the speed of AES-256 with the secure key exchange of RSA-2048.
- **Envelope Encryption**: AES session keys are encrypted per recipient using their RSA public keys.
- **Authenticated Encryption (GCM)**: Ensures that data has not been tampered with during transit or storage.
- **Medical Image Security**: Specialized DICOM and image encryption/decryption modules.

### **2. Role-Based Access Control (RBAC)**
- **Granular Permissions**: Different roles (Doctor, Nurse, Admin, Patient) have specific access to services.
- **Cryptographic Enforcement**: Access to sensitive data is enforced through per-user RSA key pairs.

### **3. Admin & Security Monitoring**
- **Admin Activity Dashboard**: Real-time, system-wide monitoring of all user logins, cryptographic operations, and security events.
- **Hash-Chained Audit Logging**: Every system action is logged in an immutable, hash-linked chain to prevent log tampering.
- **Integrity Verification**: Built-in tools to verify the integrity of audit logs and detect unauthorized modifications.

### **4. Modern User Experience**
- **Professional Web UI**: A sleek, dark-themed interface built with glassmorphism and responsive design.
- **Role-Specific Dashboards**: Tailored experiences for clinical staff and patients.
- **Security Enhancements**: Interactive password visibility toggles and real-time system health diagnostics.

---

## 🛠️ **Tech Stack**

- **Backend**: Python 3.x, Flask (Web Framework)
- **Cryptography**: `cryptography` library (AES-256-GCM, RSA-2048, SHA-256)
- **Frontend**: HTML5, CSS3 (Modern Grid/Flexbox, Glassmorphism), JavaScript (Vanilla)
- **Data Handling**: JSON-based secure payload storage and DICOM medical image processing.

---

## 🔑 **Default Credentials**

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` |
| **Doctor** | `doctor` | `doctor123` |
| **Nurse** | `nurse` | `nurse123` |
| **Patient** | `patient` | `patient123` |

---

## 📂 **Project Structure**

- `app.py`: Main Flask application and routing logic.
- `audit_logger.py`: Implements hash-chained logging and integrity checks.
- `key_manager.py`: Handles RSA/AES key generation, storage, and rotation.
- `rbac_crypto.py`: Enforces role-based cryptographic access.
- `templates/`: Modern HTML templates for all dashboards and services.
- `uploads/`: Secure storage for encrypted medical images and data payloads.

---

## 🚦 **Getting Started**

1. **Install Dependencies**:
   ```bash
   pip install flask cryptography pillow pydicom
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Portal**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🛡️ **Security Principles**
- **Confidentiality**: Only authorized recipients can decrypt data using their private RSA keys.
- **Integrity**: Any unauthorized change to encrypted data or audit logs is immediately detected.
- **Accountability**: All actions are logged and attributable to a specific user and timestamp.
