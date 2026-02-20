import subprocess
import sys
import os
import json

from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from functools import wraps

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

# Role-based access control - define which roles can access which routes
ROLE_PERMISSIONS = {
    'index': ['doctor', 'nurse', 'admin'],
    'encrypt': ['doctor', 'nurse'],
    'decrypt': ['doctor', 'nurse', 'admin'],
    'send_email': ['doctor', 'nurse'],
    'receive_email': ['doctor', 'nurse'],
    'verify_audit': ['admin'],
    'tamper_test': ['admin'],
    'status': ['doctor', 'nurse', 'admin'],
}


def role_required(route_name):
    """Decorator to enforce role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            user_role = session.get('role', '')
            allowed_roles = ROLE_PERMISSIONS.get(route_name, [])
            
            if user_role not in allowed_roles:
                flash(f'Access denied. Your role ({user_role}) does not have permission to access this page.', 'error')
                # Log out the user
                session.clear()
                return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


app = Flask(__name__)
app.secret_key = 'healthcare_crypto_secret_key'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Simple user credentials (can be extended with a database)
USERS = {
    'doctor': {'password': 'doctor123', 'role': 'doctor'},
    'nurse': {'password': 'nurse123', 'role': 'nurse'},
    'admin': {'password': 'admin123', 'role': 'admin'},
}

# Hospital data
HOSPITALS = {
    'city_general': {
        'id': 'city_general',
        'name': 'City General Hospital',
        'address': '123 Healthcare Avenue, Medical District',
        'phone': '+1 (555) 123-4567',
        'email': 'info@citygeneralhospital.com'
    },
    'st_marys': {
        'id': 'st_marys',
        'name': "St. Mary's Medical Center",
        'address': '456 Hope Street, Downtown',
        'phone': '+1 (555) 987-6543',
        'email': 'contact@stmarysmedical.com'
    },
    'university_hospital': {
        'id': 'university_hospital',
        'name': 'University Hospital',
        'address': '789 Academic Way, College Town',
        'phone': '+1 (555) 456-7890',
        'email': 'admissions@universityhospital.edu'
    }
}

# Patient database (file-based)
PATIENTS_FILE = os.path.join(PROJECT_DIR, 'patients.json')


def load_email_config():
    """Load email configuration from config file"""
    config_path = os.path.join(PROJECT_DIR, 'email_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def send_smtp_email(to_email, subject, body):
    """Send email using SMTP"""
    config = load_email_config()
    smtp_email = config.get('email', 'faiyazmansuri303@gmail.com')
    smtp_password = config.get('password', 'ycvullhpceyddwkv')
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


def load_patients():
    """Load patients from JSON file"""
    if os.path.exists(PATIENTS_FILE):
        with open(PATIENTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_patients(patients):
    """Save patients to JSON file"""
    with open(PATIENTS_FILE, 'w') as f:
        json.dump(patients, f, indent=2)


def initialize_system():
    """Run initialization if keys don't exist"""
    keys_dir = os.path.join(PROJECT_DIR, 'keys')
    if not os.path.exists(keys_dir) or not os.path.exists(
            os.path.join(keys_dir, 'public.pem')):
        print("[INFO] Running system initialization...")
        try:
            subprocess.run(
                [sys.executable, 'init.py'],
                cwd=PROJECT_DIR,
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"[WARN] Initialization warning: {e}")


# Initialize system on startup
initialize_system()


def run_python_script(script_name, args=None):
    """Run a Python script and return output"""
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)

    # Pass environment variables to subprocess
    env = os.environ.copy()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
            timeout=30,
            env=env
        )
        return result.stdout + result.stderr, result.returncode
    except Exception as e:
        return str(e), 1


