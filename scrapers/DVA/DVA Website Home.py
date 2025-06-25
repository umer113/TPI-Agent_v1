import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager  # ✅ this is key

BASE_URL = "https://clik.dva.gov.au/"

# ✅ Setup headless Chrome with WebDriver Manager
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ✅ Use webdriver-manager to auto-download chromedriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def normalize_url(url):
        return url if url.startswith('http') else urljoin(BASE_URL, url)

    # NAVBAR
    navbar_links = []
    navbar = soup.find('nav')
    if navbar:
        for a in navbar.find_all('a', href=True):
            name = a.text.strip()
            url = normalize_url(a['href'])
            navbar_links.append({'Section': 'Navbar', 'Type': 'Link', 'Name': name, 'URL': url})

    # FOOTER
    footer_links = []
    footer = soup.find('footer')
    if footer:
        for a in footer.find_all('a', href=True):
            name = a.text.strip()
            url = normalize_url(a['href'])
            footer_links.append({'Section': 'Footer', 'Type': 'Link', 'Name': name, 'URL': url})

    # BANNER
    banner_data = []
    banner = soup.find('div', class_='site-banner-outter bg-with-image')
    if banner:
        h1_tag = banner.find('h1')
        p_tags = banner.find_all('p')
        if h1_tag:
            banner_data.append({'Section': 'Banner', 'Type': 'H1', 'Content': h1_tag.get_text(strip=True), 'URL': ''})
        for p in p_tags:
            banner_data.append({'Section': 'Banner', 'Type': 'P', 'Content': p.get_text(strip=True), 'URL': ''})

    # IMPORTANT NOTICE
    notice_data = []
    important_notice_h2 = soup.find('h2', string=lambda text: text and 'Important Notice' in text)
    if important_notice_h2:
        notice_section = important_notice_h2.find_next('div')
        if notice_section:
            for element in notice_section.find_all(['h2', 'h3', 'p', 'a']):
                text = element.get_text(strip=True)
                if element.name in ['h2', 'h3', 'p']:
                    links = element.find_all('a')
                    if links:
                        for link in links:
                            normalized_url = normalize_url(link['href'])
                            notice_data.append({'Section': 'Important Notice', 'Type': 'Link', 'Content': link.text.strip(), 'URL': normalized_url})
                    else:
                        notice_data.append({'Section': 'Important Notice', 'Type': element.name.upper(), 'Content': text, 'URL': ''})
                elif element.name == 'a':
                    normalized_url = normalize_url(element['href'])
                    notice_data.append({'Section': 'Important Notice', 'Type': 'Link', 'Content': element.text.strip(), 'URL': normalized_url})

    # CLIK LIBRARIES
    libraries_data = []
    libraries_h2 = soup.find('h2', string='CLIK Libraries')
    if libraries_h2:
        libraries_section = libraries_h2.find_next('div')
        if libraries_section:
            for element in libraries_section.find_all(['h2', 'h3', 'p', 'a']):
                text = element.get_text(strip=True)
                if element.name in ['h2', 'h3', 'p']:
                    links = element.find_all('a')
                    if links:
                        for link in links:
                            normalized_url = normalize_url(link['href'])
                            libraries_data.append({'Section': 'CLIK Libraries', 'Type': 'Link', 'Content': link.text.strip(), 'URL': normalized_url})
                    else:
                        libraries_data.append({'Section': 'CLIK Libraries', 'Type': element.name.upper(), 'Content': text, 'URL': ''})
                elif element.name == 'a':
                    normalized_url = normalize_url(element['href'])
                    libraries_data.append({'Section': 'CLIK Libraries', 'Type': 'Link', 'Content': element.text.strip(), 'URL': normalized_url})

    # IMAGES
    image_data = []
    for img in soup.find_all('img'):
        src = normalize_url(img.get('src', ''))
        alt = img.get('alt', '')
        image_data.append({'Section': 'Images', 'Type': 'Image', 'Content': alt, 'URL': src})

    # SAVE TO CSV
    combined_data = navbar_links + banner_data + notice_data + libraries_data + footer_links + image_data
    df_combined = pd.DataFrame(combined_data)
    df_combined.to_csv('DVA Website Home.csv', index=False)

finally:
    driver.quit()
