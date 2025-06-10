import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta
import time

# Import notification system
from notification_system import create_notification, create_buddy_notifications, show_notifications

# Health Buddy - Virtual Health Companion

def get_buddy_data():
    """Load or create the buddy data"""
    if os.path.exists('buddy_data.json'):
        with open('buddy_data.json', 'r') as f:
            return json.load(f)
    else:
        buddy_data = {
            "users": {}
        }
        save_buddy_data(buddy_data)
        return buddy_data

def save_buddy_data(buddy_data):
    """Save the buddy data"""
    with open('buddy_data.json', 'w') as f:
        json.dump(buddy_data, f, indent=4)

def create_user_buddy(username, buddy_name=None):
    """Create a new buddy for a user"""
    buddy_data = get_buddy_data()
    
    # Default buddy name if not provided
    if not buddy_name:
        buddy_name = "Health Buddy"
    
    # Default personality traits
    personalities = [
        "supportive", "motivational", "encouraging", "positive", 
        "friendly", "gentle", "understanding", "enthusiastic"
    ]
    
    # Create buddy with random personality traits
    buddy = {
        "name": buddy_name,
        "personality_traits": random.sample(personalities, 3),
        "created_at": str(datetime.now()),
        "last_interaction": str(datetime.now()),
        "streak": 0,
        "messages": [],
        "health_goals": [],
        "reminders": [],
        "achievements": []
    }
    
    # Add buddy to user's data
    buddy_data["users"][username] = buddy
    save_buddy_data(buddy_data)
    
    # Create welcome notification
    create_notification(
        username,
        f"Meet {buddy_name}!",
        f"Your new Health Buddy {buddy_name} is here to support your health journey. Check out the Health Buddy page to get started!",
        notification_type="success"
    )
    
    return buddy

def get_user_buddy(username):
    """Get a user's buddy"""
    buddy_data = get_buddy_data()
    
    # Create buddy if user doesn't have one
    if username not in buddy_data["users"]:
        return create_user_buddy(username)
    
    # Check streak and update if needed
    buddy = buddy_data["users"][username]
    last_interaction = datetime.fromisoformat(buddy["last_interaction"].replace('Z', '+00:00'))
    today = datetime.now()
    
    # If last interaction was yesterday, increment streak
    if (today.date() - last_interaction.date()).days == 1:
        buddy["streak"] += 1
        buddy["last_interaction"] = str(today)
        buddy_data["users"][username] = buddy
        save_buddy_data(buddy_data)
        
        # Create streak notification for milestones
        if buddy["streak"] in [7, 14, 30, 60, 90, 180, 365]:
            create_notification(
                username,
                f"{buddy['streak']} Day Streak!",
                f"Congratulations! You've maintained a {buddy['streak']}-day streak with {buddy['name']}. Keep up the great work!",
                notification_type="success"
            )
    
    # If last interaction was more than a day ago (but not today), reset streak
    elif (today.date() - last_interaction.date()).days > 1:
        old_streak = buddy["streak"]
        buddy["streak"] = 0
        buddy["last_interaction"] = str(today)
        buddy_data["users"][username] = buddy
        save_buddy_data(buddy_data)
        
        if old_streak > 3:
            create_notification(
                username,
                "Streak Reset",
                f"Your {old_streak}-day streak with {buddy['name']} has been reset. Visit your Health Buddy daily to maintain your streak!",
                notification_type="warning"
            )
    
    # If interaction is on the same day, just return buddy without updating
    return buddy_data["users"][username]

def update_buddy(username, data):
    """Update buddy data"""
    buddy_data = get_buddy_data()
    
    # Create buddy if user doesn't have one
    if username not in buddy_data["users"]:
        buddy = create_user_buddy(username)
    else:
        buddy = buddy_data["users"][username]
    
    # Update provided fields
    for key, value in data.items():
        if key in buddy:
            buddy[key] = value
    
    # Update last interaction
    buddy["last_interaction"] = str(datetime.now())
    
    # Save updated buddy
    buddy_data["users"][username] = buddy
    save_buddy_data(buddy_data)
    
    return buddy

