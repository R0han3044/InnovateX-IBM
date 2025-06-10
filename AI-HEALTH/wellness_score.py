import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import random

# Wellness Score and Health Analytics

def get_wellness_data():
    """Load or create the wellness data"""
    if os.path.exists('wellness_data.json'):
        with open('wellness_data.json', 'r') as f:
            return json.load(f)
    else:
        wellness_data = {
            "users": {}
        }
        save_wellness_data(wellness_data)
        return wellness_data

def save_wellness_data(wellness_data):
    """Save the wellness data"""
    with open('wellness_data.json', 'w') as f:
        json.dump(wellness_data, f, indent=4)

def get_user_wellness(username):
    """Get a user's wellness data"""
    wellness_data = get_wellness_data()
    
    # Create default data if user doesn't have any
    if username not in wellness_data["users"]:
        # Generate some initial sample data
        start_date = datetime.now() - timedelta(days=30)
        dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(31)]
        
        # Generate random wellness scores with an upward trend and some variation
        random.seed(username)  # Use username as seed for consistency
        base_scores = np.linspace(60, 75, 31)  # Base trend from 60 to 75
        variation = np.random.normal(0, 5, 31)  # Random variation
        scores = np.clip(base_scores + variation, 0, 100).astype(int)
        
        # Create component scores with different patterns
        physical = np.clip(np.random.normal(scores - 5, 10, 31), 0, 100).astype(int)
        mental = np.clip(np.random.normal(scores + 5, 8, 31), 0, 100).astype(int)
        nutrition = np.clip(np.random.normal(scores - 2, 7, 31), 0, 100).astype(int)
        sleep = np.clip(np.random.normal(scores + 2, 15, 31), 0, 100).astype(int)
        activity = np.clip(np.random.normal(scores, 12, 31), 0, 100).astype(int)
        
        # Create wellness record
        user_wellness = {
            "dates": dates,
            "overall_scores": scores.tolist(),
            "component_scores": {
                "physical": physical.tolist(),
                "mental": mental.tolist(),
                "nutrition": nutrition.tolist(),
                "sleep": sleep.tolist(),
                "activity": activity.tolist()
            },
            "health_insights": [],
            "wellness_activities": [],
            "last_updated": str(datetime.now())
        }
        
        wellness_data["users"][username] = user_wellness
        save_wellness_data(wellness_data)
    
    return wellness_data["users"][username]

def update_user_wellness(username, new_score=None, component_updates=None, activity=None, insight=None):
    """Update a user's wellness data"""
    wellness_data = get_wellness_data()
    
    # Get existing data or create if not exists
    user_wellness = get_user_wellness(username)
    
    # Update with today's timestamp
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if we need to append a new day or update the latest
    if len(user_wellness["dates"]) == 0 or user_wellness["dates"][-1] != today:
        # Add new day
        user_wellness["dates"].append(today)
        
        # If no specific new score is provided, use previous + some variation
        if new_score is None:
            if len(user_wellness["overall_scores"]) > 0:
                prev_score = user_wellness["overall_scores"][-1]
                # Random variation between -3 and +5 for slight upward bias
                variation = random.randint(-3, 5)
                new_score = max(0, min(100, prev_score + variation))
            else:
                new_score = random.randint(60, 80)  # Initial score
        
        user_wellness["overall_scores"].append(new_score)
        
        # Initialize component scores
        if component_updates is None:
            component_updates = {}
            
            # Generate component scores based on overall score if not provided
            for component in user_wellness["component_scores"]:
                if component not in component_updates:
                    # Random variation around overall score
                    variation = random.randint(-10, 10)
                    component_score = max(0, min(100, new_score + variation))
                    component_updates[component] = component_score
        
        # Update component scores
        for component, score in component_updates.items():
            if component in user_wellness["component_scores"]:
                user_wellness["component_scores"][component].append(score)
            else:
                # Initialize if new component
                user_wellness["component_scores"][component] = [score]
    else:
        # Update today's scores
        if new_score is not None:
            user_wellness["overall_scores"][-1] = new_score
        
        # Update component scores
        if component_updates:
            for component, score in component_updates.items():
                if component in user_wellness["component_scores"]:
                    if len(user_wellness["component_scores"][component]) == len(user_wellness["dates"]):
                        user_wellness["component_scores"][component][-1] = score
                    else:
                        # Fill in missing values if needed
                        while len(user_wellness["component_scores"][component]) < len(user_wellness["dates"]) - 1:
                            user_wellness["component_scores"][component].append(50)  # Default value
                        user_wellness["component_scores"][component].append(score)
                else:
                    # Initialize if new component
                    user_wellness["component_scores"][component] = [50] * (len(user_wellness["dates"]) - 1)
                    user_wellness["component_scores"][component].append(score)
    
    # Add wellness activity if provided
    if activity:
        if "wellness_activities" not in user_wellness:
            user_wellness["wellness_activities"] = []
            
        user_wellness["wellness_activities"].append({
            "activity": activity,
            "date": today,
            "timestamp": str(datetime.now())
        })
    
    # Add health insight if provided
    if insight:
        if "health_insights" not in user_wellness:
            user_wellness["health_insights"] = []
            
        user_wellness["health_insights"].append({
            "insight": insight,
            "date": today,
            "timestamp": str(datetime.now())
        })
    
    # Update timestamp
    user_wellness["last_updated"] = str(datetime.now())
    
    # Save updated data
    wellness_data["users"][username] = user_wellness
    save_wellness_data(wellness_data)
    
    return user_wellness

