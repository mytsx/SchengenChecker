# Schengen Visa Appointment Checker

A Python-based application to monitor Schengen visa appointment availability and send desktop notifications when an appointment is found.

## Features
- Automatically checks for available Schengen visa appointments every 10 minutes (or configurable interval).
- Sends desktop notifications with appointment details when an appointment is found.
- Logs appointment availability, errors, and check timestamps to separate log files.
  - `appointment_logs.txt`: Logs appointment details and errors.
  - `control_times.txt`: Logs the times the script checks for appointments.

## Requirements
- Python 3.7+ (ensure it is installed if running the script on a new machine).
- Required Python libraries:
  - `requests`
  - `plyer`

## Installation

### On a Computer Without Python Installed:

1. **Install Python**:
   - Download Python from the [official Python website](https://www.python.org/).
   - Install Python and ensure the option "Add Python to PATH" is selected during installation.

2. **Download the Project**:
   - Clone this repository or download it as a ZIP file and extract it:
     ```bash
     git clone <repository_url>
     cd <repository_name>
     ```

3. **Install Required Libraries**:
   - Open a terminal (or Command Prompt) and install the dependencies:
     ```bash
     pip install -r requirements.txt
     ```
     Alternatively, install them manually:
     ```bash
     pip install requests plyer
     ```

4. **Save the Script**:
   - Ensure the script is saved as `SchengenChecker.py` (or any preferred name).

## Usage

Run the script using Python:

```bash
python SchengenChecker.py
```

The program will:
1. Check for Schengen visa appointment availability using the specified API.
2. Print availability information in the terminal.
3. Send a desktop notification if an appointment is available.
4. Log all relevant details in `appointment_logs.txt` and `control_times.txt`.
5. Repeat the process every 10 minutes.

## Configuration

- **Interval**: The default interval is set to 10 minutes. You can change this by modifying the `time.sleep()` value in the code:

  ```python
  time.sleep(600)  # Adjust the interval (in seconds)
  ```

- **API URL**: If the API URL changes, update the `url` variable:

  ```python
  url = "<new_api_endpoint>"
  ```

## Example Output

**Console Output:**
```bash
Kontrol başlatıldı.
France için randevu tarihi: 2024-12-15
Germany için mevcut randevu yok.
```

**Desktop Notification:**
- Title: `Randevu Bulundu`
- Message: `France için randevu tarihi: 2024-12-15`

## Log Files

- `appointment_logs.txt`: Contains detailed logs of appointment availability and errors.
- `control_times.txt`: Logs timestamps for when checks are performed.

## Dependencies
- **Requests**: To handle HTTP requests.
- **Plyer**: For desktop notifications.

Install dependencies using:
```bash
pip install requests plyer
```

## Notes
- Ensure an active internet connection to fetch data from the API.
- Desktop notifications may behave differently based on your operating system. For Windows, ensure system notifications are enabled.
- Log files will be created in the same directory as the script.

## Automatically Start on Boot

To make the script run automatically when your computer starts:

### Windows:
1. **Create a Shortcut**:
   - Right-click on the script or a `.bat` file that runs the script and create a shortcut.
   - Move the shortcut to the `Startup` folder. Access it by pressing `Win + R`, typing `shell:startup`, and pressing Enter.

2. **Create a `.bat` File**:
   - Create a file named `start_script.bat` with the following content:
     ```bat
     @echo off
     python "path\to\SchengenChecker.py"
     pause
     ```
   - Replace `path\to\SchengenChecker.py` with the full path to your Python script.
   - Place this `.bat` file in the `Startup` folder.

3. **Optional**: Use Task Scheduler for more control.

### macOS/Linux Users:
1. **Create a Shell Script**:
   - Create a file named `start_script.sh` with the following content:
     ```bash
     #!/bin/bash
     python3 /path/to/SchengenChecker.py
     ```
   - Replace `/path/to/SchengenChecker.py` with the full path to your Python script.

2. **Make the Script Executable**:
   ```bash
   chmod +x start_script.sh
   ```

3. **Add to Startup Applications**:
   - On Linux, add the script to your startup applications.
   - On macOS, use `launchd` or another startup manager to run the script automatically.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing
Contributions are welcome! If you'd like to improve this program, please fork the repository and submit a pull request.

## Contact
For any inquiries or issues, feel free to open an issue in the repository or contact the maintainer.

