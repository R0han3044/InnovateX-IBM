import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import hashlib
import json
import os
from datetime import datetime, timedelta
from emergency_system import show_emergency_page
from health_buddy import show_health_buddy_page, get_user_buddy
from notification_system import show_notifications, create_scheduled_health_notifications, show_notification_center
from wellness_score import show_wellness_score_page
from db_utils import (
    get_users_db, save_users_db, hash_password, verify_password, authenticate,
    register_user, get_user_data, update_user, get_patients_db, save_patients_db,
    add_patient, get_patient, update_patient, get_all_patients, get_health_records_db,
    save_health_records_db, add_health_record, get_patient_records
)

# Set page configuration
st.set_page_config(
    page_title="HealthAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# ----- Medications Tracking Functions -----

def get_medications_db():
    """Load or create the medications database"""
    if os.path.exists('medications_db.json'):
        with open('medications_db.json', 'r') as f:
            return json.load(f)
    else:
        medications = {
            "medications": []
        }
        save_medications_db(medications)
        return medications

def save_medications_db(medications):
    """Save the medications database"""
    with open('medications_db.json', 'w') as f:
        json.dump(medications, f, indent=4)

def add_medication(patient_id, data, created_by):
    """Add a new medication"""
    medications = get_medications_db()
    
    # Generate medication ID
    medication_id = f"MED{len(medications['medications']) + 1:04d}"
    
    # Create medication record
    medication = {
        "id": medication_id,
        "patient_id": patient_id,
        "created_by": created_by,
        "created_at": str(datetime.now()),
        "data": data
    }
    
    medications["medications"].append(medication)
    save_medications_db(medications)
    return medication_id

def get_patient_medications(patient_id):
    """Get all medications for a patient"""
    medications = get_medications_db()
    return [med for med in medications["medications"] if med["patient_id"] == patient_id]

def update_medication(medication_id, data):
    """Update medication data"""
    medications = get_medications_db()
    for i, medication in enumerate(medications["medications"]):
        if medication["id"] == medication_id:
            # Update medication data
            for key, value in data.items():
                medications["medications"][i]["data"][key] = value
            
            # Update modified timestamp
            medications["medications"][i]["modified_at"] = str(datetime.now())
            
            save_medications_db(medications)
            return True
    return False

def delete_medication(medication_id):
    """Delete a medication"""
    medications = get_medications_db()
    medications["medications"] = [m for m in medications["medications"] if m["id"] != medication_id]
    save_medications_db(medications)
    return True

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

# ----- Helper Functions -----

def load_common_symptoms():
    """
    Load a list of common symptoms for the symptom checker.
    
    Returns:
        list: Common medical symptoms
    """
    symptoms = [
        "Abdominal pain", "Anxiety", "Back pain", "Bloating", "Chest pain", 
        "Chills", "Congestion", "Constipation", "Cough", "Depression", 
        "Diarrhea", "Difficulty breathing", "Dizziness", "Dry mouth",
        "Ear pain", "Fatigue", "Fever", "Headache", "Heartburn", 
        "Heart palpitations", "High blood pressure", "Hives", "Insomnia",
        "Irregular heartbeat", "Itching", "Joint pain", "Loss of appetite",
        "Memory problems", "Muscle weakness", "Nausea", "Neck pain", 
        "Night sweats", "Numbness", "Rash", "Runny nose", "Seizures",
        "Shortness of breath", "Skin discoloration", "Sore throat", 
        "Stiffness", "Swelling", "Swelling in legs", "Vomiting", 
        "Weakness", "Weight gain", "Weight loss", "Wheezing"
    ]
    return sorted(symptoms)

def load_common_conditions():
    """
    Load a list of common medical conditions for reference.
    
    Returns:
        dict: Dictionary mapping conditions to brief descriptions
    """
    conditions = {
        "Common Cold": "A viral infection of the upper respiratory tract",
        "Influenza": "A contagious respiratory illness caused by influenza viruses",
        "Hypertension": "High blood pressure that can lead to serious health problems",
        "Type 2 Diabetes": "A chronic condition affecting how the body processes blood sugar",
        "Asthma": "A condition causing airways to narrow and swell, producing extra mucus",
        "Migraine": "A headache of varying intensity, often accompanied by nausea and sensitivity to light and sound",
        "Allergic Rhinitis": "Inflammation of the nasal passages caused by allergens",
        "Gastroesophageal Reflux Disease (GERD)": "A digestive disorder affecting the ring of muscle between the esophagus and stomach",
        "Urinary Tract Infection": "An infection in any part of the urinary system",
        "Osteoarthritis": "A degenerative joint disease that causes pain and stiffness",
        "Depression": "A mood disorder causing persistent feelings of sadness and loss of interest",
        "Anxiety Disorders": "Conditions characterized by feelings of worry, anxiety, or fear",
        "Irritable Bowel Syndrome": "A common disorder affecting the large intestine",
        "Eczema": "A condition that makes your skin red and itchy",
        "Psoriasis": "A skin disease that causes red, itchy scaly patches"
    }
    return conditions

def get_lifestyle_fields():
    """
    Return common lifestyle fields for the user profile.
    
    Returns:
        dict: Dictionary of lifestyle fields and their default values
    """
    return {
        "Exercise": "",
        "Diet": "",
        "Sleep": "",
        "Stress level": "",
        "Smoking": "",
        "Alcohol consumption": ""
    }

def generate_sample_health_data(days=30, with_randomness=True):
    """
    Generate sample health data for visualization purposes.
    This is used only for the dashboard visualization and does not represent real patient data.
    
    Args:
        days (int): Number of days to generate data for
        with_randomness (bool): Whether to add random variation to the data
    
    Returns:
        pd.DataFrame: Sample health data for visualization
    """
    # Create date range for the past N days
    end_date = pd.Timestamp.now().floor('D')
    start_date = end_date - pd.Timedelta(days=days-1)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate sample data
    np.random.seed(42)  # For reproducibility
    
    # Create base patterns
    steps_base = np.linspace(7000, 9000, days)
    sleep_base = np.linspace(6.5, 7.5, days)
    heart_rate_base = np.linspace(72, 68, days)
    
    # Add weekly patterns and randomness if requested
    if with_randomness:
        # Create weekly pattern (lower values on weekends)
        weekly_pattern = np.array([0 if (i % 7 >= 5) else 1 for i in range(days)])
        
        steps = steps_base + weekly_pattern * 1500 + np.random.normal(0, 500, days)
        sleep = sleep_base - weekly_pattern * 0.5 + np.random.normal(0, 0.3, days)
        heart_rate = heart_rate_base + np.random.normal(0, 2, days)
    else:
        steps = steps_base
        sleep = sleep_base
        heart_rate = heart_rate_base
    
    # Ensure values are reasonable
    steps = np.clip(steps, 2000, 15000).astype(int)
    sleep = np.clip(sleep, 4, 10)
    heart_rate = np.clip(heart_rate, 50, 100).astype(int)
    
    # Create DataFrame
    data = pd.DataFrame({
        'date': date_range,
        'steps': steps,
        'sleep_hours': sleep,
        'heart_rate': heart_rate
    })
    
    return data

def get_demo_response(query, context=""):
    """
    Generate a demo response that simulates AI output.
    """
    # Sample responses for different types of medical queries
    if "symptoms" in query.lower() or "symptoms" in context.lower():
        responses = [
            """Based on the symptoms you've described, here are some possibilities to consider:

1. **Upper Respiratory Infection** (Common Cold): Your symptoms align with a viral upper respiratory infection, which typically resolves within 7-10 days with rest and hydration.

2. **Seasonal Allergies**: The timing and nature of your symptoms could indicate an allergic reaction, especially if you notice they worsen in certain environments.

3. **Sinusitis**: If you're experiencing facial pressure or pain, this could indicate inflammation of the sinuses.

**Severity Assessment**: Mild to moderate

**Medical Attention**: Most likely not immediately necessary unless symptoms worsen significantly or persist beyond 10-14 days.

**Self-Care Recommendations**:
- Rest and stay hydrated
- Over-the-counter decongestants may provide symptom relief
- Saline nasal irrigation can help clear congestion
- Monitor for fever or worsening symptoms

**Medical Disclaimer**: This information is not a diagnosis. If symptoms worsen, persist, or cause significant concern, please consult with a healthcare professional.""",

            """After reviewing the symptoms you've described, here are some potential considerations:

1. **Gastroenteritis** (Stomach Flu): Your symptoms suggest a possible viral or bacterial infection of the digestive tract.

2. **Food Intolerance/Sensitivity**: Consider if symptoms appear after eating specific foods.

3. **Irritable Bowel Syndrome**: If these symptoms recur frequently, they could align with IBS.

4. **Gastroesophageal Reflux Disease (GERD)**: Especially if you experience heartburn or regurgitation.

**Severity Assessment**: Moderate

**Medical Attention**: Consider consulting a healthcare provider if symptoms persist beyond 3-4 days, or if you experience severe dehydration, bloody stool, or extreme pain.

**Self-Care Recommendations**:
- Stay hydrated with clear fluids
- Eat small, bland meals (BRAT diet: bananas, rice, applesauce, toast)
- Avoid dairy, caffeine, and spicy foods temporarily
- Rest and monitor symptoms

**Medical Disclaimer**: These suggestions are not a substitute for professional medical advice. Please consult a healthcare provider for proper evaluation and treatment."""
        ]
        return random.choice(responses)
    
    elif "exercise" in query.lower() or "physical activity" in context.lower():
        return """Regular physical activity is crucial for maintaining good health. Here are some evidence-based recommendations:

1. **General Guidelines**: Aim for at least 150 minutes of moderate-intensity aerobic activity or 75 minutes of vigorous-intensity activity per week, plus muscle-strengthening activities on 2 or more days per week.

2. **Benefits**: Regular exercise helps control weight, reduces risk of heart disease, improves mental health and mood, strengthens bones and muscles, and reduces risk of many chronic diseases.

3. **Getting Started**: If you're new to exercise, start slowly and gradually increase duration and intensity. Walking, swimming, and cycling are excellent low-impact options.

4. **Consistency**: It's better to exercise regularly at moderate intensity than occasionally at high intensity.

Remember, it's important to listen to your body and avoid overexertion. If you have any underlying health conditions, please consult with your healthcare provider before starting a new exercise regimen.

**Medical Disclaimer**: These are general guidelines and not personalized recommendations. Individual needs may vary based on health status, age, and fitness level."""
    
    elif "diet" in query.lower() or "nutrition" in context.lower():
        return """Maintaining a balanced diet is fundamental to good health. Here are some evidence-based nutrition recommendations:

1. **Balanced Intake**: Focus on variety, nutrient density, and appropriate portions. A healthy eating pattern includes:
   - Vegetables of all types
   - Fruits, especially whole fruits
   - Grains, at least half of which are whole grains
   - Fat-free or low-fat dairy
   - Protein foods, including lean meats, poultry, eggs, seafood, beans, and nuts
   - Oils

2. **Limit**: Reduce consumption of added sugars, saturated fats, sodium, and highly processed foods.

3. **Hydration**: Drink plenty of water throughout the day.

4. **Individualization**: Nutritional needs vary based on age, gender, activity level, and overall health status.

If you have specific health concerns or conditions, a registered dietitian can provide personalized nutrition advice.

**Medical Disclaimer**: These recommendations provide general guidance but are not intended to replace personalized medical or nutritional advice."""
    
    else:
        return """Thank you for your health-related question. As a demo version of HealthAssist AI, I can provide general information on common health topics.

For specific medical concerns, I'd recommend consulting with a healthcare professional who can provide personalized advice based on a complete evaluation of your situation.

Some general wellness tips include:
- Maintain a balanced diet rich in fruits, vegetables, whole grains, and lean proteins
- Aim for at least 150 minutes of moderate physical activity weekly
- Ensure adequate sleep (7-9 hours for most adults)
- Stay hydrated by drinking plenty of water throughout the day
- Practice stress management techniques like meditation or deep breathing

**Medical Disclaimer**: This information is for educational purposes only and is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition."""

# ----- Initialize Session State -----
# Initialize user session variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

if 'common_symptoms' not in st.session_state:
    st.session_state.common_symptoms = load_common_symptoms()

if 'common_conditions' not in st.session_state:
    st.session_state.common_conditions = load_common_conditions()

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'

if 'health_data' not in st.session_state:
    st.session_state.health_data = generate_sample_health_data(days=30)

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []

if 'patient_id' not in st.session_state:
    st.session_state.patient_id = None

# ----- Login/Registration Pages -----
def show_login_page():
    st.title("🩺 HealthAssist AI")
    st.subheader("Login to your account")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter your username and password")
    
    with col2:
        st.markdown("""
        ### Welcome to HealthAssist AI
        
        Your AI-powered healthcare assistant with features for:
        
        - 👨‍⚕️ **Doctors**: Manage patients and their health records
        - 👨‍💼 **Administrators**: Manage system users and settings
        - 👨‍👩‍👧‍👦 **Patients**: Track health metrics and get personalized recommendations
        
        Don't have an account? Contact an administrator to create one for you.
        """)

def show_registration_page():
    st.title("🩺 HealthAssist AI")
    st.subheader("Register New User")
    
    # Only admin can create new users
    if st.session_state.user['role'] != 'admin':
        st.error("Only administrators can create new users")
        return
    
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["patient", "doctor", "admin"])
        
        submit = st.form_submit_button("Register", use_container_width=True)
        
        if submit:
            if not (name and email and username and password and confirm_password):
                st.error("Please fill out all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = register_user(username, password, role, name, email)
                if success:
                    st.success(message)
                    st.session_state.current_view = 'admin_panel'
                    st.rerun()
                else:
                    st.error(message)

# ----- AI Response Functions -----
def get_symptom_analysis(symptoms, age, gender, medical_history):
    """Generate a symptom analysis response using OpenAI if available"""
    if not symptoms:
        return "Please provide at least one symptom for analysis."
    
    # Check if OpenAI API key is available
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    if openai_api_key:
        try:
            from openai import OpenAI
            
            # Initialize OpenAI client
            client = OpenAI(api_key=openai_api_key)
            
            # Prepare prompt for OpenAI
            prompt = f"""
            I'm a {age}-year-old {gender} experiencing the following symptoms: {', '.join(symptoms)}.
            My medical history includes: {', '.join(medical_history) if medical_history else 'None'}.
            
            Please provide a medical analysis of these symptoms with the following information:
            1. Possible conditions that might explain these symptoms
            2. Severity assessment (mild, moderate, severe)
            3. Whether medical attention is likely necessary
            4. Self-care recommendations
            5. Warning signs that would indicate I should seek immediate medical attention
            
            Include a clear medical disclaimer at the end.
            """
            
            # Get response from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a helpful healthcare assistant providing symptom analysis. Always include appropriate medical disclaimers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            
            return response.choices[0].message.content
        except Exception as e:
            # Create context for fallback demo response
            fallback_context = f"""
            The user is a {age}-year-old {gender} with the following symptoms: {', '.join(symptoms)}.
            Medical history: {', '.join(medical_history) if medical_history else 'None provided'}.
            """
            # Fallback to demo response with error message
            return f"Error connecting to AI service. Using demo response instead.\n\n{get_demo_response('symptoms analysis', fallback_context)}"
    
    # If no API key, use demo response
    context = f"""
    The user is a {age}-year-old {gender} with the following symptoms: {', '.join(symptoms)}.
    Medical history: {', '.join(medical_history) if medical_history else 'None provided'}.
    """
    return get_demo_response("symptoms analysis", context)

def get_medical_qa_response(question, user_info=None):
    """Generate a medical Q&A response using OpenAI if available"""
    if not question:
        return "Please ask a medical question to receive a response."
    
    # Check if OpenAI API key is available
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    # Prepare context
    context = ""
    if user_info:
        context = f"""
        User information:
        - Age: {user_info.get('age', 'Not provided')}
        - Gender: {user_info.get('gender', 'Not provided')}
        - Medical history: {', '.join(user_info.get('medical_history', [])) if user_info.get('medical_history') else 'None provided'}
        """
    
    if openai_api_key:
        try:
            from openai import OpenAI
            
            # Initialize OpenAI client
            client = OpenAI(api_key=openai_api_key)
            
            # Prepare system message with medical guidelines
            system_message = """
            You are a helpful healthcare assistant providing informational answers to medical questions.
            
            Guidelines:
            1. Provide evidence-based information and cite medical consensus where appropriate
            2. Clearly distinguish between established medical facts and areas where medical opinion varies
            3. Be respectful and non-judgmental about health conditions and choices
            4. Use plain language that is accessible to non-medical professionals
            5. Do not make definitive diagnoses
            6. Include relevant preventive health information when appropriate
            7. Always include a clear medical disclaimer at the end
            """
            
            # Prepare user message with context
            user_message = question
            if context:
                user_message = f"{context}\n\nMy question is: {question}"
            
            # Get response from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800
            )
            
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to demo response with error message
            return f"Error connecting to AI service. Using demo response instead.\n\n{get_demo_response(question, context)}"
    
    # If no API key, use demo response
    return get_demo_response(question, context)

