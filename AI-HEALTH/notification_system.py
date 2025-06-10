import streamlit as st
import json
import os
from datetime import datetime, timedelta
import time
import random

# Notification System for Health Buddy

def get_notifications_db():
    """Load or create the notifications database"""
    if os.path.exists('notifications_db.json'):
        with open('notifications_db.json', 'r') as f:
            return json.load(f)
    else:
        notifications = {
            "users": {}
        }
        save_notifications_db(notifications)
        return notifications

def save_notifications_db(notifications):
    """Save the notifications database"""
    with open('notifications_db.json', 'w') as f:
        json.dump(notifications, f, indent=4)

def create_notification(username, title, message, notification_type="info", expiry=None, action=None, read=False):
    """Create a new notification for a user"""
    notifications = get_notifications_db()
    
    # Initialize user notifications if not exists
    if username not in notifications["users"]:
        notifications["users"][username] = []
    
    # Generate notification ID
    notification_id = f"notif_{len(notifications['users'][username]) + 1}_{int(time.time())}"
    
    # Create notification
    notification = {
        "id": notification_id,
        "title": title,
        "message": message,
        "type": notification_type,  # info, success, warning, error
        "created_at": str(datetime.now()),
        "expiry": str(expiry) if expiry else "",
        "read": read,
        "action": action  # Optional action to take when notification is clicked
    }
    
    # Add to user's notifications
    notifications["users"][username].append(notification)
    save_notifications_db(notifications)
    
    return notification_id

def get_user_notifications(username, include_read=False, limit=50):
    """Get notifications for a user"""
    notifications = get_notifications_db()
    
    if username not in notifications["users"]:
        return []
    
    # Get notifications, filter by read status if needed
    user_notifications = notifications["users"][username]
    if not include_read:
        user_notifications = [n for n in user_notifications if not n["read"]]
    
    # Sort by creation time (newest first)
    user_notifications.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Check for expired notifications
    now = datetime.now()
    valid_notifications = []
    for notif in user_notifications:
        if notif["expiry"]:
            try:
                expiry_time = datetime.fromisoformat(notif["expiry"].replace('Z', '+00:00'))
                if expiry_time < now:
                    continue  # Skip expired notifications
            except (ValueError, TypeError):
                pass  # If expiry date is invalid, keep the notification
        
        valid_notifications.append(notif)
    
    # Return limited number of notifications
    return valid_notifications[:limit]

def mark_notification_read(username, notification_id):
    """Mark a notification as read"""
    notifications = get_notifications_db()
    
    if username not in notifications["users"]:
        return False
    
    # Find and update notification
    for i, notification in enumerate(notifications["users"][username]):
        if notification["id"] == notification_id:
            notifications["users"][username][i]["read"] = True
            save_notifications_db(notifications)
            return True
    
    return False

def mark_all_read(username):
    """Mark all notifications as read for a user"""
    notifications = get_notifications_db()
    
    if username not in notifications["users"]:
        return False
    
    # Mark all as read
    for i in range(len(notifications["users"][username])):
        notifications["users"][username][i]["read"] = True
    
    save_notifications_db(notifications)
    return True

def delete_notification(username, notification_id):
    """Delete a notification"""
    notifications = get_notifications_db()
    
    if username not in notifications["users"]:
        return False
    
    # Filter out the notification to delete
    original_count = len(notifications["users"][username])
    notifications["users"][username] = [
        n for n in notifications["users"][username] if n["id"] != notification_id
    ]
    
    # Check if anything was deleted
    if len(notifications["users"][username]) < original_count:
        save_notifications_db(notifications)
        return True
    
    return False

