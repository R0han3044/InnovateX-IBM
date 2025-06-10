import os
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Base class for SQLAlchemy models
Base = declarative_base()

# Define models
class User(Base):
    """User model for storing patient information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    age = Column(Integer)
    gender = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_history = relationship("MedicalHistory", back_populates="user", cascade="all, delete-orphan")
    health_metrics = relationship("HealthMetric", back_populates="user", cascade="all, delete-orphan")
    symptom_checks = relationship("SymptomCheck", back_populates="user", cascade="all, delete-orphan")

class MedicalHistory(Base):
    """Model for storing user medical history"""
    __tablename__ = "medical_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    condition = Column(String(100))
    diagnosed_date = Column(DateTime)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    medications = Column(Text)  # Stored as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="medical_history")
    
    def set_medications(self, medications_list):
        """Convert list to JSON string for storage"""
        self.medications = json.dumps(medications_list)
    
    def get_medications(self):
        """Convert JSON string back to list"""
        if self.medications:
            return json.loads(self.medications)
        return []

class HealthMetric(Base):
    """Model for storing user health metrics"""
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    metric_type = Column(String(50))  # e.g., "steps", "sleep_hours", "heart_rate", etc.
    value = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="health_metrics")

class SymptomCheck(Base):
    """Model for storing symptom check results"""
    __tablename__ = "symptom_checks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symptoms = Column(Text)  # Stored as JSON
    date = Column(DateTime, default=datetime.utcnow)
    assessment = Column(Text)  # AI-generated assessment
    severity = Column(String(20))  # e.g., "mild", "moderate", "severe"
    
    # Relationships
    user = relationship("User", back_populates="symptom_checks")
    
    def set_symptoms(self, symptoms_list):
        """Convert list to JSON string for storage"""
        self.symptoms = json.dumps(symptoms_list)
    
    def get_symptoms(self):
        """Convert JSON string back to list"""
        if self.symptoms:
            return json.loads(self.symptoms)
        return []

# Database connection function
def get_database_connection():
    """
    Create and return a SQLAlchemy database engine
    
    Returns:
        SQLAlchemy engine or None if connection fails
    """
    if not DATABASE_URL:
        st.warning("Database URL not found. Please add your Supabase database URL to the environment variables.")
        return None
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return None

def init_database():
    """
    Initialize the database by creating all tables
    
    Returns:
        bool: True if successful, False otherwise
    """
    engine = get_database_connection()
    if engine:
        try:
            # Create all tables
            Base.metadata.create_all(engine)
            return True
        except Exception as e:
            st.error(f"Failed to create database tables: {str(e)}")
            return False
    return False

def get_session():
    """
    Create and return a SQLAlchemy session
    
    Returns:
        SQLAlchemy session or None if connection fails
    """
    engine = get_database_connection()
    if engine:
        Session = sessionmaker(bind=engine)
        return Session()
    return None

# User-related database functions
def create_user(name, email, age, gender):
    """
    Create a new user in the database
    
    Args:
        name (str): User's name
        email (str): User's email
        age (int): User's age
        gender (str): User's gender
        
    Returns:
        User: Created user object or None if failed
    """
    session = get_session()
    if session:
        try:
            user = User(name=name, email=email, age=age, gender=gender)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            st.error(f"Failed to create user: {str(e)}")
            return None
        finally:
            session.close()
    return None

def get_user_by_email(email):
    """
    Get a user by email
    
    Args:
        email (str): User's email
        
    Returns:
        User: User object or None if not found
    """
    session = get_session()
    if session:
        try:
            user = session.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            st.error(f"Failed to get user: {str(e)}")
            return None
        finally:
            session.close()
    return None

def save_health_metrics(user_id, metrics_data):
    """
    Save health metrics for a user
    
    Args:
        user_id (int): User ID
        metrics_data (list): List of dictionaries with metric data
            Each dict should have: date, metric_type, value
            
    Returns:
        bool: True if successful, False otherwise
    """
    session = get_session()
    if session:
        try:
            for metric in metrics_data:
                health_metric = HealthMetric(
                    user_id=user_id,
                    date=metric.get('date'),
                    metric_type=metric.get('metric_type'),
                    value=metric.get('value')
                )
                session.add(health_metric)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            st.error(f"Failed to save health metrics: {str(e)}")
            return False
        finally:
            session.close()
    return False

def save_symptom_check(user_id, symptoms, assessment, severity):
    """
    Save a symptom check result
    
    Args:
        user_id (int): User ID
        symptoms (list): List of symptoms
        assessment (str): AI-generated assessment
        severity (str): Assessed severity
        
    Returns:
        SymptomCheck: Created symptom check object or None if failed
    """
    session = get_session()
    if session:
        try:
            symptom_check = SymptomCheck(
                user_id=user_id,
                assessment=assessment,
                severity=severity
            )
            symptom_check.set_symptoms(symptoms)
            
            session.add(symptom_check)
            session.commit()
            return symptom_check
        except Exception as e:
            session.rollback()
            st.error(f"Failed to save symptom check: {str(e)}")
            return None
        finally:
            session.close()
    return None

def add_medical_history(user_id, condition, diagnosed_date, notes, medications, is_active=True):
    """
    Add a medical history entry for a user
    
    Args:
        user_id (int): User ID
        condition (str): Medical condition
        diagnosed_date (datetime): Date of diagnosis
        notes (str): Additional notes
        medications (list): List of medications
        is_active (bool): Whether the condition is currently active
        
    Returns:
        MedicalHistory: Created medical history object or None if failed
    """
    session = get_session()
    if session:
        try:
            medical_history = MedicalHistory(
                user_id=user_id,
                condition=condition,
                diagnosed_date=diagnosed_date,
                notes=notes,
                is_active=is_active
            )
            medical_history.set_medications(medications)
            
            session.add(medical_history)
            session.commit()
            return medical_history
        except Exception as e:
            session.rollback()
            st.error(f"Failed to add medical history: {str(e)}")
            return None
        finally:
            session.close()
    return None

def get_user_health_metrics(user_id, metric_type=None, start_date=None, end_date=None, limit=100):
    """
    Get health metrics for a user with optional filtering
    
    Args:
        user_id (int): User ID
        metric_type (str, optional): Filter by metric type
        start_date (datetime, optional): Filter by start date
        end_date (datetime, optional): Filter by end date
        limit (int): Maximum number of records to return
        
    Returns:
        list: List of HealthMetric objects
    """
    session = get_session()
    if session:
        try:
            query = session.query(HealthMetric).filter(HealthMetric.user_id == user_id)
            
            if metric_type:
                query = query.filter(HealthMetric.metric_type == metric_type)
            
            if start_date:
                query = query.filter(HealthMetric.date >= start_date)
                
            if end_date:
                query = query.filter(HealthMetric.date <= end_date)
                
            query = query.order_by(HealthMetric.date.desc()).limit(limit)
            
            return query.all()
        except Exception as e:
            st.error(f"Failed to get health metrics: {str(e)}")
            return []
        finally:
            session.close()
    return []