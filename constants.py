# constants.py

# Application Info
APP_NAME = "Image File Consolidator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "RFID Tags and Services" # <--- Customize this
APP_DESCRIPTION = (
    "A utility to copy image files from multiple source folders "
    "to a single destination folder, renaming them with unique IDs "
    "to prevent filename collisions."
)
ABOUT_TEXT = f"{APP_NAME}\nVersion: {APP_VERSION}\n\n{APP_DESCRIPTION}\n\nDeveloped by: {APP_AUTHOR}"

# UI Text
WINDOW_TITLE = APP_NAME
BTN_ADD_FOLDER = "Add Single Folder..."
BTN_ADD_MULTIPLE_FOLDERS = "Add Multiple Folders..."
BTN_REMOVE_SELECTED = "Remove Selected"
BTN_BROWSE = "Browse"
BTN_START_COPY = "Start Copy"
BTN_CANCEL = "Cancel"
BTN_OPEN_DEST_FOLDER = "Open Destination Folder"
BTN_OPEN_LOG_FILE = "Open Log File"
BTN_CLEAR_LOG = "Clear Log Display"

LBL_SOURCE_FOLDERS = "1. Select Source Folders (Add multiple)"
LBL_DESTINATION_FOLDER = "2. Select Destination Folder"
LBL_SELECTED_SOURCES = "Selected Source Folders:"
LBL_DESTINATION = "Destination:"
LBL_PROCESS_LOG = "Process Log"
LBL_PROGRESS = "Progress: 0/0 files"
LBL_SCANNING = "Scanning files..."

MSG_CONFIRM_COPY_TITLE = "Confirm Copy"
MSG_CONFIRM_CANCEL_TITLE = "Cancel Copy"
MSG_CONFIRM_EXIT_TITLE = "Exit Application"
MSG_FOLDER_ALREADY_ADDED = "Folder already added."
MSG_NO_SOURCE_FOLDERS = "Please select at least one source folder."
MSG_NO_DEST_FOLDER = "Please select a destination folder."
MSG_DEST_FOLDER_NOT_EXIST = "Destination folder not set or does not exist."
MSG_LOG_FILE_NOT_FOUND = "Log file not found."
MSG_PROCESS_COMPLETE = "Process Complete"
MSG_PROCESS_COMPLETE_WITH_ERRORS = "Process Complete with Errors"
MSG_PROCESS_CANCELLED = "Process Cancelled"
MSG_PROCESS_FAILED = "Process Failed"
MSG_SETTINGS_ERROR = "Settings Error"
MSG_SETTINGS_SAVE_ERROR = "Settings Save Error"

STATUS_READY = "Ready."
STATUS_SCANNING = "Scanning files..."
STATUS_COPYING = "Copying files..."
STATUS_COMPLETE = "Process complete!"
STATUS_COMPLETE_ERRORS = "Process complete with errors."
STATUS_CANCELLED = "Process cancelled."
STATUS_FAILED = "Process failed."

# Confirmation Messages
MSG_CONFIRM_REMOVE_FOLDER = "Are you sure you want to remove this folder from the list?"