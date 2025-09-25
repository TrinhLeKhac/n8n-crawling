# Remote Deployment Scripts

This folder contains scripts for deploying and running the YellowPages crawler on remote servers via SSH.

## Files Overview

| File | Purpose | When to Use |
|------|---------|-------------|
| `setup_env.py` | Setup environment (Python, Chrome, dependencies) | First time setup on new server |
| `update_code.py` | Clone/pull code from Git + install requirements | Get code (first time or update) |
| `run_crawler.py` | Execute crawler + download results | Run crawler and get output files |

## Usage Workflow

### 1. Get Code (First Time or Update)
```bash
python3 update_code.py
```
- Installs Git
- Clones repository (first time) or pulls updates
- Activates virtual environment
- Installs/updates requirements from `requirements.txt`

### 2. Setup Environment (First Time Only)
```bash
python3 setup_env.py
```
- Creates `/root/n8n-crawling` folder if not exists
- Installs Python3, pip, venv, Chrome, ChromeDriver
- Creates virtual environment in `/root/n8n-crawling/venv`

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

## Complete Setup Process

For a brand new server:

1. `python3 update_code.py` - Get code
2. `python3 setup_env.py` - Setup environment  
3. `python3 run_crawler.py` - Run crawler

For subsequent runs:
- Update: `python3 update_code.py`
- Run: `python3 run_crawler.py`


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