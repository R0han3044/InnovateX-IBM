import streamlit as st
import os
from utils.llm_utils import initialize_llm_chain
from utils.medical_data import load_common_symptoms, load_common_conditions

# Page configuration
st.set_page_config(
    page_title="HealthAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'openai_client' not in st.session_state:
    st.session_state.openai_client = initialize_llm_chain()

if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': '',
        'age': None,
        'gender': '',
        'medical_history': [],
        'current_symptoms': [],
        'medications': []
    }

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'common_symptoms' not in st.session_state:
    st.session_state.common_symptoms = load_common_symptoms()

if 'common_conditions' not in st.session_state:
    st.session_state.common_conditions = load_common_conditions()

# Application header
st.title("🩺 HealthAssist AI")
st.markdown("### Your AI-powered healthcare assistant")

# Set demo mode by default for public use
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True
    st.session_state.openai_client = "DEMO_MODE"

# Main page content
st.markdown("""
Welcome to HealthAssist AI, your personal healthcare assistant powered by artificial intelligence. 
This application provides several tools to help you manage your health:

- **Symptom Checker**: Analyze your symptoms and get potential conditions
- **Medical Q&A**: Ask health-related questions and get reliable answers
- **Personalized Care**: Receive tailored health recommendations
- **Health Dashboard**: Visualize your health data and track progress
""")

# User profile sidebar
with st.sidebar:
    st.header("User Profile")
    
    # User information form
    with st.expander("Personal Information", expanded=True):
        st.session_state.user_data['name'] = st.text_input("Name", st.session_state.user_data['name'])
        st.session_state.user_data['age'] = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.user_data['age'] if st.session_state.user_data['age'] else 0)
        st.session_state.user_data['gender'] = st.selectbox("Gender", ['', 'Male', 'Female', 'Non-binary', 'Prefer not to say'], index=0 if not st.session_state.user_data['gender'] else ['', 'Male', 'Female', 'Non-binary', 'Prefer not to say'].index(st.session_state.user_data['gender']))
    
    # Navigation
    st.header("Navigation")
    navigation = st.radio(
        "Go to:",
        ["Home", "Symptom Checker", "Medical Q&A", "Care Recommendations", "Health Dashboard", "User Profile"]
    )

# Main page routing
if navigation == "Home":
    # Display main page content (already shown above)
    
    # Quick access cards
    st.subheader("Quick Access")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Check My Symptoms", use_container_width=True):
            navigation = "Symptom Checker"
            st.rerun()
    
    with col2:
        if st.button("❓ Ask a Medical Question", use_container_width=True):
            navigation = "Medical Q&A"
            st.rerun()
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📋 Get Care Recommendations", use_container_width=True):
            navigation = "Care Recommendations"
            st.rerun()
    
    with col4:
        if st.button("📊 View Health Dashboard", use_container_width=True):
            navigation = "Health Dashboard"
            st.rerun()

    # Health tips section
    st.subheader("Daily Health Tip")
    health_tips = [
        "Stay hydrated by drinking at least 8 glasses of water daily.",
        "Aim for 7-9 hours of quality sleep each night.",
        "Include at least 30 minutes of moderate exercise in your daily routine.",
        "Maintain a balanced diet rich in fruits, vegetables, and whole grains.",
        "Practice mindfulness or meditation to reduce stress levels."
    ]
    import random
    st.info(random.choice(health_tips))

    # Disclaimer
    st.markdown("---")
    st.caption("""
    **Disclaimer**: HealthAssist AI is designed to provide general health information and is not a substitute for professional medical advice, 
    diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have 
    regarding a medical condition.
    """)

elif navigation == "Symptom Checker":
    from pages.symptom_checker import show_symptom_checker
    show_symptom_checker()

elif navigation == "Medical Q&A":
    from pages.medical_qa import show_medical_qa
    show_medical_qa()

elif navigation == "Care Recommendations":
    from pages.care_recommendations import show_care_recommendations
    show_care_recommendations()

elif navigation == "Health Dashboard":
    from pages.patient_dashboard import show_patient_dashboard
    show_patient_dashboard()
    
elif navigation == "User Profile":
    from pages.user_profile import show_user_profile
    show_user_profile()
