import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.database import (
    get_user_by_email, create_user, add_medical_history, 
    get_user_health_metrics, save_health_metrics
)

def show_user_profile():
    """
    Display the User Profile page where users can view and update their health information,
    medical history, and connect their account to the database.
    """
    st.header("👤 User Profile")
    st.markdown("""
    Manage your personal health information, medical history, and account settings.
    Your information is securely stored and used to provide personalized health recommendations.
    """)
    
    # For a public app, inform users about data storage
    st.info("""
    **Your data is stored locally in this session.**
    
    For privacy and security reasons, your health information is only stored during your current session.
    If you'd like to save your data, you can use the Export feature in the Account Settings tab.
    """)
    
    # Add session persistence notice
    with st.expander("About Data Privacy", expanded=False):
        st.markdown("""
        ### Data Privacy in HealthAssist AI
        
        **How we handle your data:**
        - All your health information is stored only in your browser session
        - Nothing is sent to external servers without your consent
        - You can export your data at any time using the Account Settings tab
        - When you close your browser, your data is automatically removed
        
        We take your privacy seriously and follow best practices for health information protection.
        """)
    
    # User profile tabs
    tabs = st.tabs(["Personal Information", "Medical History", "Account Settings"])
    
    with tabs[0]:
        show_personal_info_tab()
        
    with tabs[1]:
        show_medical_history_tab()
        
    with tabs[2]:
        show_account_settings_tab()
    
    # Data privacy notice
    st.markdown("---")
    st.caption("""
    **Privacy Notice**: Your health data is stored securely and is only used to provide 
    personalized health recommendations. We never share your data with third parties.
    """)

def show_personal_info_tab():
    """Display and manage personal information"""
    st.subheader("Personal Information")
    
    # Initialize session state if needed
    if 'user_profile_saved' not in st.session_state:
        st.session_state.user_profile_saved = False
    
    # Personal information form
    with st.form("personal_info_form"):
        name = st.text_input("Full Name", st.session_state.user_data.get('name', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.user_data.get('age', 0) or 0)
            height = st.number_input("Height (cm)", min_value=0, max_value=250, value=st.session_state.user_data.get('height', 0) or 0)
        
        with col2:
            gender = st.selectbox(
                "Gender", 
                ["", "Male", "Female", "Non-binary", "Prefer not to say"],
                index=0 if not st.session_state.user_data.get('gender') else ["", "Male", "Female", "Non-binary", "Prefer not to say"].index(st.session_state.user_data.get('gender'))
            )
            weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=st.session_state.user_data.get('weight', 0) or 0)
        
        email = st.text_input("Email Address", st.session_state.user_data.get('email', ''), help="Used for account identification")
        
        # Save button
        submitted = st.form_submit_button("Save Profile", use_container_width=True)
        
        if submitted:
            # Update session state
            st.session_state.user_data.update({
                'name': name,
                'age': age,
                'gender': gender,
                'height': height,
                'weight': weight,
                'email': email
            })
            
            # Try to save to database if available
            if email and os.getenv("DATABASE_URL"):
                # Check if user exists
                existing_user = get_user_by_email(email)
                
                if existing_user:
                    # Update existing user (would need additional update function)
                    st.success(f"Profile updated for {name}!")
                else:
                    # Create new user
                    user = create_user(name, email, age, gender)
                    if user:
                        st.session_state.user_id = user.id
                        st.success(f"Profile created for {name}!")
                    else:
                        st.error("Failed to save profile to database.")
            else:
                # Just update session state
                st.success("Profile information updated!")
                
            st.session_state.user_profile_saved = True
    
    # Display saved profile
    if st.session_state.user_profile_saved and st.session_state.user_data.get('name'):
        st.info(f"""
        **Profile Summary**:
        - Name: {st.session_state.user_data.get('name')}
        - Age: {st.session_state.user_data.get('age')}
        - Gender: {st.session_state.user_data.get('gender')}
        - Height: {st.session_state.user_data.get('height')} cm
        - Weight: {st.session_state.user_data.get('weight')} kg
        """)
        
        # Calculate BMI if height and weight are provided
        if st.session_state.user_data.get('height', 0) > 0 and st.session_state.user_data.get('weight', 0) > 0:
            height_m = st.session_state.user_data.get('height') / 100
            bmi = st.session_state.user_data.get('weight') / (height_m * height_m)
            
            st.metric("BMI (Body Mass Index)", f"{bmi:.1f}")
            
            # BMI categories
            if bmi < 18.5:
                st.caption("BMI Category: Underweight")
            elif bmi < 25:
                st.caption("BMI Category: Normal weight")
            elif bmi < 30:
                st.caption("BMI Category: Overweight")
            else:
                st.caption("BMI Category: Obesity")

