from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import os
import unicodedata
import re

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

def normalize_filename(text):
    """Convert Vietnamese text to ASCII filename"""
    # Remove accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Replace spaces and special chars with underscore
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text.lower()

def extract_company_detail(driver, company_url, category_name):
    """Extract detailed information from company page"""
    try:
        driver.get(company_url)
        time.sleep(3)
        
        name = ""
        try:
            name_element = driver.find_element(By.CSS_SELECTOR, ".fs-3.text-capitalize")
            name = name_element.text.strip()
        except:
            pass
        
        elements = driver.find_elements(By.CSS_SELECTOR, ".m-0.pb-2")
        
        address = ""
        if elements:
            try:
                address = elements[0].text.strip()
            except:
                pass
        
        phone = ""
        hotline = ""
        if len(elements) > 1:
            try:
                fw_elements = elements[1].find_elements(By.CSS_SELECTOR, ".fw-semibold.fs18")
                if fw_elements:
                    phone = fw_elements[0].text.strip()
                if len(fw_elements) > 1:
                    hotline = fw_elements[1].text.strip()
            except:
                pass
        
        email = ""
        if len(elements) > 2:
            try:
                email_link = elements[2].find_element(By.CSS_SELECTOR, "a")
                email = email_link.text.strip()
            except:
                pass
        
        website = ""
        try:
            website_element = driver.find_element(By.CSS_SELECTOR, ".m-0.fs18")
            website = website_element.text.strip()
        except:
            pass
        
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
        
        business = ""
        try:
            business_element = driver.find_element(By.CSS_SELECTOR, ".yp_div_nganh_thitruong")
            business = business_element.text.strip()
        except:
            pass
        
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
        
        category_parts = category_name.split(' - ', 1)
        main_category = category_parts[0] if len(category_parts) > 0 else ""
        sub_category = category_parts[1] if len(category_parts) > 1 else ""
        
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

def get_existing_companies(main_category):
    """Get existing companies from file to avoid duplicates"""
    filename = normalize_filename(main_category)
    filepath = f'output/{filename}_company_details.xlsx'
    
    existing_companies = set()
    if os.path.exists(filepath):
        try:
            df = pd.read_excel(filepath)
            existing_companies = set(df['Tên công ty'].tolist())
            print(f"  Found {len(existing_companies)} existing companies in {filepath}")
        except Exception as e:
            print(f"  Error reading existing file: {e}")
    
    return existing_companies

def get_crawled_progress():
    """Load crawled progress metadata"""
    try:
        if os.path.exists('output/metadata_crawled.xlsx'):
            return pd.read_excel('output/metadata_crawled.xlsx')
        return pd.DataFrame(columns=['main_category', 'sub_category', 'number_company_crawled'])
    except Exception as e:
        print(f"Error loading crawled progress: {e}")
        return pd.DataFrame(columns=['main_category', 'sub_category', 'number_company_crawled'])

def update_crawled_progress(main_category, sub_category, crawled_count):
    """Update crawled progress metadata"""
    try:
        progress_df = get_crawled_progress()
        
        # Update or add record
        mask = (progress_df['main_category'] == main_category) & (progress_df['sub_category'] == sub_category)
        if mask.any():
            progress_df.loc[mask, 'number_company_crawled'] = crawled_count
        else:
            new_row = pd.DataFrame([{
                'main_category': main_category,
                'sub_category': sub_category, 
                'number_company_crawled': crawled_count
            }])
            progress_df = pd.concat([progress_df, new_row], ignore_index=True)
        
        progress_df.to_excel('output/metadata_crawled.xlsx', index=False)
        print(f"  Updated progress: {main_category} - {sub_category}: {crawled_count} companies")
        
    except Exception as e:
        print(f"  Error updating progress: {e}")

def save_companies_batch(main_category, companies_batch):
    """Save batch of companies to file"""
    if not companies_batch:
        return
        
    try:
        filename = normalize_filename(main_category)
        filepath = f'output/{filename}_company_details.xlsx'
        
        # Load existing data if file exists
        if os.path.exists(filepath):
            try:
                existing_df = pd.read_excel(filepath)
                new_df = pd.DataFrame(companies_batch)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                # Remove duplicates based on company name
                combined_df = combined_df.drop_duplicates(subset=['Tên công ty'], keep='first')
                combined_df.to_excel(filepath, index=False)
                print(f"    Saved {len(companies_batch)} companies to {filepath} (total: {len(combined_df)})")
            except Exception as e:
                print(f"    Error updating existing file: {e}")
                # Fallback: save new data only
                companies_df = pd.DataFrame(companies_batch)
                companies_df.to_excel(filepath, index=False)
        else:
            companies_df = pd.DataFrame(companies_batch)
            companies_df.to_excel(filepath, index=False)
            print(f"    Created {filepath} with {len(companies_batch)} companies")
            
    except Exception as e:
        print(f"    Error saving companies batch: {e}")

