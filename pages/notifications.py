import streamlit as st
from datetime import datetime, timedelta
from utils.health_data import HealthDataManager

def show_notifications():
    """Display notifications page"""
    st.title("🔔 Notifications")
    st.write("Stay updated with your health reminders and alerts")
    
    # Initialize health data manager
    health_manager = HealthDataManager()
    
    # Get user notifications
    notifications = health_manager.get_notifications(st.session_state.username)
    
    # Notification summary
    show_notification_summary(notifications)
    
    # Create sample notifications if none exist
    if not notifications:
        create_sample_notifications(health_manager)
        notifications = health_manager.get_notifications(st.session_state.username)
    
    # Notification tabs
    tab1, tab2, tab3 = st.tabs(["📥 All Notifications", "⚙️ Settings", "📊 Health Reminders"])
    
    with tab1:
        show_all_notifications(notifications, health_manager)
    
    with tab2:
        show_notification_settings(health_manager)
    
    with tab3:
        show_health_reminders(health_manager)

def show_notification_summary(notifications):
    """Display notification summary"""
    unread_count = len([n for n in notifications if not n.get("read", False)])
    total_count = len(notifications)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📬 Total Notifications", total_count)
    
    with col2:
        st.metric("📩 Unread", unread_count)
    
    with col3:
        st.metric("✅ Read", total_count - unread_count)
    
    if unread_count > 0:
        st.info(f"💡 You have {unread_count} unread notification{'s' if unread_count != 1 else ''}")

def show_all_notifications(notifications, health_manager):
    """Display all notifications"""
    st.subheader("📥 All Notifications")
    
    if not notifications:
        st.info("🔕 No notifications yet. Check back later for health reminders and updates!")
        return
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_type = st.selectbox(
            "Filter by type:",
            ["All", "Info", "Success", "Warning", "Error"]
        )
    
    with col2:
        show_read = st.checkbox("Show read notifications", value=True)
    
    with col3:
        if st.button("✅ Mark All as Read"):
            mark_all_notifications_read(notifications, health_manager)
            st.rerun()
    
    # Filter notifications
    filtered_notifications = notifications.copy()
    
    if filter_type != "All":
        filtered_notifications = [n for n in filtered_notifications if n.get("type", "info").lower() == filter_type.lower()]
    
    if not show_read:
        filtered_notifications = [n for n in filtered_notifications if not n.get("read", False)]
    
    # Sort by date (newest first)
    filtered_notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Display notifications
    for notification in filtered_notifications:
        display_notification(notification, health_manager)

def display_notification(notification, health_manager):
    """Display a single notification"""
    # Determine notification style
    notification_type = notification.get("type", "info")
    read_status = notification.get("read", False)
    
    # Icon and color mapping
    type_config = {
        "info": {"icon": "ℹ️", "color": "blue"},
        "success": {"icon": "✅", "color": "green"},
        "warning": {"icon": "⚠️", "color": "orange"},
        "error": {"icon": "❌", "color": "red"}
    }
    
    config = type_config.get(notification_type, type_config["info"])
    
    # Create notification container
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Notification header
            title = notification.get("title", "Notification")
            if not read_status:
                title = f"🟢 {title}"  # Unread indicator
            
            st.markdown(f"**{config['icon']} {title}**")
            
            # Notification content
            message = notification.get("message", "No message content")
            st.write(message)
            
            # Timestamp
            created_at = notification.get("created_at", "")
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at)
                    time_ago = get_time_ago(created_date)
                    st.caption(f"🕒 {time_ago}")
                except:
                    st.caption(f"🕒 {created_at[:10]}")
        
        with col2:
            # Action buttons
            notification_id = notification.get("id", "")
            
            if not read_status and notification_id:
                if st.button("✅", key=f"read_{notification_id}", help="Mark as read"):
                    health_manager.mark_notification_read(st.session_state.username, notification_id)
                    st.rerun()
            
            if st.button("🗑️", key=f"delete_{notification_id}", help="Delete"):
                # This would need to be implemented in HealthDataManager
                st.info("Delete functionality - to be implemented")
        
        st.markdown("---")

def show_notification_settings(health_manager):
    """Display notification settings"""
    st.subheader("⚙️ Notification Settings")
    
    st.write("Customize your notification preferences:")
    
    # Health reminder settings
    with st.expander("🏥 Health Reminders"):
        daily_reminders = st.checkbox("Daily wellness check-in", value=True)
        medication_reminders = st.checkbox("Medication reminders", value=True)
        appointment_reminders = st.checkbox("Appointment reminders", value=True)
        exercise_reminders = st.checkbox("Exercise reminders", value=False)
        
        reminder_time = st.time_input("Preferred reminder time", value=datetime.strptime("09:00", "%H:%M").time())
    
    # Wellness alerts
    with st.expander("📊 Wellness Alerts"):
        score_drops = st.checkbox("Alert when wellness score drops significantly", value=True)
        goal_reminders = st.checkbox("Goal progress reminders", value=True)
        achievement_notifications = st.checkbox("Achievement notifications", value=True)
    
    # AI insights
    with st.expander("🤖 AI Insights"):
        ai_insights = st.checkbox("Weekly AI health insights", value=True)
        personalized_tips = st.checkbox("Personalized health tips", value=True)
    
    if st.button("💾 Save Settings", type="primary"):
        # Save settings (would be implemented in data manager)
        settings = {
            "daily_reminders": daily_reminders,
            "medication_reminders": medication_reminders,
            "appointment_reminders": appointment_reminders,
            "exercise_reminders": exercise_reminders,
            "reminder_time": str(reminder_time),
            "score_drops": score_drops,
            "goal_reminders": goal_reminders,
            "achievement_notifications": achievement_notifications,
            "ai_insights": ai_insights,
            "personalized_tips": personalized_tips
        }
        
        st.success("✅ Notification settings saved!")

