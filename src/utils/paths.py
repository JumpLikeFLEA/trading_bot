import os
import sys

def get_resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and for Nuitka/PyInstaller.
    
    Args:
        relative_path (str): The path relative to the root of the project.
        
    Returns:
        str: The absolute path to the resource.
    """
    try:
        # Nuitka/PyInstaller creates a temp folder and stores path in _MEIPASS
        # Or in Nuitka, it can also be handled by the executable path.
        if getattr(sys, 'frozen', False):
            # For bundled executables
            # sys._MEIPASS is common for PyInstaller, Nuitka might use different mechanisms
            # but usually it's easier to use the executable's directory.
            base_path = os.path.dirname(sys.executable)
        else:
            # For development environment
            # Get the directory where this file is located, then go up to the project root
            # Assuming this file is in src/utils/
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            
        return os.path.join(base_path, relative_path)
    except Exception:
        # Fallback to current working directory
        return os.path.abspath(relative_path)

def get_config_path(filename="settings.yaml"):
    """Get the absolute path to a configuration file in the config/ directory."""
    return get_resource_path(os.path.join("config", filename))

def get_log_path(filename="trading_bot.log"):
    """Get the absolute path to a log file in the logs/ directory."""
    return get_resource_path(os.path.join("logs", filename))
