"""
Styling utilities for the F1 Data Visualization app.
"""

def get_apple_style_css():
    """
    Return CSS styling for an Apple-inspired look and feel.
    """
    return """
    <style>
    :root {
        --background-color: #f5f5f7;
        --text-color: #1d1d1f;
        --accent-color: #0071e3;
        --accent-color-light: #419eff;
        --border-color: #d2d2d7;
        --success-color: #36b37e;
        --warning-color: #ffab00;
        --error-color: #ff5630;
        --card-background: #ffffff;
        --panel-background: #ffffff;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #1d1d1f;
            --text-color: #f5f5f7;
            --border-color: #424245;
            --card-background: #2d2d2f;
            --panel-background: #2d2d2f;
        }
    }
    
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Improve text readability */
    p, li, div {
        font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.5;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 20px;
        padding: 0.25rem 1rem;
        background-color: var(--accent-color);
        color: white;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-color-light);
        transform: scale(1.02);
    }
    
    /* Sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background-color: var(--card-background);
        border-right: 1px solid var(--border-color);
    }
    
    /* Cards */
    .css-keje6w {
        border-radius: 12px;
        border: 1px solid var(--border-color);
        overflow: hidden;
        background-color: var(--card-background);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .css-keje6w:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Widget labels */
    .css-16huue1 {
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        color: var(--text-color);
    }
    
    /* Improve selectbox styling */
    .stSelectbox {
        margin-bottom: 1rem;
    }
    
    /* Tables */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe th {
        background-color: var(--accent-color);
        color: white;
        padding: 0.5rem;
        text-align: left;
    }
    
    .dataframe td {
        padding: 0.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .dataframe tr:nth-child(even) {
        background-color: rgba(0,0,0,0.03);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 2.5rem;
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }
    </style>
    """

def get_info_box(title, message, icon="ℹ️", style="info"):
    """
    Return HTML for a styled info box.
    
    Args:
        title: Title text
        message: Message text
        icon: Icon to show (emoji)
        style: Style variant (info, warning, error, success)
    
    Returns:
        HTML string
    """
    color_map = {
        "info": "#0071e3",
        "warning": "#ffab00",
        "error": "#ff5630",
        "success": "#36b37e"
    }
    
    color = color_map.get(style, color_map["info"])
    
    return f"""
    <div style="border-left: 5px solid {color}; 
                background-color: var(--card-background); 
                padding: 1rem; 
                margin: 1rem 0; 
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</div>
            <h3 style="margin: 0; font-size: 1.1rem;">{title}</h3>
        </div>
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">{message}</p>
    </div>
    """

def get_metric_card(label, value, icon="", delta=None, units=""):
    """
    Return HTML for a styled metric card.
    
    Args:
        label: Metric label
        value: Metric value
        icon: Icon to show (emoji)
        delta: Change indicator (positive or negative number)
        units: Units to display after the value
    
    Returns:
        HTML string
    """
    delta_html = ""
    if delta is not None:
        delta_color = "#36b37e" if delta >= 0 else "#ff5630"
        delta_sign = "+" if delta > 0 else ""
        delta_html = f"""
        <div style="color: {delta_color}; font-size: 0.8rem; margin-top: 0.25rem;">
            {delta_sign}{delta}{units}
        </div>
        """
    
    return f"""
    <div style="background-color: var(--card-background); 
                padding: 1rem; 
                border-radius: 10px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                text-align: center;
                height: 100%;">
        <div style="font-size: 1rem; opacity: 0.7; margin-bottom: 0.5rem;">{label}</div>
        <div style="display: flex; justify-content: center; align-items: center;">
            {f'<div style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</div>' if icon else ''}
            <div style="font-size: 1.8rem; font-weight: 600;">{value}{units}</div>
        </div>
        {delta_html}
    </div>
    """

def get_header_card(title, subtitle, icon="", bg_color="var(--accent-color)"):
    """
    Return HTML for a styled header card.
    
    Args:
        title: Header title
        subtitle: Header subtitle
        icon: Icon to show (emoji)
        bg_color: Background color
    
    Returns:
        HTML string
    """
    return f"""
    <div style="background-color: {bg_color}; 
                color: white;
                padding: 1.5rem; 
                border-radius: 12px; 
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center;">
            {f'<div style="font-size: 2.5rem; margin-right: 1rem;">{icon}</div>' if icon else ''}
            <div>
                <h2 style="margin: 0; font-size: 1.8rem;">{title}</h2>
                <p style="margin: 0.25rem 0 0 0; opacity: 0.8;">{subtitle}</p>
            </div>
        </div>
    </div>
    """

def get_navigation_menu(options, active_index=0):
    """
    Return HTML for a custom navigation menu.
    
    Args:
        options: List of menu options
        active_index: Index of the active option
    
    Returns:
        HTML string
    """
    buttons_html = ""
    for i, option in enumerate(options):
        is_active = i == active_index
        bg_color = "var(--accent-color)" if is_active else "transparent"
        text_color = "white" if is_active else "var(--text-color)"
        border = "none" if is_active else "1px solid var(--border-color)"
        
        buttons_html += f"""
        <button style="background-color: {bg_color}; 
                       color: {text_color}; 
                       border: {border};
                       padding: 0.5rem 1rem;
                       border-radius: 20px;
                       margin-right: 0.5rem;
                       font-size: 0.9rem;
                       cursor: pointer;">
            {option}
        </button>
        """
    
    return f"""
    <div style="display: flex; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
        {buttons_html}
    </div>
    """ 