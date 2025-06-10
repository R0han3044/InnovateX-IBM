import streamlit as st
import pandas as pd
from datetime import datetime
from utils.health_data import HealthDataManager
from utils.auth_utils import AuthManager

def show_patient_management():
    """Display patient management interface (for doctors/admin)"""
    st.title("👥 Patient Management")
    
    # Check user role
    if st.session_state.user_role not in ["doctor", "admin"]:
        st.error("🚫 Access denied. This section is only available to healthcare providers.")
        return
    
    st.write("Manage patient records and health data")
    
    # Initialize managers
    health_manager = HealthDataManager()
    auth_manager = AuthManager()
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Patient List", "📊 Patient Records", "👤 Add Patient", "📈 Analytics"])
    
    with tab1:
        show_patient_list(auth_manager, health_manager)
    
    with tab2:
        show_patient_records(health_manager)
    
    with tab3:
        show_add_patient(auth_manager)
    
    with tab4:
        show_patient_analytics(health_manager)

def show_patient_list(auth_manager, health_manager):
    """Display list of patients"""
    st.subheader("📋 Patient List")
    
    # Get all patients
    patients = auth_manager.list_users(role_filter="patient")
    
    if not patients:
        st.info("No patients registered in the system.")
        return
    
    # Search and filter
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Search patients:", placeholder="Search by name or username")
    with col2:
        show_all = st.checkbox("Show all details", value=False)
    
    # Filter patients based on search
    if search_term:
        filtered_patients = [
            p for p in patients 
            if search_term.lower() in p.get("name", "").lower() or 
               search_term.lower() in p.get("username", "").lower()
        ]
    else:
        filtered_patients = patients
    
    # Display patients
    for patient in filtered_patients:
        with st.expander(f"👤 {patient.get('name', 'Unknown')} ({patient.get('username', 'N/A')})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Username:** {patient.get('username', 'N/A')}")
                st.write(f"**Email:** {patient.get('email', 'N/A')}")
                st.write(f"**Registered:** {patient.get('created_at', 'N/A')[:10]}")
            
            with col2:
                # Get health summary
                health_summary = health_manager.get_health_metrics_summary(patient.get('username'))
                st.write(f"**Wellness Score:** {health_summary.get('overall_score', 'N/A')}")
                st.write(f"**Trend:** {health_summary.get('trend', 'N/A').title()}")
                st.write(f"**Health Records:** {health_summary.get('total_records', 0)}")
            
            if show_all:
                st.markdown("---")
                st.write("**Detailed Information:**")
                for key, value in patient.items():
                    if key not in ["password"]:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📊 View Records", key=f"records_{patient['username']}"):
                    st.session_state.selected_patient = patient['username']
                    st.rerun()
            
            with col2:
                if st.button(f"💬 Send Message", key=f"message_{patient['username']}"):
                    send_patient_message(patient['username'])
            
            with col3:
                if st.session_state.user_role == "admin":
                    if st.button(f"✏️ Edit", key=f"edit_{patient['username']}"):
                        st.session_state.edit_patient = patient['username']