def add_buddy_message(username, message, from_buddy=True):
    """Add a message to the buddy's message history"""
    buddy_data = get_buddy_data()
    
    # Get or create buddy
    if username not in buddy_data["users"]:
        buddy = create_user_buddy(username)
    else:
        buddy = buddy_data["users"][username]
    
    # Initialize messages array if not exists
    if "messages" not in buddy:
        buddy["messages"] = []
    
    # Create message object
    message_obj = {
        "text": message,
        "from_buddy": from_buddy,
        "timestamp": str(datetime.now())
    }
    
    # Add message to history
    buddy["messages"].append(message_obj)
    
    # Limit message history to last 50 messages
    if len(buddy["messages"]) > 50:
        buddy["messages"] = buddy["messages"][-50:]
    
    # Update last interaction
    buddy["last_interaction"] = str(datetime.now())
    
    # Save updated buddy
    buddy_data["users"][username] = buddy
    save_buddy_data(buddy_data)
    
    return message_obj

def add_health_goal(username, goal, target_date=None):
    """Add a health goal for the user"""
    buddy_data = get_buddy_data()
    
    # Get or create buddy
    if username not in buddy_data["users"]:
        buddy = create_user_buddy(username)
    else:
        buddy = buddy_data["users"][username]
    
    # Initialize health goals array if not exists
    if "health_goals" not in buddy:
        buddy["health_goals"] = []
    
    # Create goal ID
    goal_id = f"goal_{len(buddy['health_goals']) + 1}_{int(time.time())}"
    
    # Parse target date if provided
    if target_date:
        try:
            # Validate date format
            parsed_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
            target_date = str(parsed_date)
        except (ValueError, TypeError):
            # Default to 30 days from now if invalid
            target_date = str(datetime.now() + timedelta(days=30))
    else:
        # Default to 30 days from now
        target_date = str(datetime.now() + timedelta(days=30))
    
    # Create goal object
    goal_obj = {
        "id": goal_id,
        "description": goal,
        "created_at": str(datetime.now()),
        "target_date": target_date,
        "completed": False,
        "progress": 0,
        "check_ins": []
    }
    
    # Add goal to health goals
    buddy["health_goals"].append(goal_obj)
    
    # Create notification for new goal
    create_notification(
        username,
        "New Health Goal Created",
        f"You've set a new health goal: {goal}. Your buddy will help you track your progress!",
        notification_type="info"
    )
    
    # Update last interaction
    buddy["last_interaction"] = str(datetime.now())
    
    # Save updated buddy
    buddy_data["users"][username] = buddy
    save_buddy_data(buddy_data)
    
    return goal_obj

def update_health_goal(username, goal_id, data):
    """Update a health goal"""
    buddy_data = get_buddy_data()
    
    # Return False if user doesn't have a buddy
    if username not in buddy_data["users"]:
        return False
    
    buddy = buddy_data["users"][username]
    
    # Return False if health goals array doesn't exist
    if "health_goals" not in buddy:
        return False
    
    # Find the goal with matching ID
    for i, goal in enumerate(buddy["health_goals"]):
        if goal["id"] == goal_id:
            # Handle progress updates
            if "progress" in data:
                old_progress = goal["progress"]
                new_progress = data["progress"]
                
                # Add check-in for progress update
                if "check_ins" not in goal:
                    goal["check_ins"] = []
                
                goal["check_ins"].append({
                    "date": str(datetime.now()),
                    "old_progress": old_progress,
                    "new_progress": new_progress,
                    "note": data.get("note", "")
                })
                
                # Create notification for significant progress
                if new_progress >= 50 and old_progress < 50:
                    create_notification(
                        username,
                        "Halfway to Your Goal!",
                        f"You're now 50% of the way to achieving your goal: {goal['description']}. Keep up the great work!",
                        notification_type="success"
                    )
                elif new_progress == 100 and old_progress < 100:
                    create_notification(
                        username,
                        "Goal Achieved!",
                        f"Congratulations! You've achieved your health goal: {goal['description']}",
                        notification_type="success"
                    )
            
            # Update completion status
            if "completed" in data and data["completed"] and not goal["completed"]:
                # If marking as complete, update the buddy's achievements
                if "achievements" not in buddy:
                    buddy["achievements"] = []
                
                buddy["achievements"].append({
                    "type": "goal_completed",
                    "description": goal["description"],
                    "date": str(datetime.now())
                })
                
                # Create completion notification
                create_notification(
                    username,
                    "Goal Completed!",
                    f"Congratulations on completing your health goal: {goal['description']}",
                    notification_type="success"
                )
            
            # Update goal fields
            for key, value in data.items():
                if key in goal:
                    buddy["health_goals"][i][key] = value
            
            # Update last interaction
            buddy["last_interaction"] = str(datetime.now())
            
            # Save updated buddy
            buddy_data["users"][username] = buddy
            save_buddy_data(buddy_data)
            
            return True
    
    return False

