import streamlit as st
import pandas as pd
from utils.llm_utils import get_medical_qa_response

def show_medical_qa():
    """
    Display the Medical Q&A page where users can ask health-related questions
    and get AI-powered answers.
    """
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
                # Get response from LLM with user context
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
                                # Get response from LLM with user context
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
