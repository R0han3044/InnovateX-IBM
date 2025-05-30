import pandas as pd
import numpy as np
import streamlit as st

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
