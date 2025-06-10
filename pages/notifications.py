import streamlit as st
from datetime import datetime, timedelta
import uuid
import hashlib
from utils.health_data import HealthDataManager

def show_notifications():
    st.title("🔔 Notifications")
    st.write("Stay updated with your health reminders and alerts")

    health_manager = HealthDataManager()
    username = st.session_state.get("username", "guest")
    notifications = health_manager.get_notifications(username)

    show_notification_summary(notifications)

    if not notifications:
        create_sample_notifications(health_manager)
        notifications = health_manager.get_notifications(username)

    tab1, tab2, tab3 = st.tabs(["📥 All Notifications", "⚙️ Settings", "📊 Health Reminders"])

    with tab1:
        show_all_notifications(notifications, health_manager, username)

    with tab2:
        show_notification_settings(health_manager)

    with tab3:
        show_health_reminders(health_manager)

def show_notification_summary(notifications):
    unread_count = len([n for n in notifications if not n.get("read", False)])
    total_count = len(notifications)

    col1, col2, col3 = st.columns(3)
    col1.metric("📬 Total Notifications", total_count)
    col2.metric("📩 Unread", unread_count)
    col3.metric("✅ Read", total_count - unread_count)

    if unread_count > 0:
        st.info(f"💡 You have {unread_count} unread notification{'s' if unread_count != 1 else ''}")

def show_all_notifications(notifications, health_manager, username):
    st.subheader("📥 All Notifications")

    if not notifications:
        st.info("🔕 No notifications yet. Check back later for health reminders and updates!")
        return

    # Ensure all notifications have an ID
    for notif in notifications:
        if "id" not in notif or not notif["id"]:
            notif["id"] = str(uuid.uuid4())

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Filter by type:", ["All", "Info", "Success", "Warning", "Error"])
    with col2:
        show_read = st.checkbox("Show read notifications", value=True)
    with col3:
        if st.button("✅ Mark All as Read"):
            mark_all_notifications_read(notifications, health_manager, username)
            st.rerun()

    filtered_notifications = notifications.copy()
    if filter_type != "All":
        filtered_notifications = [n for n in filtered_notifications if n.get("type", "info").lower() == filter_type.lower()]
    if not show_read:
        filtered_notifications = [n for n in filtered_notifications if not n.get("read", False)]

    filtered_notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    for idx, notification in enumerate(filtered_notifications):
        display_notification(notification, health_manager, idx)

def display_notification(notification, health_manager, idx=None):
    notification_type = notification.get("type", "info")
    read_status = notification.get("read", False)

    type_config = {
        "info": {"icon": "ℹ️", "color": "blue"},
        "success": {"icon": "✅", "color": "green"},
        "warning": {"icon": "⚠️", "color": "orange"},
        "error": {"icon": "❌", "color": "red"}
    }

    config = type_config.get(notification_type, type_config["info"])

    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            title = notification.get("title", "Notification")
            if not read_status:
                title = f"🟢 {title}"

            st.markdown(f"**{config['icon']} {title}**")
            st.write(notification.get("message", "No message content"))

            created_at = notification.get("created_at", "")
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at)
                    time_ago = get_time_ago(created_date)
                    st.caption(f"🕒 {time_ago}")
                except:
                    st.caption(f"🕒 {created_at[:10]}")

        with col2:
            username = st.session_state.get("username", "guest")
            notif_id = notification.get("id", str(uuid.uuid4()))

            # Use index to guarantee key uniqueness
            unique_hash = hashlib.md5(f"{username}-{notif_id}-{notification.get('title', '')}-{notification.get('message', '')}".encode()).hexdigest()
            read_key = f"read_{unique_hash}_{idx}"
            delete_key = f"delete_{unique_hash}_{idx}"

            if not read_status:
                if st.button("✅", key=read_key, help="Mark as read"):
                    health_manager.mark_notification_read(username, notif_id)
                    st.rerun()

            if st.button("🗑️", key=delete_key, help="Delete"):
                st.warning("⚠️ Delete feature coming soon!")

        st.markdown("---")

