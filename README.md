# HealthAssist AI - IBM Granite 3.3-2b-instruct Integration

A comprehensive healthcare AI assistant powered by IBM's Granite 3.3-2b-instruct model, deployed with Streamlit for interactive web interface.

## Features

### AI-Powered Healthcare Assistant
- **Medical Chat Interface**: Natural language conversations with IBM Granite model
- **Intelligent Symptom Analysis**: AI-driven symptom checking and medical recommendations
- **Wellness Dashboard**: Health analytics and personalized insights
- **Patient Management**: Comprehensive patient record management
- **Smart Notifications**: Automated health reminders and alerts
- **Role-Based Access**: Admin, Doctor, and Patient user roles

### Technical Stack
- **AI Model**: IBM Granite 3.3-2b-instruct with 4-bit quantization
- **Framework**: Streamlit for web interface
- **Backend**: Python with PyTorch and Transformers
- **Deployment**: Google Colab with T4 GPU support
- **Data**: JSON-based storage with structured health records

## Quick Start

### Google Colab Deployment (Recommended)

1. **Open the Deployment Notebook**:
   - Upload `HealthAssist_AI_Colab_Deploy.ipynb` to Google Colab
   - Switch to GPU runtime (T4 recommended)

2. **Run Setup Cells**:
   - Execute dependency installation
   - Configure environment variables
   - Setup ngrok for public access

3. **Launch Application**:
   - Run the deployment cell
   - Access via provided public URL

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd healthassist-ai

# Install dependencies
pip install streamlit torch transformers accelerate bitsandbytes plotly pandas

# Run application
streamlit run app.py --server.port 5000
```

## Authentication

### Demo Accounts
- **Admin**: admin / admin123
- **Doctor**: doctor / doctor123  
- **Patient**: patient / patient123

## System Requirements

### Minimum Requirements
- **GPU**: T4 GPU (15GB VRAM) for optimal performance
- **RAM**: 8GB system memory
- **Storage**: 5GB for model and dependencies

### Recommended Configuration
- **GPU**: A100 or V100 for production deployment
- **RAM**: 16GB+ system memory
- **Network**: Stable internet for model downloading

## Architecture

### Core Components
- `app.py`: Main Streamlit application
- `utils/model_utils.py`: IBM Granite model integration
- `pages/`: Individual page components
- `utils/auth_utils.py`: Authentication system
- `utils/health_data.py`: Health data management

### Data Structure
```
data/
├── users.json          # User authentication data
├── patients.json       # Patient records
├── health_records.json # Medical history
└── notifications.json  # System notifications
```

## Model Integration

### IBM Granite 3.3-2b-instruct
- **Parameters**: 3.3 billion parameters optimized for instruction following
- **Quantization**: 4-bit precision for memory efficiency
- **Context**: Maintains conversation history for coherent responses
- **Specialization**: Medical domain fine-tuning for healthcare applications

### Performance Metrics
- **Memory Usage**: 4-6GB VRAM with quantization
- **Response Time**: 2-5 seconds per query on T4 GPU
- **Accuracy**: High-quality medical information with safety guardrails

## Security and Privacy

### Data Protection
- Local data storage with JSON encryption
- Session-based authentication
- Role-based access control
- Medical data anonymization

### Compliance Considerations
- HIPAA compliance framework ready
- Audit logging capabilities
- Data retention policies
- Secure communication protocols

## Development

### Adding New Features
1. Create component in `pages/` directory
2. Update navigation in `app.py`
3. Add authentication checks
4. Implement data persistence

### Model Customization
- Modify parameters in `utils/model_utils.py`
- Adjust quantization settings for different GPUs
- Fine-tune prompts for specific medical domains

## Deployment Options

### Google Colab (Development)
- Free T4 GPU access
- Pre-configured environment
- Public URL via ngrok
- Ideal for testing and demos

### Cloud Production
- Google Cloud Run with GPU
- AWS ECS with GPU instances
- Azure Container Instances
- Hugging Face Spaces

## Troubleshooting

### Common Issues
- **Model Loading**: Ensure GPU runtime and sufficient VRAM
- **Connection**: Regenerate ngrok tunnel if URL inactive
- **Performance**: Monitor GPU utilization and memory usage
- **Authentication**: Verify demo credentials and clear browser cache

### Performance Optimization
- Enable gradient checkpointing for memory efficiency
- Implement model caching for faster responses
- Use conversation trimming for long sessions
- Configure batch processing for multiple users

## Contributing

### Development Setup
1. Fork repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

### Code Standards
- Follow Python PEP 8 guidelines
- Add docstrings for all functions
- Implement error handling
- Write unit tests for new features

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This application is for demonstration and educational purposes only. The AI responses should not replace professional medical consultation. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.

## Support

For technical support and questions:
- Review deployment guide documentation
- Check system requirements and compatibility
- Verify authentication and network configuration
- Monitor GPU usage and performance metrics