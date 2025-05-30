# HealthAssist AI

## Overview

HealthAssist AI is an AI-powered healthcare assistant built with Streamlit that provides various health-related tools for users, including symptom checking, medical Q&A, personalized care recommendations, and health tracking. The application uses language models (specifically IBM Granite LLM) via Hugging Face to provide intelligent responses to medical queries.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

HealthAssist AI follows a straightforward architecture centered around Streamlit for the frontend and LangChain with Hugging Face for the AI capabilities. The application is designed as a multi-page Streamlit app with a modular structure.

### Key Architectural Decisions:

1. **Streamlit as the UI Framework**:
   - Chosen for its simplicity and rapid development capabilities
   - Enables interactive components like chat interfaces and data visualizations
   - Allows for a multi-page application structure with minimal boilerplate

2. **LangChain Integration**:
   - Provides a framework for chaining LLM operations together
   - Maintains conversation context between user interactions
   - Handles prompt template management

3. **IBM Granite LLM via Hugging Face Hub**:
   - Selected for its medical knowledge capabilities
   - Accessed through the Hugging Face Hub API
   - Model parameters are configured for healthcare-specific responses

4. **Modular Component Structure**:
   - Different healthcare tools are separated into independent pages
   - Common utilities are shared through the utils module
   - Medical data is centralized for consistent reference across the application

## Key Components

### 1. Main Application (`app.py`)
- Entry point for the Streamlit application
- Sets up the application layout and global session state
- Initializes the LLM chain and other data dependencies

### 2. Page Components
- **Symptom Checker** (`pages/symptom_checker.py`): Interactive tool for analyzing user symptoms
- **Medical Q&A** (`pages/medical_qa.py`): Chat interface for answering health-related questions
- **Care Recommendations** (`pages/care_recommendations.py`): Provides personalized health advice
- **Patient Dashboard** (`pages/patient_dashboard.py`): Visualizes health metrics and trends

### 3. Utilities
- **LLM Utilities** (`utils/llm_utils.py`): Handles interaction with the language model
- **Medical Data** (`utils/medical_data.py`): Provides health-related reference data and generates sample visualization data

## Data Flow

1. **User Input Flow**:
   - User enters symptoms, questions, or health data through the Streamlit interface
   - Input is processed and stored in the session state
   - Relevant data is prepared as context for the LLM

2. **AI Processing Flow**:
   - User query and context are formatted using prompt templates
   - The formatted prompt is sent to the IBM Granite LLM via HuggingFaceHub
   - The LLM processes the query and returns a response
   - Response is displayed to the user through the Streamlit interface

3. **Health Data Flow**:
   - User profile and health metrics are captured and stored in session state
   - Visualization components transform this data into interactive charts
   - The dashboard displays health trends over configurable time periods

## External Dependencies

### Primary Dependencies:
1. **Streamlit** (v1.45.1+): Main UI framework
2. **LangChain**: For orchestrating LLM operations
3. **Hugging Face Hub**: For accessing the IBM Granite LLM
4. **Pandas & NumPy**: For data manipulation and analysis
5. **Plotly**: For advanced data visualizations in the dashboard

### API Dependencies:
1. **Hugging Face API**: Requires an API token set as the `HUGGINGFACE_API_TOKEN` environment variable

## Deployment Strategy

The application is configured for deployment on Replit with the following considerations:

1. **Runtime Environment**:
   - Uses Python 3.11 module
   - Relies on stable Nix channel (24_05)
   - Includes bash and glibcLocales packages

2. **Deployment Target**:
   - Set to "autoscale" for handling variable loads

3. **Server Configuration**:
   - Streamlit runs on port 5000
   - Server is configured as headless with address 0.0.0.0
   - Custom theme settings are defined in `.streamlit/config.toml`

4. **Workflows**:
   - Run button is configured to start the "Project" workflow
   - Project workflow runs the server in parallel mode
   - Server task executes Streamlit with the main app.py file

## Future Development Areas

1. **Database Integration**: Currently using session state for data storage; could be enhanced with a persistent database
2. **Enhanced AI Capabilities**: Potential for more specialized medical models or fine-tuning
3. **User Authentication**: Adding secure login functionality for personalized experiences
4. **Mobile Responsiveness**: Optimizing the UI for better mobile experience
5. **Integration with External Health APIs**: For real medical data and drug information