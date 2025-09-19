# YellowPages Vietnam Crawler with n8n

A comprehensive web crawler for extracting company information from yellowpages.vn, integrated with n8n workflow automation and PostgreSQL database.

## Project Structure

```
n8n/
├── yellowpages_full_crawler.py    # Main crawler script
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image configuration
├── docker-compose.yml            # Services orchestration
├── build.sh                      # Build and deployment script
├── output/                       # Crawler output directory
│   ├── metadata.xlsx             # Category and company mapping
│   └── company_details.xlsx      # Detailed company information
└── README.md                     # This file
```

## Features

- **Hierarchical Crawling**: Main categories → Sub categories → Companies
- **Resume Capability**: Automatically resumes from last crawled category
- **Batch Processing**: Saves data every 50 companies
- **Detailed Extraction**: Company name, address, phone, email, website, introduction, business info, products/services
- **Docker Integration**: Containerized with n8n and PostgreSQL
- **Anti-Detection**: Chrome options to avoid bot detection

## Data Structure

### Metadata File (metadata.xlsx)
| Column | Description |
|--------|-------------|
| main_category | Primary business category |
| sub_category | Specific industry subcategory |
| company | Company name |

### Company Details File (company_details.xlsx)
| Column | Description |
|--------|-------------|
| Tên công ty | Company name |
| Địa chỉ | Full address |
| Điện thoại | Primary phone number |
| Hotline | Secondary phone/hotline |
| Email | Contact email |
| Website | Company website |
| Giới thiệu | Company introduction |
| Ngành nghề | Business industry |
| Sản phẩm dịch vụ | Products and services |
| Ngành | Category classification |

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone and navigate to project**
```bash
git clone <repository>
cd n8n
```

2. **Build and start services**
```bash
./build.sh
```

Or manually:
```bash
docker build -t trinhlk2:n8n-crawling .
docker-compose up -d
```

3. **Access services**
- n8n: http://localhost:5678
- PostgreSQL: localhost:5432 (postgres/postgres)

### Running the Crawler

#### Option 1: Direct Python execution
```bash
python yellowpages_full_crawler.py
```

#### Option 2: Inside Docker container
```bash
docker-compose exec n8n python /app/yellowpages_full_crawler.py
```

#### Option 3: Via n8n workflow
1. Access n8n at http://localhost:5678
2. Create workflow with Execute Command node
3. Command: `python /app/yellowpages_full_crawler.py`

## Configuration

### Crawler Settings
Edit `yellowpages_full_crawler.py`:
```python
max_companies=5  # Companies per subcategory
time.sleep(3)    # Delay between requests
```

### Chrome Options
```python
chrome_options.add_argument("--headless")  # Run headless
chrome_options.add_argument("--no-sandbox")  # Docker compatibility
```

### Database Connection
PostgreSQL connection details in `docker-compose.yml`:
```yaml
environment:
  - DB_TYPE=postgresdb
  - DB_POSTGRESDB_HOST=postgres
  - DB_POSTGRESDB_DATABASE=n8n
  - DB_POSTGRESDB_USER=postgres
  - DB_POSTGRESDB_PASSWORD=postgres
```

## How It Works

### 1. Main Category Discovery
- Visits yellowpages.vn homepage
- Extracts all main categories from `.p-2.ps-1 a.text-dark` elements
- Skips already crawled categories (resume capability)

### 2. Sub Category Extraction
- For each main category, finds sub categories
- Uses `.col-sm-6.p-4.pe-3.pt-0.pb-2 a` selector
- Extracts category name and URL

### 3. Company List Crawling
- Navigates to each sub category page
- Finds company links via `.yp_noidunglistings .fs-5.pb-0.text-capitalize a`
- Collects company names and detail page URLs

### 4. Detailed Information Extraction
- Visits each company's detail page
- Extracts comprehensive information:
  - **Name**: `.fs-3.text-capitalize`
  - **Address**: First `.m-0.pb-2` element (includes icon + address + city)
  - **Phone/Hotline**: `.fw-semibold.fs18` elements in second `.m-0.pb-2`
  - **Email**: `<a>` tag in third `.m-0.pb-2`
  - **Website**: `.m-0.fs18` element
  - **Introduction**: Siblings of `.yp_h2_border` containing "giới thiệu công ty"
  - **Business**: `.yp_div_nganh_thitruong` element
  - **Products**: `.yp_div_sanphamdichvu1` + `.yp_div_sanphamdichvu2` elements

### 5. Data Persistence
- Saves metadata and company details every 50 records
- Appends to existing Excel files
- Maintains crawling progress for resume capability

## Monitoring and Debugging

### View Logs
```bash
docker-compose logs -f n8n
```

### Check Output Files
```bash
ls -la output/
```

### Monitor Progress
The crawler prints detailed progress information:
```
Found 25 main categories
[1/25] Crawling category: An Ninh - Bảo Vệ
  Found 8 sub categories
    Crawling sub category: Bảo vệ
      Found 12 companies
        Crawling: CÔNG TY TNHH BẢO VỆ ABC
          Name: CÔNG TY TNHH BẢO VỆ ABC
          Address: 123 Nguyễn Văn Cừ, Quận 1, TP. HCM
          Phone: 028.1234.5678
          ...
```

## Troubleshooting

### Common Issues

1. **Chrome not found**
```bash
# Install Chrome in container
docker-compose exec n8n apk add chromium chromium-chromedriver
```

2. **Permission denied**
```bash
# Fix file permissions
sudo chown -R $USER:$USER output/
```

3. **Memory issues**
```bash
# Increase shared memory
docker-compose down
# Edit docker-compose.yml: shm_size: 4gb
docker-compose up -d
```

4. **Resume not working**
- Check if `metadata.xlsx` exists in output directory
- Verify file permissions
- Check for corrupted Excel files

### Performance Optimization

1. **Increase batch size**
```python
if len(all_companies) >= 100:  # Instead of 50
```

2. **Reduce delays**
```python
time.sleep(1)  # Instead of 3
```

3. **Parallel processing**
- Run multiple containers with different category ranges
- Use threading for company detail extraction

### Database Integration
To save directly to PostgreSQL instead of Excel:
1. Install psycopg2: `pip install psycopg2-binary`
2. Replace `save_batch()` function with database operations
3. Create appropriate database tables