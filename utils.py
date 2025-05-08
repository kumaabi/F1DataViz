import fastf1
import pandas as pd
import numpy as np
import streamlit as st

import f1_data_fetcher

def load_session(year, event_name, session_type, quali_session=None, sprint_session=None):
    """
    Load a specific F1 session using FastF1.
    
    Args:
        year: The year of the F1 season
        event_name: The name of the event (e.g., "Monaco Grand Prix")
        session_type: The type of session (e.g., "Race", "Qualifying")
        quali_session: The specific qualifying session (e.g., "Qualifying 1", "Qualifying 2", "Qualifying 3")
        sprint_session: The specific sprint session (e.g., "Sprint Quali 1", "Sprint Quali 2", "Sprint Quali 3")
    
    Returns:
        FastF1 session object or None if session doesn't exist
    """
    try:
        # Map session type to FastF1 session name
        session_map = {
            'Race': 'R',
            'Qualifying': 'Q',
            'Sprint': 'S',
            'Practice 1': 'FP1',
            'Practice 2': 'FP2',
            'Practice 3': 'FP3',
            # Specific qualifying sessions
            'Qualifying 1': 'Q1',
            'Qualifying 2': 'Q2',
            'Qualifying 3': 'Q3',
            # Sprint qualifying sessions
            'Sprint Quali 1': 'SQ1',
            'Sprint Quali 2': 'SQ2',
            'Sprint Quali 3': 'SQ3'
        }
        
        # Determine which session name to use based on session type and qualifying/sprint selection
        if session_type == 'Qualifying' and quali_session:
            # Use specific qualifying session (Q1, Q2, Q3)
            session_name = session_map.get(quali_session)
        elif session_type == 'Sprint' and sprint_session:
            # Use specific sprint session
            if sprint_session == 'Sprint':
                session_name = 'S'
            else:
                session_name = session_map.get(sprint_session)
        else:
            # Use regular session type
            session_name = session_map.get(session_type)
            
        if not session_name:
            return None
        
        # Initialize cache directory
        try:
            fastf1.Cache.enable_cache('./cache')
        except Exception as cache_error:
            st.warning(f"Could not enable cache: {cache_error}. Continuing without cache.")
            
        # Special handling for 2025 data
        if year >= 2025:
            # Use the specialized 2025 data fetcher
            return f1_data_fetcher.get_session_reference_data(year, event_name, session_type)
        
        # Normal case - try to get the session for the specified year
        try:
            session = fastf1.get_session(year, event_name, session_name)
            return session
        except AttributeError:
            # Fallback for older FastF1 versions
            session = fastf1.core.get_session(year, event_name, session_name)
            return session
    except Exception as e:
        st.error(f"Error loading session: {e}")
        return None

def get_available_sessions(year, event_name):
    """
    Get a list of available sessions for a specific event.
    
    Args:
        year: The year of the F1 season
        event_name: The name of the event
    
    Returns:
        List of available session types
    """
    # For 2025 or future years, try to access live data first
    if year >= 2025:
        # Standard sessions that are typically available for all events
        sessions = ['Race', 'Qualifying', 'Sprint', 'Practice 3', 'Practice 2', 'Practice 1']
        
        # In a real scenario, we would try to get the actual available sessions for 2025 events
        # from the API once they become available, but for now we return the standard list
        return sessions
        
    try:
        try:
            event = fastf1.get_event(year, event_name)
        except AttributeError:
            # Fallback for older FastF1 versions
            event = fastf1.core.get_event(year, event_name)
            
        available_sessions = []
        
        session_map = {
            'R': 'Race',
            'Q': 'Qualifying',
            'S': 'Sprint',
            'FP1': 'Practice 1',
            'FP2': 'Practice 2',
            'FP3': 'Practice 3'
        }
        
        # Check which sessions are available
        for code, name in session_map.items():
            try:
                if hasattr(event, code.lower()) and getattr(event, code.lower()) is not None:
                    available_sessions.append(name)
            except:
                continue
        
        # If no sessions were found, return default list
        if not available_sessions:
            return ['Race', 'Qualifying', 'Practice 3', 'Practice 2', 'Practice 1']
                
        return available_sessions
    except Exception as e:
        st.error(f"Error getting available sessions: {e}")
        # Return default list on error
        return ['Race', 'Qualifying', 'Practice 3', 'Practice 2', 'Practice 1']

