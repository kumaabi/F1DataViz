import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from utils import get_driver_color

def plot_driver_championship_standings(standings_df):
    """
    Create a bar chart visualization of driver championship standings.
    
    Args:
        standings_df: DataFrame containing driver standings
        
    Returns:
        Matplotlib figure
    """
    if standings_df.empty:
        # Create a figure with a message when no data is available
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No driver championship data available", 
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig
    
    # Sort by position
    standings_df = standings_df.sort_values('Position')
    
    # Get top 20 drivers
    if len(standings_df) > 20:
        standings_df = standings_df.head(20)
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Define x positions and width for the bars
    positions = np.arange(len(standings_df))
    width = 0.8
    
    # Create the bars
    for i, (_, row) in enumerate(standings_df.iterrows()):
        driver_code = row['DriverCode']
        team = row['Team']
        points = row['Points']
        
        # Get color for the driver/team
        color = get_driver_color(driver_code, team)
        
        # Create bar with driver color
        bar = ax.bar(positions[i], points, width, color=color, 
                   label=f"{row['Driver']} ({driver_code})")
        
        # Add driver code and points on top of the bar
        ax.text(positions[i], points + 2, f"{driver_code}\n{points}", 
                ha='center', va='bottom', fontsize=9)
    
    # Add wins indicator for drivers with wins
    for i, (_, row) in enumerate(standings_df.iterrows()):
        if row['Wins'] > 0:
            ax.text(positions[i], row['Points'] * 0.5, 
                    f"{row['Wins']}\nWIN{'' if row['Wins']==1 else 'S'}", 
                    ha='center', va='center', fontsize=8, 
                    color='white', fontweight='bold')
    
    # Set labels and title
    ax.set_title("Driver Championship Standings", fontsize=14)
    ax.set_ylabel("Points", fontsize=12)
    
    # Add horizontal grid lines but keep them light
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    
    # Remove x axis ticks and use driver positions as labels
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{pos}." for pos in standings_df['Position']])
    
    # Remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_constructor_championship_standings(standings_df):
    """
    Create a bar chart visualization of constructor (team) championship standings.
    
    Args:
        standings_df: DataFrame containing constructor standings
        
    Returns:
        Matplotlib figure
    """
    if standings_df.empty:
        # Create a figure with a message when no data is available
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No constructor championship data available", 
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig
    
    # Sort by position
    standings_df = standings_df.sort_values('Position')
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Define x positions and width for the bars
    positions = np.arange(len(standings_df))
    width = 0.8
    
    # Team colors mapping (simplified)
    team_colors = {
        'Red Bull': '#0600EF',
        'Mercedes': '#00D2BE',
        'Ferrari': '#DC0000',
        'McLaren': '#FF8700',
        'Aston Martin': '#006F62',
        'Alpine': '#0090FF',
        'Williams': '#005AFF',
        'AlphaTauri': '#2B4562',
        'Sauber': '#900000',
        'Haas F1 Team': '#FFFFFF',
        'Racing Point': '#F596C8',
        'Renault': '#FFF500',
        'Alfa Romeo': '#900000',
        'Toro Rosso': '#469BFF',
        'Force India': '#F596C8',
        'Lotus F1': '#FFB800',
        'Marussia': '#6E0000',
        'Caterham': '#048646'
    }
    
    # Create the bars
    for i, (_, row) in enumerate(standings_df.iterrows()):
        team = row['Team']
        points = row['Points']
        
        # Get color for the team or use a default color
        color = team_colors.get(team, '#CCCCCC')
        
        # Create bar with team color
        bar = ax.bar(positions[i], points, width, color=color, 
                   label=team)
        
        # Add team name and points on top of the bar
        ax.text(positions[i], points + max(standings_df['Points']) * 0.02, 
                f"{team}\n{points}", ha='center', va='bottom', fontsize=9)
    
    # Add wins indicator for teams with wins
    for i, (_, row) in enumerate(standings_df.iterrows()):
        if row['Wins'] > 0:
            ax.text(positions[i], row['Points'] * 0.5, 
                    f"{row['Wins']}\nWIN{'' if row['Wins']==1 else 'S'}", 
                    ha='center', va='center', fontsize=8, 
                    color='white', fontweight='bold')
    
    # Set labels and title
    ax.set_title("Constructor Championship Standings", fontsize=14)
    ax.set_ylabel("Points", fontsize=12)
    
    # Add horizontal grid lines but keep them light
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    
    # Remove x axis ticks and use constructor positions as labels
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{pos}." for pos in standings_df['Position']])
    
    # Remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_championship_progression(standings_by_round, championship_type='driver'):
    """
    Create a line chart showing how championship standings evolved across rounds.
    
    Args:
        standings_by_round: Dictionary mapping round numbers to standings DataFrames
        championship_type: 'driver' or 'constructor'
        
    Returns:
        Matplotlib figure
    """
    # Check if we have data
    if not standings_by_round or all(df.empty for df in standings_by_round.values()):
        # Create a figure with a message when no data is available
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"No {championship_type} championship progression data available", 
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig
    
    # Get all unique drivers/constructors across all rounds
    all_entries = set()
    for round_num, df in standings_by_round.items():
        if not df.empty:
            if championship_type == 'driver':
                all_entries.update(df['DriverCode'].tolist())
            else:  # constructor
                all_entries.update(df['Team'].tolist())
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Set up the x-axis to be round numbers
    round_numbers = sorted(standings_by_round.keys())
    
    # Track the points by driver/constructor across rounds
    points_by_entry = {entry: [] for entry in all_entries}
    
    # Fill in the points data
    for round_num in round_numbers:
        df = standings_by_round[round_num]
        if df.empty:
            continue
            
        # For each entry, get their points in this round
        for entry in all_entries:
            if championship_type == 'driver':
                entry_data = df[df['DriverCode'] == entry]
            else:  # constructor
                entry_data = df[df['Team'] == entry]
                
            # If the entry exists in this round, add their points
            if not entry_data.empty:
                points_by_entry[entry].append(float(entry_data['Points'].values[0]))
            else:
                # If the entry doesn't exist in this round, use their previous points
                # or 0 if they have no previous points
                prev_points = points_by_entry[entry][-1] if points_by_entry[entry] else 0
                points_by_entry[entry].append(prev_points)
    
    # Plot the lines
    for entry, points in points_by_entry.items():
        if championship_type == 'driver':
            # Get the team for this driver from the latest round where they appear
            team = None
            for round_num in reversed(round_numbers):
                df = standings_by_round[round_num]
                if not df.empty:
                    entry_data = df[df['DriverCode'] == entry]
                    if not entry_data.empty:
                        team = entry_data['Team'].values[0]
                        break
            
            color = get_driver_color(entry, team)
            label = f"{entry} ({team if team else 'Unknown'})" 
        else:  # constructor
            # Simplified team colors
            team_colors = {
                'Red Bull': '#0600EF',
                'Mercedes': '#00D2BE',
                'Ferrari': '#DC0000',
                'McLaren': '#FF8700',
                'Aston Martin': '#006F62',
                'Alpine': '#0090FF',
                'Williams': '#005AFF',
                'AlphaTauri': '#2B4562',
                'Sauber': '#900000',
                'Haas F1 Team': '#FFFFFF',
                'Racing Point': '#F596C8',
                'Renault': '#FFF500',
                'Alfa Romeo': '#900000',
                'Toro Rosso': '#469BFF',
                'Force India': '#F596C8',
                'Lotus F1': '#FFB800',
                'Marussia': '#6E0000',
                'Caterham': '#048646'
            }
            color = team_colors.get(entry, '#CCCCCC')
            label = entry
        
        # Plot the points progression
        ax.plot(round_numbers[:len(points)], points, marker='o', linestyle='-', 
                color=color, label=label, linewidth=2)
    
    # Add labels and title
    if championship_type == 'driver':
        title = "Driver Championship Points Progression by Round"
    else:
        title = "Constructor Championship Points Progression by Round"
        
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Round", fontsize=12)
    ax.set_ylabel("Points", fontsize=12)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Set xticks to be the round numbers
    ax.set_xticks(round_numbers)
    ax.set_xticklabels([str(r) for r in round_numbers])
    
    # Add legend with multiple columns to accommodate many entries
    legend = ax.legend(loc='upper left', fontsize=9, 
                      ncol=min(3, len(all_entries) // 5 + 1))
    
    # Remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_historical_championship_winners(historical_standings, championship_type='driver'):
    """
    Create a visualization showing championship winners across multiple years.
    
    Args:
        historical_standings: Dictionary mapping years to standings DataFrames
        championship_type: 'driver' or 'constructor'
        
    Returns:
        Matplotlib figure
    """
    # Check if we have data
    if not historical_standings or all(df.empty for df in historical_standings.values()):
        # Create a figure with a message when no data is available
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, f"No historical {championship_type} championship data available", 
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig
    
    # Extract winners for each year
    winners = []
    for year, df in sorted(historical_standings.items()):
        if not df.empty:
            winner_row = df.iloc[0]  # First row is the champion
            
            if championship_type == 'driver':
                winner = {
                    'Year': year,
                    'Name': winner_row['Driver'],
                    'Code': winner_row['DriverCode'],
                    'Team': winner_row['Team'],
                    'Points': winner_row['Points']
                }
            else:  # constructor
                winner = {
                    'Year': year,
                    'Name': winner_row['Team'],
                    'Points': winner_row['Points']
                }
                
            winners.append(winner)
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Define x positions for the bars (years)
    years = [w['Year'] for w in winners]
    positions = np.arange(len(years))
    width = 0.8
    
    # Create the bars
    for i, winner in enumerate(winners):
        # Get color
        if championship_type == 'driver':
            color = get_driver_color(winner['Code'], winner['Team'])
        else:  # constructor
            # Simplified team colors
            team_colors = {
                'Red Bull': '#0600EF',
                'Mercedes': '#00D2BE',
                'Ferrari': '#DC0000',
                'McLaren': '#FF8700',
                'Aston Martin': '#006F62',
                'Alpine': '#0090FF',
                'Williams': '#005AFF',
                'AlphaTauri': '#2B4562',
                'Sauber': '#900000',
                'Haas F1 Team': '#FFFFFF',
                'Racing Point': '#F596C8',
                'Renault': '#FFF500',
                'Alfa Romeo': '#900000',
                'Toro Rosso': '#469BFF',
                'Force India': '#F596C8',
                'Lotus F1': '#FFB800',
                'Marussia': '#6E0000',
                'Caterham': '#048646'
            }
            color = team_colors.get(winner['Name'], '#CCCCCC')
        
        # Create bar with color
        bar = ax.bar(positions[i], winner['Points'], width, color=color)
        
        # Add year and name on top of the bar
        ax.text(positions[i], winner['Points'] * 1.02, 
                f"{winner['Year']}\n{winner['Name']}", 
                ha='center', va='bottom', fontsize=9, rotation=0)
    
    # Set labels and title
    if championship_type == 'driver':
        title = "F1 World Drivers' Champions"
    else:
        title = "F1 World Constructors' Champions"
        
    ax.set_title(title, fontsize=14)
    ax.set_ylabel("Championship Points", fontsize=12)
    
    # Add horizontal grid lines but keep them light
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    
    # Remove x axis ticks
    ax.set_xticks([])
    
    # Remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_points_gap_to_leader(standings_df, championship_type='driver'):
    """
    Create a horizontal bar chart showing the points gap to the championship leader.
    
    Args:
        standings_df: DataFrame containing standings
        championship_type: 'driver' or 'constructor'
        
    Returns:
        Matplotlib figure
    """
    if standings_df.empty:
        # Create a figure with a message when no data is available
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"No {championship_type} standings data available", 
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        return fig
    
    # Sort by position
    standings_df = standings_df.sort_values('Position')
    
    # Get leader's points
    leader_points = standings_df.iloc[0]['Points']
    
    # Calculate points gap for each entry
    standings_df['PointsGap'] = leader_points - standings_df['Points']
    
    # Get top 10 entries
    if len(standings_df) > 10:
        standings_df = standings_df.head(10)
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define y positions for the bars
    positions = np.arange(len(standings_df))
    height = 0.7
    
    # Create the bars
    for i, (_, row) in enumerate(standings_df.iterrows()):
        # Skip leader (gap is 0)
        if i == 0:
            continue
            
        if championship_type == 'driver':
            name = row['DriverCode']
            team = row['Team']
            color = get_driver_color(name, team)
            label = f"{name} ({team})"
        else:  # constructor
            name = row['Team']
            team_colors = {
                'Red Bull': '#0600EF',
                'Mercedes': '#00D2BE',
                'Ferrari': '#DC0000',
                'McLaren': '#FF8700',
                'Aston Martin': '#006F62',
                'Alpine': '#0090FF',
                'Williams': '#005AFF',
                'AlphaTauri': '#2B4562',
                'Sauber': '#900000',
                'Haas F1 Team': '#FFFFFF',
                'Racing Point': '#F596C8',
                'Renault': '#FFF500',
                'Alfa Romeo': '#900000',
                'Toro Rosso': '#469BFF',
                'Force India': '#F596C8',
                'Lotus F1': '#FFB800',
                'Marussia': '#6E0000',
                'Caterham': '#048646'
            }
            color = team_colors.get(name, '#CCCCCC')
            label = name
        
        # Create bar with color
        bar = ax.barh(positions[i], row['PointsGap'], height, color=color, 
                    label=label)
        
        # Add points gap at the end of the bar
        ax.text(row['PointsGap'] + 1, positions[i], 
                f"{row['PointsGap']:.0f} pts", 
                va='center', fontsize=9)
    
    # Add leader at the top with a marker instead of a bar
    if championship_type == 'driver':
        leader_name = standings_df.iloc[0]['DriverCode']
        leader_team = standings_df.iloc[0]['Team']
        leader_color = get_driver_color(leader_name, leader_team)
        leader_label = f"{leader_name} ({leader_team})"
    else:  # constructor
        leader_name = standings_df.iloc[0]['Team']
        team_colors = {
            'Red Bull': '#0600EF',
            'Mercedes': '#00D2BE',
            'Ferrari': '#DC0000',
            'McLaren': '#FF8700',
            'Aston Martin': '#006F62',
            'Alpine': '#0090FF',
            'Williams': '#005AFF',
            'AlphaTauri': '#2B4562',
            'Sauber': '#900000',
            'Haas F1 Team': '#FFFFFF',
            'Racing Point': '#F596C8',
            'Renault': '#FFF500',
            'Alfa Romeo': '#900000',
            'Toro Rosso': '#469BFF',
            'Force India': '#F596C8',
            'Lotus F1': '#FFB800',
            'Marussia': '#6E0000',
            'Caterham': '#048646'
        }
        leader_color = team_colors.get(leader_name, '#CCCCCC')
        leader_label = leader_name
    
    # Add leader marker
    ax.scatter([0], [positions[0]], color=leader_color, s=100, 
              label=f"{leader_label} (LEADER)")
    ax.text(1, positions[0], f"LEADER: {leader_points:.0f} pts", 
            va='center', fontsize=9, fontweight='bold')
    
    # Set labels and title
    if championship_type == 'driver':
        title = "Points Gap to Championship Leader - Drivers"
    else:
        title = "Points Gap to Championship Leader - Constructors"
        
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Points Behind Leader", fontsize=12)
    
    # Set yticks
    ax.set_yticks(positions)
    if championship_type == 'driver':
        ax.set_yticklabels([f"{i+1}. {row['DriverCode']}" for i, (_, row) in enumerate(standings_df.iterrows())])
    else:
        ax.set_yticklabels([f"{i+1}. {row['Team']}" for i, (_, row) in enumerate(standings_df.iterrows())])
    
    # Add vertical grid lines but keep them light
    ax.xaxis.grid(True, linestyle='--', alpha=0.3)
    
    # Remove spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.tight_layout()
    return fig
