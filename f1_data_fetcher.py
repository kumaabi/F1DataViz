import fastf1
import pandas as pd
import streamlit as st
from fastf1.ergast import Ergast
import datetime
import requests
import json

# Set up Ergast API interface
ergast = Ergast(result_type='pandas')

# Define future F1 races that will happen in 2025
FUTURE_2025_RACES = [
    {
        "season": "2025",
        "round": "1",
        "raceName": "Bahrain Grand Prix",
        "date": "2025-03-02",
        "circuit": "Bahrain International Circuit",
        "locality": "Sakhir",
        "country": "Bahrain"
    },
    {
        "season": "2025",
        "round": "2",
        "raceName": "Saudi Arabian Grand Prix",
        "date": "2025-03-09",
        "circuit": "Jeddah Corniche Circuit",
        "locality": "Jeddah",
        "country": "Saudi Arabia"
    },
    {
        "season": "2025",
        "round": "3",
        "raceName": "Australian Grand Prix",
        "date": "2025-03-23",
        "circuit": "Albert Park Grand Prix Circuit",
        "locality": "Melbourne",
        "country": "Australia"
    },
    {
        "season": "2025",
        "round": "4",
        "raceName": "Japanese Grand Prix",
        "date": "2025-04-06",
        "circuit": "Suzuka Circuit",
        "locality": "Suzuka",
        "country": "Japan"
    },
    {
        "season": "2025",
        "round": "5",
        "raceName": "Chinese Grand Prix",
        "date": "2025-04-20",
        "circuit": "Shanghai International Circuit",
        "locality": "Shanghai",
        "country": "China"
    },
    {
        "season": "2025",
        "round": "6",
        "raceName": "Miami Grand Prix",
        "date": "2025-05-04",
        "circuit": "Miami International Autodrome",
        "locality": "Miami",
        "country": "USA"
    },
    {
        "season": "2025",
        "round": "7",
        "raceName": "Emilia Romagna Grand Prix",
        "date": "2025-05-18",
        "circuit": "Autodromo Enzo e Dino Ferrari",
        "locality": "Imola",
        "country": "Italy"
    },
    {
        "season": "2025",
        "round": "8",
        "raceName": "Monaco Grand Prix",
        "date": "2025-05-25",
        "circuit": "Circuit de Monaco",
        "locality": "Monte-Carlo",
        "country": "Monaco"
    },
    {
        "season": "2025",
        "round": "9",
        "raceName": "Canadian Grand Prix",
        "date": "2025-06-08",
        "circuit": "Circuit Gilles Villeneuve",
        "locality": "Montreal",
        "country": "Canada"
    },
    {
        "season": "2025",
        "round": "10",
        "raceName": "Spanish Grand Prix",
        "date": "2025-06-22",
        "circuit": "Circuit de Barcelona-Catalunya",
        "locality": "Montmeló",
        "country": "Spain"
    },
    {
        "season": "2025",
        "round": "11",
        "raceName": "Austrian Grand Prix",
        "date": "2025-06-29",
        "circuit": "Red Bull Ring",
        "locality": "Spielberg",
        "country": "Austria"
    },
    {
        "season": "2025",
        "round": "12",
        "raceName": "British Grand Prix",
        "date": "2025-07-06",
        "circuit": "Silverstone Circuit",
        "locality": "Silverstone",
        "country": "UK"
    },
    {
        "season": "2025",
        "round": "13",
        "raceName": "Hungarian Grand Prix",
        "date": "2025-07-27",
        "circuit": "Hungaroring",
        "locality": "Budapest",
        "country": "Hungary"
    },
    {
        "season": "2025",
        "round": "14",
        "raceName": "Belgian Grand Prix",
        "date": "2025-08-03",
        "circuit": "Circuit de Spa-Francorchamps",
        "locality": "Spa",
        "country": "Belgium"
    },
    {
        "season": "2025",
        "round": "15",
        "raceName": "Dutch Grand Prix",
        "date": "2025-08-24",
        "circuit": "Circuit Zandvoort",
        "locality": "Zandvoort",
        "country": "Netherlands"
    },
    {
        "season": "2025",
        "round": "16",
        "raceName": "Italian Grand Prix",
        "date": "2025-08-31",
        "circuit": "Autodromo Nazionale Monza",
        "locality": "Monza",
        "country": "Italy"
    },
    {
        "season": "2025",
        "round": "17",
        "raceName": "Azerbaijan Grand Prix",
        "date": "2025-09-14",
        "circuit": "Baku City Circuit",
        "locality": "Baku",
        "country": "Azerbaijan"
    },
    {
        "season": "2025",
        "round": "18",
        "raceName": "Singapore Grand Prix",
        "date": "2025-09-21",
        "circuit": "Marina Bay Street Circuit",
        "locality": "Singapore",
        "country": "Singapore"
    },
    {
        "season": "2025",
        "round": "19",
        "raceName": "United States Grand Prix",
        "date": "2025-10-19",
        "circuit": "Circuit of the Americas",
        "locality": "Austin",
        "country": "USA"
    },
    {
        "season": "2025",
        "round": "20",
        "raceName": "Mexico City Grand Prix",
        "date": "2025-10-26",
        "circuit": "Autódromo Hermanos Rodríguez",
        "locality": "Mexico City",
        "country": "Mexico"
    },
    {
        "season": "2025",
        "round": "21",
        "raceName": "São Paulo Grand Prix",
        "date": "2025-11-09",
        "circuit": "Autódromo José Carlos Pace",
        "locality": "São Paulo",
        "country": "Brazil"
    },
    {
        "season": "2025",
        "round": "22",
        "raceName": "Las Vegas Grand Prix",
        "date": "2025-11-23",
        "circuit": "Las Vegas Strip Circuit",
        "locality": "Las Vegas",
        "country": "USA"
    },
    {
        "season": "2025",
        "round": "23",
        "raceName": "Qatar Grand Prix",
        "date": "2025-11-30",
        "circuit": "Losail International Circuit",
        "locality": "Lusail",
        "country": "Qatar"
    },
    {
        "season": "2025",
        "round": "24",
        "raceName": "Abu Dhabi Grand Prix",
        "date": "2025-12-07",
        "circuit": "Yas Marina Circuit",
        "locality": "Abu Dhabi",
        "country": "UAE"
    }
]

