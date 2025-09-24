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
    
    # Chạy crawler trên remote (giả định đã có folder từ Git)
    stdin, stdout, stderr = ssh.exec_command("cd /root/n8n-crawling && python3 yellowpages_full_crawler.py")
    
    # Hiển thị output real-time
    for line in stdout:
        print(line.strip())
    
    # Download kết quả
    try:
        sftp = ssh.open_sftp()
        current_dir = Path(__file__).parent
        output_path = current_dir.parent / "output" / "company_details.xlsx"
        sftp.get("/root/n8n-crawling/output/company_details.xlsx", str(output_path))
        sftp.close()
        print("✓ Đã download kết quả")
    except Exception as e:
        print(f"Lỗi download: {e}")
    
except Exception as e:
    print(f"Lỗi: {e}")
finally:
    ssh.close()