def create_scheduled_health_notifications(username, patient_data=None):
    """Create scheduled health notifications based on user data"""
    # Get existing notifications to avoid duplicates
    existing = get_user_notifications(username, include_read=True)
    existing_titles = [n["title"] for n in existing]
    
    # Check how many notifications were added today
    today = datetime.now().strftime("%Y-%m-%d")
    today_notifications = [n for n in existing if n["created_at"].startswith(today)]
    
    # Limit new notifications per day
    if len(today_notifications) >= 5:
        return 0  # Maximum daily notifications reached
    
    # List of potential notifications
    potential_notifications = []
    
    # Add general health reminders
    general_reminders = [
        {"title": "Stay Hydrated", "message": "Remember to drink water regularly throughout the day for optimal health."},
        {"title": "Take a Break", "message": "It's time for a short break. Stand up, stretch, and rest your eyes."},
        {"title": "Posture Check", "message": "Check your posture. Sit up straight and adjust your position if needed."},
        {"title": "Deep Breathing", "message": "Take a moment for deep breathing. Inhale slowly for 4 counts, hold for 2, and exhale for 6."},
        {"title": "Step Count", "message": "Have you reached your step goal today? Consider taking a short walk."},
        {"title": "Mindfulness Moment", "message": "Take a mindful moment. Focus on your surroundings and practice being present."},
        {"title": "Healthy Snack", "message": "It's snack time! Choose a nutritious option like fruits, nuts, or yogurt."},
        {"title": "Sleep Reminder", "message": "Start winding down for good sleep. Reduce screen time and prepare for rest."}
    ]
    
    # Add personalized reminders if patient data is available
    if patient_data:
        # Age-based reminders
        if "age" in patient_data:
            age = patient_data["age"]
            if age > 50:
                potential_notifications.append({
                    "title": "Health Screening Reminder", 
                    "message": "Regular health screenings are important at your age. Check with your doctor about recommended screenings."
                })
        
        # Medical history-based reminders
        if "medical_history" in patient_data and patient_data["medical_history"]:
            # Check for specific conditions
            conditions = [c.lower() for c in patient_data["medical_history"]]
            
            if any("diabetes" in c for c in conditions):
                potential_notifications.append({
                    "title": "Blood Sugar Check", 
                    "message": "Don't forget to monitor your blood sugar levels today."
                })
            
            if any("hypertension" in c or "blood pressure" in c for c in conditions):
                potential_notifications.append({
                    "title": "Blood Pressure Check", 
                    "message": "Remember to check your blood pressure today and log the results."
                })
            
            if any("heart" in c for c in conditions):
                potential_notifications.append({
                    "title": "Heart Health", 
                    "message": "Take your heart medications as prescribed and stay active within your doctor's guidelines."
                })
    
    # Combine general and personalized notifications
    all_potential = general_reminders + potential_notifications
    
    # Filter out notifications that were already sent today
    filtered_notifications = [n for n in all_potential if n["title"] not in existing_titles]
    
    # Determine how many notifications to add
    num_to_add = min(2, 5 - len(today_notifications))
    
    # Randomly select notifications to add
    if filtered_notifications and num_to_add > 0:
        selected = random.sample(filtered_notifications, min(num_to_add, len(filtered_notifications)))
        
        # Create the selected notifications
        for notif in selected:
            # Set expiry to end of day
            expiry = datetime.now().replace(hour=23, minute=59, second=59)
            create_notification(
                username,
                notif["title"],
                notif["message"],
                notification_type="info",
                expiry=expiry
            )
        
        return len(selected)
    
    return 0

def create_buddy_notifications(username, buddy_data=None):
    """Create health buddy notifications based on user data"""
    # Check if buddy data exists
    if not buddy_data:
        return 0
    
    # Get existing notifications to avoid duplicates
    existing = get_user_notifications(username, include_read=True)
    existing_titles = [n["title"] for n in existing]
    
    # Check how many notifications were added today
    today = datetime.now().strftime("%Y-%m-%d")
    today_notifications = [n for n in existing if n["created_at"].startswith(today)]
    
    # Limit new notifications per day
    if len(today_notifications) >= 5:
        return 0  # Maximum daily notifications reached
    
    notifications_added = 0
    
    # Check for streak notification
    if buddy_data.get("streak", 0) > 0 and "Streak Milestone" not in existing_titles:
        streak = buddy_data["streak"]
        if streak in [7, 14, 30, 60, 90, 180, 365]:  # Streak milestones
            create_notification(
                username,
                "Streak Milestone!",
                f"Congratulations! You've maintained a {streak}-day streak with your Health Buddy. Keep up the great work!",
                notification_type="success",
                expiry=datetime.now() + timedelta(days=1)
            )
            notifications_added += 1
    
    # Check for reminders based on buddy data
    if "reminders" in buddy_data:
        for reminder in buddy_data["reminders"]:
            if reminder.get("completed", False):
                continue  # Skip completed reminders
                
            reminder_title = reminder.get("title", "")
            if reminder_title and f"Reminder: {reminder_title}" not in existing_titles:
                create_notification(
                    username,
                    f"Reminder: {reminder_title}",
                    f"Your Health Buddy reminds you: {reminder_title}",
                    notification_type="info",
                    expiry=datetime.now() + timedelta(days=1)
                )
                notifications_added += 1
                
                # Limit number of reminder notifications
                if notifications_added >= 2:
                    break
    
    # Check for incomplete goals
    if "health_goals" in buddy_data:
        incomplete_goals = [g for g in buddy_data["health_goals"] if not g.get("completed", False)]
        
        if incomplete_goals:
            # Find goals with target dates approaching
            urgent_goals = []
            for goal in incomplete_goals:
                if "target_date" in goal and goal["target_date"]:
                    try:
                        target_date = datetime.fromisoformat(goal["target_date"].replace('Z', '+00:00'))
                        days_left = (target_date - datetime.now()).days
                        
                        if 0 <= days_left <= 3:  # Target date approaching
                            urgent_goals.append((goal, days_left))
                    except (ValueError, TypeError):
                        pass
            
            # Sort by days left (ascending)
            urgent_goals.sort(key=lambda x: x[1])
            
            # Create notifications for urgent goals
            for goal, days_left in urgent_goals[:1]:  # Limit to 1 goal notification
                goal_desc = goal.get("description", "your health goal")
                days_text = "today" if days_left == 0 else f"in {days_left} day{'s' if days_left > 1 else ''}"
                
                title = f"Goal Deadline: {days_text.capitalize()}"
                if title not in existing_titles:
                    create_notification(
                        username,
                        title,
                        f"Your health goal '{goal_desc}' is due {days_text}. Current progress: {goal.get('progress', 0)}%",
                        notification_type="warning",
                        expiry=datetime.now() + timedelta(days=1)
                    )
                    notifications_added += 1
    
    return notifications_added