def get_company_data_with_order(driver):
    """Get company data with correct order numbers by finding parent containers"""
    company_data = []
    try:
        # Find div_listing parent container first
        div_listing = driver.find_element(By.CSS_SELECTOR, ".div_listing")
        
        # Find all child divs with class "rounded-4 border bg-white shadow-sm mb-3 pb-4" inside div_listing
        listing_divs = div_listing.find_elements(By.CSS_SELECTOR, ".rounded-4.border.bg-white.shadow-sm.mb-3.pb-4")
        print(f"    Found {len(listing_divs)} listing containers in div_listing")
        
        for i, listing_div in enumerate(listing_divs):
            try:
                # Find yp_noidunglistings div for company link
                company_link = listing_div.find_element(By.CSS_SELECTOR, ".yp_noidunglistings .fs-5.pb-0.text-capitalize a")
                name = company_link.text.strip()
                href = company_link.get_attribute('href')
                
                if name and href:
                    # Try to get order number, use index as fallback
                    try:
                        order_elem = listing_div.find_element(By.CSS_SELECTOR, ".yp_sothutu .yp_sothutu_txt small")
                        order_num = int(order_elem.text.strip())
                    except:
                        order_num = i + 1  # Use index as fallback
                    
                    company_data.append((name, href, order_num))
                    print(f"      Found #{order_num}: {name}")
                    
            except Exception as e:
                print(f"      Error processing listing {i+1}: {e}")
                continue
                    
    except Exception as e:
        print(f"    Error getting company data from div_listing: {e}")
        # Fallback: try without div_listing parent
        try:
            listing_divs = driver.find_elements(By.CSS_SELECTOR, ".rounded-4.border.bg-white.shadow-sm.mb-3.pb-4")
            print(f"    Fallback: Found {len(listing_divs)} listing containers")
            
            for i, listing_div in enumerate(listing_divs):
                try:
                    # Find yp_noidunglistings div for company link
                    company_link = listing_div.find_element(By.CSS_SELECTOR, ".yp_noidunglistings .fs-5.pb-0.text-capitalize a")
                    name = company_link.text.strip()
                    href = company_link.get_attribute('href')
                    
                    if name and href:
                        # Try to get order number, use index as fallback
                        try:
                            order_elem = listing_div.find_element(By.CSS_SELECTOR, ".yp_sothutu .yp_sothutu_txt small")
                            order_num = int(order_elem.text.strip())
                        except:
                            order_num = i + 1  # Use index as fallback
                        
                        company_data.append((name, href, order_num))
                        
                except Exception as e2:
                    continue
        except Exception as e2:
            print(f"    Ultimate fallback error: {e2}")
            # Last resort: old method
            try:
                company_divs = driver.find_elements(By.CSS_SELECTOR, ".yp_noidunglistings .fs-5.pb-0.text-capitalize a")
                print(f"    Last resort: Found {len(company_divs)} company links")
                for i, div in enumerate(company_divs):
                    try:
                        name = div.text.strip()
                        href = div.get_attribute('href')
                        if name and href:
                            company_data.append((name, href, i + 1))
                    except:
                        continue
            except:
                pass
    
    print(f"    Total company data extracted: {len(company_data)}")
    return company_data