@app.route('/')
@role_required('index')
def index():
    """Home/Dashboard page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with Sign In, Sign Up, and Forgot Password"""
    if request.method == 'POST':
        action = request.form.get('action', 'signin')
        
        # Handle Sign Up
        if action == 'signup':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip().lower()
            password = request.form.get('password', '')
            role = request.form.get('role', '')
            
            if not name or not username or not password:
                flash('Please fill in all required fields.', 'error')
                return redirect(url_for('login'))
            
            # For patients, save to patients.json
            if role == 'patient':
                patients = load_patients()
                if username in patients:
                    flash('Patient ID already registered. Please sign in.', 'error')
                    return redirect(url_for('login'))
                patients[username] = {
                    'name': name,
                    'email': email,
                    'password': password,
                }
                save_patients(patients)
                flash('Account created successfully! Please sign in.', 'success')
                return redirect(url_for('login'))
            else:
                # For staff (doctor, nurse, admin)
                if username in USERS:
                    flash('Username already exists. Please sign in.', 'error')
                    return redirect(url_for('login'))
                USERS[username] = {'password': password, 'role': role}
                flash(f'Account created for {role}! Please sign in.', 'success')
                return redirect(url_for('login'))
        
        # Handle Forgot Password
        elif action == 'forgot':
            username = request.form.get('username', '').strip().lower()
            email = request.form.get('email', '').strip()
            
            # Check if user exists
            patients = load_patients()
            if username in patients:
                if patients[username].get('email') == email:
                    # Send actual password reset email
                    reset_link = f"http://localhost:8000/reset-password?user={username}"
                    email_subject = "Password Reset - Healthcare Crypto System"
                    email_body = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #00d4ff;">Password Reset Request</h2>
                        <p>Hello {patients[username]['name']},</p>
                        <p>We received a request to reset your password. Click the link below to reset your password:</p>
                        <p><a href="{reset_link}" style="background: #00d4ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                        <p>Or copy this link: {reset_link}</p>
                        <p>If you didn't request this, please ignore this email.</p>
                        <p style="color: #666; font-size: 12px; margin-top: 20px;">This link will expire in 24 hours.</p>
                    </body>
                    </html>
                    """
                    success, message = send_smtp_email(email, email_subject, email_body)
                    if success:
                        flash(f'Password reset link sent to {email}', 'success')
                    else:
                        flash(f'Error sending email: {message}', 'error')
                else:
                    flash('Email does not match our records.', 'error')
            elif username in USERS:
                # For staff users, send reset email
                staff_email = f"{username}@healthcrypto.com"
                reset_link = f"http://localhost:8000/reset-password?user={username}"
                email_subject = "Password Reset - Healthcare Crypto System"
                email_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #00d4ff;">Password Reset Request</h2>
                    <p>Hello {username},</p>
                    <p>We received a request to reset your password. Click the link below to reset your password:</p>
                    <p><a href="{reset_link}" style="background: #00d4ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                    <p>Or copy this link: {reset_link}</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">This link will expire in 24 hours.</p>
                </body>
                </html>
                """
                success, message = send_smtp_email(staff_email, email_subject, email_body)
                if success:
                    flash(f'Password reset link sent to {staff_email}', 'success')
                else:
                    flash(f'Error sending email: {message}', 'error')
            else:
                flash('User not found. Please check your details.', 'error')
            return redirect(url_for('login'))
        
        # Handle Sign In (original logic)
        else:
            username = request.form.get('username', '').lower()
            password = request.form.get('password', '')
            role = request.form.get('role', '')

            # Check if it's a patient login
            if role == 'patient':
                patients = load_patients()
                if username in patients and patients[username]['password'] == password:
                    session['patient_logged_in'] = True
                    session['patient_id'] = username.upper()
                    session['patient_name'] = patients[username]['name']
                    session['patient_email'] = patients[username].get('email', '')
                    flash(f'Welcome, {patients[username]["name"]}!', 'success')
                    return redirect(url_for('patient_dashboard'))
                else:
                    flash('Invalid Patient ID or password.', 'error')
                    return redirect(url_for('login'))
            
            # Staff login (doctor, nurse, admin)
            if username in USERS and USERS[username]['password'] == password:
                session['user'] = username
                session['role'] = role if role else USERS[username]['role']
                session['logged_in'] = True
                flash(f'Welcome back, {username}! Logged in as {session["role"]}', 'success')
                
                # Redirect admin to audit page
                if session['role'] == 'admin':
                    return redirect(url_for('verify_audit'))
                # Redirect doctor/nurse to hospital selection
                elif session['role'] in ['doctor', 'nurse']:
                    return redirect(url_for('select_hospital'))
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password. Please try again.', 'error')
                return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/select-hospital', methods=['GET', 'POST'])
