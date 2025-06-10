# GraniteInstructor - HealthAssist AI

A Streamlit-based app powered by IBM Granite 3.3 2B Instruct model.

## 🛠 Requirements

- Python 3.10 or later
- pip (Python package manager)
- Optional: GPU with CUDA (for faster model inference)

## 🚀 How to Run in VS Code (Step-by-Step for Beginners)

### 1. Unzip and Open the Folder in VS Code

- Extract the ZIP
- Open the folder in VS Code

### 2. Open the Terminal in VS Code

- Go to `Terminal > New Terminal`

### 3. Create and Activate a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Requirements

```bash
pip install -r requirements.txt
```

### 5. Run the App

```bash
streamlit run app.py
```

### 6. Open in Browser

- VS Code terminal will show a local URL like: `http://localhost:8501`
- Click or open it in your browser to use the app!

---

This app will download the IBM Granite model on first run (~few GBs).