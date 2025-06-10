import streamlit as st
from datetime import datetime

def show_chat_page():
    """Display the AI chat interface"""
    st.title("💬 AI Health Chat")
    st.write("Chat with HealthAssist AI powered by IBM Granite 3.3-2b-instruct")
    
    # Check if model is loaded
    if not st.session_state.model_loaded or not st.session_state.model_manager:
        st.error("🤖 AI Model not loaded. Please load the model from the main page.")
        if st.button("🔄 Go to Main Page"):
            st.session_state.authenticated = False
            st.rerun()
        return
    
    # Model info
    with st.expander("🔧 Model Information"):
        model_info = st.session_state.model_manager.get_model_info()
        for key, value in model_info.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Chat interface
    st.markdown("---")
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("💭 Chat History")
        
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Chat input
    st.markdown("---")
    st.subheader("💬 Ask HealthAssist AI")
    
    # Predefined prompts
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤒 Symptoms Help"):
            prompt = "I'm experiencing some symptoms and would like general guidance on when I should see a doctor."
            handle_user_input(prompt)
    
    with col2:
        if st.button("💊 Medication Info"):
            prompt = "Can you provide general information about medication management and adherence?"
            handle_user_input(prompt)
    
    with col3:
        if st.button("🏃 Wellness Tips"):
            prompt = "What are some general wellness tips for maintaining good health?"
            handle_user_input(prompt)
    
    # Text input
    user_input = st.text_area(
        "Your message:",
        placeholder="Ask about symptoms, health concerns, wellness tips, or any health-related questions...",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📤 Send", type="primary"):
            if user_input.strip():
                handle_user_input(user_input.strip())
            else:
                st.warning("Please enter a message first.")
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Chat settings
    with st.expander("⚙️ Chat Settings"):
        temperature = st.slider(
            "Response Creativity (Temperature)",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Lower values make responses more focused and consistent, higher values make them more creative."
        )
        
        max_tokens = st.slider(
            "Maximum Response Length",
            min_value=100,
            max_value=800,
            value=400,
            step=50,
            help="Maximum number of tokens (roughly words) in the AI response."
        )
        
        # Update model parameters
        if st.session_state.model_manager:
            st.session_state.model_manager.temperature = temperature
            st.session_state.model_manager.max_new_tokens = max_tokens

def handle_user_input(user_input):
    """Process user input and generate AI response"""
    if not user_input:
        return
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Show loading spinner
    with st.spinner("🤖 HealthAssist AI is thinking..."):
        try:
            # Generate response using the model manager
            response = st.session_state.model_manager.health_chat_response(
                user_input,
                st.session_state.chat_history
            )
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().isoformat()
            })
    
    # Rerun to update the display
    st.rerun()

def export_chat_history():
    """Export chat history to text file"""
    if not st.session_state.chat_history:
        return None
    
    chat_text = f"HealthAssist AI Chat History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    chat_text += "=" * 60 + "\n\n"
    
    for message in st.session_state.chat_history:
        role = "You" if message["role"] == "user" else "HealthAssist AI"
        timestamp = message.get("timestamp", "")
        chat_text += f"{role} ({timestamp}):\n"
        chat_text += f"{message['content']}\n\n"
        chat_text += "-" * 40 + "\n\n"
    
    return chat_text


