from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from colorama import Fore, init

init(autoreset=True)


SBR_WEBDRIVER = 'https://brd-customer-hl_7affd633-zone-ai_scraper:hwvja2pke04f@brd.superproxy.io:9515'


def scrape_website(website):
    print(f"{Fore.GREEN}Launching chrome browser...")

    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        #print('Connected! Navigating to: {}'.format(website))
        driver.get(website)
        print(f'{Fore.YELLOW}Waiting captcha to solve...')

        solve_res = driver.execute('executeCdpCommand', {
            'cmd': 'Captcha.waitForSolve',
            'params': {'detectTimeout': 10000},
        })

        print('Captcha solve status:', solve_res['value'][f'status'])
        print('Navigated! Scraping page content...')

        html = driver.page_source
        print(f'{Fore.GREEN}Scraping finalized!')
        return html


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ''

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())
    return cleaned_content

def split_dom_content(dom_content, max_length=5000):
    return [dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)]