def add_buddy_reminder(username, title, time, recurrence="once", notes=""):
    """Add a reminder for the user"""
    buddy_data = get_buddy_data()
    
    # Get or create buddy
    if username not in buddy_data["users"]:
        buddy = create_user_buddy(username)
    else:
        buddy = buddy_data["users"][username]
    
    # Initialize reminders array if not exists
    if "reminders" not in buddy:
        buddy["reminders"] = []
    
    # Create reminder ID
    reminder_id = f"reminder_{len(buddy['reminders']) + 1}_{int(time.time())}"
    
    # Create reminder object
    reminder_obj = {
        "id": reminder_id,
        "title": title,
        "time": time,
        "recurrence": recurrence,  # once, daily, weekly, monthly
        "notes": notes,
        "created_at": str(datetime.now()),
        "completed": False
    }
    
    # Add reminder to reminders
    buddy["reminders"].append(reminder_obj)
    
    # Create notification for new reminder
    create_notification(
        username,
        "New Reminder Set",
        f"Your Health Buddy will remind you: {title}",
        notification_type="info"
    )
    
    # Update last interaction
    buddy["last_interaction"] = str(datetime.now())
    
    # Save updated buddy
    buddy_data["users"][username] = buddy
    save_buddy_data(buddy_data)
    
    return reminder_obj

def update_buddy_reminder(username, reminder_id, data):
    """Update a reminder"""
    buddy_data = get_buddy_data()
    
    # Return False if user doesn't have a buddy
    if username not in buddy_data["users"]:
        return False
    
    buddy = buddy_data["users"][username]
    
    # Return False if reminders array doesn't exist
    if "reminders" not in buddy:
        return False
    
    # Find the reminder with matching ID
    for i, reminder in enumerate(buddy["reminders"]):
        if reminder["id"] == reminder_id:
            # Update reminder fields
            for key, value in data.items():
                if key in reminder:
                    buddy["reminders"][i][key] = value
            
            # If marking as complete, add completion notification
            if "completed" in data and data["completed"] and not reminder["completed"]:
                create_notification(
                    username,
                    "Reminder Completed",
                    f"You've completed your reminder: {reminder['title']}",
                    notification_type="success"
                )
            
            # Update last interaction
            buddy["last_interaction"] = str(datetime.now())
            
            # Save updated buddy
            buddy_data["users"][username] = buddy
            save_buddy_data(buddy_data)
            
            return True
    
    return False