def create_health_event_notifications(username, patient_data=None):
    """Create notifications for health events like appointments"""
    if not patient_data:
        return 0
    
    # Get existing notifications
    existing = get_user_notifications(username, include_read=True)
    existing_titles = [n["title"] for n in existing]
    
    notifications_added = 0
    
    # Check if there are upcoming appointments
    if "appointments" in patient_data:
        for appointment in patient_data["appointments"]:
            if appointment.get("date"):
                try:
                    appt_date = datetime.fromisoformat(appointment["date"].replace('Z', '+00:00'))
                    days_until = (appt_date - datetime.now()).days
                    
                    # Notify for upcoming appointments
                    if 0 <= days_until <= 3:
                        appt_type = appointment.get("type", "medical appointment")
                        doctor = appointment.get("doctor", "your doctor")
                        
                        title = f"Upcoming Appointment: {days_until} day{'s' if days_until > 1 else ''}"
                        if days_until == 0:
                            title = "Appointment Today"
                            
                        if title not in existing_titles:
                            create_notification(
                                username,
                                title,
                                f"You have a {appt_type} with {doctor} on {appt_date.strftime('%A, %B %d at %I:%M %p')}",
                                notification_type="warning",
                                expiry=appt_date
                            )
                            notifications_added += 1
                except (ValueError, TypeError):
                    pass
    
    return notifications_added

def create_medication_notifications(username, patient_data=None):
    """Create notifications for medication reminders"""
    if not patient_data:
        return 0
    
    # Get existing notifications
    existing = get_user_notifications(username, include_read=True)
    existing_titles = [n["title"] for n in existing]
    
    notifications_added = 0
    
    # Check if there are medications
    if "medications" in patient_data:
        now = datetime.now()
        current_hour = now.hour
        
        for medication in patient_data["medications"]:
            med_name = medication.get("name", "your medication")
            dosage = medication.get("dosage", "")
            
            # Morning medication reminder (8-10 AM)
            if 8 <= current_hour <= 10 and "Morning Medication" not in existing_titles:
                create_notification(
                    username,
                    "Morning Medication",
                    f"Time to take {med_name} {dosage}",
                    notification_type="info",
                    expiry=now.replace(hour=10, minute=59, second=59)
                )
                notifications_added += 1
            
            # Afternoon medication reminder (12-2 PM)
            elif 12 <= current_hour <= 14 and "Afternoon Medication" not in existing_titles:
                create_notification(
                    username,
                    "Afternoon Medication",
                    f"Time to take {med_name} {dosage}",
                    notification_type="info",
                    expiry=now.replace(hour=14, minute=59, second=59)
                )
                notifications_added += 1
            
            # Evening medication reminder (6-8 PM)
            elif 18 <= current_hour <= 20 and "Evening Medication" not in existing_titles:
                create_notification(
                    username,
                    "Evening Medication",
                    f"Time to take {med_name} {dosage}",
                    notification_type="info",
                    expiry=now.replace(hour=20, minute=59, second=59)
                )
                notifications_added += 1
            
            # Bedtime medication reminder (9-11 PM)
            elif 21 <= current_hour <= 23 and "Bedtime Medication" not in existing_titles:
                create_notification(
                    username,
                    "Bedtime Medication",
                    f"Time to take {med_name} {dosage} before bed",
                    notification_type="info",
                    expiry=now.replace(hour=23, minute=59, second=59)
                )
                notifications_added += 1
    
    return notifications_added

