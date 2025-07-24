# app.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, Toplevel, Label
import os
import threading
import queue
import sys
from logger_setup import logger, LOG_FILEPATH
from config_manager import ConfigManager
from copier_logic import copy_worker
from constants import (
    APP_NAME, WINDOW_TITLE, BTN_ADD_FOLDER, BTN_REMOVE_SELECTED,
    BTN_BROWSE, BTN_START_COPY, BTN_CANCEL, BTN_OPEN_DEST_FOLDER,
    BTN_OPEN_LOG_FILE, BTN_CLEAR_LOG, LBL_SOURCE_FOLDERS,
    LBL_DESTINATION_FOLDER, LBL_SELECTED_SOURCES, LBL_DESTINATION,
    LBL_PROCESS_LOG, LBL_PROGRESS, LBL_SCANNING,
    MSG_CONFIRM_COPY_TITLE, MSG_CONFIRM_CANCEL_TITLE, MSG_CONFIRM_EXIT_TITLE,
    MSG_FOLDER_ALREADY_ADDED, MSG_NO_SOURCE_FOLDERS, MSG_NO_DEST_FOLDER,
    MSG_DEST_FOLDER_NOT_EXIST, MSG_LOG_FILE_NOT_FOUND,
    MSG_PROCESS_COMPLETE, MSG_PROCESS_COMPLETE_WITH_ERRORS,
    MSG_PROCESS_CANCELLED, MSG_PROCESS_FAILED, ABOUT_TEXT,
    MSG_SETTINGS_ERROR, MSG_SETTINGS_SAVE_ERROR,
    STATUS_READY, STATUS_SCANNING, STATUS_COPYING, STATUS_COMPLETE,
    STATUS_COMPLETE_ERRORS, STATUS_CANCELLED, STATUS_FAILED,
    MSG_CONFIRM_REMOVE_FOLDER
)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.x = 0
        self.y = 0

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show) # Show after 500ms

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self):
        if self.tooltip_window:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip_window, text=self.text, background="#FFFFEA", relief="solid", borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class ImageCopierApp:
    def __init__(self, master):
        self.master = master
        master.title(WINDOW_TITLE)
        master.geometry("800x650")
        master.resizable(True, True)

        # Platform-specific maximization
        if os.sys.platform == "win32":
            master.state('zoomed')
        elif os.sys.platform == "darwin":
            screen_width = master.winfo_screenwidth()
            screen_height = master.winfo_screenheight()
            master.geometry(f"{screen_width}x{screen_height}+0+0")
        else: # Linux/X11
            master.attributes('-zoomed', True)

        # Optional: Set a consistent application icon
        try:
            # --- MODIFIED FOR PYINSTALLER COMPATIBILITY ---
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running in a PyInstaller bundle: use the temp path for bundled resources
                base_path = sys._MEIPASS
            else:
                # Running as a normal Python script: use the script's directory
                base_path = os.path.dirname(__file__)
            
            icon_path = os.path.join(base_path, 'icon.ico')

            if os.path.exists(icon_path):
                master.iconbitmap(icon_path)
            else:
                logger.warning(f"Application icon not found at: {icon_path}. Ensure it's in the same directory as app.py or bundled correctly.")
        except tk.TclError:
            logger.warning("Could not load application icon. Ensure 'icon.ico' is valid and present.")
        except Exception as e:
            logger.error(f"Error loading application icon: {e}")
            
        self.source_folders = []
        self.destination_folder = ""
        self.current_copy_thread = None
        self.message_queue = queue.Queue()
        self.cancel_event = threading.Event()

        self.config_manager = ConfigManager()

        self._create_widgets()
        self._load_initial_settings()
        self._set_initial_states()
        self._update_status_bar(STATUS_READY)

    def _create_widgets(self):
        # --- Controls Frame ---
        self.controls_frame = tk.Frame(self.master, padx=10, pady=10, bd=2, relief="groove")
        self.controls_frame.pack(side=tk.TOP, fill=tk.X)

        # Source Folders
        self.source_frame = tk.LabelFrame(self.controls_frame, text=LBL_SOURCE_FOLDERS, padx=5, pady=5)
        self.source_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        self.source_frame.columnconfigure(0, weight=1)

        tk.Label(self.source_frame, text=LBL_SELECTED_SOURCES).pack(side=tk.TOP, anchor=tk.W)
        self.source_listbox = tk.Listbox(self.source_frame, height=4, width=80, selectmode=tk.SINGLE)
        self.source_listbox.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5)
        self.source_listbox.bind('<Delete>', self._remove_selected_source_folder)
        self.source_listbox.bind('<BackSpace>', self._remove_selected_source_folder)
        self.source_listbox.bind('<<ListboxSelect>>', self._on_listbox_select) # <--- NEW: Bind selection event

        source_btn_frame = tk.Frame(self.source_frame)
        source_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.add_source_button = tk.Button(source_btn_frame, text=BTN_ADD_FOLDER, command=self._add_source_folder)
        self.add_source_button.pack(side=tk.LEFT, padx=5)
        Tooltip(self.add_source_button, "Add a folder from which to copy image files.")

        self.remove_source_button = tk.Button(source_btn_frame, text=BTN_REMOVE_SELECTED, command=self._remove_selected_source_folder)
        self.remove_source_button.pack(side=tk.LEFT, padx=5)
        Tooltip(self.remove_source_button, "Remove the currently selected source folder from the list.")

        # Destination Folder
        self.dest_frame = tk.LabelFrame(self.controls_frame, text=LBL_DESTINATION_FOLDER, padx=5, pady=5)
        self.dest_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        self.dest_frame.columnconfigure(1, weight=1)

        tk.Label(self.dest_frame, text=LBL_DESTINATION).grid(row=0, column=0, padx=5, sticky="w")
        self.dest_entry = tk.Entry(self.dest_frame, width=60, state="readonly", bd=2, relief=tk.SUNKEN)
        self.dest_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.browse_dest_button = tk.Button(self.dest_frame, text=BTN_BROWSE, command=self._select_destination_folder)
        self.browse_dest_button.grid(row=0, column=2, padx=5)
        Tooltip(self.browse_dest_button, "Browse for and select the folder where images will be copied.")

        # Action Buttons
        self.buttons_frame = tk.Frame(self.controls_frame, padx=5, pady=5)
        self.buttons_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.start_button = tk.Button(self.buttons_frame, text=BTN_START_COPY, command=self._start_copy_process,
                                      font=("Helvetica", 10, "bold"), bg="lightblue")
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        Tooltip(self.start_button, "Start the process of copying images from source(s) to destination.")

        self.cancel_button = tk.Button(self.buttons_frame, text=BTN_CANCEL, command=self._cancel_copy_process,
                                       font=("Helvetica", 10), bg="lightcoral", state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=10, pady=5)
        Tooltip(self.cancel_button, "Cancel the ongoing image copying process.")

        self.open_dest_button = tk.Button(self.buttons_frame, text=BTN_OPEN_DEST_FOLDER, command=self._open_destination_folder, state=tk.DISABLED)
        self.open_dest_button.pack(side=tk.LEFT, padx=10, pady=5)
        Tooltip(self.open_dest_button, "Open the selected destination folder in your file explorer.")

        self.open_log_button = tk.Button(self.buttons_frame, text=BTN_OPEN_LOG_FILE, command=self._open_log_file)
        self.open_log_button.pack(side=tk.LEFT, padx=10, pady=5)
        Tooltip(self.open_log_button, "Open the current session's log file.")

        self.about_button = tk.Button(self.buttons_frame, text="About", command=self._show_about_dialog)
        self.about_button.pack(side=tk.LEFT, padx=10, pady=5)
        Tooltip(self.about_button, "Show information about this application.")

        # Progress Bar
        self.progress_frame = tk.Frame(self.controls_frame, padx=5, pady=5)
        self.progress_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.progress_label = tk.Label(self.progress_frame, text=LBL_PROGRESS)
        self.progress_label.pack(side=tk.TOP, anchor=tk.W)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(side=tk.TOP, fill=tk.X, expand=True)

        # Log Output
        self.log_frame = tk.LabelFrame(self.master, text=LBL_PROCESS_LOG, padx=10, pady=5)
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.output_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, height=15, width=80, state=tk.DISABLED, font=("Consolas", 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.clear_log_button = tk.Button(self.log_frame, text=BTN_CLEAR_LOG, command=self._clear_log_display)
        self.clear_log_button.pack(side=tk.BOTTOM, pady=5)

        # Configure column weights for controls_frame
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        self.status_bar = tk.Label(self.master, text=STATUS_READY, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    def _load_initial_settings(self):
        """Loads settings from ConfigManager and updates UI."""
        if self.config_manager.load_settings():
            self.source_folders = self.config_manager.source_folders
            self.destination_folder = self.config_manager.destination_folder
            self._update_source_listbox()
            
            self.dest_entry.config(state="normal")
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, self.destination_folder)
            self.dest_entry.config(state="readonly")
            self._update_destination_entry_visual()

    def _set_initial_states(self):
        """Sets initial states of UI elements."""
        self.cancel_button.config(state=tk.DISABLED)
        if self.destination_folder and os.path.exists(self.destination_folder):
            self.open_dest_button.config(state=tk.NORMAL)
        else:
            self.open_dest_button.config(state=tk.DISABLED)

        self.progress_bar['value'] = 0
        self.progress_bar['mode'] = 'determinate'
        self.progress_label.config(text=LBL_PROGRESS)
        self.add_source_button.config(state=tk.NORMAL)
        self.remove_source_button.config(state=tk.DISABLED)
        self.browse_dest_button.config(state=tk.NORMAL)
        self._update_status_bar(STATUS_READY)
        self._update_destination_entry_visual()

    def _add_source_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Source Folder")
        if folder_selected:
            folder_selected = os.path.normpath(folder_selected)
            if folder_selected not in self.source_folders:
                self.source_folders.append(folder_selected)
                self._update_source_listbox()
                self._update_status_bar(f"Added source: {os.path.basename(folder_selected)}")
            else:
                messagebox.showinfo("Info", MSG_FOLDER_ALREADY_ADDED)

    

    

    def _select_destination_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Destination Folder")
        if folder_selected:
            self.destination_folder = os.path.normpath(folder_selected)
            self.dest_entry.config(state="normal")
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, self.destination_folder)
            self.dest_entry.config(state="readonly")
            self._update_destination_entry_visual()
            if os.path.exists(self.destination_folder):
                self.open_dest_button.config(state=tk.NORMAL)
                self._update_status_bar(f"Destination set: {os.path.basename(self.destination_folder)}")
            else:
                self.open_dest_button.config(state=tk.DISABLED)
                self._update_status_bar("Invalid destination folder selected.")


    def _clear_log_display(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self._update_status_bar("Log display cleared.") # <--- NEW: Update status

    def _display_message_in_ui(self, message_data):
        """Helper to display messages from the queue in the UI."""
        level = message_data.get('level', 'info')
        message = message_data.get('message', 'No message')

        self.output_text.config(state=tk.NORMAL)
        if level == "error":
            self.output_text.insert(tk.END, f"[ERROR] {message}\n", 'error_tag')
            self.output_text.tag_config('error_tag', foreground='red')
        elif level == "warning":
            self.output_text.insert(tk.END, f"[WARNING] {message}\n", 'warning_tag')
            self.output_text.tag_config('warning_tag', foreground='orange')
        else:
            self.output_text.insert(tk.END, f"[INFO] {message}\n")
        
        self.output_text.see(tk.END)
        self.output_text.yview_scroll(1, "units")

        self.output_text.config(state=tk.DISABLED)
        self.master.update_idletasks()

    def _check_message_queue(self):
        """Periodically check the queue for messages from the worker thread."""
        while not self.message_queue.empty():
            message_data = self.message_queue.get()
            msg_type = message_data.get('type')

            if msg_type == 'progress':
                current = message_data.get('current', 0)
                total = message_data.get('total', 0)
                mode = message_data.get('mode', 'determinate')
                
                self.progress_bar['mode'] = mode
                if mode == 'determinate':
                    if total > 0:
                        self.progress_bar['value'] = current
                        self.progress_bar['maximum'] = total
                        self._update_status_bar(f"{STATUS_COPYING} ({current}/{total})") # <--- NEW: Update status
                    else:
                        self.progress_bar['value'] = 0
                        self.progress_bar['maximum'] = 1
                        self._update_status_bar(STATUS_READY) # Fallback to ready if no files
                    self.progress_label.config(text=f"Progress: {current}/{total} files")
                elif mode == 'indeterminate':
                    self.progress_bar.start()
                    self.progress_label.config(text=LBL_SCANNING)
                    self._update_status_bar(STATUS_SCANNING) # <--- NEW: Update status
            elif msg_type == 'finished':
                self.progress_bar.stop()
                self.progress_bar['mode'] = 'determinate'
                status = message_data.get('status')
                copied_count = message_data.get('copied_count', 0)
                skipped_count = message_data.get('skipped_count', 0)
                self._on_copy_finished(status, copied_count, skipped_count)
                return
            else:
                self._display_message_in_ui(message_data)

        self.master.after(100, self._check_message_queue)

    def _start_copy_process(self):
        if not self.source_folders:
            messagebox.showwarning("Warning", MSG_NO_SOURCE_FOLDERS)
            logger.warning("Attempted to start copy without source folders.")
            self._update_status_bar(STATUS_READY) # <--- NEW: Reset status
            return
        if not self.destination_folder:
            messagebox.showwarning("Warning", MSG_NO_DEST_FOLDER)
            logger.warning("Attempted to start copy without destination folder.")
            self._update_status_bar(STATUS_READY) # <--- NEW: Reset status
            return

        if not os.path.isdir(self.destination_folder):
            messagebox.showerror("Error", f"The selected destination folder does not exist or is not a valid directory:\n'{self.destination_folder}'\nPlease select a valid folder.")
            logger.error(f"Invalid destination folder selected: {self.destination_folder}")
            self._update_status_bar(STATUS_FAILED) # <--- NEW: Update status
            return # Prevent starting the copy process
        confirm = messagebox.askyesno(
            MSG_CONFIRM_COPY_TITLE,
            f"Are you sure you want to copy images from {len(self.source_folders)} folder(s) to:\n'{self.destination_folder}'?\n\nExisting files will be renamed to unique IDs."
        )
        if not confirm:
            logger.info("Copy process cancelled by user confirmation dialog.")
            self._update_status_bar(STATUS_READY) # <--- NEW: Reset status
            return

        self._clear_log_display()
        self._display_message_in_ui({'level': 'info', 'message': "Initiating copy process..."})
        self._update_status_bar("Starting copy process...") # <--- NEW: Update status

        self.cancel_event.clear()
        self._set_ui_state_on_start()
        
        self.current_copy_thread = threading.Thread(
            target=copy_worker,
            args=(self.source_folders, self.destination_folder, self.message_queue, self.cancel_event)
        )
        self.current_copy_thread.daemon = True
        self.current_copy_thread.start()

        self.master.after(100, self._check_message_queue)

    def _cancel_copy_process(self):
        if messagebox.askyesno(MSG_CONFIRM_CANCEL_TITLE, "Are you sure you want to cancel the current copying process?"):
            self.cancel_event.set()
            self._display_message_in_ui({'level': 'warning', 'message': "Cancellation requested. Waiting for current file operation to finish..."})
            logger.warning("User requested cancellation.")
            
            self.progress_bar.stop()
            self.progress_bar['mode'] = 'determinate'
            self.progress_bar['value'] = 0
            self.progress_label.config(text=LBL_PROGRESS) 
            self._update_status_bar(STATUS_CANCELLED) # <--- NEW: Update status

            self._set_ui_state_on_finish(cancelled=True)

    def _on_copy_finished(self, status, copied_count, skipped_count):
        """Called when the worker thread signals completion."""
        self.progress_bar.stop()
        self.progress_bar['mode'] = 'determinate'
        self._set_ui_state_on_finish()
        if status == 'completed':
            messagebox.showinfo(MSG_PROCESS_COMPLETE, f"Successfully copied {copied_count} image files.")
            logger.info(f"Copy process completed successfully. Copied: {copied_count}, Skipped: {skipped_count}")
            self._update_status_bar(STATUS_COMPLETE) # <--- NEW: Update status
        elif status == 'completed_with_errors':
            messagebox.showwarning(MSG_PROCESS_COMPLETE_WITH_ERRORS, f"Copied {copied_count} files, but {skipped_count} files were skipped due to errors. Check log for details.")
            logger.warning(f"Copy process completed with errors. Copied: {copied_count}, Skipped: {skipped_count}")
            self._update_status_bar(STATUS_COMPLETE_ERRORS) # <--- NEW: Update status
        elif status == 'cancelled':
            messagebox.showinfo(MSG_PROCESS_CANCELLED, "Image copying process was cancelled.")
            logger.info("Copy process explicitly cancelled.")
            self._update_status_bar(STATUS_CANCELLED) # <--- NEW: Update status
        elif status == 'error':
            messagebox.showerror(MSG_PROCESS_FAILED, "Image copying process failed due to an error. Check log for details.")
            logger.error("Copy process failed.")
            self._update_status_bar(STATUS_FAILED) # <--- NEW: Update status

    def _set_ui_state_on_start(self):
        """Sets UI elements to a state appropriate for process start."""
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.add_source_button.config(state=tk.DISABLED)
        self.remove_source_button.config(state=tk.DISABLED)
        self.browse_dest_button.config(state=tk.DISABLED)
        self.open_dest_button.config(state=tk.DISABLED)

    def _set_ui_state_on_finish(self, cancelled=False):
        """Sets UI elements back to a state appropriate for process finish."""
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.add_source_button.config(state=tk.NORMAL)
        self.remove_source_button.config(state=tk.NORMAL)
        self.browse_dest_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_label.config(text=LBL_PROGRESS)

        if not cancelled and self.destination_folder and os.path.exists(self.destination_folder):
            self.open_dest_button.config(state=tk.NORMAL)
        else:
            self.open_dest_button.config(state=tk.DISABLED)            
            
    def _remove_selected_source_folder(self, event=None):
        selected_index = self.source_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            folder_to_remove = self.source_folders[index]
            # --- NEW: Confirmation Dialog ---
            confirm = messagebox.askyesno("Confirm Removal", f"{MSG_CONFIRM_REMOVE_FOLDER}\n\n'{folder_to_remove}'?")
            if not confirm:
                logger.info(f"Removal of folder '{folder_to_remove}' cancelled by user.")
                return
            # --- END NEW ---

            removed_folder = self.source_folders.pop(index)
            self._update_source_listbox()
            logger.info(f"Removed source folder: {removed_folder}")
            self._update_status_bar(f"Removed source: {os.path.basename(removed_folder)}")
        else:
            messagebox.showwarning("Warning", "Please select a source folder to remove.")
            logger.warning("Attempted to remove source folder without selection.")
            
    def _update_source_listbox(self):
        """Refreshes the source folders listbox."""
        self.source_listbox.delete(0, tk.END)
        for folder in self.source_folders:
            self.source_listbox.insert(tk.END, folder)
        self.config_manager.source_folders = self.source_folders
        self._on_listbox_select() # <--- NEW: Call to update button state after refresh
        
    def _on_listbox_select(self, event=None): # <--- NEW METHOD: Handle listbox selection
        """Enables/disables the remove button based on listbox selection."""
        if self.source_listbox.curselection():
            self.remove_source_button.config(state=tk.NORMAL)
        else:
            self.remove_source_button.config(state=tk.DISABLED)
    # ... (rest of _set_ui_state_on_start, _set_ui_state_on_finish unchanged) ...
    def _open_destination_folder(self):
        if self.destination_folder and os.path.exists(self.destination_folder):
            try:
                if os.sys.platform == "win32":
                    os.startfile(self.destination_folder)
                elif os.sys.platform == "darwin":
                    os.system(f"open \"{self.destination_folder}\"")
                else:
                    os.system(f"xdg-open \"{self.destination_folder}\"")
                logger.info(f"Opened destination folder: {self.destination_folder}")
                self._update_status_bar(f"Opened: {os.path.basename(self.destination_folder)}") # <--- NEW: Update status
            except Exception as e:
                messagebox.showerror("Error", f"Could not open destination folder: {e}")
                logger.error(f"Failed to open destination folder '{self.destination_folder}': {e}")
                self._update_status_bar(STATUS_FAILED) # <--- NEW: Update status
        else:
            messagebox.showwarning("Warning", MSG_DEST_FOLDER_NOT_EXIST)
            logger.warning("Attempted to open non-existent destination folder.")
            self._update_status_bar("Cannot open: Destination not set or invalid.") # <--- NEW: Update status

    def _open_log_file(self):
        try:
            if os.path.exists(LOG_FILEPATH):
                if os.sys.platform == "win32":
                    os.startfile(LOG_FILEPATH)
                elif os.sys.platform == "darwin":
                    os.system(f"open \"{LOG_FILEPATH}\"")
                else:
                    os.system(f"xdg-open \"{LOG_FILEPATH}\"")
                logger.info(f"Opened log file: {LOG_FILEPATH}")
                self._update_status_bar("Opened log file.") # <--- NEW: Update status
            else:
                messagebox.showwarning("Warning", MSG_LOG_FILE_NOT_FOUND)
                logger.warning(f"Attempted to open non-existent log file: {LOG_FILEPATH}")
                self._update_status_bar("Log file not found.") # <--- NEW: Update status
        except Exception as e:
            messagebox.showerror("Error", f"Could not open log file: {e}")
            logger.error(f"Failed to open log file '{LOG_FILEPATH}': {e}")
            self._update_status_bar(STATUS_FAILED) # <--- NEW: Update status

    def on_closing(self):
        """Handle window closing, ensuring thread is cleaned up and settings saved."""
        if self.current_copy_thread and self.current_copy_thread.is_alive():
            if messagebox.askyesno(MSG_CONFIRM_EXIT_TITLE, "A copy process is running. Do you want to stop it and exit?"):
                self.cancel_event.set()
                self._update_status_bar("Attempting to stop copy process before exiting...")
                logger.info("Application closing: Cancellation requested for active copy thread.")
                
                # --- MODIFIED: Wait for the thread to finish with a timeout ---
                self.current_copy_thread.join(timeout=5) # Wait up to 5 seconds
                if self.current_copy_thread.is_alive():
                    logger.warning("Copy thread did not terminate gracefully within timeout.")
                    self._update_status_bar("Forcing exit (copy thread still running).")
                else:
                    logger.info("Copy thread terminated gracefully.")
                    self._update_status_bar("Copy thread stopped. Exiting.")
                # --- END MODIFIED ---

                self.config_manager.save_settings(self.source_folders, self.destination_folder)
                self.master.destroy()
            else:
                pass
        else:
            self.config_manager.save_settings(self.source_folders, self.destination_folder)
            self.master.destroy()

    def _show_about_dialog(self):
        """Displays an About dialog with application information."""
        messagebox.showinfo("About " + APP_NAME, ABOUT_TEXT)
        self._update_status_bar("About dialog displayed.") # <--- NEW: Update status

    # --- NEW METHOD: Update Status Bar ---
    def _update_status_bar(self, message):
        """Updates the text in the status bar."""
        self.status_bar.config(text=message)
        self.master.update_idletasks() # Ensure it updates visually
    
    def _update_destination_entry_visual(self):
        if self.destination_folder and os.path.isdir(self.destination_folder):
            self.dest_entry.config(bg="lightgreen", fg="black", relief=tk.RIDGE) # Valid path: green background, raised
        else:
            self.dest_entry.config(bg="lightcoral", fg="black", relief=tk.GROOVE) # Invalid path: red background, sunken
        self.master.update_idletasks() # Ensure immediate visual update
    # --- END NEW METHOD ---

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCopierApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()