def get_buddy_greeting(buddy):
    """Get a greeting from the buddy based on time of day and personality"""
    # Determine time of day
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"
    
    # Get buddy personality traits
    personality = buddy.get("personality_traits", ["friendly"])
    
    # Greeting templates based on personality traits
    greetings = {
        "supportive": [
            f"Good {time_of_day}! I'm here to support your health journey today.",
            f"Hello! How can I support your well-being this {time_of_day}?",
            f"I'm ready to help you stay on track this {time_of_day}!"
        ],
        "motivational": [
            f"Good {time_of_day}! Let's make today count for your health!",
            f"It's a great {time_of_day} to work on your health goals!",
            f"Ready to crush your health goals this {time_of_day}?"
        ],
        "encouraging": [
            f"Good {time_of_day}! Every small step matters, and I'm proud of you for being here.",
            f"You're doing great just by checking in this {time_of_day}!",
            f"I believe in you! What health goals are we focusing on this {time_of_day}?"
        ],
        "positive": [
            f"Good {time_of_day}! Today is full of healthy possibilities!",
            f"Hello! What positive health choice will you make this {time_of_day}?",
            f"It's going to be a wonderful {time_of_day} for your well-being!"
        ],
        "friendly": [
            f"Hey there! How's your {time_of_day} going?",
            f"Hi friend! What can I help you with this {time_of_day}?",
            f"Hello! I'm happy to chat with you this {time_of_day}!"
        ],
        "gentle": [
            f"Good {time_of_day}. How are you feeling today?",
            f"Hello. I'm here if you need any gentle guidance today.",
            f"Taking a moment for your health this {time_of_day} is wonderful."
        ],
        "understanding": [
            f"Good {time_of_day}. How are you really doing today?",
            f"I'm here to listen and understand your health concerns this {time_of_day}.",
            f"Health journeys have ups and downs. How's yours going this {time_of_day}?"
        ],
        "enthusiastic": [
            f"Awesome {time_of_day}! I'm SO excited to help with your health today!",
            f"HI THERE! Ready for an AMAZING {time_of_day} of health and wellness?!",
            f"Let's make this the BEST {time_of_day} ever for your health journey!"
        ]
    }
    
    # Select a personality trait and a random greeting
    trait = random.choice(personality) if personality else "friendly"
    trait = trait if trait in greetings else "friendly"
    greeting = random.choice(greetings[trait])
    
    # Add buddy name
    greeting = f"{greeting} I'm {buddy['name']}."
    
    # Add streak mention if applicable
    if buddy.get("streak", 0) > 0:
        streak = buddy["streak"]
        if streak == 1:
            greeting += f" You've checked in for 1 day in a row!"
        else:
            greeting += f" You've checked in for {streak} days in a row!"
    
    return greeting

