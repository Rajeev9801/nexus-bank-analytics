# Build Instructions for Nexus Bank Analytics

To convert this project into a standalone Windows Executable (.exe), follow these steps:

1.  **Install PyInstaller**:
    ```bash
    pip install pyinstaller
    ```

2.  **Run the Build Command**:
    Navigate to the project root and run:
    ```bash
    pyinstaller --noconsole --onefile --name "NexusBankAnalytics" --add-data "banking-dashboard/database_files;database_files" --add-data "banking-dashboard/assets;assets" --add-data "banking-dashboard/themes;themes" banking-dashboard/main.py
    ```

3.  **Find your EXE**:
    The executable will be generated in the `dist/` folder.

### Notes for Assets:
If you add images to the `assets/` folder, ensure the `--add-data` flags in the command above are updated to include them. The current code is optimized to look for the database and logs in relative paths.