# Define drivers for 2025 season
F1_2025_DRIVERS = [
    {"driverId": "max_verstappen", "code": "VER", "number": "1", "name": "Max Verstappen", "team": "Red Bull Racing"},
    {"driverId": "lando_norris", "code": "NOR", "number": "4", "name": "Lando Norris", "team": "McLaren"},
    {"driverId": "kimi_antonelli", "code": "ANT", "number": "12", "name": "Kimi Antonelli", "team": "Mercedes"},
    {"driverId": "oscar_piastri", "code": "PIA", "number": "81", "name": "Oscar Piastri", "team": "McLaren"},
    {"driverId": "george_russell", "code": "RUS", "number": "63", "name": "George Russell", "team": "Mercedes"},
    {"driverId": "carlos_sainz", "code": "SAI", "number": "55", "name": "Carlos Sainz", "team": "Williams"},
    {"driverId": "alex_albon", "code": "ALB", "number": "23", "name": "Alexander Albon", "team": "Williams"},
    {"driverId": "charles_leclerc", "code": "LEC", "number": "16", "name": "Charles Leclerc", "team": "Ferrari"},
    {"driverId": "esteban_ocon", "code": "OCO", "number": "31", "name": "Esteban Ocon", "team": "Haas F1 Team"},
    {"driverId": "yuki_tsunoda", "code": "TSU", "number": "22", "name": "Yuki Tsunoda", "team": "Red Bull Racing"},
    {"driverId": "isack_hadjar", "code": "HAD", "number": "6", "name": "Isack Hadjar", "team": "Racing Bulls"},
    {"driverId": "lewis_hamilton", "code": "HAM", "number": "44", "name": "Lewis Hamilton", "team": "Ferrari"},
    {"driverId": "gabriel_bortoleto", "code": "BOR", "number": "5", "name": "Gabriel Bortoleto", "team": "Kick Sauber"},
    {"driverId": "jack_doohan", "code": "DOO", "number": "7", "name": "Jack Doohan", "team": "Alpine"},
    {"driverId": "liam_lawson", "code": "LAW", "number": "30", "name": "Liam Lawson", "team": "Racing Bulls"},
    {"driverId": "nico_hulkenberg", "code": "HUL", "number": "27", "name": "Nico Hülkenberg", "team": "Kick Sauber"},
    {"driverId": "fernando_alonso", "code": "ALO", "number": "14", "name": "Fernando Alonso", "team": "Aston Martin"},
    {"driverId": "pierre_gasly", "code": "GAS", "number": "10", "name": "Pierre Gasly", "team": "Alpine"},
    {"driverId": "lance_stroll", "code": "STR", "number": "18", "name": "Lance Stroll", "team": "Aston Martin"},
    {"driverId": "oliver_bearman", "code": "BEA", "number": "87", "name": "Oliver Bearman", "team": "Haas F1 Team"}
]