def crawl_companies_from_subcategory(driver, main_category, sub_category, max_companies, existing_companies=None, start_from=0):
    """Crawl companies from a specific subcategory with resume capability"""
    if existing_companies is None:
        existing_companies = set()
        
    companies = []
    
    try:
        # Navigate to yellowpages and find the category
        driver.get("https://www.yellowpages.vn/")
        time.sleep(3)
        
        # Find main category link
        main_elements = driver.find_elements(By.CSS_SELECTOR, ".p-2.ps-1 a.text-dark")
        main_href = None
        
        for elem in main_elements:
            if elem.text.strip() == main_category:
                main_href = elem.get_attribute('href')
                break
        
        if not main_href:
            print(f"  Main category '{main_category}' not found")
            return companies
        
        # Navigate to main category
        driver.get(main_href)
        time.sleep(3)
        
        # Find subcategory link
        sub_elements = driver.find_elements(By.CSS_SELECTOR, ".col-sm-6.p-4.pe-3.pt-0.pb-2 a")
        sub_href = None
        
        for elem in sub_elements:
            elem_text = elem.text.strip()
            # Remove (number) from text for comparison
            clean_text = re.sub(r'\s*\(\d+\)$', '', elem_text)
            if clean_text == sub_category:
                sub_href = elem.get_attribute('href')
                break
        
        if not sub_href:
            print(f"  Subcategory '{sub_category}' not found")
            return companies
        
        # Store base subcategory URL for pagination
        base_subcategory_url = sub_href
        
        # Calculate starting page based on crawled count (assuming ~45 companies per page)
        start_page = max(1, (start_from // 45) + 1) if start_from > 0 else 1
        
        # Navigate to appropriate starting page
        if start_page > 1:
            start_url = f"{base_subcategory_url}?page={start_page}"
            print(f"    Resuming from page {start_page}: {start_url}")
            driver.get(start_url)
        else:
            driver.get(base_subcategory_url)
        time.sleep(3)
        
        # Crawl companies from all pages
        page = start_page
        crawled_count = start_from
        
        while crawled_count < max_companies:
            print(f"    Page {page}... ({crawled_count}/{max_companies})")
            
            # Get companies with their correct order numbers
            company_data = get_company_data_with_order(driver)
            
            if not company_data:
                print(f"    No companies found on page {page}")
                break
            
            # Count new companies on this page
            new_companies_on_page = 0
            for name, href, order in company_data:
                if name not in existing_companies:
                    new_companies_on_page += 1
            
            print(f"    Found {new_companies_on_page} new companies on page {page} (total progress: {crawled_count}/{max_companies})")
            
            # If no new companies for several pages, consider stopping
            if new_companies_on_page == 0:
                if not hasattr(crawl_companies_from_subcategory, 'empty_pages_count'):
                    crawl_companies_from_subcategory.empty_pages_count = 0
                crawl_companies_from_subcategory.empty_pages_count += 1
                
                if crawl_companies_from_subcategory.empty_pages_count >= 5:
                    print(f"    No new companies found in 5 consecutive pages - likely reached end of unique data")
                    print(f"    Current progress: {crawled_count}/{max_companies} companies")
                    break
            else:
                crawl_companies_from_subcategory.empty_pages_count = 0
            
            # Store current page URL before crawling companies
            current_page_url = driver.current_url
            
            # Crawl each company
            for name, href, order in company_data:
                if crawled_count >= max_companies:
                    break
                
                # Skip if already exists
                if name in existing_companies:
                    print(f"      Skipping existing: {name}")
                    continue
                    
                try:
                    print(f"      Crawling #{order}: {name}")
                    company_info = extract_company_detail(driver, href, f"{main_category} - {sub_category}")
                    if company_info:
                        companies.append(company_info)
                        crawled_count += 1
                        existing_companies.add(name)
                        print(f"      ✓ {name} ({crawled_count}/{max_companies})")
                        
                        # Update progress and save data every 10 companies
                        if crawled_count % 10 == 0:
                            update_crawled_progress(main_category, sub_category, crawled_count)
                            # Save current batch of companies
                            current_batch = [comp for comp in companies if comp['Ngành'] == main_category and comp['Ngành nhỏ'] == sub_category]
                            if current_batch:
                                save_companies_batch(main_category, current_batch)
                    
                    # Return to subcategory page after crawling each company
                    driver.get(current_page_url)
                    time.sleep(2)
                            
                except Exception as e:
                    print(f"      ✗ Error crawling {name}: {e}")
                    # Still return to subcategory page even if error
                    try:
                        driver.get(current_page_url)
                        time.sleep(2)
                    except:
                        pass
                    continue
            
            # Try to go to next page if we haven't reached target and there are still new companies
            if crawled_count < max_companies:
                try:
                    # Find next page link in pagination
                    next_link = None
                    paging_links = driver.find_elements(By.CSS_SELECTOR, "#paging a")
                    
                    for link in paging_links:
                        if link.text.strip() == "Tiếp":
                            href = link.get_attribute('href')
                            if href and href != "#":
                                next_link = href
                                break
                    
                    if next_link:
                        if next_link.startswith('?'):
                            next_page_url = base_subcategory_url + next_link
                        else:
                            next_page_url = next_link
                        
                        print(f"    Going to next page: {next_page_url}")
                        driver.get(next_page_url)
                        time.sleep(3)
                        page += 1
                    else:
                        # No more pages - check if we should continue or stop
                        if new_companies_on_page == 0:
                            print(f"    No next page found and no new companies - end of results")
                            break
                        else:
                            # Try a few more pages to see if there are new companies
                            pages_without_new = 0
                            max_empty_pages = 3  # Stop after 3 consecutive pages with no new companies
                            
                            for attempt_page in range(page + 1, page + max_empty_pages + 1):
                                next_page_url = f"{base_subcategory_url}?page={attempt_page}"
                                print(f"    Trying page {attempt_page}: {next_page_url}")
                                driver.get(next_page_url)
                                time.sleep(3)
                                
                                test_companies = get_company_data_with_order(driver)
                                if test_companies:
                                    # Count new companies on this test page
                                    test_new_count = sum(1 for name, _, _ in test_companies if name not in existing_companies)
                                    if test_new_count > 0:
                                        print(f"    Found {test_new_count} new companies on page {attempt_page} - continuing")
                                        page = attempt_page
                                        break
                                    else:
                                        pages_without_new += 1
                                        print(f"    No new companies on page {attempt_page} ({pages_without_new}/{max_empty_pages})")
                                else:
                                    pages_without_new += 1
                                    print(f"    No companies on page {attempt_page} ({pages_without_new}/{max_empty_pages})")
                            
                            if pages_without_new >= max_empty_pages:
                                print(f"    No new companies found in {max_empty_pages} consecutive pages - stopping")
                                break
                        
                except Exception as e:
                    print(f"    Error navigating to next page: {e}")
                    break
            else:
                print(f"    Reached target {max_companies} companies")
                break
        
        # Final progress update and save remaining companies
        update_crawled_progress(main_category, sub_category, crawled_count)
        if companies:
            save_companies_batch(main_category, companies)
        
    except Exception as e:
        print(f"  Error crawling subcategory: {e}")
    
    return companies

def find_resume_position(metadata_df, progress_df):
    """Find the last incomplete subcategory to resume from"""
    if progress_df.empty:
        return 0  # Start from beginning
    
    # Get last progress entry
    last_progress = progress_df.iloc[-1]
    last_main = last_progress['main_category']
    last_sub = last_progress['sub_category']
    last_count = last_progress['number_company_crawled']
    
    print(f"Last progress: {last_main} - {last_sub}: {last_count} companies")
    
    # Find position in metadata
    for idx, row in metadata_df.iterrows():
        if row['main_category'] == last_main and row['sub_category'] == last_sub:
            # Check if this subcategory is completed
            if last_count >= row['number_website']:
                print(f"  Last subcategory completed, starting from next one")
                return idx + 1  # Start from next subcategory
            else:
                print(f"  Resuming incomplete subcategory at position {idx}")
                return idx  # Resume this subcategory
    
    return 0  # Fallback to beginning

def crawl_by_metadata():
    """Crawl companies based on metadata file with resume capability"""
    # Load metadata
    try:
        metadata_df = pd.read_excel('output/categories_metadata.xlsx')
        print(f"Loaded metadata with {len(metadata_df)} subcategories")
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return
    
    # Load crawled progress
    progress_df = get_crawled_progress()
    
    # Find resume position
    start_idx = find_resume_position(metadata_df, progress_df)
    print(f"Starting from position {start_idx}/{len(metadata_df)}")
    
    driver = setup_driver()
    
    try:
        # Process from resume position onwards
        for idx in range(start_idx, len(metadata_df)):
            row = metadata_df.iloc[idx]
            main_category = row['main_category']
            sub_category = row['sub_category']
            max_companies = row['number_website']
            
            print(f"\n[{idx+1}/{len(metadata_df)}] Processing: {main_category} - {sub_category}")
            
            # Get existing companies to avoid duplicates
            existing_companies = get_existing_companies(main_category)
            
            # Check progress for this specific subcategory
            progress_mask = (progress_df['main_category'] == main_category) & (progress_df['sub_category'] == sub_category)
            
            if progress_mask.any():
                crawled_count = progress_df.loc[progress_mask, 'number_company_crawled'].iloc[0]
                if crawled_count >= max_companies:
                    print(f"  Skipping - already completed ({crawled_count}/{max_companies})")
                    continue
                else:
                    print(f"  Resuming from {crawled_count} to {max_companies}")
            else:
                crawled_count = 0
                print(f"  Starting fresh ({max_companies} companies)")
            
            companies = crawl_companies_from_subcategory(
                driver, main_category, sub_category, max_companies, existing_companies, crawled_count
            )
            
            print(f"  Crawled {len(companies)} new companies from {sub_category}")
            
    except Exception as e:
        print(f"Error during crawling: {e}")
    finally:
        driver.quit()

def main():
    """Main function"""
    import os
    os.makedirs('output', exist_ok=True)
    crawl_by_metadata()

if __name__ == "__main__":
    main()