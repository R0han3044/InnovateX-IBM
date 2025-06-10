import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from utils.health_data import HealthDataManager

def show_wellness_dashboard():
    """Display the wellness dashboard"""
    st.title("📊 Wellness Dashboard")
    st.write("Track your health metrics and wellness trends")
    
    # Initialize health data manager
    health_manager = HealthDataManager()
    
    # Get user wellness data
    wellness_data = health_manager.get_wellness_data(st.session_state.username)
    
    # Summary metrics
    show_wellness_summary(wellness_data)
    
    # Charts and visualizations
    show_wellness_charts(wellness_data)
    
    # AI insights
    if st.session_state.model_loaded:
        show_ai_insights(wellness_data)
    
    # Data input section
    show_data_input(health_manager)
    
    # Goals and achievements
    show_goals_section(wellness_data, health_manager)

def show_wellness_summary(wellness_data):
    """Display wellness summary metrics"""
    st.subheader("📈 Current Wellness Overview")
    
    # Calculate current metrics
    if wellness_data.get("overall_scores"):
        current_score = wellness_data["overall_scores"][-1]
        prev_score = wellness_data["overall_scores"][-2] if len(wellness_data["overall_scores"]) > 1 else current_score
        score_change = current_score - prev_score
        
        # Weekly average
        recent_scores = wellness_data["overall_scores"][-7:] if len(wellness_data["overall_scores"]) >= 7 else wellness_data["overall_scores"]
        weekly_avg = sum(recent_scores) / len(recent_scores)
    else:
        current_score = 0
        score_change = 0
        weekly_avg = 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Wellness",
            value=f"{current_score}/100",
            delta=f"{score_change:+d}" if score_change != 0 else None
        )
    
    with col2:
        st.metric(
            label="7-Day Average",
            value=f"{weekly_avg:.1f}/100"
        )
    
    with col3:
        # Calculate streak (consecutive days with score > 70)
        streak = calculate_wellness_streak(wellness_data["overall_scores"])
        st.metric(
            label="Wellness Streak",
            value=f"{streak} days"
        )
    
    with col4:
        # Wellness level
        level = get_wellness_level(current_score)
        st.metric(
            label="Wellness Level",
            value=level
        )
    
    # Component scores
    st.markdown("---")
    st.subheader("🎯 Component Scores")
    
    if wellness_data.get("component_scores"):
        cols = st.columns(len(wellness_data["component_scores"]))
        
        for i, (component, scores) in enumerate(wellness_data["component_scores"].items()):
            with cols[i]:
                current_component_score = scores[-1] if scores else 0
                component_name = component.replace("_", " ").title()
                
                # Color coding based on score
                if current_component_score >= 80:
                    color = "normal"
                elif current_component_score >= 60:
                    color = "inverse"
                else:
                    color = "off"
                
                st.metric(
                    label=component_name,
                    value=f"{current_component_score}/100"
                )

def show_wellness_charts(wellness_data):
    """Display wellness charts and visualizations"""
    st.markdown("---")
    st.subheader("📊 Wellness Trends")
    
    if not wellness_data.get("dates") or not wellness_data.get("overall_scores"):
        st.info("No wellness data available yet. Add some data to see trends!")
        return
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Date': pd.to_datetime(wellness_data["dates"]),
        'Overall Score': wellness_data["overall_scores"]
    })
    
    # Add component scores
    for component, scores in wellness_data.get("component_scores", {}).items():
        if len(scores) == len(wellness_data["dates"]):
            df[component.replace("_", " ").title()] = scores
    
    # Overall trend chart
    fig_overall = px.line(
        df, 
        x='Date', 
        y='Overall Score',
        title='Overall Wellness Score Trend',
        markers=True
    )
    fig_overall.update_layout(
        yaxis_range=[0, 100],
        height=400
    )
    fig_overall.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Good Wellness Threshold")
    
    st.plotly_chart(fig_overall, use_container_width=True)
    
    # Component comparison
    st.subheader("🔍 Component Analysis")
    
    # Latest component scores radar chart
    if wellness_data.get("component_scores"):
        components = list(wellness_data["component_scores"].keys())
        latest_scores = [wellness_data["component_scores"][comp][-1] if wellness_data["component_scores"][comp] else 0 for comp in components]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=latest_scores,
            theta=[comp.replace("_", " ").title() for comp in components],
            fill='toself',
            name='Current Scores'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Current Component Scores",
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Component trends
        st.subheader("📈 Component Trends")
        component_cols = st.columns(2)
        
        for i, (component, scores) in enumerate(wellness_data["component_scores"].items()):
            with component_cols[i % 2]:
                if scores and len(scores) == len(wellness_data["dates"]):
                    component_df = pd.DataFrame({
                        'Date': pd.to_datetime(wellness_data["dates"]),
                        'Score': scores
                    })
                    
                    fig_component = px.line(
                        component_df,
                        x='Date',
                        y='Score',
                        title=f'{component.replace("_", " ").title()} Trend',
                        markers=True
                    )
                    fig_component.update_layout(
                        yaxis_range=[0, 100],
                        height=300
                    )
                    
                    st.plotly_chart(fig_component, use_container_width=True)