def get_2025_season_schedule():
    """
    Get the F1 2025 season schedule using real data when available,
    or projected data when real data isn't available yet.
    
    Returns:
        pandas.DataFrame: DataFrame containing the 2025 F1 race schedule
    """
    try:
        # First try to get the official season schedule from Ergast
        schedule = ergast.get_race_schedule(season=2025)
        
        # Check if we got actual data
        if len(schedule) > 0:
            st.success("Retrieved official 2025 F1 schedule from Ergast API")
            return schedule
        else:
            # If no data available yet, use our projected calendar
            df = pd.DataFrame(FUTURE_2025_RACES)
            df['date'] = pd.to_datetime(df['date'])
            st.info("Using projected 2025 F1 calendar - Official data not yet available")
            return df
    except Exception as e:
        st.warning(f"Error accessing Ergast API: {e}")
        # Fallback to projected calendar
        df = pd.DataFrame(FUTURE_2025_RACES)
        df['date'] = pd.to_datetime(df['date'])
        st.info("Using projected 2025 F1 calendar - Official data not yet available")
        return df

def get_2025_drivers():
    """
    Get the F1 2025 drivers list using real data when available,
    or projected data when real data isn't available yet.
    
    Returns:
        pandas.DataFrame: DataFrame containing the 2025 F1 drivers
    """
    try:
        # Try to get official driver standings from the first race of 2025
        # This would indicate the season has started and we have real data
        drivers = ergast.get_driver_standings(season=2025, round=1)
        
        # Check if we got actual data
        if hasattr(drivers, 'content') and len(drivers.content) > 0:
            st.success("Retrieved official 2025 F1 drivers from Ergast API")
            return drivers.content[0][['driverId', 'code', 'permanentNumber', 'givenName', 'familyName', 'constructorId']]
        else:
            # If no data available yet, use our projected driver list
            df = pd.DataFrame(F1_2025_DRIVERS)
            st.info("Using projected 2025 F1 driver lineup - Official data not yet available")
            return df
    except Exception as e:
        st.warning(f"Error accessing Ergast API: {e}")
        # Fallback to projected drivers
        df = pd.DataFrame(F1_2025_DRIVERS)
        st.info("Using projected 2025 F1 driver lineup - Official data not yet available")
        return df

