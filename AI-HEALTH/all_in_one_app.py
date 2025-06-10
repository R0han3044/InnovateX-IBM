import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="HealthAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set demo mode by default for public use
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

# Initialize session state variables if they don't exist
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': '',
        'age': None,
        'gender': '',
        'medical_history': [],
        'current_symptoms': [],
        'medications': [],
        'lifestyle': {}
    }

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []

if 'previous_recommendations' not in st.session_state:
    st.session_state.previous_recommendations = []

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

# ----- Load Data -----
if 'common_symptoms' not in st.session_state:
    st.session_state.common_symptoms = load_common_symptoms()

if 'common_conditions' not in st.session_state:
    st.session_state.common_conditions = load_common_conditions()

# ----- AI Response Functions -----
def get_symptom_analysis(symptoms, age, gender, medical_history):
    """Generate a symptom analysis response"""
    if not symptoms:
        return "Please provide at least one symptom for analysis."
    
    context = f"""
    The user is a {age}-year-old {gender} with the following symptoms: {', '.join(symptoms)}.
    Medical history: {', '.join(medical_history) if medical_history else 'None provided'}.
    """
    return get_demo_response("symptoms analysis", context)

def get_medical_qa_response(question, user_info=None):
    """Generate a medical Q&A response"""
    if not question:
        return "Please ask a medical question to receive a response."
    
    context = ""
    if user_info:
        context = f"""
        User information:
        - Age: {user_info.get('age', 'Not provided')}
        - Gender: {user_info.get('gender', 'Not provided')}
        - Medical history: {', '.join(user_info.get('medical_history', [])) if user_info.get('medical_history') else 'None provided'}
        """
    
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

# ----- Main Application -----
# Application header
st.title("🩺 HealthAssist AI")
st.markdown("### Your AI-powered healthcare assistant")

# Sidebar for user profile and navigation
with st.sidebar:
    # User profile in sidebar
    st.header("User Profile")
    
    # User information form
    with st.expander("Personal Information", expanded=True):
        st.session_state.user_data['name'] = st.text_input("Name", st.session_state.user_data['name'], key="sidebar_name")
        st.session_state.user_data['age'] = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.user_data.get('age', 0) or 0, key="sidebar_age")
        st.session_state.user_data['gender'] = st.selectbox("Gender", 
            ['', 'Male', 'Female', 'Non-binary', 'Prefer not to say'], 
            index=0 if not st.session_state.user_data.get('gender') else ['', 'Male', 'Female', 'Non-binary', 'Prefer not to say'].index(st.session_state.user_data.get('gender')),
            key="sidebar_gender")
    
    # Navigation
    st.header("Navigation")
    navigation = st.radio(
        "Go to:",
        ["Home", "Symptom Checker", "Medical Q&A", "Care Recommendations", "Health Dashboard", "User Profile"],
        key="navigation"
    )

# ----- Main Page Content -----

if navigation == "Home":
    # Main page content
    st.markdown("""
    Welcome to HealthAssist AI, your personal healthcare assistant powered by artificial intelligence. 
    This application provides several tools to help you manage your health:
    
    - **Symptom Checker**: Analyze your symptoms and get potential conditions
    - **Medical Q&A**: Ask health-related questions and get reliable answers
    - **Personalized Care**: Receive tailored health recommendations
    - **Health Dashboard**: Visualize your health data and track progress
    """)
    
    # Quick access cards
    st.subheader("Quick Access")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Check My Symptoms", use_container_width=True, key="home_symptom_btn"):
            st.session_state['navigation'] = "Symptom Checker"
            st.rerun()
    
    with col2:
        if st.button("❓ Ask a Medical Question", use_container_width=True, key="home_qa_btn"):
            st.session_state['navigation'] = "Medical Q&A"
            st.rerun()
    
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📋 Get Care Recommendations", use_container_width=True, key="home_care_btn"):
            st.session_state['navigation'] = "Care Recommendations"
            st.rerun()
    
    with col4:
        if st.button("📊 View Health Dashboard", use_container_width=True, key="home_dashboard_btn"):
            st.session_state['navigation'] = "Health Dashboard"
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
    st.info(random.choice(health_tips))
    
    # Disclaimer
    st.markdown("---")
    st.caption("""
    **Disclaimer**: HealthAssist AI is designed to provide general health information and is not a substitute for professional medical advice, 
    diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have 
    regarding a medical condition.
    """)

