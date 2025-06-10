import streamlit as st
from datetime import datetime
from utils.health_data import HealthDataManager

def show_symptom_checker():
    """Display the symptom checker interface"""
    st.title("🔍 AI Symptom Checker")
    st.write("Get general guidance about your symptoms using AI analysis")
    
    # Important disclaimer
    st.error("""
    ⚠️ **IMPORTANT MEDICAL DISCLAIMER**
    
    This symptom checker is for informational purposes only and should NOT be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions you may have regarding a medical condition.
    
    **Seek immediate medical attention if you experience:**
    - Severe chest pain or difficulty breathing
    - Signs of stroke (sudden numbness, confusion, severe headache)
    - Severe allergic reactions
    - High fever with severe symptoms
    - Any emergency medical situation
    """)
    
    # Check if model is loaded
    if not st.session_state.model_loaded or not st.session_state.model_manager:
        st.error("🤖 AI Model not loaded. Please load the model first.")
        return
    
    st.markdown("---")
    
    # Symptom input form
    with st.form("symptom_form"):
        st.subheader("📝 Describe Your Symptoms")
        
        # Primary symptoms
        primary_symptoms = st.text_area(
            "Primary symptoms (describe in detail):",
            placeholder="e.g., headache, fever, cough, stomach pain, fatigue...",
            height=100
        )
        
        # Duration
        col1, col2 = st.columns(2)
        with col1:
            symptom_duration = st.selectbox(
                "How long have you had these symptoms?",
                ["Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"]
            )
        
        with col2:
            severity = st.selectbox(
                "Symptom severity:",
                ["Mild", "Moderate", "Severe"]
            )
        
        # Additional information
        st.subheader("🏥 Additional Information")
        
        col1, col2 = st.columns(2)
        with col1:
            age_group = st.selectbox(
                "Age group:",
                ["Under 18", "18-30", "31-50", "51-65", "Over 65"]
            )
        
        with col2:
            has_conditions = st.checkbox("I have existing medical conditions")
        
        if has_conditions:
            medical_conditions = st.text_area(
                "Existing medical conditions:",
                placeholder="e.g., diabetes, hypertension, asthma..."
            )
        else:
            medical_conditions = ""
        
        current_medications = st.text_area(
            "Current medications (optional):",
            placeholder="List any medications you're currently taking..."
        )
        
        additional_info = st.text_area(
            "Any additional relevant information:",
            placeholder="Recent travel, exposure to illness, family history, etc."
        )
        
        # Submit button
        submit_button = st.form_submit_button("🔍 Analyze Symptoms", type="primary")
        
        if submit_button:
            if primary_symptoms.strip():
                analyze_symptoms(
                    primary_symptoms,
                    symptom_duration,
                    severity,
                    age_group,
                    medical_conditions,
                    current_medications,
                    additional_info
                )
            else:
                st.warning("Please describe your primary symptoms.")
    
    # Common symptoms quick check
    st.markdown("---")
    st.subheader("🎯 Quick Symptom Checks")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤒 Fever & Cold Symptoms"):
            quick_symptom_check("fever, runny nose, sore throat, body aches")
    
    with col2:
        if st.button("🤕 Headache & Pain"):
            quick_symptom_check("headache, neck pain, light sensitivity")
    
    with col3:
        if st.button("😷 Digestive Issues"):
            quick_symptom_check("nausea, stomach pain, digestive discomfort")

def analyze_symptoms(primary_symptoms, duration, severity, age_group, medical_conditions, medications, additional_info):
    """Analyze symptoms using AI"""
    
    # Prepare patient context
    patient_context = {
        "age_group": age_group,
        "duration": duration,
        "severity": severity,
        "medical_conditions": medical_conditions,
        "medications": medications,
        "additional_info": additional_info
    }
    
    # Create detailed prompt
    patient_info = f"""
    Patient Information:
    - Age group: {age_group}
    - Symptom duration: {duration}
    - Severity: {severity}
    """
    
    if medical_conditions:
        patient_info += f"\n- Existing conditions: {medical_conditions}"
    
    if medications:
        patient_info += f"\n- Current medications: {medications}"
    
    if additional_info:
        patient_info += f"\n- Additional info: {additional_info}"
    
    # Show analysis loading
    with st.spinner("Analyzing symptoms with AI..."):
        try:
            # Get AI analysis using demo model
            from utils.model_utils_demo import DemoModelManager
            demo_model = DemoModelManager()
            analysis = demo_model.symptom_analysis(
                primary_symptoms,
                patient_info
            )
            
            # Display results
            display_symptom_analysis(primary_symptoms, analysis, patient_context)
            
            # Save to health records
            save_symptom_record(primary_symptoms, analysis, patient_context)
            
        except Exception as e:
            st.error(f"Error analyzing symptoms: {str(e)}")

