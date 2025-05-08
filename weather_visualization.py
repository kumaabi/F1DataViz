import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime, timedelta


def create_weather_visualization(session):
    """
    Create a visualization of weather data including air/track temperature and rainfall
    that matches the example screenshot provided by the user.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure or None if weather data not available
    """
    # Check if session has weather data
    if not hasattr(session, 'weather_data') or session.weather_data is None or session.weather_data.empty:
        return None
        
    # Get the weather data
    weather_data = session.weather_data.copy()
    
    # Create figure with dark background for better readability
    plt.style.use('dark_background')
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    # Format the x-axis to show hours:minutes
    time_values = []
    
    # Create a base time for x-axis formatting - start at 00:00
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate timestamps for x-axis
    if 'Time' in weather_data.columns:
        # If Time column contains timedeltas, convert to timestamps
        if pd.api.types.is_timedelta64_dtype(weather_data['Time']) or isinstance(weather_data['Time'].iloc[0], timedelta):
            time_samples = len(weather_data)
            time_range = []
            for i in range(time_samples):
                try:
                    td = weather_data['Time'].iloc[i]
                    if hasattr(td, 'total_seconds'):
                        seconds = td.total_seconds()
                    else:
                        seconds = float(td)
                    # Create a timestamp at x seconds from base
                    time_range.append(base_time + timedelta(seconds=seconds))
                except:
                    # Fallback if we can't get the time
                    time_range.append(base_time + timedelta(minutes=i*5))
            time_values = time_range
    else:
        # If no Time column, create equally spaced timestamps
        time_samples = len(weather_data)
        time_values = [base_time + timedelta(minutes=i*5) for i in range(time_samples)]
    
    # Create vertical shaded areas for rainfall if present
    if 'Rainfall' in weather_data.columns:
        # Determine where rainfall occurs (when value > 0)
        rainfall_occurred = weather_data['Rainfall'] > 0
        if rainfall_occurred.any():
            # Find consecutive ranges of rainfall
            rain_intervals = []
            start_idx = None
            
            for i, is_raining in enumerate(rainfall_occurred):
                if is_raining and start_idx is None:
                    start_idx = i  # Start of a rain period
                elif not is_raining and start_idx is not None:
                    # End of a rain period, add to intervals
                    rain_intervals.append((start_idx, i-1))
                    start_idx = None
            
            # Handle case where rainfall continues to the end
            if start_idx is not None:
                rain_intervals.append((start_idx, len(rainfall_occurred)-1))
            
            # Add light blue semi-transparent patches for each rain interval
            for start, end in rain_intervals:
                if start < len(time_values) and end < len(time_values):
                    ax1.axvspan(time_values[start], time_values[end], 
                              alpha=0.3, color='#88CCFF', label='Rainfall')
    
    # Plot the temperature lines - use a more vibrant red and blue
    if 'AirTemp' in weather_data.columns:
        ax1.plot(time_values, weather_data['AirTemp'], 
               color='#FF5555', marker='', linestyle='-', linewidth=2,
               label='Air Temp (°C)')
    
    if 'TrackTemp' in weather_data.columns:
        ax1.plot(time_values, weather_data['TrackTemp'], 
               color='#5555FF', marker='', linestyle='-', linewidth=2,
               label='Track Temp (°C)')
    
    # Set up temperature axis with proper styling
    ax1.set_xlabel('Session Time', fontsize=10, color='white')
    ax1.set_ylabel('Temperature (°C)', fontsize=10, color='white')
    ax1.grid(False)  # Remove grid lines
    ax1.tick_params(axis='both', colors='white')
    
    # Set up legend with custom styling
    legend = ax1.legend(loc='upper left', framealpha=0.7)
    plt.setp(legend.get_texts(), color='white')
    
    # Format x-axis to show time labels (00:00, 00:30, etc)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))  # Every 30 minutes
    plt.xticks(rotation=0)
    
    # Set title with event information
    try:
        event_name = session.event['EventName']
        event_year = session.event.year
        plt.title(f"Weather Conditions - {event_name} {event_year}", fontsize=14, color='white')
    except:
        plt.title("Weather Conditions", fontsize=14, color='white')
    
    # No grid lines
    # ax1.grid(False)  # Already set above
    
    # Adjust layout for better spacing
    plt.tight_layout()
    
    return fig