def select_hospital():
    """Hospital selection page for doctors and nurses"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if session.get('role') not in ['doctor', 'nurse']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        hospital_id = request.form.get('hospital_id')
        if hospital_id and hospital_id in HOSPITALS:
            session['hospital'] = HOSPITALS[hospital_id]
            flash(f"Connected to {HOSPITALS[hospital_id]['name']}", 'success')
            return redirect(url_for('index'))
        else:
            flash('Please select a valid hospital.', 'error')
    
    return render_template('hospital_select.html', hospitals=HOSPITALS)


@app.route('/patient-login', methods=['GET', 'POST'])
def patient_login():
    """Patient login and signup page"""
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'signup':
            # Handle patient signup
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            patient_id = request.form.get('patient_id', '').strip().upper()
            password = request.form.get('password', '')
            
            if not name or not patient_id or not password:
                flash('Please fill in all fields', 'error')
                return redirect(url_for('patient_login'))
            
            # Load existing patients
            patients = load_patients()
            
            # Check if patient_id already exists
            if patient_id in patients:
                flash('Patient ID already registered. Please login.', 'error')
                return redirect(url_for('patient_login'))
            
            # Register new patient
            patients[patient_id] = {
                'name': name,
                'email': email,
                'password': password,  # In production, hash this!
                'registered_at': str(os.path.getmtime(__file__)) if os.path.exists(PATIENTS_FILE) else '0'
            }
            save_patients(patients)
            
            flash('Registration successful! Please login with your Patient ID.', 'success')
            return redirect(url_for('patient_login'))
        
        elif action == 'login':
            # Handle patient login
            patient_id = request.form.get('patient_id', '').strip().upper()
            password = request.form.get('password', '')
            
            # Load patients and validate
            patients = load_patients()
            
            if patient_id in patients and patients[patient_id]['password'] == password:
                # Store patient info in session
                session['patient_logged_in'] = True
                session['patient_id'] = patient_id
                session['patient_name'] = patients[patient_id]['name']
                session['patient_email'] = patients[patient_id].get('email', '')
                
                flash(f'Welcome, {patients[patient_id]["name"]}!', 'success')
                return redirect(url_for('patient_dashboard'))
            else:
                flash('Invalid Patient ID or password.', 'error')
                return redirect(url_for('patient_login'))
    
    return render_template('patient_login.html')


@app.route('/patient-dashboard')
def patient_dashboard():
    """Patient dashboard - view their reports"""
    if not session.get('patient_logged_in'):
        return redirect(url_for('patient_login'))
    
    patient_id = session.get('patient_id', '')
    patient_name = session.get('patient_name', 'Patient')
    
    # Load encrypted record and try to decrypt for this patient
    encrypted_file = os.path.join(PROJECT_DIR, 'encrypted_record.json')
    records = []
    
    if os.path.exists(encrypted_file):
        try:
            with open(encrypted_file, 'r') as f:
                encrypted_record = json.load(f)
            
            # Try to decrypt with active key
            from secure_record import decrypt_record
            from key_manager import get_active_key
            
            key, key_id = get_active_key()
            
            # For patients, try to decrypt with patient role (limited access)
            # Or decrypt all fields and filter
            decrypted = decrypt_record(encrypted_record, role='patient')
            
            # Check if this record belongs to this patient
            if decrypted.get('patient_id') == patient_id:
                records.append(decrypted)
            elif 'patient_id' in decrypted:
                # Show any record that exists (for demo purposes)
                records.append(decrypted)
                
        except Exception as e:
            flash(f'Could not load records: {str(e)}', 'error')
    
    return render_template('patient_dashboard.html', 
                         patient_id=patient_id, 
                         patient_name=patient_name,
                         records=records)


@app.route('/patient-logout')
def patient_logout():
    """Patient logout"""
    session.pop('patient_logged_in', None)
    session.pop('patient_id', None)
    session.pop('patient_name', None)
    session.pop('patient_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('patient_login'))


@app.route('/patient-contact')
def patient_contact():
    """Patient contact information page"""
    if not session.get('patient_logged_in'):
        return redirect(url_for('patient_login'))
    
    patient_id = session.get('patient_id', '')
    patient_name = session.get('patient_name', 'Patient')
    
    # Hospital and doctor contact information
    hospital_info = {
        'name': 'City General Hospital',
        'address': '123 Healthcare Avenue, Medical District',
        'phone': '+1 (555) 123-4567',
        'emergency': '+1 (555) 911-HELP',
        'email': 'info@citygeneralhospital.com',
        'hours': '24/7 Emergency Services'
    }
    
    doctors = [
        {
            'name': 'Dr. Sarah Johnson',
            'specialty': 'General Medicine',
            'phone': '+1 (555) 234-5678',
            'email': 'dr.johnson@citygeneralhospital.com',
            'availability': 'Mon-Fri: 9AM-5PM'
        },
        {
            'name': 'Dr. Michael Chen',
            'specialty': 'Cardiology',
            'phone': '+1 (555) 345-6789',
            'email': 'dr.chen@citygeneralhospital.com',
            'availability': 'Mon-Thu: 10AM-4PM'
        },
        {
            'name': 'Dr. Emily Williams',
            'specialty': 'Pediatrics',
            'phone': '+1 (555) 456-7890',
            'email': 'dr.williams@citygeneralhospital.com',
            'availability': 'Tue-Fri: 8AM-3PM'
        }
    ]
    
    return render_template('patient_contact.html',
                         patient_id=patient_id,
                         patient_name=patient_name,
                         hospital_info=hospital_info,
                         doctors=doctors)


@app.route('/profile')
def profile():
    """User profile page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_data = {
        'username': session.get('user', 'User'),
        'role': session.get('role', 'Unknown'),
        'hospital': session.get('hospital', {}),
        'email': f"{session.get('user', 'user')}@healthcrypto.com"
    }
    return render_template('profile.html', user=user_data)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """User settings page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings'))
    
    user_data = {
        'username': session.get('user', 'User'),
        'role': session.get('role', 'Unknown'),
    }
    return render_template('settings.html', user=user_data)


@app.route('/security')
def security():
    """Security settings page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_data = {
        'username': session.get('user', 'User'),
        'role': session.get('role', 'Unknown'),
    }
    return render_template('security.html', user=user_data)


