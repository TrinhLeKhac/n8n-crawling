#!/usr/bin/env python3
import paramiko

# Server connection details
HOST = input("Server IP: ")
USERNAME = input("Username: ")
PASSWORD = input("Password: ")
PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, PORT, USERNAME, PASSWORD)
    print(f"✓ Connected to {HOST}")
    
    # Check OS and install git
    stdin, stdout, stderr = ssh.exec_command("which apt || which yum")
    pkg_manager = "apt" if "apt" in stdout.read().decode() else "yum"
    
    # Install git and handle repository
    git_commands = [
        f"{pkg_manager} update && {pkg_manager} install -y git" if pkg_manager == "apt" else f"{pkg_manager} update -y && {pkg_manager} install -y git",
        "cd /root && if [ ! -d n8n-crawling ]; then git clone https://github.com/TrinhLeKhac/n8n-crawling.git; else cd n8n-crawling && git pull origin main; fi",
        "cd /root/n8n-crawling && if [ -f venv/bin/activate ]; then source venv/bin/activate && pip install -r requirements.txt; else echo 'Virtual environment not found, run setup_env.py first'; fi"
    ]
    
    print("Pulling latest code from Git...")
    for cmd in git_commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode()
        error = stderr.read().decode()
        if result:
            print(result)
        if error:
            print(f"Error: {error}")
    
    print("✓ Code updated from Git")
    print("Use run_crawler.py to execute crawler")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()