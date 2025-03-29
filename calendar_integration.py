import os
import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pandas as pd

def get_google_calendar_service():
    """Create and return a Google Calendar service instance"""
    api_key = os.environ.get('GOOGLE_CALENDAR_API_KEY')
    
    if not api_key:
        st.warning("Google Calendar API key not found. Some calendar features may be limited.")
        return None
    
    try:
        service = build('calendar', 'v3', developerKey=api_key, static_discovery=False)
        return service
    except Exception as e:
        st.error(f"Error connecting to Google Calendar API: {str(e)}")
        return None

def get_upcoming_holidays(days=60):
    """Get upcoming holidays from Google Calendar API"""
    service = get_google_calendar_service()
    
    if not service:
        # Return empty list if service not available
        return []
    
    try:
        # Use the Google Calendar holiday calendar for India
        calendar_id = 'en.indian#holiday@group.v.calendar.google.com'
        
        # Calculate time range
        now = datetime.utcnow()
        end_date = now + timedelta(days=days)
        
        # Format time for API
        now_str = now.isoformat() + 'Z'
        end_str = end_date.isoformat() + 'Z'
        
        # Get upcoming holidays
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now_str,
            timeMax=end_str,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events for display
        holiday_list = []
        for event in events:
            start = event['start'].get('date', event['start'].get('dateTime', 'N/A'))
            if 'T' in start:  # dateTime format
                start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            else:  # date format
                start_date = datetime.strptime(start, '%Y-%m-%d')
            
            holiday_list.append({
                'date': start_date.date(),
                'name': event['summary']
            })
        
        return holiday_list
    
    except Exception as e:
        st.error(f"Error retrieving holidays: {str(e)}")
        return []

def create_date_picker_with_suggestions():
    """Enhanced date picker with calendar integration"""
    # Get holidays
    holidays = get_upcoming_holidays()
    
    # Default to today
    selected_date = datetime.now().date()
    
    # Create date columns
    date_col1, date_col2 = st.columns([2, 1])
    
    with date_col1:
        # Standard date picker
        selected_date = st.date_input("Date", selected_date)
    
    with date_col2:
        # Quick date buttons
        if st.button("Today"):
            selected_date = datetime.now().date()
        if st.button("Yesterday"):
            selected_date = datetime.now().date() - timedelta(days=1)
    
    # Check if selected date is a holiday
    holiday_name = None
    for holiday in holidays:
        if holiday['date'] == selected_date:
            holiday_name = holiday['name']
            break
    
    # Display holiday information if applicable
    if holiday_name:
        st.info(f"📅 Note: {selected_date} is {holiday_name}")
    
    # The holiday table will be available but hidden by default
    # We'll keep the holiday info in the code but won't display the table
    
    return selected_date