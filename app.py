import streamlit as st

# Set page configuration first before any other Streamlit commands
st.set_page_config(
    page_title="HealthAssist AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import json
from datetime import datetime
import sys
from utils.model_utils_demo import DemoModelManager

# Initialize DemoModelManager
if "model_manager" not in st.session_state or not isinstance(st.session_state.model_manager, DemoModelManager):
    st.session_state.model_manager = DemoModelManager()

# Import utility modules
from utils.auth_utils import AuthManager
from utils.health_data import HealthDataManager

def initialize_session_state():
    """Initialize session state variables"""
    default_state = {
        'authenticated': False,
        'username': None,
        'user_role': None,
        'model_loaded': False,
        'chat_history': []
    }
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

def check_colab_environment():
    """Stubbed Colab check for compatibility (no real effect in VS Code)"""
    return False  # Always false, because we're in VS Code

def display_system_info():
    """Display system information"""
    with st.expander("System Information"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Environment:**")
            st.write(f"Python: {sys.version.split()[0]}")
            st.write("Running on CPU")

        with col2:
            st.write("**Model Status:**")
            if st.session_state.model_loaded:
                st.success("IBM Granite Model Ready")
            else:
                st.info("Model Available for Loading")

            st.write("**Authentication:**")
            if st.session_state.authenticated:
                st.success(f"Logged in as: {st.session_state.username}")
            else:
                st.error("Not authenticated")

def login_page():
    """Display login page"""
    st.title("🏥 HealthAssist AI")
    st.subheader("Advanced Healthcare Assistant with IBM Granite AI")

    is_colab = check_colab_environment()
    display_system_info()
    st.markdown("---")

    with st.form("login_form"):
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            auth_manager = AuthManager()
            if auth_manager.authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = auth_manager.get_user_role(username)
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with st.expander("📋 Demo Accounts"):
        st.write("**Available Demo Accounts:**")
        st.write("- Admin: `admin` / `admin123`")
        st.write("- Doctor: `doctor` / `doctor123`")
        st.write("- Patient: `patient` / `patient123`")

    st.markdown("---")
    st.subheader("🤖 IBM Granite Model")

    if not st.session_state.model_loaded:
        if st.button("🚀 Load IBM Granite Model", type="primary"):
            load_model()
    else:
        st.success("✅ IBM Granite 3.3-2b-instruct model is ready!")
        if st.button("🔄 Reload Model"):
            st.session_state.model_loaded = False
            st.session_state.model_manager = DemoModelManager()
            st.rerun()

def load_model():
    """Simulate loading the IBM Granite model for demo purposes"""
    with st.spinner("Preparing IBM Granite 3.3-2b-instruct model simulation..."):
        import time
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Initializing model simulation...")
        progress_bar.progress(25)
        time.sleep(1)

        status_text.text("Setting up AI capabilities...")
        progress_bar.progress(75)
        time.sleep(1)

        progress_bar.progress(100)
        st.session_state.model_loaded = True
        st.session_state.model_manager = DemoModelManager()
        status_text.text("Model simulation ready!")
        st.success("IBM Granite model simulation loaded successfully!")
        st.rerun()

def main_app():
    """Main application interface"""
    import pages.chat as chat_page
    import pages.symptom_checker as symptom_page
    import pages.wellness_dashboard as wellness_page
    import pages.patient_management as patient_page
    import pages.notifications as notifications_page

    with st.sidebar:
        st.title("🏥 HealthAssist AI")
        st.write(f"Welcome, {st.session_state.username}!")
        st.write(f"Role: {st.session_state.user_role.title()}")

        if st.session_state.model_loaded:
            st.success("🤖 AI Model Ready")
        else:
            st.error("🤖 AI Model Not Loaded")
            if st.button("Load Model"):
                load_model()

        st.markdown("---")

        pages = {
            "💬 AI Chat": "chat",
            "🔍 Symptom Checker": "symptom_checker",
            "📊 Wellness Dashboard": "wellness",
            "👥 Patient Management": "patients",
            "🔔 Notifications": "notifications"
        }

        if st.session_state.user_role == "patient":
            pages = {k: v for k, v in pages.items() if v != "patients"}

        selected_page = st.selectbox("Navigate to:", list(pages.keys()))
        page_key = pages[selected_page]

        st.markdown("---")

        with st.expander("System Info"):
            st.write("Running on CPU")
            st.write("Ready for AI model loading")

        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.rerun()

    if page_key == "chat":
        chat_page.show_chat_page()
    elif page_key == "symptom_checker":
        symptom_page.show_symptom_checker()
    elif page_key == "wellness":
        wellness_page.show_wellness_dashboard()
    elif page_key == "patients":
        patient_page.show_patient_management()
    elif page_key == "notifications":
        notifications_page.show_notifications()

def main():
    """Main application entry point"""
    initialize_session_state()

    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
