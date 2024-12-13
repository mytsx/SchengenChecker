# Schengen Visa Appointment Checker 🌍

An automated monitoring system built with **Python** to check for available Schengen visa appointments. It provides real-time notifications via a web dashboard, desktop notifications, and logs the data for analysis.

---

## 🏗️ **Features**

✨ **Real-time Monitoring**  
- Automatically checks Schengen visa appointment availability at configurable intervals.  

📢 **Multi-channel Notifications**  
- Desktop notifications for instant alerts.  
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
- Easy-to-edit JSON files for notification preferences and check intervals.

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

---

## 🚀 **Getting Started**

### 🐍 **For Python Beginners**

1. **Install Python**:  
   - Visit [Python.org's Beginner Guide](https://www.python.org/about/gettingstarted/).  
   - Download and install Python 3.7 or newer.  
   - During installation, ensure "Add Python to PATH" is checked.

2. **Install Dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ **Configuration**

### Main Configuration (`config.json`)
```json
{
  "notification": false,
  "check_interval": 10
}
```
- `notification`: Enable/disable desktop notifications.  
- `check_interval`: Time between checks (in seconds).

### Database Configuration (`postgreconfig.json`)
```json
{
  "host": "your_host",
  "database": "your_db",
  "user": "your_user",
  "password": "your_password"
}
```

---

## 📁 **Project Structure**

```
├── static/                 # Static web assets
│   ├── css/                # CSS styles
│   └── js/                 # JavaScript files
├── templates/              # HTML templates
├── app.py                  # Flask web application
├── checker_runner.py       # Main checker script
├── config.json             # Main configuration file
├── postgreconfig.json      # PostgreSQL configuration file
├── database.py             # Database operations
├── schengen_checker.py     # Core checking logic
├── local_data.db           # SQLite database file
├── requirements.txt        # Python dependencies
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

## 🖥️ **Web Interface**

### **Dashboard Features**
Access the monitoring dashboard at `http://localhost:8080` after starting the application. It includes:
- **Recent Appointments**: Displays the latest appointment availability.
- **Response Changes**: Highlights changes in API responses.
- **Complete Logs**: Detailed logs for debugging and analysis.
- **Auto-refresh**: Updates every 10 seconds.

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

---

## 🛡️ **Rate Limiting**

The application implements responsible API usage:
- Configurable check intervals (default: 10 seconds).
- Built-in error handling for API failures.
- Automatic retry mechanism with exponential backoff.

---

## 🤝 **Contributing**

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
