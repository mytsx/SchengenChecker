# Schengen Visa Appointment Checker 🌍

An automated monitoring system built with **Python** to check for available Schengen visa appointments. It provides real-time notifications via a web dashboard, Telegram bot, and desktop notifications while logging the data for analysis.

---

## 🏗️ **Features**

✨ **Real-time Monitoring**  
- Automatically checks Schengen visa appointment availability at configurable intervals.  

📢 **Multi-channel Notifications**  
- Desktop notifications for instant alerts.
- Telegram notifications using a bot.    
- Web dashboard for real-time updates.  
- Detailed logging of events.  

💾 **Data Persistence**  
- Stores data in both **PostgreSQL** and **SQLite** for reliability and local access.  
- Automatically prunes SQLite data to keep it lightweight (up to 5,000 records per table).

🖥️ **Web Dashboard**  
- Beautiful, responsive interface to track:
  - Recent appointments.
  - API response changes.
  - Complete log history.

⚙️ **Configurable Settings**  
- All settings are managed through JSON configuration files stored in the `config` folder.

---

## 🚀 **Getting Started**

### **Setup Instructions**

1. **Install Python**:  
   - Visit [Python.org's Beginner Guide](https://www.python.org/about/gettingstarted/).  
   - Download and install Python 3.7 or newer.  
   - During installation, ensure "Add Python to PATH" is checked.

2. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Application:**
   - Update the configuration files in the `config` folder.
   - See the "Configuration" section for details.

5. **Start the Application:**
   ```bash
   bash start.sh
   ```
   
   The application includes:
   - A background process for monitoring visa appointments.
   - A web server running at `http://localhost:8080`.

> **Running on WSL?**  
> Check the [WSL Setup Guide](./WSL%20Setup%20Guide.md) for detailed instructions on configuring and running the application on Windows Subsystem for Linux.

---

## ⚙️ **Configuration**

All configuration files are located in the `config` folder. Update the relevant JSON files before running the application.

### **Main Configuration (`config/config.json`)**
```json
{
  "notification": true,
  "check_interval": 600,
  "desktop_notification": true,
  "telegram_notification": true
}
```
- `notification`: Enable/disable notifications globally.
- `check_interval`: Time between checks (in seconds).
- `desktop_notification`: Enable/disable desktop notifications.
- `telegram_notification`: Enable/disable Telegram notifications.

### **Telegram Bot Configuration (`config/telegram.json`)**
```json
{
  "telegram_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID"
}
```
- `telegram_token`: The bot token provided by [BotFather](https://t.me/BotFather).
- `telegram_chat_id`: Your personal or group chat ID.

### **Database Configuration (`config/database.json`)**
```json
{
  "postgres": {
    "dbname": "your_dbname",
    "user": "your_user",
    "password": "your_password",
    "host": "your_host",
    "port": 5432
  },
  "sqlite": {
    "file": "local_data.db"
  }
}
```
- PostgreSQL is used for persistent storage.
- SQLite is used as a lightweight local database.

---

## 🔀 **Telegram Bot Integration**

### Steps to Set Up Telegram Bot

1. **Create a Bot:**
   - Open [BotFather](https://t.me/BotFather) on Telegram.
   - Use the `/newbot` command to create a new bot.
   - Save the provided bot token.

2. **Get Your Chat ID:**
   - Start a chat with your bot and send a message (e.g., `/start`).
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to find your chat ID in the response.

3. **Update `config/telegram.json`:**
   ```json
   {
     "telegram_token": "YOUR_BOT_TOKEN",
     "telegram_chat_id": "YOUR_CHAT_ID"
   }
   ```

4. **Run the Application:**
   - Ensure `telegram_notification` is enabled in `config/config.json`.

The bot will now send appointment notifications to your Telegram chat.

You can use it here: [SchengenCheckerBot](https://t.me/SchengenCheckerBot)

---


## 📚 **Project Structure**

```
project_root/
├── config/                 # Configuration files
│   ├── config.json         # Main application settings
│   ├── telegram.json       # Telegram bot settings
│   ├── database.json       # Database settings
├── static/                 # Static web assets
│   ├── css/                # CSS styles
│   └── js/                 # JavaScript files
├── templates/              # HTML templates
├── app.py                  # Flask web application
├── checker_runner.py       # Main checker script
├── database.py             # Database operations
├── schengen_checker.py     # Core checking logic
├── telegram_bot.py         # Telegram bot integration
├── config_loader.py        # Config file loader
├── requirements.txt        # Python dependencies
├── start.sh                # Startup script
```

---


## 💾 **Database Tables**

### PostgreSQL
- **`responses`**: Tracks API response changes.
- **`logs`**: General application logs.
- **`appointments`**: Stores appointment availability history.

### SQLite (for local storage)
- Same structure as PostgreSQL.
- Automatically prunes older records, keeping only the last 5,000 entries per table.

---


## 🛠️ **Tech Stack**

- **Backend**: Python 3.7+
- **Web Framework**: Flask
- **Database**: PostgreSQL + SQLite
- **Frontend**:  
  - HTML5
  - CSS3 (Bootstrap 5)
  - JavaScript
- **Dependencies**:  
  - `requests`: API communication
  - `plyer`: Desktop notifications
  - `flask`: Web interface
  - `psycopg2-binary`: PostgreSQL integration
  - `pytz`: Timezone handling
  - `gunicorn`: WSGI server for deploying Flask applications

---


## 🔎 **Web Interface**

### **Dashboard Features**
Access the monitoring dashboard at `http://localhost:8080`. It includes:
- **Recent Appointments**: Displays the latest appointment availability.
- **Response Changes**: Highlights changes in API responses.
- **Complete Logs**: Detailed logs for debugging and analysis.

### **Live Updates**
- The dashboard auto-refreshes every 10 seconds using AJAX.

You can also visit the live application here: [Schengen Checker Web Interface](https://schengen-checker-mytsx.replit.app/)

---

## 🔄 **Autostart Configuration**

### **Windows**
1. Create `start_schengen.bat`:
   ```batch
   @echo off
   cd /d %~dp0
   python checker_runner.py
   ```
2. Press `Win + R`, type `shell:startup`, and copy the batch file there.

### **Linux/macOS**
1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/schengen-checker.service
   ```
2. Add configuration:
   ```ini
   [Unit]
   Description=Schengen Visa Checker
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/checker_runner.py
   WorkingDirectory=/path/to/project
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl enable schengen-checker
   sudo systemctl start schengen-checker
   ```

---

## 🚧 **Rate Limiting**

The application implements responsible API usage:
- Configurable check intervals (default: 10 seconds).
- Built-in error handling for API failures.
- Automatic retry mechanism with exponential backoff.

---

## 🙏 **Contributing**

1. Fork the repository.  
2. Create a feature branch.  
3. Commit changes.  
4. Push to the branch.  
5. Create a Pull Request.

---

## 🆘 **Support**

For support:
1. Check existing issues.  
2. Create a new issue with:
   - Detailed description.  
   - Steps to reproduce.  
   - Expected vs actual behavior.

---

## 📄 **License**

This project is licensed under the MIT License - see the `LICENSE` file for details.
