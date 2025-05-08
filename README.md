# F1 Data Visualization

A comprehensive Formula 1 data visualization platform built with Python and Streamlit. This application provides interactive visualizations of F1 race data, telemetry, and performance metrics.

## Features

- **Lap Time Analysis**: Compare lap times across different drivers and sessions
- **Driver Comparison**: Detailed head-to-head performance visualization between drivers
- **Telemetry Data**: View detailed telemetry including speed, throttle, brakes, and gear shifts
- **Track Position**: Track position visualization for all drivers at specific lap numbers
- **Sector Times**: Analysis of sector times with fastest sector indicators
- **Weather Data**: Temperature, rainfall, humidity, and wind condition visualizations
- **Team Pace**: Box plot comparison of team performance
- **Tyre Strategies**: Visualize tyre compound choices and stint lengths
- **Qualifying Analysis**: Detailed Q1/Q2/Q3 performance breakdown

## Technology Stack

- **Python 3.11+**
- **Streamlit** for the web interface
- **FastF1** for accessing Formula 1 data
- **Matplotlib/Pandas/NumPy** for data processing and visualization
- **Ergast API** as a fallback data source

## Installation

```bash
# Clone the repository
git clone https://github.com/kumaabi/F1DataViz.git
cd F1DataViz

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Usage

Select a season, event, and session type using the sidebar. The application will load the data and provide various visualization tabs for analysis. Each tab focuses on a different aspect of the race data.

## License

MIT License
