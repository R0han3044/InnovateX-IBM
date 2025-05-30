import json
import os
from datetime import datetime
import hashlib

# ----- User Authentication Functions -----

def get_users_db():
    """Load or create the users database"""
    if os.path.exists('users_db.json'):
        with open('users_db.json', 'r') as f:
            return json.load(f)
    else:
        # Create initial admin, doctor, and patient users
        users = {
            "users": [
                {
                    "username": "admin",
                    "password": hash_password("admin123"),
                    "role": "admin",
                    "name": "System Administrator",
                    "email": "admin@healthassist.ai",
                    "created_at": str(datetime.now())
                },
                {
                    "username": "doctor",
                    "password": hash_password("doctor123"),
                    "role": "doctor",
                    "name": "Dr. John Smith",
                    "email": "doctor@healthassist.ai",
                    "created_at": str(datetime.now())
                },
                {
                    "username": "patient",
                    "password": hash_password("patient123"),
                    "role": "patient",
                    "name": "Jane Doe",
                    "email": "patient@healthassist.ai",
                    "created_at": str(datetime.now())
                }
            ]
        }
        save_users_db(users)
        return users

def save_users_db(users):
    """Save the users database"""
    with open('users_db.json', 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash a password for storing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return stored_password == hash_password(provided_password)

def authenticate(username, password):
    """Authenticate a user"""
    users = get_users_db()
    for user in users["users"]:
        if user["username"] == username and verify_password(user["password"], password):
            return user
    return None

def register_user(username, password, role, name, email):
    """Register a new user"""
    users = get_users_db()
    
    # Check if username already exists
    if any(user["username"] == username for user in users["users"]):
        return False, "Username already exists"
    
    # Create new user
    new_user = {
        "username": username,
        "password": hash_password(password),
        "role": role,
        "name": name,
        "email": email,
        "created_at": str(datetime.now())
    }
    
    users["users"].append(new_user)
    save_users_db(users)
    return True, "User registered successfully"

def get_user_data(username):
    """Get user data from the database"""
    users = get_users_db()
    for user in users["users"]:
        if user["username"] == username:
            return user
    return None

def update_user(username, data):
    """Update user data"""
    users = get_users_db()
    for i, user in enumerate(users["users"]):
        if user["username"] == username:
            # Update user data
            for key, value in data.items():
                if key != "username" and key != "password":  # Don't update username
                    users["users"][i][key] = value
            save_users_db(users)
            return True
    return False

# ----- Patient Records Functions -----

def get_patients_db():
    """Load or create the patients database"""
    if os.path.exists('patients_db.json'):
        with open('patients_db.json', 'r') as f:
            return json.load(f)
    else:
        patients = {
            "patients": []
        }
        save_patients_db(patients)
        return patients

def save_patients_db(patients):
    """Save the patients database"""
    with open('patients_db.json', 'w') as f:
        json.dump(patients, f, indent=4)

def add_patient(data):
    """Add a new patient record"""
    patients = get_patients_db()
    
    # Generate patient ID
    patient_id = f"PT{len(patients['patients']) + 1:04d}"
    
    # Create patient record
    patient = {
        "id": patient_id,
        "created_at": str(datetime.now()),
        **data
    }
    
    patients["patients"].append(patient)
    save_patients_db(patients)
    return patient_id

def get_patient(patient_id):
    """Get patient data by ID"""
    patients = get_patients_db()
    for patient in patients["patients"]:
        if patient["id"] == patient_id:
            return patient
    return None

def update_patient(patient_id, data):
    """Update patient data"""
    patients = get_patients_db()
    for i, patient in enumerate(patients["patients"]):
        if patient["id"] == patient_id:
            # Update patient data
            for key, value in data.items():
                if key != "id":  # Don't update ID
                    patients["patients"][i][key] = value
            save_patients_db(patients)
            return True
    return False

def get_all_patients():
    """Get all patients"""
    patients = get_patients_db()
    return patients["patients"]

# ----- Health Records Functions -----

def get_health_records_db():
    """Load or create the health records database"""
    if os.path.exists('health_records_db.json'):
        with open('health_records_db.json', 'r') as f:
            return json.load(f)
    else:
        records = {
            "records": []
        }
        save_health_records_db(records)
        return records

def save_health_records_db(records):
    """Save the health records database"""
    with open('health_records_db.json', 'w') as f:
        json.dump(records, f, indent=4)

def add_health_record(patient_id, record_type, data, created_by):
    """Add a new health record"""
    records = get_health_records_db()
    
    # Generate record ID
    record_id = f"REC{len(records['records']) + 1:04d}"
    
    # Create record
    record = {
        "id": record_id,
        "patient_id": patient_id,
        "type": record_type,
        "data": data,
        "created_by": created_by,
        "created_at": str(datetime.now())
    }
    
    records["records"].append(record)
    save_health_records_db(records)
    return record_id

def get_patient_records(patient_id):
    """Get all health records for a patient"""
    records = get_health_records_db()
    return [record for record in records["records"] if record["patient_id"] == patient_id]