@app.route('/activity')
def activity():
    """Activity log page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Sample activity data
    activities = [
        {'action': 'Login', 'time': 'Today, 10:30 AM', 'status': 'Success'},
        {'action': 'Encrypt Data', 'time': 'Today, 10:15 AM', 'status': 'Success'},
        {'action': 'Send Email', 'time': 'Yesterday, 3:45 PM', 'status': 'Success'},
        {'action': 'View Audit Log', 'time': 'Yesterday, 2:30 PM', 'status': 'Success'},
    ]
    
    user_data = {
        'username': session.get('user', 'User'),
        'role': session.get('role', 'Unknown'),
    }
    return render_template('activity.html', user=user_data, activities=activities)


@app.route('/help')
def help_page():
    """Help/Documentation page"""
    return render_template('help.html')


@app.route('/contact-support', methods=['GET', 'POST'])
def contact_support():
    """Contact support page"""
    # Allow access without login for support requests
    user_data = {}
    if session.get('logged_in'):
        user_data = {
            'username': session.get('user', 'User'),
            'role': session.get('role', 'Unknown'),
        }
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not subject or not message:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('contact_support'))
        
        # Send email to support team
        config = load_email_config()
        support_email = config.get('email', 'faiyazmansuri303@gmail.com')
        
        # Email to support team
        email_subject = f"Support Request: {subject}"
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563eb;">New Support Request</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Name:</strong></td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Email:</strong></td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{email}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;"><strong>Subject:</strong></td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{subject}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #e2e8f0; vertical-align: top;"><strong>Message:</strong></td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{message}</td>
                </tr>
            </table>
            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                This email was sent from the Healthcare Crypto System Contact Support form.
            </p>
        </body>
        </html>
        """
        
        # Send to support team
        success, result = send_smtp_email(support_email, email_subject, email_body)
        
        if success:
            # Also send confirmation to user
            confirmation_subject = "We received your support request"
            confirmation_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2563eb;">Thank you for contacting us!</h2>
                <p>Hello {name},</p>
                <p>We have received your support request regarding: <strong>{subject}</strong></p>
                <p>Our support team will review your message and get back to you within 24-48 hours.</p>
                <p>Here's a copy of your message:</p>
                <blockquote style="background: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 15px 0;">
                    {message}
                </blockquote>
                <p>Best regards,<br>The Healthcare Crypto Support Team</p>
            </body>
            </html>
            """
            send_smtp_email(email, confirmation_subject, confirmation_body)
            flash('Your message has been sent! Check your email for confirmation.', 'success')
        else:
            flash(f'Error sending message: {result}', 'error')
        
        return redirect(url_for('contact_support'))
    
    return render_template('contact_support.html', user=user_data)


@app.route('/logout')
def logout():
    """Logout and clear session"""
    username = session.get('user', 'User')
    session.clear()
    flash(f'You have been logged out, {username}.', 'success')
    return redirect(url_for('login'))


@app.route('/encrypt', methods=['GET', 'POST'])
@role_required('encrypt')
def encrypt():
    """Encryption page"""
    if request.method == 'POST':
        output, code = run_python_script('main.py', ['encrypt'])
        flash(f'Encryption Output:\n{output}',
              'success' if code == 0 else 'error')
        return redirect(url_for('encrypt'))
    return render_template('encrypt.html')


@app.route('/decrypt', methods=['GET', 'POST'])
@role_required('decrypt')
def decrypt():
    """Decryption page"""
    if request.method == 'POST':
        role = request.form.get('role', 'doctor')
        output, code = run_python_script('main.py', ['decrypt', role])
        flash(f'Decryption Output (Role: {role}):\n{output}',
              'success' if code == 0 else 'error')
        return redirect(url_for('decrypt'))
    return render_template('decrypt.html')


@app.route('/send-email', methods=['GET', 'POST'])
@role_required('send_email')
def send_email():
    """Send secure email page"""
    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'send_all':
            output, code = run_python_script(
                'main.py', ['encrypt-email-all'])
        elif action == 'send_single':
            email = request.form.get('email', '')
            if not email:
                flash('Please enter a recipient email', 'error')
                return redirect(url_for('send_email'))
            output, code = run_python_script(
                'main.py', ['encrypt-email', email])
        else:
            email = request.form.get('email', '')
            if not email:
                flash('Please enter a recipient email', 'error')
                return redirect(url_for('send_email'))
            output, code = run_python_script(
                'main.py', ['encrypt-email', email])

        flash(f'Email Send Output:\n{output}',
              'success' if code == 0 else 'error')
        return redirect(url_for('send_email'))
    return render_template('email.html')


@app.route('/receive-email', methods=['GET', 'POST'])
@role_required('receive_email')
def receive_email():
    """Receive and verify email page"""
    if request.method == 'POST':
        email = request.form.get('email', '')
        role = request.form.get('role', 'doctor')

        if not email:
            flash('Please enter the sender email', 'error')
            return redirect(url_for('receive_email'))

        output, code = run_python_script(
            'secure_email_receiver.py',
            ['secure_payload.json', email, role])
        flash(f'Receive Email Output (Role: {role}):\n{output}',
              'success' if code == 0 else 'error')
        return redirect(url_for('receive_email'))
    return render_template('receive_email.html')


@app.route('/verify-audit', methods=['GET', 'POST'])
@role_required('verify_audit')
def verify_audit():
    """Verify audit log page"""
    if request.method == 'POST':
        output, code = run_python_script('main.py', ['verify'])
        flash(f'Audit Verification Output:\n{output}',
              'success' if code == 0 else 'error')
        return redirect(url_for('verify_audit'))
    return render_template('audit.html')


@app.route('/tamper-test', methods=['GET', 'POST'])
@role_required('tamper_test')
def tamper_test():
    """Tamper testing page (Red Team)"""
    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'tamper_payload':
            output, code = run_python_script(
                'tamper_gui.py', ['tamper-payload'])
        elif action == 'tamper_audit':
            output, code = run_python_script(
                'tamper_gui.py', ['tamper-audit'])
        elif action == 'reset':
            output, code = run_python_script('tamper_gui.py', ['reset'])
        else:
            output, code = "Unknown action", 1

        flash(f'Tamper Test Output:\n{output}',
              'success' if code == 0 else 'error')
        return redirect(url_for('tamper_test'))
    return render_template('tamper.html')



@app.route('/status')
@role_required('status')
def status():
    """System status page"""
    status_info = {}

    keys_dir = os.path.join(PROJECT_DIR, 'keys')
    recipient_keys_dir = os.path.join(PROJECT_DIR, 'recipient_keys')

    status_info['keys_exist'] = os.path.exists(keys_dir) and os.path.exists(
        os.path.join(keys_dir, 'public.pem'))
    status_info['recipient_keys_exist'] = os.path.exists(recipient_keys_dir)
    status_info['payload_exists'] = os.path.exists(
        os.path.join(PROJECT_DIR, 'secure_payload.json'))
    status_info['audit_exists'] = os.path.exists(
        os.path.join(PROJECT_DIR, 'audit.log'))

    return render_template('status.html', status=status_info)


# Lab Results Data Storage
LAB_RESULTS_FILE = os.path.join(PROJECT_DIR, 'lab_results.json')


def load_lab_results():
    """Load lab results from JSON file"""
    if os.path.exists(LAB_RESULTS_FILE):
        with open(LAB_RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_lab_results(results):
    """Save lab results to JSON file"""
    with open(LAB_RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)


@app.route('/lab-results', methods=['GET', 'POST'])
@role_required('index')
def lab_results():
    """Lab Results page for doctors"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Only doctors can access this page
    if session.get('role') not in ['doctor', 'nurse', 'admin']:
        flash('Access denied. Only medical staff can access lab results.', 'error')
        return redirect(url_for('index'))
    
    # Handle new lab result submission
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        patient_name = request.form.get('patient_name', '').strip()
        test_type = request.form.get('test_type', '').strip()
        results = request.form.get('results', '').strip()
        status = request.form.get('status', 'Pending').strip()
        
        if patient_id and patient_name and test_type and results:
            lab_data = load_lab_results()
            
            import datetime
            new_result = {
                'id': len(lab_data) + 1,
                'patient_id': patient_id.upper(),
                'patient_name': patient_name,
                'test_type': test_type,
                'results': results,
                'status': status,
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'hospital': session.get('hospital', {}).get('name', 'Unknown'),
                'doctor': session.get('user', 'Unknown')
            }
            lab_data.append(new_result)
            save_lab_results(lab_data)
            flash('Lab result added successfully!', 'success')
        else:
            flash('Please fill in all required fields.', 'error')
        
        return redirect(url_for('lab_results'))
    
    # Get filter parameters
    patient_id_filter = request.args.get('patient_id', '').strip()
    test_type_filter = request.args.get('test_type', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    # Load and filter lab results
    lab_data = load_lab_results()
    
    # Filter results
    filtered_results = lab_data
    if patient_id_filter:
        filtered_results = [r for r in filtered_results if patient_id_filter.upper() in r.get('patient_id', '')]
    if test_type_filter:
        filtered_results = [r for r in filtered_results if r.get('test_type') == test_type_filter]
    if status_filter:
        filtered_results = [r for r in filtered_results if r.get('status') == status_filter]
    
    # Sort by date (newest first)
    filtered_results.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('lab_results.html', lab_results=filtered_results)


@app.route('/download-lab-report/<int:result_id>')
@role_required('index')
def download_lab_report(result_id):
    """Download lab report as text file"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    lab_data = load_lab_results()
    result = next((r for r in lab_data if r.get('id') == result_id), None)
    
    if not result:
        flash('Lab result not found', 'error')
        return redirect(url_for('lab_results'))
    
    # Create text content for the report
    report_content = f"""
================================================================================
                    LABORATORY TEST REPORT
================================================================================

Report ID: LR-{result_id:06d}
Date: {result.get('date', 'N/A')}

--------------------------------------------------------------------------------
                        PATIENT INFORMATION
--------------------------------------------------------------------------------

Patient ID:     {result.get('patient_id', 'N/A')}
Patient Name:   {result.get('patient_name', 'N/A')}
Hospital:       {result.get('hospital', 'N/A')}
Physician:      {result.get('doctor', 'N/A')}

--------------------------------------------------------------------------------
                        TEST INFORMATION
--------------------------------------------------------------------------------

Test Type:      {result.get('test_type', 'N/A')}
Status:         {result.get('status', 'N/A')}

--------------------------------------------------------------------------------
                        TEST RESULTS
--------------------------------------------------------------------------------

{result.get('results', 'N/A')}

================================================================================
This is a computer-generated document.
Healthcare Crypto System - Secure Healthcare Reporting
================================================================================
"""
    
    # Create response with the report content
    response = make_response(report_content)
    response.headers['Content-Disposition'] = f'attachment; filename=lab_report_{result_id}.txt'
    response.headers['Content-Type'] = 'text/plain'
    
    return response





# Chat messages storage
CHAT_FILE = os.path.join(PROJECT_DIR, 'chat_messages.json')


def load_chat_messages():
    """Load chat messages from file"""
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, 'r') as f:
            return json.load(f)
    return []


def save_chat_messages(messages):
    """Save chat messages to file"""
    with open(CHAT_FILE, 'w') as f:
        json.dump(messages, f, indent=2)


@app.route('/live-chat')
def live_chat():
    """Live chat support page"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_data = {
        'username': session.get('user', 'User'),
        'role': session.get('role', 'Unknown'),
    }
    messages = load_chat_messages()
    return render_template('chat.html', user=user_data, messages=messages)


