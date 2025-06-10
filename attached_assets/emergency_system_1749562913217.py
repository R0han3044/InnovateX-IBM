import streamlit as st
import geocoder
import json
import os
from datetime import datetime
import random
from db_utils import get_patient, get_all_patients

# Emergency system functions

def get_emergency_contacts_db():
    """Load or create the emergency contacts database"""
    if os.path.exists('emergency_contacts_db.json'):
        with open('emergency_contacts_db.json', 'r') as f:
            return json.load(f)
    else:
        contacts = {
            "contacts": []
        }
        save_emergency_contacts_db(contacts)
        return contacts

def save_emergency_contacts_db(contacts):
    """Save the emergency contacts database"""
    with open('emergency_contacts_db.json', 'w') as f:
        json.dump(contacts, f, indent=4)

def add_emergency_contact(patient_id, contact_data):
    """Add a new emergency contact"""
    contacts = get_emergency_contacts_db()
    
    # Generate contact ID
    contact_id = f"EC{len(contacts['contacts']) + 1:04d}"
    
    # Create contact record
    contact = {
        "id": contact_id,
        "patient_id": patient_id,
        "name": contact_data["name"],
        "relationship": contact_data["relationship"],
        "phone": contact_data["phone"],
        "email": contact_data.get("email", ""),
        "is_primary": contact_data.get("is_primary", False),
        "created_at": str(datetime.now())
    }
    
    # If this is marked as primary, unmark any other primary contacts
    if contact["is_primary"]:
        for existing_contact in contacts["contacts"]:
            if (existing_contact["patient_id"] == patient_id and 
                existing_contact["is_primary"] and 
                existing_contact["id"] != contact_id):
                existing_contact["is_primary"] = False
    
    contacts["contacts"].append(contact)
    save_emergency_contacts_db(contacts)
    return contact_id

def get_patient_emergency_contacts(patient_id):
    """Get all emergency contacts for a patient"""
    contacts = get_emergency_contacts_db()
    return [contact for contact in contacts["contacts"] if contact["patient_id"] == patient_id]

def update_emergency_contact(contact_id, data):
    """Update emergency contact data"""
    contacts = get_emergency_contacts_db()
    
    # Find the contact
    for i, contact in enumerate(contacts["contacts"]):
        if contact["id"] == contact_id:
            # If setting this as primary, unmark other primary contacts
            if data.get("is_primary") and not contact.get("is_primary"):
                patient_id = contact["patient_id"]
                for other_contact in contacts["contacts"]:
                    if (other_contact["patient_id"] == patient_id and 
                        other_contact["is_primary"] and 
                        other_contact["id"] != contact_id):
                        other_contact["is_primary"] = False
            
            # Update contact data
            for key, value in data.items():
                contacts["contacts"][i][key] = value
            
            # Update modified timestamp
            contacts["contacts"][i]["modified_at"] = str(datetime.now())
            
            save_emergency_contacts_db(contacts)
            return True
    
    return False

def delete_emergency_contact(contact_id):
    """Delete an emergency contact"""
    contacts = get_emergency_contacts_db()
    contacts["contacts"] = [c for c in contacts["contacts"] if c["id"] != contact_id]
    save_emergency_contacts_db(contacts)
    return True

def get_user_location():
    """Get the user's current location using geocoder"""
    try:
        # Attempt to get location from IP (this is approximate)
        g = geocoder.ip('me')
        if g.ok:
            return {
                "latitude": g.lat,
                "longitude": g.lng,
                "address": g.address,
                "city": g.city,
                "state": g.state,
                "country": g.country,
                "accuracy": "approximate (IP-based)",
                "timestamp": str(datetime.now())
            }
        else:
            # Return a placeholder if geocoder fails
            return {
                "error": "Could not determine location",
                "timestamp": str(datetime.now())
            }
    except Exception as e:
        return {
            "error": f"Error getting location: {str(e)}",
            "timestamp": str(datetime.now())
        }

def log_emergency_event(patient_id, location_data, contacted_numbers=None, message=None):
    """Log an emergency event to the database"""
    # Create or load the emergency events database
    if os.path.exists('emergency_events_db.json'):
        with open('emergency_events_db.json', 'r') as f:
            events = json.load(f)
    else:
        events = {
            "events": []
        }
    
    # Generate event ID
    event_id = f"EM{len(events['events']) + 1:04d}"
    
    # Create the event record
    event = {
        "id": event_id,
        "patient_id": patient_id,
        "timestamp": str(datetime.now()),
        "location_data": location_data,
        "contacted_numbers": contacted_numbers or [],
        "message": message or "Emergency alert triggered",
        "status": "active"
    }
    
    # Add to events database
    events["events"].append(event)
    
    # Save events database
    with open('emergency_events_db.json', 'w') as f:
        json.dump(events, f, indent=4)
    
    return event_id

def get_patient_emergency_events(patient_id):
    """Get all emergency events for a patient"""
    if os.path.exists('emergency_events_db.json'):
        with open('emergency_events_db.json', 'r') as f:
            events = json.load(f)
        return [event for event in events["events"] if event["patient_id"] == patient_id]
    else:
        return []

