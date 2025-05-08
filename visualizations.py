import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec
from utils import get_driver_color
import streamlit as st
from optimizations import optimize_dataframe

# Configure matplotlib for displaying timedeltas properly
mpl.rcParams['date.autoformatter.minute'] = '%M:%S'
mpl.rcParams['date.autoformatter.second'] = '%S.%f'

def plot_lap_times(session, drivers, title=None):
    """
    Plot lap times for selected drivers.
    
    Args:
        session: FastF1 session object
        drivers: List of driver identifiers to plot
        title: Custom plot title (optional)
    
    Returns:
        Matplotlib figure
    """
    if not drivers:
        return None
    
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
        
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Flag to check if any driver data was plotted
    data_plotted = False
    
    # Plot lap times for each selected driver
    for driver in drivers:
        try:
            driver_laps = session.laps.pick_drivers(driver)
            
            # Skip if no valid laps
            if driver_laps.empty:
                continue
            
            # Get team for driver color
            team = driver_laps['Team'].iloc[0] if 'Team' in driver_laps.columns and not driver_laps.empty else None
            color = get_driver_color(driver, team)
            
            # Check for required columns
            if not all(col in driver_laps.columns for col in ['IsAccurate', 'LapTime', 'LapNumber']):
                continue
                
            # Filter out outlier laps (like in/out laps or laps with issues)
            try:
                valid_laps = driver_laps[driver_laps['IsAccurate'] & (driver_laps['LapTime'] < pd.Timedelta(seconds=120))]
            except:
                # If IsAccurate or other filtering fails, use all laps
                valid_laps = driver_laps
            
            if not valid_laps.empty:
                # Convert lap times to seconds for plotting to avoid overflow
                try:
                    lap_times_seconds = valid_laps['LapTime'].dt.total_seconds()
                    ax.plot(valid_laps['LapNumber'], lap_times_seconds, marker='o', label=driver, color=color)
                    data_plotted = True
                except Exception as e:
                    # If conversion fails, try to plot directly
                    try:
                        ax.plot(valid_laps['LapNumber'], valid_laps['LapTime'], marker='o', label=driver, color=color)
                        data_plotted = True
                    except:
                        # Skip if both methods fail
                        pass
        except Exception as e:
            continue
    
    # Check if any data was plotted
    if not data_plotted:
        ax.text(0.5, 0.5, "No valid lap data available for selected drivers", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    # Formatting
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time')
    if title:
        ax.set_title(title)
    else:
        try:
            event_name = session.event['EventName'] if isinstance(session.event, dict) and 'EventName' in session.event else "Unknown Event"
            year = session.event.year if hasattr(session.event, 'year') else ""
            ax.set_title(f"Lap Time Comparison - {event_name} {year}")
        except:
            ax.set_title("Lap Time Comparison")
            
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as time
    try:
        # Use a custom formatter to avoid the overflow error
        def format_timedelta(x, pos):
            try:
                # Convert to seconds first to avoid overflow
                seconds = x.total_seconds() if hasattr(x, 'total_seconds') else float(x)
                minutes, seconds = divmod(seconds, 60)
                return f"{int(minutes):02d}:{seconds:06.3f}"
            except:
                return str(x)
                
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(format_timedelta))
    except Exception as e:
        # Fallback to simple formatting
        pass
    
    # Adjust layout - use a simpler approach to avoid tight_layout issues
    try:
        plt.tight_layout()
    except Exception as e:
        # Skip tight layout if it causes problems
        pass
    
    return fig