# Auto-response from support team
def get_auto_response(user_message):
    """Generate auto-responses for support queries"""
    user_message = user_message.lower()
    
    # Common responses based on keywords
    if any(word in user_message for word in ['encrypt', 'encryption']):
        return "🔒 For encryption help: Go to the Encrypt page, select your data file, and click 'Encrypt'. Use a strong key for better security. Need more help?"
    elif any(word in user_message for word in ['decrypt', 'decryption']):
        return "🔓 For decryption: Visit the Decrypt page, enter your role (doctor/nurse), and provide the correct decryption key. Contact admin if you need key reset."
    elif any(word in user_message for word in ['password', 'reset', 'forgot']):
        return "🔑 For password reset: Go to login page, click 'Forgot Password', enter your username/email, and check your inbox for reset link."
    elif any(word in user_message for word in ['email', 'send', 'receive']):
        return "📧 For secure emails: Use the Send Email feature to encrypt messages. Recipients need their public key registered to receive encrypted emails."
    elif any(word in user_message for word in ['audit', 'log', 'verify']):
        return "📋 Audit logs track all system activities. Admins can verify integrity using the Verify Audit page. Logs cannot be tampered with!"
    elif any(word in user_message for word in ['key', 'keys']):
        return "🔑 Keys are managed by the system. If you need a new key, contact admin. Never share your private keys with anyone."
    elif any(word in user_message for word in ['dicom', 'medical', 'image']):
        return "🏥 DICOM files are medical images. Use the DICOM handler to sign and verify medical images for authenticity."
    elif any(word in user_message for word in ['help', 'help me', 'support']):
        return "👋 Hi! I'm the Healthcare Crypto Support Bot. I can help with: encryption, decryption, passwords, emails, keys, and audit logs. What do you need?"
    elif any(word in user_message for word in ['thank', 'thanks']):
        return "😊 You're welcome! Let me know if you need anything else. Stay secure!"
    elif any(word in user_message for word in ['hi', 'hello', 'hey']):
        return "👋 Hello! Welcome to Healthcare Crypto Support. How can I assist you today?"
    else:
        return "📝 I've received your message. Our support team will get back to you shortly. For urgent issues, call +1 (555) 911-HELP. Is there something specific I can help with?"