def send_emergency_alert(contact_info, patient_name, location_data, message=None):
    """
    Send an emergency alert to the contact
    
    In a real app, this would use Twilio or another service to send SMS/calls
    For now, we'll simulate this and return a success message
    """
    # Create a default message if none provided
    if not message:
        message = f"EMERGENCY ALERT: {patient_name} has triggered an emergency alert."
    
    # Add location if available
    if location_data and not location_data.get("error"):
        location_text = f"Last known location: {location_data.get('address', 'Unknown')}"
        if location_data.get("latitude") and location_data.get("longitude"):
            map_link = f"https://maps.google.com/?q={location_data['latitude']},{location_data['longitude']}"
            location_text += f"\nMap link: {map_link}"
        message += f"\n\n{location_text}"
    
    # In a real app, you'd call your SMS service here
    # For simulation purposes, we'll just return success with a random delay
    success = random.choice([True, True, True, False])  # 75% success rate for simulation
    
    if success:
        return {
            "success": True,
            "recipient": contact_info.get("name", "Emergency Contact"),
            "phone": contact_info.get("phone", ""),
            "message": message,
            "timestamp": str(datetime.now())
        }
    else:
        return {
            "success": False,
            "error": "Failed to send emergency alert (simulated failure)",
            "recipient": contact_info.get("name", "Emergency Contact"),
            "phone": contact_info.get("phone", ""),
            "timestamp": str(datetime.now())
        }

