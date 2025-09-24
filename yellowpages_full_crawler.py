from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os

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

def crawl_companies_from_page(driver, category_name, crawled_companies=None):
    """Crawl companies from all pages, skipping already crawled ones"""
    if crawled_companies is None:
        crawled_companies = set()
    
    companies = []
    page = 1
    
    try:
        print(f"Crawling {category_name}")
        
        while True:
            print(f"  Page {page}...")
            time.sleep(3)
            
            # Find all companies and save links first
            company_links = []
            company_divs = driver.find_elements(By.CSS_SELECTOR, ".yp_noidunglistings .fs-5.pb-0.text-capitalize a")
            
            if not company_divs:
                print(f"  No companies found on page {page}")
                break
            
            for div in company_divs:
                try:
                    name = div.text.strip()
                    href = div.get_attribute('href')
                    if name and href:
                        company_links.append((name, href))
                except:
                    continue
            
            print(f"  Found {len(company_links)} companies on page {page}")
            
            for name, href in company_links:
                try:
                    # Skip if company already crawled
                    if name in crawled_companies:
                        print(f"    Skipping already crawled: {name}")
                        continue
                        
                    print(f"    Crawling: {name}")
                    company_info = extract_company_detail(driver, href, category_name)
                    if company_info:
                        companies.append(company_info)
                        print(f"    ✓ {company_info['Tên công ty']}")
                except Exception as e:
                    print(f"    ✗ Error crawling {name}: {e}")
                    continue
            
            # Try to find next page
            try:
                page_links = driver.find_elements(By.CSS_SELECTOR, "#paging > a")
                next_page_found = False
                
                for link in page_links:
                    link_text = link.text.strip()
                    # Find next page (page number greater than current page)
                    if link_text.isdigit() and int(link_text) == page + 1:
                        print(f"  Moving to page {page + 1}")
                        driver.execute_script("arguments[0].click();", link)
                        page += 1
                        next_page_found = True
                        # Wait for new page to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, ".yp_noidunglistings .fs-5.pb-0.text-capitalize a"))
                        )
                        time.sleep(3)
                        break
                
                if not next_page_found:
                    print(f"  No more pages found. Crawled {page} pages total.")
                    break
                    
            except Exception as e:
                print(f"  Error finding next page: {e}")
                break
        
        print(f"  Crawled {len(companies)} new companies from {page} pages")
        
    except Exception as e:
        print(f"  Error crawling companies: {e}")
    
    return companies

