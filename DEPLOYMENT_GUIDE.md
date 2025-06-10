# HealthAssist AI - Google Colab Deployment Guide

## Quick Start in Google Colab

### Method 1: Using the Jupyter Notebook (Recommended)

1. **Open Google Colab**: Go to [colab.research.google.com](https://colab.research.google.com)

2. **Upload Notebook**: Upload the `HealthAssist_AI_Colab_Deploy.ipynb` file

3. **Switch to GPU Runtime**: 
   - Runtime → Change Runtime Type → GPU (T4)
   - Click "Save"

4. **Run Setup Cells**: Execute the first 4 cells to install dependencies

5. **Get Ngrok Token**: 
   - Sign up at [ngrok.com](https://ngrok.com) (free)
   - Copy your auth token from the dashboard

6. **Launch Application**: Run the final cell and follow the public URL

### Method 2: Manual Setup

```python
# 1. Install dependencies
!pip install streamlit torch transformers accelerate bitsandbytes plotly pandas pyngrok

# 2. Clone or upload your project files
# Upload app.py, utils/, pages/, and other project files

# 3. Setup ngrok
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")

# 4. Run Streamlit
!streamlit run app.py --server.port 8501 &
public_url = ngrok.connect(8501)
print(f"App running at: {public_url}")
```

## Project Structure

```
HealthAssist-AI/
├── app.py                           # Main Streamlit application
├── colab_setup.py                   # Google Colab setup script
├── HealthAssist_AI_Colab_Deploy.ipynb  # Complete deployment notebook
├── DEPLOYMENT_GUIDE.md              # This guide
├── utils/
│   ├── model_utils.py              # IBM Granite model integration
│   ├── model_utils_demo.py         # Demo/fallback implementation
│   ├── auth_utils.py               # Authentication system
│   └── health_data.py              # Health data management
├── pages/
│   ├── chat.py                     # AI chat interface
│   ├── symptom_checker.py          # Symptom analysis
│   ├── wellness_dashboard.py       # Health analytics
│   ├── patient_management.py       # Patient records
│   └── notifications.py            # Smart notifications
└── data/
    ├── users.json                  # User database
    ├── patients.json               # Patient records
    └── health_records.json         # Health data
```

## Features

### AI-Powered Healthcare Assistant
- **Medical Chat**: Natural conversation with IBM Granite 3.3-2b-instruct
- **Symptom Analysis**: Intelligent symptom checking and recommendations
- **Health Insights**: Personalized wellness recommendations
- **Multi-Role Support**: Admin, Doctor, Patient access levels

### Technical Specifications
- **Model**: IBM Granite 3.3-2b-instruct with 4-bit quantization
- **Memory**: 4-6GB VRAM usage on T4 GPU
- **Response Time**: 2-5 seconds per query
- **Interface**: Streamlit web application

## Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Doctor | doctor | doctor123 |
| Patient | patient | patient123 |

## Performance Optimization

### GPU Requirements
- **Minimum**: T4 GPU (15GB VRAM)
- **Recommended**: A100 or V100 for faster inference
- **Fallback**: CPU mode available (slower responses)

### Memory Management
- 4-bit quantization reduces memory usage by 75%
- Dynamic batching for multiple users
- Conversation history trimming for context management

## Security Considerations

### Demo vs Production
- Current implementation uses simple authentication
- For production deployment, implement:
  - OAuth2/JWT authentication
  - Encrypted data storage
  - HIPAA compliance measures
  - Audit logging

### Data Privacy
- No real medical data should be used in demo
- Implement data anonymization for production
- Follow healthcare data protection regulations

## Troubleshooting

### Common Issues

**Model Loading Fails**
- Ensure GPU runtime is selected
- Check VRAM availability with `!nvidia-smi`
- Restart runtime if needed

**Connection Timeout**
- Regenerate ngrok tunnel
- Check firewall settings
- Verify port accessibility

**Memory Errors**
- Reduce max_token_length in responses
- Enable gradient checkpointing
- Use smaller batch sizes

**Authentication Issues**
- Clear browser cache
- Check demo credentials
- Restart Streamlit application

### Performance Monitoring

```python
# Monitor GPU usage
!nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv

# Check active connections
import psutil
print(f"Active connections: {len(psutil.net_connections())}")
```

## Advanced Configuration

### Model Customization
```python
# Adjust model parameters in utils/model_utils.py
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)
```

### UI Customization
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

## Production Deployment

### Cloud Platforms
- **Google Cloud Run**: Container deployment
- **AWS ECS**: Elastic container service
- **Azure Container Instances**: Serverless containers
- **Hugging Face Spaces**: Direct model deployment

### Scaling Considerations
- Load balancing for multiple users
- Model caching and optimization
- Database migration to PostgreSQL/MongoDB
- CDN for static assets

## Support and Updates

### Getting Help
1. Check this deployment guide
2. Review error logs in Colab
3. Verify system requirements
4. Test with demo accounts first

### Version Updates
- Model updates: Modify `model_name` in `utils/model_utils.py`
- Feature updates: Pull latest code from repository
- Security patches: Update dependencies regularly

---

**Disclaimer**: This application is for demonstration and educational purposes. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment. The AI responses should not replace professional medical consultation.