def get_buddy_response(message, buddy, username, patient_data=None):
    """Generate a response from the buddy based on the user's message"""
    # Low-tech, pattern-matching responses for demo purposes
    # In a real app, this would use a more sophisticated NLP approach
    
    message_lower = message.lower()
    
    # Get buddy personality traits
    personality = buddy.get("personality_traits", ["friendly"])
    primary_trait = personality[0] if personality else "friendly"
    
    # Common responses based on personality trait
    responses = {
        "supportive": {
            "greeting": [
                f"Hi there! I'm here to support your health journey. How can I help today?",
                f"Hello! I'm always here for you. What's on your mind regarding your health?",
                f"Welcome back! I'm here to support you every step of the way."
            ],
            "health": [
                "Taking care of your health is so important. I'm proud of you for focusing on it.",
                "Your health journey matters, and I'm here to support you through it.",
                "Every step you take towards better health is worthwhile. How can I support you today?"
            ],
            "goal": [
                "Setting health goals is a wonderful way to make progress. I believe in you!",
                "I'm here to support you with your health goals. What small step can you take today?",
                "Your goals matter, and I'm here to help you achieve them. Let's break it down into manageable steps."
            ]
        },
        "motivational": {
            "greeting": [
                "Let's crush your health goals today! What are we focusing on?",
                "Every day is a new opportunity for better health. Ready to make it count?",
                "Your health journey is a marathon, not a sprint. Let's keep moving forward!"
            ],
            "health": [
                "Your health is your greatest asset. Let's make today count!",
                "Small, consistent actions lead to big health improvements. You've got this!",
                "Today's choices shape tomorrow's health. What positive choice will you make today?"
            ],
            "goal": [
                "Goals give us direction! Let's break yours down into actionable steps.",
                "Your health goals are within reach. Stay committed, stay focused!",
                "Progress over perfection. Every step toward your goal matters!"
            ]
        },
        "friendly": {
            "greeting": [
                "Hey there! How's your day going?",
                "Hi friend! What's on your mind today?",
                "Hello! Always nice to chat with you about your health journey."
            ],
            "health": [
                "Health is about balance. How are you finding your balance today?",
                "I'm here for all your health questions! What can I help with?",
                "Your well-being matters to me. Let's chat about how you're doing."
            ],
            "goal": [
                "Friends help friends achieve their goals! What are we working on?",
                "I'd love to hear about your health goals! What are you focusing on?",
                "Goals are more fun when we work on them together. How can I help with yours?"
            ]
        }
    }
    
    # Use friendly as fallback trait if needed
    trait_responses = responses.get(primary_trait, responses["friendly"])
    
    # Default response if no patterns match
    default_responses = [
        f"I'm here to help with your health journey. Can you tell me more?",
        f"That's interesting. How does that relate to your health goals?",
        f"I'm listening. What else is on your mind about your health?"
    ]
    
    # Check for specific patterns and return appropriate responses
    
    # Greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "howdy", "greetings"]):
        return random.choice(trait_responses.get("greeting", default_responses))
    
    # Health questions
    if any(word in message_lower for word in ["health", "healthy", "wellness", "well-being", "wellbeing"]):
        return random.choice(trait_responses.get("health", default_responses))
    
    # Goal-related
    if any(word in message_lower for word in ["goal", "aim", "target", "objective", "plan"]):
        return random.choice(trait_responses.get("goal", default_responses))
    
    # Mood/emotions
    if any(word in message_lower for word in ["happy", "sad", "anxious", "stressed", "tired", "exhausted"]):
        return "Your emotional well-being is just as important as your physical health. How can I help you feel better today?"
    
    # Exercise-related
    if any(word in message_lower for word in ["exercise", "workout", "run", "jog", "walk", "gym"]):
        return "Exercise is great for both physical and mental health! Even small amounts of movement can make a big difference."
    
    # Diet-related
    if any(word in message_lower for word in ["diet", "eat", "food", "nutrition", "meal"]):
        return "A balanced diet is key to good health. Focus on whole foods, plenty of vegetables, and staying hydrated!"
    
    # Sleep-related
    if any(word in message_lower for word in ["sleep", "tired", "insomnia", "rest", "nap"]):
        return "Quality sleep is essential for health. Aim for 7-9 hours and try to maintain a consistent sleep schedule."
    
    # Medication-related
    if any(word in message_lower for word in ["medicine", "medication", "pill", "drug", "prescription"]):
        return "It's important to take medications as prescribed. Would you like me to set a reminder for you?"
    
    # Stress-related
    if any(word in message_lower for word in ["stress", "anxious", "anxiety", "worry", "overwhelmed"]):
        return "Managing stress is crucial for your overall health. Deep breathing, meditation, and regular exercise can all help."
    
    # Thank you
    if any(word in message_lower for word in ["thanks", "thank you", "appreciate"]):
        return "You're very welcome! I'm always here to support your health journey."
    
    # Default response
    return random.choice(default_responses)