def extract_company_detail(driver, company_url, category_name):
    """Extract detailed information from company page"""
    try:
        driver.get(company_url)
        time.sleep(3)
        
        # Extract company name: Find element with class "fs-3 text-capitalize" and get its text
        name = ""
        try:
            name_element = driver.find_element(By.CSS_SELECTOR, ".fs-3.text-capitalize")
            name = name_element.text.strip()
        except:
            pass
        
        # Get all elements with class "m-0 pb-2" once for efficient processing
        elements = driver.find_elements(By.CSS_SELECTOR, ".m-0.pb-2")
        
        # Extract address: Get text from first "m-0 pb-2" element
        # Structure: <i> icon + address text + <span class="fw-semibold"> city text
        # Result: "92A-94 Bạch Đằng, Phường 2, Quận Tân Bình, TP. Hồ Chí Minh (TPHCM)"
        address = ""
        if elements:
            address_element = elements[0]
            try:
                address = address_element.text.strip()
            except:
                pass
        
        # Extract phone and hotline: Find "fw-semibold fs18" elements in second "m-0 pb-2"
        # First fw-semibold element = phone, second fw-semibold element = hotline (if exists)
        phone = ""
        hotline = ""
        if len(elements) > 1:
            phone_element = elements[1]
            try:
                fw_elements = phone_element.find_elements(By.CSS_SELECTOR, ".fw-semibold.fs18")
                if fw_elements:
                    phone = fw_elements[0].text.strip()
                if len(fw_elements) > 1:
                    hotline = fw_elements[1].text.strip()
            except:
                pass
        
        # Extract email: Find <a> tag in third "m-0 pb-2" element and get its text
        email = ""
        if len(elements) > 2:
            email_element = elements[2]
            try:
                email_link = email_element.find_element(By.CSS_SELECTOR, "a")
                email = email_link.text.strip()
            except:
                pass
        
        # Extract website: Find element with class "m-0 fs18" and get its text
        website = ""
        try:
            website_element = driver.find_element(By.CSS_SELECTOR, ".m-0.fs18")
            website = website_element.text.strip()
        except:
            pass
        
        # Extract company introduction: Find "yp_h2_border" element with text "giới thiệu công ty"
        # Then get all sibling elements after it and concatenate their text
        intro = ""
        try:
            h2_elements = driver.find_elements(By.CSS_SELECTOR, ".yp_h2_border")
            for h2 in h2_elements:
                if "giới thiệu công ty" in h2.text.lower():
                    siblings = driver.execute_script("""
                        var siblings = [];
                        var sibling = arguments[0].nextElementSibling;
                        while (sibling) {
                            siblings.push(sibling);
                            sibling = sibling.nextElementSibling;
                        }
                        return siblings;
                    """, h2)
                    intro_parts = [elem.text.strip() for elem in siblings if elem.text.strip()]
                    intro = " ".join(intro_parts)
                    break
        except:
            pass
        
        # Extract business industry: Find element with class "yp_div_nganh_thitruong" and get its text
        business = ""
        try:
            business_element = driver.find_element(By.CSS_SELECTOR, ".yp_div_nganh_thitruong")
            business = business_element.text.strip()
        except:
            pass
        
        # Extract products and services: Find elements with classes "yp_div_sanphamdichvu1" and "yp_div_sanphamdichvu2"
        # Get text from both elements and concatenate them
        products = ""
        try:
            product_texts = []
            for class_name in [".yp_div_sanphamdichvu1", ".yp_div_sanphamdichvu2"]:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, class_name)
                    product_texts.append(element.text.strip())
                except:
                    continue
            products = " ".join(product_texts)
        except:
            pass
        
        # Split category_name into main_category and sub_category
        category_parts = category_name.split(' - ', 1)
        main_category = category_parts[0] if len(category_parts) > 0 else ""
        sub_category = category_parts[1] if len(category_parts) > 1 else ""
        
        # Print company details for monitoring
        print(f"      Name: {name}")
        print(f"      Address: {address}")
        print(f"      Phone: {phone}")
        print(f"      Hotline: {hotline}")
        print(f"      Email: {email}")
        print(f"      Website: {website}")
        print(f"      Introduction: {intro[:500]}..." if len(intro) > 500 else f"      Introduction: {intro}")
        print(f"      Business: {business}")
        print(f"      Products: {products[:100]}..." if len(products) > 100 else f"      Products: {products}")
        print(f"      Category: {main_category}")
        print(f"      SubCategory: {sub_category}")
        print("      ---")
        
        return {
            "Tên công ty": name,
            "Địa chỉ": address,
            "Điện thoại": phone,
            "Hotline": hotline,
            "Email": email,
            "Website": website,
            "Giới thiệu": intro,
            "Ngành nghề": business,
            "Sản phẩm dịch vụ": products,
            "Ngành": main_category,
            "Ngành nhỏ": sub_category
        }
        
    except Exception as e:
        print(f"    Error extracting detail: {e}")
        return None

def crawl_sub_categories(driver, main_category_name, existing_metadata):
    """Crawl sub categories from class col-sm-6 p-4 pe-3 pt-0 pb-2"""
    all_companies = []
    metadata_list = []
    
    try:
        # Find sub categories and save info first
        sub_elements = driver.find_elements(By.CSS_SELECTOR, ".col-sm-6.p-4.pe-3.pt-0.pb-2 a")
        sub_data = [(elem.text.strip(), elem.get_attribute('href')) for elem in sub_elements]
        print(f"  Found {len(sub_data)} sub categories")
        
        for sub_name, sub_href in sub_data:
            try:
                print(f"    Processing sub category: {sub_name}")
                
                # Get already crawled companies for this subcategory
                crawled_companies = get_crawled_companies(existing_metadata, main_category_name, sub_name)
                
                if crawled_companies:
                    print(f"    Found {len(crawled_companies)} already crawled companies")
                
                # Click on sub category
                driver.get(sub_href)
                time.sleep(3)
                
                # Crawl companies (skip already crawled ones)
                companies = crawl_companies_from_page(
                    driver, 
                    f"{main_category_name} - {sub_name}", 
                    crawled_companies=crawled_companies
                )
                
                # Add to metadata
                for company in companies:
                    metadata_list.append({
                        "main_category": main_category_name,
                        "sub_category": sub_name,
                        "company": company["Tên công ty"]
                    })
                
                all_companies.extend(companies)
                
                # Save batch every 50 companies
                if len(all_companies) >= 50:
                    save_batch(metadata_list, all_companies)
                    metadata_list = []
                    all_companies = []
                
            except Exception as e:
                print(f"    Error crawling sub category {sub_name}: {e}")
                continue
        
        # Save remaining data
        if metadata_list or all_companies:
            save_batch(metadata_list, all_companies)
        
        return all_companies
        
    except Exception as e:
        print(f"  Error crawling sub categories: {e}")
        return all_companies

