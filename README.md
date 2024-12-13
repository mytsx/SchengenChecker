# Schengen Visa Appointment Checker

A Python-based application to monitor Schengen visa appointment availability and send desktop notifications when an appointment is found.

## Features
- Automatically checks for available Schengen visa appointments every 10 minutes (or configurable interval).
- Sends desktop notifications with appointment details when an appointment is found.
- Logs appointment availability and errors to the console.

## Requirements
- Python 3.7+
- Required Python libraries:
  - `requests`
  - `plyer`

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, you can manually install the libraries:
   ```bash
   pip install requests plyer
   ```

3. Save the script as `SchengenChecker.py` (or any preferred name).

## Usage

Run the script using Python:

```bash
python SchengenChecker.py
```

The program will:
1. Check for Schengen visa appointment availability using the specified API.
2. Print availability information in the terminal.
3. Send a desktop notification if an appointment is available.
4. Repeat the process every 10 minutes.

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
program çalıştı
France için randevu tarihi: 2024-12-15
Germany için mevcut randevu yok.
```

**Desktop Notification:**
- Title: `Randevu Bulundu`
- Message: `France için randevu tarihi: 2024-12-15`

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

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing
Contributions are welcome! If you'd like to improve this program, please fork the repository and submit a pull request.

## Contact
For any inquiries or issues, feel free to open an issue in the GitLab repository or contact the maintainer.
