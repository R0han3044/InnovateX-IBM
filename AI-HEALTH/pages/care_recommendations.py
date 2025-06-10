import streamlit as st
import pandas as pd
from utils.llm_utils import get_care_recommendations
from utils.medical_data import get_lifestyle_fields

def show_care_recommendations():
    """
    Display the Personalized Care Recommendations page where users
    can get tailored health advice based on their profile and symptoms.
    """
    st.header("📋 Personalized Care Recommendations")
    st.markdown("""
    Get personalized health recommendations based on your symptoms, medical history, and lifestyle.
    This tool provides tailored advice to help you manage your health effectively.
    
    **Note**: These recommendations are personalized but not a substitute for professional medical advice.
    """)
    
    # Check if we have basic user information
    if not st.session_state.user_data.get('age') or not st.session_state.user_data.get('gender'):
        st.warning("Please complete your profile information in the sidebar to get personalized recommendations.")
    
    # Initialize lifestyle fields if not already present
    if 'lifestyle' not in st.session_state.user_data:
        st.session_state.user_data['lifestyle'] = get_lifestyle_fields()
    
    # User health profile form
    with st.expander("Your Health Profile", expanded=True):
        st.subheader("Basic Information")
        cols = st.columns(2)
        
        with cols[0]:
            age = st.number_input("Age", min_value=0, max_value=120, 
                                value=st.session_state.user_data.get('age', 0) or 0,
                                key="care_age_input")
        
        with cols[1]:
            gender_options = ["Male", "Female", "Non-binary", "Prefer not to say"]
            default_gender_index = 3  # Default to "Prefer not to say"
            
            if st.session_state.user_data.get('gender') in gender_options:
                default_gender_index = gender_options.index(st.session_state.user_data.get('gender'))
                
            gender = st.selectbox(
                "Gender", 
                gender_options,
                index=default_gender_index,
                key="care_gender_input"
            )
        
        st.subheader("Current Symptoms")
        symptoms = st.multiselect(
            "Select any current symptoms:",
            options=st.session_state.common_symptoms,
            default=st.session_state.user_data.get('current_symptoms', []),
            key="care_symptoms_select"
        )
        
        st.subheader("Medical History")
        medical_history = st.multiselect(
            "Select any medical conditions you have:",
            ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Cancer", "Autoimmune Disorder", "Thyroid Disorder", "Other"],
            default=st.session_state.user_data.get('medical_history', []),
            key="care_medical_history"
        )
        
        st.subheader("Medications")
        medications = st.text_area(
            "List any current medications (one per line):",
            value="\n".join(st.session_state.user_data.get('medications', [])) if st.session_state.user_data.get('medications') else "",
            key="care_medications_input"
        )
        medications_list = [med.strip() for med in medications.split("\n") if med.strip()]
        
        st.subheader("Lifestyle Factors")
        lifestyle = {}
        
        cols = st.columns(2)
        lifestyle_fields = get_lifestyle_fields()
        
        for i, (field, default_value) in enumerate(lifestyle_fields.items()):
            current_value = st.session_state.user_data['lifestyle'].get(field, default_value)
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
    
    # Update session state with user info
    st.session_state.user_data['age'] = age
    st.session_state.user_data['gender'] = gender
    st.session_state.user_data['current_symptoms'] = symptoms
    st.session_state.user_data['medical_history'] = medical_history
    st.session_state.user_data['medications'] = medications_list
    st.session_state.user_data['lifestyle'] = lifestyle
    
    # Get recommendations button
    st.markdown("---")
    generate_button = st.button("Generate Care Recommendations", type="primary", use_container_width=True)
    
    if generate_button:
        if not age or not gender:
            st.error("Please provide your age and gender to get personalized recommendations.")
        else:
            with st.spinner("Generating personalized care recommendations..."):
                # Get personalized recommendations from LLM
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
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'type': 'care_recommendations',
                    'input': {
                        'user_data': st.session_state.user_data
                    },
                    'output': recommendations,
                    'timestamp': str(pd.Timestamp.now())
                })
    
    # Display previous recommendations if they exist
    if 'previous_recommendations' not in st.session_state:
        st.session_state.previous_recommendations = []
    
    if st.session_state.previous_recommendations and not generate_button:
        with st.expander("Previous Recommendations", expanded=False):
            for rec in reversed(st.session_state.previous_recommendations[-3:]):
                st.markdown(f"**Date**: {rec['date']}")
                st.markdown(rec['content'])
                st.markdown("---")
    
    # Medical disclaimer
    st.markdown("---")
    st.info("""
    **Medical Disclaimer**: These recommendations are intended for informational purposes only and are 
    not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of 
    your physician or other qualified health provider with any questions you may have regarding a medical condition.
    """)