def show_patient_records(health_manager):
    """Display detailed patient records"""
    st.subheader("📊 Patient Health Records")
    
    # Patient selection
    auth_manager = AuthManager()
    patients = auth_manager.list_users(role_filter="patient")
    
    if not patients:
        st.info("No patients available.")
        return
    
    patient_options = {p['name']: p['username'] for p in patients}
    selected_patient_name = st.selectbox("Select Patient:", list(patient_options.keys()))
    selected_patient = patient_options[selected_patient_name]
    
    # Get patient records
    records = health_manager.get_patient_records(selected_patient)
    wellness_data = health_manager.get_wellness_data(selected_patient)
    
    # Display summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(records))
    
    with col2:
        if wellness_data.get("overall_scores"):
            current_wellness = wellness_data["overall_scores"][-1]
            st.metric("Current Wellness", f"{current_wellness}/100")
    
    with col3:
        recent_records = [r for r in records if 
                         datetime.fromisoformat(r.get("created_at", "2000-01-01")) > 
                         datetime.now() - pd.Timedelta(days=30)]
        st.metric("Recent Records (30d)", len(recent_records))
    
    # Records timeline
    if records:
        st.subheader("📅 Records Timeline")
        
        # Sort records by date
        records_sorted = sorted(records, key=lambda x: x.get("created_at", ""), reverse=True)
        
        for record in records_sorted[:10]:  # Show last 10 records
            record_date = record.get("created_at", "Unknown")[:10]
            record_type = record.get("type", "General").title()
            
            with st.expander(f"{record_date} - {record_type}"):
                for key, value in record.items():
                    if key not in ["username", "record_id"]:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Wellness trends
    if wellness_data.get("dates") and wellness_data.get("overall_scores"):
        st.subheader("📈 Wellness Trends")
        
        # Create simple chart data
        chart_data = pd.DataFrame({
            'Date': wellness_data["dates"][-30:],  # Last 30 days
            'Wellness Score': wellness_data["overall_scores"][-30:]
        })
        
        st.line_chart(chart_data.set_index('Date'))
    
    # AI Analysis (if model is loaded)
    if st.session_state.model_loaded and st.session_state.model_manager:
        st.subheader("🤖 AI Patient Analysis")
        
        if st.button("🔍 Generate Patient Analysis"):
            with st.spinner("Analyzing patient data..."):
                try:
                    # Prepare patient data summary
                    patient_summary = prepare_patient_summary(records, wellness_data)
                    
                    # Get AI analysis
                    analysis = st.session_state.model_manager.wellness_insights(patient_summary)
                    
                    st.success("Analysis Complete")
                    st.write(analysis)
                    
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")

