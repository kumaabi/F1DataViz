import streamlit as st
import fastf1
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from utils import load_session, get_available_sessions, get_available_drivers
import optimizations as opt

def format_laptime(seconds):
    """
    Format lap time as MM:SS.sss like the provided example (01:26.204)
    Args:
        seconds: Lap time in seconds
    Returns:
        Formatted lap time string
    """
    minutes = int(seconds // 60)
    seconds_remainder = seconds % 60
    formatted_time = f"{minutes:02d}:{seconds_remainder:06.3f}"
    
    # Remove trailing zeros from milliseconds but keep at least one decimal
    if formatted_time.endswith('0'):
        formatted_time = formatted_time.rstrip('0')
    if formatted_time.endswith('.'):
        formatted_time = formatted_time + '0'
    
    return formatted_time
from visualizations import (
    plot_lap_times, 
    plot_driver_comparison, 
    plot_telemetry_data, 
    plot_track_position,
    plot_lap_time_distribution,
    create_speed_trace,
    plot_position_changes,
    plot_team_pace_comparison,
    plot_tyre_strategies,
    plot_qualifying_results,
    plot_gear_shifts_on_track,
    plot_laptimes_scatter,
    plot_tyre_degradation,
    plot_top_speed_heatmap,
    plot_speed_trace_with_corners,
    plot_laptime_distribution,
    plot_track_map_with_corners,
    analyze_driver_tyre_stints,
    analyze_sector_times,
    plot_sector_times_comparison,
    plot_weather_data,
    plot_humidity_data,
    plot_wind_data,
    plot_dhl_fastest_lap
)

# Configure page settings
st.set_page_config(
    page_title="F1 Data Visualization",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enable performance optimizations
opt.enable_performance_optimizations()

# Close any existing matplotlib figures to prevent memory leaks
opt.close_all_figures()

# Create cache directory if it doesn't exist
import os
cache_dir = "./cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Configure FastF1 cache
try:
    fastf1.Cache.enable_cache(cache_dir)
except Exception as e:
    st.warning(f"Could not enable cache: {e}. Continuing without cache.")

# App title
st.title("🏎️ Formula 1 Data Visualization")
st.markdown("Explore F1 race data visualizations powered by FastF1")

# Sidebar for data selection
st.sidebar.header("Data Selection")

# Season selection
available_seasons = list(range(2018, 2026))  # Extended to include 2025 data
selected_season = st.sidebar.selectbox("Select Season", available_seasons, index=len(available_seasons)-1)

# Load available events for the selected season
with st.spinner("Loading events..."):
    try:
        # Special handling for 2025 data
        if selected_season >= 2025:
            # Try to get 2025 event schedule from our data fetcher
            import f1_data_fetcher
            events_df = f1_data_fetcher.get_2025_season_schedule()
            event_names = events_df['raceName'].tolist()
            selected_event = st.sidebar.selectbox("Select Event (2025)", event_names)
        else:
            # Normal handling for past seasons
            try:
                events = fastf1.get_event_schedule(selected_season)
            except AttributeError:
                # Fallback for older FastF1 versions
                events = fastf1.core.get_event_schedule(selected_season)
                
            event_names = events['EventName'].tolist()
            selected_event = st.sidebar.selectbox("Select Event", event_names)
    except Exception as e:
        st.sidebar.error(f"Error loading events: {e}")
        # Fallback to a default list of popular events, including 2025 events
        default_events = [
            "Bahrain Grand Prix", 
            "Saudi Arabian Grand Prix", 
            "Australian Grand Prix",
            "Japanese Grand Prix",
            "Chinese Grand Prix",
            "Miami Grand Prix",
            "Emilia Romagna Grand Prix",
            "Monaco Grand Prix",
            "Canadian Grand Prix",
            "Spanish Grand Prix",
            "Austrian Grand Prix",
            "British Grand Prix", 
            "Hungarian Grand Prix",
            "Belgian Grand Prix",
            "Dutch Grand Prix",
            "Italian Grand Prix", 
            "Azerbaijan Grand Prix",
            "Singapore Grand Prix", 
            "United States Grand Prix", 
            "Mexico City Grand Prix",
            "São Paulo Grand Prix",
            "Las Vegas Grand Prix",
            "Qatar Grand Prix",
            "Abu Dhabi Grand Prix"
        ]
        selected_event = st.sidebar.selectbox("Select Event (Default List)", default_events)

# Session type selection
session_types = ['Race', 'Qualifying', 'Sprint', 'Practice 3', 'Practice 2', 'Practice 1']
selected_session_type = st.sidebar.selectbox("Select Session Type", session_types)

# Qualifying session selection (only show when Qualifying is selected)
if selected_session_type == 'Qualifying':
    quali_sessions = ['Qualifying 1', 'Qualifying 2', 'Qualifying 3']
    selected_quali_session = st.sidebar.selectbox("Select Qualifying Session", quali_sessions, index=2)
elif selected_session_type == 'Sprint':
    sprint_quali_sessions = ['Practice 1', 'Sprint Quali 1', 'Sprint Quali 2', 'Sprint Quali 3', 'Sprint']
    selected_sprint_session = st.sidebar.selectbox("Select Sprint Session", sprint_quali_sessions, index=4)

# Load session data
try:
    with st.spinner(f"Loading {selected_session_type} data for {selected_event} {selected_season}..."):
        # Pass the qualifying or sprint session selection if applicable
        if selected_session_type == 'Qualifying':
            session = load_session(selected_season, selected_event, selected_session_type, quali_session=selected_quali_session)
        elif selected_session_type == 'Sprint':
            session = load_session(selected_season, selected_event, selected_session_type, sprint_session=selected_sprint_session)
        else:
            session = load_session(selected_season, selected_event, selected_session_type)
        
        # Check if session is available
        if session is None:
            st.error(f"❌ {selected_session_type} data is not available for {selected_event} {selected_season}.")
            # Rather than stopping, show a message to guide the user
            st.info("Please try selecting a different event, session type, or season. The API could not provide data for this specific selection.")
            # Add a special notice for 2025 data
            if selected_season >= 2025:
                st.info("Note: 2025 data is only available as it becomes available during the F1 season. Many sessions may not have data yet.")
                # Create a placeholder session to prevent errors
                class PlaceholderSession:
                    def __init__(self):
                        self.event = {"EventName": selected_event, "year": selected_season}
                        # Create empty DataFrames for laps and results with proper structure
                        self.laps = pd.DataFrame(columns=['Driver', 'LapNumber', 'LapTime', 'Stint', 'Compound'])
                        self.results = None
                        
                    def load(self):
                        pass
                
                session = PlaceholderSession()
        else:
            # Load session data
            try:
                session.load()
            except Exception as load_error:
                st.error(f"Error loading session data: {load_error}")
                st.info("Attempting to continue with limited functionality.")
                # Session exists but couldn't load data, proceed with empty laps with proper structure
                session.laps = pd.DataFrame(columns=['Driver', 'LapNumber', 'LapTime', 'Stint', 'Compound'])
except Exception as e:
    st.error(f"Error loading session data: {e}")
    st.info("Unable to load session data. Please try selecting a different event or season.")
    # Create a placeholder session to prevent errors
    class PlaceholderSession:
        def __init__(self):
            self.event = {"EventName": selected_event, "year": selected_season}
            # Create empty DataFrames for laps and results with proper structure
            self.laps = pd.DataFrame(columns=['Driver', 'LapNumber', 'LapTime', 'Stint', 'Compound'])
            self.results = None
    
    session = PlaceholderSession()

# Main content
if selected_session_type == 'Qualifying' and 'selected_quali_session' in locals():
    st.header(f"{selected_event} {selected_season} - {selected_quali_session}")
elif selected_session_type == 'Sprint' and 'selected_sprint_session' in locals():
    st.header(f"{selected_event} {selected_season} - {selected_sprint_session}")
else:
    st.header(f"{selected_event} {selected_season} - {selected_session_type}")

# Display info message for 2025 data
if selected_season >= 2025:
    st.info("""
    🔄 The app will try to fetch 2025 F1 season data directly from the FastF1 API.
    
    If data is not available for the selected session, you'll see an error message.
    As real 2025 data becomes available throughout the season, visualizations will update automatically.
    
    Try selecting different events or session types that have already taken place in the 2025 season.
    """)

# Get available drivers from the session
available_drivers = get_available_drivers(session)

# Note about future FastF1 API changes
if st.sidebar.checkbox("Show API notes", value=False):
    st.sidebar.info("""
    **Note for developers**: The FastF1 library will deprecate the `pick_driver` method 
    in a future release. It will be replaced with `pick_drivers`. This app will be 
    updated when the change occurs.
    
    For now, we handle all potential errors with this transition to ensure 
    a smooth user experience.
    """)

# Analysis selection tabs
analysis_tabs = [
        "Lap Times", 
        "Driver Comparison", 
        "Telemetry Analysis", 
        "Position Changes", 
        "Team Pace", 
        "Tyre Strategies",
        "Track Position", 
    "Sector Times",
    "Weather Data",
    "Championship",
    "Statistics",
    "Advanced"
]

# Add a qualifying-specific tab only for qualifying sessions
if selected_session_type == 'Qualifying':
    analysis_tabs.insert(1, "Qualifying Analysis")
    
analysis_tab = st.tabs(analysis_tabs)

# Dedicated Qualifying Analysis Tab (only appears for qualifying sessions)
if selected_session_type == 'Qualifying' and 'Qualifying Analysis' in analysis_tabs:
    # Calculate the index where the Qualifying Analysis tab was inserted
    quali_tab_index = analysis_tabs.index("Qualifying Analysis")
    
    with analysis_tab[quali_tab_index]:
        st.subheader("Qualifying Session Analysis")
        st.info("This tab provides dedicated analysis tools for qualifying sessions.")
        
        # Display the results from the Ergast API if available
        try:
            # Use Ergast API to get qualifying results if available
            st.markdown("### Qualifying Classification")
            
            # Check if we can get official classification first
            official_quali_results = []
            try:
                # First try to access official qualifying classification if available
                if hasattr(session, 'results') and session.results is not None:
                    for i, result in enumerate(session.results):
                        if 'Driver' in result and 'Position' in result and 'TeamName' in result:
                            # Extract Q3 time if available, otherwise Q2, then Q1
                            lap_time_str = 'No Time'
                            if 'Q3' in result and result['Q3'] is not None:
                                lap_time_str = result['Q3']
                            elif 'Q2' in result and result['Q2'] is not None:
                                lap_time_str = result['Q2']
                            elif 'Q1' in result and result['Q1'] is not None:
                                lap_time_str = result['Q1']
                            
                            tyre = 'SOFT'  # Most qualifying laps are on softs
                            
                            official_quali_results.append({
                                'Position': int(result['Position']),
                                'Driver': result['Driver'],
                                'Team': result['TeamName'],
                                'Best Lap': lap_time_str,
                                'Tyre': tyre
                            })
                    
                    # If we have official data, use it directly
                    if official_quali_results:
                        st.success("Using official qualifying classification data")
                        quali_results = official_quali_results
                        st.caption("Note: Official positions are shown as per FIA classification")
            except Exception as official_err:
                st.info(f"Official qualifying data not available: {str(official_err)}")
                official_quali_results = []
            
            # If no official data, calculate it from lap times
            if not official_quali_results:
                st.info("Using calculated qualifying classification based on fastest lap times")
                # Create a simple qualifying results display that won't fail
                # This bypasses the common 'Lap object has no attribute columns' error
                quali_results = []
                
                # Try to get qualifying results from our multi-source fetcher
                try:
                    from f1_data_fetcher import get_qualifying_results
                    
                    official_results = get_qualifying_results(session.event.year, session.event.EventName)
                    if official_results is not None and len(official_results) > 0:
                        st.success("Using official qualifying classification data")
                        quali_results = official_results
                        
                        # Let the user know we're using official data
                        st.caption("Positions shown are based on official F1 classification data")
                except Exception as official_data_error:
                    st.warning(f"Could not fetch official qualifying results: {str(official_data_error)}")
                    quali_results = []
                
                # Fallback to lap time calculation if no official data available
                if not quali_results:
                    for driver in available_drivers:
                        try:
                            # Try to safely get the driver's fastest lap
                            driver_laps = session.laps.pick_drivers(driver)
                            fastest_lap = None
                            fastest_time = float('inf')
                            
                            # Manual method to find fastest lap without depending on pick_fastest()
                            if not driver_laps.empty and 'LapTime' in driver_laps.columns:
                                for _, lap in driver_laps.iterrows():
                                    if pd.notnull(lap['LapTime']) and lap['LapTime'].total_seconds() < fastest_time:
                                        fastest_time = lap['LapTime'].total_seconds()
                                        fastest_lap = lap
                            
                            if fastest_lap is not None:
                                # Extract needed information
                                # Format lap time as MM:SS.sss like the provided example (01:26.204)
                                lap_time_str = format_laptime(fastest_time)
                                compound = fastest_lap['Compound'] if 'Compound' in fastest_lap and pd.notnull(fastest_lap['Compound']) else 'Unknown'
                                team = fastest_lap['Team'] if 'Team' in fastest_lap and pd.notnull(fastest_lap['Team']) else 'Unknown'
                                
                                quali_results.append({
                                    'Driver': driver,
                                    'Team': team,
                                    'Best Lap': lap_time_str,
                                    'Tyre': compound
                                })
                            else:
                                # Driver has no valid lap time
                                quali_results.append({
                                    'Driver': driver,
                                    'Team': 'Unknown',
                                    'Best Lap': 'No Time',
                                    'Tyre': 'Unknown'
                                })
                        except Exception as e:
                            # Fallback for any error
                            quali_results.append({
                                'Driver': driver,
                                'Team': 'Unknown',
                                'Best Lap': 'Error',
                                'Tyre': 'Unknown'
                            })
                    
                    # Sort by lap time (putting errors and no times at the end)
                    def sort_key(result):
                        if result['Best Lap'] == 'No Time' or result['Best Lap'] == 'Error':
                            return float('inf')
                        try:
                            # Extract minutes and seconds from the time string
                            parts = result['Best Lap'].split(':')
                            return int(parts[0]) * 60 + float(parts[1])
                        except:
                            return float('inf')
                    
                    quali_results.sort(key=sort_key)
                    
                    # Add position based on sorted order
                    for i, result in enumerate(quali_results):
                        result['Position'] = i + 1
                    
                    st.caption("Note: Positions calculated based on lap times may differ from official classification")
                    st.info("⚠️ The position data is calculated from lap times and may differ from the official FIA classification. For definitive results, please refer to the official F1 website.")
            
            # Ensure results are sorted by position if position is available
            if 'Position' in quali_results[0]:
                quali_results.sort(key=lambda x: x['Position'])
            
            # Show the results
            if quali_results:
                # Reorder columns to show position first
                display_columns = ['Position', 'Driver', 'Team', 'Best Lap', 'Tyre']
                quali_df = pd.DataFrame(quali_results)
                st.dataframe(quali_df[display_columns], use_container_width=True)
            else:
                st.info("No qualifying results available for this session.")
                
            # Identify drivers who advanced to Q2 and Q3
            # We'll assume a standard format with 20 drivers, top 15 advance to Q2, top 10 to Q3
            # This is basic logic based on position - for more accurate data we'd need session-specific info
            q1_drivers = [result['Driver'] for result in quali_results]
            q2_drivers = q1_drivers[:15] if len(q1_drivers) >= 15 else q1_drivers
            q3_drivers = q2_drivers[:10] if len(q2_drivers) >= 10 else q2_drivers
            
            # Q1, Q2, Q3 Session Analysis with driver filtering
            st.markdown("### Session Breakdown")
            st.info("Qualifying is typically divided into Q1, Q2, and Q3 segments.")
            
            q_tabs = st.tabs(["Q1", "Q2", "Q3"])
            
            with q_tabs[0]:
                st.markdown("#### Q1 Session")
                st.info("All drivers participate in Q1, with the slowest five eliminated.")
                
                # Driver comparison selection for Q1
                st.subheader("Q1 Driver Comparison")
                if len(q1_drivers) >= 2:
                    # Two columns for driver selection
                    col1, col2 = st.columns(2)
                    with col1:
                        driver1 = st.selectbox("Select First Driver (Q1)", q1_drivers, index=0, key="q1_driver1")
                        # Get fastest lap information
                        try:
                            driver1_laps = session.laps.pick_drivers(driver1)
                            if not driver1_laps.empty:
                                fastest_lap = driver1_laps.pick_fastest()
                                if not fastest_lap.empty and 'LapTime' in fastest_lap:
                                    lap_time = fastest_lap['LapTime'].total_seconds()
                                    lap_num = int(fastest_lap['LapNumber'])
                                    lap_time_str = format_laptime(lap_time)
                                    st.info(f"🏁 {driver1}'s fastest lap: Lap {lap_num} ({lap_time_str})")
                        except Exception as e:
                            st.warning(f"Could not determine fastest lap for {driver1}: {e}")
                    
                    with col2:
                        default_idx = 1 if len(q1_drivers) > 1 else 0
                        driver2 = st.selectbox("Select Second Driver (Q1)", q1_drivers, index=default_idx, key="q1_driver2")
                        # Get fastest lap information
                        try:
                            driver2_laps = session.laps.pick_drivers(driver2)
                            if not driver2_laps.empty:
                                fastest_lap = driver2_laps.pick_fastest()
                                if not fastest_lap.empty and 'LapTime' in fastest_lap:
                                    lap_time = fastest_lap['LapTime'].total_seconds()
                                    lap_num = int(fastest_lap['LapNumber'])
                                    lap_time_str = format_laptime(lap_time)
                                    st.info(f"🏁 {driver2}'s fastest lap: Lap {lap_num} ({lap_time_str})")
                        except Exception as e:
                            st.warning(f"Could not determine fastest lap for {driver2}: {e}")
                    
                    # Compare the drivers
                    if st.button("Compare Q1 Laps", key="compare_q1"):
                        try:
                            fig = plot_driver_comparison(session, driver1, driver2)
                            opt.display_figure_with_cleanup(fig)
                        except Exception as e:
                            st.error(f"Error comparing drivers: {e}")
                
            with q_tabs[1]:
                st.markdown("#### Q2 Session")
                st.info("Q2 features the 15 remaining drivers, with the slowest five eliminated.")
                
                # Show which drivers advanced to Q2
                if len(q2_drivers) > 0:
                    st.markdown(f"##### Drivers in Q2 ({len(q2_drivers)})")
                    st.write(", ".join(q2_drivers))
                    
                    # Driver comparison selection for Q2
                    st.subheader("Q2 Driver Comparison")
                    if len(q2_drivers) >= 2:
                        # Two columns for driver selection
                        col1, col2 = st.columns(2)
                        with col1:
                            driver1 = st.selectbox("Select First Driver (Q2)", q2_drivers, index=0, key="q2_driver1")
                            # Get fastest lap information
                            try:
                                driver1_laps = session.laps.pick_drivers(driver1)
                                if not driver1_laps.empty:
                                    fastest_lap = driver1_laps.pick_fastest()
                                    if not fastest_lap.empty and 'LapTime' in fastest_lap:
                                        lap_time = fastest_lap['LapTime'].total_seconds()
                                        lap_num = int(fastest_lap['LapNumber'])
                                        lap_time_str = format_laptime(lap_time)
                                        st.info(f"🏁 {driver1}'s fastest lap: Lap {lap_num} ({lap_time_str})")
                            except Exception as e:
                                st.warning(f"Could not determine fastest lap for {driver1}: {e}")
                        
                        with col2:
                            default_idx = 1 if len(q2_drivers) > 1 else 0
                            driver2 = st.selectbox("Select Second Driver (Q2)", q2_drivers, index=default_idx, key="q2_driver2")
                            # Get fastest lap information
                            try:
                                driver2_laps = session.laps.pick_drivers(driver2)
                                if not driver2_laps.empty:
                                    fastest_lap = driver2_laps.pick_fastest()
                                    if not fastest_lap.empty and 'LapTime' in fastest_lap:
                                        lap_time = fastest_lap['LapTime'].total_seconds()
                                        lap_num = int(fastest_lap['LapNumber'])
                                        lap_time_str = format_laptime(lap_time)
                                        st.info(f"🏁 {driver2}'s fastest lap: Lap {lap_num} ({lap_time_str})")
                            except Exception as e:
                                st.warning(f"Could not determine fastest lap for {driver2}: {e}")
                        
                        # Compare the drivers
                        if st.button("Compare Q2 Laps", key="compare_q2"):
                            try:
                                fig = plot_driver_comparison(session, driver1, driver2)
                                opt.display_figure_with_cleanup(fig)
                            except Exception as e:
                                st.error(f"Error comparing drivers: {e}")
                
            with q_tabs[2]:
                st.markdown("#### Q3 Session")
                st.info("Q3 is the final qualifying segment with the top 10 drivers competing for pole position.")
                
                # Show which drivers advanced to Q3
                if len(q3_drivers) > 0:
                    st.markdown(f"##### Drivers in Q3 ({len(q3_drivers)})")
                    st.write(", ".join(q3_drivers))
                    
                    # Driver comparison selection for Q3
                    st.subheader("Q3 Driver Comparison")
                    if len(q3_drivers) >= 2:
                        # Two columns for driver selection
                        col1, col2 = st.columns(2)
                        with col1:
                            driver1 = st.selectbox("Select First Driver (Q3)", q3_drivers, index=0, key="q3_driver1")
                            # Get fastest lap information
                            try:
                                driver1_laps = session.laps.pick_drivers(driver1)
                                if not driver1_laps.empty:
                                    fastest_lap = driver1_laps.pick_fastest()
                                    if not fastest_lap.empty and 'LapTime' in fastest_lap:
                                        lap_time = fastest_lap['LapTime'].total_seconds()
                                        lap_num = int(fastest_lap['LapNumber'])
                                        lap_time_str = format_laptime(lap_time)
                                        st.info(f"🏁 {driver1}'s fastest lap: Lap {lap_num} ({lap_time_str})")
                            except Exception as e:
                                st.warning(f"Could not determine fastest lap for {driver1}: {e}")
                        
                        with col2:
                            default_idx = 1 if len(q3_drivers) > 1 else 0
                            driver2 = st.selectbox("Select Second Driver (Q3)", q3_drivers, index=default_idx, key="q3_driver2")
                            # Get fastest lap information
                            try:
                                driver2_laps = session.laps.pick_drivers(driver2)
                                if not driver2_laps.empty:
                                    fastest_lap = driver2_laps.pick_fastest()
                                    if not fastest_lap.empty and 'LapTime' in fastest_lap:
                                        lap_time = fastest_lap['LapTime'].total_seconds()
                                        lap_num = int(fastest_lap['LapNumber'])
                                        lap_time_str = format_laptime(lap_time)
                                        st.info(f"🏁 {driver2}'s fastest lap: Lap {lap_num} ({lap_time_str})")
                            except Exception as e:
                                st.warning(f"Could not determine fastest lap for {driver2}: {e}")
                        
                        # Compare the drivers
                        if st.button("Compare Q3 Laps", key="compare_q3"):
                            try:
                                fig = plot_driver_comparison(session, driver1, driver2)
                                opt.display_figure_with_cleanup(fig)
                            except Exception as e:
                                st.error(f"Error comparing drivers: {e}")
                
        except Exception as e:
            st.error(f"Error in qualifying analysis: {str(e)}")
            st.info("The Qualifying Analysis tab handles qualifying data separately from other tabs to avoid data structure errors.")


with analysis_tab[0]:  # Lap Times
    st.subheader("Lap Time Analysis")
    
    # Driver selection for lap time analysis
    selected_drivers_lap = st.multiselect(
        "Select Drivers", 
        available_drivers,
        default=available_drivers[:3] if len(available_drivers) > 2 else available_drivers
    )
    
    if selected_drivers_lap:
        fig_lap_times = plot_lap_times(session, selected_drivers_lap)
        opt.display_figure_with_cleanup(fig_lap_times)
    else:
        st.info("Please select at least one driver to view lap times.")

with analysis_tab[1]:  # Driver Comparison
    st.subheader("Driver Comparison")
    
    # Select two drivers to compare
    if len(available_drivers) >= 2:
        # Two columns for driver selection
        col1, col2 = st.columns(2)
        with col1:
            driver1 = st.selectbox("Select First Driver", available_drivers, index=0)
            # Get laps for the selected driver
            driver1_laps = session.laps.pick_drivers(driver1)
            if not driver1_laps.empty:
                lap_numbers_d1 = driver1_laps['LapNumber'].astype(int).unique().tolist()
                fastest_lap_idx = 0
                # Try to find the fastest lap index
                try:
                    fastest_lap = driver1_laps.pick_fastest()
                    if not fastest_lap.empty and 'LapNumber' in fastest_lap:
                        fastest_lap_num = int(fastest_lap['LapNumber'])
                        if fastest_lap_num in lap_numbers_d1:
                            fastest_lap_idx = lap_numbers_d1.index(fastest_lap_num)
                            # Show the fastest lap time
                            lap_time = fastest_lap['LapTime'].total_seconds()
                            lap_time_str = format_laptime(lap_time)
                            st.info(f"🏁 {driver1}'s fastest lap: Lap {fastest_lap_num} ({lap_time_str})")
                except Exception as e:
                    pass
                
                # Create lap options with clear indication of the fastest lap
                lap_options = []
                for lap_num in lap_numbers_d1:
                    if lap_num == fastest_lap_num:
                        lap_options.append(f"Lap {lap_num} (Fastest)")
                    else:
                        lap_options.append(f"Lap {lap_num}")
                
                selected_lap_option = st.selectbox(
                    f"Select Lap for {driver1}",
                    lap_options,
                    index=fastest_lap_idx,
                    key=f"lap_d1_{driver1}"
                )
                
                # Extract the lap number from the selected option
                selected_lap_d1 = int(selected_lap_option.split(' ')[1].split(' ')[0])
            else:
                st.warning(f"No lap data available for {driver1}")
                selected_lap_d1 = None
                
        with col2:
            # Set default to second driver in the list
            default_idx = 1 if len(available_drivers) > 1 else 0
            driver2 = st.selectbox("Select Second Driver", available_drivers, index=default_idx)
            # Get laps for the selected driver
            driver2_laps = session.laps.pick_drivers(driver2)
            if not driver2_laps.empty:
                lap_numbers_d2 = driver2_laps['LapNumber'].astype(int).unique().tolist()
                fastest_lap_idx = 0
                # Try to find the fastest lap index
                try:
                    fastest_lap = driver2_laps.pick_fastest()
                    if not fastest_lap.empty and 'LapNumber' in fastest_lap:
                        fastest_lap_num = int(fastest_lap['LapNumber'])
                        if fastest_lap_num in lap_numbers_d2:
                            fastest_lap_idx = lap_numbers_d2.index(fastest_lap_num)
                            # Show the fastest lap time
                            lap_time = fastest_lap['LapTime'].total_seconds()
                            lap_time_str = format_laptime(lap_time)
                            st.info(f"🏁 {driver2}'s fastest lap: Lap {fastest_lap_num} ({lap_time_str})")
                except Exception as e:
                    pass
                
                # Create lap options with clear indication of the fastest lap
                lap_options = []
                for lap_num in lap_numbers_d2:
                    if lap_num == fastest_lap_num:
                        lap_options.append(f"Lap {lap_num} (Fastest)")
                    else:
                        lap_options.append(f"Lap {lap_num}")
                
                selected_lap_option = st.selectbox(
                    f"Select Lap for {driver2}",
                    lap_options,
                    index=fastest_lap_idx,
                    key=f"lap_d2_{driver2}"
                )
                
                # Extract the lap number from the selected option
                selected_lap_d2 = int(selected_lap_option.split(' ')[1].split(' ')[0])
            else:
                st.warning(f"No lap data available for {driver2}")
                selected_lap_d2 = None
        
        # Check if we can compare the drivers
        if driver1 != driver2 and selected_lap_d1 is not None and selected_lap_d2 is not None:
            # Modified plot_driver_comparison function with specific lap numbers
            st.info(f"Comparing {driver1} (Lap {selected_lap_d1}) vs {driver2} (Lap {selected_lap_d2})")
            comp_fig = plot_driver_comparison(session, driver1, driver2, selected_lap_d1, selected_lap_d2)
            opt.display_figure_with_cleanup(comp_fig)
        else:
            if driver1 == driver2:
                st.warning("Please select two different drivers for comparison.")
            elif selected_lap_d1 is None or selected_lap_d2 is None:
                st.warning("Lap data not available for one or both drivers.")
    else:
        st.info("Need at least two drivers in the session for comparison.")

with analysis_tab[2]:  # Telemetry Analysis
    st.subheader("Telemetry Analysis")
    
    # Driver selection for telemetry
    selected_driver_telemetry = st.selectbox(
        "Select Driver for Telemetry",
        available_drivers,
        index=0
    )
    
    # Lap selection
    try:
        driver_laps = session.laps.pick_drivers(selected_driver_telemetry)
        if len(driver_laps) > 0:
            lap_numbers = driver_laps['LapNumber'].unique()
            selected_lap = st.selectbox(
                "Select Lap Number",
                lap_numbers,
                index=len(lap_numbers) // 2  # Select a lap in the middle by default
            )
            
            # Telemetry data visualization
            telemetry_fig = plot_telemetry_data(session, selected_driver_telemetry, selected_lap)
            opt.display_figure_with_cleanup(telemetry_fig)
            
            # Speed trace visualization
            st.subheader("Speed Trace")
            speed_fig = create_speed_trace(session, selected_driver_telemetry, selected_lap)
            opt.display_figure_with_cleanup(speed_fig)
        else:
            st.info(f"No lap data available for {selected_driver_telemetry}.")
    except Exception as e:
        st.error(f"Error generating telemetry: {e}")

with analysis_tab[3]:  # Position Changes
    st.subheader("Position Changes Throughout the Race")
    
    if selected_session_type == 'Race':
        try:
            # Select lap range for position changes
            max_lap = session.laps['LapNumber'].max()
            
            st.markdown("### Track position changes for all drivers")
            
            # Option to select specific drivers
            all_drivers = st.checkbox("Show all drivers", value=True)
            selected_drivers_position = []
            
            if not all_drivers:
                selected_drivers_position = st.multiselect(
                    "Select specific drivers to display",
                    available_drivers,
                    default=available_drivers[:5] if len(available_drivers) >= 5 else available_drivers
                )
            
            # Generate and display the position changes visualization
            fig_position_changes = plot_position_changes(
                session, 
                drivers=None if all_drivers else selected_drivers_position
            )
            opt.display_figure_with_cleanup(fig_position_changes)
            
        except Exception as e:
            st.error(f"Error generating position changes visualization: {e}")
    else:
        st.info("Position changes visualization is only available for Race sessions.")

with analysis_tab[4]:  # Team Pace
    st.subheader("Team Pace Comparison")
    
    try:
        st.markdown("### Compare lap time distributions by team")
        fig_team_pace = plot_team_pace_comparison(session)
        opt.display_figure_with_cleanup(fig_team_pace)
        
        st.markdown("### Lap Times Scatter Plot")
        
        # Option to select specific drivers
        all_drivers_scatter = st.checkbox("Show all drivers in scatter plot", value=True)
        selected_drivers_scatter = []
        
        if not all_drivers_scatter:
            selected_drivers_scatter = st.multiselect(
                "Select specific drivers for lap time scatter",
                available_drivers,
                default=available_drivers[:3] if len(available_drivers) >= 3 else available_drivers
            )
        
        # Generate and display the scatter plot
        fig_laptimes_scatter = plot_laptimes_scatter(
            session, 
            drivers=None if all_drivers_scatter else selected_drivers_scatter
        )
        opt.display_figure_with_cleanup(fig_laptimes_scatter)
        
    except Exception as e:
        st.error(f"Error generating team pace comparison: {e}")

with analysis_tab[5]:  # Tyre Strategies
    st.subheader("Tyre Strategies")
    
    if selected_session_type == 'Race':
        try:
            # Visual tyre strategy overview
            st.markdown("### Tyre compound strategies used during the race")
            fig_tyre_strategies = plot_tyre_strategies(session)
            opt.display_figure_with_cleanup(fig_tyre_strategies)
            
            # Detailed driver stint analysis
            st.markdown("### Driver Tyre Stint Analysis")
            st.info("Select a driver to view detailed information about each tyre stint: compound used, stint length, and tyre life.")
            
            selected_driver_stint = st.selectbox(
                "Select Driver for Stint Analysis",
                available_drivers,
                index=0,
                key="stint_analysis_driver"
            )
            
            # Get detailed stint information for the selected driver
            stint_data = analyze_driver_tyre_stints(session, selected_driver_stint)
            
            if stint_data:
                st.markdown(f"#### Tyre Stint Details for {stint_data['driver']} ({stint_data['team']})")
                
                # Create a table to display stint data
                stint_rows = []
                for stint in stint_data['stints']:
                    stint_rows.append({
                        "Stint": stint['stint_number'],
                        "Compound": stint['compound'],
                        "Laps": f"{stint['start_lap']}-{stint['end_lap']}",
                        "Length": f"{stint['length']} laps",
                        "Tyre Life": f"{stint['start_tyre_life']}-{stint['end_tyre_life']}"
                    })
                
                if stint_rows:
                    # Display as a dataframe
                    stint_df = pd.DataFrame(stint_rows)
                    st.dataframe(stint_df, use_container_width=True)
                    
                    # Display summary information
                    total_race_laps = max([stint['end_lap'] for stint in stint_data['stints']])
                    total_stints = len(stint_data['stints'])
                    compounds_used = ", ".join(set([stint['compound'] for stint in stint_data['stints']]))
                    
                    st.markdown(f"**Race Summary**: {total_race_laps} total laps, {total_stints} tyre changes, compounds used: {compounds_used}")
                else:
                    st.info("No stint data available for the selected driver.")
            else:
                st.warning(f"No tyre stint data available for {selected_driver_stint}")
        except Exception as e:
            st.error(f"Error generating tyre strategies visualization: {e}")
    else:
        st.info("Tyre strategies visualization is only available for Race sessions.")

with analysis_tab[6]:  # Track Position
    st.subheader("Track Position Visualization")
    
    if selected_session_type == 'Race':
        # Select lap for track position
        try:
            max_lap = session.laps['LapNumber'].max()
            selected_position_lap = st.slider(
                "Select Lap Number for Position View", 
                min_value=1, 
                max_value=int(max_lap), 
                value=int(max_lap // 2)
            )
            
            position_fig = plot_track_position(session, selected_position_lap)
            opt.display_figure_with_cleanup(position_fig)
        except Exception as e:
            st.error(f"Error generating track position: {e}")
    else:
        st.info("Track position visualization is only available for Race sessions.")

with analysis_tab[7]:  # Sector Times
    st.subheader("Sector Times Analysis")
    
    st.markdown("### Fastest Sector Times Comparison")
    st.info("This visualization compares the overall fastest lap sectors with the fastest individual sectors from all drivers.")
    
    # Import required modules for the visualization
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import matplotlib.dates as mdates
    
    try:
        # Check if session has valid lap data structure
        if not hasattr(session, 'laps') or session.laps is None or isinstance(session.laps, list) or len(session.laps) == 0:
            st.error("No valid lap data available for sector time analysis.")
            st.info("Please select a different session or event with complete lap and sector time data.")
        else:
            # Get laps with complete sector time data
            laps_with_times = session.laps.dropna(subset=['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time'])
            
            if laps_with_times.empty:
                st.warning("No complete sector time data available for this session.")
                st.info("This visualization requires laps with complete sector time data.")
            else:
                # Find the overall fastest lap
                fastest_overall = laps_with_times.loc[laps_with_times['LapTime'].idxmin()]
                
                # Find the fastest individual sectors
                fastest_s1_lap = laps_with_times.loc[laps_with_times['Sector1Time'].idxmin()]
                fastest_s2_lap = laps_with_times.loc[laps_with_times['Sector2Time'].idxmin()]
                fastest_s3_lap = laps_with_times.loc[laps_with_times['Sector3Time'].idxmin()]
                
                # Display overall fastest lap information
                st.markdown("#### Overall Fastest Lap")
                col1, col2 = st.columns(2)
                
                with col1:
                    fastest_lap_time = fastest_overall['LapTime'].total_seconds()
                    fastest_lap_time_str = format_laptime(fastest_lap_time)
                    
                    st.markdown(f"**Driver:** {fastest_overall['Driver']}")
                    st.markdown(f"**Team:** {fastest_overall['Team'] if 'Team' in fastest_overall else 'Unknown'}")
                    st.markdown(f"**Lap Number:** {int(fastest_overall['LapNumber'])}")
                    st.markdown(f"**Time:** {fastest_lap_time_str}")
                
                with col2:
                    # Format sector times
                    s1_time = fastest_overall['Sector1Time'].total_seconds()
                    s2_time = fastest_overall['Sector2Time'].total_seconds()
                    s3_time = fastest_overall['Sector3Time'].total_seconds()
                    
                    s1_time_str = format_laptime(s1_time).lstrip('0')
                    s2_time_str = format_laptime(s2_time).lstrip('0')
                    s3_time_str = format_laptime(s3_time).lstrip('0')
                    
                    st.markdown("**Sector Breakdown:**")
                    st.markdown(f"Sector 1: {s1_time_str}")
                    st.markdown(f"Sector 2: {s2_time_str}")
                    st.markdown(f"Sector 3: {s3_time_str}")
                
                # Display fastest individual sectors information
                st.markdown("#### Fastest Individual Sectors")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    s1_time = fastest_s1_lap['Sector1Time'].total_seconds()
                    s1_time_str = format_laptime(s1_time).lstrip('0')
                    st.markdown(f"**Sector 1**")
                    st.markdown(f"{s1_time_str}")
                    st.markdown(f"by **{fastest_s1_lap['Driver']}**")
                    st.markdown(f"on Lap {int(fastest_s1_lap['LapNumber'])}")
                
                with col2:
                    s2_time = fastest_s2_lap['Sector2Time'].total_seconds()
                    s2_time_str = format_laptime(s2_time).lstrip('0')
                    st.markdown(f"**Sector 2**")
                    st.markdown(f"{s2_time_str}")
                    st.markdown(f"by **{fastest_s2_lap['Driver']}**")
                    st.markdown(f"on Lap {int(fastest_s2_lap['LapNumber'])}")
                
                with col3:
                    s3_time = fastest_s3_lap['Sector3Time'].total_seconds()
                    s3_time_str = format_laptime(s3_time).lstrip('0')
                    st.markdown(f"**Sector 3**")
                    st.markdown(f"{s3_time_str}")
                    st.markdown(f"by **{fastest_s3_lap['Driver']}**")
                    st.markdown(f"on Lap {int(fastest_s3_lap['LapNumber'])}")
                
                # Create a visualization comparing the fastest lap to fastest individual sectors
                st.markdown("#### Visual Comparison")
                
                # Define sector colors for consistency
                sector_colors = ['#FF9999', '#99FF99', '#9999FF']
                
                # Create plot
                fig, ax = plt.subplots(figsize=(14, 6))
                
                # Prepare data for plotting
                drivers = ['Fastest Lap', 'Fastest Sectors']
                s1_times = [fastest_overall['Sector1Time'].total_seconds(), fastest_s1_lap['Sector1Time'].total_seconds()]
                s2_times = [fastest_overall['Sector2Time'].total_seconds(), fastest_s2_lap['Sector2Time'].total_seconds()]
                s3_times = [fastest_overall['Sector3Time'].total_seconds(), fastest_s3_lap['Sector3Time'].total_seconds()]
                
                # Set up positions for the bars
                y_pos = np.arange(len(drivers))
                bar_height = 0.6
                
                # Plot each sector time as stacked bars
                bars1 = ax.barh(y_pos, s1_times, bar_height, color=sector_colors[0], label='Sector 1')
                bars2 = ax.barh(y_pos, s2_times, bar_height, left=s1_times, color=sector_colors[1], label='Sector 2')
                bars3 = ax.barh(y_pos, s3_times, bar_height, left=[s1+s2 for s1, s2 in zip(s1_times, s2_times)], color=sector_colors[2], label='Sector 3')
                
                # Add total lap time at the end of each bar
                for i, (s1, s2, s3) in enumerate(zip(s1_times, s2_times, s3_times)):
                    total = s1 + s2 + s3
                    ax.text(total + 0.1, i, format_laptime(total), va='center', fontsize=10, fontweight='bold')
                
                # Add driver labels to the sectors
                ax.text(s1_times[1]/2, 1, fastest_s1_lap['Driver'], ha='center', va='center', fontsize=8, fontweight='bold')
                ax.text(s1_times[1] + s2_times[1]/2, 1, fastest_s2_lap['Driver'], ha='center', va='center', fontsize=8, fontweight='bold')
                ax.text(s1_times[1] + s2_times[1] + s3_times[1]/2, 1, fastest_s3_lap['Driver'], ha='center', va='center', fontsize=8, fontweight='bold')
                
                # Customize axis and labels
                ax.set_yticks(y_pos)
                ax.set_yticklabels(drivers, fontsize=12, fontweight='bold')
                
                # Format x-axis as time
                def format_seconds_as_time(seconds, pos):
                    minutes = int(seconds // 60)
                    remaining_seconds = seconds % 60
                    return f"{minutes}:{remaining_seconds:.3f}"
                
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_seconds_as_time))
                
                # Add title and labels
                ax.set_title('Fastest Lap vs. Fastest Individual Sectors', fontsize=14)
                ax.set_xlabel('Time (MM:SS.sss)', fontsize=10)
                
                # Add legend
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
                
                # Add grid
                ax.grid(True, which='major', linestyle='-', linewidth=0.5, color='gray', alpha=0.3)
                ax.set_axisbelow(True)
                
                # Show the plot
                plt.tight_layout()
                opt.display_figure_with_cleanup(fig)
                # Clear the figure to free memory
                opt.close_all_figures()
                
                # Display tabular data of sector times
                st.markdown("#### Detailed Sector Times by Driver")
                
                # Create a formatted dataframe for display
                display_data = []
                
                # Get all drivers' best laps
                for driver in laps_with_times['Driver'].unique():
                    driver_laps = laps_with_times[laps_with_times['Driver'] == driver]
                    if driver_laps.empty:
                        continue
                        
                    # Get driver's fastest lap
                    fastest_lap = driver_laps.loc[driver_laps['LapTime'].idxmin()]
                    
                    # Format lap times
                    lap_time_str = format_laptime(fastest_lap['LapTime'].total_seconds())
                    s1_time_str = format_laptime(fastest_lap['Sector1Time'].total_seconds()).lstrip('0')
                    s2_time_str = format_laptime(fastest_lap['Sector2Time'].total_seconds()).lstrip('0')
                    s3_time_str = format_laptime(fastest_lap['Sector3Time'].total_seconds()).lstrip('0')
                    
                    # Add highlighting for best sectors
                    s1_best = driver == fastest_s1_lap['Driver']
                    s2_best = driver == fastest_s2_lap['Driver']
                    s3_best = driver == fastest_s3_lap['Driver']
                    
                    # Add row to display data
                    display_data.append({
                        'Driver': driver,
                        'Team': fastest_lap['Team'] if 'Team' in fastest_lap else 'Unknown',
                        'Best Lap': lap_time_str,
                        'Lap #': int(fastest_lap['LapNumber']),
                        'Sector 1': f"{s1_time_str} ★" if s1_best else s1_time_str,
                        'Sector 2': f"{s2_time_str} ★" if s2_best else s2_time_str,
                        'Sector 3': f"{s3_time_str} ★" if s3_best else s3_time_str
                    })
                
                # Convert to dataframe and sort by fastest lap time
                display_df = pd.DataFrame(display_data)
                # Sort by fastest lap time if we have data
                if not display_df.empty:
                    # Get lap time in seconds for sorting
                    display_df = display_df.sort_values('Best Lap')
                
                # Display the dataframe
                st.dataframe(display_df, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error analyzing sector times: {e}")
        st.info("This analysis requires complete sector time data which may not be available for this session.")

with analysis_tab[8]:  # Weather Data
    st.markdown("### Weather Conditions Analysis")

    # Import the new weather visualization function
    from weather_visualization import create_weather_visualization
    
    try:
        # Check if session has weather data
        if not hasattr(session, 'weather_data') or session.weather_data is None or session.weather_data.empty:
            st.warning("Weather data is not available for this session.")
            st.info("Some sessions do not include detailed weather information in the FastF1 dataset.")
        else:
            
            # Create and display the improved weather visualization
            st.markdown("#### Temperature and Rainfall Conditions")
            st.info("This visualization shows air temperature, track temperature, and rainfall data throughout the session.")
            
            with st.spinner("Generating weather visualization..."):
                weather_fig = create_weather_visualization(session)
                
                if weather_fig is not None:
                    opt.display_figure_with_cleanup(weather_fig)
                else:
                    st.warning("Could not generate weather visualization with the available data.")
                    
            # Show additional weather-related information
            st.markdown("#### Weather Impact on Racing")
            st.markdown("""
            Weather conditions can significantly impact F1 racing performance:
            - **Temperature**: Affects tire grip and degradation
            - **Track Temperature**: Influences optimal tire compound selection
            - **Rainfall**: Can dramatically change track conditions, requiring wet or intermediate tires
            - **Humidity**: Impacts engine performance and cooling
            - **Wind**: Affects aerodynamics and braking points
            """)
            
            # Display humidity data if available
            with st.spinner("Checking for humidity data..."):
                if 'Humidity' in session.weather_data.columns:
                    humidity_data = session.weather_data['Humidity']
                    st.markdown("#### Humidity Data")
                    
                    # Create a simple line chart for humidity
                    humidity_fig, hum_ax = plt.subplots(figsize=(10, 4))
                    hum_ax.plot(np.arange(len(humidity_data)), humidity_data, label='Humidity (%)', color='green')
                    hum_ax.set_xlabel('Session Progress')
                    hum_ax.set_ylabel('Humidity (%)')
                    hum_ax.grid(False)  # Remove grid lines
                    hum_ax.set_title('Humidity Levels During Session')
                    opt.display_figure_with_cleanup(humidity_fig)
            
            # Display wind data if available
            with st.spinner("Checking for wind data..."):
                if 'WindSpeed' in session.weather_data.columns:
                    wind_speed = session.weather_data['WindSpeed']
                    st.markdown("#### Wind Conditions")
                    
                    # Create a simple line chart for wind speed
                    wind_fig, wind_ax = plt.subplots(figsize=(10, 4))
                    wind_ax.plot(np.arange(len(wind_speed)), wind_speed, label='Wind Speed', color='purple')
                    wind_ax.set_xlabel('Session Progress')
                    wind_ax.set_ylabel('Wind Speed')
                    wind_ax.grid(False)  # Remove grid lines
                    wind_ax.set_title('Wind Speed During Session')
                    opt.display_figure_with_cleanup(wind_fig)
                    
    except Exception as e:
        st.error(f"Error analyzing weather data: {e}")
        st.info("This visualization requires weather data which may not be available for this session.")
        st.write("Debug - Exception details:", str(e))

with analysis_tab[9]:  # Championship
    st.subheader("F1 Championship Standings")
    
    # Import championship data functions
    from championship_data import (
        get_driver_standings,
        get_constructor_standings,
        get_historical_driver_standings,
        get_historical_constructor_standings,
        get_driver_standings_after_round,
        get_constructor_standings_after_round,
        get_season_rounds,
        get_driver_standings_direct,
        get_constructor_standings_direct
    )
    
    # Import championship visualization functions
    from championship_visualizations import (
        plot_driver_championship_standings,
        plot_constructor_championship_standings,
        plot_championship_progression,
        plot_historical_championship_winners,
        plot_points_gap_to_leader
    )
    
    # Select championship visualization type
    championship_viz_type = st.selectbox(
        "Select Visualization Type",
        [
            "Current Driver Standings",
            "Current Constructor Standings",
            "Championship Progress by Round",
            "Historical Championship Winners",
            "Points Gap to Leader"
        ]
    )
    
    # Add season selection for the visualization
    current_year = 2025  # Default to 2025 for now
    try:
        if hasattr(session, 'event') and hasattr(session.event, 'year'):
            current_year = session.event.year
    except:
        pass
    
    # Create UI based on selected visualization type
    if championship_viz_type == "Current Driver Standings":
        # Season selector
        selected_year = st.slider("Select Season", min_value=2010, max_value=2025, value=current_year)
        
        # Remove the data source radio button and use Direct Calculation by default
        up_to_round = st.slider("Calculate Up To Round", min_value=1, max_value=23, value=5)
        
        with st.spinner(f"Calculating {selected_year} driver standings up to round {up_to_round}..."):
            # Get driver standings using direct calculation
            driver_standings = get_driver_standings_direct(selected_year, up_to_round)
            
            if driver_standings.empty:
                st.warning(f"No driver standings data could be calculated for {selected_year}.")
                st.info("Try selecting a different season or fewer rounds.")
            else:
                # Display standings table
                st.success(f"Showing calculated driver standings for {selected_year} (first {up_to_round} rounds)")
                st.dataframe(driver_standings, use_container_width=True)
                
                # Plot standings visualization
                fig = plot_driver_championship_standings(driver_standings)
                opt.display_figure_with_cleanup(fig)
    
    elif championship_viz_type == "Current Constructor Standings":
        # Season selector
        selected_year = st.slider("Select Season", min_value=2010, max_value=2025, value=current_year)
        
        # Remove the data source radio button and use Direct Calculation by default
        up_to_round = st.slider("Calculate Up To Round", min_value=1, max_value=23, value=5)
        
        with st.spinner(f"Calculating {selected_year} constructor standings up to round {up_to_round}..."):
            # Get constructor standings using direct calculation
            constructor_standings = get_constructor_standings_direct(selected_year, up_to_round)
            
            if constructor_standings.empty:
                st.warning(f"No constructor standings data could be calculated for {selected_year}.")
                st.info("Try selecting a different season or fewer rounds.")
            else:
                # Display standings table
                st.success(f"Showing calculated constructor standings for {selected_year} (first {up_to_round} rounds)")
                
                # Select only the columns we want to display
                display_columns = ['Position', 'Team', 'Points', 'Wins']
                st.dataframe(constructor_standings[display_columns], use_container_width=True)
                
                # Plot standings visualization
                fig = plot_constructor_championship_standings(constructor_standings)
                opt.display_figure_with_cleanup(fig)
    
    elif championship_viz_type == "Championship Progress by Round":
        # Season selector
        selected_year = st.slider("Select Season", min_value=2010, max_value=2025, value=current_year)
        
        # Championship type selector
        champ_type = st.radio("Championship Type", ["Drivers", "Constructors"], horizontal=True)
        
        with st.spinner(f"Loading {selected_year} championship progression..."):
            # Get all rounds in the season
            rounds = get_season_rounds(selected_year)
            
            if rounds.empty:
                st.warning(f"No round data available for {selected_year}.")
            else:
                # Create a dictionary of standings by round
                standings_by_round = {}
                
                # Show progress bar for round loading
                progress_bar = st.progress(0)
                
                # Fetch standings for each round
                for i, (_, round_data) in enumerate(rounds.iterrows()):
                    round_num = round_data['Round']
                    progress_percent = int((i / len(rounds)) * 100)
                    progress_bar.progress(progress_percent, text=f"Loading round {round_num}...")
                    
                    if champ_type == "Drivers":
                        round_standings = get_driver_standings_after_round(selected_year, round_num)
                    else:  # Constructors
                        round_standings = get_constructor_standings_after_round(selected_year, round_num)
                    
                    standings_by_round[round_num] = round_standings
                
                # Complete progress
                progress_bar.progress(100, text="Loading complete!")
                
                # Plot championship progression
                championship_type = 'driver' if champ_type == "Drivers" else 'constructor'
                fig = plot_championship_progression(standings_by_round, championship_type)
                opt.display_figure_with_cleanup(fig)
    
    elif championship_viz_type == "Historical Championship Winners":
        # Year range selector
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("Start Year", min_value=1950, max_value=2025, value=2010)
        with col2:
            end_year = st.number_input("End Year", min_value=1950, max_value=2025, value=current_year)
        
        # Championship type selector
        champ_type = st.radio("Championship Type", ["Drivers", "Constructors"], horizontal=True)
        
        # Validate year range
        if start_year > end_year:
            st.error("Start year must be less than or equal to end year.")
        else:
            with st.spinner(f"Loading championship winners from {start_year} to {end_year}..."):
                # Get historical standings
                if champ_type == "Drivers":
                    historical_standings = get_historical_driver_standings(start_year, end_year)
                    championship_type = 'driver'
                else:  # Constructors
                    historical_standings = get_historical_constructor_standings(start_year, end_year)
                    championship_type = 'constructor'
                
                # Plot historical championship winners
                fig = plot_historical_championship_winners(historical_standings, championship_type)
                opt.display_figure_with_cleanup(fig)
    
    elif championship_viz_type == "Points Gap to Leader":
        # Season selector
        selected_year = st.slider("Select Season", min_value=2010, max_value=2025, value=current_year)
        
        # Championship type selector
        champ_type = st.radio("Championship Type", ["Drivers", "Constructors"], horizontal=True)
        
        with st.spinner(f"Loading {selected_year} standings..."):
            # Get standings
            if champ_type == "Drivers":
                standings = get_driver_standings(selected_year)
                championship_type = 'driver'
            else:  # Constructors
                standings = get_constructor_standings(selected_year)
                championship_type = 'constructor'
            
            if standings.empty:
                st.warning(f"No {champ_type.lower()} standings data available for {selected_year}.")
            else:
                # Plot points gap to leader
                fig = plot_points_gap_to_leader(standings, championship_type)
                opt.display_figure_with_cleanup(fig)

with analysis_tab[10]:  # Statistics
    st.subheader("Session Statistics")
    
    try:
        # Check if session has lap data
        if not hasattr(session, 'laps') or session.laps is None or isinstance(session.laps, list) or not hasattr(session.laps, 'columns'):
            st.error("No valid lap data available for this session.")
            st.info("Please select a different session or event.")
            raise ValueError("Invalid lap data structure")
            
        # Skip this entire section for Qualifying sessions - we handle them in a separate tab
        if selected_session_type == 'Qualifying':
            st.info("📊 For qualifying session statistics, please use the dedicated **Qualifying Analysis** tab.")
            st.warning("The Statistics tab is currently optimized for Race sessions.")
        else:
            # Add DHL Fastest Lap Award section for Race sessions
            if selected_session_type == 'Race':
                st.markdown("### 🏆 DHL Fastest Lap Award")
                st.info("The DHL Fastest Lap Award is presented to the driver who sets the fastest lap in a race.")
                
                # Generate the DHL Fastest Lap Award visualization
                fastest_lap_fig = plot_dhl_fastest_lap(session)
                opt.display_figure_with_cleanup(fastest_lap_fig)

            # Lap time distribution
            st.markdown("### Lap Time Distribution")
            dist_fig = plot_lap_time_distribution(session)
            opt.display_figure_with_cleanup(dist_fig)
            
            # Session results table
            st.markdown("### Session Results")
            
            if selected_session_type == 'Race':
                # For race, show final classification
                results = session.results
                if results is not None:
                    results_df = pd.DataFrame(results)
                    selected_columns = ['DriverNumber', 'Abbreviation', 'FullName', 'TeamName', 'Position', 'Points', 'Status']
                    
                    # Handle column presence
                    available_columns = [col for col in selected_columns if col in results_df.columns]
                    if available_columns:
                        st.dataframe(results_df[available_columns], use_container_width=True)
                    else:
                        st.info("No results data available.")
                else:
                    st.info("No results data available for this session.")
            else:
                # For practice/sprint, show fastest laps
                try:
                    fastest_laps = session.laps.pick_fastest()
                    fastest_laps = fastest_laps.sort_values(by='LapTime') if 'LapTime' in fastest_laps.columns else fastest_laps
                    
                    if not fastest_laps.empty:
                        # Create a more readable dataframe for display
                        # Format lap times using our helper function
                        lap_times = []
                        for idx, lap in fastest_laps.iterrows():
                            lap_time = lap['LapTime'].total_seconds()
                            lap_times.append(format_laptime(lap_time))
                            
                        display_df = pd.DataFrame({
                            'Position': range(1, len(fastest_laps) + 1),
                            'Driver': fastest_laps['Driver'],
                            'Team': fastest_laps['Team'],
                            'Best Lap': lap_times,
                            'Compound': fastest_laps['Compound']
                        })
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.info("No lap time data available.")
                except Exception as sprint_error:
                    st.error(f"Error processing fastest laps: {sprint_error}")
                    st.info("Detailed fastest lap data is not available for this session.")

                
    except Exception as e:
        st.error(f"Error generating statistics: {e}")

with analysis_tab[10]:  # Advanced
    st.subheader("Advanced Visualizations")
    
    # Create tabs for different advanced visualizations
    advanced_tabs = st.tabs([
        "Lap Time Distribution", 
        "Gear Shifts on Track", 
        "Speed Trace with Corners",
        "Track Map",
        "Top Speed Heatmap"
    ])
    
    with advanced_tabs[0]:  # Lap Time Distribution
        st.markdown("### Lap Time Distribution Analysis")
        
        # Option to select specific driver for distribution
        driver_specific = st.checkbox("Analyze specific driver", value=False)
        selected_driver_dist = None
        
        if driver_specific:
            selected_driver_dist = st.selectbox(
                "Select Driver for Distribution Analysis",
                available_drivers,
                index=0
            )
        
        try:
            # Check if session has valid lap data structure
            if not hasattr(session, 'laps') or session.laps is None or not hasattr(session.laps, 'columns'):
                st.error("No valid lap data available for this visualization.")
                st.info("Please select a different session or event.")
            else:
                # Generate the lap time distribution visualization
                fig_laptime_dist = plot_laptime_distribution(session, driver=selected_driver_dist)
                opt.display_figure_with_cleanup(fig_laptime_dist)
        except Exception as e:
            st.error(f"Error generating lap time distribution: {e}")
    
    with advanced_tabs[1]:  # Gear Shifts on Track
        st.markdown("### Gear Shifts Visualization on Track")
        
        # Driver selection for gear visualization
        selected_driver_gear = st.selectbox(
            "Select Driver for Gear Shifts",
            available_drivers,
            index=0,
            key="gear_shift_driver"
        )
        
        # Lap selection
        try:
            # Check if session has valid lap data structure
            if not hasattr(session, 'laps') or session.laps is None or not hasattr(session.laps, 'columns'):
                st.error("No valid lap data available for this visualization.")
                st.info("Please select a different session or event.")
            else:
                driver_laps = session.laps.pick_drivers(selected_driver_gear)
                if len(driver_laps) > 0:
                    lap_numbers = driver_laps['LapNumber'].unique()
                    selected_lap_gear = st.selectbox(
                        "Select Lap Number for Gear Shifts",
                        lap_numbers,
                        index=len(lap_numbers) // 2,
                        key="gear_shift_lap"
                    )
                    
                    # Generate and display the gear shifts visualization
                    fig_gear_shifts = plot_gear_shifts_on_track(session, selected_driver_gear, selected_lap_gear)
                    opt.display_figure_with_cleanup(fig_gear_shifts)
                else:
                    st.info(f"No lap data available for {selected_driver_gear}.")
        except Exception as e:
            st.error(f"Error generating gear shifts visualization: {e}")
    
    with advanced_tabs[2]:  # Speed Trace with Corners
        st.markdown("### Speed Trace with Corner Annotations")
        
        # Driver selection for speed trace
        selected_driver_speed = st.selectbox(
            "Select Driver for Speed Trace",
            available_drivers,
            index=0,
            key="speed_trace_driver"
        )
        
        # Lap selection
        try:
            # Check if session has valid lap data structure
            if not hasattr(session, 'laps') or session.laps is None or not hasattr(session.laps, 'columns'):
                st.error("No valid lap data available for this visualization.")
                st.info("Please select a different session or event.")
            else:
                driver_laps = session.laps.pick_drivers(selected_driver_speed)
                if len(driver_laps) > 0:
                    lap_numbers = driver_laps['LapNumber'].unique()
                    selected_lap_speed = st.selectbox(
                        "Select Lap Number for Speed Trace",
                        lap_numbers,
                        index=len(lap_numbers) // 2,
                        key="speed_trace_lap"
                    )
                    
                    # Generate and display the speed trace visualization
                    fig_speed_trace = plot_speed_trace_with_corners(session, selected_driver_speed, selected_lap_speed)
                    opt.display_figure_with_cleanup(fig_speed_trace)
                else:
                    st.info(f"No lap data available for {selected_driver_speed}.")
        except Exception as e:
            st.error(f"Error generating speed trace visualization: {e}")
    
    with advanced_tabs[3]:  # Track Map
        st.markdown("### Track Map with Numbered Corners")
        
        try:
            # Generate and display the track map visualization
            fig_track_map = plot_track_map_with_corners(session)
            opt.display_figure_with_cleanup(fig_track_map)
        except Exception as e:
            st.error(f"Error generating track map: {e}")
        
        # Add qualifying results if it's a qualifying session
        if selected_session_type == 'Qualifying':
            st.markdown("### Qualifying Results Overview")
            
            try:
                fig_quali = plot_qualifying_results(session)
                opt.display_figure_with_cleanup(fig_quali)
            except Exception as e:
                st.error(f"Error generating qualifying results: {e}")
                
    with advanced_tabs[4]:  # Top Speed Heatmap
        st.markdown("### Top Speed Heatmap Analysis")
        st.markdown("This visualization shows a color-coded heatmap of top speeds across the track. Redder areas indicate higher speeds.")
        
        # Option to filter by driver
        driver_filter = st.checkbox("Filter by specific driver", value=False)
        selected_driver_heatmap = None
        
        if driver_filter:
            selected_driver_heatmap = st.selectbox(
                "Select Driver for Speed Heatmap",
                available_drivers,
                index=0,
                key="speed_heatmap_driver"
            )
            
        # Option to filter by lap
        lap_filter = False
        selected_lap_heatmap = None
        
        if driver_filter and selected_driver_heatmap:
            lap_filter = st.checkbox("Filter by specific lap", value=False)
            
            if lap_filter:
                try:
                    # Check if session has valid lap data structure
                    if not hasattr(session, 'laps') or session.laps is None or not hasattr(session.laps, 'columns'):
                        st.error("No valid lap data available for this visualization.")
                        st.info("Please select a different session or event.")
                        lap_filter = False
                    else:
                        driver_laps = session.laps.pick_drivers(selected_driver_heatmap)
                        if len(driver_laps) > 0:
                            lap_numbers = driver_laps['LapNumber'].unique()
                            selected_lap_heatmap = st.selectbox(
                                "Select Lap Number for Heatmap",
                                lap_numbers,
                                index=len(lap_numbers) // 2,
                                key="speed_heatmap_lap"
                            )
                        else:
                            st.info(f"No lap data available for {selected_driver_heatmap}.")
                            lap_filter = False
                except Exception as e:
                    st.error(f"Error getting lap data: {e}")
                    lap_filter = False
        
        try:
            # Check if session has valid lap data structure
            if not hasattr(session, 'laps') or session.laps is None or not hasattr(session.laps, 'columns'):
                st.error("No valid lap data available for this visualization.")
                st.info("Please select a different session or event.")
            else:
                # Generate the speed heatmap
                speed_heatmap_fig = plot_top_speed_heatmap(
                    session, 
                    lap_number=selected_lap_heatmap if lap_filter else None,
                    driver=selected_driver_heatmap if driver_filter else None
                )
                opt.display_figure_with_cleanup(speed_heatmap_fig)
            
                # Add explanatory text
                st.markdown("""
            #### How to interpret this visualization:
            - **Color Scale**: From blue/green (lower speeds) to yellow/red (higher speeds)
            - **Track Layout**: Black line shows the track shape
            - **Red Dot**: Indicates the start/finish line
            - This visualization compiles data from all laps (or filtered laps) to show where drivers reach their maximum speeds
            """)
        except Exception as e:
            st.error(f"Error generating top speed heatmap: {e}")
            


# Footer
st.markdown("---")
st.markdown("Data provided by [FastF1](https://theoehrly.github.io/Fast-F1/) Python package")

# Final cleanup of all matplotlib resources
st.sidebar.markdown("---")
if st.sidebar.checkbox("Debug Mode", value=False):
    if st.sidebar.button("Force Memory Cleanup"):
        opt.close_all_figures()
        st.sidebar.success("Memory cleanup completed")

# Always clean up at the end
opt.close_all_figures()