def show_notification_settings(health_manager):
    st.subheader("⚙️ Notification Settings")
    st.write("Customize your notification preferences:")

    with st.expander("🏥 Health Reminders"):
        daily = st.checkbox("Daily wellness check-in", value=True)
        med = st.checkbox("Medication reminders", value=True)
        appt = st.checkbox("Appointment reminders", value=True)
        exercise = st.checkbox("Exercise reminders", value=False)
        reminder_time = st.time_input("Preferred reminder time", value=datetime.strptime("09:00", "%H:%M").time())

    with st.expander("📊 Wellness Alerts"):
        score_drop = st.checkbox("Alert when wellness score drops significantly", value=True)
        goals = st.checkbox("Goal progress reminders", value=True)
        achievements = st.checkbox("Achievement notifications", value=True)

    with st.expander("🤖 AI Insights"):
        ai = st.checkbox("Weekly AI health insights", value=True)
        tips = st.checkbox("Personalized health tips", value=True)

    if st.button("💾 Save Settings", type="primary"):
        settings = {
            "daily": daily,
            "medication": med,
            "appointment": appt,
            "exercise": exercise,
            "reminder_time": str(reminder_time),
            "score_drop": score_drop,
            "goals": goals,
            "achievements": achievements,
            "ai": ai,
            "tips": tips
        }
        st.success("✅ Notification settings saved!")

def show_health_reminders(health_manager):
    st.subheader("📊 Health Reminders")
    col1, col2 = st.columns(2)

    if col1.button("💊 Medication Reminder"):
        create_medication_reminder(health_manager)
    if col1.button("🏃 Exercise Reminder"):
        create_exercise_reminder(health_manager)

    if col2.button("🩺 Check-up Reminder"):
        create_checkup_reminder(health_manager)
    if col2.button("💧 Hydration Reminder"):
        create_hydration_reminder(health_manager)

    st.markdown("---")
    st.subheader("➕ Create Custom Reminder")

    with st.form("custom_reminder"):
        title = st.text_input("Reminder Title", placeholder="e.g., Take vitamins")
        message = st.text_area("Reminder Message", placeholder="Don't forget to take your daily vitamins!")
        frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "One-time"])
        time = st.time_input("Reminder Time")

        if st.form_submit_button("⏰ Create Reminder"):
            if title and message:
                create_custom_reminder(health_manager, title, message, frequency, time)
                st.success("✅ Custom reminder created!")
                st.rerun()
            else:
                st.warning("Please fill in both title and message.")

def create_sample_notifications(health_manager):
    username = st.session_state.get("username", "guest")
    samples = [
        {"title": "Welcome to HealthAssist AI!", "message": "Start by updating your wellness data.", "type": "success"},
        {"title": "Daily Wellness Check", "message": "Log your daily wellness metrics.", "type": "info"},
        {"title": "Hydration Reminder", "message": "Stay hydrated throughout the day.", "type": "info"},
        {"title": "AI Model Ready", "message": "Your IBM Granite AI model is ready to assist.", "type": "success"}
    ]
    for n in samples:
        health_manager.add_notification(username, n["title"], n["message"], n["type"])

def create_medication_reminder(health_manager):
    health_manager.add_notification(
        st.session_state.username,
        "💊 Medication Reminder",
        "Time to take your medication.",
        "warning",
        expires_hours=8
    )
    st.success("💊 Medication reminder created!")

def create_exercise_reminder(health_manager):
    health_manager.add_notification(
        st.session_state.username,
        "🏃 Exercise Time",
        "Do a 15-minute walk!",
        "info",
        expires_hours=4
    )
    st.success("🏃 Exercise reminder created!")

def create_checkup_reminder(health_manager):
    health_manager.add_notification(
        st.session_state.username,
        "🩺 Health Check-up",
        "Schedule your regular health check-up.",
        "warning",
        expires_hours=48
    )
    st.success("🩺 Check-up reminder created!")

def create_hydration_reminder(health_manager):
    health_manager.add_notification(
        st.session_state.username,
        "💧 Stay Hydrated",
        "Drink water regularly!",
        "info",
        expires_hours=2
    )
    st.success("💧 Hydration reminder created!")

def create_custom_reminder(health_manager, title, message, frequency, time):
    expiry_hours = {"Daily": 24, "Weekly": 168, "Monthly": 720, "One-time": 24}
    health_manager.add_notification(
        st.session_state.username,
        f"⏰ {title}",
        f"{message}\n\nFrequency: {frequency}\nTime: {time}",
        "info",
        expires_hours=expiry_hours.get(frequency, 24)
    )

def mark_all_notifications_read(notifications, health_manager, username):
    for notification in notifications:
        if not notification.get("read", False):
            notif_id = notification.get("id", "")
            if notif_id:
                health_manager.mark_notification_read(username, notif_id)

def get_time_ago(dt):
    now = datetime.now()
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600} hour{'s' if diff.seconds // 3600 != 1 else ''} ago"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60} minute{'s' if diff.seconds // 60 != 1 else ''} ago"
    return "Just now"

if __name__ == "__main__":
    show_notifications()