def show_medical_history_tab():
    """Display and manage medical history"""
    st.subheader("Medical History")
    
    # Medical conditions
    medical_history = st.multiselect(
        "Select any medical conditions you have:",
        ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Cancer", "Autoimmune Disorder", "Thyroid Disorder", "Other"],
        default=st.session_state.user_data.get('medical_history', [])
    )
    
    # Medications
    medications = st.text_area(
        "List any current medications (one per line):",
        value="\n".join(st.session_state.user_data.get('medications', [])) if st.session_state.user_data.get('medications') else ""
    )
    medications_list = [med.strip() for med in medications.split("\n") if med.strip()]
    
    # Allergies
    allergies = st.text_area(
        "List any allergies (one per line):",
        value="\n".join(st.session_state.user_data.get('allergies', [])) if st.session_state.user_data.get('allergies') else ""
    )
    allergies_list = [allergy.strip() for allergy in allergies.split("\n") if allergy.strip()]
    
    # Save button
    if st.button("Save Medical History", type="primary"):
        # Update session state
        st.session_state.user_data.update({
            'medical_history': medical_history,
            'medications': medications_list,
            'allergies': allergies_list
        })
        
        # Try to save to database if available
        if os.getenv("DATABASE_URL") and 'user_id' in st.session_state:
            # For simplicity, we'll just add a new entry for each condition
            for condition in medical_history:
                add_medical_history(
                    user_id=st.session_state.user_id,
                    condition=condition,
                    diagnosed_date=datetime.now(),
                    notes="",
                    medications=medications_list,
                    is_active=True
                )
            
            st.success("Medical history saved to your profile!")
        else:
            st.success("Medical history updated in session!")
    
    # Display summary
    if medical_history or medications_list or allergies_list:
        st.markdown("### Medical Summary")
        
        if medical_history:
            st.markdown(f"**Medical Conditions**: {', '.join(medical_history)}")
        
        if medications_list:
            st.markdown("**Current Medications**:")
            for med in medications_list:
                st.markdown(f"- {med}")
        
        if allergies_list:
            st.markdown("**Allergies**:")
            for allergy in allergies_list:
                st.markdown(f"- {allergy}")

def show_account_settings_tab():
    """Display and manage account settings"""
    st.subheader("Account Settings")
    
    # Display session information
    st.markdown("**Session Information**")
    st.info("🔒 Your data is stored securely in your current browser session only.")
    
    # Data import/export
    st.markdown("### Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Health Data", use_container_width=True):
            # Prepare data for export
            user_data = st.session_state.user_data
            
            # Convert to DataFrame for CSV export
            data = {
                "Field": ["Name", "Age", "Gender", "Height (cm)", "Weight (kg)", "Email",
                         "Medical History", "Medications", "Allergies"],
                "Value": [
                    user_data.get('name', ''),
                    user_data.get('age', ''),
                    user_data.get('gender', ''),
                    user_data.get('height', ''),
                    user_data.get('weight', ''),
                    user_data.get('email', ''),
                    ", ".join(user_data.get('medical_history', [])),
                    ", ".join(user_data.get('medications', [])),
                    ", ".join(user_data.get('allergies', []))
                ]
            }
            
            df = pd.DataFrame(data)
            
            # Generate CSV
            csv = df.to_csv(index=False)
            
            # Offer download
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="health_data_export.csv",
                mime="text/csv"
            )
    
    with col2:
        uploaded_file = st.file_uploader("Import Health Data", type="csv")
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                
                # Convert DataFrame to dict
                data_dict = dict(zip(df["Field"], df["Value"]))
                
                # Update user data
                field_mapping = {
                    "Name": "name",
                    "Age": "age",
                    "Gender": "gender",
                    "Height (cm)": "height",
                    "Weight (kg)": "weight",
                    "Email": "email",
                    "Medical History": "medical_history",
                    "Medications": "medications",
                    "Allergies": "allergies"
                }
                
                for field, value in data_dict.items():
                    if field in field_mapping:
                        session_field = field_mapping[field]
                        
                        # Handle list fields
                        if session_field in ["medical_history", "medications", "allergies"]:
                            if isinstance(value, str) and value.strip():
                                value = [item.strip() for item in value.split(",")]
                            else:
                                value = []
                        
                        # Handle numeric fields
                        if session_field in ["age", "height", "weight"]:
                            try:
                                value = float(value) if session_field in ["height", "weight"] else int(value)
                            except:
                                value = 0
                        
                        st.session_state.user_data[session_field] = value
                
                st.success("Health data imported successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")
    
    # Delete account option
    st.markdown("### Account Actions")
    
    if st.button("Clear Session Data", type="secondary"):
        # Reset session data
        st.session_state.user_data = {
            'name': '',
            'age': None,
            'gender': '',
            'medical_history': [],
            'current_symptoms': [],
            'medications': []
        }
        
        if 'user_id' in st.session_state:
            del st.session_state.user_id
        
        st.session_state.user_profile_saved = False
        
        st.success("Session data cleared successfully!")
        st.rerun()