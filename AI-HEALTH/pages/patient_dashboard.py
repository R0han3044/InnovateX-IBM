import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.medical_data import generate_sample_health_data

def show_patient_dashboard():
    """
    Display the Patient Health Dashboard page with visualizations
    of health metrics and activity data.
    """
    st.header("📊 Health Dashboard")
    st.markdown("""
    Track your health metrics and visualize your progress over time.
    This dashboard provides an overview of your health data and trends.
    """)
    
    # Check if user profile is complete
    if not st.session_state.user_data.get('name') or not st.session_state.user_data.get('age'):
        st.warning("Please complete your profile information in the sidebar for a personalized dashboard.")
    
    # Initialize health tracking data if not present
    if 'health_data' not in st.session_state:
        # Generate sample health data for visualization purposes
        st.session_state.health_data = generate_sample_health_data(days=30)
    
    # Dashboard time range selector
    time_range = st.selectbox(
        "Select time range:",
        ["Last 7 days", "Last 14 days", "Last 30 days", "Last 90 days"],
        index=2  # Default to 30 days
    )
    
    # Convert time range to number of days
    days_mapping = {
        "Last 7 days": 7,
        "Last 14 days": 14,
        "Last 30 days": 30,
        "Last 90 days": 90
    }
    days = days_mapping[time_range]
    
    # Filter data based on selected time range
    end_date = pd.Timestamp.now().floor('D')
    start_date = end_date - pd.Timedelta(days=days-1)
    
    # If we don't have enough data, generate more
    if len(st.session_state.health_data) < days:
        st.session_state.health_data = generate_sample_health_data(days=max(90, days))
    
    filtered_data = st.session_state.health_data[
        (st.session_state.health_data['date'] >= start_date) & 
        (st.session_state.health_data['date'] <= end_date)
    ].copy()
    
    # Main dashboard layout
    st.subheader("Health Metrics Overview")
    
    # Metrics cards
    cols = st.columns(3)
    
    # Calculate average metrics for the selected period
    avg_steps = int(filtered_data['steps'].mean())
    avg_sleep = round(filtered_data['sleep_hours'].mean(), 1)
    avg_heart_rate = int(filtered_data['heart_rate'].mean())
    
    # Display metric cards
    with cols[0]:
        st.metric(
            label="Avg. Daily Steps",
            value=f"{avg_steps:,}",
            delta=f"{int(avg_steps - 8000)}" if avg_steps != 8000 else None,
            delta_color="normal"
        )
    
    with cols[1]:
        st.metric(
            label="Avg. Sleep (hours)",
            value=avg_sleep,
            delta=f"{round(avg_sleep - 7.0, 1)}" if avg_sleep != 7.0 else None,
            delta_color="normal"
        )
    
    with cols[2]:
        st.metric(
            label="Avg. Heart Rate (BPM)",
            value=avg_heart_rate,
            delta=f"{int(avg_heart_rate - 70)}" if avg_heart_rate != 70 else None,
            delta_color="inverse"  # Lower heart rate is generally better
        )
    
    # Create trend visualizations
    st.subheader("Health Trends")
    
    # Daily steps chart
    fig_steps = px.line(
        filtered_data, 
        x='date', 
        y='steps',
        title='Daily Steps',
        markers=True
    )
    fig_steps.update_layout(
        xaxis_title="Date",
        yaxis_title="Steps",
        hovermode="x unified"
    )
    fig_steps.add_hline(
        y=10000, 
        line_dash="dash", 
        line_color="green",
        annotation_text="Recommended Steps",
        annotation_position="top right"
    )
    st.plotly_chart(fig_steps, use_container_width=True)
    
    # Sleep hours and heart rate charts
    cols = st.columns(2)
    
    with cols[0]:
        # Sleep hours chart
        fig_sleep = px.line(
            filtered_data, 
            x='date', 
            y='sleep_hours',
            title='Sleep Duration',
            markers=True
        )
        fig_sleep.update_layout(
            xaxis_title="Date",
            yaxis_title="Hours",
            hovermode="x unified",
            yaxis=dict(range=[4, 10])
        )
        fig_sleep.add_hrect(
            y0=7, y1=9,
            line_width=0, 
            fillcolor="green", 
            opacity=0.2,
            annotation_text="Ideal Range",
            annotation_position="top right"
        )
        st.plotly_chart(fig_sleep, use_container_width=True)
    
    with cols[1]:
        # Heart rate chart
        fig_hr = px.line(
            filtered_data, 
            x='date', 
            y='heart_rate',
            title='Resting Heart Rate',
            markers=True
        )
        fig_hr.update_layout(
            xaxis_title="Date",
            yaxis_title="BPM",
            hovermode="x unified",
            yaxis=dict(range=[50, 100])
        )
        fig_hr.add_hrect(
            y0=60, y1=80,
            line_width=0, 
            fillcolor="green", 
            opacity=0.2,
            annotation_text="Normal Range",
            annotation_position="top right"
        )
        st.plotly_chart(fig_hr, use_container_width=True)
    
    # Weekly summary
    st.subheader("Weekly Summary")
    
    # Group data by week and calculate averages
    filtered_data['week'] = filtered_data['date'].dt.isocalendar().week
    weekly_data = filtered_data.groupby('week').agg({
        'steps': 'mean',
        'sleep_hours': 'mean',
        'heart_rate': 'mean',
        'date': 'min'  # Get the first day of each week
    }).reset_index()
    
    # Weekly comparison chart
    fig_weekly = go.Figure()
    
    # Add traces for each metric
    fig_weekly.add_trace(go.Bar(
        x=weekly_data['date'],
        y=weekly_data['steps'] / 1000,  # Convert to thousands for scale
        name='Steps (thousands)',
        marker_color='blue'
    ))
    
    fig_weekly.add_trace(go.Bar(
        x=weekly_data['date'],
        y=weekly_data['sleep_hours'],
        name='Sleep (hours)',
        marker_color='purple'
    ))
    
    fig_weekly.add_trace(go.Bar(
        x=weekly_data['date'],
        y=weekly_data['heart_rate'] / 10,  # Scale down for visibility
        name='Heart Rate (tens)',
        marker_color='red'
    ))
    
    fig_weekly.update_layout(
        title='Weekly Health Metrics Comparison',
        xaxis_title='Week Starting',
        yaxis_title='Value (Scaled)',
        barmode='group',
        hovermode="x unified"
    )
    
    st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Health insights based on data
    st.subheader("Health Insights")
    
    # Calculate some basic insights
    steps_trend = filtered_data['steps'].iloc[-7:].mean() - filtered_data['steps'].iloc[-14:-7].mean()
    sleep_trend = filtered_data['sleep_hours'].iloc[-7:].mean() - filtered_data['sleep_hours'].iloc[-14:-7].mean()
    hr_trend = filtered_data['heart_rate'].iloc[-7:].mean() - filtered_data['heart_rate'].iloc[-14:-7].mean()
    
    # Display insights based on trends
    insights = []
    
    if steps_trend > 500:
        insights.append("✅ **Physical Activity**: Your daily steps have increased recently. Great job staying active!")
    elif steps_trend < -500:
        insights.append("❗ **Physical Activity**: Your daily steps have decreased. Try to incorporate more walking into your day.")
    else:
        insights.append("ℹ️ **Physical Activity**: Your step count has been relatively stable.")
    
    if sleep_trend > 0.5:
        insights.append("✅ **Sleep**: You've been sleeping more hours recently, which is beneficial for your health.")
    elif sleep_trend < -0.5:
        insights.append("❗ **Sleep**: Your sleep duration has decreased. Aim for 7-9 hours of sleep per night.")
    else:
        insights.append("ℹ️ **Sleep**: Your sleep pattern has been consistent.")
    
    if hr_trend < -2:
        insights.append("✅ **Heart Health**: Your resting heart rate has decreased, which may indicate improving fitness.")
    elif hr_trend > 2:
        insights.append("❗ **Heart Health**: Your resting heart rate has increased. Monitor this trend and consider consulting a healthcare provider if it continues.")
    else:
        insights.append("ℹ️ **Heart Health**: Your resting heart rate has been stable.")
    
    # Add general insight based on overall data
    if avg_steps > 10000 and avg_sleep > 7.5 and avg_heart_rate < 70:
        insights.append("🌟 **Overall Health**: Your metrics suggest excellent health habits. Keep up the good work!")
    elif avg_steps < 5000 and avg_sleep < 6.5:
        insights.append("❗ **Overall Health**: Your metrics suggest room for improvement in physical activity and sleep.")
    else:
        insights.append("ℹ️ **Overall Health**: Your health metrics are within typical ranges, but there's always room for improvement.")
    
    # Display insights
    for insight in insights:
        st.markdown(insight)
    
    # Health recommendations
    st.subheader("Recommendations")
    
    # Generate recommendations based on metrics
    recommendations = []
    
    if avg_steps < 8000:
        recommendations.append("🚶‍♂️ Aim to increase your daily steps to at least 10,000 steps per day.")
    
    if avg_sleep < 7:
        recommendations.append("😴 Try to improve your sleep duration by establishing a regular sleep schedule.")
    
    if avg_heart_rate > 75:
        recommendations.append("❤️ Consider incorporating more cardiovascular exercise to improve your heart health.")
    
    # Add general recommendations
    recommendations.extend([
        "💧 Stay hydrated by drinking at least 8 glasses of water daily.",
        "🥗 Maintain a balanced diet rich in fruits, vegetables, and whole grains.",
        "🧘‍♀️ Practice stress-reduction techniques like meditation or deep breathing exercises."
    ])
    
    # Display recommendations
    for recommendation in recommendations:
        st.markdown(recommendation)
    
    # Data disclaimer
    st.markdown("---")
    st.caption("""
    **Note**: This dashboard uses simulated health data for demonstration purposes. 
    In a real application, this would be replaced with actual data from wearable devices, 
    health apps, or manual entries.
    """)