def calculate_wellness_score(health_data, user_info=None):
    """Calculate wellness score from health metrics"""
    # Default weights for different components
    weights = {
        "steps": 0.15,
        "sleep_hours": 0.20,
        "heart_rate": 0.15,
        "nutrition": 0.20,
        "mental": 0.20,
        "medication_adherence": 0.10
    }
    
    # Initialize scores dictionary
    scores = {}
    component_scores = {}
    
    # 1. Steps score (based on 10,000 steps daily target)
    if "steps" in health_data:
        steps = health_data["steps"]
        steps_score = min(100, int((steps / 10000) * 100))
        component_scores["activity"] = steps_score
    else:
        # Default activity score
        component_scores["activity"] = random.randint(60, 80)
    
    # 2. Sleep score (based on 7-9 hours as ideal)
    if "sleep_hours" in health_data:
        sleep_hours = health_data["sleep_hours"]
        if sleep_hours >= 7 and sleep_hours <= 9:
            sleep_score = 100
        elif sleep_hours < 7:
            sleep_score = int((sleep_hours / 7) * 100)
        else:  # sleep_hours > 9
            sleep_score = max(60, 100 - (sleep_hours - 9) * 10)
        component_scores["sleep"] = sleep_score
    else:
        # Default sleep score
        component_scores["sleep"] = random.randint(60, 80)
    
    # 3. Heart rate score (60-100 bpm as normal range for adults)
    if "heart_rate" in health_data:
        hr = health_data["heart_rate"]
        if hr >= 60 and hr <= 100:
            hr_score = 100
        elif hr < 60:  # Athlete's heart can be healthy with lower HR
            hr_score = max(70, 100 - (60 - hr) * 2)
        else:  # hr > 100
            hr_score = max(0, 100 - (hr - 100) * 3)
        component_scores["physical"] = hr_score
    else:
        # Default physical score
        component_scores["physical"] = random.randint(60, 80)
    
    # 4. Default nutrition score if not provided
    if "nutrition" not in component_scores:
        component_scores["nutrition"] = random.randint(60, 80)
    
    # 5. Default mental health score if not provided
    if "mental" not in component_scores:
        component_scores["mental"] = random.randint(60, 80)
    
    # Calculate weighted overall score
    overall_score = 0
    for component, score in component_scores.items():
        if component in weights:
            overall_score += score * weights.get(component, 0.1)
        else:
            overall_score += score * 0.1  # Default weight
    
    # Adjust for missing components
    total_weight = sum(weights.get(c, 0.1) for c in component_scores.keys())
    if total_weight > 0:
        overall_score = overall_score / total_weight
    
    # Round to integer
    overall_score = int(round(overall_score))
    
    return overall_score, component_scores

def get_wellness_insights(overall_score, component_scores, health_data=None, username=None):
    """Generate insights based on wellness scores"""
    insights = []
    
    # Overall wellness insights
    if overall_score >= 90:
        insights.append("Your overall wellness score is excellent! Keep up the great work with your healthy habits.")
    elif overall_score >= 80:
        insights.append("You're doing very well with your overall wellness. Small improvements in weaker areas could boost your health even further.")
    elif overall_score >= 70:
        insights.append("Your wellness score is good, but there's room for improvement in some areas. Focus on the components with lower scores.")
    elif overall_score >= 60:
        insights.append("Your wellness score is average. Consider making some lifestyle changes to improve your overall health and well-being.")
    else:
        insights.append("Your wellness score indicates that your health habits need attention. Focus on making gradual improvements in all areas.")
    
    # Component-specific insights
    for component, score in component_scores.items():
        if component == "physical" and score < 70:
            insights.append("Consider scheduling a check-up with your doctor to monitor your physical health metrics.")
        elif component == "mental" and score < 70:
            insights.append("Your mental wellness score suggests you might benefit from stress-reduction activities like meditation or mindfulness.")
        elif component == "nutrition" and score < 70:
            insights.append("Try incorporating more fruits, vegetables, and whole foods into your diet to improve your nutrition score.")
        elif component == "sleep" and score < 70:
            insights.append("Your sleep score is lower than ideal. Consider establishing a regular sleep schedule and creating a restful bedroom environment.")
        elif component == "activity" and score < 70:
            insights.append("Increasing your daily physical activity, even with short walks, could significantly improve your activity score.")
    
    # Dynamic insights based on data patterns (if username is provided)
    if username:
        wellness_data = get_user_wellness(username)
        
        # Check for trends in overall score
        if len(wellness_data["overall_scores"]) >= 7:  # At least a week of data
            recent_trend = wellness_data["overall_scores"][-7:]
            if all(recent_trend[i] <= recent_trend[i-1] for i in range(1, len(recent_trend))):
                insights.append("Your wellness score has been declining over the past week. Consider what factors might be affecting your health habits.")
            elif all(recent_trend[i] >= recent_trend[i-1] for i in range(1, len(recent_trend))):
                insights.append("Great job! Your wellness score has been improving consistently over the past week.")
            
            # Check for volatility
            if max(recent_trend) - min(recent_trend) > 20:
                insights.append("Your wellness score has been fluctuating significantly. More consistent health habits may help stabilize your well-being.")
    
    return insights

