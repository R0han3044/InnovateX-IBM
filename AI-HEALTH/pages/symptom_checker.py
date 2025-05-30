import streamlit as st
import pandas as pd
from utils.llm_utils import get_symptom_analysis

def show_symptom_checker():
    """
    Display the symptom checker page where users can input symptoms
    and receive potential conditions and recommendations.
    """
    st.header("🔍 Symptom Checker")
    st.markdown("""
    The Symptom Checker helps you understand what might be causing your symptoms. 
    Please provide information about your symptoms and health background for a more accurate assessment.
    
    **Note**: This tool is for informational purposes only and does not provide a medical diagnosis.
    """)
    
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
            if st.button(category, use_container_width=True, type="secondary" if category != st.session_state.active_symptom_category else "primary"):
                st.session_state.active_symptom_category = category
                st.rerun()
    
    # Filter symptoms based on selected category
    st.subheader("What symptoms are you experiencing?")
    
    if st.session_state.active_symptom_category == "All Symptoms":
        # Show all symptoms
        common_symptoms = st.session_state.common_symptoms
        display_symptoms = common_symptoms
    else:
        # Show only symptoms from selected category
        display_symptoms = symptom_categories[st.session_state.active_symptom_category]
    
    # Currently selected symptoms (persisted across category changes)
    if 'selected_symptoms_list' not in st.session_state:
        st.session_state.selected_symptoms_list = st.session_state.user_data.get('current_symptoms', [])
    
    # Allow users to select from filtered symptoms
    selected_symptoms = st.multiselect(
        f"Select symptoms from the {st.session_state.active_symptom_category.lower()}:",
        options=display_symptoms,
        default=[s for s in st.session_state.selected_symptoms_list if s in display_symptoms]
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
        custom_symptom = st.text_input("Enter a symptom not listed above:")
    with col2:
        if st.button("Add Symptom", use_container_width=True) and custom_symptom:
            if custom_symptom not in st.session_state.selected_symptoms_list:
                st.session_state.selected_symptoms_list.append(custom_symptom)
                st.success(f"Added: {custom_symptom}")
                st.rerun()
    
    # Show all currently selected symptoms
    if st.session_state.selected_symptoms_list:
        st.markdown("#### Your selected symptoms:")
        for symptom in st.session_state.selected_symptoms_list:
            st.markdown(f"- {symptom} " + 
                     f"<small>[Remove](javascript:void)</small>", unsafe_allow_html=True)
    else:
        st.info("Please select at least one symptom to continue.")
    
    # Update session state
    st.session_state.user_data['current_symptoms'] = st.session_state.selected_symptoms_list
    
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
        # These fields should be pre-filled if the user already entered them in the user profile
        age = st.number_input("Age", min_value=0, max_value=120, 
                             value=st.session_state.user_data.get('age', 0) or 0,
                             key="symptom_age_input")
        
        gender_options = ["Male", "Female", "Non-binary", "Prefer not to say"]
        default_gender_index = 3  # Default to "Prefer not to say"
        
        if st.session_state.user_data.get('gender') in gender_options:
            default_gender_index = gender_options.index(st.session_state.user_data.get('gender'))
            
        gender = st.selectbox(
            "Gender", 
            gender_options,
            index=default_gender_index,
            key="symptom_gender_input"
        )
    
    # Medical history (pre-fill from session state if available)
    medical_history = st.multiselect(
        "Do you have any of these medical conditions?",
        ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Cancer", "Autoimmune Disorder", "Thyroid Disorder", "Other"],
        default=st.session_state.user_data.get('medical_history', []),
        key="symptom_medical_history"
    )
    
    # Update session state with user info
    st.session_state.user_data['age'] = age
    st.session_state.user_data['gender'] = gender
    st.session_state.user_data['medical_history'] = medical_history
    
    # Analysis button
    st.markdown("---")
    if selected_symptoms:
        analyze_button = st.button("Analyze My Symptoms", type="primary", use_container_width=True)
        
        if analyze_button:
            with st.spinner("Analyzing your symptoms..."):
                # Prepare context with all information
                context = {
                    'symptoms': selected_symptoms,
                    'duration': symptom_duration,
                    'severity': symptom_severity,
                    'age': age,
                    'gender': gender,
                    'medical_history': medical_history
                }
                
                # Get analysis from LLM
                analysis = get_symptom_analysis(
                    selected_symptoms, 
                    age, 
                    gender, 
                    medical_history
                )
                
                # Display results
                st.success("Analysis complete!")
                st.subheader("Symptom Analysis Results")
                
                st.markdown(analysis)
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'type': 'symptom_check',
                    'input': {
                        'symptoms': selected_symptoms,
                        'context': context
                    },
                    'output': analysis,
                    'timestamp': str(pd.Timestamp.now())
                })
                
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