def get_available_drivers(session):
    """
    Get a list of drivers in the session.
    
    Args:
        session: FastF1 session object
    
    Returns:
        List of driver identifiers
    """
    try:
        # First check if session has the laps attribute
        if not hasattr(session, 'laps'):
            return []
            
        # Then check if laps is None or empty
        if session.laps is None or session.laps.empty:
            return []
            
        # Check if 'Driver' column exists in laps DataFrame
        if not hasattr(session.laps, 'columns') or 'Driver' not in session.laps.columns:
            return []
            
        # Get unique drivers from the session
        drivers = session.laps['Driver'].unique().tolist()
        return drivers
    except Exception as e:
        st.error(f"Error getting available drivers: {e}")
        return ["VER", "HAM", "LEC"]  # Return a fallback list of common drivers if all else fails

def get_driver_color(driver, team=None):
    """
    Get standardized F1 color for a driver or team.
    
    Args:
        driver: Driver abbreviation
        team: Team name (optional)
    
    Returns:
        Hex color code
    """
    # Default to team colors when possible - updated for 2025 teams
    team_colors = {
        # Current teams (2023-2025)
        'Mercedes': '#00D2BE',
        'Red Bull': '#0600EF',
        'Ferrari': '#DC0000',
        'McLaren': '#FF8700',
        'Alpine': '#0090FF',
        'Aston Martin': '#006F62',
        'Williams': '#005AFF',
        'Haas': '#FFFFFF',
        
        # RB (formerly AlphaTauri)
        'RB': '#2B4562',
        'AlphaTauri': '#2B4562',
        'Alpha Tauri': '#2B4562',
        
        # Stake/Sauber (formerly Alfa Romeo)
        'Stake': '#900000',
        'Stake F1': '#900000',
        'Kick Sauber': '#900000',
        'Alfa Romeo': '#900000',
        'Sauber': '#9B0000',
        
        # Historical teams (pre-2023)
        'Racing Point': '#F596C8',
        'Renault': '#FFF500',
        'Toro Rosso': '#469BFF',
        'Force India': '#F596C8',
    }
    
    # Use team color if provided
    if team and team in team_colors:
        return team_colors[team]
    
    # Fallback to a color map based on driver initials - updated for 2025 drivers
    driver_colors = {
        # Mercedes
        'HAM': '#00D2BE',
        'RUS': '#00D2BE',
        
        # Red Bull
        'VER': '#0600EF',
        'PER': '#0600EF',
        
        # Ferrari
        'LEC': '#DC0000',
        'SAI': '#DC0000',
        'HAM': '#DC0000',  # Lewis to Ferrari in 2025
        
        # McLaren
        'NOR': '#FF8700',
        'PIA': '#FF8700',
        
        # Aston Martin
        'ALO': '#006F62',
        'STR': '#006F62',
        
        # Alpine
        'GAS': '#0090FF',
        'OCO': '#0090FF',
        
        # RB (formerly AlphaTauri)
        'TSU': '#2B4562',
        'RIC': '#2B4562',
        'LAW': '#2B4562',  # Lawson
        
        # Williams
        'ALB': '#005AFF',
        'SAR': '#005AFF',
        'COA': '#005AFF',  # Colapinto
        
        # Stake F1 (formerly Alfa Romeo)
        'BOT': '#900000',
        'ZHO': '#900000',
        
        # Haas
        'MAG': '#FFFFFF',
        'HUL': '#FFFFFF',
        'BEA': '#FFFFFF',  # Bearman
        
        # Historical/Other drivers
        'VET': '#006F62',  # Aston Martin
        'MSC': '#FFFFFF',  # Haas
        'RAI': '#900000',  # Alfa Romeo
        'LAT': '#005AFF',  # Williams
    }
    
    if driver in driver_colors:
        return driver_colors[driver]
    
    # Generate a random color if no matching color is found
    import hashlib
    hash_object = hashlib.md5(driver.encode())
    hex_dig = hash_object.hexdigest()
    return f"#{hex_dig[:6]}"