def show_emergency_page():
    """Display the emergency contact and location sharing page"""
    st.header("🚨 Emergency Services")
    
    # Get patient ID
    if st.session_state.user['role'] == 'patient':
        patients = get_all_patients()
        patient = next((p for p in patients if p.get('user_id') == st.session_state.user['username']), None)
        
        if not patient:
            st.warning("Patient profile not found. Please complete your profile first.")
            if st.button("Create Patient Profile"):
                st.session_state.current_view = 'patient_profile'
                st.rerun()
            return
        
        patient_id = patient['id']
    else:
        # For doctors/admins, if no patient selected, prompt for selection
        if not st.session_state.patient_id:
            patients = get_all_patients()
            if patients:
                selected_patient = st.selectbox(
                    "Select Patient",
                    options=[f"{p['name']} (ID: {p['id']})" for p in patients],
                    format_func=lambda x: x
                )
                
                if selected_patient:
                    patient_id = selected_patient.split("(ID: ")[1].split(")")[0]
                    st.session_state.patient_id = patient_id
                    st.rerun()
                else:
                    st.warning("Please select a patient to manage their emergency contacts")
                    return
            else:
                st.warning("No patients found in the system")
                return
        else:
            patient_id = st.session_state.patient_id
    
    # Get patient and emergency contacts
    patient = get_patient(patient_id)
    emergency_contacts = get_patient_emergency_contacts(patient_id)
    
    # Tab system
    tabs = st.tabs(["Emergency Button", "Manage Contacts", "Emergency History"])
    
    # Emergency Button Tab
    with tabs[0]:
        st.subheader("One-Tap Emergency Alert")
        
        if not emergency_contacts:
            st.warning("No emergency contacts found. Please add emergency contacts before using this feature.")
        else:
            st.markdown("""
            In case of a medical emergency, press the button below to:
            1. Alert your emergency contacts
            2. Share your current location
            3. Send your medical information to emergency responders
            """)
            
            # Get the primary contact, or first contact if no primary
            primary_contact = next((c for c in emergency_contacts if c.get("is_primary")), 
                                  emergency_contacts[0] if emergency_contacts else None)
            
            if primary_contact:
                st.info(f"Primary emergency contact: **{primary_contact['name']}** ({primary_contact['phone']})")
            
            # Custom message
            custom_message = st.text_area(
                "Add a custom message (optional):",
                placeholder="E.g., I need help with my medication, please contact me ASAP",
                max_chars=200
            )
            
            # Big emergency button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚨 SEND EMERGENCY ALERT", 
                           use_container_width=True, 
                           type="primary",
                           help="This will alert your emergency contacts with your location",
                           key="emergency_button"):
                    
                    # Get location
                    with st.spinner("Getting your location..."):
                        location = get_user_location()
                    
                    if location.get("error"):
                        st.error(f"Location error: {location['error']}")
                        location_success = False
                    else:
                        st.success(f"Location identified: {location.get('address', 'Unknown')}")
                        location_success = True
                    
                    # Send alerts to all contacts
                    contact_results = []
                    with st.spinner("Sending emergency alerts..."):
                        for contact in emergency_contacts:
                            result = send_emergency_alert(
                                contact, 
                                patient['name'], 
                                location,
                                custom_message
                            )
                            contact_results.append(result)
                    
                    # Log the emergency event
                    contacted_numbers = [r.get("phone") for r in contact_results if r.get("success")]
                    event_id = log_emergency_event(
                        patient_id, 
                        location, 
                        contacted_numbers,
                        custom_message
                    )
                    
                    # Show results
                    st.subheader("Alert Results")
                    
                    # Summary
                    success_count = sum(1 for r in contact_results if r.get("success"))
                    if success_count > 0:
                        st.success(f"Successfully sent alerts to {success_count} of {len(emergency_contacts)} contacts")
                    else:
                        st.error("Failed to send alerts to any contacts. Please try again or call emergency services directly.")
                    
                    # Detailed results
                    for result in contact_results:
                        if result.get("success"):
                            st.info(f"✅ Alert sent to {result['recipient']} ({result['phone']})")
                        else:
                            st.warning(f"❌ Failed to send alert to {result['recipient']} ({result['phone']})")
                    
                    # Next steps
                    st.markdown("### Next Steps")
                    st.markdown("""
                    - Keep your phone with you
                    - Wait for your emergency contact to respond
                    - If this is a life-threatening emergency, call emergency services (911) directly
                    """)
            
            # Confirmation dialog
            st.info("Press the emergency button ONLY in case of a genuine emergency")
    
    # Manage Contacts Tab
    with tabs[1]:
        st.subheader("Manage Emergency Contacts")
        
        # Display existing contacts
        if emergency_contacts:
            st.write(f"You have {len(emergency_contacts)} emergency contacts")
            
            for i, contact in enumerate(emergency_contacts):
                with st.expander(f"{contact['name']} - {contact['relationship']}" + 
                               (" (Primary)" if contact.get('is_primary') else ""), 
                               expanded=i==0):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Name**: {contact['name']}")
                        st.markdown(f"**Relationship**: {contact['relationship']}")
                    
                    with col2:
                        st.markdown(f"**Phone**: {contact['phone']}")
                        if contact.get('email'):
                            st.markdown(f"**Email**: {contact['email']}")
                    
                    # Action buttons
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if not contact.get('is_primary'):
                            if st.button(f"Set as Primary", key=f"primary_{contact['id']}", use_container_width=True):
                                update_emergency_contact(contact['id'], {"is_primary": True})
                                st.success(f"{contact['name']} set as primary emergency contact")
                                st.rerun()
                    
                    with action_col2:
                        if st.button(f"Remove Contact", key=f"remove_{contact['id']}", use_container_width=True):
                            delete_emergency_contact(contact['id'])
                            st.success(f"Removed {contact['name']} from emergency contacts")
                            st.rerun()
        else:
            st.warning("No emergency contacts found. Add your first contact below.")
        
        # Add new contact form
        st.subheader("Add New Emergency Contact")
        with st.form("add_emergency_contact_form"):
            name = st.text_input("Contact Name")
            relationship = st.selectbox(
                "Relationship",
                ["Family - Spouse", "Family - Parent", "Family - Child", "Family - Sibling", 
                 "Family - Other", "Friend", "Neighbor", "Caregiver", "Doctor", "Other"]
            )
            phone = st.text_input("Phone Number")
            email = st.text_input("Email (Optional)")
            is_primary = st.checkbox("Set as Primary Contact", value=not emergency_contacts)
            
            submit = st.form_submit_button("Add Contact")
            
            if submit:
                if name and phone:
                    # Create contact data
                    contact_data = {
                        "name": name,
                        "relationship": relationship,
                        "phone": phone,
                        "email": email,
                        "is_primary": is_primary
                    }
                    
                    # Add contact
                    add_emergency_contact(
                        patient_id=patient_id,
                        contact_data=contact_data
                    )
                    
                    st.success(f"Added {name} as an emergency contact")
                    st.rerun()
                else:
                    st.error("Please enter at least a name and phone number")
    
    # Emergency History Tab
    with tabs[2]:
        st.subheader("Emergency Alert History")
        
        # Get emergency events for this patient
        events = get_patient_emergency_events(patient_id)
        
        if events:
            # Sort by most recent first
            events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            for event in events:
                with st.expander(f"Emergency Alert - {event['timestamp'][:16]}"):
                    st.markdown(f"**Time**: {event['timestamp']}")
                    
                    if event.get('message'):
                        st.markdown(f"**Message**: {event['message']}")
                    
                    # Location information
                    location = event.get('location_data', {})
                    if location and not location.get('error'):
                        st.markdown("**Location:**")
                        st.markdown(f"- Address: {location.get('address', 'Unknown')}")
                        if location.get('latitude') and location.get('longitude'):
                            st.markdown(f"- Coordinates: {location['latitude']}, {location['longitude']}")
                            # Display a map if coordinates are available
                            try:
                                import pandas as pd
                                map_data = pd.DataFrame({
                                    'lat': [location['latitude']],
                                    'lon': [location['longitude']]
                                })
                                st.map(map_data)
                            except:
                                st.warning("Could not display map")
                    
                    # Contacted numbers
                    if event.get('contacted_numbers'):
                        st.markdown("**Contacted:**")
                        for number in event['contacted_numbers']:
                            st.markdown(f"- {number}")
                    else:
                        st.warning("No contacts were successfully notified")
        else:
            st.info("No emergency alerts have been triggered yet.")