#!/usr/bin/env python3
import paramiko
from pathlib import Path

# Import config (tạo file config.py từ config_template.py)
try:
    from config import SERVER_CONFIG
except ImportError:
    print("Tạo file config.py từ config_template.py và điền thông tin server")
    exit(1)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(**SERVER_CONFIG)
    print(f"✓ Đã kết nối tới {SERVER_CONFIG['HOST']}")
    
    # Setup và chạy
    commands = [
        "cd /root/n8n-crawling",
        "apt update && apt install -y python3-pip google-chrome-stable",
        "pip3 install selenium pandas openpyxl",
        "python3 yellowpages_full_crawler.py"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        for line in stdout:
            print(line.strip())
    
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    ssh.close()