# ----- Symptom Checker Page -----
elif navigation == "Symptom Checker":
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
        st.session_state.selected_symptoms_list = st.session_state.user_data.get('current_symptoms', [])
    
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
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'type': 'symptom_check',
                    'input': {
                        'symptoms': st.session_state.selected_symptoms_list,
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

# ----- Medical Q&A Page -----
elif navigation == "Medical Q&A":
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
                # Get response
                response = get_medical_qa_response(user_question, st.session_state.user_data)
                
                st.write(response)
                
                # Add to chat history
                st.session_state.qa_history.append({
                    'question': user_question,
                    'answer': response,
                    'timestamp': str(pd.Timestamp.now())
                })
                
                # Add to conversation history for tracking
                st.session_state.conversation_history.append({
                    'type': 'medical_qa',
                    'input': user_question,
                    'output': response,
                    'timestamp': str(pd.Timestamp.now())
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
                        user_question = topic
                        
                        # Display user question
                        with st.chat_message("user"):
                            st.write(user_question)
                        
                        # Process and display AI response
                        with st.chat_message("assistant", avatar="🩺"):
                            with st.spinner("Researching medical information..."):
                                # Get response
                                response = get_medical_qa_response(user_question, st.session_state.user_data)
                                
                                st.write(response)
                                
                                # Add to chat history
                                st.session_state.qa_history.append({
                                    'question': user_question,
                                    'answer': response,
                                    'timestamp': str(pd.Timestamp.now())
                                })
                                
                                # Add to conversation history for tracking
                                st.session_state.conversation_history.append({
                                    'type': 'medical_qa',
                                    'input': user_question,
                                    'output': response,
                                    'timestamp': str(pd.Timestamp.now())
                                })
    
    # Medical disclaimer
    st.markdown("---")
    st.info("""
    **Medical Disclaimer**: The information provided is not intended to be a substitute for 
    professional medical advice, diagnosis, or treatment. Always seek the advice of your 
    physician or other qualified health provider with any questions you may have regarding 
    a medical condition.
    """)

# ----- Care Recommendations Page -----
elif navigation == "Care Recommendations":
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
    generate_button = st.button("Generate Care Recommendations", type="primary", use_container_width=True, key="care_generate_btn")
    
    if generate_button:
        if not age or not gender:
            st.error("Please provide your age and gender to get personalized recommendations.")
        else:
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
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'type': 'care_recommendations',
                    'input': {
                        'user_data': st.session_state.user_data
                    },
                    'output': recommendations,
                    'timestamp': str(pd.Timestamp.now())
                })
                
                # Store in previous recommendations
                if 'previous_recommendations' not in st.session_state:
                    st.session_state.previous_recommendations = []
                
                st.session_state.previous_recommendations.append({
                    'date': str(pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')),
                    'content': recommendations
                })
    
    # Display previous recommendations if they exist
    if 'previous_recommendations' in st.session_state and st.session_state.previous_recommendations and not generate_button:
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

# ----- Health Dashboard Page -----
elif navigation == "Health Dashboard":
    import numpy as np
    
    st.header("📊 Health Dashboard")
    st.markdown("""
    Track your health metrics and visualize your progress over time.
    This dashboard provides an overview of your health data and trends.
    """)
    
    # Check if user profile is complete
    if not st.session_state.user_data.get('name') or not st.session_state.user_data.get('age'):
        st.warning("Please complete your profile information in the sidebar for a personalized dashboard.")
    
    # Initialize health tracking data if not present
    if 'health_data' not in st.session_state:
        # Generate sample health data for visualization purposes
        st.session_state.health_data = generate_sample_health_data(days=30)
    
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
    
    # Weekly summary
    st.subheader("Weekly Summary")
    
    # Group data by week and calculate averages
    filtered_data['week'] = filtered_data['date'].dt.isocalendar().week
    weekly_data = filtered_data.groupby('week').agg({
        'steps': 'mean',
        'sleep_hours': 'mean',
        'heart_rate': 'mean',
        'date': 'min'  # Get the first day of each week
    }).reset_index()
    
    # Weekly comparison chart
    fig_weekly = go.Figure()
    
    # Add traces for each metric
    fig_weekly.add_trace(go.Bar(
        x=weekly_data['date'],
        y=weekly_data['steps'] / 1000,  # Convert to thousands for scale
        name='Steps (thousands)',
        marker_color='blue'
    ))
    
    fig_weekly.add_trace(go.Bar(
        x=weekly_data['date'],
        y=weekly_data['sleep_hours'],
        name='Sleep (hours)',
        marker_color='purple'
    ))
    
    fig_weekly.add_trace(go.Bar(
        x=weekly_data['date'],
        y=weekly_data['heart_rate'] / 10,  # Scale down for visibility
        name='Heart Rate (tens)',
        marker_color='red'
    ))
    
    fig_weekly.update_layout(
        title='Weekly Health Metrics Comparison',
        xaxis_title='Week Starting',
        yaxis_title='Value (Scaled)',
        barmode='group',
        hovermode="x unified"
    )
    
    st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Health insights based on data
    st.subheader("Health Insights")
    
    # Calculate some basic insights
    steps_trend = filtered_data['steps'].iloc[-7:].mean() - filtered_data['steps'].iloc[-14:-7].mean()
    sleep_trend = filtered_data['sleep_hours'].iloc[-7:].mean() - filtered_data['sleep_hours'].iloc[-14:-7].mean()
    hr_trend = filtered_data['heart_rate'].iloc[-7:].mean() - filtered_data['heart_rate'].iloc[-14:-7].mean()
    
    # Display insights based on trends
    insights = []
    
    if steps_trend > 500:
        insights.append("✅ **Physical Activity**: Your daily steps have increased recently. Great job staying active!")
    elif steps_trend < -500:
        insights.append("❗ **Physical Activity**: Your daily steps have decreased. Try to incorporate more walking into your day.")
    else:
        insights.append("ℹ️ **Physical Activity**: Your step count has been relatively stable.")
    
    if sleep_trend > 0.5:
        insights.append("✅ **Sleep**: You've been sleeping more hours recently, which is beneficial for your health.")
    elif sleep_trend < -0.5:
        insights.append("❗ **Sleep**: Your sleep duration has decreased. Aim for 7-9 hours of sleep per night.")
    else:
        insights.append("ℹ️ **Sleep**: Your sleep pattern has been consistent.")
    
    if hr_trend < -2:
        insights.append("✅ **Heart Health**: Your resting heart rate has decreased, which may indicate improving fitness.")
    elif hr_trend > 2:
        insights.append("❗ **Heart Health**: Your resting heart rate has increased. Monitor this trend and consider consulting a healthcare provider if it continues.")
    else:
        insights.append("ℹ️ **Heart Health**: Your resting heart rate has been stable.")
    
    # Add general insight based on overall data
    if avg_steps > 10000 and avg_sleep > 7.5 and avg_heart_rate < 70:
        insights.append("🌟 **Overall Health**: Your metrics suggest excellent health habits. Keep up the good work!")
    elif avg_steps < 5000 and avg_sleep < 6.5:
        insights.append("❗ **Overall Health**: Your metrics suggest room for improvement in physical activity and sleep.")
    else:
        insights.append("ℹ️ **Overall Health**: Your health metrics are within typical ranges, but there's always room for improvement.")
    
    # Display insights
    for insight in insights:
        st.markdown(insight)
    
    # Health recommendations
    st.subheader("Recommendations")
    
    # Generate recommendations based on metrics
    recommendations = []
    
    if avg_steps < 8000:
        recommendations.append("🚶‍♂️ Aim to increase your daily steps to at least 10,000 steps per day.")
    
    if avg_sleep < 7:
        recommendations.append("😴 Try to improve your sleep duration by establishing a regular sleep schedule.")
    
    if avg_heart_rate > 75:
        recommendations.append("❤️ Consider incorporating more cardiovascular exercise to improve your heart health.")
    
    # Add general recommendations
    recommendations.extend([
        "💧 Stay hydrated by drinking at least 8 glasses of water daily.",
        "🥗 Maintain a balanced diet rich in fruits, vegetables, and whole grains.",
        "🧘‍♀️ Practice stress-reduction techniques like meditation or deep breathing exercises."
    ])
    
    # Display recommendations
    for recommendation in recommendations:
        st.markdown(recommendation)
    
    # Data disclaimer
    st.markdown("---")
    st.caption("""
    **Note**: This dashboard uses simulated health data for demonstration purposes. 
    In a real application, this would be replaced with actual data from wearable devices, 
    health apps, or manual entries.
    """)

# ----- User Profile Page -----
elif navigation == "User Profile":
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
    
    # Personal Information tab
    with tabs[0]:
        st.subheader("Personal Information")
        
        # Personal information form
        with st.form("personal_info_form", clear_on_submit=False):
            name = st.text_input("Full Name", st.session_state.user_data.get('name', ''), key="profile_name")
            
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.user_data.get('age', 0) or 0, key="profile_age")
                height = st.number_input("Height (cm)", min_value=0, max_value=250, value=st.session_state.user_data.get('height', 0) or 0, key="profile_height")
            
            with col2:
                gender = st.selectbox(
                    "Gender", 
                    ["", "Male", "Female", "Non-binary", "Prefer not to say"],
                    index=0 if not st.session_state.user_data.get('gender') else ["", "Male", "Female", "Non-binary", "Prefer not to say"].index(st.session_state.user_data.get('gender')),
                    key="profile_gender"
                )
                weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=st.session_state.user_data.get('weight', 0) or 0, key="profile_weight")
            
            email = st.text_input("Email Address", st.session_state.user_data.get('email', ''), help="Used for account identification", key="profile_email")
            
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
                
                st.success("Profile information updated!")
                st.session_state.user_profile_saved = True
        
        # Display saved profile
        if st.session_state.user_data.get('name'):
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
    
    # Medical History tab
    with tabs[1]:
        st.subheader("Medical History")
        
        # Medical conditions
        medical_history = st.multiselect(
            "Select any medical conditions you have:",
            ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Cancer", "Autoimmune Disorder", "Thyroid Disorder", "Other"],
            default=st.session_state.user_data.get('medical_history', []),
            key="profile_medical_history"
        )
        
        # Medications
        medications = st.text_area(
            "List any current medications (one per line):",
            value="\n".join(st.session_state.user_data.get('medications', [])) if st.session_state.user_data.get('medications') else "",
            key="profile_medications"
        )
        medications_list = [med.strip() for med in medications.split("\n") if med.strip()]
        
        # Allergies
        allergies = st.text_area(
            "List any allergies (one per line):",
            value="\n".join(st.session_state.user_data.get('allergies', [])) if st.session_state.user_data.get('allergies') else "",
            key="profile_allergies"
        )
        allergies_list = [allergy.strip() for allergy in allergies.split("\n") if allergy.strip()]
        
        # Save button
        if st.button("Save Medical History", type="primary", key="profile_save_medical"):
            # Update session state
            st.session_state.user_data.update({
                'medical_history': medical_history,
                'medications': medications_list,
                'allergies': allergies_list
            })
            
            st.success("Medical history updated!")
        
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
    
    # Account Settings tab
    with tabs[2]:
        st.subheader("Account Settings")
        
        # Display session information
        st.markdown("**Session Information**")
        st.info("🔒 Your data is stored securely in your current browser session only.")
        
        # Data import/export
        st.markdown("### Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Health Data", use_container_width=True, key="profile_export"):
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
                    mime="text/csv",
                    key="profile_download_csv"
                )
        
        with col2:
            uploaded_file = st.file_uploader("Import Health Data", type="csv", key="profile_upload")
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
        
        if st.button("Clear Session Data", type="secondary", key="profile_clear"):
            # Reset session data
            st.session_state.user_data = {
                'name': '',
                'age': None,
                'gender': '',
                'medical_history': [],
                'current_symptoms': [],
                'medications': []
            }
            
            st.success("Session data cleared successfully!")
            st.rerun()