import os
import openai
import streamlit as st
import random

def initialize_llm_chain():
    """
    Initialize the OpenAI client for medical queries.
    """
    # Check if we're in demo mode
    if 'demo_mode' in st.session_state and st.session_state.demo_mode:
        return "DEMO_MODE"
    
    # API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    
    try:
        # Initialize the OpenAI client
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Test the client with a simple request
        if openai_api_key:
            try:
                # Simple test to verify the API key works
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a healthcare assistant."},
                        {"role": "user", "content": "Hello"}
                    ],
                    max_tokens=5
                )
                return client
            except Exception as e:
                st.error(f"Error testing OpenAI connection: {str(e)}")
                return None
        else:
            st.warning("OpenAI API key not found. You can enable demo mode to see example responses.")
            return None
    
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None

def get_llm_response(query, context="", max_retries=3):
    """
    Get a response from the OpenAI model with error handling and retries.
    
    Args:
        query (str): The user's medical query
        context (str): Additional context to help the model provide a better response
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        str: The model's response or an error message
    """
    # Check if we're in demo mode
    if 'openai_client' in st.session_state and st.session_state.openai_client == "DEMO_MODE":
        return get_demo_response(query, context)
    
    # Check if API is configured
    if 'openai_client' not in st.session_state or st.session_state.openai_client is None:
        return "Please add your OpenAI API key in the settings or enable demo mode to use AI features."
    
    # Construct the full prompt with medical guidelines and context
    system_prompt = """
    You are an AI healthcare assistant trained to provide helpful, accurate, and ethical medical information.
    
    Important rules to follow:
    1. Never diagnose specific conditions definitively.
    2. Always suggest consulting with a healthcare professional.
    3. Provide evidence-based information when available.
    4. Be clear about the limitations of AI medical advice.
    5. Focus on education rather than treatment recommendations.
    """
    
    if context:
        system_prompt += f"\nAdditional context: {context}"
    
    retries = 0
    while retries < max_retries:
        try:
            response = st.session_state.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.5,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                return f"I'm sorry, but I couldn't process your request at this time. Error: {str(e)}"
            # Wait before retrying
            import time
            time.sleep(1)
    
    return "Unable to get a response from the medical AI system. Please try again later."

def get_demo_response(query, context=""):
    """
    Generate a demo response that simulates AI output.
    
    Args:
        query (str): The user's query
        context (str): Optional context to customize the response
    
    Returns:
        str: A simulated AI response
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

def get_symptom_analysis(symptoms, age, gender, medical_history):
    """
    Analyze symptoms using the LLM and provide potential conditions with disclaimer.
    
    Args:
        symptoms (list): List of user symptoms
        age (int): User's age
        gender (str): User's gender
        medical_history (list): User's medical history
    
    Returns:
        str: Analysis results with potential conditions
    """
    context = f"""
    The user is a {age}-year-old {gender} with the following symptoms: {', '.join(symptoms)}.
    Medical history: {', '.join(medical_history) if medical_history else 'None provided'}.
    
    Based on these symptoms, provide:
    1. Possible conditions that might be associated with these symptoms (3-5 possibilities)
    2. General severity assessment (mild, moderate, serious)
    3. Whether immediate medical attention might be needed
    4. General self-care recommendations if appropriate
    
    Remember to include standard medical disclaimers.
    """
    
    query = "What might be causing these symptoms and what should I do next?"
    
    return get_llm_response(query, context)

def get_medical_qa_response(question, user_info=None):
    """
    Get response for medical Q&A section.
    
    Args:
        question (str): User's medical question
        user_info (dict): Optional user information for context
    
    Returns:
        str: The model's response to the medical question
    """
    context = ""
    if user_info:
        context = f"""
        User information:
        - Age: {user_info.get('age', 'Not provided')}
        - Gender: {user_info.get('gender', 'Not provided')}
        - Medical history: {', '.join(user_info.get('medical_history', [])) if user_info.get('medical_history') else 'None provided'}
        - Current medications: {', '.join(user_info.get('medications', [])) if user_info.get('medications') else 'None provided'}
        
        When answering, consider the user's personal context when relevant, but maintain medical accuracy above all.
        """
    
    return get_llm_response(question, context)

def get_care_recommendations(symptoms, age, gender, medical_history, lifestyle_factors):
    """
    Generate personalized care recommendations.
    
    Args:
        symptoms (list): User's current symptoms
        age (int): User's age
        gender (str): User's gender
        medical_history (list): User's medical history
        lifestyle_factors (dict): User's lifestyle information
    
    Returns:
        str: Personalized care recommendations
    """
    lifestyle_info = "\n".join([f"- {k}: {v}" for k, v in lifestyle_factors.items() if v])
    
    context = f"""
    The user is a {age}-year-old {gender} with the following:
    
    Symptoms: {', '.join(symptoms) if symptoms else 'None reported'}
    Medical history: {', '.join(medical_history) if medical_history else 'None reported'}
    
    Lifestyle information:
    {lifestyle_info if lifestyle_info else 'None provided'}
    
    Based on this information, please provide:
    1. Personalized health recommendations
    2. Lifestyle adjustments that may improve their condition
    3. General wellness tips appropriate for their profile
    4. When they should consider seeking professional medical advice
    
    Focus on evidence-based recommendations and include appropriate disclaimers.
    """
    
    query = "What personalized care recommendations would be appropriate for me?"
    
    return get_llm_response(query, context)
