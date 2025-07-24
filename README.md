# Image Organizer & Copier

## Table of Contents
- [About](#about)
- [Features](#features)
- [Installation](#installation)
  - [From Source](#from-source)
  - [Standalone Executable](#standalone-executable)
- [How to Use](#how-to-use)
- [Configuration & Logs](#configuration--logs)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About
The **Image Organizer & Copier** is a straightforward desktop application designed to simplify the process of consolidating image files from various sources into a single, organized destination folder. It intelligently renames files based on their creation date and a unique identifier to prevent naming conflicts, making it perfect for managing photos from multiple cameras, phones, or storage devices.

Built with Python and Tkinter, it offers a user-friendly graphical interface with real-time feedback and persistent settings.

## Features
-   **Multi-Source Consolidation:** Effortlessly add and manage multiple source directories from which to copy images.
-   **Intelligent Renaming:** Automatically renames copied images to a `YYYYMMDD_HHMMSS_UniqueId.ext` format, ensuring no overwrites due to identical filenames.
-   **Intuitive GUI:** A clean and easy-to-navigate graphical user interface.
-   **Persistent Settings:** Your selected source and destination folders are automatically saved and loaded between sessions.
-   **Real-time Progress & Logging:** Monitor the copy process with a dynamic progress bar and a detailed, scrollable log display within the application.
-   **Process Control:** Ability to cancel an ongoing copy operation gracefully at any time.
-   **Quick Access:** Dedicated buttons to instantly open the destination folder or the application's comprehensive log file.
-   **Visual Feedback:** The destination folder input field provides immediate visual cues (green/red border) indicating its path validity.
-   **Dynamic UI Elements:** The "Remove Selected" button automatically enables/disables based on whether an item is selected in the source folders list.
-   **Robust Application Exit:** Ensures background copying processes are handled cleanly when the application is closed.
-   **Standalone Distribution:** Can be packaged into a single executable file for easy sharing and use without requiring Python installation on target machines.

## Installation

### From Source
To run the application directly from its source code:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/Image-Organizer-Copier.git](https://github.com/your-username/Image-Organizer-Copier.git)
    cd Image-Organizer-Copier
    ```
    *(Remember to replace `your-username/Image-Organizer-Copier.git` with the actual URL of your repository.)*

2.  **Create and activate a virtual environment (highly recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install pyinstaller # Required for building the executable
    pip install appdirs     # Recommended for cross-platform config/log path handling
    ```
    *(Note: Tkinter is part of Python's standard library and usually doesn't require separate installation.)*

4.  **Run the application:**
    ```bash
    python app.py
    ```

### Standalone Executable
You can also generate a single executable file for easier distribution:

1.  **Ensure you have PyInstaller installed** (see "From Source" installation steps).
2.  **Navigate to the project's root directory** in your terminal or command prompt.
3.  **Build the executable:**
    * **For Windows:**
        ```bash
        pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "icon.ico;." app.py
        ```
    * **For macOS/Linux:**
        ```bash
        pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "icon.ico:." app.py
        ```
4.  **Locate the executable:** Your standalone application will be found in the `dist/` folder within your project directory.

## How to Use

1.  **Add Source Folders:** Click "Add Folder..." to browse and select one or more directories containing the image files you wish to copy.
2.  **Set Destination Folder:** Click "Browse" next to the "Destination Folder" field to choose the single target directory for your copied images. The input field will visually indicate (green/red border) if the selected path is valid.
3.  **Start Copy:** Once your source(s) and a valid destination are set, click "Start Copy" to begin the transfer process.
4.  **Monitor Progress:** Observe the progress bar and the detailed log area for real-time updates on the copying operation.
5.  **Cancel:** To halt an ongoing copy operation, click the "Cancel" button.
6.  **Open Destination:** The "Open Destination Folder" button provides quick access to your target directory in your system's file explorer.
7.  **View Logs:** Click "Open Log File" to open the comprehensive application log file, useful for debugging or reviewing past operations.

## Configuration & Logs
The application automatically saves your selected source and destination folders between sessions for convenience.

* **Configuration File (`config.json`):** This file stores your application settings. Its location is typically within your user's application data directory, which varies by OS:
    * **Windows:** `C:\Users\<YourUsername>\AppData\Local\<APP_NAME>\<APP_AUTHOR>\config.json`
    * **macOS:** `/Users/<YourUsername>/Library/Application Support/<APP_NAME>/config.json`
    * **Linux:** `/home/<YourUsername>/.config/<APP_NAME>/config.json`
    *(Note: `<APP_NAME>` and `<APP_AUTHOR>` are defined within the application's constants.)*

* **Log File (`log.log`):** Detailed logs of all operations, warnings, and errors are written to this file. You can easily access it via the "Open Log File" button in the application. It is located alongside the `config.json` in the user data directory.

## Troubleshooting
* **"Folder already added"**: You are attempting to add a source folder that is already present in your list.
* **"No source folders selected" / "No destination folder selected"**: Ensure you have added at least one source folder and provided a valid destination folder.
* **"Destination folder does not exist"**: The selected path for the destination folder is invalid or does not exist. Please choose an existing directory.
* **"Log file not found"**: The log file might have been moved or deleted externally. A new one will be created automatically upon the next application run.
* **Application crash/unexpected behavior**: Check the `log.log` file for detailed error messages. These logs are crucial for diagnosing issues.

## Contributing
Contributions are welcome! If you find a bug or have an idea for a new feature, please feel free to open an issue or submit a pull request on the GitHub repository.

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contact
Developed by RFID Tags and Services
[Optional: Your GitHub Profile Link, Website, or Email]