def get_qualifying_results(year, event_name):
    """
    Get qualifying results using multiple data sources.
    First tries FastF1 session.results using the method from the example code,
    then falls back to Ergast API, then manual calculation.
    This function implements a robust multi-source strategy to get the most accurate data.
    
    Args:
        year: The year of the F1 season
        event_name: The name of the event (e.g., "Monaco Grand Prix")
        
    Returns:
        List of qualifying results with position information
    """
    try:
        # First try to get data from FastF1 session.results
        # This is the most reliable source when available
        session = fastf1.get_session(year, event_name, 'Q')
        session.load()
        
        # Method from example code - extract directly from session.results
        if hasattr(session, 'results') and session.results is not None:
            # Extract official results (Position, Driver, Team, Q1/Q2/Q3)
            results_df = session.results[['Position', 'Abbreviation', 'FullName', 'TeamName', 'Q1', 'Q2', 'Q3']]
            
            # Format for our app
            results = []
            for _, row in results_df.iterrows():
                # Get the best qualifying time (Q3, Q2, or Q1 in that order of preference)
                quali_time = None
                for q_session in ['Q3', 'Q2', 'Q1']:
                    if q_session in row and pd.notnull(row[q_session]):
                        quali_time = row[q_session]
                        break
                
                if quali_time is None:
                    quali_time = 'No Time'
                    
                # Format the result
                # Check if quali_time is a timedelta object and format it properly
                formatted_time = quali_time
                if pd.notnull(quali_time) and not isinstance(quali_time, str):
                    # Format time as MM:SS.sss
                    if hasattr(quali_time, 'total_seconds'):
                        total_secs = quali_time.total_seconds()
                        minutes = int(total_secs // 60)
                        seconds = total_secs % 60
                        formatted_time = f"{minutes:02d}:{seconds:06.3f}"
                        # Remove trailing zeros from milliseconds
                        if formatted_time.endswith('0'):
                            formatted_time = formatted_time.rstrip('0')
                        if formatted_time.endswith('.'):
                            formatted_time = formatted_time + '0'
                
                results.append({
                    'Position': float(row['Position']),  # Match the format from the example
                    'Driver': row['Abbreviation'],
                    'Team': row['TeamName'],
                    'Best Lap': formatted_time,
                    'Tyre': 'SOFT'  # Most qualifying laps are on softs
                })
            
            if results:
                # Sort by position to ensure proper order
                results.sort(key=lambda x: x['Position'])
                return results
    except Exception as e:
        st.info(f"Could not get official qualifying results from FastF1 using results approach: {e}")
    
    # Second approach - try to use the session laps data from FastF1
    try:
        if hasattr(session, 'laps') and not session.laps.empty:
            # Collect all drivers
            drivers = session.laps['Driver'].unique()
            results = []
            
            for driver in drivers:
                try:
                    # Get driver's laps
                    driver_laps = session.laps.pick_drivers(driver)
                    if not driver_laps.empty:
                        # Get the fastest lap
                        fastest_lap = driver_laps.pick_fastest()
                        if not fastest_lap.empty:
                            # Get driver information
                            team = fastest_lap['Team']
                            lap_time = fastest_lap['LapTime']
                            position = -1  # Will be determined after sorting
                            
                            # Format the lap time nicely
                            formatted_time = lap_time
                            if pd.notnull(lap_time) and hasattr(lap_time, 'total_seconds'):
                                # Format time as MM:SS.sss
                                total_secs = lap_time.total_seconds()
                                minutes = int(total_secs // 60)
                                seconds = total_secs % 60
                                formatted_time = f"{minutes:02d}:{seconds:06.3f}"
                                # Remove trailing zeros from milliseconds
                                if formatted_time.endswith('0'):
                                    formatted_time = formatted_time.rstrip('0')
                                if formatted_time.endswith('.'):
                                    formatted_time = formatted_time + '0'
                            
                            # Add to results
                            results.append({
                                'Driver': driver,
                                'Team': team,
                                'Best Lap': formatted_time,
                                'Tyre': fastest_lap.get('Compound', 'SOFT'),
                                'RawTime': lap_time.total_seconds() if pd.notnull(lap_time) else float('inf')
                            })
                except Exception as driver_error:
                    st.warning(f"Error processing driver {driver}: {driver_error}")
            
            if results:
                # Sort by lap time
                results.sort(key=lambda x: x.get('RawTime', float('inf')))
                
                # Add position based on sort order
                for i, result in enumerate(results):
                    result['Position'] = i + 1
                    # Clean up temporary field
                    if 'RawTime' in result:
                        del result['RawTime']
                
                return results
    except Exception as e:
        st.info(f"Could not get qualifying results from FastF1 laps data: {e}")
        
    # If FastF1 direct results fail, try Ergast API
    try:
        # Try to get data from Ergast API
        ergast = Ergast()
        # Get the round number for this event
        schedule = ergast.get_race_schedule(season=year)
        round_number = None
        
        for _, race in schedule.iterrows():
            if event_name in race['raceName']:
                round_number = race['round']
                break
        
        if round_number:
            # Get qualifying results from Ergast
            qualifying_results = ergast.get_qualification_results(season=year, round=round_number)
            
            if qualifying_results is not None and not qualifying_results.empty:
                results = []
                for _, row in qualifying_results.iterrows():
                    driver_code = row['Driver Code']
                    team = row['Team']
                    position = row['Position']
                    
                    # Get best Q time
                    best_time = 'No Time'
                    raw_time = None
                    
                    # Check each qualifying session in order of preference
                    for q_session in ['Q3', 'Q2', 'Q1']:
                        if pd.notnull(row[q_session]):
                            raw_time = row[q_session]
                            break
                    
                    # Format the time in MM:SS.sss format
                    if raw_time is not None:
                        # Ergast typically returns strings like '1:26.204'
                        if isinstance(raw_time, str):
                            # Just use the raw string which is already in the right format
                            best_time = raw_time
                        # But also handle if it's a timedelta object
                        elif hasattr(raw_time, 'total_seconds'):
                            total_secs = raw_time.total_seconds()
                            minutes = int(total_secs // 60)
                            seconds = total_secs % 60
                            best_time = f"{minutes:02d}:{seconds:06.3f}"
                            # Remove trailing zeros from milliseconds
                            if best_time.endswith('0'):
                                best_time = best_time.rstrip('0')
                            if best_time.endswith('.'):
                                best_time = best_time + '0'
                    
                    results.append({
                        'Position': position,
                        'Driver': driver_code,
                        'Team': team,
                        'Best Lap': best_time,
                        'Tyre': 'SOFT'
                    })
                
                if results:
                    # Sort by position to ensure proper order
                    results.sort(key=lambda x: x['Position'])
                    return results
    except Exception as e:
        st.info(f"Could not get qualifying results from Ergast API: {e}")
    
    # If all data sources fail, return None so the app can calculate positions from lap times
    return None

def get_session_reference_data(year, event_name, session_type):
    """
    For 2025 data, try to get reference data from earlier seasons when needed.
    This function tries to fetch real-time data first, then falls back to
    reference data from previous seasons.
    
    Args:
        year: The year of the F1 season (should be 2025)
        event_name: The name of the event (e.g., "Monaco Grand Prix")
        session_type: The type of session (e.g., "Race", "Qualifying")
    
    Returns:
        FastF1 session object or None
    """
    # We directly access F1 data without initial fallbacks like in the provided FastF1 example
    use_reference_data = False  # Don't use reference data by default
    # Enable fallback data for better user experience
    use_fallback_data = True   # Allow fallback to reference data if needed
    
    # Map session type to FastF1 session name
    session_map = {
        'Race': 'R',
        'Qualifying': 'Q',
        'Sprint': 'S',
        'Practice 1': 'FP1',
        'Practice 2': 'FP2',
        'Practice 3': 'FP3'
    }
    
    session_name = session_map.get(session_type)
    if not session_name:
        return None
    
    try:
        # Try to fetch data directly (including 2025 data)
        # Only fall back to reference data if use_reference_data is True
        if use_reference_data:
            st.info(f"Using reference data for {event_name} {session_type} since we're in reference data mode")
        else:
            # Try to get real data directly from FastF1
            # This will fetch 2025 data if it's available
            session = fastf1.get_session(year, event_name, session_name)
            
            # Enable detailed logging to see what's happening
            session.load(laps=True, telemetry=True, weather=True, messages=True)
            
            # If we get here, we have actual data
            if session and hasattr(session, 'laps') and not session.laps.empty:
                st.success(f"✅ Successfully loaded official data for {event_name} - {session_type}")
                return session
            else:
                st.warning(f"Session loaded but contains no lap data for {event_name} - {session_type}")

            # If loading the data fails, either show an error or use fallback data
            if not use_fallback_data:
                st.error(f"❌ Failed to fetch data for {event_name} {session_type}. No data is available for this session.")
                return None
        
        # Fall back to reference data only if use_fallback_data is True
        if use_fallback_data:
            # Fall back to 2024 or 2023 reference data
            current_year = datetime.datetime.now().year
            reference_years = [year for year in range(current_year, 2022, -1) if year < 2025]
            
            for reference_year in reference_years:
                try:
                    # Try to get the same event from the reference year
                    st.info(f"Attempting to load reference data from {reference_year} for {event_name}...")
                    ref_session = fastf1.get_session(reference_year, event_name, session_name)
                    ref_session.load(laps=True, telemetry=True, weather=True, messages=True)
                    
                    if ref_session and hasattr(ref_session, 'laps') and not ref_session.laps.empty:
                        st.info(f"🔄 Using {reference_year} data as reference for {event_name} {session_type}.")
                        return ref_session
                    else:
                        st.warning(f"Reference {reference_year} session loaded but contains no lap data")
                except Exception as ref_error:
                    st.warning(f"Could not load {reference_year} reference data: {ref_error}")
                    # If that fails, try the next reference year
                    continue
            
            # If all else fails, use British GP as a fallback (it usually has good data)
            try:
                st.info(f"Attempting to load default reference data (2023 British Grand Prix)...")
                ref_session = fastf1.get_session(2023, "British Grand Prix", session_name)
                ref_session.load(laps=True, telemetry=True, weather=True, messages=True)
                
                if ref_session and hasattr(ref_session, 'laps') and not ref_session.laps.empty:
                    st.info(f"🔄 Using 2023 British Grand Prix data as reference for {event_name} {session_type}.")
                    return ref_session
                else:
                    st.warning("Default reference session loaded but contains no lap data")
                    return None
            except Exception as fallback_error:
                st.error(f"Unable to load any reference data for {event_name} {session_type}: {fallback_error}")
                return None
        else:
            st.error(f"❌ No data available for {event_name} {session_type}. Fallback to reference data is disabled.")
            return None
    
    except Exception as e:
        st.error(f"Error in session data loading process: {e}")
        return None
