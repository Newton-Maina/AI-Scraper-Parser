import time
import os
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from colorama import Fore, init

init(autoreset=True)

SBR_WEBDRIVER = 'https://brd-customer-hl_a23e659a-zone-store_scraper:fqxrbl54it17@brd.superproxy.io:9515'


def scrape_website(website, max_pages=10):
    print(f"{Fore.GREEN}Launching chrome browser...")

    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
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
                print(f"{Fore.RED}Next button not found or failed to click on page {page_num} ({e})")
                driver.save_screenshot(f"error_page_{page_num}.png")
                with open(f"error_page_{page_num}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                break

    finally:
        driver.quit()

    return all_pages_html

def extract_body_content(html_content):
    """
    Extract only <body> content from raw HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ''


def clean_body_content(body_content):
    """
    Extract ONLY visible text from body content (no HTML, no attributes).
    """
    soup = BeautifulSoup(body_content, 'html.parser')

    # Remove scripts, styles, and irrelevant tags
    for tag in soup(['script', 'style', 'svg']):
        tag.decompose()

    # Remove buttons, nav, footer if you don’t want "Add to Cart" etc.
    for tag in soup(['button', 'nav', 'footer', 'header']):
        tag.decompose()

    # Extract plain text
    cleaned_content = soup.get_text(separator="\n")

    # Remove empty lines / whitespace
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content




# def split_dom_content(dom_content, max_length=5000):
#     """
#     Splits DOM content into chunks.
#     - If dom_content is a list (multiple pages), each page is split separately.
#     - If dom_content is a string (single page), it is split directly.
#     """
#     chunks = []

#     if isinstance(dom_content, list):  # multiple pages
#         for page in dom_content:
#             for i in range(0, len(page), max_length):
#                 chunks.append(page[i: i + max_length])
#     elif isinstance(dom_content, str):  # single page
#         for i in range(0, len(dom_content), max_length):
#             chunks.append(dom_content[i: i + max_length])
#     else:
#         raise TypeError("dom_content must be a string or a list of strings")

#     return chunks


# def save_dom_files(pages_html, output_dir="scraped_dom"):
#     """
#     Save cleaned DOM from each page into text files.
#     """
#     os.makedirs(output_dir, exist_ok=True)
#     for idx, html in enumerate(pages_html, start=1):
#         body = extract_body_content(html)
#         cleaned = clean_body_content(body)
#         file_path = os.path.join(output_dir, f"page_{idx}.txt")
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(cleaned)
#         print(f"{Fore.GREEN}Saved {file_path}")
