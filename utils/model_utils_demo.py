import streamlit as st
from datetime import datetime
import random

class DemoModelManager:
    """Demo version of ModelManager for showcasing functionality without heavy dependencies"""
    
    def __init__(self):
        self.model_name = "ibm-granite/granite-3.3-2b-instruct"
        self.loaded = False
        
    def load_model(self):
        """Simulate model loading"""
        self.loaded = True
        return True
    
    def health_chat_response(self, user_message, chat_history=None):
        """Generate demo health-focused chat response"""
        
        # Demo responses based on common health topics
        responses = {
            "symptom": [
                "Based on the symptoms you've described, I recommend monitoring them closely. If symptoms persist or worsen, please consult with a healthcare professional for proper evaluation.",
                "These symptoms could indicate several conditions. It's important to track when they occur and their severity. Consider scheduling an appointment with your doctor if they continue.",
                "Thank you for sharing your symptoms. While I can provide general information, a healthcare provider can give you the most accurate assessment based on your specific situation."
            ],
            "medication": [
                "Medication adherence is crucial for treatment effectiveness. Always follow your prescribed schedule and consult your pharmacist or doctor if you have questions about your medications.",
                "It's important to take medications as prescribed. If you're experiencing side effects or have concerns, speak with your healthcare provider about potential adjustments.",
                "Keep track of your medications, including dosages and timing. A pill organizer can help ensure you don't miss doses."
            ],
            "wellness": [
                "Maintaining good health involves regular exercise, balanced nutrition, adequate sleep, and stress management. Start with small, sustainable changes.",
                "Focus on the basics: stay hydrated, get 7-9 hours of sleep, include fruits and vegetables in your diet, and try to be active for at least 30 minutes daily.",
                "Preventive care is key to long-term health. Regular check-ups, screenings, and maintaining healthy habits can help prevent many health issues."
            ],
            "general": [
                "I'm here to provide general health information and support. For specific medical concerns, always consult with qualified healthcare professionals.",
                "Your health is important. If you have specific concerns or symptoms, I recommend discussing them with your doctor or healthcare provider.",
                "Thank you for your question. While I can offer general guidance, personalized medical advice should come from licensed healthcare professionals."
            ]
        }
        
        # Simple keyword matching for demo purposes
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["symptom", "pain", "ache", "fever", "sick", "hurt"]):
            category = "symptom"
        elif any(word in message_lower for word in ["medication", "medicine", "pill", "drug", "prescription"]):
            category = "medication"
        elif any(word in message_lower for word in ["wellness", "health", "exercise", "diet", "sleep", "stress"]):
            category = "wellness"
        else:
            category = "general"
        
        response = random.choice(responses[category])
        
        # Add disclaimer
        disclaimer = "\n\n**Important:** This information is for educational purposes only and should not replace professional medical advice. Always consult healthcare providers for medical concerns."
        
        return response + disclaimer
    
    def symptom_analysis(self, symptoms, patient_info=None):
        """Generate demo symptom analysis"""
        
        analysis = f"""**Symptom Analysis - Educational Information Only**

**Symptoms Reported:** {symptoms}

**General Guidance:**
Based on the symptoms you've described, here are some general considerations:

• **Monitoring:** Keep track of when symptoms occur, their severity, and any triggers
• **Self-Care:** Ensure adequate rest, hydration, and nutrition
• **Documentation:** Maintain a symptom diary to share with healthcare providers

**When to Seek Medical Attention:**
• Symptoms worsen or don't improve within expected timeframes
• New or concerning symptoms develop
• You experience severe pain, difficulty breathing, or other emergency signs

**Next Steps:**
1. Continue monitoring your symptoms
2. Consider scheduling an appointment with your healthcare provider
3. Prepare a list of questions and symptom details for your visit

**Important Disclaimer:**
This analysis is for informational purposes only and does not constitute medical diagnosis or treatment advice. Always consult qualified healthcare professionals for proper evaluation and care."""

        if patient_info:
            analysis += f"\n\n**Additional Context Noted:** {patient_info}"
            
        return analysis
    
    def wellness_insights(self, wellness_data):
        """Generate demo wellness insights"""
        
        insights = """**Wellness Insights - AI Analysis**

Based on your wellness data, here are some personalized recommendations:

**Positive Trends:**
• Your wellness tracking shows commitment to health monitoring
• Consistent data entry indicates good health awareness

**Areas for Focus:**
• **Physical Activity:** Aim for 150 minutes of moderate exercise weekly
• **Sleep Quality:** Maintain 7-9 hours of quality sleep nightly
• **Nutrition:** Include variety in your diet with fruits, vegetables, and whole grains
• **Stress Management:** Consider meditation, deep breathing, or other relaxation techniques

**Actionable Steps:**
1. Set specific, measurable health goals
2. Track progress regularly
3. Celebrate small improvements
4. Adjust strategies based on what works for you

**Remember:** Sustainable lifestyle changes happen gradually. Focus on one area at a time for lasting results.

*This analysis is based on general wellness principles and should complement, not replace, professional healthcare guidance.*"""

        return insights
    
    def get_model_info(self):
        """Get demo model information"""
        return {
            "model_name": self.model_name,
            "status": "Demo Mode",
            "device": "CPU Simulation",
            "capabilities": "Health Chat, Symptom Analysis, Wellness Insights"
        }