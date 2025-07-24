# config_manager.py
import json
import os
from logger_setup import logger # Import the configured logger

# Global application constants/configurations
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.ico')
SETTINGS_FILE = "settings.json"

class ConfigManager:
    """Manages loading and saving application settings."""
    def __init__(self):
        self.source_folders = []
        self.destination_folder = ""

    def load_settings(self):
        """Loads last used source/destination paths from settings file."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    
                    loaded_sources = settings.get("source_folders", [])
                    self.source_folders = [
                        os.path.normpath(p) for p in loaded_sources if os.path.isdir(p)
                    ]

                    loaded_dest = settings.get("destination_folder", "")
                    if os.path.isdir(loaded_dest):
                        self.destination_folder = os.path.normpath(loaded_dest)
                    
                    logger.info("Settings loaded successfully.")
                    return True
            except json.JSONDecodeError as e:
                logger.error(f"Error reading {SETTINGS_FILE}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading settings: {e}")
        else:
            logger.info(f"No {SETTINGS_FILE} found. Starting with default paths.")
        return False

    def save_settings(self, source_folders, destination_folder):
        """Saves current source/destination paths to settings file."""
        settings = {
            "source_folders": source_folders,
            "destination_folder": destination_folder
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            logger.info("Settings saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Error saving settings to {SETTINGS_FILE}: {e}")
        return False