def show_notifications(username, location="sidebar"):
    """Display notifications in the app"""
    notifications = get_user_notifications(username)
    
    if not notifications:
        return
    
    if location == "sidebar":
        with st.sidebar:
            st.markdown(f"### 🔔 Notifications ({len(notifications)})")
            
            for notification in notifications[:5]:  # Show max 5 in sidebar
                notification_type = notification.get("type", "info")
                
                # Select icon based on notification type
                if notification_type == "success":
                    icon = "✅"
                elif notification_type == "warning":
                    icon = "⚠️"
                elif notification_type == "error":
                    icon = "❌"
                else:
                    icon = "ℹ️"
                
                with st.expander(f"{icon} {notification['title']}"):
                    st.write(notification['message'])
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Mark as Read", key=f"read_{notification['id']}", use_container_width=True):
                            mark_notification_read(username, notification['id'])
                            st.rerun()
                    
                    with col2:
                        if st.button("Dismiss", key=f"dismiss_{notification['id']}", use_container_width=True):
                            delete_notification(username, notification['id'])
                            st.rerun()
            
            if len(notifications) > 5:
                st.write(f"+ {len(notifications) - 5} more notifications")
                
            if len(notifications) > 0:
                if st.button("Mark All as Read", use_container_width=True):
                    mark_all_read(username)
                    st.rerun()
    else:
        # Full notification center
        st.subheader(f"🔔 Notifications ({len(notifications)})")
        
        if len(notifications) == 0:
            st.info("You have no new notifications")
            return
        
        # Group notifications by type for better organization
        success_notifications = [n for n in notifications if n.get("type") == "success"]
        warning_notifications = [n for n in notifications if n.get("type") == "warning"]
        error_notifications = [n for n in notifications if n.get("type") == "error"]
        info_notifications = [n for n in notifications if n.get("type") == "info" or n.get("type") not in ["success", "warning", "error"]]
        
        # Display by priority: error, warning, success, info
        for notif_group, title, icon in [
            (error_notifications, "Urgent", "❌"),
            (warning_notifications, "Important", "⚠️"),
            (success_notifications, "Good News", "✅"),
            (info_notifications, "Informational", "ℹ️")
        ]:
            if notif_group:
                st.markdown(f"#### {icon} {title}")
                
                for notification in notif_group:
                    with st.container():
                        st.markdown(f"**{notification['title']}**")
                        st.write(notification['message'])
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Mark as Read", key=f"read_{notification['id']}", use_container_width=True):
                                mark_notification_read(username, notification['id'])
                                st.rerun()
                        
                        with col2:
                            if st.button("Dismiss", key=f"dismiss_{notification['id']}", use_container_width=True):
                                delete_notification(username, notification['id'])
                                st.rerun()
                        
                        st.markdown("---")
        
        # Mark all as read button
        if st.button("Mark All as Read", use_container_width=True):
            mark_all_read(username)
            st.rerun()

def show_notification_center(username, patient_data=None, buddy_data=None):
    """Show the full notification center page"""
    st.header("🔔 Notification Center")
    
    # Create new notifications based on health data
    with st.spinner("Checking for new notifications..."):
        # Generate various types of notifications
        create_scheduled_health_notifications(username, patient_data)
        
        if buddy_data:
            create_buddy_notifications(username, buddy_data)
        
        if patient_data:
            create_health_event_notifications(username, patient_data)
            create_medication_notifications(username, patient_data)
    
    # Display all notifications
    show_notifications(username, location="full")
    
    # Notification preferences
    st.subheader("Notification Preferences")
    
    # Create columns for different notification types
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Health Reminders")
        st.checkbox("Daily health tips", value=True, key="notif_health_tips")
        st.checkbox("Medication reminders", value=True, key="notif_medications")
        st.checkbox("Activity reminders", value=True, key="notif_activities")
    
    with col2:
        st.markdown("##### Health Buddy")
        st.checkbox("Buddy messages", value=True, key="notif_buddy_messages")
        st.checkbox("Goal reminders", value=True, key="notif_goals")
        st.checkbox("Streak updates", value=True, key="notif_streaks")
    
    # Test notification button (for debugging)
    if st.button("Save Preferences", use_container_width=True):
        st.success("Notification preferences saved successfully!")
        
        # For demo purposes, create a test notification
        create_notification(
            username,
            "Preferences Updated",
            "Your notification preferences have been updated successfully.",
            notification_type="success",
            expiry=datetime.now() + timedelta(hours=1)
        )
        
        time.sleep(1)
        st.rerun()