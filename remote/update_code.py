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
    
    # Pull latest code from Git
    git_commands = [
        "apt update && apt install -y git",
        "cd /root/n8n-crawling && git pull origin main",
        "cd /root/n8n-crawling && pip3 install -r requirements.txt"
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