#!/usr/bin/env python3
import paramiko
from pathlib import Path

# Thông tin server
HOST = input("Server IP: ")
USERNAME = input("Username: ")
PASSWORD = input("Password: ")
PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, PORT, USERNAME, PASSWORD)
    print(f"✓ Đã kết nối tới {HOST}")
    
    # Kiểm tra và tạo folder n8n-crawling nếu chưa có
    stdin, stdout, stderr = ssh.exec_command("ls -la /root/n8n-crawling")
    if stderr.read().decode():
        print("Tạo folder n8n-crawling...")
        ssh.exec_command("mkdir -p /root/n8n-crawling/output")
    else:
        print("Folder n8n-crawling đã tồn tại")
    
    # Cài đặt môi trường
    setup_commands = [
        "apt update",
        "apt install -y python3-pip",
        "pip3 install selenium pandas openpyxl",
        "apt install -y wget unzip",
        "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -",
        "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list",
        "apt update",
        "apt install -y google-chrome-stable",
        "wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip",
        "unzip /tmp/chromedriver.zip -d /usr/local/bin/",
        "chmod +x /usr/local/bin/chromedriver"
    ]
    
    print("Đang cài đặt môi trường...")
    for cmd in setup_commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()  # Wait for completion
    
    print("✓ Đã cài xong môi trường")
    print("Sử dụng run_crawler.py để chạy crawler")
    
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    ssh.close()