@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    """API to send a chat message"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Empty message'}), 400
    
    messages = load_chat_messages()
    
    import datetime
    new_message = {
        'id': len(messages) + 1,
        'user': session.get('user', 'User'),
        'role': session.get('role', 'Unknown'),
        'message': message,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_support': False
    }
    messages.append(new_message)
    
    # Generate auto-response from support bot
    auto_response = {
        'id': len(messages) + 1,
        'user': 'Support Bot',
        'role': 'support',
        'message': get_auto_response(message),
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_support': True
    }
    messages.append(auto_response)
    
    save_chat_messages(messages)
    
    return jsonify({'success': True, 'message': new_message})


@app.route('/api/chat/messages')
def chat_messages():
    """API to get chat messages"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    messages = load_chat_messages()
    return jsonify(messages)


@app.route('/api/chat/clear', methods=['POST'])
def chat_clear():
    """API to clear chat messages (admin only)"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    
    save_chat_messages([])
    return jsonify({'success': True})


# File upload configuration
UPLOAD_FOLDER = os.path.join(PROJECT_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'dcm', 'xray', 'bmp', 'webp'}

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/chat/upload', methods=['POST'])
def chat_upload():
    """API to upload files (images, X-rays, medical documents)"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Not logged in'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        import datetime
        import uuid
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Determine file type
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        file_type = 'image' if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'] else 'document'
        
        # Create message with file info
        messages = load_chat_messages()
        
        new_message = {
            'id': len(messages) + 1,
            'user': session.get('user', 'User'),
            'role': session.get('role', 'Unknown'),
            'message': f'📎 Uploaded {file_type}: {file.filename}',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_support': False,
            'file': {
                'name': file.filename,
                'url': f'/uploads/{filename}',
                'type': file_type,
                'size': file_size
            }
        }
        messages.append(new_message)
        
        # Auto-response about the file
        if file_type == 'image':
            auto_response = {
                'id': len(messages) + 1,
                'user': 'Support Bot',
                'role': 'support',
                'message': f'📥 Thank you for uploading {file.filename}! Our medical team will review this image shortly. Is there anything specific you\'d like to know about this file?',
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_support': True
            }
        else:
            auto_response = {
                'id': len(messages) + 1,
                'user': 'Support Bot',
                'role': 'support',
                'message': f'📄 Thank you for uploading {file.filename}! We\'ve received your document. Our team will analyze it and get back to you shortly.',
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_support': True
            }
        
        messages.append(auto_response)
        save_chat_messages(messages)
        
        return jsonify({'success': True, 'file': new_message['file']})
    
    return jsonify({'error': 'File type not allowed'}), 400


# Serve uploaded files
@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return make_response.send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Secure Healthcare Crypto System - Web Interface")
    print("=" * 60)
    print("Starting Flask server at http://localhost:8000")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    app.run(debug=True, port=8000, host='0.0.0.0')
