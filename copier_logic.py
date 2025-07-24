# copier_logic.py
import os
import shutil
import uuid
import queue
import threading
from logger_setup import logger, LOG_FILEPATH # <--- CORRECTED: Import LOG_FILEPATH from logger_setup
from config_manager import IMAGE_EXTENSIONS # Correct: Only IMAGE_EXTENSIONS from config_manager

def copy_worker(source_folders, destination_folder, message_queue, cancel_event):
    """
    Worker function to perform image copying in a separate thread.
    Communicates progress and status via a queue.
    """
    def send_message(level, message):
        message_queue.put({'level': level, 'message': message})
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def send_progress(current, total, mode="determinate"): # <--- MODIFIED: Added mode parameter
        message_queue.put({'type': 'progress', 'current': current, 'total': total, 'mode': mode}) # <--- MODIFIED: Send mode

    send_message("info", "--- Starting Image Copy Process ---")
    send_message("info", f"Log file for this session: {LOG_FILEPATH}")

    if not destination_folder:
        send_message("error", "Error: No destination folder selected.")
        message_queue.put({'type': 'finished', 'status': 'error'})
        return

    try:
        destination_folder = os.path.abspath(os.path.normpath(destination_folder))
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            send_message("info", f"Created destination folder: {destination_folder}")
        else:
            send_message("info", f"Using existing destination folder: {destination_folder}")
    except OSError as e:
        send_message("error", f"Error creating/accessing destination folder '{destination_folder}': {e}")
        message_queue.put({'type': 'finished', 'status': 'error'})
        return

    if not source_folders:
        send_message("warning", "Warning: No source folders selected.")
        message_queue.put({'type': 'finished', 'status': 'warning'})
        return

    all_files_to_process = []
    
    # --- NEW: Indicate file enumeration start ---
    send_message("info", "Scanning source folders for image files...")
    send_progress(0, 0, mode="indeterminate") # <--- NEW: Set indeterminate mode for scanning
    # --- END NEW ---

    for folder_path in source_folders:
        if cancel_event.is_set():
            send_message("warning", "Process cancelled during file enumeration.")
            message_queue.put({'type': 'finished', 'status': 'cancelled'})
            return

        try:
            folder_path = os.path.abspath(os.path.normpath(folder_path))
            if not os.path.isdir(folder_path):
                send_message("warning", f"Source folder not found or is not a directory, skipping: {folder_path}")
                continue
            
            # Removed the "Enumerating files in..." message here, as the general "Scanning..." covers it
            for root, _, files in os.walk(folder_path):
                for filename in files:
                    if filename.lower().endswith(IMAGE_EXTENSIONS):
                        all_files_to_process.append(os.path.join(root, filename))
        except PermissionError as e:
            send_message("error", f"Permission denied accessing folder '{folder_path}': {e}")
        except Exception as e:
            send_message("error", f"An unexpected error occurred while enumerating folder '{folder_path}': {e}")
            
    total_files_to_copy = len(all_files_to_process)
    copied_count = 0
    skipped_count = 0
    
    # --- NEW: Indicate enumeration complete and switch to determinate mode ---
    send_message("info", f"Finished scanning. Found {total_files_to_copy} potential image files to copy.")
    send_progress(0, total_files_to_copy, mode="determinate") # <--- NEW: Switch to determinate mode with total
    # --- END NEW ---

    for i, source_path in enumerate(all_files_to_process):
        if cancel_event.is_set():
            send_message("warning", "Process cancelled during file copying.")
            message_queue.put({'type': 'finished', 'status': 'cancelled'})
            return

        send_progress(i + 1, total_files_to_copy) # <--- Keep sending determinate progress

        extension = os.path.splitext(os.path.basename(source_path))[1]
        unique_id = uuid.uuid4().hex
        new_filename = f"{unique_id}{extension}"
        
        destination_path = os.path.join(destination_folder, new_filename)
        
        try:
            shutil.copy2(source_path, destination_path)
            copied_count += 1
            send_message("info", f"  Copied '{os.path.basename(source_path)}' as '{new_filename}'")
        except (shutil.Error, OSError) as e:
            send_message("error", f"  Error copying '{os.path.basename(source_path)}' to '{destination_path}': {e}")
            skipped_count += 1
        except Exception as e:
            send_message("error", f"  An unexpected error occurred while copying '{os.path.basename(source_path)}': {e}")
            skipped_count += 1

    final_status = 'completed' if skipped_count == 0 else 'completed_with_errors'
    send_message("info", "\n--- Finished Image Copy Process ---")
    send_message("info", f"Total files identified: {total_files_to_copy}")
    send_message("info", f"Total image files copied successfully: {copied_count}")
    if skipped_count > 0:
        send_message("warning", f"Total files skipped due to errors: {skipped_count}")

    message_queue.put({'type': 'finished', 'status': final_status, 'copied_count': copied_count, 'skipped_count': skipped_count})