def get_care_recommendations(symptoms, age, gender, medical_history, lifestyle_factors):
    """Generate personalized care recommendations"""
    if not symptoms and not medical_history:
        return "Please provide some health information to receive personalized recommendations."
    
    lifestyle_info = "\n".join([f"- {k}: {v}" for k, v in lifestyle_factors.items() if v])
    
    context = f"""
    The user is a {age}-year-old {gender} with the following:
    
    Symptoms: {', '.join(symptoms) if symptoms else 'None reported'}
    Medical history: {', '.join(medical_history) if medical_history else 'None reported'}
    
    Lifestyle information:
    {lifestyle_info if lifestyle_info else 'None provided'}
    """
    
    return get_demo_response("lifestyle recommendations", context)

# ----- Patient Dashboard -----
def show_patient_dashboard():
    import numpy as np
    
    st.header("📊 Patient Health Dashboard")
    
    # Get patient data
    if st.session_state.patient_id:
        patient = get_patient(st.session_state.patient_id)
    else:
        # If doctor or admin is viewing without selecting a patient
        if st.session_state.user['role'] in ['doctor', 'admin']:
            patients = get_all_patients()
            if patients:
                selected_patient = st.selectbox(
                    "Select Patient",
                    options=[f"{p['name']} (ID: {p['id']})" for p in patients],
                    format_func=lambda x: x
                )
                
                if selected_patient:
                    patient_id = selected_patient.split("(ID: ")[1].split(")")[0]
                    st.session_state.patient_id = patient_id
                    patient = get_patient(patient_id)
                    st.rerun()
                else:
                    st.warning("Please select a patient to view their dashboard")
                    return
            else:
                st.warning("No patients found in the system")
                return
        # For patients viewing their own dashboard
        elif st.session_state.user['role'] == 'patient':
            # Find patient record for this user
            patients = get_all_patients()
            patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
            
            if not patient:
                st.warning("Patient profile not found. Please complete your profile first.")
                if st.button("Create Patient Profile"):
                    st.session_state.current_view = 'patient_profile'
                    st.rerun()
                return
            
            st.session_state.patient_id = patient['id']
        else:
            st.error("Unauthorized access")
            return
    
    st.subheader(f"Health Dashboard for {patient['name']}")
    st.markdown(f"""
    **Patient ID**: {patient['id']}  
    **Age**: {patient['age']}  
    **Gender**: {patient['gender']}
    """)
    
    # Dashboard time range selector
    time_range = st.selectbox(
        "Select time range:",
        ["Last 7 days", "Last 14 days", "Last 30 days", "Last 90 days"],
        index=2,  # Default to 30 days
        key="dashboard_timerange"
    )
    
    # Convert time range to number of days
    days_mapping = {
        "Last 7 days": 7,
        "Last 14 days": 14,
        "Last 30 days": 30,
        "Last 90 days": 90
    }
    days = days_mapping[time_range]
    
    # Filter data based on selected time range
    end_date = pd.Timestamp.now().floor('D')
    start_date = end_date - pd.Timedelta(days=days-1)
    
    # If we don't have enough data, generate more
    if len(st.session_state.health_data) < days:
        st.session_state.health_data = generate_sample_health_data(days=max(90, days))
    
    filtered_data = st.session_state.health_data[
        (st.session_state.health_data['date'] >= start_date) & 
        (st.session_state.health_data['date'] <= end_date)
    ].copy()
    
    # Main dashboard layout
    st.subheader("Health Metrics Overview")
    
    # Metrics cards
    cols = st.columns(3)
    
    # Calculate average metrics for the selected period
    avg_steps = int(filtered_data['steps'].mean())
    avg_sleep = round(filtered_data['sleep_hours'].mean(), 1)
    avg_heart_rate = int(filtered_data['heart_rate'].mean())
    
    # Display metric cards
    with cols[0]:
        st.metric(
            label="Avg. Daily Steps",
            value=f"{avg_steps:,}",
            delta=f"{int(avg_steps - 8000)}" if avg_steps != 8000 else None,
            delta_color="normal"
        )
    
    with cols[1]:
        st.metric(
            label="Avg. Sleep (hours)",
            value=avg_sleep,
            delta=f"{round(avg_sleep - 7.0, 1)}" if avg_sleep != 7.0 else None,
            delta_color="normal"
        )
    
    with cols[2]:
        st.metric(
            label="Avg. Heart Rate (BPM)",
            value=avg_heart_rate,
            delta=f"{int(avg_heart_rate - 70)}" if avg_heart_rate != 70 else None,
            delta_color="inverse"  # Lower heart rate is generally better
        )
    
    # Create trend visualizations
    st.subheader("Health Trends")
    
    # Daily steps chart
    fig_steps = px.line(
        filtered_data, 
        x='date', 
        y='steps',
        title='Daily Steps',
        markers=True
    )
    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps",
        hovermode="x unified"
    )
    fig_steps.add_hline(
        y=10000, 
        line_dash="dash", 
        line_color="green",
        annotation_text="Recommended Steps",
        annotation_position="top right"
    )
    st.plotly_chart(fig_steps, use_container_width=True)
    
    # Sleep hours and heart rate charts
    cols = st.columns(2)
    
    with cols[0]:
        # Sleep hours chart
        fig_sleep = px.line(
            filtered_data, 
            x='date', 
            y='sleep_hours',
            title='Sleep Duration',
            markers=True
        )
        fig_sleep.update_layout(
            xaxis_title="Date",
            yaxis_title="Hours",
            hovermode="x unified",
            yaxis=dict(range=[4, 10])
        )
        fig_sleep.add_hrect(
            y0=7, y1=9,
            line_width=0, 
            fillcolor="green", 
            opacity=0.2,
            annotation_text="Ideal Range",
            annotation_position="top right"
        )
        st.plotly_chart(fig_sleep, use_container_width=True)
    
    with cols[1]:
        # Heart rate chart
        fig_hr = px.line(
            filtered_data, 
            x='date', 
            y='heart_rate',
            title='Resting Heart Rate',
            markers=True
        )
        fig_hr.update_layout(
            xaxis_title="Date",
            yaxis_title="BPM",
            hovermode="x unified",
            yaxis=dict(range=[50, 100])
        )
        fig_hr.add_hrect(
            y0=60, y1=80,
            line_width=0, 
            fillcolor="green", 
            opacity=0.2,
            annotation_text="Normal Range",
            annotation_position="top right"
        )
        st.plotly_chart(fig_hr, use_container_width=True)
    
    # Get patient records
    records = get_patient_records(st.session_state.patient_id)
    
    # Patient records section
    st.subheader("Medical Records")
    if records:
        # Display records in tabs by type
        record_types = list(set(record['type'] for record in records))
        tabs = st.tabs(record_types)
        
        for i, record_type in enumerate(record_types):
            with tabs[i]:
                filtered_records = [r for r in records if r['type'] == record_type]
                filtered_records.sort(key=lambda x: x['created_at'], reverse=True)
                
                for record in filtered_records:
                    with st.expander(f"Record from {record['created_at'][:10]} by {record['created_by']}"):
                        st.json(record['data'])
    else:
        st.info("No medical records found for this patient")
    
    # Doctor Notes Section (only visible to doctors)
    if st.session_state.user['role'] in ['doctor', 'admin']:
        st.subheader("Add Medical Record")
        
        with st.form("add_record_form"):
            record_type = st.selectbox(
                "Record Type",
                ["Consultation", "Prescription", "Lab Result", "Treatment Plan"]
            )
            
            record_data = {}
            
            if record_type == "Consultation":
                record_data["symptoms"] = st.text_area("Symptoms Reported")
                record_data["diagnosis"] = st.text_area("Diagnosis")
                record_data["notes"] = st.text_area("Doctor's Notes")
                
            elif record_type == "Prescription":
                record_data["medications"] = st.text_area("Medications (one per line)")
                record_data["dosage"] = st.text_area("Dosage Instructions")
                record_data["duration"] = st.text_input("Duration")
                record_data["notes"] = st.text_area("Additional Notes")
                
            elif record_type == "Lab Result":
                record_data["test_type"] = st.text_input("Test Type")
                record_data["result"] = st.text_area("Test Results")
                record_data["reference_range"] = st.text_input("Reference Range")
                record_data["interpretation"] = st.text_area("Interpretation")
                
            elif record_type == "Treatment Plan":
                record_data["condition"] = st.text_input("Condition")
                record_data["treatment"] = st.text_area("Treatment Plan")
                record_data["duration"] = st.text_input("Expected Duration")
                record_data["follow_up"] = st.text_input("Follow-up Required")
            
            submit = st.form_submit_button("Add Record")
            
            if submit:
                add_health_record(
                    patient_id=st.session_state.patient_id,
                    record_type=record_type,
                    data=record_data,
                    created_by=st.session_state.user['username']
                )
                st.success(f"{record_type} record added successfully!")
                st.rerun()

