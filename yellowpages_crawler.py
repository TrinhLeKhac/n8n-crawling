from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

def setup_driver():
    """Thiết lập Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_company_info(driver, company_index):
    """Trích xuất thông tin từ một div công ty bằng index"""
    try:
        # Tìm lại element để tránh stale
        company_divs = driver.find_elements(By.CSS_SELECTOR, "body > div.mt-3.m-auto.h-auto > div > div.div_listing.mb-4 > div")
        if company_index >= len(company_divs):
            return None
        
        company_div = company_divs[company_index]
        
        # Scroll đến element và đợi
        driver.execute_script("arguments[0].scrollIntoView(true);", company_div)
        time.sleep(2)
        
        # Kiểm tra loại layout
        outer_html = company_div.get_attribute('outerHTML')
        is_full_layout = 'yp_div_logo_diachi' in outer_html
        
        print(f"  [DEBUG] Công ty {company_index + 1} - Layout: {'Full' if is_full_layout else 'Simple'}")
        
        # Tên công ty - thử nhiều selector
        name = ""
        name_selectors = [
            "div.yp_noidunglistings > div:nth-child(1) > div > h2 > a",
            "h2 > a",
            "h2",
            "a[href*='detail']",
            ".yp_noidunglistings h2 a"
        ]
        
        for selector in name_selectors:
            try:
                name_element = company_div.find_element(By.CSS_SELECTOR, selector)
                name = name_element.text.strip()
                if name:
                    print(f"  [DEBUG] Tên tìm thấy với selector: {selector}")
                    break
            except:
                continue
        
        # Địa chỉ - xử lý khác nhau cho 2 layout
        address = ""
        if is_full_layout:
            # Layout đầy đủ thông tin
            address_selectors = [
                "div.yp_noidunglistings > div.yp_div_logo_diachi.clearfix > div.float-end.yp_diachi_logo > p:nth-child(1)",
                ".yp_diachi_logo p:first-child"
            ]
            for selector in address_selectors:
                try:
                    address_element = company_div.find_element(By.CSS_SELECTOR, selector)
                    address = address_element.text.strip()
                    if address and any(keyword in address.lower() for keyword in ['số', 'đường', 'phường', 'quận']):
                        print(f"  [DEBUG] Địa chỉ tìm thấy với selector: {selector}")
                        break
                except:
                    continue
        else:
            # Layout đơn giản - selector cụ thể
            try:
                address_element = company_div.find_element(By.CSS_SELECTOR, "div.yp_noidunglistings > div.h-auto.clearfix.mt-3 > p:nth-child(1)")
                address = address_element.text.strip()
                print(f"  [DEBUG] Địa chỉ simple layout tìm thấy")
            except:
                pass
        
        # Số điện thoại - xử lý khác nhau cho 2 layout
        phone = ""
        if is_full_layout:
            phone_selectors = [
                "div.yp_noidunglistings > div.yp_div_logo_diachi.clearfix > div.float-end.yp_diachi_logo > p:nth-child(2)",
                ".yp_diachi_logo p:nth-child(2)"
            ]
            for selector in phone_selectors:
                try:
                    phone_element = company_div.find_element(By.CSS_SELECTOR, selector)
                    phone_text = phone_element.text.strip()
                    if phone_text and any(char.isdigit() for char in phone_text):
                        phone = phone_text
                        print(f"  [DEBUG] Điện thoại tìm thấy với selector: {selector}")
                        break
                except:
                    continue
        else:
            # Layout đơn giản - selector cụ thể
            try:
                phone_element = company_div.find_element(By.CSS_SELECTOR, "div.yp_noidunglistings > div.h-auto.clearfix.mt-3 > p:nth-child(2)")
                phone = phone_element.text.strip()
                print(f"  [DEBUG] Điện thoại simple layout tìm thấy")
            except:
                pass
        
        # Hotline
        hotline = ""
        try:
            hotline_element = company_div.find_element(By.CSS_SELECTOR, "div.yp_noidunglistings > div.yp_div_logo_diachi.clearfix > div.float-end.yp_diachi_logo > p.m-0.pb-2")
            hotline = hotline_element.text.strip()
        except:
            pass
        
        # Email - xử lý khác nhau cho 2 layout
        email = ""
        if is_full_layout:
            email_selectors = [
                "div.yp_noidunglistings > div.yp_div_logo_diachi.clearfix > div.float-end.yp_diachi_logo > p:nth-child(4)",
                "a[href^='mailto:']",
                ".yp_diachi_logo p"
            ]
            for selector in email_selectors:
                try:
                    email_element = company_div.find_element(By.CSS_SELECTOR, selector)
                    email_text = email_element.text.strip()
                    if '@' in email_text:
                        email = email_text
                        print(f"  [DEBUG] Email tìm thấy với selector: {selector}")
                        break
                except:
                    continue
        else:
            # Layout đơn giản - selector cụ thể
            try:
                email_element = company_div.find_element(By.CSS_SELECTOR, "div.yp_noidunglistings > div.h-auto.clearfix.mt-3 > p:nth-child(3)")
                email = email_element.text.strip()
                print(f"  [DEBUG] Email simple layout tìm thấy")
            except:
                # Thử mailto link
                try:
                    email_element = company_div.find_element(By.CSS_SELECTOR, "a[href^='mailto:']")
                    email = email_element.get_attribute('href').replace('mailto:', '')
                    print(f"  [DEBUG] Email tìm thấy qua mailto")
                except:
                    pass
        
        # Website - xử lý khác nhau cho 2 layout
        website = ""
        if is_full_layout:
            website_selectors = [
                "div.yp_noidunglistings > div.yp_div_logo_diachi.clearfix > div.float-end.yp_diachi_logo > p:nth-child(5)",
                ".yp_diachi_logo p"
            ]
            for selector in website_selectors:
                try:
                    website_element = company_div.find_element(By.CSS_SELECTOR, selector)
                    website_text = website_element.text.strip()
                    if 'www' in website_text.lower() or 'http' in website_text.lower():
                        website = website_text
                        print(f"  [DEBUG] Website tìm thấy với selector: {selector}")
                        break
                except:
                    continue
        else:
            # Layout đơn giản - selector cụ thể
            try:
                website_element = company_div.find_element(By.CSS_SELECTOR, "div.yp_noidunglistings > div.h-auto.clearfix.mt-3 > p:nth-child(4)")
                website = website_element.text.strip()
                print(f"  [DEBUG] Website simple layout tìm thấy")
            except:
                pass
        
        # Nội dung giới thiệu
        description = ""
        try:
            desc_element = company_div.find_element(By.CSS_SELECTOR, "div.yp_noidunglistings > div.mt-3.rounded-4.pb-2.h-auto.text_quangcao")
            description = desc_element.text.strip()
        except:
            pass
        
        # Print chi tiết thông tin crawl được
        print(f"  - Tên: '{name}'")
        print(f"  - Địa chỉ: '{address}'")
        print(f"  - Điện thoại: '{phone}'")
        print(f"  - Hotline: '{hotline}'")
        print(f"  - Email: '{email}'")
        print(f"  - Website: '{website}'")
        print(f"  - Mô tả: '{description[:100]}...' ({len(description)} ký tự)")
        
        return {
            "Tên công ty": name,
            "Địa chỉ": address,
            "Điện thoại": phone,
            "Hotline": hotline,
            "Email": email,
            "Website": website,
            "Mô tả": description
        }
    except Exception as e:
        return None

def crawl_yellowpages(url):
    """Crawl Yellow Pages với selector cụ thể"""
    driver = setup_driver()
    all_companies = []
    page = 1
    
    try:
        # Load trang đầu tiên
        driver.get(url)
        time.sleep(5)
        
        while True:
            print(f"Đang crawl trang {page}...")
            
            # Tìm tất cả div công ty
            company_divs = driver.find_elements(By.CSS_SELECTOR, "body > div.mt-3.m-auto.h-auto > div > div.div_listing.mb-4 > div")
            
            if not company_divs:
                print(f"Không tìm thấy công ty nào ở trang {page}")
                break
            
            print(f"Tìm thấy {len(company_divs)} công ty ở trang {page}")
            
            # Trích xuất thông tin từng công ty
            for i in range(len(company_divs)):
                print(f"Đang xử lý công ty {i+1}/{len(company_divs)}")
                company_info = extract_company_info(driver, i)
                if company_info and company_info["Tên công ty"]:
                    all_companies.append(company_info)
                    print(f"✓ Đã lưu công ty: {company_info['Tên công ty']}")
                    print("---")
                else:
                    print(f"⚠ Không lấy được thông tin công ty {i+1}")
                    print("---")
            
            # Tìm tất cả các nút trang
            try:
                page_links = driver.find_elements(By.CSS_SELECTOR, "#paging > a")
                next_page_found = False
                
                for link in page_links:
                    link_text = link.text.strip()
                    # Tìm trang tiếp theo (số trang lớn hơn trang hiện tại)
                    if link_text.isdigit() and int(link_text) == page + 1:
                        print(f"Chuyển sang trang {page + 1}")
                        driver.execute_script("arguments[0].click();", link)
                        page += 1
                        next_page_found = True
                        # Đợi trang mới load hoàn toàn
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.mt-3.m-auto.h-auto > div > div.div_listing.mb-4 > div"))
                        )
                        time.sleep(3)
                        break
                
                if not next_page_found:
                    print("Đã crawl hết tất cả các trang")
                    break
                    
            except Exception as e:
                print(f"Lỗi khi tìm trang tiếp theo: {e}")
                break
    
    except Exception as e:
        print(f"Lỗi khi crawl: {e}")
    
    finally:
        driver.quit()
    
    return all_companies

def save_to_excel(data, filename="yellowpages_data.xlsx"):
    """Lưu dữ liệu vào file Excel"""
    if data:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Đã lưu {len(data)} công ty vào file {filename}")
    else:
        print("Không có dữ liệu để lưu")

if __name__ == "__main__":
    url = "https://www.yellowpages.vn/cls/419935/chuyen-phat-nhanh-cong-ty-chuyen-phat-nhanh.html"
    
    print("Bắt đầu crawling Yellow Pages...")
    companies = crawl_yellowpages(url)
    
    if companies:
        print(f"\nTìm thấy tổng cộng {len(companies)} công ty:")
        for i, company in enumerate(companies, 1):
            print(f"\n{i}. {company['Tên công ty']}")
            if company['Địa chỉ']:
                print(f"   Địa chỉ: {company['Địa chỉ']}")
            if company['Điện thoại']:
                print(f"   Điện thoại: {company['Điện thoại']}")
            if company['Hotline']:
                print(f"   Hotline: {company['Hotline']}")
            if company['Email']:
                print(f"   Email: {company['Email']}")
            if company['Website']:
                print(f"   Website: {company['Website']}")
        
        save_to_excel(companies)
    else:
        print("Không tìm thấy dữ liệu công ty nào")