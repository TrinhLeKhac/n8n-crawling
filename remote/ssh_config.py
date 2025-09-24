#!/usr/bin/env python3
"""
SSH Connection Helper for Remote Server
"""

import paramiko
import os
import sys

class SSHConnection:
    def __init__(self, hostname, username, password=None, key_path=None, port=22):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_path = key_path
        self.port = port
        self.client = None
        
    def connect(self):
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_path and os.path.exists(self.key_path):
                # Connect using SSH key
                self.client.connect(
                    hostname=self.hostname,
                    username=self.username,
                    key_filename=self.key_path,
                    port=self.port
                )
            else:
                # Connect using password
                self.client.connect(
                    hostname=self.hostname,
                    username=self.username,
                    password=self.password,
                    port=self.port
                )
            print(f"✓ Connected to {self.hostname}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def execute_command(self, command):
        """Execute command on remote server"""
        if not self.client:
            print("Not connected to server")
            return None
            
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error:
                print(f"Error: {error}")
            return output
        except Exception as e:
            print(f"Command execution failed: {e}")
            return None
    
    def upload_file(self, local_path, remote_path):
        """Upload file to remote server"""
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"✓ Uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            print(f"✗ Upload failed: {e}")
            return False
    
    def download_file(self, remote_path, local_path):
        """Download file from remote server"""
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            print(f"✓ Downloaded {remote_path} to {local_path}")
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False
    
    def close(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            print("Connection closed")

# Example usage
if __name__ == "__main__":
    # Replace with your server details
    ssh = SSHConnection(
        hostname="YOUR_SERVER_IP",
        username="YOUR_USERNAME", 
        password="YOUR_PASSWORD",  # or use key_path="/path/to/private/key"
        port=22
    )
    
    if ssh.connect():
        # Test connection
        result = ssh.execute_command("pwd && ls -la")
        print(result)
        ssh.close()