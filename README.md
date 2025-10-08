# YellowPages Vietnam Crawler

A comprehensive web crawler for extracting company information from yellowpages.vn with resume capability and background execution.

## Project Structure

```
n8n-crawling/
├── scan_metadata.py              # Initial metadata scanner (run once to generate categories_metadata.xlsx)
├── crawl_by_metadata.py          # Main crawler script
├── run_crawler.sh                # Background execution wrapper
├── monitor.sh                    # System monitoring script
├── com.crawler.yellowpages.plist # macOS LaunchAgent service file
├── requirements.txt              # Python dependencies
├── venv/                         # Virtual environment
│   ├── bin/activate              # Virtual environment activation
│   └── lib/python3.10/           # Python packages
├── output/                       # Crawler output directory
│   ├── categories_metadata.xlsx  # Input: Category metadata (main_category, sub_category, number_website)
│   ├── metadata_crawled.xlsx     # Progress: Crawling progress tracking (main_category, sub_category, number_company_crawled)
│   └── *_company_details.xlsx    # Output: Company data by category (do_gia_dung_company_details.xlsx, bep_gas_company_details.xlsx, etc.)
├── crawler.log                   # Real-time output logs
├── crawler.error.log            # Error logs
├── crawler.pid                   # Process ID file (for stopping background crawler)
└── README.md                     # This documentation
```

## Crawling Logic Flow

### 0. **Initial Setup (Run Once)**
```
Run scan_metadata.py → Scan yellowpages.vn → Extract all categories & subcategories
                     ↓
Count companies in each subcategory → Generate categories_metadata.xlsx
                     ↓
This file becomes input for main crawler (defines crawling targets & stop points)
```

### 1. **Initialization & Resume Detection**
```
Start → Load categories_metadata.xlsx → Check metadata_crawled.xlsx
                                      ↓
Find last crawled position → Jump to resume position (skip completed subcategories)
                           ↓
Start crawling from exact position (no scanning from beginning)
```

### 2. **Category Navigation Flow**
```
yellowpages.vn homepage
        ↓
Find main category link (.p-2.ps-1 a.text-dark)
        ↓
Navigate to main category page
        ↓
Find subcategory link (.col-sm-6.p-4.pe-3.pt-0.pb-2 a)
        ↓
Navigate to subcategory listing page
```

### 3. **Company Extraction Flow**
```
Subcategory page → Extract companies (.rounded-4.border.bg-white.shadow-sm.mb-3.pb-4)
                ↓
Get company name & URL (.yp_noidunglistings .fs-5.pb-0.text-capitalize a)
                ↓
Get order number (.yp_sothutu .yp_sothutu_txt small)
                ↓
Visit company detail page → Extract all information → Return to subcategory page
                ↓
Next company → Repeat until page complete
                ↓
Next page (?page=2, ?page=3...) → Repeat until subcategory complete
                ↓
Next subcategory → Repeat until all categories complete
```

### 4. **Data Extraction Details**
For each company detail page, extract:
- **Name**: `.fs-3.text-capitalize`
- **Address**: First `.m-0.pb-2` element
- **Phone/Hotline**: `.fw-semibold.fs18` elements
- **Email**: `<a>` tag in contact section
- **Website**: `.m-0.fs18` element
- **Introduction**: Siblings of `.yp_h2_border` containing "giới thiệu công ty"
- **Business**: `.yp_div_nganh_thitruong` element
- **Products**: `.yp_div_sanphamdichvu1` + `.yp_div_sanphamdichvu2` elements

### 5. **Progress Tracking & Data Persistence**
```
Every 10 companies crawled:
    ↓
Update metadata_crawled.xlsx (progress tracking)
    ↓
Save to category-specific Excel file (do_gia_dung_company_details.xlsx)
    ↓
Continue crawling...
```

## Features

- **Smart Resume**: Automatically resumes from last crawled position
- **Background Execution**: Runs continuously with auto-restart
- **Progress Tracking**: Real-time progress monitoring and logging
- **Anti-Sleep**: Prevents system sleep during crawling (`caffeinate`)
- **Batch Processing**: Saves data every 10 companies
- **Detailed Extraction**: Company name, address, phone, email, website, introduction, business info, products/services
- **Unbuffered Output**: Real-time log viewing with `python -u`
- **Anti-Detection**: Chrome options to avoid bot detection
- **Duplicate Prevention**: Skips already crawled companies

## Data Structure

### Input File: categories_metadata.xlsx
| Column | Description | Example |
|--------|-------------|---------|
| main_category | Primary business category | Đồ Gia Dụng |
| sub_category | Specific industry subcategory | Đồ Gia Dụng - Sản Xuất và Bán Buôn |
| number_website | Total companies in subcategory | 299 |

### Progress File: metadata_crawled.xlsx
| Column | Description | Example |
|--------|-------------|---------|
| main_category | Primary business category | Đồ Gia Dụng |
| sub_category | Specific industry subcategory | Đồ Gia Dụng - Sản Xuất và Bán Buôn |
| number_company_crawled | Companies already crawled | 252 |

### Output Files: *_company_details.xlsx
| Column | Description | Example |
|--------|-------------|---------|
| Tên công ty | Company name | Công Ty TNHH ABC |
| Địa chỉ | Full address | 123 Nguyễn Văn Cừ, Quận 1, TP.HCM |
| Điện thoại | Primary phone number | 028.1234.5678 |
| Hotline | Secondary phone/hotline | 0901.234.567 |
| Email | Contact email | info@abc.com |
| Website | Company website | www.abc.com |
| Giới thiệu | Company introduction | Công ty chuyên sản xuất... |
| Ngành nghề | Business industry | Sản xuất đồ gia dụng |
| Sản phẩm dịch vụ | Products and services | Nồi, chảo, bếp gas... |
| Ngành | Category classification | Đồ Gia Dụng |

