import time
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, init
import os

init(autoreset=True)

def get_webdriver_url():
    # Use environment variable or fallback (caution with fallback in production)
    return os.getenv('SBR_WEBDRIVER', 'https://brd-customer-hl_a23e659a-zone-store_scraper:fqxrbl54it17@brd.superproxy.io:9515')

def scrape_website(website, max_pages=10):
    print(f"{Fore.GREEN}Launching chrome browser...")
    
    sbr_url = get_webdriver_url()
    sbr_connection = ChromiumRemoteConnection(sbr_url, 'goog', 'chrome')
    driver = Remote(sbr_connection, options=ChromeOptions())

    all_pages_html = []
    try:
        driver.get(website)
        print(f"{Fore.YELLOW}Waiting captcha to solve...")

        solve_res = driver.execute('executeCdpCommand', {
            'cmd': 'Captcha.waitForSolve',
            'params': {'detectTimeout': 15000},
        })
        print("Captcha solve status:", solve_res['value']['status'])

        for page_num in range(1, max_pages + 1):
            # Wait for product grid to load (target ProductCard container)
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sm\\:grid-cols-2.lg\\:grid-cols-3.xl\\:grid-cols-4, [class*='grid-cols']"))
            )

            # Wait for at least one ProductCard to ensure products are loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-nc-id='ProductCard']"))
            )

            time.sleep(1)  # Brief wait for React to stabilize
            products = driver.find_elements(By.CSS_SELECTOR, "[data-nc-id='ProductCard']")
            print(f"{Fore.YELLOW}Found {len(products)} products on page {page_num}")

            html = driver.page_source
            all_pages_html.append(html)
            print(f"{Fore.GREEN}Captured product page {page_num}")

            # Try to find and click the "Next" button
            try:
                # Selector for the "Next" button based on Pagination component
                next_button = driver.find_element(
                    By.XPATH, "//button[contains(., '›') and contains(@class, 'inline-flex') and contains(@class, 'w-11')]"
                )

                # Check if the button is disabled
                if next_button.get_attribute("disabled"):
                    print(f"{Fore.CYAN}No more product pages after {page_num} (Next button disabled)")
                    break

                # Store a reference to a product element to detect staleness
                first_product = driver.find_element(By.CSS_SELECTOR, "[data-nc-id='ProductCard']:first-child")

                next_button.click()
                print(f"{Fore.CYAN}Clicked 'Next' button on page {page_num}")

                # Wait for the product grid to update (staleness of first product)
                WebDriverWait(driver, 15).until(
                    EC.staleness_of(first_product)
                )

                # Additional wait for new products to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-nc-id='ProductCard']"))
                )

                print(f"{Fore.CYAN}➡️ Moved to product page {page_num + 1}")

            except Exception as e:
                # If next button is not found or fails, we assume end of pagination or error
                # We can log it but if it's just "not found", it usually means last page.
                print(f"{Fore.CYAN}Stopping pagination (Next button issue or end of list): {e}")
                # Optional: Screenshot or save error page if debugging is needed
                # driver.save_screenshot(f"error_page_{page_num}.png")
                break

    finally:
        driver.quit()

    return all_pages_html