def save_batch(metadata_list, companies_list):
    """Save batch of metadata and company details to files"""
    try:
        # Save metadata
        if metadata_list:
            metadata_df = pd.DataFrame(metadata_list)
            if os.path.exists('output/metadata.xlsx'):
                existing_metadata = pd.read_excel('output/metadata.xlsx')
                metadata_df = pd.concat([existing_metadata, metadata_df], ignore_index=True)
            
            os.makedirs('output', exist_ok=True)
            metadata_df.to_excel('output/metadata.xlsx', index=False)
            print(f"  Saved {len(metadata_list)} metadata records")
        
        # Save company details - each main category as separate sheet
        if companies_list:
            companies_df = pd.DataFrame(companies_list)
            
            # Group companies by main category
            categories = companies_df['Ngành'].unique()
            
            os.makedirs('output', exist_ok=True)
            company_file = 'output/company_details.xlsx'
            
            # Load existing data if file exists
            existing_sheets = {}
            if os.path.exists(company_file):
                try:
                    with pd.ExcelFile(company_file) as xls:
                        for sheet_name in xls.sheet_names:
                            existing_sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
                except Exception as e:
                    print(f"  Warning: Could not read existing file: {e}")
            
            # Prepare data for each category
            with pd.ExcelWriter(company_file, engine='openpyxl', mode='w') as writer:
                # Write existing sheets first
                for sheet_name, df in existing_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Add new data for each category
                for category in categories:
                    category_companies = companies_df[companies_df['Ngành'] == category]
                    
                    # Clean sheet name (Excel sheet names have restrictions)
                    sheet_name = category.replace('/', '_').replace('\\', '_').replace('*', '_').replace('?', '_').replace(':', '_').replace('[', '_').replace(']', '_')[:31]
                    
                    if sheet_name in existing_sheets:
                        # Append to existing sheet data
                        combined_df = pd.concat([existing_sheets[sheet_name], category_companies], ignore_index=True)
                        combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"  Updated sheet '{sheet_name}' with {len(category_companies)} companies")
                    else:
                        # Create new sheet
                        category_companies.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"  Created new sheet '{sheet_name}' with {len(category_companies)} companies")
            
            print(f"  Saved {len(companies_list)} company details across {len(categories)} categories")
            
    except Exception as e:
        print(f"  Error saving batch: {e}")

def load_progress():
    """Load existing metadata to determine crawling progress"""
    try:
        if os.path.exists('output/metadata.xlsx'):
            metadata_df = pd.read_excel('output/metadata.xlsx')
            return metadata_df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading progress: {e}")
        return pd.DataFrame()

def get_crawled_companies(existing_metadata, main_category, sub_category):
    """Get set of already crawled companies for a specific main_category and sub_category"""
    if existing_metadata.empty:
        return set()
    
    subcategory_data = existing_metadata[
        (existing_metadata['main_category'] == main_category) & 
        (existing_metadata['sub_category'] == sub_category)
    ]
    
    return set(subcategory_data['company'].tolist()) if not subcategory_data.empty else set()

def crawl_main_categories(driver):
    """Crawl all main categories from yellowpages.vn homepage"""
    # Load existing progress
    existing_metadata = load_progress()
    
    if not existing_metadata.empty:
        print(f"Found existing progress: {len(existing_metadata)} records")
        print(f"Categories in progress: {existing_metadata['main_category'].nunique()}")
    
    try:
        driver.get("https://www.yellowpages.vn/")
        time.sleep(5)
        
        # Get all main categories and save info first
        main_elements = driver.find_elements(By.CSS_SELECTOR, ".p-2.ps-1 a.text-dark")
        main_data = [(elem.text.strip(), elem.get_attribute('href')) for elem in main_elements]
        print(f"Found {len(main_data)} main categories")
        
        for i, (category_name, category_href) in enumerate(main_data):
            try:
                print(f"\n[{i+1}/{len(main_data)}] Processing category: {category_name}")
                
                # Click on main category
                driver.get(category_href)
                time.sleep(3)
                
                # Crawl sub categories (with resume logic inside)
                crawl_sub_categories(driver, category_name, existing_metadata)
                
                # Reload metadata after each main category to get updated progress
                existing_metadata = load_progress()
                
            except Exception as e:
                print(f"Error crawling category {category_name}: {e}")
                continue
        
        print("\nCrawling completed!")
        
    except Exception as e:
        print(f"Error crawling main categories: {e}")

def main():
    """Main function to run crawler"""
    driver = setup_driver()
    
    try:
        # Crawl all main categories with resume capability
        crawl_main_categories(driver)
            
    except Exception as e:
        print(f"Error during crawling: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()