def show_add_patient(auth_manager):
    """Add new patient interface"""
    st.subheader("👤 Add New Patient")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", placeholder="patient_username")
            name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email*", placeholder="patient@email.com")
        
        with col2:
            password = st.text_input("Password*", type="password", placeholder="Temporary password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            phone = st.text_input("Phone", placeholder="(555) 123-4567")
        
        # Additional patient info
        st.subheader("📋 Additional Information")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=0, max_value=150, value=30)
            gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other", "Prefer not to say"])
        
        with col2:
            blood_type = st.selectbox("Blood Type", ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
            emergency_contact = st.text_input("Emergency Contact", placeholder="Name and phone number")
        
        medical_history = st.text_area("Medical History", placeholder="Known conditions, allergies, medications...")
        notes = st.text_area("Notes", placeholder="Additional notes about the patient...")
        
        submit_button = st.form_submit_button("➕ Add Patient", type="primary")
        
        if submit_button:
            # Validation
            if not all([username, name, email, password]):
                st.error("Please fill in all required fields marked with *")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Create patient account
                success, message = auth_manager.create_user(username, password, "patient", name, email)
                
                if success:
                    # Add additional patient information to health records
                    health_manager = HealthDataManager()
                    patient_info = {
                        "type": "patient_registration",
                        "age": age,
                        "gender": gender if gender != "Select" else None,
                        "blood_type": blood_type if blood_type != "Select" else None,
                        "emergency_contact": emergency_contact,
                        "medical_history": medical_history,
                        "notes": notes,
                        "phone": phone
                    }
                    
                    health_manager.add_health_record(username, patient_info)
                    
                    st.success(f"✅ Patient {name} added successfully!")
                    st.info(f"🔑 Login credentials - Username: {username}, Password: {password}")
                    st.info("💡 Please ask the patient to change their password on first login.")
                else:
                    st.error(f"❌ Failed to add patient: {message}")

def show_patient_analytics(health_manager):
    """Show patient analytics and statistics"""
    st.subheader("📈 Patient Analytics")
    
    # Get all patient data
    auth_manager = AuthManager()
    patients = auth_manager.list_users(role_filter="patient")
    
    if not patients:
        st.info("No patient data available for analytics.")
        return
    
    # Calculate statistics
    total_patients = len(patients)
    
    # Get wellness statistics
    wellness_scores = []
    active_patients = 0
    
    for patient in patients:
        wellness_data = health_manager.get_wellness_data(patient['username'])
        if wellness_data.get("overall_scores"):
            wellness_scores.extend(wellness_data["overall_scores"][-7:])  # Last week
            if wellness_data.get("last_updated"):
                last_update = datetime.fromisoformat(wellness_data["last_updated"])
                if (datetime.now() - last_update).days <= 7:
                    active_patients += 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", total_patients)
    
    with col2:
        st.metric("Active Patients (7d)", active_patients)
    
    with col3:
        if wellness_scores:
            avg_wellness = sum(wellness_scores) / len(wellness_scores)
            st.metric("Avg Wellness Score", f"{avg_wellness:.1f}")
        else:
            st.metric("Avg Wellness Score", "N/A")
    
    with col4:
        engagement_rate = (active_patients / total_patients * 100) if total_patients > 0 else 0
        st.metric("Engagement Rate", f"{engagement_rate:.1f}%")
    
    # Wellness distribution
    if wellness_scores:
        st.subheader("📊 Wellness Score Distribution")
        
        # Create bins for wellness scores
        bins = [0, 40, 60, 80, 100]
        labels = ["Poor (0-40)", "Fair (41-60)", "Good (61-80)", "Excellent (81-100)"]
        
        score_counts = [0, 0, 0, 0]
        for score in wellness_scores:
            if score <= 40:
                score_counts[0] += 1
            elif score <= 60:
                score_counts[1] += 1
            elif score <= 80:
                score_counts[2] += 1
            else:
                score_counts[3] += 1
        
        # Display as columns
        cols = st.columns(4)
        colors = ["🔴", "🟡", "🟢", "🟢"]
        
        for i, (label, count, color) in enumerate(zip(labels, score_counts, colors)):
            with cols[i]:
                st.metric(f"{color} {label}", count)
    
    # Recent activity
    st.subheader("📅 Recent Patient Activity")
    
    recent_activity = []
    for patient in patients:
        records = health_manager.get_patient_records(patient['username'])
        for record in records[-3:]:  # Last 3 records per patient
            activity = {
                "Patient": patient.get('name', patient['username']),
                "Activity": record.get('type', 'Unknown').title(),
                "Date": record.get('created_at', 'Unknown')[:10]
            }
            recent_activity.append(activity)
    
    if recent_activity:
        # Sort by date and show recent
        recent_activity.sort(key=lambda x: x['Date'], reverse=True)
        
        activity_df = pd.DataFrame(recent_activity[:20])  # Last 20 activities
        st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("No recent patient activity.")

def send_patient_message(patient_username):
    """Send message to patient (placeholder)"""
    st.info(f"Message feature for {patient_username} - This could integrate with notification system")

def prepare_patient_summary(records, wellness_data):
    """Prepare patient data summary for AI analysis"""
    summary = f"Patient Health Summary:\n"
    summary += f"- Total health records: {len(records)}\n"
    
    if wellness_data.get("overall_scores"):
        recent_scores = wellness_data["overall_scores"][-7:]
        avg_score = sum(recent_scores) / len(recent_scores)
        summary += f"- Average wellness score (last 7 days): {avg_score:.1f}/100\n"
        summary += f"- Current wellness score: {wellness_data['overall_scores'][-1]}/100\n"
    
    # Recent record types
    recent_records = records[-10:] if records else []
    record_types = [r.get("type", "unknown") for r in recent_records]
    summary += f"- Recent record types: {', '.join(set(record_types))}\n"
    
    return summary