def show_ai_insights(wellness_data):
    """Generate and display AI insights"""
    st.markdown("---")
    st.subheader("AI Wellness Insights")
    
    if not st.session_state.model_loaded:
        st.info("AI model not loaded. Load the model to get personalized insights.")
        return
    
    if st.button("Generate AI Insights", type="primary"):
        with st.spinner("Analyzing your wellness data..."):
            try:
                # Prepare wellness data summary
                data_summary = prepare_wellness_summary(wellness_data)
                
                # Get AI insights using demo model
                from utils.model_utils_demo import DemoModelManager
                demo_model = DemoModelManager()
                insights = demo_model.wellness_insights(data_summary)
                
                # Display insights
                st.success("AI Insights Generated")
                st.write(insights)
                
                # Save insights
                save_wellness_insights(insights)
                
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")

def show_data_input(health_manager):
    """Show data input section"""
    st.markdown("---")
    st.subheader("📝 Update Wellness Data")
    
    with st.form("wellness_update"):
        col1, col2 = st.columns(2)
        
        with col1:
            physical_score = st.slider("Physical Health", 0, 100, 75)
            mental_score = st.slider("Mental Health", 0, 100, 75)
            sleep_score = st.slider("Sleep Quality", 0, 100, 75)
        
        with col2:
            nutrition_score = st.slider("Nutrition", 0, 100, 75)
            activity_score = st.slider("Physical Activity", 0, 100, 75)
            overall_feeling = st.slider("Overall Feeling", 0, 100, 75)
        
        notes = st.text_area("Daily Notes (optional)", placeholder="How are you feeling today? Any specific observations?")
        
        if st.form_submit_button("💾 Update Wellness Data", type="primary"):
            # Calculate overall score
            component_scores = {
                "physical": physical_score,
                "mental": mental_score,
                "sleep": sleep_score,
                "nutrition": nutrition_score,
                "activity": activity_score
            }
            
            # Update wellness data
            new_data = {
                "component_scores": component_scores,
                "overall_score": overall_feeling,
                "notes": notes,
                "last_updated": datetime.now().isoformat()
            }
            
            # This would typically update the existing data structure
            st.success("✅ Wellness data updated successfully!")
            
            # Add notification
            health_manager.add_notification(
                st.session_state.username,
                "Wellness Data Updated",
                f"Your wellness score has been updated to {overall_feeling}/100",
                "success"
            )
            
            st.rerun()

def show_goals_section(wellness_data, health_manager):
    """Show wellness goals and achievements"""
    st.markdown("---")
    st.subheader("🎯 Wellness Goals")
    
    # Current goals
    goals = wellness_data.get("goals", [])
    
    if goals:
        st.write("**Active Goals:**")
        for i, goal in enumerate(goals):
            if not goal.get("completed", False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {goal['description']}")
                    if goal.get("target_date"):
                        st.write(f"  Target: {goal['target_date']}")
                with col2:
                    if st.button(f"✅ Complete", key=f"complete_{i}"):
                        # Mark goal as completed
                        wellness_data["goals"][i]["completed"] = True
                        wellness_data["goals"][i]["completed_date"] = datetime.now().isoformat()
                        st.success("Goal completed! 🎉")
                        st.rerun()
    else:
        st.info("No active goals. Set some wellness goals to track your progress!")
    
    # Add new goal
    with st.expander("➕ Add New Goal"):
        goal_description = st.text_input("Goal Description", placeholder="e.g., Exercise 30 minutes daily")
        goal_target_date = st.date_input("Target Date", value=datetime.now() + timedelta(days=30))
        
        if st.button("🎯 Add Goal"):
            if goal_description:
                new_goal = {
                    "description": goal_description,
                    "target_date": goal_target_date.isoformat(),
                    "created_date": datetime.now().isoformat(),
                    "completed": False
                }
                
                if "goals" not in wellness_data:
                    wellness_data["goals"] = []
                
                wellness_data["goals"].append(new_goal)
                st.success("Goal added successfully! 🎯")
                st.rerun()
    
    # Achievements
    completed_goals = [g for g in goals if g.get("completed", False)]
    if completed_goals:
        st.subheader("🏆 Achievements")
        for goal in completed_goals[-5:]:  # Show last 5 achievements
            st.write(f"✅ {goal['description']} (Completed: {goal.get('completed_date', 'Unknown')[:10]})")

def calculate_wellness_streak(scores):
    """Calculate consecutive days with good wellness scores"""
    if not scores:
        return 0
    
    streak = 0
    for score in reversed(scores):
        if score >= 70:  # Good wellness threshold
            streak += 1
        else:
            break
    
    return streak

def get_wellness_level(score):
    """Get wellness level based on score"""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    else:
        return "Needs Attention"

def prepare_wellness_summary(wellness_data):
    """Prepare wellness data summary for AI analysis"""
    if not wellness_data.get("overall_scores"):
        return "No wellness data available."
    
    recent_scores = wellness_data["overall_scores"][-7:]  # Last 7 days
    avg_score = sum(recent_scores) / len(recent_scores)
    
    # Component averages
    component_summary = {}
    for component, scores in wellness_data.get("component_scores", {}).items():
        if scores:
            component_summary[component] = sum(scores[-7:]) / len(scores[-7:])
    
    summary = f"""
    Recent Wellness Summary:
    - Average overall score (last 7 days): {avg_score:.1f}/100
    - Current score: {wellness_data["overall_scores"][-1]}/100
    - Component scores: {component_summary}
    - Total data points: {len(wellness_data["overall_scores"])}
    - Data range: {wellness_data["dates"][0]} to {wellness_data["dates"][-1]}
    """
    
    return summary

def save_wellness_insights(insights):
    """Save AI insights to user data"""
    try:
        health_manager = HealthDataManager()
        health_manager.add_health_record(
            st.session_state.username,
            {
                "type": "ai_wellness_insights",
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        )
    except Exception as e:
        st.warning(f"Could not save insights: {str(e)}")
