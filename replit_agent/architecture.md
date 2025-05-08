# Architecture Documentation

## Overview

This repository contains a Formula 1 data visualization application built using Streamlit. The application leverages the FastF1 Python package to access, analyze, and visualize Formula 1 race data. Users can explore various aspects of F1 races, including lap times, driver comparisons, telemetry data, and track positions through an interactive web interface.

The application is designed to provide both casual F1 fans and data enthusiasts with insights into race performance, strategy, and technical aspects of Formula 1 racing using real-world data.

## System Architecture

The system follows a simple frontend-centric architecture with the following components:

1. **Presentation Layer**: Streamlit-based web interface that renders visualizations and provides interactive controls.
2. **Application Logic**: Python modules that handle data fetching, processing, and visualization generation.
3. **Data Access Layer**: Utilizes FastF1 library to fetch F1 race data from official sources.

The architecture is stateless, with data being fetched and processed on-demand based on user selections. The application relies heavily on FastF1's caching mechanism to avoid redundant API calls and improve performance.

## Key Components

### 1. Streamlit Web Application (`app.py`)

The main entry point serving as the frontend interface. It:
- Provides interactive widgets for selecting races, drivers, and visualization types
- Orchestrates the flow between data fetching and visualization
- Renders the visualization components
- Handles user input and state management

### 2. Data Fetching Module (`f1_data_fetcher.py`)

Responsible for retrieving F1 data:
- Interfaces with FastF1 and Ergast APIs to fetch race data
- Contains hardcoded future races for 2025 (likely for demonstration purposes)
- Handles error conditions when data is unavailable

### 3. Visualization Module (`visualizations.py` and `visualizations_new.py`)

Contains functions that generate different F1 data visualizations:
- Lap time comparisons
- Driver performance analysis
- Telemetry data visualization
- Track position mapping
- Speed traces and heatmaps
- Tire strategy analysis
- And many other specialized F1 visualizations

### 4. Utilities Module (`utils.py`)

Provides helper functions used across the application:
- Session loading and management
- Data transformation and formatting
- Driver color mapping
- Data filtering and selection

## Data Flow

1. **User Input**: The user selects parameters such as race year, event, session type, and drivers through the Streamlit UI.

2. **Data Retrieval**: 
   - The application uses FastF1 to fetch the selected session data.
   - Data is cached locally to improve performance for subsequent requests.

3. **Data Processing**:
   - Raw data from FastF1 is filtered and transformed based on user selections.
   - Specific metrics are calculated for the requested visualization type.

4. **Visualization Generation**:
   - The appropriate visualization function is called with the processed data.
   - Matplotlib figures are generated with the requested visualization.

5. **Rendering**:
   - Streamlit displays the Matplotlib figures in the web interface.
   - Additional UI elements provide context and controls for the visualizations.

## External Dependencies

### Core Libraries
- **Streamlit**: Powers the web interface and interactive elements
- **FastF1**: Provides access to Formula 1 data and telemetry
- **Matplotlib**: Creates data visualizations
- **Pandas**: Handles data manipulation and analysis
- **NumPy**: Supports numerical operations

### External APIs
- **FastF1 API**: The primary source of race data and telemetry
- **Ergast API**: Provides additional Formula 1 statistics and historical data

## Deployment Strategy

The application is configured for deployment using Replit's infrastructure:

1. **Environment Configuration**:
   - Python 3.11 is specified as the runtime.
   - Additional system packages (cairo, ffmpeg, etc.) are specified in the Nix configuration.

2. **Containerization**:
   - The application is deployed in a containerized environment managed by Replit.
   - `.replit` file configures the deployment target as "autoscale".

3. **Web Service**:
   - Streamlit server runs on port 5000 internally.
   - External port is mapped to port 80 for public access.
   - Streamlit is configured to run in headless mode with `.streamlit/config.toml`.

4. **Workflow Automation**:
   - Replit workflows are defined to automate the startup process.
   - The main workflow runs the Streamlit server with proper port configuration.

This deployment strategy allows for efficient resource utilization while providing public access to the application without requiring users to set up the development environment locally.

## Design Considerations and Limitations

### Performance Optimization
- Local caching of FastF1 data is used to improve response times.
- The cache directory structure is visible in the repository.

### Error Handling
- Visualizations include fallback behaviors for missing data.
- Error messages are displayed when data cannot be loaded.

### Future Extensibility
- The modular structure allows for easy addition of new visualization types.
- Separation of data fetching, processing, and visualization concerns supports future enhancements.

### Known Limitations
- Some visualizations may encounter errors with certain data combinations.
- The application is focused on visualization rather than deep analysis or prediction.
- Future race data for 2025 is hardcoded rather than dynamically fetched.