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
        laps_data = session.laps.pick_driver(driver)
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
        cbar = plt.colorbar(sc, ax=ax, pad=0.02)
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