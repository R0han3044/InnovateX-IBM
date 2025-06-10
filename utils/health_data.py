import json
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class HealthDataManager:
    """Manages health data storage and retrieval"""
    
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_json_file(self, filename):
        """Load JSON file with error handling"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return {}
    
    def save_json_file(self, filename, data):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def get_patient_records(self, username=None):
        """Get patient health records"""
        records = self.load_json_file("health_records_db.json")
        if not records:
            records = {"records": []}
        
        if username:
            user_records = [r for r in records["records"] if r.get("username") == username]
            return user_records
        
        return records["records"]
    
    def add_health_record(self, username, record_data):
        """Add a new health record"""
        records = self.load_json_file("health_records_db.json")
        if not records:
            records = {"records": []}
        
        # Add metadata
        record_data.update({
            "username": username,
            "record_id": f"rec_{len(records['records']) + 1}_{int(datetime.now().timestamp())}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        records["records"].append(record_data)
        return self.save_json_file("health_records_db.json", records)
    
    def get_wellness_data(self, username):
        """Get wellness data for a user"""
        wellness_file = f"wellness_{username}.json"
        wellness_data = self.load_json_file(wellness_file)
        
        if not wellness_data:
            # Generate initial wellness data
            wellness_data = self.generate_initial_wellness_data(username)
            self.save_json_file(wellness_file, wellness_data)
        
        return wellness_data
    
    def update_wellness_data(self, username, new_data):
        """Update wellness data for a user"""
        wellness_file = f"wellness_{username}.json"
        wellness_data = self.load_json_file(wellness_file)
        
        if not wellness_data:
            wellness_data = self.generate_initial_wellness_data(username)
        
        # Update with new data
        wellness_data.update(new_data)
        wellness_data["last_updated"] = datetime.now().isoformat()
        
        return self.save_json_file(wellness_file, wellness_data)
    
    def generate_initial_wellness_data(self, username):
        """Generate initial wellness data for a new user"""
        # Create 30 days of sample data
        dates = []
        scores = []
        components = {
            "physical": [],
            "mental": [],
            "nutrition": [],
            "sleep": [],
            "activity": []
        }
        
        base_date = datetime.now() - timedelta(days=30)
        np.random.seed(hash(username) % 1000)  # Consistent randomization per user
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
            
            # Generate trending upward scores with variation
            base_score = 60 + (i * 0.5) + np.random.normal(0, 8)
            score = max(30, min(95, base_score))
            scores.append(int(score))
            
            # Generate component scores with different patterns
            for component in components:
                component_variation = np.random.normal(0, 10)
                component_score = max(20, min(100, score + component_variation))
                components[component].append(int(component_score))
        
        return {
            "username": username,
            "dates": dates,
            "overall_scores": scores,
            "component_scores": components,
            "goals": [],
            "achievements": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def get_notifications(self, username):
        """Get notifications for a user"""
        notifications_file = f"notifications_{username}.json"
        notifications = self.load_json_file(notifications_file)
        
        if not notifications:
            notifications = {"notifications": []}
        
        # Filter out expired notifications
        current_time = datetime.now()
        valid_notifications = []
        
        for notif in notifications.get("notifications", []):
            if "expires_at" in notif:
                try:
                    expires_at = datetime.fromisoformat(notif["expires_at"])
                    if expires_at > current_time:
                        valid_notifications.append(notif)
                except:
                    valid_notifications.append(notif)
            else:
                valid_notifications.append(notif)
        
        return valid_notifications
    
    def add_notification(self, username, title, message, notification_type="info", expires_hours=24):
        """Add a notification for a user"""
        notifications_file = f"notifications_{username}.json"
        notifications = self.load_json_file(notifications_file)
        
        if not notifications:
            notifications = {"notifications": []}
        
        # Create notification
        notification = {
            "id": f"notif_{int(datetime.now().timestamp())}",
            "title": title,
            "message": message,
            "type": notification_type,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=expires_hours)).isoformat(),
            "read": False
        }
        
        notifications["notifications"].append(notification)
        return self.save_json_file(notifications_file, notifications)
    
    def mark_notification_read(self, username, notification_id):
        """Mark a notification as read"""
        notifications_file = f"notifications_{username}.json"
        notifications = self.load_json_file(notifications_file)
        
        if not notifications:
            return False
        
        for notif in notifications.get("notifications", []):
            if notif.get("id") == notification_id:
                notif["read"] = True
                return self.save_json_file(notifications_file, notifications)
        
        return False
    
    def get_health_metrics_summary(self, username):
        """Get a summary of health metrics for a user"""
        wellness_data = self.get_wellness_data(username)
        health_records = self.get_patient_records(username)
        
        # Calculate averages and trends
        if wellness_data.get("overall_scores"):
            recent_scores = wellness_data["overall_scores"][-7:]  # Last 7 days
            avg_score = sum(recent_scores) / len(recent_scores)
            
            if len(wellness_data["overall_scores"]) >= 14:
                prev_week_scores = wellness_data["overall_scores"][-14:-7]
                prev_avg = sum(prev_week_scores) / len(prev_week_scores)
                trend = "improving" if avg_score > prev_avg else "declining" if avg_score < prev_avg else "stable"
            else:
                trend = "stable"
        else:
            avg_score = 0
            trend = "no_data"
        
        # Component averages
        component_averages = {}
        if wellness_data.get("component_scores"):
            for component, scores in wellness_data["component_scores"].items():
                if scores:
                    component_averages[component] = sum(scores[-7:]) / len(scores[-7:])
        
        return {
            "username": username,
            "overall_score": round(avg_score, 1),
            "trend": trend,
            "component_averages": component_averages,
            "total_records": len(health_records),
            "last_updated": wellness_data.get("last_updated", "Never")
        }
