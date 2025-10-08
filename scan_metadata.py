from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import unicodedata

def setup_driver():
    """Setup Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_website_count(sub_name):
    """Extract number of websites from subcategory name like 'Bếp Gas (140)'"""
    match = re.search(r'\((\d+)\)$', sub_name)
    if match:
        return int(match.group(1)), re.sub(r'\s*\(\d+\)$', '', sub_name)
    return 0, sub_name

def scan_categories_metadata(driver):
    """Scan all categories and subcategories to create metadata"""
    metadata_list = []
    
    try:
        driver.get("https://www.yellowpages.vn/")
        time.sleep(5)
        
        # Get all main categories
        main_elements = driver.find_elements(By.CSS_SELECTOR, ".p-2.ps-1 a.text-dark")
        main_data = [(elem.text.strip(), elem.get_attribute('href')) for elem in main_elements]
        print(f"Found {len(main_data)} main categories")
        
        for i, (main_category, main_href) in enumerate(main_data):
            try:
                print(f"\n[{i+1}/{len(main_data)}] Scanning: {main_category}")
                
                # Navigate to main category
                driver.get(main_href)
                time.sleep(3)
                
                # Get subcategories
                sub_elements = driver.find_elements(By.CSS_SELECTOR, ".col-sm-6.p-4.pe-3.pt-0.pb-2 a")
                
                for sub_element in sub_elements:
                    try:
                        sub_name_raw = sub_element.text.strip()
                        website_count, sub_name_clean = extract_website_count(sub_name_raw)
                        
                        print(f"  - {sub_name_clean}: {website_count} websites")
                        
                        metadata_list.append({
                            "main_category": main_category,
                            "sub_category": sub_name_clean,
                            "number_website": website_count
                        })
                        
                    except Exception as e:
                        print(f"  Error processing subcategory: {e}")
                        continue
                
            except Exception as e:
                print(f"Error scanning category {main_category}: {e}")
                continue
        
        # Save metadata
        metadata_df = pd.DataFrame(metadata_list)
        metadata_df.to_excel('output/categories_metadata.xlsx', index=False)
        print(f"\nSaved metadata for {len(metadata_list)} subcategories to output/categories_metadata.xlsx")
        
    except Exception as e:
        print(f"Error scanning categories: {e}")

def main():
    """Main function"""
    import os
    os.makedirs('output', exist_ok=True)
    
    driver = setup_driver()
    try:
        scan_categories_metadata(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()