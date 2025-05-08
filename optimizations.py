"""
Performance optimization utilities for the F1 Data Visualization app.
"""

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import gc
from functools import lru_cache

def enable_performance_optimizations():
    """Apply various performance optimizations for matplotlib and streamlit"""
    # Configure matplotlib to be more efficient
    plt.rcParams['figure.max_open_warning'] = 25  # Increase limit before warning
    plt.rcParams['figure.dpi'] = 100  # Lower DPI for faster rendering
    
    # Initialize session state for caching
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.cached_data = {}
        st.session_state.cached_figures = {}

def display_figure_with_cleanup(fig):
    """
    Display a matplotlib figure in Streamlit and then clean up to free memory.
    
    Args:
        fig: Matplotlib figure object to display
    
    Returns:
        None
    """
    if fig is None:
        st.warning("No figure to display")
        return
        
    # Display the figure
    st.pyplot(fig)
    
    # Close this figure to free memory
    plt.close(fig)
    
    # Every 10 figure displays, force garbage collection
    if not hasattr(display_figure_with_cleanup, "counter"):
        display_figure_with_cleanup.counter = 0
    display_figure_with_cleanup.counter += 1
    
    if display_figure_with_cleanup.counter % 10 == 0:
        close_all_figures()

def close_all_figures():
    """
    Close all open matplotlib figures to free up memory.
    This should be called periodically, especially after
    generating multiple visualizations in Streamlit.
    
    Returns:
        None
    """
    # Close all figures
    plt.close('all')
    
    # Force garbage collection
    gc.collect()
    
    # Print memory usage information when in debug mode
    if hasattr(plt, '_debug') and plt._debug:
        import psutil
        process = psutil.Process()
        print(f"Memory usage after closing figures: {process.memory_info().rss / 1024 / 1024:.2f} MB")

def optimize_dataframe(df):
    """
    Optimize memory usage of a DataFrame by downcasting numeric columns.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Optimized DataFrame
    """
    if df is None or df.empty:
        return df
        
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Iterate through all columns
    for col in result.columns:
        # Skip non-numeric columns
        if result[col].dtype == 'object' or pd.api.types.is_datetime64_dtype(result[col]):
            continue
            
        # Convert integers
        if pd.api.types.is_integer_dtype(result[col]):
            # Get min and max values
            col_min = result[col].min()
            col_max = result[col].max()
            
            # Choose appropriate integer type
            if col_min >= 0:  # Unsigned integer
                if col_max <= 255:
                    result[col] = result[col].astype(np.uint8)
                elif col_max <= 65535:
                    result[col] = result[col].astype(np.uint16)
                elif col_max <= 4294967295:
                    result[col] = result[col].astype(np.uint32)
            else:  # Signed integer
                if col_min >= -128 and col_max <= 127:
                    result[col] = result[col].astype(np.int8)
                elif col_min >= -32768 and col_max <= 32767:
                    result[col] = result[col].astype(np.int16)
                elif col_min >= -2147483648 and col_max <= 2147483647:
                    result[col] = result[col].astype(np.int32)
                    
        # Convert floats
        elif pd.api.types.is_float_dtype(result[col]):
            result[col] = result[col].astype(np.float32)
    
    # Run garbage collection
    gc.collect()
    
    return result

@lru_cache(maxsize=32)
def cached_computation(key, *args):
    """
    A general purpose caching decorator for computational results.
    
    Args:
        key: A unique identifier for the computation
        *args: Arguments that the computation depends on
    
    Returns:
        Cached result if available, otherwise None
    """
    return None  # The actual computation should be done by the caller

def cleanup_memory():
    """Force a garbage collection to free up memory"""
    gc.collect() 