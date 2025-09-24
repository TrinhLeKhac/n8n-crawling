#!/usr/bin/env python3
"""
Remote Server Setup for n8n Crawler Project
"""

from ssh_config import SSHConnection
import os

def setup_remote_environment(ssh):
    """Setup Python environment on remote server"""
    commands = [
        # Update system
        "sudo apt update",
        
        # Install Python and pip
        "sudo apt install -y python3 python3-pip",
        
        # Install Chrome for Selenium
        "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list",
        "sudo apt update",
        "sudo apt install -y google-chrome-stable",
        
        # Install ChromeDriver
        "sudo apt install -y chromium-chromedriver",
        
        # Create project directory
        "mkdir -p ~/n8n-crawling",
        "cd ~/n8n-crawling && mkdir -p output"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        result = ssh.execute_command(cmd)
        if result:
            print(result)

def deploy_crawler(ssh):
    """Deploy crawler files to remote server"""
    local_files = [
        "yellowpages_full_crawler.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile"
    ]
    
    for file in local_files:
        if os.path.exists(file):
            ssh.upload_file(file, f"~/n8n-crawling/{file}")
    
    # Install Python dependencies
    ssh.execute_command("cd ~/n8n-crawling && pip3 install -r requirements.txt")

def run_crawler_remote(ssh):
    """Run crawler on remote server"""
    commands = [
        "cd ~/n8n-crawling",
        "python3 yellowpages_full_crawler.py"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        result = ssh.execute_command(cmd)
        print(result)

if __name__ == "__main__":
    # Configure your server details here
    SERVER_CONFIG = {
        "hostname": input("Server IP: "),
        "username": input("Username: "),
        "password": input("Password: "),  # or use key_path
        "port": 22
    }
    
    ssh = SSHConnection(**SERVER_CONFIG)
    
    if ssh.connect():
        choice = input("Choose action:\n1. Setup environment\n2. Deploy crawler\n3. Run crawler\n4. All\nChoice: ")
        
        if choice in ["1", "4"]:
            setup_remote_environment(ssh)
        if choice in ["2", "4"]:
            deploy_crawler(ssh)
        if choice in ["3", "4"]:
            run_crawler_remote(ssh)
            
        ssh.close()