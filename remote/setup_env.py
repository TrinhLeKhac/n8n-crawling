#!/usr/bin/env python3
import paramiko
from pathlib import Path

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
    
    # Check and create n8n-crawling folder if not exists
    stdin, stdout, stderr = ssh.exec_command("ls -la /root/n8n-crawling")
    if stderr.read().decode():
        print("Creating n8n-crawling folder...")
        ssh.exec_command("mkdir -p /root/n8n-crawling/output")
    else:
        print("n8n-crawling folder already exists")
    
    # Check OS and setup environment
    stdin, stdout, stderr = ssh.exec_command("which apt || which yum")
    pkg_manager = "apt" if "apt" in stdout.read().decode() else "yum"
    
    if pkg_manager == "apt":
        setup_commands = [
            "apt update",
            "apt install -y python3-pip python3-venv wget unzip",
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -",
            "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list",
            "apt update",
            "apt install -y google-chrome-stable"
        ]
    else:
        setup_commands = [
            "yum update -y",
            "yum install -y python3-pip wget unzip",
            "yum install -y chromium"
        ]
    
    # Common commands
    setup_commands.extend([
        "wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip",
        "unzip /tmp/chromedriver.zip -d /usr/local/bin/",
        "chmod +x /usr/local/bin/chromedriver",
        "cd /root/n8n-crawling && python3 -m venv venv"
    ])
    
    print("Setting up environment...")
    for cmd in setup_commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()  # Wait for completion
    
    print("✓ Environment setup completed")
    print("Use run_crawler.py to execute crawler")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()