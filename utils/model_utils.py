import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import gc
import os
from datetime import datetime

class ModelManager:
    """Manages the IBM Granite model loading and inference"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = "ibm-granite/granite-3.3-2b-instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_new_tokens = 512
        self.temperature = 0.7
        
    def load_model(self):
        """Load the IBM Granite model"""
        try:
            st.info(f"Loading model on: {self.device}")
            
            # Configure quantization for GPU memory efficiency
            quantization_config = None
            if self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load tokenizer
            st.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            st.info("Loading model...")
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None,
            }
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            st.success("Model loaded successfully!")
            return True
            
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def generate_response(self, prompt, system_prompt=None, max_tokens=None, temperature=None):
        """Generate response using the loaded model"""
        if self.model is None or self.tokenizer is None:
            return "Error: Model not loaded. Please load the model first."
        
        try:
            # Use provided parameters or defaults
            max_tokens = max_tokens or self.max_new_tokens
            temperature = temperature or self.temperature
            
            # Format the prompt with system message if provided
            if system_prompt:
                formatted_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            else:
                formatted_prompt = f"User: {prompt}\n\nAssistant:"
            
            # Tokenize input
            inputs = self.tokenizer.encode(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new response (after "Assistant:")
            if "Assistant:" in full_response:
                response = full_response.split("Assistant:")[-1].strip()
            else:
                response = full_response[len(formatted_prompt):].strip()
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def health_chat_response(self, user_message, chat_history=None):
        """Generate health-focused chat response"""
        system_prompt = """You are HealthAssist AI, a helpful medical assistant powered by IBM Granite. You provide accurate health information, symptom analysis, and general medical guidance. 

IMPORTANT DISCLAIMERS:
- Always remind users that your advice is for informational purposes only
- Encourage users to consult healthcare professionals for serious concerns
- Do not provide specific medical diagnoses or treatment recommendations
- Be empathetic and supportive in your responses

Focus on:
- General health education
- Symptom awareness (not diagnosis)
- Wellness tips and preventive care
- When to seek professional medical help
- Mental health support and resources

Keep responses concise, helpful, and medically responsible."""
        
        # Include chat history context if provided
        context = ""
        if chat_history:
            recent_history = chat_history[-6:]  # Last 3 exchanges
            for entry in recent_history:
                if entry['role'] == 'user':
                    context += f"User: {entry['content']}\n"
                else:
                    context += f"Assistant: {entry['content']}\n"
        
        full_prompt = f"{context}\nUser: {user_message}"
        
        return self.generate_response(
            full_prompt,
            system_prompt=system_prompt,
            max_tokens=400,
            temperature=0.7
        )
    
    def symptom_analysis(self, symptoms, patient_info=None):
        """Analyze symptoms and provide general guidance"""
        system_prompt = """You are a medical information assistant. Analyze the provided symptoms and give general guidance about possible conditions and when to seek medical care. 

CRITICAL GUIDELINES:
- Do NOT provide specific diagnoses
- Focus on general symptom categories and common causes
- Always recommend consulting a healthcare provider
- Highlight red flag symptoms that need immediate attention
- Provide general self-care suggestions when appropriate

Be thorough but emphasize that this is educational information only."""
        
        prompt = f"Please analyze these symptoms and provide general guidance: {symptoms}"
        if patient_info:
            prompt += f"\n\nPatient context: {patient_info}"
        
        return self.generate_response(
            prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.6
        )
    
    def wellness_insights(self, wellness_data):
        """Generate wellness insights based on health data"""
        system_prompt = """You are a wellness coach AI. Analyze the provided health data and generate personalized insights and recommendations for improving overall wellness.

Focus on:
- Identifying trends and patterns
- Suggesting realistic lifestyle improvements
- Highlighting positive progress
- Providing motivational support
- Recommending specific, actionable steps

Keep suggestions practical and encouraging."""
        
        prompt = f"Analyze this wellness data and provide insights: {wellness_data}"
        
        return self.generate_response(
            prompt,
            system_prompt=system_prompt,
            max_tokens=400,
            temperature=0.8
        )
    
    def clear_memory(self):
        """Clear GPU memory"""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if self.model is None:
            return "No model loaded"
        
        info = {
            "model_name": self.model_name,
            "device": self.device,
            "parameters": f"{sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M",
            "dtype": str(self.model.dtype) if hasattr(self.model, 'dtype') else "Unknown"
        }
        
        if self.device == "cuda":
            info["gpu_memory"] = f"{torch.cuda.max_memory_allocated() / 1024**3:.2f} GB"
        
        return info