def show_wellness_score_page(username, patient_data=None):
    """Display the Wellness Score and Health Analytics page"""
    st.header("📊 Wellness Score & Health Analytics")
    
    # Get wellness data
    wellness_data = get_user_wellness(username)
    
    # Calculate today's wellness score from health data if available
    health_data = {}
    
    # Check if there's sample health data in session state
    if 'health_data' in st.session_state:
        # Get today's data or most recent
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = st.session_state.health_data[
            st.session_state.health_data['date'].dt.strftime("%Y-%m-%d") == today
        ]
        
        if not today_data.empty:
            health_data = {
                "steps": today_data['steps'].values[0],
                "sleep_hours": today_data['sleep_hours'].values[0],
                "heart_rate": today_data['heart_rate'].values[0]
            }
        else:
            # Use most recent data
            latest_data = st.session_state.health_data.iloc[-1]
            health_data = {
                "steps": latest_data['steps'],
                "sleep_hours": latest_data['sleep_hours'],
                "heart_rate": latest_data['heart_rate']
            }
    
    # Main wellness score display
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Get the latest overall score
        current_score = wellness_data["overall_scores"][-1] if wellness_data["overall_scores"] else 0
        
        # Create gauge chart for overall wellness score
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Wellness Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 60], 'color': "orange"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': current_score
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=30, r=30, t=30, b=30),
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Lookup tables for score interpretations
        score_categories = ["Needs Attention", "Fair", "Good", "Very Good", "Excellent"]
        score_colors = ["red", "orange", "blue", "teal", "green"]
        
        # Determine score category
        if current_score < 40:
            category_idx = 0
        elif current_score < 60:
            category_idx = 1
        elif current_score < 75:
            category_idx = 2
        elif current_score < 90:
            category_idx = 3
        else:
            category_idx = 4
        
        # Display score interpretation
        st.markdown(
            f"<div style='text-align: center; color: {score_colors[category_idx]}; padding: 10px; "
            f"border-radius: 5px; font-weight: bold; font-size: 18px;'>"
            f"{score_categories[category_idx]}"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Show last updated
        st.caption(f"Last updated: {wellness_data['last_updated'][:16]}")
    
    with col2:
        # Component scores visualization
        st.subheader("Health Components")
        
        # Get the latest component scores
        component_data = {}
        for component, scores in wellness_data["component_scores"].items():
            if scores:  # If there are any scores for this component
                component_data[component.capitalize()] = scores[-1]
        
        # Create radar chart for component scores
        categories = list(component_data.keys())
        values = list(component_data.values())
        
        # Add the first value at the end to close the polygon
        categories.append(categories[0])
        values.append(values[0])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Components',
            line_color='darkblue',
            fillcolor='rgba(0, 0, 128, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            height=300,
            margin=dict(l=30, r=30, t=30, b=30),
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Wellness score history chart
    st.subheader("Wellness Score History")
    
    # Time range selector
    time_range = st.selectbox(
        "Select time range:",
        ["Last 7 days", "Last 14 days", "Last 30 days", "All data"],
        index=0
    )
    
    # Convert time range to number of days
    if time_range == "Last 7 days":
        days = 7
    elif time_range == "Last 14 days":
        days = 14
    elif time_range == "Last 30 days":
        days = 30
    else:
        days = len(wellness_data["dates"])
    
    # Filter data for selected time range
    dates = wellness_data["dates"][-days:]
    scores = wellness_data["overall_scores"][-days:]
    
    # Create line chart
    df_history = pd.DataFrame({
        'Date': dates,
        'Score': scores
    })
    
    # Convert dates to datetime for proper plotting
    df_history['Date'] = pd.to_datetime(df_history['Date'])
    
    # Create line chart with Plotly
    fig = px.line(
        df_history, 
        x='Date', 
        y='Score',
        title='Wellness Score Trend',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Wellness Score",
        yaxis=dict(range=[0, 100]),
        hovermode="x unified"
    )
    
    # Add reference zones
    fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor="green", opacity=0.1)
    fig.add_hrect(y0=60, y1=80, line_width=0, fillcolor="yellow", opacity=0.1)
    fig.add_hrect(y0=40, y1=60, line_width=0, fillcolor="orange", opacity=0.1)
    fig.add_hrect(y0=0, y1=40, line_width=0, fillcolor="red", opacity=0.1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display component trends
    st.subheader("Health Component Trends")
    
    # Create tabs for different components
    components = list(wellness_data["component_scores"].keys())
    if components:
        # Let user select which components to display
        selected_components = st.multiselect(
            "Select components to display:",
            options=[comp.capitalize() for comp in components],
            default=[comp.capitalize() for comp in components[:min(3, len(components))]]
        )
        
        if selected_components:
            # Create DataFrame for component trends
            component_data = {
                'Date': dates
            }
            
            for comp in selected_components:
                comp_lower = comp.lower()
                if comp_lower in wellness_data["component_scores"]:
                    comp_scores = wellness_data["component_scores"][comp_lower][-days:]
                    # Pad with NaN if needed
                    if len(comp_scores) < len(dates):
                        comp_scores = [None] * (len(dates) - len(comp_scores)) + comp_scores
                    component_data[comp] = comp_scores
            
            df_components = pd.DataFrame(component_data)
            df_components['Date'] = pd.to_datetime(df_components['Date'])
            
            # Create line chart for component trends
            fig = px.line(
                df_components,
                x='Date',
                y=selected_components,
                title='Health Component Trends',
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Score",
                yaxis=dict(range=[0, 100]),
                hovermode="x unified",
                legend_title="Components"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Health insights section
    st.subheader("Health Insights")
    
    # Generate insights based on current scores
    overall_score = wellness_data["overall_scores"][-1] if wellness_data["overall_scores"] else 0
    component_scores = {}
    for component, scores in wellness_data["component_scores"].items():
        if scores:
            component_scores[component] = scores[-1]
    
    insights = get_wellness_insights(overall_score, component_scores, health_data, username)
    
    # Display insights
    for i, insight in enumerate(insights):
        st.info(insight, icon="🔍")
    
    # Wellness activity tracking
    st.subheader("Track Your Wellness Activity")
    
    # Allow users to record wellness activities
    cols = st.columns([3, 1])
    
    with cols[0]:
        activity = st.text_input("What did you do today for your wellness?", 
                                placeholder="e.g., 30-minute walk, meditation, yoga class")
    
    with cols[1]:
        if st.button("Log Activity", use_container_width=True):
            if activity:
                update_user_wellness(username, activity=activity)
                st.success("Activity logged successfully!")
                st.rerun()
    
    # Display recent wellness activities
    if "wellness_activities" in wellness_data and wellness_data["wellness_activities"]:
        st.subheader("Recent Wellness Activities")
        
        activities = wellness_data["wellness_activities"]
        
        # Display most recent activities first
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Show the most recent 5 activities
        for activity in activities[:5]:
            date = activity["date"]
            act = activity["activity"]
            st.markdown(f"**{date}**: {act}")
    
    # Manual update section
    with st.expander("Update Your Wellness Components", expanded=False):
        st.write("Use the sliders below to manually update your health components:")
        
        component_updates = {}
        cols = st.columns(2)
        
        # Define components and their descriptions
        component_info = {
            "physical": "Physical Health (medical conditions, pain levels, etc.)",
            "mental": "Mental Health (stress, mood, emotional well-being)",
            "nutrition": "Nutrition (diet quality, hydration, balanced eating)",
            "sleep": "Sleep Quality (duration, quality, feeling rested)",
            "activity": "Physical Activity (exercise, movement throughout day)"
        }
        
        i = 0
        for component, description in component_info.items():
            with cols[i % 2]:
                current_value = component_scores.get(component, 50)
                component_updates[component] = st.slider(
                    description,
                    0, 100, int(current_value),
                    help=f"Rate your {component} health from 0-100"
                )
            i += 1
        
        if st.button("Update Wellness Scores", use_container_width=True):
            # Calculate new overall score (average of components)
            new_overall = sum(component_updates.values()) / len(component_updates)
            
            # Update wellness data
            update_user_wellness(
                username,
                new_score=int(new_overall),
                component_updates=component_updates
            )
            
            st.success("Wellness scores updated successfully!")
            st.rerun()