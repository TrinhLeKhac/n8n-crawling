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
    
    # Run crawler on remote server (assumes folder exists from Git)
    stdin, stdout, stderr = ssh.exec_command("cd /root/n8n-crawling && python3 yellowpages_full_crawler.py")
    
    # Display real-time output
    for line in stdout:
        print(line.strip())
    
    # Download results
    try:
        sftp = ssh.open_sftp()
        current_dir = Path(__file__).parent
        
        # Download both files
        files = ["company_details.xlsx", "metadata.xlsx"]
        for file in files:
            remote_path = f"/root/n8n-crawling/output/{file}"
            local_path = current_dir.parent / "output" / file
            sftp.get(remote_path, str(local_path))
            print(f"✓ Downloaded {file}")
        
        sftp.close()
    except Exception as e:
        print(f"Download error: {e}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()