# ----- Doctor's Patient List -----
def show_doctor_patient_list():
    st.header("👨‍⚕️ Patient Management")
    
    if st.session_state.user['role'] not in ['doctor', 'admin']:
        st.error("Only doctors can access this page")
        return
    
    # Get all patients
    patients = get_all_patients()
    
    # Add new patient section
    with st.expander("Add New Patient", expanded=False):
        with st.form("add_patient_form"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Contact Number")
            email = st.text_input("Email")
            address = st.text_area("Address")
            medical_history = st.text_area("Medical History")
            allergies = st.text_area("Allergies")
            
            # If admin, allow linking patient to existing user
            user_id = None
            if st.session_state.user['role'] == 'admin':
                users = get_users_db()
                patient_users = [u for u in users["users"] if u["role"] == "patient"]
                
                if patient_users:
                    user_options = ["None"] + [f"{u['name']} ({u['username']})" for u in patient_users]
                    selected_user = st.selectbox("Link to User Account", options=user_options)
                    
                    if selected_user != "None":
                        user_id = selected_user.split("(")[1].split(")")[0]
            
            submit = st.form_submit_button("Add Patient")
            
            if submit:
                if name and age and gender:
                    # Prepare patient data
                    patient_data = {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "contact": contact,
                        "email": email,
                        "address": address,
                        "medical_history": medical_history.split('\n') if medical_history else [],
                        "allergies": allergies.split('\n') if allergies else [],
                        "user_id": user_id
                    }
                    
                    # Add patient
                    patient_id = add_patient(patient_data)
                    st.success(f"Patient added successfully with ID: {patient_id}")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (Name, Age, Gender)")
    
    # Display patient list
    st.subheader("Patient List")
    
    if patients:
        # Create a dataframe for display
        patient_data = []
        for p in patients:
            patient_data.append({
                "ID": p["id"],
                "Name": p["name"],
                "Age": p["age"],
                "Gender": p["gender"],
                "Contact": p.get("contact", ""),
                "Last Visit": p.get("last_visit", "N/A")
            })
        
        df = pd.DataFrame(patient_data)
        st.dataframe(df, use_container_width=True)
        
        # Patient selection for viewing
        selected_patient_id = st.selectbox(
            "Select Patient to View",
            options=[p["id"] for p in patients],
            format_func=lambda x: next((p["name"] + " (ID: " + p["id"] + ")" for p in patients if p["id"] == x), x)
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("View Patient Dashboard", use_container_width=True):
                st.session_state.patient_id = selected_patient_id
                st.session_state.current_view = 'patient_dashboard'
                st.rerun()
        
        with col2:
            if st.button("View Patient Records", use_container_width=True):
                st.session_state.patient_id = selected_patient_id
                st.session_state.current_view = 'patient_records'
                st.rerun()
    else:
        st.info("No patients found in the system. Add your first patient using the form above.")

# ----- Admin Panel -----
def show_admin_panel():
    st.header("👨‍💼 Administration Panel")
    
    if st.session_state.user['role'] != 'admin':
        st.error("Only administrators can access this page")
        return
    
    tabs = st.tabs(["User Management", "System Statistics", "Settings"])
    
    # User Management Tab
    with tabs[0]:
        st.subheader("User Management")
        
        # Add new user button
        if st.button("Add New User", use_container_width=True):
            st.session_state.current_view = 'registration'
            st.rerun()
        
        # Get all users
        users = get_users_db()["users"]
        
        # Create a dataframe for display
        user_data = []
        for u in users:
            user_data.append({
                "Username": u["username"],
                "Name": u["name"],
                "Email": u["email"],
                "Role": u["role"].capitalize(),
                "Created": u["created_at"][:10] if len(u["created_at"]) > 10 else u["created_at"]
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        
        # User selection for actions
        selected_username = st.selectbox(
            "Select User",
            options=[u["username"] for u in users],
            format_func=lambda x: next((u["name"] + " (" + x + ")" for u in users if u["username"] == x), x)
        )
        
        # Actions for selected user
        if selected_username:
            selected_user = next((u for u in users if u["username"] == selected_username), None)
            
            if selected_user:
                with st.expander("Edit User", expanded=False):
                    with st.form("edit_user_form"):
                        name = st.text_input("Full Name", value=selected_user["name"])
                        email = st.text_input("Email", value=selected_user["email"])
                        role = st.selectbox("Role", ["patient", "doctor", "admin"], index=["patient", "doctor", "admin"].index(selected_user["role"]))
                        
                        reset_password = st.checkbox("Reset Password")
                        new_password = st.text_input("New Password", type="password") if reset_password else None
                        
                        submit = st.form_submit_button("Update User")
                        
                        if submit:
                            update_data = {
                                "name": name,
                                "email": email,
                                "role": role
                            }
                            
                            if reset_password and new_password:
                                update_data["password"] = hash_password(new_password)
                            
                            if update_user(selected_username, update_data):
                                st.success("User updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update user")
    
    # System Statistics Tab
    with tabs[1]:
        st.subheader("System Statistics")
        
        # Get statistics
        users = get_users_db()["users"]
        patients = get_all_patients()
        records = get_health_records_db()["records"]
        
        # Display statistics
        cols = st.columns(3)
        
        with cols[0]:
            st.metric("Total Users", len(users))
            st.metric("Patients", len([u for u in users if u["role"] == "patient"]))
            st.metric("Doctors", len([u for u in users if u["role"] == "doctor"]))
        
        with cols[1]:
            st.metric("Total Patients", len(patients))
            st.metric("Male Patients", len([p for p in patients if p["gender"] == "Male"]))
            st.metric("Female Patients", len([p for p in patients if p["gender"] == "Female"]))
        
        with cols[2]:
            st.metric("Total Records", len(records))
            record_types = {}
            for r in records:
                if r["type"] in record_types:
                    record_types[r["type"]] += 1
                else:
                    record_types[r["type"]] = 1
            
            for rt, count in record_types.items():
                st.metric(f"{rt} Records", count)
        
        # User activity by role
        st.subheader("User Distribution by Role")
        role_counts = {"Admin": 0, "Doctor": 0, "Patient": 0}
        for u in users:
            role = u["role"].capitalize()
            if role in role_counts:
                role_counts[role] += 1
            else:
                role_counts[role] = 1
        
        # Create pie chart
        fig = px.pie(
            values=list(role_counts.values()),
            names=list(role_counts.keys()),
            title="User Distribution by Role"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Settings Tab
    with tabs[2]:
        st.subheader("System Settings")
        
        # System backup option
        if st.button("Backup System Data"):
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = "backups"
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Backup users
            if os.path.exists('users_db.json'):
                with open('users_db.json', 'r') as f:
                    users_data = f.read()
                
                with open(f"{backup_dir}/users_db_{timestamp}.json", 'w') as f:
                    f.write(users_data)
            
            # Backup patients
            if os.path.exists('patients_db.json'):
                with open('patients_db.json', 'r') as f:
                    patients_data = f.read()
                
                with open(f"{backup_dir}/patients_db_{timestamp}.json", 'w') as f:
                    f.write(patients_data)
            
            # Backup health records
            if os.path.exists('health_records_db.json'):
                with open('health_records_db.json', 'r') as f:
                    records_data = f.read()
                
                with open(f"{backup_dir}/health_records_db_{timestamp}.json", 'w') as f:
                    f.write(records_data)
            
            st.success(f"System backup created successfully in {backup_dir} directory")

# ----- Patient Records View -----
def show_patient_records():
    st.header("📋 Patient Records")
    
    # Check permissions
    if st.session_state.user['role'] not in ['doctor', 'admin']:
        if st.session_state.user['role'] == 'patient':
            # Patients can only view their own records
            patients = get_all_patients()
            patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
            
            if not patient:
                st.warning("Patient profile not found.")
                return
            
            st.session_state.patient_id = patient['id']
        else:
            st.error("Unauthorized access")
            return
    
    # If no patient selected, prompt for selection
    if not st.session_state.patient_id:
        patients = get_all_patients()
        if patients:
            selected_patient = st.selectbox(
                "Select Patient",
                options=[f"{p['name']} (ID: {p['id']})" for p in patients],
                format_func=lambda x: x
            )
            
            if selected_patient:
                patient_id = selected_patient.split("(ID: ")[1].split(")")[0]
                st.session_state.patient_id = patient_id
                st.rerun()
            else:
                st.warning("Please select a patient to view their records")
                return
        else:
            st.warning("No patients found in the system")
            return
    
    # Get patient and their records
    patient = get_patient(st.session_state.patient_id)
    records = get_patient_records(st.session_state.patient_id)
    
    # Display patient info
    st.subheader(f"Records for {patient['name']}")
    st.markdown(f"""
    **Patient ID**: {patient['id']}  
    **Age**: {patient['age']}  
    **Gender**: {patient['gender']}
    """)
    
    # Add new record (only for doctors/admin)
    if st.session_state.user['role'] in ['doctor', 'admin']:
        with st.expander("Add New Record", expanded=False):
            with st.form("add_record_form"):
                record_type = st.selectbox(
                    "Record Type",
                    ["Consultation", "Prescription", "Lab Result", "Treatment Plan", "Vital Signs"]
                )
                
                record_data = {}
                
                if record_type == "Consultation":
                    record_data["symptoms"] = st.text_area("Symptoms Reported")
                    record_data["diagnosis"] = st.text_area("Diagnosis")
                    record_data["notes"] = st.text_area("Doctor's Notes")
                    
                elif record_type == "Prescription":
                    record_data["medications"] = st.text_area("Medications (one per line)")
                    record_data["dosage"] = st.text_area("Dosage Instructions")
                    record_data["duration"] = st.text_input("Duration")
                    record_data["notes"] = st.text_area("Additional Notes")
                    
                elif record_type == "Lab Result":
                    record_data["test_type"] = st.text_input("Test Type")
                    record_data["result"] = st.text_area("Test Results")
                    record_data["reference_range"] = st.text_input("Reference Range")
                    record_data["interpretation"] = st.text_area("Interpretation")
                    
                elif record_type == "Treatment Plan":
                    record_data["condition"] = st.text_input("Condition")
                    record_data["treatment"] = st.text_area("Treatment Plan")
                    record_data["duration"] = st.text_input("Expected Duration")
                    record_data["follow_up"] = st.text_input("Follow-up Required")
                    
                elif record_type == "Vital Signs":
                    record_data["blood_pressure"] = st.text_input("Blood Pressure (mmHg)")
                    record_data["heart_rate"] = st.number_input("Heart Rate (BPM)", min_value=0)
                    record_data["temperature"] = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, step=0.1)
                    record_data["respiratory_rate"] = st.number_input("Respiratory Rate (breaths/min)", min_value=0)
                    record_data["oxygen_saturation"] = st.number_input("Oxygen Saturation (%)", min_value=0, max_value=100)
                
                submit = st.form_submit_button("Add Record")
                
                if submit:
                    add_health_record(
                        patient_id=st.session_state.patient_id,
                        record_type=record_type,
                        data=record_data,
                        created_by=st.session_state.user['username']
                    )
                    st.success(f"{record_type} record added successfully!")
                    st.rerun()
    
    # Display patient records
    if records:
        # Sort records by date (most recent first)
        records.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Filter options
        record_types = list(set(record['type'] for record in records))
        selected_type = st.multiselect("Filter by Record Type", options=record_types, default=record_types)
        
        # Filter records
        if selected_type:
            filtered_records = [r for r in records if r['type'] in selected_type]
        else:
            filtered_records = records
        
        # Display records in a timeline
        for record in filtered_records:
            record_date = record['created_at'][:10] if len(record['created_at']) >= 10 else record['created_at']
            
            with st.expander(f"{record['type']} - {record_date} by {record['created_by']}"):
                # Display record data in a user-friendly format
                if record['type'] == "Consultation":
                    st.markdown("#### Consultation Notes")
                    st.markdown(f"**Symptoms Reported:** {record['data'].get('symptoms', 'N/A')}")
                    st.markdown(f"**Diagnosis:** {record['data'].get('diagnosis', 'N/A')}")
                    st.markdown(f"**Doctor's Notes:** {record['data'].get('notes', 'N/A')}")
                
                elif record['type'] == "Prescription":
                    st.markdown("#### Prescription")
                    st.markdown(f"**Medications:**")
                    medications = record['data'].get('medications', '').split('\n')
                    for med in medications:
                        if med.strip():
                            st.markdown(f"- {med}")
                    
                    st.markdown(f"**Dosage:** {record['data'].get('dosage', 'N/A')}")
                    st.markdown(f"**Duration:** {record['data'].get('duration', 'N/A')}")
                    st.markdown(f"**Notes:** {record['data'].get('notes', 'N/A')}")
                
                elif record['type'] == "Lab Result":
                    st.markdown("#### Laboratory Result")
                    st.markdown(f"**Test:** {record['data'].get('test_type', 'N/A')}")
                    st.markdown(f"**Result:** {record['data'].get('result', 'N/A')}")
                    st.markdown(f"**Reference Range:** {record['data'].get('reference_range', 'N/A')}")
                    st.markdown(f"**Interpretation:** {record['data'].get('interpretation', 'N/A')}")
                
                elif record['type'] == "Treatment Plan":
                    st.markdown("#### Treatment Plan")
                    st.markdown(f"**Condition:** {record['data'].get('condition', 'N/A')}")
                    st.markdown(f"**Treatment:** {record['data'].get('treatment', 'N/A')}")
                    st.markdown(f"**Duration:** {record['data'].get('duration', 'N/A')}")
                    st.markdown(f"**Follow-up:** {record['data'].get('follow_up', 'N/A')}")
                
                elif record['type'] == "Vital Signs":
                    st.markdown("#### Vital Signs")
                    st.markdown(f"**Blood Pressure:** {record['data'].get('blood_pressure', 'N/A')}")
                    st.markdown(f"**Heart Rate:** {record['data'].get('heart_rate', 'N/A')} BPM")
                    st.markdown(f"**Temperature:** {record['data'].get('temperature', 'N/A')}°C")
                    st.markdown(f"**Respiratory Rate:** {record['data'].get('respiratory_rate', 'N/A')} breaths/min")
                    st.markdown(f"**Oxygen Saturation:** {record['data'].get('oxygen_saturation', 'N/A')}%")
                
                else:
                    st.json(record['data'])
    else:
        st.info("No records found for this patient.")
    
    # Navigation buttons
    if st.session_state.user['role'] in ['doctor', 'admin']:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Back to Patient List", use_container_width=True):
                st.session_state.patient_id = None
                st.session_state.current_view = 'doctor_patient_list'
                st.rerun()
        
        with col2:
            if st.button("View Patient Dashboard", use_container_width=True):
                st.session_state.current_view = 'patient_dashboard'
                st.rerun()

# ----- Patient Profile -----
def show_patient_profile():
    st.header("👤 Patient Profile")
    
    # Check if this is a patient creating their own profile
    creating_own_profile = st.session_state.user['role'] == 'patient'
    
    # Get patients list
    patients = get_all_patients()
    
    # If patient is logged in, find their profile
    if creating_own_profile:
        patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        
        if patient:
            st.info(f"You already have a profile. You can view your health dashboard or edit your information below.")
            st.session_state.patient_id = patient['id']
    
    # For doctors/admins, if no patient selected, prompt for selection
    if not creating_own_profile and not st.session_state.patient_id:
        if st.session_state.user['role'] in ['doctor', 'admin']:
            if patients:
                selected_patient = st.selectbox(
                    "Select Patient",
                    options=[f"{p['name']} (ID: {p['id']})" for p in patients],
                    format_func=lambda x: x
                )
                
                if selected_patient:
                    patient_id = selected_patient.split("(ID: ")[1].split(")")[0]
                    st.session_state.patient_id = patient_id
                    st.rerun()
                else:
                    st.warning("Please select a patient to view their profile")
                    return
            else:
                st.warning("No patients found in the system")
                return
        else:
            st.error("Unauthorized access")
            return
    
    # Get patient if ID exists
    patient = None
    if st.session_state.patient_id:
        patient = get_patient(st.session_state.patient_id)
    
    # Patient profile form
    with st.form("patient_profile_form"):
        name = st.text_input("Full Name", value=patient['name'] if patient else st.session_state.user['name'] if creating_own_profile else "")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=patient['age'] if patient else 0)
            height = st.number_input("Height (cm)", min_value=0, max_value=250, value=patient.get('height', 0) if patient else 0)
            blood_type = st.selectbox(
                "Blood Type", 
                ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                index=["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(patient.get('blood_type', 'Unknown')) if patient and 'blood_type' in patient else 0
            )
        
        with col2:
            gender = st.selectbox(
                "Gender", 
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(patient['gender']) if patient else 0
            )
            weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=patient.get('weight', 0) if patient else 0)
            emergency_contact = st.text_input("Emergency Contact", value=patient.get('emergency_contact', '') if patient else "")
        
        contact = st.text_input("Contact Number", value=patient.get('contact', '') if patient else "")
        email = st.text_input("Email", value=patient.get('email', '') if patient else st.session_state.user['email'] if creating_own_profile else "")
        address = st.text_area("Address", value=patient.get('address', '') if patient else "")
        
        # Medical information
        st.subheader("Medical Information")
        
        allergies = st.text_area("Allergies (one per line)", value='\n'.join(patient.get('allergies', [])) if patient and 'allergies' in patient else "")
        medical_history = st.text_area("Medical History (one per line)", value='\n'.join(patient.get('medical_history', [])) if patient and 'medical_history' in patient else "")
        current_medications = st.text_area("Current Medications (one per line)", value='\n'.join(patient.get('medications', [])) if patient and 'medications' in patient else "")
        
        if creating_own_profile:
            submit_text = "Create My Profile" if not patient else "Update My Profile"
        else:
            submit_text = "Add Patient" if not patient else "Update Patient"
        
        submit = st.form_submit_button(submit_text, use_container_width=True)
        
        if submit:
            if name and age and gender:
                # Prepare patient data
                patient_data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "height": height,
                    "weight": weight,
                    "blood_type": blood_type,
                    "emergency_contact": emergency_contact,
                    "contact": contact,
                    "email": email,
                    "address": address,
                    "allergies": [a.strip() for a in allergies.split('\n') if a.strip()],
                    "medical_history": [mh.strip() for mh in medical_history.split('\n') if mh.strip()],
                    "medications": [med.strip() for med in current_medications.split('\n') if med.strip()]
                }
                
                # If creating own profile, link to user account
                if creating_own_profile:
                    patient_data["user_id"] = st.session_state.user['username']
                
                # Update or create patient
                if patient:
                    if update_patient(st.session_state.patient_id, patient_data):
                        st.success("Patient profile updated successfully!")
                    else:
                        st.error("Failed to update patient profile")
                else:
                    patient_id = add_patient(patient_data)
                    st.session_state.patient_id = patient_id
                    st.success(f"Patient profile created successfully with ID: {patient_id}")
                
                # Redirect to appropriate page
                if creating_own_profile:
                    st.session_state.current_view = 'patient_dashboard'
                else:
                    st.session_state.current_view = 'patient_records'
                
                st.rerun()
            else:
                st.error("Please fill in all required fields (Name, Age, Gender)")
    
    # Show BMI calculation if weight and height are available
    if patient and patient.get('height', 0) > 0 and patient.get('weight', 0) > 0:
        st.subheader("Health Metrics")
        
        # Calculate BMI
        height_m = patient['height'] / 100
        bmi = patient['weight'] / (height_m * height_m)
        
        st.metric("BMI (Body Mass Index)", f"{bmi:.1f}")
        
        # BMI categories
        if bmi < 18.5:
            st.markdown("**BMI Category**: Underweight")
        elif bmi < 25:
            st.markdown("**BMI Category**: Normal weight")
        elif bmi < 30:
            st.markdown("**BMI Category**: Overweight")
        else:
            st.markdown("**BMI Category**: Obesity")
        
        # Health risk assessment based on BMI and other factors
        risk_factors = []
        
        if bmi > 30:
            risk_factors.append("High BMI (Obesity)")
        
        if patient.get('medical_history'):
            for condition in patient['medical_history']:
                if any(c.lower() in condition.lower() for c in ["diabetes", "hypertension", "heart disease", "stroke"]):
                    risk_factors.append(f"History of {condition}")
        
        if risk_factors:
            st.subheader("Health Risk Factors")
            for factor in risk_factors:
                st.markdown(f"- {factor}")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("View Dashboard", use_container_width=True):
            st.session_state.current_view = 'patient_dashboard'
            st.rerun()
    
    with col2:
        if st.session_state.user['role'] in ['doctor', 'admin']:
            if st.button("Back to Patient List", use_container_width=True):
                st.session_state.patient_id = None
                st.session_state.current_view = 'doctor_patient_list'
                st.rerun()

# ----- Main Application -----
def show_medication_tracker():
    """Display the medication tracker page for managing medications and reminders"""
    st.header("💊 Medication Tracker")
    st.markdown("""
    Keep track of your medications, dosages, and schedules. This tool helps you manage your 
    prescriptions and set reminders for when to take your medications.
    """)
    
    # Get patient ID
    if st.session_state.user['role'] == 'patient':
        patients = get_all_patients()
        patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        
        if not patient:
            st.warning("Patient profile not found. Please complete your profile first.")
            if st.button("Create Patient Profile"):
                st.session_state.current_view = 'patient_profile'
                st.rerun()
            return
        
        patient_id = patient['id']
    else:
        # For doctors/admins, if no patient selected, prompt for selection
        if not st.session_state.patient_id:
            patients = get_all_patients()
            if patients:
                selected_patient = st.selectbox(
                    "Select Patient",
                    options=[f"{p['name']} (ID: {p['id']})" for p in patients],
                    format_func=lambda x: x
                )
                
                if selected_patient:
                    patient_id = selected_patient.split("(ID: ")[1].split(")")[0]
                    st.session_state.patient_id = patient_id
                    st.rerun()
                else:
                    st.warning("Please select a patient to view their medications")
                    return
            else:
                st.warning("No patients found in the system")
                return
        else:
            patient_id = st.session_state.patient_id
            
    # Get patient info
    patient = get_patient(patient_id)
    st.subheader(f"Medication Tracker for {patient['name']}")
    
    # Get patient medications
    medications = get_patient_medications(patient_id)
    
    # Add new medication section
    with st.expander("Add New Medication", expanded=False):
        with st.form("add_medication_form"):
            med_name = st.text_input("Medication Name")
            dosage = st.text_input("Dosage (e.g., 10mg)")
            frequency = st.selectbox(
                "Frequency",
                ["Once daily", "Twice daily", "Three times daily", "Four times daily", 
                 "Once weekly", "As needed", "Other"]
            )
            
            if frequency == "Other":
                custom_frequency = st.text_input("Custom Frequency")
            else:
                custom_frequency = ""
            
            timing = st.multiselect(
                "Time of Day",
                ["Morning", "Afternoon", "Evening", "Before bed", "With meals", "Before meals", "After meals"]
            )
            
            start_date = st.date_input("Start Date", min_value=datetime.now())
            end_date = st.date_input("End Date (leave blank if ongoing)", value=None)
            
            instructions = st.text_area("Special Instructions")
            notes = st.text_area("Notes")
            
            submit = st.form_submit_button("Add Medication")
            
            if submit:
                if med_name:
                    # Create medication data
                    med_data = {
                        "name": med_name,
                        "dosage": dosage,
                        "frequency": custom_frequency if frequency == "Other" else frequency,
                        "timing": timing,
                        "start_date": str(start_date),
                        "end_date": str(end_date) if end_date else "",
                        "instructions": instructions,
                        "notes": notes,
                        "status": "Active"
                    }
                    
                    # Add medication
                    add_medication(
                        patient_id=patient_id,
                        data=med_data,
                        created_by=st.session_state.user['username']
                    )
                    
                    st.success(f"Medication '{med_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a medication name.")
    
    # Display current medications
    st.subheader("Current Medications")
    
    if medications:
        # Filter active/inactive medications
        show_active = st.checkbox("Show Active Medications Only", value=True)
        
        if show_active:
            filtered_meds = [m for m in medications if m["data"].get("status", "Active") == "Active"]
        else:
            filtered_meds = medications
        
        if filtered_meds:
            # Create tabs for each medication
            med_tabs = st.tabs([f"{m['data']['name']} ({m['data']['dosage']})" for m in filtered_meds])
            
            for i, med in enumerate(filtered_meds):
                with med_tabs[i]:
                    med_data = med["data"]
                    
                    # Display medication details
                    cols = st.columns(2)
                    
                    with cols[0]:
                        st.markdown(f"**Medication**: {med_data['name']}")
                        st.markdown(f"**Dosage**: {med_data['dosage']}")
                        st.markdown(f"**Frequency**: {med_data['frequency']}")
                        st.markdown(f"**Timing**: {', '.join(med_data['timing'])}")
                    
                    with cols[1]:
                        st.markdown(f"**Start Date**: {med_data['start_date']}")
                        if med_data.get('end_date'):
                            st.markdown(f"**End Date**: {med_data['end_date']}")
                        else:
                            st.markdown("**End Date**: Ongoing")
                        st.markdown(f"**Status**: {med_data.get('status', 'Active')}")
                    
                    if med_data.get('instructions'):
                        st.markdown(f"**Special Instructions**: {med_data['instructions']}")
                    
                    if med_data.get('notes'):
                        st.markdown(f"**Notes**: {med_data['notes']}")
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if med_data.get('status', 'Active') == 'Active':
                            if st.button(f"Mark as Inactive", key=f"deactivate_{med['id']}", use_container_width=True):
                                update_medication(med['id'], {"status": "Inactive"})
                                st.success(f"Medication '{med_data['name']}' marked as inactive.")
                                st.rerun()
                        else:
                            if st.button(f"Mark as Active", key=f"activate_{med['id']}", use_container_width=True):
                                update_medication(med['id'], {"status": "Active"})
                                st.success(f"Medication '{med_data['name']}' marked as active.")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"Delete Medication", key=f"delete_{med['id']}", use_container_width=True):
                            delete_medication(med['id'])
                            st.success(f"Medication '{med_data['name']}' deleted.")
                            st.rerun()
        else:
            st.info("No active medications found. Add a medication using the form above.")
    else:
        st.info("No medications found for this patient. Add a medication using the form above.")
    
    # Medication schedule visualization
    if medications:
        st.subheader("Medication Schedule")
        
        # Create a daily schedule view
        st.markdown("### Daily Schedule")
        
        # Define time periods
        time_periods = ["Morning", "Afternoon", "Evening", "Before bed"]
        meal_times = ["Before meals", "With meals", "After meals"]
        
        # Group medications by time period
        schedule = {period: [] for period in time_periods + meal_times}
        
        for med in medications:
            if med["data"].get("status", "Active") == "Active":
                for timing in med["data"]["timing"]:
                    if timing in schedule:
                        schedule[timing].append(med["data"])
        
        # Display the schedule
        for period in time_periods:
            if schedule[period]:
                st.markdown(f"**{period}**")
                for med in schedule[period]:
                    st.markdown(f"- {med['name']} ({med['dosage']}) - {med['frequency']}")
            
        st.markdown("**Meal-Related Medications**")
        for period in meal_times:
            if schedule[period]:
                st.markdown(f"*{period}*")
                for med in schedule[period]:
                    st.markdown(f"- {med['name']} ({med['dosage']}) - {med['frequency']}")
        
        # Create a weekly calendar view if there are weekly medications
        weekly_meds = [m for m in medications if m["data"].get("status", "Active") == "Active" and "weekly" in m["data"]["frequency"].lower()]
        
        if weekly_meds:
            st.markdown("### Weekly Schedule")
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            for med in weekly_meds:
                st.markdown(f"**{med['data']['name']}** ({med['data']['dosage']}) - {med['data']['frequency']}")
    
    # Medication adherence section
    if st.session_state.user['role'] == 'patient' and medications:
        st.subheader("Medication Adherence")
        st.markdown("""
        Tracking how well you follow your medication schedule can help improve your health outcomes.
        Use this section to log when you take your medications.
        """)
        
        active_meds = [m for m in medications if m["data"].get("status", "Active") == "Active"]
        
        if active_meds:
            # Allow user to mark medications as taken
            st.markdown("### Mark Medications as Taken")
            
            # Get current date
            today = datetime.now().date()
            selected_date = st.date_input("Date", value=today, max_value=today)
            
            # Group by timing
            timing_groups = {}
            for med in active_meds:
                for timing in med["data"]["timing"]:
                    if timing not in timing_groups:
                        timing_groups[timing] = []
                    timing_groups[timing].append(med)
            
            # Display each timing group
            for timing, meds in timing_groups.items():
                st.markdown(f"**{timing}**")
                for med in meds:
                    medication_taken = st.checkbox(
                        f"{med['data']['name']} ({med['data']['dosage']})",
                        key=f"adherence_{med['id']}_{selected_date}_{timing}"
                    )
                    
                    if medication_taken:
                        # Here we would record this in an adherence database
                        # For now, just display a confirmation
                        st.success(f"Marked {med['data']['name']} as taken for {timing} on {selected_date}")

def main():
    # Initialize notification-related session state
    if 'last_notification_check' not in st.session_state:
        st.session_state.last_notification_check = datetime.now() - timedelta(minutes=10)  # Check on first load
    
    # Initialize wellness score view
    if 'show_wellness' not in st.session_state:
        st.session_state.show_wellness = False

    # Check if user is logged in
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # Sidebar with navigation
    with st.sidebar:
        st.title("🩺 HealthAssist AI")
        st.caption(f"Logged in as: {st.session_state.user['name']} ({st.session_state.user['role'].capitalize()})")
        
        # Show notifications in sidebar for logged-in users
        if st.session_state.logged_in:
            # Check for new notifications periodically
            current_time = datetime.now()
            if (current_time - st.session_state.last_notification_check).total_seconds() > 300:  # 5 minutes
                if st.session_state.user['role'] == 'patient':
                    # Get patient data for personalized notifications
                    patients = get_all_patients()
                    patient_data = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
                    
                    # Generate health notifications
                    create_scheduled_health_notifications(st.session_state.user['username'], patient_data)
                    
                    # Update last check time
                    st.session_state.last_notification_check = current_time
            
            # Display notifications
            show_notifications(st.session_state.user['username'], location="sidebar")
        
        # Navigation based on user role
        st.header("Navigation")
        
        # Common navigation items for all users
        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state.current_view = 'home'
            st.rerun()
        
        # Patient-specific navigation
        if st.session_state.user['role'] == 'patient':
            if st.button("🚨 Emergency Button", key="nav_emergency", use_container_width=True, 
                       type="primary"):
                st.session_state.current_view = 'emergency'
                st.rerun()
                
            if st.button("🤖 My Health Buddy", key="nav_buddy", use_container_width=True,
                      type="secondary"):
                st.session_state.current_view = 'health_buddy'
                st.rerun()
                
            if st.button("🔔 Notifications", key="nav_notifications", use_container_width=True,
                      type="secondary"):
                st.session_state.current_view = 'notifications'
                st.rerun()
                
            if st.button("📊 Wellness Score", key="nav_wellness", use_container_width=True,
                      type="secondary"):
                st.session_state.current_view = 'wellness_score'
                st.rerun()
                
            st.markdown("---")  # Separator
            
            if st.button("My Health Dashboard", key="nav_dashboard", use_container_width=True):
                st.session_state.current_view = 'patient_dashboard'
                st.rerun()
            
            if st.button("My Health Profile", key="nav_profile", use_container_width=True):
                st.session_state.current_view = 'patient_profile'
                st.rerun()
            
            if st.button("Symptom Checker", key="nav_symptom", use_container_width=True):
                st.session_state.current_view = 'symptom_checker'
                st.rerun()
            
            if st.button("Medical Q&A", key="nav_qa", use_container_width=True):
                st.session_state.current_view = 'medical_qa'
                st.rerun()
            
            if st.button("Care Recommendations", key="nav_care", use_container_width=True):
                st.session_state.current_view = 'care_recommendations'
                st.rerun()
            
            if st.button("Medication Tracker", key="nav_meds", use_container_width=True):
                st.session_state.current_view = 'medication_tracker'
                st.rerun()
        
        # Doctor-specific navigation
        elif st.session_state.user['role'] == 'doctor':
            if st.button("Patient List", key="nav_patients", use_container_width=True):
                st.session_state.current_view = 'doctor_patient_list'
                st.rerun()
            
            if st.button("Medical Records", key="nav_records", use_container_width=True):
                st.session_state.current_view = 'patient_records'
                st.rerun()
            
            if st.button("Patient Medications", key="nav_meds", use_container_width=True):
                st.session_state.current_view = 'medication_tracker'
                st.rerun()
        
        # Admin-specific navigation
        elif st.session_state.user['role'] == 'admin':
            if st.button("Admin Panel", key="nav_admin", use_container_width=True):
                st.session_state.current_view = 'admin_panel'
                st.rerun()
            
            if st.button("Patient Management", key="nav_patients", use_container_width=True):
                st.session_state.current_view = 'doctor_patient_list'
                st.rerun()
            
            if st.button("Medical Records", key="nav_records", use_container_width=True):
                st.session_state.current_view = 'patient_records'
                st.rerun()
            
            if st.button("Medication Management", key="nav_meds", use_container_width=True):
                st.session_state.current_view = 'medication_tracker'
                st.rerun()
        
        # Logout button
        if st.button("Logout", key="nav_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.current_view = 'home'
            st.rerun()
    
    # Main content based on current view
    if st.session_state.current_view == 'home':
        st.title("🩺 HealthAssist AI")
        st.subheader(f"Welcome, {st.session_state.user['name']}!")
        
        # Role-specific welcome message
        if st.session_state.user['role'] == 'patient':
            # Emergency button at the top
            st.markdown("### Emergency Services")
            if st.button("🚨 ONE-TAP EMERGENCY ALERT", use_container_width=True, type="primary"):
                st.session_state.current_view = 'emergency'
                st.rerun()
            
            st.info("In case of emergency, use this button to alert your contacts and share your location")
            
            st.markdown("---")
            
            st.markdown("""
            Welcome to your personal healthcare assistant! With HealthAssist AI, you can:
            
            - 📊 Track your health metrics and visualize trends
            - 🔍 Check your symptoms and get potential causes
            - ❓ Ask medical questions and get reliable answers
            - 📋 Receive personalized care recommendations
            - 💊 Track your medications and set reminders
            - 🚨 Send emergency alerts with location sharing
            - 🤖 Chat with your Health Buddy for support and motivation
            
            Get started by clicking on any of the options in the sidebar.
            """)
            
            # Quick access cards
            st.subheader("Quick Access")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔍 Check My Symptoms", use_container_width=True):
                    st.session_state.current_view = 'symptom_checker'
                    st.rerun()
                
                if st.button("📊 View My Dashboard", use_container_width=True):
                    st.session_state.current_view = 'patient_dashboard'
                    st.rerun()
            
            with col2:
                if st.button("❓ Ask a Medical Question", use_container_width=True):
                    st.session_state.current_view = 'medical_qa'
                    st.rerun()
                
                if st.button("📋 Get Care Recommendations", use_container_width=True):
                    st.session_state.current_view = 'care_recommendations'
                    st.rerun()
            
            with col3:
                if st.button("💊 Medication Tracker", use_container_width=True):
                    st.session_state.current_view = 'medication_tracker'
                    st.rerun()
                
                if st.button("🤖 My Health Buddy", use_container_width=True):
                    st.session_state.current_view = 'health_buddy'
                    st.rerun()
            
            # Health tips
            st.subheader("Daily Health Tip")
            health_tips = [
                "Stay hydrated by drinking at least 8 glasses of water daily.",
                "Aim for 7-9 hours of quality sleep each night.",
                "Include at least 30 minutes of moderate exercise in your daily routine.",
                "Maintain a balanced diet rich in fruits, vegetables, and whole grains.",
                "Practice mindfulness or meditation to reduce stress levels.",
                "Keep track of your medications and take them as prescribed by your doctor.",
                "Regular health check-ups can help detect potential issues early."
            ]
            st.info(random.choice(health_tips))
            
        elif st.session_state.user['role'] == 'doctor':
            st.markdown("""
            Welcome to the physician portal! As a doctor, you can:
            
            - 👨‍👩‍👧‍👦 View and manage your patient list
            - 📝 Add and access patient medical records
            - 📊 View patient health dashboards and metrics
            - 📑 Create treatment plans and prescriptions
            - 💊 Manage patient medications and track adherence
            
            Use the sidebar to navigate between different sections.
            """)
            
            # Quick access
            st.subheader("Quick Access")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("👨‍👩‍👧‍👦 View Patient List", use_container_width=True):
                    st.session_state.current_view = 'doctor_patient_list'
                    st.rerun()
            
            with col2:
                if st.button("💊 Manage Medications", use_container_width=True):
                    st.session_state.current_view = 'medication_tracker'
                    st.rerun()
        
        elif st.session_state.user['role'] == 'admin':
            st.markdown("""
            Welcome to the administration portal! As an administrator, you can:
            
            - 👨‍💼 Manage system users (patients, doctors, admins)
            - 📊 View system statistics and usage metrics
            - ⚙️ Configure system settings and backup data
            - 👨‍👩‍👧‍👦 Access patient records and management
            - 💊 Oversee medication management across the system
            
            Use the sidebar to navigate between different sections.
            """)
            
            # Quick access
            st.subheader("Quick Access")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("👨‍💼 Go to Admin Panel", use_container_width=True):
                    st.session_state.current_view = 'admin_panel'
                    st.rerun()
            
            with col2:
                if st.button("👨‍👩‍👧‍👦 Patient Management", use_container_width=True):
                    st.session_state.current_view = 'doctor_patient_list'
                    st.rerun()
    
    elif st.session_state.current_view == 'patient_dashboard':
        show_patient_dashboard()
    
    elif st.session_state.current_view == 'patient_profile':
        show_patient_profile()
    
    elif st.session_state.current_view == 'medication_tracker':
        show_medication_tracker()
    
    elif st.session_state.current_view == 'emergency':
        show_emergency_page()
    
    elif st.session_state.current_view == 'health_buddy':
        # Get patient data if available (for personalized buddy experience)
        patient_data = None
        if st.session_state.user['role'] == 'patient':
            patients = get_all_patients()
            patient_data = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        
        # Get the user's buddy for notifications
        buddy_data = get_user_buddy(st.session_state.user['username'])
        
        # Show the health buddy page
        show_health_buddy_page(st.session_state.user['username'], patient_data)
    
    elif st.session_state.current_view == 'notifications':
        # Get patient data if available (for personalized notifications)
        patient_data = None
        if st.session_state.user['role'] == 'patient':
            patients = get_all_patients()
            patient_data = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        
        # Get the user's buddy for buddy-related notifications
        buddy_data = get_user_buddy(st.session_state.user['username'])
        
        # Show the notification center
        show_notification_center(st.session_state.user['username'], patient_data, buddy_data)
    
    elif st.session_state.current_view == 'wellness_score':
        # Get patient data if available (for personalized wellness score)
        patient_data = None
        if st.session_state.user['role'] == 'patient':
            patients = get_all_patients()
            patient_data = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        
        # Show the wellness score page
        show_wellness_score_page(st.session_state.user['username'], patient_data)
    
    elif st.session_state.current_view == 'symptom_checker':
        # Insert your symptom checker code here
        st.header("🔍 Symptom Checker")
        st.markdown("""
        The Symptom Checker helps you understand what might be causing your symptoms. 
        Please provide information about your symptoms and health background for a more accurate assessment.
        
        **Note**: This tool is for informational purposes only and does not provide a medical diagnosis.
        """)
        
        # Implementation of symptom checker would go here
        # Using the imported code from all_in_one_app.py
        
        # Featured symptom categories for easier selection
        symptom_categories = {
            "Respiratory": ["Cough", "Shortness of breath", "Sore throat", "Runny nose", "Congestion", "Wheezing"],
            "Digestive": ["Abdominal pain", "Nausea", "Vomiting", "Diarrhea", "Constipation", "Bloating", "Heartburn"],
            "Neurological": ["Headache", "Dizziness", "Fatigue", "Confusion", "Memory problems", "Seizures"],
            "Cardiovascular": ["Chest pain", "Heart palpitations", "Swelling in legs", "High blood pressure", "Irregular heartbeat"],
            "Musculoskeletal": ["Joint pain", "Back pain", "Muscle weakness", "Stiffness", "Swelling", "Neck pain"],
            "Skin": ["Rash", "Itching", "Hives", "Skin discoloration", "Bruising", "Dry skin"]
        }
        
        # Show category tabs
        if 'active_symptom_category' not in st.session_state:
            st.session_state.active_symptom_category = "All Symptoms"
        
        categories = ["All Symptoms"] + list(symptom_categories.keys())
        category_cols = st.columns(len(categories))
        
        for i, category in enumerate(categories):
            with category_cols[i]:
                if st.button(category, use_container_width=True, 
                            type="primary" if category == st.session_state.active_symptom_category else "secondary",
                            key=f"symptom_cat_{i}"):
                    st.session_state.active_symptom_category = category
                    st.rerun()
        
        # Filter symptoms based on selected category
        st.subheader("What symptoms are you experiencing?")
        
        if st.session_state.active_symptom_category == "All Symptoms":
            # Show all symptoms
            display_symptoms = st.session_state.common_symptoms
        else:
            # Show only symptoms from selected category
            display_symptoms = symptom_categories[st.session_state.active_symptom_category]
        
        # Currently selected symptoms (persisted across category changes)
        if 'selected_symptoms_list' not in st.session_state:
            st.session_state.selected_symptoms_list = []
        
        # Allow users to select from filtered symptoms
        selected_symptoms = st.multiselect(
            f"Select symptoms from the {st.session_state.active_symptom_category.lower()}:",
            options=display_symptoms,
            default=[s for s in st.session_state.selected_symptoms_list if s in display_symptoms],
            key="symptom_symptom_select"
        )
        
        # Update the master list of selected symptoms
        # Remove any symptoms that were deselected in this category
        for s in display_symptoms:
            if s in st.session_state.selected_symptoms_list and s not in selected_symptoms:
                st.session_state.selected_symptoms_list.remove(s)
        
        # Add any new symptoms that were selected
        for s in selected_symptoms:
            if s not in st.session_state.selected_symptoms_list:
                st.session_state.selected_symptoms_list.append(s)
        
        # Allow users to add custom symptoms
        st.markdown("#### Add a custom symptom")
        col1, col2 = st.columns([3, 1])
        with col1:
            custom_symptom = st.text_input("Enter a symptom not listed above:", key="symptom_custom")
        with col2:
            if st.button("Add Symptom", use_container_width=True, key="symptom_add_btn") and custom_symptom:
                if custom_symptom not in st.session_state.selected_symptoms_list:
                    st.session_state.selected_symptoms_list.append(custom_symptom)
                    st.success(f"Added: {custom_symptom}")
                    st.rerun()
        
        # Show all currently selected symptoms
        if st.session_state.selected_symptoms_list:
            st.markdown("#### Your selected symptoms:")
            for symptom in st.session_state.selected_symptoms_list:
                st.markdown(f"- {symptom}")
        else:
            st.info("Please select at least one symptom to continue.")
        
        # Additional information
        st.subheader("Additional Information")
        cols = st.columns(2)
        
        with cols[0]:
            symptom_duration = st.selectbox(
                "How long have you had these symptoms?",
                ["Less than 24 hours", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks", "Chronic/Recurring"],
                key="symptom_duration"
            )
            
            symptom_severity = st.select_slider(
                "How severe are your symptoms?",
                options=["Mild", "Moderate", "Severe", "Very Severe"],
                key="symptom_severity"
            )
        
        with cols[1]:
            # Get patient data if available
            patient = None
            patients = get_all_patients()
            if st.session_state.user['role'] == 'patient':
                patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
            elif st.session_state.patient_id:
                patient = get_patient(st.session_state.patient_id)
            
            # Pre-fill with patient data if available
            age = st.number_input("Age", min_value=0, max_value=120, 
                                value=patient['age'] if patient else 0,
                                key="symptom_age_input")
            
            gender_options = ["Male", "Female", "Other"]
            default_gender_index = 0
            
            if patient:
                if patient['gender'] in gender_options:
                    default_gender_index = gender_options.index(patient['gender'])
                
            gender = st.selectbox(
                "Gender", 
                gender_options,
                index=default_gender_index,
                key="symptom_gender_input"
            )
        
        # Medical history
        medical_history = []
        if patient and 'medical_history' in patient:
            medical_history = patient['medical_history']
        
        # Analysis button
        st.markdown("---")
        if st.session_state.selected_symptoms_list:
            analyze_button = st.button("Analyze My Symptoms", type="primary", use_container_width=True, key="symptom_analyze_btn")
            
            if analyze_button:
                with st.spinner("Analyzing your symptoms..."):
                    # Prepare context with all information
                    context = {
                        'symptoms': st.session_state.selected_symptoms_list,
                        'duration': symptom_duration,
                        'severity': symptom_severity,
                        'age': age,
                        'gender': gender,
                        'medical_history': medical_history
                    }
                    
                    # Get analysis
                    analysis = get_symptom_analysis(
                        st.session_state.selected_symptoms_list, 
                        age, 
                        gender, 
                        medical_history
                    )
                    
                    # Display results
                    st.success("Analysis complete!")
                    st.subheader("Symptom Analysis Results")
                    
                    st.markdown(analysis)
                    
                    # Save as health record if patient exists
                    if st.session_state.patient_id and st.session_state.user['role'] in ['doctor', 'admin']:
                        record_data = {
                            "symptoms": ", ".join(st.session_state.selected_symptoms_list),
                            "duration": symptom_duration,
                            "severity": symptom_severity,
                            "analysis": analysis
                        }
                        
                        add_health_record(
                            patient_id=st.session_state.patient_id,
                            record_type="Symptom Analysis",
                            data=record_data,
                            created_by=st.session_state.user['username']
                        )
                        
                        st.success("Analysis saved to patient records")
                    
                    # Medical disclaimer
                    st.info("""
                    **Important**: This analysis is for informational purposes only and is not a substitute for professional 
                    medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified 
                    health provider with any questions you may have regarding a medical condition.
                    """)
        else:
            st.warning("Please select at least one symptom to continue.")
        
        # Emergency warning
        st.error("""
        **Emergency Warning**: If you are experiencing severe chest pain, difficulty breathing, 
        severe bleeding, or any other life-threatening symptoms, please call emergency services 
        (911 in the US) immediately or go to your nearest emergency room.
        """)
    
    elif st.session_state.current_view == 'medical_qa':
        # Insert your medical Q&A code here
        st.header("❓ Medical Q&A")
        st.markdown("""
        Ask any health-related questions and get reliable answers based on medical knowledge.
        Our AI assistant can provide information on symptoms, conditions, treatments, and general health advice.
        
        **Note**: This is not a substitute for professional medical advice. For serious concerns,
        please consult with a healthcare provider.
        """)
        
        # Chat interface
        st.subheader("Ask a Medical Question")
        
        # Display previous chat history
        if 'qa_history' not in st.session_state:
            st.session_state.qa_history = []
        
        for i, exchange in enumerate(st.session_state.qa_history):
            with st.chat_message("user"):
                st.write(exchange['question'])
            with st.chat_message("assistant", avatar="🩺"):
                st.write(exchange['answer'])
        
        # Input for new question
        user_question = st.chat_input("Type your medical question here...")
        
        if user_question:
            # Display user question
            with st.chat_message("user"):
                st.write(user_question)
            
            # Process and display AI response
            with st.chat_message("assistant", avatar="🩺"):
                with st.spinner("Researching medical information..."):
                    # Get user info if available
                    user_info = None
                    if st.session_state.patient_id:
                        patient = get_patient(st.session_state.patient_id)
                        if patient:
                            user_info = {
                                'age': patient['age'],
                                'gender': patient['gender'],
                                'medical_history': patient.get('medical_history', [])
                            }
                    
                    # Get response
                    response = get_medical_qa_response(user_question, user_info)
                    
                    st.write(response)
                    
                    # Add to chat history
                    st.session_state.qa_history.append({
                        'question': user_question,
                        'answer': response,
                        'timestamp': str(datetime.now())
                    })
        
        # Create a more organized topic selection area
        st.subheader("Popular Health Topics")
        
        # Group topics by category for better organization
        topic_categories = {
            "Common Conditions": [
                "What are the symptoms of the common cold vs. flu?",
                "How can I manage seasonal allergies?",
                "What should I know about high blood pressure?",
                "What are the warning signs of diabetes?"
            ],
            "Wellness & Prevention": [
                "How much physical activity do I need each week?",
                "How can I improve my sleep quality?",
                "What are the best foods for heart health?",
                "How can I reduce stress naturally?"
            ],
            "Medical Guidance": [
                "What are the recommended vaccines for adults?",
                "When should I go to the ER vs. urgent care?",
                "How often should I get health screenings?",
                "What questions should I ask my doctor during a check-up?"
            ]
        }
        
        # Create tabs for topic categories
        topic_tabs = st.tabs(list(topic_categories.keys()))
        
        # Display topics in each tab
        for i, (category, topics) in enumerate(topic_categories.items()):
            with topic_tabs[i]:
                st.write(f"Click on any {category.lower()} topic to learn more:")
                
                # Create a grid of buttons
                cols = st.columns(2)
                for j, topic in enumerate(topics):
                    with cols[j % 2]:
                        if st.button(topic, key=f"topic_{category}_{j}", use_container_width=True):
                            # This will be caught on the next rerun and displayed
                            with st.chat_message("user"):
                                st.write(topic)
                            
                            # Process and display AI response
                            with st.chat_message("assistant", avatar="🩺"):
                                with st.spinner("Researching medical information..."):
                                    # Get user info if available
                                    user_info = None
                                    if st.session_state.patient_id:
                                        patient = get_patient(st.session_state.patient_id)
                                        if patient:
                                            user_info = {
                                                'age': patient['age'],
                                                'gender': patient['gender'],
                                                'medical_history': patient.get('medical_history', [])
                                            }
                                    
                                    # Get response
                                    response = get_medical_qa_response(topic, user_info)
                                    
                                    st.write(response)
                                    
                                    # Add to chat history
                                    st.session_state.qa_history.append({
                                        'question': topic,
                                        'answer': response,
                                        'timestamp': str(datetime.now())
                                    })
        
        # Medical disclaimer
        st.markdown("---")
        st.info("""
        **Medical Disclaimer**: The information provided is not intended to be a substitute for 
        professional medical advice, diagnosis, or treatment. Always seek the advice of your 
        physician or other qualified health provider with any questions you may have regarding 
        a medical condition.
        """)
    
    elif st.session_state.current_view == 'care_recommendations':
        # Insert your care recommendations code here
        st.header("📋 Personalized Care Recommendations")
        st.markdown("""
        Get personalized health recommendations based on your symptoms, medical history, and lifestyle.
        This tool provides tailored advice to help you manage your health effectively.
        
        **Note**: These recommendations are personalized but not a substitute for professional medical advice.
        """)
        
        # Get patient data if available
        patient = None
        if st.session_state.user['role'] == 'patient':
            patients = get_all_patients()
            patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        elif st.session_state.patient_id:
            patient = get_patient(st.session_state.patient_id)
        
        if not patient:
            st.warning("Patient profile not found. Please complete your profile first.")
            if st.button("Create Patient Profile"):
                st.session_state.current_view = 'patient_profile'
                st.rerun()
            return
        
        # User health profile form
        with st.expander("Your Health Profile", expanded=True):
            st.subheader("Basic Information")
            cols = st.columns(2)
            
            with cols[0]:
                age = patient['age']
                st.info(f"**Age**: {age} years")
            
            with cols[1]:
                gender = patient['gender']
                st.info(f"**Gender**: {gender}")
            
            st.subheader("Current Symptoms")
            symptoms = st.multiselect(
                "Select any current symptoms:",
                options=st.session_state.common_symptoms,
                default=patient.get('current_symptoms', []),
                key="care_symptoms_select"
            )
            
            st.subheader("Medical History")
            # Display existing medical history
            if patient.get('medical_history'):
                st.info("**Medical History**: " + ", ".join(patient['medical_history']))
            
            # Additional medical conditions
            additional_conditions = st.multiselect(
                "Select any additional medical conditions:",
                ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Cancer", "Autoimmune Disorder", "Thyroid Disorder", "Other"],
                default=[],
                key="care_additional_conditions"
            )
            
            # Combine existing and additional conditions
            medical_history = list(set(patient.get('medical_history', []) + additional_conditions))
            
            st.subheader("Medications")
            # Display existing medications
            if patient.get('medications'):
                st.info("**Current Medications**: " + ", ".join(patient['medications']))
            
            # Additional medications
            additional_medications = st.text_area(
                "List any additional medications (one per line):",
                value="",
                key="care_additional_medications"
            )
            additional_medications_list = [med.strip() for med in additional_medications.split("\n") if med.strip()]
            
            # Combine existing and additional medications
            medications_list = list(set(patient.get('medications', []) + additional_medications_list))
            
            st.subheader("Lifestyle Factors")
            lifestyle = {}
            
            cols = st.columns(2)
            lifestyle_fields = get_lifestyle_fields()
            
            for i, (field, default_value) in enumerate(lifestyle_fields.items()):
                current_value = patient.get('lifestyle', {}).get(field, default_value)
                with cols[i % 2]:
                    if field == "Exercise":
                        lifestyle[field] = st.selectbox(
                            f"{field}:",
                            ["None", "Light (1-2 days/week)", "Moderate (3-4 days/week)", "Active (5+ days/week)"],
                            index=["None", "Light (1-2 days/week)", "Moderate (3-4 days/week)", "Active (5+ days/week)"].index(current_value) if current_value in ["None", "Light (1-2 days/week)", "Moderate (3-4 days/week)", "Active (5+ days/week)"] else 0,
                            key=f"care_exercise_{i}"
                        )
                    elif field == "Diet":
                        lifestyle[field] = st.selectbox(
                            f"{field}:",
                            ["Standard/Mixed", "Vegetarian", "Vegan", "Keto", "Low-carb", "Mediterranean", "Other"],
                            index=["Standard/Mixed", "Vegetarian", "Vegan", "Keto", "Low-carb", "Mediterranean", "Other"].index(current_value) if current_value in ["Standard/Mixed", "Vegetarian", "Vegan", "Keto", "Low-carb", "Mediterranean", "Other"] else 0,
                            key=f"care_diet_{i}"
                        )
                    elif field == "Sleep":
                        lifestyle[field] = st.selectbox(
                            f"{field}:",
                            ["Less than 6 hours", "6-7 hours", "7-8 hours", "8+ hours", "Poor quality", "Irregular"],
                            index=["Less than 6 hours", "6-7 hours", "7-8 hours", "8+ hours", "Poor quality", "Irregular"].index(current_value) if current_value in ["Less than 6 hours", "6-7 hours", "7-8 hours", "8+ hours", "Poor quality", "Irregular"] else 0,
                            key=f"care_sleep_{i}"
                        )
                    elif field == "Stress level":
                        lifestyle[field] = st.selectbox(
                            f"{field}:",
                            ["Low", "Moderate", "High", "Very high"],
                            index=["Low", "Moderate", "High", "Very high"].index(current_value) if current_value in ["Low", "Moderate", "High", "Very high"] else 0,
                            key=f"care_stress_{i}"
                        )
                    elif field == "Smoking":
                        lifestyle[field] = st.selectbox(
                            f"{field}:",
                            ["Non-smoker", "Former smoker", "Light smoker", "Heavy smoker"],
                            index=["Non-smoker", "Former smoker", "Light smoker", "Heavy smoker"].index(current_value) if current_value in ["Non-smoker", "Former smoker", "Light smoker", "Heavy smoker"] else 0,
                            key=f"care_smoking_{i}"
                        )
                    elif field == "Alcohol consumption":
                        lifestyle[field] = st.selectbox(
                            f"{field}:",
                            ["None", "Occasional", "Moderate", "Heavy"],
                            index=["None", "Occasional", "Moderate", "Heavy"].index(current_value) if current_value in ["None", "Occasional", "Moderate", "Heavy"] else 0,
                            key=f"care_alcohol_{i}"
                        )
                    else:
                        lifestyle[field] = st.text_input(f"{field}:", value=current_value, key=f"care_other_{i}")
        
        # Get recommendations button
        st.markdown("---")
        generate_button = st.button("Generate Care Recommendations", type="primary", use_container_width=True, key="care_generate_btn")
        
        if generate_button:
            with st.spinner("Generating personalized care recommendations..."):
                # Get personalized recommendations
                recommendations = get_care_recommendations(
                    symptoms,
                    age,
                    gender,
                    medical_history,
                    lifestyle
                )
                
                # Display recommendations
                st.success("Recommendations generated!")
                st.subheader("Your Personalized Care Recommendations")
                
                st.markdown(recommendations)
                
                # Save to patient record if doctor/admin
                if st.session_state.user['role'] in ['doctor', 'admin']:
                    record_data = {
                        "symptoms": symptoms,
                        "medical_history": medical_history,
                        "lifestyle_factors": lifestyle,
                        "recommendations": recommendations
                    }
                    
                    add_health_record(
                        patient_id=patient['id'],
                        record_type="Care Recommendations",
                        data=record_data,
                        created_by=st.session_state.user['username']
                    )
                    
                    st.success("Recommendations saved to patient records")
                
                # Update patient data with new information
                patient_updates = {
                    "current_symptoms": symptoms,
                    "medical_history": medical_history,
                    "medications": medications_list,
                    "lifestyle": lifestyle
                }
                
                update_patient(patient['id'], patient_updates)
                
                # Medical disclaimer
                st.info("""
                **Medical Disclaimer**: These recommendations are intended for informational purposes only and are 
                not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of 
                your physician or other qualified health provider with any questions you may have regarding a medical condition.
                """)
    
    elif st.session_state.current_view == 'doctor_patient_list':
        show_doctor_patient_list()
    
    elif st.session_state.current_view == 'admin_panel':
        show_admin_panel()
    
    elif st.session_state.current_view == 'patient_records':
        show_patient_records()
    
    elif st.session_state.current_view == 'registration':
        show_registration_page()

# Run the app
if __name__ == "__main__":
    main()