def quick_symptom_check(symptoms):
    """Quick symptom analysis for common issues"""
    with st.spinner("Quick analysis..."):
        try:
            from utils.model_utils_demo import DemoModelManager
            demo_model = DemoModelManager()
            analysis = demo_model.symptom_analysis(symptoms)
            
            st.subheader("Quick Analysis Results")
            st.write(analysis)
            
            st.info("For a more detailed analysis, use the full symptom checker form above.")
            
        except Exception as e:
            st.error(f"Error in quick analysis: {str(e)}")

def display_symptom_analysis(symptoms, analysis, context):
    """Display the symptom analysis results"""
    st.success("✅ Analysis Complete")
    
    # Analysis results
    st.subheader("🔍 AI Analysis Results")
    
    # Display the AI analysis
    st.write(analysis)
    
    # Action recommendations
    st.markdown("---")
    st.subheader("📋 Recommended Actions")
    
    # Determine urgency based on severity and symptoms
    severity = context.get("severity", "Mild")
    
    if severity == "Severe" or any(word in symptoms.lower() for word in ["chest pain", "difficulty breathing", "severe headache", "high fever"]):
        st.error("🚨 **URGENT: Seek immediate medical attention**")
        st.write("Your symptoms may require immediate medical evaluation. Contact emergency services or go to the nearest emergency room.")
    elif severity == "Moderate":
        st.warning("⚠️ **Consider seeing a healthcare provider**")
        st.write("Your symptoms should be evaluated by a healthcare professional, especially if they persist or worsen.")
    else:
        st.info("💡 **Monitor symptoms and consider self-care**")
        st.write("Continue monitoring your symptoms. If they worsen or persist, consider consulting a healthcare provider.")
    
    # General recommendations
    st.markdown("---")
    st.subheader("🏠 General Self-Care Tips")
    
    recommendations = [
        "Rest and get adequate sleep",
        "Stay well hydrated",
        "Eat nutritious foods",
        "Monitor your temperature regularly",
        "Keep a symptom diary",
        "Avoid strenuous activities if feeling unwell"
    ]
    
    for rec in recommendations:
        st.write(f"• {rec}")
    
    # When to seek help
    st.markdown("---")
    st.subheader("🏥 When to Seek Medical Help")
    
    warning_signs = [
        "Symptoms worsen significantly",
        "New concerning symptoms develop",
        "Fever exceeds 103°F (39.4°C)",
        "Difficulty breathing or chest pain",
        "Severe dehydration",
        "Symptoms persist beyond expected duration"
    ]
    
    for sign in warning_signs:
        st.write(f"• {sign}")

def save_symptom_record(symptoms, analysis, context):
    """Save symptom check to health records"""
    try:
        health_manager = HealthDataManager()
        
        record_data = {
            "type": "symptom_check",
            "symptoms": symptoms,
            "analysis": analysis,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        success = health_manager.add_health_record(
            st.session_state.username,
            record_data
        )
        
        if success:
            st.success("📝 Symptom check saved to your health records")
        
    except Exception as e:
        st.warning(f"Could not save to health records: {str(e)}")

# Emergency contacts section
def show_emergency_contacts():
    """Display emergency contact information"""
    st.markdown("---")
    st.subheader("🚨 Emergency Contacts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Emergency Services:**")
        st.write("• Emergency: 911")
        st.write("• Poison Control: 1-800-222-1222")
        st.write("• Crisis Text Line: Text HOME to 741741")
    
    with col2:
        st.write("**Mental Health Support:**")
        st.write("• National Suicide Prevention Lifeline: 988")
        st.write("• Crisis Text Line: Text HOME to 741741")
        st.write("• SAMHSA Helpline: 1-800-662-4357")

# Show emergency contacts at the bottom
show_emergency_contacts()
