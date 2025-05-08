#!/bin/bash

# Kill any existing Streamlit processes
pkill -f streamlit

# Try ports in sequence
for port in 8501 8502 8503 8504 8505; do
    echo "Attempting to start Streamlit on port $port..."
    
    # Check if port is available
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo "Port $port is available. Starting Streamlit..."
        source venv/bin/activate && streamlit run app.py --server.port=$port
        exit 0
    else
        echo "Port $port is already in use. Trying next port..."
    fi
done

echo "All ports are in use. Please free up a port and try again."
exit 1 