## Quick Start

### Prerequisites
- Python 3.10+
- Chrome browser
- Virtual environment

### Installation

1. **Setup virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

2. **Make scripts executable**
```bash
chmod +x run_crawler.sh
chmod +x monitor.sh
```

3. **Generate initial metadata (run once)**
```bash
# Scan yellowpages.vn to generate categories_metadata.xlsx
python scan_metadata.py

# This creates output/categories_metadata.xlsx with:
# - All main categories and subcategories
# - Company count for each subcategory
# - Crawling targets and stop points
```

### Running the Crawler

#### Option 1: Background execution (Recommended)
```bash
# Run in background with auto-restart
nohup ./run_crawler.sh > crawler.log 2>&1 &

# Save PID for later stopping
echo $! > crawler.pid
```

#### Option 2: Direct execution
```bash
# Run directly (terminal must stay open)
./run_crawler.sh
```

## Monitoring and Control

### Real-time Log Viewing
```bash
# View live crawler output
tail -f crawler.log

# View error logs
tail -f crawler.error.log
```

### System Monitoring
```bash
# Check crawler status and system health
./monitor.sh

# Check running processes
ps aux | grep crawl

# Check memory usage
ps aux | grep python | head -5
```

**monitor.sh output example:**
```
=== Crawler Status ===
Time: Wed Dec 13 10:30:45 PST 2023

✅ Crawler is running
PID: 12345

🌡️  CPU Temperature: 45°C
💾 Memory usage:
12345  2.5  1.2  python crawl_by_metadata.py

📈 Latest progress:
Updated progress: Đồ Gia Dụng - Bếp Gas: 45 companies

📝 Log tail:
[16/100] Processing: Đồ Gia Dụng - Bếp Gas...
    Page 2... (45/140)
    ✓ Thiết Bị Bếp ABC (46/140)
```

### Stopping the Crawler
```bash
# Stop background crawler
kill $(cat crawler.pid)

# Or force stop all crawler processes
pkill -f "run_crawler.sh"
```

## Configuration

### Chrome Options
```python
chrome_options.add_argument("--headless")           # Run headless
chrome_options.add_argument("--no-sandbox")         # Security
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
```

### Background Script Features
- **Auto-restart**: Restarts crawler if it crashes
- **Sleep prevention**: Uses `caffeinate` to prevent system sleep
- **Virtual environment**: Automatically activates venv
- **Unbuffered output**: Uses `python -u` for real-time logs

## Output Files

### Progress Tracking
The crawler prints detailed progress information:
```
Last progress: Đồ Gia Dụng - Đồ Gia Dụng - Sản Xuất và Bán Buôn: 252 companies
Starting from position 15/100
[16/100] Processing: Đồ Gia Dụng - Bếp Gas...
    Page 1... (0/140)
    Found 45 listing containers in div_listing
      Found #1: Thiết Bị Bếp Thuận Long
      Crawling #1: Thiết Bị Bếp Thuận Long
      ✓ Thiết Bị Bếp Thuận Long (1/140)
```

### Sample Output
```
Scanning yellowpages.vn categories...
Found 25 main categories
[1/25] Scanning: Đồ Gia Dụng
  Found 8 subcategories
    Bếp Gas (Đơn, Đôi, Hồng Ngoại, Âm): 140 companies
    Đồ Gia Dụng - Sản Xuất và Bán Buôn: 299 companies
    Nồi, Chảo Chống Dính: 89 companies
    ...
Saved metadata to output/categories_metadata.xlsx
Total: 1,247 subcategories with 45,892 companies
```

## Troubleshooting

### Common Issues

1. **Multiple crawlers running**
```bash
# Check for duplicate processes
ps aux | grep crawl

# Kill old processes
pkill -f "run_crawler.sh"
```

2. **Permission denied (macOS Desktop)**
```bash
# Move project out of Desktop folder
mv ~/Desktop/Others/n8n-crawling ~/n8n-crawling
cd ~/n8n-crawling
```

3. **Virtual environment not found**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Chrome driver issues**
```bash
# Install/update Chrome
brew install --cask google-chrome

# Install ChromeDriver
brew install chromedriver
```

5. **Resume not working**
- Check if `metadata_crawled.xlsx` exists in output directory
- Verify file permissions: `chmod 644 output/*.xlsx`
- Check for corrupted Excel files

### Performance Tips

1. **Monitor system resources**
```bash
# Check CPU and memory usage
top -pid $(pgrep -f crawl_by_metadata.py)

# Check disk space
df -h
```

2. **Optimize for overnight runs**
```bash
# Prevent display sleep but allow system optimization
pmset displaysleep 10

# Close unnecessary applications
# Ensure stable internet connection
```

## Advanced Usage

### Unbuffered Output Explained
- **`python -u`**: Forces unbuffered stdout/stderr
- **Benefit**: See logs in real-time instead of waiting for buffer flush
- **Usage**: Essential for monitoring long-running crawlers

### Background Execution with nohup
```bash
# Standard background execution
nohup ./run_crawler.sh > crawler.log 2>&1 &

# Explanation:
# nohup: Ignore hangup signals (survives terminal close)
# > crawler.log: Redirect stdout to file
# 2>&1: Redirect stderr to stdout (combine logs)
# &: Run in background
```

### System Sleep Prevention
The `run_crawler.sh` script uses `caffeinate -i` to prevent system sleep while allowing display sleep for energy efficiency.

### Resume Capability
The crawler automatically:
1. Reads last progress from `metadata_crawled.xlsx`
2. Finds corresponding position in `categories_metadata.xlsx`
3. Resumes crawling from that exact subcategory
4. Skips already crawled companies using existing Excel files