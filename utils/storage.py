import json
import os

# File to store settings
SETTINGS_FILE = "chatdev_settings.json"

def load_settings():
    """
    Load settings from file
    
    Returns:
        dict: Settings dictionary or empty dict if file doesn't exist
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    """
    Save settings to file
    
    Args:
        settings: Dictionary containing settings
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
        return True
    except Exception:
        return False