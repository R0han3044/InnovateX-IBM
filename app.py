import streamlit as st
import torch
import os
import json
from datetime import datetime
import sys

# Import utility modules
from utils.model_utils import ModelManager
from utils.auth_utils import AuthManager
from utils.health_data import HealthDataManager

# Page imports
import pages.chat as chat_page
import pages.symptom_checker as symptom_page
import pages.wellness_dashboard as wellness_page
import pages.patient_management as patient_page
import pages.notifications as notifications_page

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'model_loaded' not in st.session_state:
        st.session_state.model_loaded = False
    if 'model_manager' not in st.session_state:
        st.session_state.model_manager = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def check_colab_environment():
    """Check if running in Google Colab and setup accordingly"""
    try:
        import google.colab
        st.info("🔧 Running in Google Colab environment detected")
        
        # Check if ngrok is configured
        try:
            from pyngrok import ngrok
            active_tunnels = ngrok.get_tunnels()
            if not active_tunnels:
                st.warning("⚠️ No ngrok tunnel detected. You may need to set up ngrok for external access.")
        except:
            st.warning("⚠️ Ngrok not configured. External access may be limited.")
            
        return True
    except ImportError:
        return False

def display_system_info():
    """Display system information"""
    with st.expander("🔧 System Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Environment:**")
            st.write(f"Python: {sys.version.split()[0]}")
            
            # Check GPU
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                st.write(f"GPU: {gpu_name}")
                st.write(f"GPU Memory: {gpu_memory:.1f} GB")
            else:
                st.write("GPU: Not available")
        
        with col2:
            st.write("**Model Status:**")
            if st.session_state.model_loaded:
                st.success("✅ IBM Granite Model Loaded")
            else:
                st.error("❌ Model Not Loaded")
            
            st.write("**Authentication:**")
            if st.session_state.authenticated:
                st.success(f"✅ Logged in as: {st.session_state.username}")
            else:
                st.error("❌ Not authenticated")

def login_page():
    """Display login page"""
    st.title("🏥 HealthAssist AI")
    st.subheader("Advanced Healthcare Assistant with IBM Granite AI")
    
    # Check if running in Colab
    is_colab = check_colab_environment()
    
    # Display system info
    display_system_info()
    
    st.markdown("---")
    
    # Login form
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
    
    # Default accounts info
    with st.expander("📋 Demo Accounts"):
        st.write("**Available Demo Accounts:**")
        st.write("- Admin: `admin` / `admin123`")
        st.write("- Doctor: `doctor` / `doctor123`")
        st.write("- Patient: `patient` / `patient123`")
    
    # Model loading section
    st.markdown("---")
    st.subheader("🤖 IBM Granite Model")
    
    if not st.session_state.model_loaded:
        if st.button("🚀 Load IBM Granite Model", type="primary"):
            load_model()
    else:
        st.success("✅ IBM Granite 3.3-2b-instruct model is ready!")
        if st.button("🔄 Reload Model"):
            st.session_state.model_loaded = False
            st.session_state.model_manager = None
            st.rerun()

def load_model():
    """Load the IBM Granite model"""
    with st.spinner("Loading IBM Granite 3.3-2b-instruct model... This may take a few minutes."):
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing model manager...")
            progress_bar.progress(10)
            
            model_manager = ModelManager()
            
            status_text.text("Downloading model files...")
            progress_bar.progress(30)
            
            success = model_manager.load_model()
            progress_bar.progress(100)
            
            if success:
                st.session_state.model_manager = model_manager
                st.session_state.model_loaded = True
                status_text.text("Model loaded successfully!")
                st.success("🎉 IBM Granite model loaded successfully!")
                st.rerun()
            else:
                status_text.text("Failed to load model")
                st.error("❌ Failed to load the model. Please check the error messages above.")
                
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")

def main_app():
    """Main application interface"""
    # Sidebar navigation
    with st.sidebar:
        st.title("🏥 HealthAssist AI")
        st.write(f"Welcome, {st.session_state.username}!")
        st.write(f"Role: {st.session_state.user_role.title()}")
        
        # Model status
        if st.session_state.model_loaded:
            st.success("🤖 AI Model Ready")
        else:
            st.error("🤖 AI Model Not Loaded")
            if st.button("Load Model"):
                load_model()
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "💬 AI Chat": "chat",
            "🔍 Symptom Checker": "symptom_checker",
            "📊 Wellness Dashboard": "wellness",
            "👥 Patient Management": "patients",
            "🔔 Notifications": "notifications"
        }
        
        # Filter pages based on user role
        if st.session_state.user_role == "patient":
            # Patients can't access patient management
            pages = {k: v for k, v in pages.items() if v != "patients"}
        
        selected_page = st.selectbox("Navigate to:", list(pages.keys()))
        page_key = pages[selected_page]
        
        st.markdown("---")
        
        # System info
        with st.expander("System Info"):
            if torch.cuda.is_available():
                st.write(f"🔥 GPU: {torch.cuda.get_device_name(0)}")
                st.write(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            else:
                st.write("💻 Running on CPU")
        
        # Logout
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_role = None
            st.rerun()
    
    # Main content area
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
    st.set_page_config(
        page_title="HealthAssist AI",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