def plot_driver_comparison(session, driver1, driver2, lap_number1=None, lap_number2=None):
    """
    Compare specific laps of two drivers. If lap numbers are not provided, uses fastest laps.
    
    Args:
        session: FastF1 session object
        driver1: First driver identifier
        driver2: Second driver identifier
        lap_number1: Optional specific lap number for driver1, uses fastest if None
        lap_number2: Optional specific lap number for driver2, uses fastest if None
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get laps for both drivers
        driver1_laps = session.laps.pick_drivers(driver1)
        driver2_laps = session.laps.pick_drivers(driver2)
        
        if driver1_laps.empty or driver2_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"No lap data available for {'both drivers' if driver1_laps.empty and driver2_laps.empty else driver1 if driver1_laps.empty else driver2}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        # Get specific lap or fastest lap for driver 1
        if lap_number1 is not None:
            # Get the specified lap
            specific_laps_d1 = driver1_laps[driver1_laps['LapNumber'] == lap_number1]
            if specific_laps_d1.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.text(0.5, 0.5, f"No data available for {driver1}'s lap {lap_number1}", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            selected_lap_d1 = specific_laps_d1.iloc[0]
        else:
            # Use fastest lap if no specific lap is provided
            fastest_lap_d1 = driver1_laps.pick_fastest()
            if fastest_lap_d1.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.text(0.5, 0.5, f"No valid fastest lap for {driver1}", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            selected_lap_d1 = fastest_lap_d1
            
        # Get specific lap or fastest lap for driver 2
        if lap_number2 is not None:
            # Get the specified lap
            specific_laps_d2 = driver2_laps[driver2_laps['LapNumber'] == lap_number2]
            if specific_laps_d2.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.text(0.5, 0.5, f"No data available for {driver2}'s lap {lap_number2}", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            selected_lap_d2 = specific_laps_d2.iloc[0]
        else:
            # Use fastest lap if no specific lap is provided
            fastest_lap_d2 = driver2_laps.pick_fastest()
            if fastest_lap_d2.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.text(0.5, 0.5, f"No valid fastest lap for {driver2}", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
            selected_lap_d2 = fastest_lap_d2
        
        # Get telemetry data
        try:
            telemetry_d1 = selected_lap_d1.get_telemetry().add_distance()
            telemetry_d2 = selected_lap_d2.get_telemetry().add_distance()
            
            # Optimize telemetry DataFrames
            telemetry_d1 = optimize_dataframe(telemetry_d1)
            telemetry_d2 = optimize_dataframe(telemetry_d2)
            
        except Exception as e:
            # If telemetry retrieval fails
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"Error retrieving telemetry data: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Check if we have the necessary columns
        required_cols = ['Distance', 'Speed', 'Throttle']
        if not all(col in telemetry_d1.columns for col in required_cols) or not all(col in telemetry_d2.columns for col in required_cols):
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "Missing required telemetry data columns", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get colors for drivers
        team1 = selected_lap_d1['Team'] if 'Team' in selected_lap_d1 else None
        team2 = selected_lap_d2['Team'] if 'Team' in selected_lap_d2 else None
        color1 = get_driver_color(driver1, team1)
        color2 = get_driver_color(driver2, team2)
        
        # Create figure with subplots - now using 3 subplots instead of 2
        fig, axs = plt.subplots(3, 1, figsize=(12, 15))
        
        # Plot speed vs. distance
        axs[0].plot(telemetry_d1['Distance'], telemetry_d1['Speed'], color=color1, label=driver1)
        axs[0].plot(telemetry_d2['Distance'], telemetry_d2['Speed'], color=color2, label=driver2)
        axs[0].set_xlabel('Distance (m)')
        axs[0].set_ylabel('Speed (km/h)')
        axs[0].set_title('Speed Trace Comparison')
        axs[0].legend(loc='lower right')
        axs[0].grid(True, alpha=0.3)
        
        # Plot throttle vs. distance
        axs[1].plot(telemetry_d1['Distance'], telemetry_d1['Throttle'], color=color1, label=driver1)
        axs[1].plot(telemetry_d2['Distance'], telemetry_d2['Throttle'], color=color2, label=driver2)
        axs[1].set_xlabel('Distance (m)')
        axs[1].set_ylabel('Throttle %')
        axs[1].set_title('Throttle Application Comparison')
        axs[1].legend(loc='lower right')
        axs[1].grid(True, alpha=0.3)
        
        # NEW: Plot the speed difference between drivers
        # First, interpolate telemetry data to a common set of distance points for direct comparison
        try:
            # Create a common distance reference
            min_dist = max(telemetry_d1['Distance'].min(), telemetry_d2['Distance'].min())
            max_dist = min(telemetry_d1['Distance'].max(), telemetry_d2['Distance'].max())
            common_distances = np.linspace(min_dist, max_dist, 1000)
            
            # Interpolate speeds for both drivers at these common distances
            from scipy.interpolate import interp1d
            speed1_interp = interp1d(telemetry_d1['Distance'], telemetry_d1['Speed'], 
                                     bounds_error=False, fill_value="extrapolate")
            speed2_interp = interp1d(telemetry_d2['Distance'], telemetry_d2['Speed'], 
                                     bounds_error=False, fill_value="extrapolate")
            
            # Calculate the difference in speed
            speed1_common = speed1_interp(common_distances)
            speed2_common = speed2_interp(common_distances)
            speed_diff = speed1_common - speed2_common
            
            # Plot the speed difference
            axs[2].axhline(y=0, color='gray', linestyle='-', alpha=0.3)
            axs[2].plot(common_distances, speed_diff, color='purple', label=f'{driver1} - {driver2}')
            
            # Highlight where one driver is significantly faster
            threshold = 5  # km/h difference considered significant
            axs[2].fill_between(common_distances, speed_diff, 0, 
                              where=(speed_diff > threshold), 
                              color=color1, alpha=0.3, 
                              interpolate=True, 
                              label=f'{driver1} faster')
            axs[2].fill_between(common_distances, speed_diff, 0, 
                              where=(speed_diff < -threshold), 
                              color=color2, alpha=0.3, 
                              interpolate=True, 
                              label=f'{driver2} faster')
            
            axs[2].set_xlabel('Distance (m)')
            axs[2].set_ylabel('Speed Difference (km/h)')
            axs[2].set_title(f'Speed Advantage: {driver1} vs {driver2}')
            axs[2].legend(loc='upper right')
            axs[2].grid(True, alpha=0.3)
        except Exception as e:
            # If speed difference fails, just show an error message in the third subplot
            axs[2].text(0.5, 0.5, f"Could not calculate speed difference: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=axs[2].transAxes, fontsize=14)
            axs[2].set_xticks([])
            axs[2].set_yticks([])
        
        # Set overall title with lap information
        try:
            lap_time1 = selected_lap_d1['LapTime'].total_seconds()
            lap_time2 = selected_lap_d2['LapTime'].total_seconds()
            time_diff = abs(lap_time1 - lap_time2)
            faster = driver1 if lap_time1 < lap_time2 else driver2
            
            # Get lap numbers for better context
            lap_num1 = int(selected_lap_d1['LapNumber']) if 'LapNumber' in selected_lap_d1 else 'Unknown'
            lap_num2 = int(selected_lap_d2['LapNumber']) if 'LapNumber' in selected_lap_d2 else 'Unknown'
            
            # Format lap times to MM:SS.sss format
            def format_lap_time(seconds):
                minutes, seconds = divmod(seconds, 60)
                return f"{int(minutes):01d}:{seconds:06.3f}"
            
            # Create the main title with lap information
            is_fastest_d1 = selected_lap_d1.equals(driver1_laps.pick_fastest()) if not driver1_laps.empty else False
            is_fastest_d2 = selected_lap_d2.equals(driver2_laps.pick_fastest()) if not driver2_laps.empty else False
            
            lap_d1_label = f"Fastest Lap ({lap_num1})" if is_fastest_d1 else f"Lap {lap_num1}"
            lap_d2_label = f"Fastest Lap ({lap_num2})" if is_fastest_d2 else f"Lap {lap_num2}"
            
            fig.suptitle(f"Lap Comparison: {driver1} ({lap_d1_label}) vs {driver2} ({lap_d2_label})\n" 
                        f"{driver1}: {format_lap_time(lap_time1)} | {driver2}: {format_lap_time(lap_time2)} | "  
                        f"{faster} faster by {time_diff:.3f}s", 
                        fontsize=16)
        except Exception as e:
            # If lap time computation fails
            print(f"Error formatting lap times: {e}")
            fig.suptitle(f"Fastest Lap Comparison: {driver1} vs {driver2}", fontsize=16)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Error comparing drivers: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_telemetry_data(session, driver, lap_number):
    """
    Plot detailed telemetry data for a specific driver on a specific lap.
    
    Args:
        session: FastF1 session object
        driver: Driver identifier
        lap_number: Lap number to analyze
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get lap data
        lap = session.laps.pick_drivers(driver).pick_laps(lap_number)
        
        # Get telemetry data
        telemetry = lap.get_telemetry()
        telemetry = optimize_dataframe(telemetry)  # Optimize the dataframe
        
        if telemetry.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "No telemetry data available for this lap", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create figure with subplots
        fig, axs = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
        
        # Get driver color
        team = lap['Team'] if 'Team' in lap.index else None
        color = get_driver_color(driver, team)
        
        # Plot speed
        axs[0].plot(telemetry['Distance'], telemetry['Speed'], color=color)
        axs[0].set_ylabel('Speed (km/h)')
        axs[0].set_title(f'Speed Profile')
        axs[0].grid(True, alpha=0.3)
        
        # Plot throttle and brake
        axs[1].plot(telemetry['Distance'], telemetry['Throttle'], color='green', label='Throttle')
        if 'Brake' in telemetry.columns:
            axs[1].plot(telemetry['Distance'], telemetry['Brake'] * 100, color='red', label='Brake')  # Scale brake to percentage
        axs[1].set_ylabel('Percentage')
        axs[1].set_title('Throttle and Brake Application')
        axs[1].grid(True, alpha=0.3)
        axs[1].legend()
        
        # Plot gear if available
        if 'nGear' in telemetry.columns:
            axs[2].plot(telemetry['Distance'], telemetry['nGear'], color='purple')
            axs[2].set_ylabel('Gear')
            axs[2].set_xlabel('Distance (m)')
            axs[2].set_title('Gear Selection')
            axs[2].grid(True, alpha=0.3)
            # Set y-axis to integer steps for gears
            axs[2].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        else:
            # If no gear data, display a message
            axs[2].text(0.5, 0.5, "No gear data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=axs[2].transAxes)
            axs[2].set_ylabel('Gear')
            axs[2].set_xlabel('Distance (m)')
            axs[2].set_title('Gear Selection')
            axs[2].set_xticks([])
            axs[2].set_yticks([])
        
        # Overall title with lap time if available
        try:
            if 'LapTime' in lap.index and pd.notna(lap['LapTime']):
                lap_time = lap['LapTime'].total_seconds()
                fig.suptitle(f"Telemetry Data: {driver} - Lap {lap_number}\n"
                            f"Lap Time: {lap_time:.3f}s", 
                            fontsize=16)
            else:
                fig.suptitle(f"Telemetry Data: {driver} - Lap {lap_number}", fontsize=16)
        except:
            fig.suptitle(f"Telemetry Data: {driver} - Lap {lap_number}", fontsize=16)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Error generating telemetry: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_track_position(session, lap_number):
    """
    Visualize the positions of all drivers at a specific lap number.
    
    Args:
        session: FastF1 session object
        lap_number: The lap number to visualize
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get the laps from the session
        laps_at_lap = session.laps[session.laps['LapNumber'] == lap_number]
        
        # If we don't have position data, show error message
        if laps_at_lap.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"No data available for lap {lap_number}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Check if Position column exists
        if 'Position' not in laps_at_lap.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "Position data is not available for this session", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Sort by position
        laps_at_lap = laps_at_lap.sort_values(by='Position') if 'Position' in laps_at_lap.columns else laps_at_lap
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot each driver's position
        positions = []
        driver_labels = []
        driver_colors = []
        
        for _, lap in laps_at_lap.iterrows():
            try:
                driver = lap['Driver']
                position = lap['Position']
                
                # Skip if position is not a number
                if not pd.api.types.is_numeric_dtype(type(position)):
                    continue
                    
                team = lap['Team'] if 'Team' in lap else None
                color = get_driver_color(driver, team)
                
                positions.append(position)
                driver_labels.append(driver)
                driver_colors.append(color)
            except Exception as e:
                # Skip this driver on error
                continue
        
        # Check if we have any valid positions
        if not positions:
            ax.text(0.5, 0.5, "No valid position data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create the bar chart
        bars = ax.barh(positions, width=0.8, color=driver_colors)
        
        # Add driver abbreviations to the bars
        for i, (pos, driver) in enumerate(zip(positions, driver_labels)):
            ax.text(0.1, pos, driver, va='center', color='white', fontweight='bold')
        
        # Formatting
        ax.set_title(f'Driver Positions at Lap {lap_number}')
        ax.set_xlabel('Driver')
        ax.set_ylabel('Position')
        ax.set_yticks(range(1, len(positions) + 1))
        ax.set_xlim(0, 1)  # Fix the x-axis range
        ax.set_xticks([])  # Hide x-axis ticks
        ax.set_axisbelow(True)
        ax.grid(axis='y', alpha=0.3)
        
        # Invert y-axis so position 1 is at the top
        ax.invert_yaxis()
        
        plt.tight_layout()
        
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Error generating track position: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_lap_time_distribution(session):
    """
    Plot lap time distribution for all drivers.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Check if required columns exist
        required_cols = ['IsAccurate', 'LapTime']
        if not all(col in session.laps.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in session.laps.columns]
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"Missing required lap data columns: {missing_cols}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get all completed laps
        laps = session.laps
        
        # Try to filter out outliers
        try:
            valid_laps = laps[laps['IsAccurate'] & (laps['LapTime'] < pd.Timedelta(seconds=120))]
        except Exception:
            # If filtering fails, use all laps
            valid_laps = laps
            
        # Check if we have any valid laps after filtering
        if valid_laps.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, "No valid lap time data available for distribution analysis", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Try to convert lap times to seconds for plotting
        try:
            lap_times_seconds = valid_laps['LapTime'].dt.total_seconds()
        except:
            # If conversion fails, just use the raw values
            lap_times_seconds = valid_laps['LapTime']
            
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create histogram
        ax.hist(lap_times_seconds, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        
        # Add vertical line for median lap time
        try:
            median_time = np.median(lap_times_seconds)
            ax.axvline(x=median_time, color='red', linestyle='--', 
                    label=f'Median: {median_time:.3f}s')
        except:
            # If median calculation fails, skip it
            pass
        
        # Formatting
        ax.set_xlabel('Lap Time (seconds)')
        ax.set_ylabel('Frequency')
        ax.set_title('Lap Time Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Error generating lap time distribution: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_position_changes(session, drivers=None, laps=None):
    """
    Visualize position changes for drivers during the race.
    
    Args:
        session: FastF1 session object
        drivers: List of driver identifiers to include (optional, all drivers if None)
        laps: Range of laps to display (optional, all laps if None)
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data and it's a race session
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get unique driver IDs if not specified
        if drivers is None:
            if 'Driver' in session.laps.columns:
                all_drivers = session.laps['Driver'].unique()
                drivers = all_drivers.tolist()
            else:
                # Create a figure with a message
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.5, 0.5, "No driver data available in this session", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
        
        # Check if Position data is available
        if 'Position' not in session.laps.columns:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "Position data is not available for this session", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get lap range
        all_laps = sorted(session.laps['LapNumber'].unique())
        if not all_laps:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "No lap number data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        if laps is None:
            start_lap = all_laps[0]
            end_lap = all_laps[-1]
        else:
            start_lap, end_lap = laps
            
        # Filter laps within range
        lap_range = [lap for lap in all_laps if start_lap <= lap <= end_lap]
        
        # Create the figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Plot position changes for each driver
        for driver in drivers:
            try:
                # Get driver laps
                driver_laps = session.laps.pick_drivers(driver)
                
                if driver_laps.empty:
                    continue
                
                # Filter by lap range
                driver_laps = driver_laps[driver_laps['LapNumber'].isin(lap_range)]
                
                if driver_laps.empty:
                    continue
                
                # Get team color
                team = driver_laps['Team'].iloc[0] if 'Team' in driver_laps.columns else None
                color = get_driver_color(driver, team)
                
                # Plot positions
                ax.plot(driver_laps['LapNumber'], driver_laps['Position'], 
                       marker='o', linestyle='-', color=color, label=driver)
                
                # Add driver abbreviation at the last position
                try:
                    last_lap = driver_laps.iloc[-1]
                    ax.text(last_lap['LapNumber'] + 0.1, last_lap['Position'], 
                           driver, fontweight='bold', color=color)
                except:
                    pass
                
            except Exception as e:
                continue
        
        # Invert y-axis so position 1 is on top
        ax.invert_yaxis()
        
        # Set axis labels and grid
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Position')
        ax.set_title('Driver Position Changes Throughout the Race')
        ax.grid(True, alpha=0.3)
        
        # Set yticks to integers only (positions)
        from matplotlib.ticker import MaxNLocator
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Set xticks to integers only (lap numbers)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Add legend with smaller font size
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                 fancybox=True, shadow=True, ncol=5, fontsize='small')
        
        # Adjust layout
        try:
            plt.tight_layout()
        except Exception as e:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Error generating position changes visualization: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_team_pace_comparison(session):
    """
    Create a box plot comparing lap time distributions by team.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Check if Team data is available
        if 'Team' not in session.laps.columns:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "Team data is not available for this session", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get unique teams
        teams = session.laps['Team'].unique()
        
        if len(teams) == 0:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "No team data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Prepare data for box plot
        team_data = []
        team_colors = []
        team_labels = []
        
        for team in teams:
            try:
                # Get team laps
                team_laps = session.laps[session.laps['Team'] == team]
                
                if team_laps.empty:
                    continue
                
                # Filter valid laps and convert to seconds
                try:
                    valid_laps = team_laps[team_laps['IsAccurate'] & (team_laps['LapTime'] < pd.Timedelta(seconds=120))]
                except:
                    valid_laps = team_laps
                
                if valid_laps.empty:
                    continue
                
                # Convert lap times to seconds
                try:
                    lap_times = valid_laps['LapTime'].dt.total_seconds()
                    
                    if len(lap_times) > 0:
                        team_data.append(lap_times)
                        # Get team color (use first driver's color as team color)
                        if len(valid_laps['Driver'].unique()) > 0:
                            driver = valid_laps['Driver'].iloc[0]
                            color = get_driver_color(driver, team)
                        else:
                            color = 'gray'
                        team_colors.append(color)
                        team_labels.append(team)
                except:
                    continue
            except:
                continue
        
        # If no valid data, show error
        if len(team_data) == 0:
            ax.text(0.5, 0.5, "No valid lap time data available for team comparison", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create box plot
        box = ax.boxplot(team_data, patch_artist=True, labels=team_labels)
        
        # Color boxes according to team colors
        for patch, color in zip(box['boxes'], team_colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # Add labels and grid
        ax.set_xlabel('Team')
        ax.set_ylabel('Lap Time (seconds)')
        ax.set_title('Team Pace Comparison')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Format y-axis as time
        try:
            def format_seconds_as_time(x, pos):
                minutes, seconds = divmod(float(x), 60)
                return f"{int(minutes):01d}:{seconds:05.2f}"
            
            from matplotlib.ticker import FuncFormatter
            ax.yaxis.set_major_formatter(FuncFormatter(format_seconds_as_time))
        except:
            pass
        
        # Set overall min and max for better visibility
        all_times = np.concatenate(team_data)
        if len(all_times) > 0:
            min_time = np.min(all_times)
            max_time = np.max(all_times)
            ax.set_ylim(min_time - 1, max_time + 1)
        
        # Rotate x labels if many teams
        if len(team_labels) > 5:
            plt.xticks(rotation=45, ha='right')
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Error generating team pace comparison: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_laptimes_scatter(session, drivers=None):
    """
    Create a scatter plot of lap times with trend lines.
    
    Args:
        session: FastF1 session object
        drivers: List of driver identifiers to include (optional, all drivers if None)
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get unique driver IDs if not specified
        if drivers is None:
            if 'Driver' in session.laps.columns:
                all_drivers = session.laps['Driver'].unique()
                drivers = all_drivers.tolist()
            else:
                # Create a figure with a message
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.5, 0.5, "No driver data available in this session", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Flag to check if any driver data was plotted
        data_plotted = False
        
        # Plot lap times for each driver
        for driver in drivers:
            try:
                # Get driver laps
                driver_laps = session.laps.pick_drivers(driver)
                
                if driver_laps.empty:
                    continue
                
                # Check for required columns
                if 'LapTime' not in driver_laps.columns or 'LapNumber' not in driver_laps.columns:
                    continue
                
                # Filter out invalid laps
                try:
                    valid_laps = driver_laps[driver_laps['IsAccurate'] & (driver_laps['LapTime'] < pd.Timedelta(seconds=120))]
                except:
                    valid_laps = driver_laps[pd.notna(driver_laps['LapTime'])]
                
                if valid_laps.empty:
                    continue
                
                # Get team color
                team = valid_laps['Team'].iloc[0] if 'Team' in valid_laps.columns else None
                color = get_driver_color(driver, team)
                
                # Convert lap times to seconds
                try:
                    lap_times = valid_laps['LapTime'].dt.total_seconds()
                    
                    # Plot scatter points
                    ax.scatter(valid_laps['LapNumber'], lap_times, color=color, 
                              alpha=0.7, s=50, label=driver)
                    
                    # Add trend line (polynomial fit)
                    if len(lap_times) > 2:
                        try:
                            x = valid_laps['LapNumber']
                            y = lap_times
                            z = np.polyfit(x, y, 2)
                            p = np.poly1d(z)
                            
                            # Create smooth x values for the trend line
                            x_smooth = np.linspace(x.min(), x.max(), 100)
                            ax.plot(x_smooth, p(x_smooth), color=color, linestyle='--', alpha=0.7)
                        except:
                            # Skip trend line if it fails
                            pass
                    
                    data_plotted = True
                except:
                    continue
            except:
                continue
        
        # Check if any data was plotted
        if not data_plotted:
            ax.text(0.5, 0.5, "No valid lap time data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Add labels and grid
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (seconds)')
        ax.set_title('Driver Lap Times Scatter')
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as time
        try:
            def format_seconds_as_time(x, pos):
                minutes, seconds = divmod(float(x), 60)
                return f"{int(minutes):01d}:{seconds:05.2f}"
            
            from matplotlib.ticker import FuncFormatter
            ax.yaxis.set_major_formatter(FuncFormatter(format_seconds_as_time))
        except:
            pass
        
        # Add legend with smaller font size
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                 fancybox=True, shadow=True, ncol=5, fontsize='small')
        
        # Set xticks to integers only (lap numbers)
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Error generating lap times scatter plot: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_tyre_strategies(session):
    """
    Visualize tyre strategies used by drivers during a race with improved visualization of stint lengths.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Check if Compound data is available
        if 'Compound' not in session.laps.columns:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "Tyre compound data is not available for this session", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get unique drivers
        if 'Driver' not in session.laps.columns:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "Driver data is not available in this session", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        drivers = session.laps['Driver'].unique()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Define tyre compound colors
        compound_colors = {
            'SOFT': 'red',
            'MEDIUM': 'yellow',
            'HARD': 'white',
            'INTERMEDIATE': 'green',
            'WET': 'blue'
        }
        
        # Dictionary to store last stint end for each driver
        last_stint_end = {}
        
        # Track if we have any strategy data
        has_strategy_data = False
        
        # Plot tyre stints for each driver
        y_positions = {}
        driver_position = 0
        
        # Sort drivers by finishing position if available
        try:
            if session.results is not None:
                results_df = pd.DataFrame(session.results)
                if 'Abbreviation' in results_df.columns and 'Position' in results_df.columns:
                    sorted_drivers = results_df.sort_values(by='Position')['Abbreviation'].tolist() if 'Position' in results_df.columns else results_df['Abbreviation'].tolist()
                    # Keep only drivers that are in our lap data
                    sorted_drivers = [d for d in sorted_drivers if d in drivers]
                    # Append any drivers in lap data but not in results
                    sorted_drivers.extend([d for d in drivers if d not in sorted_drivers])
                    drivers = sorted_drivers
        except:
            pass
            
        for driver in drivers:
            driver_position += 1
            y_positions[driver] = driver_position
            
            try:
                # Get driver laps
                driver_laps = session.laps.pick_drivers(driver)
                
                if driver_laps.empty:
                    continue
                
                # Get team color
                team = driver_laps['Team'].iloc[0] if 'Team' in driver_laps.columns else None
                
                # Identify tyre stints by finding where compound changes
                stints = []
                current_stint = {
                    'start': driver_laps['LapNumber'].min(),
                    'compound': driver_laps.iloc[0]['Compound'] if pd.notna(driver_laps.iloc[0]['Compound']) else 'Unknown'
                }
                
                for idx, lap in driver_laps.iterrows():
                    if pd.isna(lap['Compound']):
                        continue
                        
                    if current_stint['compound'] != lap['Compound']:
                        # End previous stint
                        current_stint['end'] = lap['LapNumber'] - 1
                        stints.append(current_stint)
                        
                        # Start new stint
                        current_stint = {
                            'start': lap['LapNumber'],
                            'compound': lap['Compound']
                        }
                
                # Add final stint
                current_stint['end'] = driver_laps['LapNumber'].max()
                stints.append(current_stint)
                
                # Plot each stint
                for stint in stints:
                    if 'start' not in stint or 'end' not in stint or 'compound' not in stint:
                        continue
                        
                    compound = stint['compound']
                    color = compound_colors.get(compound.upper(), 'gray')
                    
                    # Plot the stint as a horizontal bar
                    ax.barh(
                        y=driver_position,
                        width=stint['end'] - stint['start'] + 1,
                        left=stint['start'],
                        height=0.6,
                        color=color,
                        alpha=0.7,
                        edgecolor='black'
                    )
                    
                    # Add compound label if the stint is wide enough
                    if stint['end'] - stint['start'] > 5:  # Only add text if stint is more than 5 laps
                        ax.text(
                            (stint['start'] + stint['end']) / 2,
                            driver_position,
                            compound,
                            ha='center',
                            va='center',
                            fontsize=8,
                            fontweight='bold',
                            color='black'
                        )
                    
                    # Update last stint end
                    last_stint_end[driver] = max(last_stint_end.get(driver, 0), stint['end'])
                    has_strategy_data = True
                    
                # Add driver label at the end
                try:
                    if driver in last_stint_end:
                        ax.text(
                            last_stint_end[driver] + 1,
                            driver_position,
                            driver,
                            va='center',
                            fontsize=10,
                            fontweight='bold'
                        )
                except:
                    pass
            except Exception as e:
                continue
        
        # Check if we have any strategy data
        if not has_strategy_data:
            ax.text(0.5, 0.5, "No valid tyre strategy data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Set axis properties
        ax.set_xlabel('Lap Number')
        ax.set_yticks([])  # Hide y-ticks since we use driver labels
        ax.set_title('Tyre Strategies')
        ax.grid(True, axis='x', alpha=0.3)
        
        # Set x-axis to show integer lap numbers
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Add legend for tyre compounds
        legend_patches = [
            plt.Rectangle((0, 0), 1, 1, color=color, alpha=0.7, edgecolor='black')
            for compound, color in compound_colors.items()
        ]
        ax.legend(
            legend_patches,
            compound_colors.keys(),
            loc='upper center',
            bbox_to_anchor=(0.5, -0.05),
            ncol=len(compound_colors),
            fancybox=True,
            shadow=True
        )
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Error generating tyre strategies visualization: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_qualifying_results(session):
    """
    Create a visualization of qualifying session results.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get fastest laps for all drivers
        fastest_laps = session.laps.pick_fastest()
        
        if fastest_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "No fastest lap data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Convert lap times to seconds and sort by time
        try:
            fastest_laps['LapTimeSeconds'] = fastest_laps['LapTime'].dt.total_seconds()
            fastest_laps = fastest_laps.sort_values(by='LapTimeSeconds') if 'LapTimeSeconds' in fastest_laps.columns else fastest_laps
        except:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "Error processing lap time data", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Reset index to get positions
        fastest_laps = fastest_laps.reset_index(drop=True)
        fastest_laps['Position'] = fastest_laps.index + 1
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Calculate pole time for reference
        pole_time = fastest_laps.iloc[0]['LapTimeSeconds']
        
        # Calculate time deltas from pole
        fastest_laps['DeltaToPole'] = fastest_laps['LapTimeSeconds'] - pole_time
        
        # Create horizontal bars for each driver
        for index, lap in fastest_laps.iterrows():
            try:
                # Get driver color
                team = lap['Team'] if 'Team' in lap.index else None
                driver = lap['Driver']
                color = get_driver_color(driver, team)
                
                position = lap['Position']
                delta = lap['DeltaToPole']
                
                # Plot time bar
                ax.barh(
                    y=position,
                    width=delta,
                    left=pole_time,
                    height=0.7,
                    color=color,
                    alpha=0.7
                )
                
                # Add driver name
                ax.text(
                    pole_time - 0.1,
                    position,
                    driver,
                    ha='right',
                    va='center',
                    fontweight='bold'
                )
                
                # Add lap time
                time_str = f"{int(lap['LapTimeSeconds'] // 60):01d}:{lap['LapTimeSeconds'] % 60:06.3f}"
                ax.text(
                    pole_time + delta + 0.05,
                    position,
                    time_str,
                    va='center'
                )
                
                # Add delta for all except pole
                if position > 1:
                    ax.text(
                        pole_time + delta / 2,
                        position,
                        f"+{delta:.3f}s",
                        ha='center',
                        va='center',
                        fontsize=9,
                        fontweight='bold',
                        color='white'
                    )
            except Exception as e:
                continue
        
        # Invert y-axis so position 1 is on top
        ax.invert_yaxis()
        
        # Add labels and title
        ax.set_title('Qualifying Results')
        ax.set_xlabel('Lap Time (seconds)')
        ax.set_yticks([])  # Hide y ticks
        
        # Add gridlines
        ax.grid(True, axis='x', alpha=0.3)
        
        # Format x-axis as time
        try:
            def format_seconds_as_time(x, pos):
                minutes, seconds = divmod(float(x), 60)
                return f"{int(minutes):01d}:{seconds:06.3f}"
            
            from matplotlib.ticker import FuncFormatter
            ax.xaxis.set_major_formatter(FuncFormatter(format_seconds_as_time))
        except:
            pass
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Error generating qualifying results visualization: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_gear_shifts_on_track(session, driver, lap_number):
    """
    Visualize gear shifts on the track layout.
    
    Args:
        session: FastF1 session object
        driver: Driver identifier
        lap_number: Lap number to visualize
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get lap data for the driver
        laps = session.laps.pick_drivers(driver)
        
        if laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, f"No lap data available for {driver}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get the specific lap
        specific_laps = laps[laps['LapNumber'] == lap_number]
        
        if specific_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, f"No data available for lap {lap_number}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        lap = specific_laps.iloc[0]
        
        # Get telemetry data
        telemetry = lap.get_telemetry()
        telemetry = optimize_dataframe(telemetry)  # Optimize the dataframe
        
        # Check if we have the required data
        if telemetry.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, "No telemetry data available for this lap", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Check if we have the necessary columns
        required_cols = ['X', 'Y', 'nGear']
        if not all(col in telemetry.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in telemetry.columns]
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, f"Missing required telemetry data: {missing_cols}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Get driver color
        team = lap['Team'] if 'Team' in lap.index else None
        color = get_driver_color(driver, team)
        
        # Plot track layout
        ax.plot(telemetry['X'], telemetry['Y'], color='black', linestyle='-', alpha=0.5)
        
        # Detect gear changes
        gear_changes = []
        prev_gear = telemetry.iloc[0]['nGear']
        
        for idx, row in telemetry.iterrows():
            current_gear = row['nGear']
            if current_gear != prev_gear:
                gear_changes.append({
                    'x': row['X'],
                    'y': row['Y'],
                    'old_gear': prev_gear,
                    'new_gear': current_gear
                })
                prev_gear = current_gear
        
        # Plot gear shift points
        for change in gear_changes:
            # Upshift: green, Downshift: red
            shift_color = 'green' if change['new_gear'] > change['old_gear'] else 'red'
            
            ax.scatter(change['x'], change['y'], color=shift_color, s=100, 
                     marker='^' if change['new_gear'] > change['old_gear'] else 'v',
                     zorder=3)
            
            # Add gear number
            ax.text(change['x'], change['y'], f"{change['old_gear']}→{change['new_gear']}", 
                   fontsize=8, ha='center', va='center',
                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2'))
        
        # Mark start/finish point
        if len(telemetry) > 0:
            ax.scatter(telemetry.iloc[0]['X'], telemetry.iloc[0]['Y'], color='blue', s=150, marker='o', label='Start')
            ax.text(telemetry.iloc[0]['X'], telemetry.iloc[0]['Y'], 'S/F', fontsize=10, ha='center', va='center')
        
        # Equal aspect ratio to prevent distortion
        ax.set_aspect('equal')
        
        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add title
        ax.set_title(f"Gear Shifts on Track - {driver} - Lap {lap_number}")
        
        # Add legend for shift types
        up_marker = plt.Line2D([], [], color='green', marker='^', linestyle='None', markersize=10, label='Upshift')
        down_marker = plt.Line2D([], [], color='red', marker='v', linestyle='None', markersize=10, label='Downshift')
        
        ax.legend(handles=[up_marker, down_marker], loc='lower right')
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.text(0.5, 0.5, f"Error generating gear shifts visualization: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_laptime_distribution(session, driver=None):
    """
    Create a distribution plot of lap times with kernel density estimate.
    
    Args:
        session: FastF1 session object
        driver: Optional driver identifier to focus on a single driver
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Create figure with 2 subplots (histogram and boxplot)
        fig = plt.figure(figsize=(14, 10))
        gs = GridSpec(2, 1, height_ratios=[3, 1], figure=fig)
        
        ax1 = fig.add_subplot(gs[0])  # Histogram
        ax2 = fig.add_subplot(gs[1])  # Boxplot
        
        # Get lap data to use
        if driver is not None:
            driver_laps = session.laps.pick_drivers(driver)
            if driver_laps.empty:
                # Create a figure with a message
                plt.clf()
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.5, 0.5, f"No lap data available for {driver}", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                ax.set_xticks([])
                ax.set_yticks([])
                return fig
                
            # Filter valid laps
            try:
                valid_laps = driver_laps[driver_laps['IsAccurate'] & (driver_laps['LapTime'] < pd.Timedelta(seconds=120))]
            except:
                valid_laps = driver_laps[pd.notna(driver_laps['LapTime'])]
                
            team = driver_laps['Team'].iloc[0] if 'Team' in driver_laps.columns else None
            color = get_driver_color(driver, team)
        else:
            # Use all drivers data
            try:
                valid_laps = session.laps[session.laps['IsAccurate'] & (session.laps['LapTime'] < pd.Timedelta(seconds=120))]
            except:
                valid_laps = session.laps[pd.notna(session.laps['LapTime'])]
                
            color = 'blue'
        
        if valid_laps.empty:
            # Create a figure with a message
            plt.clf()
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "No valid lap time data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Convert lap times to seconds for plotting
        try:
            lap_times = valid_laps['LapTime'].dt.total_seconds()
        except:
            # Create a figure with a message
            plt.clf()
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, "Error processing lap time data", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create the histogram with density estimate
        n, bins, patches = ax1.hist(lap_times, bins=20, density=True, alpha=0.6, color=color)
        
        # Add kernel density estimate if we have enough points
        if len(lap_times) > 5:
            try:
                from scipy import stats
                kde = stats.gaussian_kde(lap_times)
                x_vals = np.linspace(lap_times.min() - 0.5, lap_times.max() + 0.5, 100)
                ax1.plot(x_vals, kde(x_vals), 'r-', linewidth=2)
            except:
                pass
        
        # Add median and mean lines
        median_laptime = np.median(lap_times)
        mean_laptime = np.mean(lap_times)
        
        ax1.axvline(x=median_laptime, color='black', linestyle='--', 
                   label=f'Median: {median_laptime:.3f}s')
        ax1.axvline(x=mean_laptime, color='green', linestyle=':', 
                   label=f'Mean: {mean_laptime:.3f}s')
        
        # Add fastest lap line
        fastest_laptime = lap_times.min()
        ax1.axvline(x=fastest_laptime, color='red', linestyle='-', 
                   label=f'Fastest: {fastest_laptime:.3f}s')
        
        # Add labels and title to histogram
        title = f"{driver} Lap Time Distribution" if driver else "All Drivers Lap Time Distribution"
        ax1.set_title(title)
        ax1.set_xlabel('Lap Time (seconds)')
        ax1.set_ylabel('Density')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Format x-axis as time
        try:
            def format_seconds_as_time(x, pos):
                minutes, seconds = divmod(float(x), 60)
                return f"{int(minutes):01d}:{seconds:05.2f}"
            
            from matplotlib.ticker import FuncFormatter
            ax1.xaxis.set_major_formatter(FuncFormatter(format_seconds_as_time))
        except:
            pass
        
        # Create the boxplot
        ax2.boxplot(lap_times, vert=False, patch_artist=True, 
                   boxprops=dict(facecolor=color, alpha=0.6))
        
        # Add some statistics as text annotations
        stats_text = (
            f"Min: {lap_times.min():.3f}s, "
            f"Q1: {np.percentile(lap_times, 25):.3f}s, "
            f"Median: {median_laptime:.3f}s, "
            f"Q3: {np.percentile(lap_times, 75):.3f}s, "
            f"Max: {lap_times.max():.3f}s"
        )
        ax2.text(0.5, 0.5, stats_text, 
                transform=ax2.transAxes, 
                horizontalalignment='center',
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
        
        # Format x-axis as time for boxplot
        try:
            ax2.xaxis.set_major_formatter(FuncFormatter(format_seconds_as_time))
        except:
            pass
        
        # Hide y-ticks on boxplot
        ax2.set_yticks([])
        ax2.set_xlabel('Lap Time (seconds)')
        ax2.grid(True, axis='x', alpha=0.3)
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Error generating lap time distribution: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
def plot_speed_trace_with_corners(session, driver, lap_number):
    """
    Create a speed trace visualization with corner annotations.
    
    Args:
        session: FastF1 session object
        driver: Driver identifier
        lap_number: Lap number to visualize
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get lap data for the driver
        driver_laps = session.laps.pick_drivers(driver)
        
        if driver_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.text(0.5, 0.5, f"No lap data available for {driver}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get the specific lap
        specific_laps = driver_laps[driver_laps['LapNumber'] == lap_number]
        
        if specific_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.text(0.5, 0.5, f"No data available for lap {lap_number}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        lap = specific_laps.iloc[0]
        
        # Get telemetry data
        telemetry = lap.get_telemetry()
        telemetry = optimize_dataframe(telemetry)  # Optimize the dataframe
        
        if telemetry.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.text(0.5, 0.5, "No telemetry data available for this lap", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Check if we have the necessary data
        required_cols = ['Distance', 'Speed']
        if not all(col in telemetry.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in telemetry.columns]
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.text(0.5, 0.5, f"Missing required telemetry data: {missing_cols}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Get driver color
        team = lap['Team'] if 'Team' in lap.index else None
        color = get_driver_color(driver, team)
        
        # Plot speed trace
        ax.plot(telemetry['Distance'], telemetry['Speed'], 
               color=color, linewidth=2, label=f"{driver} Speed")
        
        # Add markers for minimum speed points (potential corners)
        # Use a sliding window to find local minima
        window_size = 10  # Adjust based on data density
        min_pts = []
        
        for i in range(window_size, len(telemetry) - window_size):
            window = telemetry['Speed'].iloc[i-window_size:i+window_size]
            if telemetry['Speed'].iloc[i] == window.min():
                # This is a local minimum (potential corner)
                min_pts.append(i)
        
        # Filter out minimum points that are too close to each other
        filtered_min_pts = []
        min_distance = 100  # Minimum distance between corners in meters
        
        if min_pts:
            filtered_min_pts.append(min_pts[0])
            for pt in min_pts[1:]:
                if abs(telemetry['Distance'].iloc[pt] - telemetry['Distance'].iloc[filtered_min_pts[-1]]) > min_distance:
                    filtered_min_pts.append(pt)
        
        # Plot the corner points and add annotations
        for i, pt_idx in enumerate(filtered_min_pts):
            corner_num = i + 1
            distance = telemetry['Distance'].iloc[pt_idx]
            speed = telemetry['Speed'].iloc[pt_idx]
            
            # Add marker for corner
            ax.scatter(distance, speed, color='red', s=100, zorder=3)
            
            # Add corner number annotation
            ax.annotate(
                f"T{corner_num}",
                xy=(distance, speed),
                xytext=(0, -20),
                textcoords='offset points',
                ha='center',
                va='top',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7)
            )
        
        # Calculate the speed change rate to highlight braking zones
        if 'Time' in telemetry.columns:
            try:
                telemetry['TimeSeconds'] = telemetry['Time'].dt.total_seconds()
                telemetry['SpeedChange'] = telemetry['Speed'].diff() / telemetry['TimeSeconds'].diff()
                
                # Highlight heavy braking zones (significant negative speed change)
                braking_threshold = -2.0  # Adjust based on data
                braking_points = telemetry[telemetry['SpeedChange'] < braking_threshold]
                
                if not braking_points.empty:
                    ax.scatter(braking_points['Distance'], braking_points['Speed'], 
                              color='blue', s=30, alpha=0.5, label='Braking Points')
            except:
                pass
        
        # Add DRS zones if available
        if 'DRS' in telemetry.columns:
            try:
                # Find DRS activation points
                drs_changes = telemetry['DRS'].diff().fillna(0)
                drs_activations = telemetry[drs_changes > 0]
                drs_deactivations = telemetry[drs_changes < 0]
                
                # Highlight DRS zones
                for i, (act_idx, act_row) in enumerate(drs_activations.iterrows()):
                    try:
                        # Find the corresponding deactivation
                        deact_rows = drs_deactivations[drs_deactivations.index > act_idx]
                        if not deact_rows.empty:
                            deact_row = deact_rows.iloc[0]
                            
                            # Add DRS zone highlight
                            ax.axvspan(
                                act_row['Distance'],
                                deact_row['Distance'],
                                alpha=0.2,
                                color='green',
                                label='DRS Zone' if i == 0 else ""
                            )
                            
                            # Add DRS text
                            mid_dist = (act_row['Distance'] + deact_row['Distance']) / 2
                            mid_speed = np.interp(mid_dist, telemetry['Distance'], telemetry['Speed'])
                            ax.text(mid_dist, mid_speed + 10, 'DRS', 
                                   ha='center', va='bottom', fontsize=10,
                                   bbox=dict(boxstyle='round,pad=0.2', fc='green', alpha=0.3))
                    except:
                        continue
            except:
                pass
        
        # Set axis labels and title
        try:
            lap_time = lap['LapTime'].total_seconds()
            ax.set_title(f"Speed Trace - {driver} - Lap {lap_number} - {lap_time:.3f}s")
        except:
            ax.set_title(f"Speed Trace - {driver} - Lap {lap_number}")
            
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Speed (km/h)')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.text(0.5, 0.5, f"Error generating speed trace with corners: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_tyre_degradation(session, driver_code):
    """
    Plot tyre degradation for a specific driver showing lap times grouped by tyre stint.
    Steeper slopes indicate higher degradation.
    
    Args:
        session: FastF1 session object
        driver_code: Driver identifier (e.g., 'VER', 'HAM')
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
        
    try:
        # Get driver data
        driver_laps = session.laps.pick_drivers(driver_code)
        
        if driver_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"No lap data available for {driver_code}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        # Check if we have required columns
        required_cols = ['LapNumber', 'LapTime', 'Compound', 'Stint']
        missing_cols = [col for col in required_cols if col not in driver_laps.columns]
        
        if missing_cols:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"Missing required columns: {', '.join(missing_cols)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        # Filter out invalid lap times
        driver_laps = driver_laps.dropna(subset=['LapTime'])
        
        # Convert lap times to seconds for easier plotting
        lap_times_sec = []
        for lap_time in driver_laps['LapTime']:
            try:
                # If it's already a timedelta, convert to seconds
                if hasattr(lap_time, 'total_seconds'):
                    lap_times_sec.append(lap_time.total_seconds())
                else:
                    lap_times_sec.append(float(lap_time))
            except (ValueError, TypeError):
                # Skip invalid lap times
                lap_times_sec.append(np.nan)
                
        # Add the converted lap times to the dataframe
        driver_laps['LapTime_sec'] = lap_times_sec
        
        # Drop rows with NaN values in LapTime_sec
        driver_laps = driver_laps.dropna(subset=['LapTime_sec'])
        
        if len(driver_laps) == 0:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f"No valid lap time data available for {driver_code}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get number of stints
        if 'Stint' in driver_laps.columns:
            stints = driver_laps['Stint'].unique()
        else:
            # If no stint information, try to infer from compound changes
            stints = [1] # Default to 1 stint if we can't infer
            if 'Compound' in driver_laps.columns:
                prev_compound = None
                stint_num = 1
                stint_data = []
                
                for _, lap in driver_laps.iterrows():
                    if prev_compound is None:
                        prev_compound = lap['Compound']
                        stint_data.append(stint_num)
                    elif lap['Compound'] != prev_compound:
                        stint_num += 1
                        prev_compound = lap['Compound']
                        stint_data.append(stint_num)
                    else:
                        stint_data.append(stint_num)
                        
                driver_laps['Stint'] = stint_data
                stints = driver_laps['Stint'].unique()
        
        # Define colors for different compounds
        compound_colors = {
            'SOFT': 'red',
            'MEDIUM': 'yellow',
            'HARD': 'white',
            'INTERMEDIATE': 'green',
            'WET': 'blue',
            'C1': '#ffb3b3', # Very light red
            'C2': '#ff9999', # Light red
            'C3': '#ff8080', # Soft red
            'C4': '#ff6666', # Medium red
            'C5': '#ff4d4d', # Hard red
            # Add any other compound names as needed
        }
        
        # Get team color for lines
        team = driver_laps['Team'].iloc[0] if 'Team' in driver_laps.columns else None
        driver_color = get_driver_color(driver_code, team)
        
        # Plot each stint
        for stint in sorted(stints):
            stint_laps = driver_laps[driver_laps['Stint'] == stint]
            
            # Skip empty stints
            if len(stint_laps) <= 1:  # Need at least 2 points for a line
                continue
                
            compound = stint_laps['Compound'].iloc[0] if 'Compound' in stint_laps.columns else 'Unknown'
            
            # Get the color for this compound
            color = compound_colors.get(compound, driver_color)
            
            # Plot the lap times for this stint
            ax.plot(stint_laps['LapNumber'], stint_laps['LapTime_sec'], 
                   marker='o', label=f'Stint {stint} ({compound})', 
                   color=color if compound != 'Unknown' else driver_color,
                   linestyle='-', linewidth=2)
            
            # Add trend line to show degradation
            try:
                x = stint_laps['LapNumber'].astype(float).values
                y = stint_laps['LapTime_sec'].values
                
                # Only add trend line if we have enough points
                if len(x) > 2:  # Need at least 3 points for a good trend line
                    z = np.polyfit(x, y, 1)
                    p = np.poly1d(z)
                    ax.plot(x, p(x), '--', color=color if compound != 'Unknown' else 'gray',
                           linewidth=1.5, alpha=0.7)
                    
                    # Annotate the slope (degradation rate)
                    slope = z[0]  # seconds per lap
                    ax.annotate(f'{slope:.3f} sec/lap', 
                              xy=(x[-1], p(x)[-1]),
                              xytext=(10, 0),
                              textcoords='offset points',
                              ha='left', va='center',
                              fontsize=8,
                              color=color if compound != 'Unknown' else 'gray')
            except Exception as e:
                # If trend line fitting fails, continue without it
                print(f"Error fitting trend line for stint {stint}: {e}")
                pass
        
        # Add labels and title
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (seconds)')
        ax.set_title(f'Tyre Degradation for {driver_code} by Stint')
        
        # Format y-axis as time
        def format_seconds_as_time(x, pos):
            minutes, seconds = divmod(x, 60)
            return f"{int(minutes):d}:{seconds:06.3f}"
            
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(format_seconds_as_time))
        
        # Add grid and legend
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        # Adjust layout
        plt.tight_layout()
        
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Error generating tyre degradation plot: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def plot_track_map_with_corners(session):
    """
    Create a track map with numbered corners.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # We need to find a lap with good position data to draw the track
        good_lap = None
        
        # Try to find a good representative lap from any driver
        for driver in session.laps['Driver'].unique():
            driver_laps = session.laps.pick_drivers(driver)
            
            if driver_laps.empty:
                continue
                
            # Try to use a middle lap as it's likely to be a clean lap
            lap_numbers = sorted(driver_laps['LapNumber'].unique())
            if len(lap_numbers) > 0:
                middle_lap_num = lap_numbers[len(lap_numbers) // 2]
                middle_lap = driver_laps[driver_laps['LapNumber'] == middle_lap_num]
                
                if not middle_lap.empty:
                    lap = middle_lap.iloc[0]
                    telemetry = lap.get_telemetry()
                    
                    # Check if we have position data
                    if not telemetry.empty and 'X' in telemetry.columns and 'Y' in telemetry.columns:
                        if len(telemetry) > 100:  # Ensure we have enough data points
                            good_lap = (lap, telemetry)
                            break
        
        if good_lap is None:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, "No suitable track position data available", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        lap, telemetry = good_lap
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot track outline
        ax.plot(telemetry['X'], telemetry['Y'], 
               color='black', linestyle='-', linewidth=3, alpha=0.7)
        
        # Fill the track outline with light gray
        ax.fill(telemetry['X'], telemetry['Y'], 
               color='lightgray', alpha=0.3)
        
        # Mark start/finish line
        ax.scatter(telemetry['X'].iloc[0], telemetry['Y'].iloc[0], 
                  color='red', s=200, marker='o', zorder=5, label='Start/Finish')
        
        # Use a sliding window to find minimum speed points (corners)
        window_size = 10  # Adjust based on data density
        corners = []
        
        if 'Speed' in telemetry.columns:
            for i in range(window_size, len(telemetry) - window_size):
                window = telemetry['Speed'].iloc[i-window_size:i+window_size]
                if telemetry['Speed'].iloc[i] == window.min():
                    # This is a local minimum (potential corner)
                    corners.append(i)
            
            # Filter out corners that are too close to each other
            filtered_corners = []
            min_distance = 50  # Minimum distance between corners
            
            if corners:
                filtered_corners.append(corners[0])
                for corner in corners[1:]:
                    x1, y1 = telemetry['X'].iloc[corner], telemetry['Y'].iloc[corner]
                    x2, y2 = telemetry['X'].iloc[filtered_corners[-1]], telemetry['Y'].iloc[filtered_corners[-1]]
                    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    if distance > min_distance:
                        filtered_corners.append(corner)
            
            # Plot and number the corners
            for i, corner_idx in enumerate(filtered_corners):
                x, y = telemetry['X'].iloc[corner_idx], telemetry['Y'].iloc[corner_idx]
                
                # Add marker for corner
                ax.scatter(x, y, color='blue', s=100, zorder=4)
                
                # Add corner number
                ax.text(x, y, str(i+1), fontsize=12, ha='center', va='center', 
                       fontweight='bold', color='white',
                       bbox=dict(boxstyle='circle', facecolor='blue', alpha=0.8, pad=0.2))
        
        # Try to find DRS zones if DRS data is available
        if 'DRS' in telemetry.columns:
            try:
                # Find DRS activation points
                drs_changes = telemetry['DRS'].diff().fillna(0)
                drs_activations = telemetry[drs_changes > 0]
                
                # Mark DRS zones
                for _, act_row in drs_activations.iterrows():
                    idx = act_row.name
                    x, y = telemetry['X'].iloc[idx], telemetry['Y'].iloc[idx]
                    
                    # Add DRS zone marker
                    ax.scatter(x, y, color='green', s=100, zorder=4, marker='s')
                    
                    # Add DRS text
                    ax.text(x, y, 'DRS', fontsize=10, ha='center', va='center', 
                           fontweight='bold', color='white',
                           bbox=dict(boxstyle='round', facecolor='green', alpha=0.8, pad=0.2))
            except:
                pass
        
        # Add track name and info if available
        track_name = ""
        
        if hasattr(session, 'event'):
            if isinstance(session.event, dict):
                track_name = session.event.get('EventName', '')
            else:
                track_name = getattr(session.event, 'EventName', '')
        
        ax.set_title(f"{track_name} Track Map" if track_name else "Track Map")
        
        # Equal aspect ratio to prevent distortion
        ax.set_aspect('equal')
        
        # Remove axis ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_axis_off()
        
        # Add north arrow indicator
        arrow_x = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05 + ax.get_xlim()[0]
        arrow_y = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.9 + ax.get_ylim()[0]
        arrow_len = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.03
        
        ax.arrow(arrow_x, arrow_y, 0, arrow_len, head_width=arrow_len/2, 
                head_length=arrow_len/2, fc='black', ec='black')
        ax.text(arrow_x, arrow_y + arrow_len + arrow_len/2, 'N', 
               ha='center', va='center', fontweight='bold')
        
        # Add race direction indicator (clockwise/counterclockwise)
        # This is a simplified heuristic based on the first few points
        if len(telemetry) > 30:
            try:
                x1, y1 = telemetry['X'].iloc[0], telemetry['Y'].iloc[0]
                x2, y2 = telemetry['X'].iloc[30], telemetry['Y'].iloc[30]
                
                # Calculate the cross product to determine direction
                cross_product = (x2 - x1) * 0 - (y2 - y1) * 1  # Assuming North is (0,1)
                direction = "Clockwise" if cross_product > 0 else "Counter-Clockwise"
                
                # Add race direction text
                direction_x = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.95 + ax.get_xlim()[0]
                direction_y = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05 + ax.get_ylim()[0]
                
                ax.text(direction_x, direction_y, f"Race Direction: {direction}", 
                       ha='right', va='bottom', fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, pad=0.3))
            except:
                pass
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.text(0.5, 0.5, f"Error generating track map: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

def create_speed_trace(session, driver, lap_number):
    """
    Create a speed trace map visualization on the track layout.
    
    Args:
        session: FastF1 session object
        driver: Driver identifier
        lap_number: Lap number to visualize
    
    Returns:
        Matplotlib figure
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        # Create a figure with a message
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.text(0.5, 0.5, "No lap data available for this session", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    try:
        # Get lap data for the driver
        laps = session.laps.pick_drivers(driver)
        
        if laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, f"No lap data available for {driver}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Get the specific lap
        specific_laps = laps[laps['LapNumber'] == lap_number]
        
        if specific_laps.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, f"No data available for lap {lap_number}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        lap = specific_laps.iloc[0]
        
        # Get telemetry data
        telemetry = lap.get_telemetry()
        telemetry = optimize_dataframe(telemetry)  # Optimize the dataframe
        
        if telemetry.empty:
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, "No telemetry data available for this lap", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Check if we have the necessary columns
        required_cols = ['X', 'Y', 'Speed']
        if not all(col in telemetry.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in telemetry.columns]
            # Create a figure with a message
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.text(0.5, 0.5, f"Missing required telemetry data: {missing_cols}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Get driver color
        team = lap['Team'] if 'Team' in lap.index else None
        color = get_driver_color(driver, team)
        
        # Create a colormap based on speed
        min_speed = telemetry['Speed'].min()
        max_speed = telemetry['Speed'].max()
        
        # Create line segments for the speed trace
        points = np.array([telemetry['X'], telemetry['Y']]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # Create a LineCollection with the colormap
        norm = plt.Normalize(min_speed, max_speed)
        lc = LineCollection(segments, cmap='viridis', norm=norm, linewidth=3, alpha=0.8)
        
        # Set the color values to the speed
        lc.set_array(telemetry['Speed'])
        line = ax.add_collection(lc)
        
        # Add a color bar
        cbar = fig.colorbar(line, ax=ax)
        cbar.set_label('Speed (km/h)')
        
        # Mark start/finish point
        ax.scatter(telemetry['X'].iloc[0], telemetry['Y'].iloc[0], 
                  color='red', s=100, marker='o', label='Start/Finish')
        
        # Equal aspect ratio to prevent distortion
        ax.set_aspect('equal')
        
        # Add labels and title
        try:
            lap_time = lap['LapTime'].total_seconds()
            ax.set_title(f"Speed Trace - {driver} - Lap {lap_number} - {lap_time:.3f}s")
        except:
            ax.set_title(f"Speed Trace - {driver} - Lap {lap_number}")
        
        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add legend
        ax.legend(loc='upper right')
        
        # Adjust layout
        try:
            plt.tight_layout()
        except:
            pass
            
        return fig
    except Exception as e:
        # Catch-all for any other errors
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.text(0.5, 0.5, f"Error generating speed trace: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
def analyze_sector_times(session):
    """
    Analyze sector times for all drivers in a session. Identifies the overall fastest lap
    and the fastest individual sectors.
    
    Args:
        session: FastF1 session object
    
    Returns:
        DataFrame with fastest sector times data or None if data not available
    """
    import pandas as pd
    
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        return None
    
    try:
        # Get laps with sector time data
        laps_with_times = session.laps.dropna(subset=['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time'])
        
        if laps_with_times.empty:
            return None
        
        # Find the overall fastest lap
        fastest_overall = laps_with_times.loc[laps_with_times['LapTime'].idxmin()]
        
        # Find the fastest individual sectors
        fastest_s1_lap = laps_with_times.loc[laps_with_times['Sector1Time'].idxmin()]
        fastest_s2_lap = laps_with_times.loc[laps_with_times['Sector2Time'].idxmin()]
        fastest_s3_lap = laps_with_times.loc[laps_with_times['Sector3Time'].idxmin()]
        
        # Create a dataframe with fastest sector times for each driver
        drivers = laps_with_times['Driver'].unique()
        results = []
        
        for driver in drivers:
            driver_laps = laps_with_times[laps_with_times['Driver'] == driver]
            if driver_laps.empty:
                continue
                
            # Get driver's fastest lap
            fastest_lap = driver_laps.loc[driver_laps['LapTime'].idxmin()]
            
            # Get driver's fastest sectors (may be from different laps)
            fastest_s1 = driver_laps.loc[driver_laps['Sector1Time'].idxmin()]
            fastest_s2 = driver_laps.loc[driver_laps['Sector2Time'].idxmin()]
            fastest_s3 = driver_laps.loc[driver_laps['Sector3Time'].idxmin()]
            
            # Compare with overall fastest sectors
            s1_delta = fastest_s1['Sector1Time'] - fastest_s1_lap['Sector1Time']
            s2_delta = fastest_s2['Sector2Time'] - fastest_s2_lap['Sector2Time']
            s3_delta = fastest_s3['Sector3Time'] - fastest_s3_lap['Sector3Time']
            
            # Prepare result row
            result = {
                'Driver': driver,
                'Team': fastest_lap['Team'] if 'Team' in fastest_lap else 'Unknown',
                'FastestLapNumber': int(fastest_lap['LapNumber']),
                'FastestLapTime': fastest_lap['LapTime'],
                'S1Time': fastest_s1['Sector1Time'],
                'S1Lap': int(fastest_s1['LapNumber']),
                'S2Time': fastest_s2['Sector2Time'],
                'S2Lap': int(fastest_s2['LapNumber']),
                'S3Time': fastest_s3['Sector3Time'],
                'S3Lap': int(fastest_s3['LapNumber']),
                'S1Delta': s1_delta,
                'S2Delta': s2_delta,
                'S3Delta': s3_delta
            }
            results.append(result)
        
        # Convert to DataFrame and sort by fastest lap time
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values('FastestLapTime')
        
        # Also store the fastest sector info
        sector_bests = {
            'S1Best': {'Driver': fastest_s1_lap['Driver'], 'Time': fastest_s1_lap['Sector1Time']},
            'S2Best': {'Driver': fastest_s2_lap['Driver'], 'Time': fastest_s2_lap['Sector2Time']},
            'S3Best': {'Driver': fastest_s3_lap['Driver'], 'Time': fastest_s3_lap['Sector3Time']}
        }
        
        return {
            'driver_data': results_df,
            'sector_bests': sector_bests,
            'fastest_overall': fastest_overall
        }
        
    except Exception as e:
        print(f"Error analyzing sector times: {e}")
        return None

def plot_sector_times_comparison(session):
    """
    Create a visualization of fastest sector times for each driver.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure
    """
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import pandas as pd
    import numpy as np
    from utils import get_driver_color
    
    fig = plt.figure(figsize=(14, 10))
    
    # Analyze sector times
    sector_analysis = analyze_sector_times(session)
    
    # If no data available, return an empty plot with a message
    if not sector_analysis or sector_analysis['driver_data'].empty:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No sector time data available for this session", 
                ha='center', va='center', fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    # Extract data
    driver_data = sector_analysis['driver_data']
    sector_bests = sector_analysis['sector_bests']
    fastest_overall = sector_analysis['fastest_overall']
    
    # Only show top drivers (limit to 10 to keep the chart readable)
    if len(driver_data) > 10:
        driver_data = driver_data.head(10)
    
    # Create Sector Time Comparison Chart
    ax = fig.add_subplot(111)
    
    # Configure the grid
    ax.grid(True, which='major', linestyle='-', linewidth=0.5, color='gray', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Define sector colors
    sector_colors = ['#FF9999', '#99FF99', '#9999FF']
    
    # Create arrays for plotting
    drivers = driver_data['Driver'].values
    s1_times = [t.total_seconds() for t in driver_data['S1Time']]
    s2_times = [t.total_seconds() for t in driver_data['S2Time']]
    s3_times = [t.total_seconds() for t in driver_data['S3Time']]
    
    # Set up positions for the bars
    y_pos = np.arange(len(drivers))
    bar_height = 0.65
    
    # Plot each sector time as stacked bars
    bars1 = ax.barh(y_pos, s1_times, bar_height, color=sector_colors[0], label='Sector 1')
    bars2 = ax.barh(y_pos, s2_times, bar_height, left=s1_times, color=sector_colors[1], label='Sector 2')
    bars3 = ax.barh(y_pos, s3_times, bar_height, left=[s1+s2 for s1, s2 in zip(s1_times, s2_times)], color=sector_colors[2], label='Sector 3')
    
    # Add total lap time at the end of each bar
    for i, (s1, s2, s3) in enumerate(zip(s1_times, s2_times, s3_times)):
        total = s1 + s2 + s3
        minutes = int(total // 60)
        seconds = total % 60
        time_str = f"{minutes}:{seconds:.3f}"
        ax.text(total + 0.1, i, time_str, va='center', fontsize=9)
    
    # Add sector best indicators
    for i, driver in enumerate(drivers):
        s1_best = driver == sector_bests['S1Best']['Driver']
        s2_best = driver == sector_bests['S2Best']['Driver']
        s3_best = driver == sector_bests['S3Best']['Driver']
        
        if s1_best:
            ax.text(s1_times[i]/2, i, '★', ha='center', va='center', color='black', fontsize=12, fontweight='bold')
        if s2_best:
            ax.text(s1_times[i] + s2_times[i]/2, i, '★', ha='center', va='center', color='black', fontsize=12, fontweight='bold')
        if s3_best:
            ax.text(s1_times[i] + s2_times[i] + s3_times[i]/2, i, '★', ha='center', va='center', color='black', fontsize=12, fontweight='bold')
    
    # Customize axis and labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(drivers)
    ax.invert_yaxis()  # To have the fastest driver at the top
    
    # Format x-axis as time
    def format_seconds_as_time(seconds, pos):
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:.3f}"
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_seconds_as_time))
    
    # Add title and labels
    ax.set_title('Fastest Sector Times by Driver', fontsize=16)
    ax.set_xlabel('Time (MM:SS.sss)', fontsize=12)
    ax.set_ylabel('Driver', fontsize=12)
    
    # Add legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    
    # Add a note about the star markers
    ax.text(0.01, -0.07, '★ indicates fastest sector time', transform=ax.transAxes, fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def analyze_driver_tyre_stints(session, driver):
    """
    Create a detailed analysis of a driver's tyre stints including compound, lap range, and tyre life.
    
    Args:
        session: FastF1 session object
        driver: Driver identifier (abbreviation)
    
    Returns:
        Dictionary containing stint information or None if data not available
    """
    # Check if session has lap data
    if session.laps is None or session.laps.empty:
        return None
    
    try:
        # Get lap data for the specific driver
        laps_driver = session.laps.pick_drivers(driver)
        
        if laps_driver.empty:
            return None
        
        # Convert Stint to numeric, handling errors
        laps_driver.loc[:, 'Stint'] = pd.to_numeric(laps_driver['Stint'], errors='coerce')
        
        # Filter relevant columns and drop rows without stint information
        driver_stints = laps_driver[['Stint', 'Compound', 'LapNumber', 'TyreLife']].dropna(subset=['Stint'])
        
        if driver_stints.empty:
            return None
        
        # Group by stint number
        stints = driver_stints.groupby('Stint')
        
        # Prepare result data
        result = {
            'driver': driver,
            'team': laps_driver['Team'].iloc[0] if 'Team' in laps_driver.columns else 'Unknown',
            'stints': []
        }
        
        # Analyze each stint
        for stint_num, stint_data in stints:
            compound = stint_data['Compound'].iloc[0]
            start_lap = int(stint_data['LapNumber'].min())
            end_lap = int(stint_data['LapNumber'].max())
            length = (end_lap - start_lap) + 1
            
            # Tyre life may be NaN in some cases
            start_tyre_life = stint_data['TyreLife'].min()
            end_tyre_life = stint_data['TyreLife'].max()
            
            start_tyre_life_int = int(start_tyre_life) if pd.notna(start_tyre_life) else 'N/A'
            end_tyre_life_int = int(end_tyre_life) if pd.notna(end_tyre_life) else 'N/A'
            
            # Add to results
            result['stints'].append({
                'stint_number': int(stint_num) if pd.notna(stint_num) else 'N/A',
                'compound': compound,
                'start_lap': start_lap,
                'end_lap': end_lap,
                'length': length,
                'start_tyre_life': start_tyre_life_int,
                'end_tyre_life': end_tyre_life_int
            })
        
        return result
    except Exception as e:
        print(f"Error analyzing tyre stints for {driver}: {e}")
        return None

def convert_timedeltas_to_timestamps(weather_data):
    """
    Convert timedelta values in the Time column to datetime timestamps to make them plottable.
    
    Args:
        weather_data: The weather data DataFrame with a Time column containing timedeltas
    
    Returns:
        DataFrame with Time column converted to datetime timestamps
    """
    import pandas as pd
    import numpy as np
    import streamlit as st
    from datetime import datetime, timedelta
    
    # Make a copy to avoid modifying the original
    data = weather_data.copy()
    
    # Debug information
    print(f"Time column type: {type(data['Time'].iloc[0])}")
    print(f"Time column dtype: {data['Time'].dtype}")
    print(f"First time value: {data['Time'].iloc[0]}")
    
    # Check if Time column exists and convert to a plottable format
    if 'Time' in data.columns:
        try:
            # If it's already a timestamp or datetime, leave it alone
            if pd.api.types.is_datetime64_dtype(data['Time']) or isinstance(data['Time'].iloc[0], datetime):
                print("Time column is already in datetime format")
                return data
                
            # For timedelta format (most likely scenario)
            base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Handle different types of time objects
            if pd.api.types.is_timedelta64_dtype(data['Time']):
                print("Converting from timedelta64")
                data['Time'] = base_time + pd.to_timedelta(data['Time'])
            elif isinstance(data['Time'].iloc[0], timedelta):
                print("Converting from Python timedelta")
                data['Time'] = [base_time + td for td in data['Time']]
            else:
                # Try to handle strings or other formats
                print(f"Attempting to convert unknown format: {data['Time'].iloc[0]}")
                # First convert to seconds elapsed if possible
                try:
                    # For string format "HH:MM:SS.sss"
                    if isinstance(data['Time'].iloc[0], str) and ':' in data['Time'].iloc[0]:
                        data['TimeSec'] = data['Time'].apply(lambda x: 
                            sum(float(i) * 60**idx for idx, i in enumerate(reversed(x.split(':'))))) 
                        data['Time'] = base_time + pd.to_timedelta(data['TimeSec'], unit='s')
                    # For numeric format (assumed to be seconds)
                    elif pd.api.types.is_numeric_dtype(data['Time']):
                        data['Time'] = base_time + pd.to_timedelta(data['Time'], unit='s')
                except Exception as e:
                    print(f"Error converting time format: {e}")
                    st.error(f"Unable to process time data: {e}")
            
            print(f"Converted time column type: {type(data['Time'].iloc[0])}")
            print(f"Converted time sample: {data['Time'].iloc[0]}")
            return data
            
        except Exception as e:
            print(f"Error in time conversion: {e}")
            st.error(f"Time conversion error: {e}")
            return data
    
    return data

def plot_weather_data(session):
    """
    Create a visualization of weather data including air/track temperature and rainfall.
    This uses a simpler direct indexing approach for plotting instead of time-based x-axis.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure or None if weather data not available
    """
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
    import pandas as pd
    import streamlit as st
    
    # Debug information
    print("Debugging Weather Data Visualization:")
    
    # Check if session has weather data
    if not hasattr(session, 'weather_data'):
        print("Session has no weather_data attribute")
        return None
    if session.weather_data is None:
        print("Session's weather_data is None")
        return None
    if session.weather_data.empty:
        print("Session's weather_data is empty")
        return None
        
    print(f"Weather data shape: {session.weather_data.shape}")
    print(f"Weather data columns: {session.weather_data.columns.tolist()}")
    
    # Get the weather data - we'll use a simple approach with index as x-axis
    weather_data = session.weather_data.copy()
    
    try:
        # Create the visualization
        print("Creating weather plot with simpler approach...")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Generate x-axis indices evenly spaced
        x_indices = np.arange(len(weather_data))
        
        # Plot air and track temperature against indices
        ax.plot(x_indices, weather_data['AirTemp'], 
                label='Air Temp (°C)', color='red', marker='.', linestyle='-')
        ax.plot(x_indices, weather_data['TrackTemp'], 
                label='Track Temp (°C)', color='blue', marker='.', linestyle='-')
        print("Temperature lines added to plot")
        
        # If there is rainfall data, overlay it on a secondary axis
        if 'Rainfall' in weather_data.columns and weather_data['Rainfall'].max() > 0:
            ax2 = ax.twinx()
            # Plot rainfall against indices
            ax2.bar(x_indices, weather_data['Rainfall'], 
                    label='Rainfall', color='lightblue', alpha=0.6, width=0.8)
            ax2.set_ylabel("Rainfall (mm or boolean)")
            ax2.legend(loc='upper right')
            print("Rainfall data added to plot")
        
        # Custom x-tick formatter to show session time progression
        def format_time_ticks(x, pos):
            if x < 0 or x >= len(weather_data):
                return ''
            # Get the timedelta at this index and format it as MM:SS
            td = weather_data['Time'].iloc[int(x)]
            # Extract minutes and seconds - handle both timedelta and raw seconds
            try:
                if hasattr(td, 'total_seconds'):
                    total_seconds = td.total_seconds()
                else:
                    total_seconds = float(td)
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                return f"{minutes:02d}:{seconds:02d}"
            except:
                return str(x)
                
        # Set up x-ticks at reasonable intervals
        num_ticks = min(10, len(weather_data))
        step = max(1, len(weather_data) // num_ticks)
        tick_positions = np.arange(0, len(weather_data), step)
        ax.set_xticks(tick_positions)
        
        # Apply the formatter
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_time_ticks))
        
        # Customize the plot
        ax.set_xlabel("Session Time (MM:SS)")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title(f"Weather Conditions - {session.event['EventName']} {session.event.year}")
        ax.legend(loc='upper left')
        ax.grid(True)
        print("Plot formatting completed")
        
        # Finalize plot
        plt.tight_layout()
        print("Plot created successfully")
        
        return fig
        
    except Exception as e:
        print(f"Error in plot_weather_data: {e}")
        st.error(f"Error creating weather plot: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_humidity_data(session):
    """
    Create a visualization of humidity data during the session.
    This uses a simpler direct indexing approach for plotting instead of time-based x-axis.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure or None if humidity data not available
    """
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
    import streamlit as st
    
    # Check if session has weather data with humidity
    if not hasattr(session, 'weather_data') or session.weather_data is None or session.weather_data.empty:
        print("No valid weather data found for humidity plot")
        return None
        
    weather_data = session.weather_data.copy()
    
    # Check if humidity data is available
    if 'Humidity' not in weather_data.columns:
        print("Humidity column not found in weather data")
        return None
        
    try:
        # Create the visualization
        print("Creating humidity plot...")
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Generate x-axis indices evenly spaced
        x_indices = np.arange(len(weather_data))
        
        # Plot humidity
        ax.plot(x_indices, weather_data['Humidity'],
                label='Humidity (%)', color='green', marker='.', linestyle='-')
        print("Humidity data added to plot")
        
        # Custom x-tick formatter to show session time progression
        def format_time_ticks(x, pos):
            if x < 0 or x >= len(weather_data):
                return ''
            # Get the timedelta at this index and format it as MM:SS
            td = weather_data['Time'].iloc[int(x)]
            # Extract minutes and seconds - handle both timedelta and raw seconds
            try:
                if hasattr(td, 'total_seconds'):
                    total_seconds = td.total_seconds()
                else:
                    total_seconds = float(td)
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                return f"{minutes:02d}:{seconds:02d}"
            except:
                return str(x)
                
        # Set up x-ticks at reasonable intervals
        num_ticks = min(10, len(weather_data))
        step = max(1, len(weather_data) // num_ticks)
        tick_positions = np.arange(0, len(weather_data), step)
        ax.set_xticks(tick_positions)
        
        # Apply the formatter
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_time_ticks))
        
        # Customize the plot
        ax.set_xlabel("Session Time (MM:SS)")
        ax.set_ylabel("Humidity (%)")
        ax.set_title(f"Humidity Conditions - {session.event['EventName']} {session.event.year}")
        ax.grid(True)
        print("Humidity plot formatting completed")
        
        # Finalize plot
        plt.tight_layout()
        print("Humidity plot created successfully")
        
        return fig
        
    except Exception as e:
        print(f"Error in plot_humidity_data: {e}")
        st.error(f"Error creating humidity plot: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_wind_data(session):
    """
    Create a visualization of wind data during the session.
    This uses a simpler direct indexing approach for plotting instead of time-based x-axis.
    
    Args:
        session: FastF1 session object
    
    Returns:
        Matplotlib figure or None if wind data not available
    """
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import numpy as np
    import streamlit as st
    
    # Check if session has weather data with wind information
    if not hasattr(session, 'weather_data') or session.weather_data is None or session.weather_data.empty:
        print("No valid weather data found for wind plot")
        return None
        
    weather_data = session.weather_data.copy()
    
    # Check if wind data is available
    if 'WindSpeed' not in weather_data.columns or 'WindDirection' not in weather_data.columns:
        print("Wind data columns not found in weather data")
        return None
    
    try:
        # Create the visualization
        print("Creating wind plot...")
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Generate x-axis indices evenly spaced
        x_indices = np.arange(len(weather_data))
        
        # Plot wind speed
        ax.plot(x_indices, weather_data['WindSpeed'],
                label='Wind Speed (km/h)', color='purple', marker='.', linestyle='-')
        print("Wind speed data added to plot")
        
        # Custom x-tick formatter to show session time progression
        def format_time_ticks(x, pos):
            if x < 0 or x >= len(weather_data):
                return ''
            # Get the timedelta at this index and format it as MM:SS
            td = weather_data['Time'].iloc[int(x)]
            # Extract minutes and seconds - handle both timedelta and raw seconds
            try:
                if hasattr(td, 'total_seconds'):
                    total_seconds = td.total_seconds()
                else:
                    total_seconds = float(td)
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                return f"{minutes:02d}:{seconds:02d}"
            except:
                return str(x)
                
        # Set up x-ticks at reasonable intervals
        num_ticks = min(10, len(weather_data))
        step = max(1, len(weather_data) // num_ticks)
        tick_positions = np.arange(0, len(weather_data), step)
        ax.set_xticks(tick_positions)
        
        # Apply the formatter
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_time_ticks))
        
        # Customize the plot
        ax.set_xlabel("Session Time (MM:SS)")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_title(f"Wind Conditions - {session.event['EventName']} {session.event.year}")
        ax.grid(True)
        print("Wind plot formatting completed")
        
        # Finalize plot
        plt.tight_layout()
        print("Wind plot created successfully")
        
        return fig
        
    except Exception as e:
        print(f"Error in plot_wind_data: {e}")
        st.error(f"Error creating wind plot: {e}")
        import traceback
        traceback.print_exc()
        return None


def plot_top_speed_heatmap(session, lap_number=None, driver=None):
    """
    Create a heatmap visualization of top speeds across the track.
    
    Args:
        session: FastF1 session object
        lap_number: Optional specific lap number to analyze
        driver: Optional driver identifier to focus on a single driver
    
    Returns:
        Matplotlib figure
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig = plt.figure(figsize=(14, 10))
    
    # If no data available, return an empty plot with a message
    if session.laps.empty:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No lap data available for this session", 
                ha='center', va='center', fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    # If driver is specified, filter to just that driver
    if driver:
        laps_data = session.laps.pick_drivers(driver)
        title_prefix = f"{driver}'s "
    else:
        laps_data = session.laps
        title_prefix = "All Drivers' "
    
    # If specific lap is requested, filter to just that lap
    if lap_number is not None:
        laps_data = laps_data[laps_data['LapNumber'] == lap_number]
        if laps_data.empty:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"No data available for lap {lap_number}", 
                    ha='center', va='center', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
    
    # Get a representative lap to plot the track shape
    # Either use a specified driver/lap or find one with good data
    track_data = None
    
    try:
        # If we have a specific lap, use it
        if not laps_data.empty:
            lap = laps_data.iloc[0]
            tel = lap.get_telemetry()
            
            if not tel.empty and 'X' in tel.columns and 'Y' in tel.columns:
                # Good data found
                track_data = tel
        
        # If no track data found yet, look for any lap with good data
        if track_data is None or track_data.empty:
            for idx, lap in session.laps.iterrows():
                tel = lap.get_telemetry()
                if not tel.empty and 'X' in tel.columns and 'Y' in tel.columns:
                    track_data = tel
                    break
        
        # If still no track data, return empty plot
        if track_data is None or track_data.empty:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No telemetry data available for track mapping", 
                    ha='center', va='center', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        # Set up the plot
        ax = fig.add_subplot(111)
        
        # Create bins for the track map to aggregate speed data
        # First, create a simplified track path by downsampling to avoid too many points
        downsample_factor = max(1, len(track_data) // 500)  # Aim for ~500 points
        track_simple = track_data.iloc[::downsample_factor].copy()
        
        # Track outline
        ax.plot(track_data['X'], track_data['Y'], color='black', linewidth=2, alpha=0.6)
        
        # For creating a heatmap, we'll aggregate speed data across the track
        # Create a grid over the track area
        min_x, max_x = track_data['X'].min(), track_data['X'].max()
        min_y, max_y = track_data['Y'].min(), track_data['Y'].max()
        
        # Add some padding to the track area
        padding = 0.05  # 5% padding
        x_pad = (max_x - min_x) * padding
        y_pad = (max_y - min_y) * padding
        min_x -= x_pad
        max_x += x_pad
        min_y -= y_pad
        max_y += y_pad
        
        # Create a 2D histogram grid to hold speed data
        grid_resolution = 100
        speed_grid = np.zeros((grid_resolution, grid_resolution))
        count_grid = np.zeros((grid_resolution, grid_resolution))  # To track points per cell
        
        # Collect speed data from all laps or specific laps based on filters
        for _, lap in laps_data.iterrows():
            try:
                tel = lap.get_telemetry()
                if tel.empty or 'Speed' not in tel.columns:
                    continue
                    
                # Bin the telemetry data into the grid
                for _, point in tel.iterrows():
                    if np.isnan(point['X']) or np.isnan(point['Y']) or np.isnan(point['Speed']):
                        continue
                        
                    # Calculate grid cell coordinates
                    grid_x = int((point['X'] - min_x) / (max_x - min_x) * (grid_resolution-1))
                    grid_y = int((point['Y'] - min_y) / (max_y - min_y) * (grid_resolution-1))
                    
                    # Ensure within bounds
                    if 0 <= grid_x < grid_resolution and 0 <= grid_y < grid_resolution:
                        # Update the grid - use max speed at each point
                        if speed_grid[grid_y, grid_x] < point['Speed']:
                            speed_grid[grid_y, grid_x] = point['Speed']
                        count_grid[grid_y, grid_x] += 1
            except Exception as e:
                # Skip laps with errors
                continue
        
        # Only show grid cells with data
        mask = count_grid > 0
        
        # Create x and y values for the grid
        x_vals = np.linspace(min_x, max_x, grid_resolution)
        y_vals = np.linspace(min_y, max_y, grid_resolution)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        # Create a custom colormap from blue (low speed) to red (high speed)
        cmap = plt.cm.get_cmap('viridis')
        
        # Plot the heatmap over the track
        sc = ax.pcolormesh(X, Y, np.ma.masked_where(~mask, speed_grid), 
                           cmap=cmap, alpha=0.7, shading='auto')
        
        # Mark start/finish line
        ax.scatter(track_data['X'].iloc[0], track_data['Y'].iloc[0], 
                   color='red', s=100, zorder=5, label='Start/Finish')
        
        # Add colorbar
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label('Speed (km/h)', fontsize=12)
        
        # Set plot title and labels
        title = f"{title_prefix}Top Speeds Across the Track"
        if lap_number:
            title += f" - Lap {lap_number}"
        ax.set_title(title, fontsize=16)
        
        # Format the plot
        ax.set_aspect('equal')
        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.grid(False)
        ax.legend(loc='best')
        
        # Tight layout for better spacing
        plt.tight_layout()
    
    except Exception as e:
        # Create an error plot if visualization failed
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, f"Error creating heatmap: {str(e)}", 
                ha='center', va='center', fontsize=14)
        ax.set_xticks([])
        ax.set_yticks([])
    
    return fig

def plot_dhl_fastest_lap(session):
    """
    Create a visualization for the DHL Fastest Lap Award.
    
    Args:
        session: FastF1 session object for a race
        
    Returns:
        Matplotlib figure
    """
    if not hasattr(session, 'laps') or session.laps is None or len(session.laps) == 0:
        # Create a message figure if no data is available
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No lap data available for DHL Fastest Lap Award", 
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig
    
    # Find the fastest lap in the race
    try:
        fastest_lap = session.laps.pick_fastest()
        if fastest_lap.empty:
            raise ValueError("No valid fastest lap found")
        
        driver_code = fastest_lap['Driver']
        driver_name = session.get_driver(driver_code)['FullName'] if hasattr(session, 'get_driver') else driver_code
        team_name = fastest_lap['Team'] if 'Team' in fastest_lap else "Unknown Team"
        lap_number = int(fastest_lap['LapNumber'])
        lap_time = fastest_lap['LapTime'].total_seconds()
        lap_time_str = f"{lap_time:.3f}s"
        lap_time_formatted = f"{int(lap_time // 60):01d}:{lap_time % 60:06.3f}"
        
        # Get telemetry for the fastest lap if available
        try:
            telemetry = fastest_lap.get_telemetry()
            max_speed = telemetry['Speed'].max() if 'Speed' in telemetry else None
            avg_speed = telemetry['Speed'].mean() if 'Speed' in telemetry else None
        except:
            telemetry = None
            max_speed = None
            avg_speed = None
        
        # Create figure with 2 rows: top for award info, bottom for speed trace
        fig = plt.figure(figsize=(12, 10))
        gs = GridSpec(2, 3, height_ratios=[1, 2], figure=fig)
        
        # Top panel - DHL Fastest Lap Award information
        ax_info = fig.add_subplot(gs[0, :])
        
        # Set background color
        ax_info.set_facecolor('#f8f8f8')
        
        # Add DHL branding
        ax_info.text(0.5, 0.9, "DHL FASTEST LAP AWARD", 
                    ha='center', va='center', fontsize=24, fontweight='bold',
                    color='#fc0')
        
        # Add driver info
        driver_color = get_driver_color(driver_code, team_name)
        ax_info.text(0.5, 0.7, f"{driver_name}", 
                    ha='center', va='center', fontsize=20, fontweight='bold',
                    color=driver_color)
        ax_info.text(0.5, 0.6, f"{team_name}", 
                    ha='center', va='center', fontsize=16,
                    color=driver_color)
        
        # Add lap time info
        ax_info.text(0.5, 0.4, f"LAP {lap_number} - {lap_time_formatted}", 
                    ha='center', va='center', fontsize=18, fontweight='bold')
        
        # Add speed info if available
        if max_speed is not None:
            ax_info.text(0.25, 0.2, f"MAX SPEED\n{max_speed:.1f} km/h", 
                        ha='center', va='center', fontsize=14)
        if avg_speed is not None:
            ax_info.text(0.75, 0.2, f"AVG SPEED\n{avg_speed:.1f} km/h", 
                        ha='center', va='center', fontsize=14)
        
        ax_info.set_xlim(0, 1)
        ax_info.set_ylim(0, 1)
        ax_info.set_axis_off()
        
        # Bottom panels for visualization
        if telemetry is not None and not telemetry.empty:
            # Speed trace
            ax_speed = fig.add_subplot(gs[1, 0:2])
            
            # Only create speed trace if we have distance and speed data
            if 'Distance' in telemetry and 'Speed' in telemetry:
                x = telemetry['Distance']
                y = telemetry['Speed']
                
                # Plot the speed trace
                ax_speed.plot(x, y, color=driver_color, linewidth=2)
                
                # Add sectors if available
                if 'Sector' in telemetry:
                    sectors = telemetry['Sector'].unique()
                    sector_colors = ['#ff9999', '#99ff99', '#9999ff']  # Red, Green, Blue
                    
                    for i, sector in enumerate(sorted(sectors)):
                        if i < len(sector_colors):  # Make sure we have enough colors
                            sector_data = telemetry[telemetry['Sector'] == sector]
                            if len(sector_data) > 0:
                                start_x = sector_data['Distance'].iloc[0]
                                end_x = sector_data['Distance'].iloc[-1]
                                ax_speed.axvspan(start_x, end_x, color=sector_colors[i], alpha=0.1)
                                ax_speed.text((start_x + end_x)/2, max(y) * 0.9, f"Sector {sector}",
                                             ha='center', fontsize=10)
                
                # Formatting
                ax_speed.set_xlabel('Distance (m)')
                ax_speed.set_ylabel('Speed (km/h)')
                ax_speed.set_title('Speed Trace of Fastest Lap')
                ax_speed.grid(True, alpha=0.3)
            
            # Gear shifts or acceleration/braking traces
            ax_gear = fig.add_subplot(gs[1, 2])
            
            # Check if we have gear data
            if 'nGear' in telemetry:
                # Plot the gear shifts
                if 'Distance' in telemetry:
                    ax_gear.scatter(telemetry['Distance'], telemetry['nGear'], 
                                  c=telemetry['nGear'], cmap='viridis', 
                                  s=10, alpha=0.7)
                    ax_gear.set_xlabel('Distance (m)')
                    ax_gear.set_ylabel('Gear')
                    ax_gear.set_title('Gear Shifts During Fastest Lap')
                    ax_gear.set_yticks(range(1, 9))
                    ax_gear.grid(True, alpha=0.3)
            elif 'Throttle' in telemetry and 'Brake' in telemetry:
                # Plot throttle and brake instead
                if 'Distance' in telemetry:
                    ax_gear.plot(telemetry['Distance'], telemetry['Throttle'], 
                               label='Throttle', color='green', linewidth=1.5)
                    ax_gear.plot(telemetry['Distance'], telemetry['Brake']*100, 
                               label='Brake', color='red', linewidth=1.5)
                    ax_gear.set_xlabel('Distance (m)')
                    ax_gear.set_ylabel('Percentage')
                    ax_gear.set_title('Throttle/Brake Application')
                    ax_gear.legend()
                    ax_gear.grid(True, alpha=0.3)
        else:
            # If no telemetry, create a message
            ax_msg = fig.add_subplot(gs[1, :])
            ax_msg.text(0.5, 0.5, "Detailed telemetry data not available for the fastest lap", 
                       ha='center', va='center', fontsize=14)
            ax_msg.set_axis_off()
        
        plt.tight_layout()
        return fig
    
    except Exception as e:
        # Create an error figure
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"Error creating DHL Fastest Lap Award: {str(e)}", 
               ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig