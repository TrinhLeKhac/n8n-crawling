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
- Installs Python3, pip, venv, Chrome, ChromeDriver
- Creates virtual environment in `/root/n8n-crawling/venv`

### 2. Deploy Code
```bash
python3 update_code.py
```
- Pulls latest code from GitHub repository
- Activates virtual environment
- Installs/updates requirements from `requirements.txt`

### 3. Run Crawler
```bash
python3 run_crawler.py
```
- Activates virtual environment
- Executes `yellowpages_full_crawler.py` on remote server
- Shows real-time output
- Downloads both result files:
  - `company_details.xlsx`
  - `metadata.xlsx`


## Server Structure

After setup, the remote server will have:
```
/root/n8n-crawling/
├── venv/                          # Virtual environment
├── yellowpages_full_crawler.py
├── requirements.txt
├── output/
│   ├── company_details.xlsx
│   └── metadata.xlsx
└── ... (other project files)
```