# WSL Setup Guide for SchengenChecker

This guide provides step-by-step instructions on setting up and running the SchengenChecker project in **Windows Subsystem for Linux (WSL)**.

---

## 1. **Install WSL**

### Steps to Enable WSL on Windows:

1. **Open PowerShell as Administrator**:
   - Press `Win + X` > Select **PowerShell (Admin)**.

2. **Enable WSL**:
   ```powershell
   wsl --install
   ```
   This command installs the latest WSL version (WSL 2) along with Ubuntu as the default Linux distribution.

3. **Restart Your Computer**:
   - Restart your machine after installation is complete.

4. **Verify Installation**:
   - Open a new PowerShell window and run:
     ```powershell
     wsl --list --verbose
     ```
     You should see Ubuntu (or your chosen Linux distribution) listed.

---

## 2. **Set Up WSL Environment**

### A. Open WSL Terminal
1. Open the **Ubuntu** app from the Start Menu.
2. Follow the prompts to set a username and password.

### B. Update and Install Required Tools
Run the following commands to update your WSL environment:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git unzip -y
```

---

## 3. **Clone the SchengenChecker Repository**

### A. Clone the Repository in WSL
Navigate to your home directory and clone the repository:
```bash
cd ~
git clone https://github.com/mytsx/SchengenChecker.git
cd SchengenChecker
```

---

## 4. **Prepare Configuration Files**

### A. Copy Configuration Files from Windows
1. **Find the Config Directory**:
   - Locate the `config` directory on your Windows machine.

2. **Copy to WSL**:
   Use PowerShell to copy the `config` directory into WSL:
   ```powershell
   cp -r C:\path\to\config \wsl$\Ubuntu\home\<your_wsl_username>\SchengenChecker\
   ```

   Alternatively, you can use File Explorer:
   - Navigate to: `\\wsl$\Ubuntu\home\<your_wsl_username>\SchengenChecker\`
   - Drag and drop the `config` directory into the project folder.

---

## 5. **Set Up the Virtual Environment**

### A. Create a Virtual Environment
Run the following commands to create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### B. Install Dependencies
Once the virtual environment is activated, install the required packages:
```bash
pip install -r requirements.txt
```

---

## 6. **Run the Application**

### A. Start the Application
Run the following command to start the application:
```bash
bash start.sh
```

### B. Access the Application in Windows
1. **Find the WSL IP Address**:
   Run this command in WSL to find the IP address:
   ```bash
   hostname -I
   ```
   Example output: `172.20.10.5`.

2. **Access in Your Browser**:
   Open your browser in Windows and navigate to:
   ```
   http://<WSL_IP>:8080
   ```
   Example: `http://172.20.10.5:8080`

3. **If Using WSL 2**:
   You can also access the application directly via `http://localhost:8080`.

---

## 7. **Automating Application Startup**

### A. Windows Startup Using Task Scheduler
1. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, and press Enter.

2. **Create a New Task**:
   - Click on **Create Task** in the right-hand menu.

3. **Set General Settings**:
   - **Name**: WSL Start
   - **Description**: Start WSL and run SchengenChecker.
   - Check **Run only when user is logged on**.
   - Check **Run with highest privileges**.

4. **Set Trigger**:
   - Click **New**, select **At log on**, and click OK.

5. **Set Action**:
   - Click **New**, select **Start a Program**, and enter the following:
     - **Program/Script**: `wsl.exe`
     - **Arguments**: `/bin/bash -c "cd ~/SchengenChecker && source venv/bin/activate && bash start.sh"`

6. **Save and Test**:
   - Save the task and restart your computer to verify it works.

### B. Auto-Start Inside WSL Using `.bashrc`
1. **Edit `.bashrc` File**:
   ```bash
   nano ~/.bashrc
   ```

2. **Add SchengenChecker Commands**:
   Add the following lines to the end of the file:
   ```bash
   if [[ $(tty) == /dev/tty1 ]]; then
       cd ~/SchengenChecker
       source venv/bin/activate
       bash start.sh
   fi
   ```

3. **Save and Test**:
   - Save the file (`Ctrl + O`, then `Ctrl + X`) and restart WSL.

### C. Windows Startup Using Batch Script
1. **Create a Batch Script**:
   - Create a file called `start_schengen.bat` with the following content:
     ```batch
     @echo off
     wsl -e bash -c "cd ~/SchengenChecker && source venv/bin/activate && bash start.sh"
     ```

2. **Add to Windows Startup Folder**:
   - Press `Win + R`, type `shell:startup`, and press Enter.
   - Copy `start_schengen.bat` into the startup folder.

---

## 8. **Troubleshooting**

### A. Common Issues
1. **Cannot Access the Application**:
   - Ensure the application is running on `0.0.0.0` and not `127.0.0.1`.
   - Check your firewall settings to ensure port `8080` is open.

2. **Missing Dependencies**:
   - Reinstall requirements using:
     ```bash
     pip install --force-reinstall -r requirements.txt
     ```

3. **Permission Errors**:
   - Use `sudo` if required for system-level operations.

---

## 9. **Next Steps**

- Test the application by visiting:
  - [Telegram Bot](https://t.me/SchengenCheckerBot)
  - The web interface at your configured URL.

- For further contributions or updates, refer to the primary README file in the repository.

---

## 10. **Resources**

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [SchengenChecker GitHub Repository](https://github.com/mytsx/SchengenChecker)