def show_health_reminders(health_manager):
    """Display health reminders section"""
    st.subheader("📊 Health Reminders")
    
    # Quick actions to create reminders
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💊 Medication Reminder"):
            create_medication_reminder(health_manager)
        
        if st.button("🏃 Exercise Reminder"):
            create_exercise_reminder(health_manager)
    
    with col2:
        if st.button("🩺 Check-up Reminder"):
            create_checkup_reminder(health_manager)
        
        if st.button("💧 Hydration Reminder"):
            create_hydration_reminder(health_manager)
    
    # Custom reminder
    st.markdown("---")
    st.subheader("➕ Create Custom Reminder")
    
    with st.form("custom_reminder"):
        reminder_title = st.text_input("Reminder Title", placeholder="e.g., Take vitamins")
        reminder_message = st.text_area("Reminder Message", placeholder="Don't forget to take your daily vitamins!")
        reminder_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "One-time"])
        reminder_time = st.time_input("Reminder Time")
        
        if st.form_submit_button("⏰ Create Reminder"):
            if reminder_title and reminder_message:
                create_custom_reminder(health_manager, reminder_title, reminder_message, reminder_frequency, reminder_time)
                st.success("✅ Custom reminder created!")
                st.rerun()
            else:
                st.warning("Please fill in both title and message.")

def create_sample_notifications(health_manager):
    """Create sample notifications for demo"""
    sample_notifications = [
        {
            "title": "Welcome to HealthAssist AI!",
            "message": "Thank you for joining HealthAssist AI. Start by updating your wellness data to get personalized insights.",
            "type": "success"
        },
        {
            "title": "Daily Wellness Check",
            "message": "Don't forget to log your daily wellness metrics. Consistent tracking helps provide better AI insights.",
            "type": "info"
        },
        {
            "title": "Hydration Reminder",
            "message": "Remember to stay hydrated! Aim for 8 glasses of water throughout the day.",
            "type": "info"
        },
        {
            "title": "AI Model Ready",
            "message": "Your IBM Granite AI model is loaded and ready to assist with health questions and analysis.",
            "type": "success"
        }
    ]
    
    for notification in sample_notifications:
        health_manager.add_notification(
            st.session_state.username,
            notification["title"],
            notification["message"],
            notification["type"]
        )

def create_medication_reminder(health_manager):
    """Create a medication reminder"""
    health_manager.add_notification(
        st.session_state.username,
        "💊 Medication Reminder",
        "It's time to take your medication. Please follow your prescribed schedule and dosage.",
        "warning",
        expires_hours=8
    )
    st.success("💊 Medication reminder created!")

def create_exercise_reminder(health_manager):
    """Create an exercise reminder"""
    health_manager.add_notification(
        st.session_state.username,
        "🏃 Exercise Time",
        "Time for your daily exercise! Even a 15-minute walk can make a difference for your health.",
        "info",
        expires_hours=4
    )
    st.success("🏃 Exercise reminder created!")

def create_checkup_reminder(health_manager):
    """Create a checkup reminder"""
    health_manager.add_notification(
        st.session_state.username,
        "🩺 Health Check-up",
        "Consider scheduling your regular health check-up. Preventive care is key to maintaining good health.",
        "warning",
        expires_hours=48
    )
    st.success("🩺 Check-up reminder created!")

def create_hydration_reminder(health_manager):
    """Create a hydration reminder"""
    health_manager.add_notification(
        st.session_state.username,
        "💧 Stay Hydrated",
        "Remember to drink water regularly throughout the day. Proper hydration supports overall health.",
        "info",
        expires_hours=2
    )
    st.success("💧 Hydration reminder created!")

def create_custom_reminder(health_manager, title, message, frequency, time):
    """Create a custom reminder"""
    # Calculate expiry based on frequency
    expiry_hours = {
        "Daily": 24,
        "Weekly": 168,
        "Monthly": 720,
        "One-time": 24
    }
    
    health_manager.add_notification(
        st.session_state.username,
        f"⏰ {title}",
        f"{message}\n\nFrequency: {frequency}\nTime: {time}",
        "info",
        expires_hours=expiry_hours.get(frequency, 24)
    )

def mark_all_notifications_read(notifications, health_manager):
    """Mark all notifications as read"""
    for notification in notifications:
        if not notification.get("read", False):
            notification_id = notification.get("id", "")
            if notification_id:
                health_manager.mark_notification_read(st.session_state.username, notification_id)

def get_time_ago(date_time):
    """Get human-readable time ago string"""
    now = datetime.now()
    diff = now - date_time
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
