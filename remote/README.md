# Remote Deployment Scripts

This folder contains scripts for deploying and running the YellowPages crawler on remote servers via SSH.

## Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `setup_env.py` | Setup environment (Python, Chrome, dependencies) | First time setup on new server |
| `update_code.py` | Pull latest code from Git + install requirements | Update code from repository |
| `run_crawler.py` | Execute crawler + download results | Run crawler and get output files |

## Usage Workflow

### 1. First Time Setup
```bash
python3 setup_env.py
```
- Creates `/root/n8n-crawling` folder if not exists
- Installs Python3, pip, Chrome, ChromeDriver
- Installs Python packages (selenium, pandas, openpyxl)

### 2. Deploy Code
```bash
python3 update_code.py
```
- Pulls latest code from GitHub repository
- Installs/updates requirements from `requirements.txt`

### 3. Run Crawler
```bash
python3 run_crawler.py
```
- Executes `yellowpages_full_crawler.py` on remote server
- Shows real-time output
- Downloads both result files:
  - `company_details.xlsx`
  - `metadata.xlsx`

## Complete Setup Process

For a brand new server:

1. **Environment Setup** (one time only)
   ```bash
   python3 setup_env.py
   ```

2. **Get Code** (first time or when updating)
   ```bash
   python3 update_code.py
   ```

3. **Run Crawler** (anytime you want to crawl)
   ```bash
   python3 run_crawler.py
   ```

## Subsequent Runs

After initial setup:

- **Update code**: `python3 update_code.py`
- **Run crawler**: `python3 run_crawler.py`

## Requirements

- Remote server with SSH access
- Ubuntu/Debian-based Linux server
- Root or sudo access
- Internet connection for package installation

## Server Structure

After setup, the remote server will have:
```
/root/n8n-crawling/
├── yellowpages_full_crawler.py
├── requirements.txt
├── output/
│   ├── company_details.xlsx
│   └── metadata.xlsx
└── ... (other project files)
```

## Troubleshooting

- **Connection failed**: Check server IP, username, password
- **Permission denied**: Ensure user has sudo/root access
- **Chrome installation failed**: Server might need different Chrome version
- **Download failed**: Check if crawler completed successfully and output files exist