def show_health_buddy_page(username, patient_data=None):
    """Display the Health Buddy page"""
    st.header("🤖 Health Buddy")
    
    # Get or create buddy
    buddy = get_user_buddy(username)
    
    # Create buddy notifications
    create_buddy_notifications(username, buddy)
    
    # Show sidebar notifications
    show_notifications(username, location="sidebar")
    
    # Display buddy information
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Display buddy avatar (placeholder)
        st.image("https://api.dicebear.com/6.x/bottts/svg?seed=" + buddy["name"], width=150)
        
        # Display streak
        if buddy.get("streak", 0) > 0:
            st.markdown(f"**Streak: {buddy['streak']} days**")
        
        # Edit buddy button
        if st.button("Customize Buddy", use_container_width=True):
            st.session_state.buddy_customize = True
    
    with col2:
        # Display buddy greeting
        st.markdown(f"### {buddy['name']}")
        st.markdown(f"*{get_buddy_greeting(buddy)}*")
        
        # Display personality traits
        traits = buddy.get("personality_traits", [])
        if traits:
            st.markdown("**Personality:** " + ", ".join(traits))
    
    # Customize buddy form
    if st.session_state.get("buddy_customize", False):
        st.markdown("---")
        st.subheader("Customize Your Health Buddy")
        
        # Buddy name input
        new_name = st.text_input("Buddy Name", value=buddy["name"])
        
        # Personality traits selection
        personality_options = [
            "supportive", "motivational", "encouraging", "positive", 
            "friendly", "gentle", "understanding", "enthusiastic"
        ]
        
        selected_traits = st.multiselect(
            "Personality Traits (select up to 3)",
            options=personality_options,
            default=buddy.get("personality_traits", ["friendly"]),
            max_selections=3
        )
        
        # Save button
        if st.button("Save Changes", use_container_width=True):
            update_data = {
                "name": new_name,
                "personality_traits": selected_traits
            }
            update_buddy(username, update_data)
            st.session_state.buddy_customize = False
            st.success("Buddy customized successfully!")
            st.rerun()
    
    # Main interaction area
    st.markdown("---")
    
    # Tabs for different buddy features
    tab1, tab2, tab3 = st.tabs(["Chat", "Health Goals", "Reminders"])
    
    with tab1:
        # Chat history
        st.subheader("Chat with Your Health Buddy")
        
        # Display chat history
        messages = buddy.get("messages", [])
        
        # Create chat container with scrolling
        chat_container = st.container()
        
        with chat_container:
            # Reverse messages for display (newest at bottom)
            for msg in messages[-10:]:
                if msg["from_buddy"]:
                    st.markdown(f"**{buddy['name']}:** {msg['text']}")
                else:
                    st.markdown(f"**You:** {msg['text']}")
        
        # Message input
        user_message = st.text_input("Type a message to your Health Buddy")
        
        if user_message:
            # Add user message to history
            add_buddy_message(username, user_message, from_buddy=False)
            
            # Generate buddy response
            response = get_buddy_response(user_message, buddy, username, patient_data)
            
            # Add buddy response to history
            add_buddy_message(username, response, from_buddy=True)
            
            # Clear input and refresh
            st.rerun()
    
    with tab2:
        # Health goals
        st.subheader("Health Goals")
        
        # Get existing goals
        goals = buddy.get("health_goals", [])
        
        # Add new goal form
        with st.expander("Add New Health Goal", expanded=not goals):
            goal_desc = st.text_area("Goal Description", placeholder="e.g., Walk 10,000 steps daily")
            
            cols = st.columns(2)
            with cols[0]:
                target_date = st.date_input("Target Date", value=datetime.now() + timedelta(days=30))
            
            if st.button("Add Goal", use_container_width=True):
                if goal_desc:
                    # Convert target date to string
                    target_date_str = str(target_date)
                    
                    # Add the goal
                    add_health_goal(username, goal_desc, target_date_str)
                    st.success("Health goal added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a goal description")
        
        # Display existing goals
        if not goals:
            st.info("You haven't set any health goals yet. Add one to get started!")
        else:
            # Sort goals: incomplete first, then by target date
            sorted_goals = sorted(
                goals, 
                key=lambda g: (g.get("completed", False), 
                              datetime.fromisoformat(g.get("target_date", str(datetime.now())).replace('Z', '+00:00')))
            )
            
            for i, goal in enumerate(sorted_goals):
                # Calculate days until target
                try:
                    target_date = datetime.fromisoformat(goal.get("target_date", str(datetime.now())).replace('Z', '+00:00'))
                    days_left = (target_date - datetime.now()).days
                    date_color = "red" if days_left < 0 else "orange" if days_left < 7 else "green"
                    date_status = "overdue!" if days_left < 0 else f"{days_left} days left"
                except (ValueError, TypeError):
                    date_color = "grey"
                    date_status = "no deadline"
                
                # Create a container for each goal
                with st.container():
                    # Goal header with completion checkbox
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        completed = goal.get("completed", False)
                        title_format = "~~" if completed else ""
                        st.markdown(f"#### {title_format}{goal.get('description', 'Goal')}{title_format}")
                    
                    with col2:
                        completed = st.checkbox("Completed", value=completed, key=f"goal_{goal.get('id', i)}")
                        if completed != goal.get("completed", False):
                            update_health_goal(username, goal.get("id"), {"completed": completed})
                            st.rerun()
                    
                    # Goal details
                    st.markdown(f"Target date: <span style='color:{date_color}'>{target_date.strftime('%Y-%m-%d')} ({date_status})</span>", unsafe_allow_html=True)
                    
                    # Progress tracking
                    progress = goal.get("progress", 0)
                    st.progress(progress / 100)
                    
                    # Update progress
                    if not completed:
                        new_progress = st.slider("Progress", 0, 100, progress, key=f"progress_{goal.get('id', i)}")
                        
                        if new_progress != progress:
                            note = st.text_input("Add a note about your progress (optional)", key=f"note_{goal.get('id', i)}")
                            
                            if st.button("Update Progress", key=f"update_{goal.get('id', i)}"):
                                update_health_goal(username, goal.get("id"), {
                                    "progress": new_progress,
                                    "note": note
                                })
                                st.success("Progress updated!")
                                st.rerun()
                    
                    # Check-ins/history
                    if "check_ins" in goal and goal["check_ins"]:
                        with st.expander("View Progress History"):
                            for check in reversed(goal["check_ins"]):
                                check_date = datetime.fromisoformat(check.get("date", "").replace('Z', '+00:00'))
                                st.markdown(f"**{check_date.strftime('%Y-%m-%d')}**: Progress updated from {check.get('old_progress', 0)}% to {check.get('new_progress', 0)}%")
                                if check.get("note"):
                                    st.markdown(f"> {check.get('note')}")
                    
                    st.markdown("---")
    
    with tab3:
        # Reminders
        st.subheader("Health Reminders")
        
        # Get existing reminders
        reminders = buddy.get("reminders", [])
        
        # Add new reminder form
        with st.expander("Add New Reminder", expanded=not reminders):
            reminder_title = st.text_input("Reminder Title", placeholder="e.g., Take medication")
            
            cols = st.columns(2)
            with cols[0]:
                reminder_time = st.time_input("Time", value=datetime.now().time())
            
            with cols[1]:
                recurrence = st.selectbox(
                    "Recurrence",
                    options=["Once", "Daily", "Weekly", "Monthly"],
                    index=1
                )
            
            reminder_notes = st.text_area("Notes (optional)", placeholder="Additional details for your reminder")
            
            if st.button("Add Reminder", use_container_width=True):
                if reminder_title:
                    # Convert time to string
                    time_str = reminder_time.strftime("%H:%M")
                    
                    # Add the reminder
                    add_buddy_reminder(username, reminder_title, time_str, recurrence.lower(), reminder_notes)
                    st.success("Reminder added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a reminder title")
        
        # Display existing reminders
        if not reminders:
            st.info("You haven't set any reminders yet. Add one to get started!")
        else:
            # Sort reminders: incomplete first, then by time
            sorted_reminders = sorted(
                reminders, 
                key=lambda r: (r.get("completed", False), r.get("time", "00:00"))
            )
            
            for i, reminder in enumerate(sorted_reminders):
                with st.container():
                    # Reminder header with completion checkbox
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        completed = reminder.get("completed", False)
                        title_format = "~~" if completed else ""
                        st.markdown(f"#### {title_format}{reminder.get('title', 'Reminder')}{title_format}")
                    
                    with col2:
                        completed = st.checkbox("Done", value=completed, key=f"reminder_{reminder.get('id', i)}")
                        if completed != reminder.get("completed", False):
                            update_buddy_reminder(username, reminder.get("id"), {"completed": completed})
                            st.rerun()
                    
                    # Reminder details
                    time_str = reminder.get("time", "")
                    recurrence = reminder.get("recurrence", "once").capitalize()
                    st.markdown(f"**Time:** {time_str} | **Recurrence:** {recurrence}")
                    
                    if reminder.get("notes"):
                        st.markdown(f"**Notes:** {reminder.get('notes')}")
                    
                    st.markdown("---")
    
    # Initialize session state if not exists
    if "buddy_customize" not in st.session_state:
        st.session_state.buddy_customize = False