import json
import hashlib
import os
from datetime import datetime

class AuthManager:
    """Manages user authentication and authorization"""
    
    def __init__(self):
        self.users_file = "data/users_db.json"
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Ensure users file exists with default accounts"""
        if not os.path.exists("data"):
            os.makedirs("data")
            
        if not os.path.exists(self.users_file):
            default_users = {
                "users": [
                    {
                        "username": "admin",
                        "password": self.hash_password("admin123"),
                        "role": "admin",
                        "name": "System Administrator",
                        "email": "admin@healthassist.ai",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "username": "doctor",
                        "password": self.hash_password("doctor123"),
                        "role": "doctor",
                        "name": "Dr. Jane Smith",
                        "email": "doctor@healthassist.ai",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "username": "patient",
                        "password": self.hash_password("patient123"),
                        "role": "patient",
                        "name": "John Doe",
                        "email": "patient@healthassist.ai",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {"users": []}
    
    def save_users(self, users_data):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            return True
        except:
            return False
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        users_data = self.load_users()
        hashed_password = self.hash_password(password)
        
        for user in users_data.get("users", []):
            if user["username"] == username and user["password"] == hashed_password:
                return True
        
        return False
    
    def get_user_info(self, username):
        """Get user information"""
        users_data = self.load_users()
        
        for user in users_data.get("users", []):
            if user["username"] == username:
                # Return user info without password
                user_info = user.copy()
                del user_info["password"]
                return user_info
        
        return None
    
    def get_user_role(self, username):
        """Get user role"""
        user_info = self.get_user_info(username)
        return user_info.get("role", "patient") if user_info else "patient"
    
    def create_user(self, username, password, role, name, email):
        """Create a new user"""
        users_data = self.load_users()
        
        # Check if username already exists
        for user in users_data.get("users", []):
            if user["username"] == username:
                return False, "Username already exists"
        
        # Create new user
        new_user = {
            "username": username,
            "password": self.hash_password(password),
            "role": role,
            "name": name,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        
        users_data["users"].append(new_user)
        
        if self.save_users(users_data):
            return True, "User created successfully"
        else:
            return False, "Failed to save user data"
    
    def update_user(self, username, updates):
        """Update user information"""
        users_data = self.load_users()
        
        for i, user in enumerate(users_data.get("users", [])):
            if user["username"] == username:
                # Update allowed fields
                allowed_fields = ["name", "email", "role"]
                for field in allowed_fields:
                    if field in updates:
                        users_data["users"][i][field] = updates[field]
                
                # Handle password update separately
                if "password" in updates:
                    users_data["users"][i]["password"] = self.hash_password(updates["password"])
                
                users_data["users"][i]["updated_at"] = datetime.now().isoformat()
                
                if self.save_users(users_data):
                    return True, "User updated successfully"
                else:
                    return False, "Failed to save user data"
        
        return False, "User not found"
    
    def delete_user(self, username):
        """Delete a user"""
        users_data = self.load_users()
        
        original_count = len(users_data.get("users", []))
        users_data["users"] = [user for user in users_data.get("users", []) if user["username"] != username]
        
        if len(users_data["users"]) < original_count:
            if self.save_users(users_data):
                return True, "User deleted successfully"
            else:
                return False, "Failed to save user data"
        
        return False, "User not found"
    
    def list_users(self, role_filter=None):
        """List all users (without passwords)"""
        users_data = self.load_users()
        users = []
        
        for user in users_data.get("users", []):
            if role_filter is None or user.get("role") == role_filter:
                user_info = user.copy()
                del user_info["password"]
                users.append(user_info)
        
        return users
