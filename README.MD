# Google Play Store Scraper

This project is a Python-based scraper for the Google Play Store. It allows users to search for apps based on specific criteria and extract detailed information about them, including contact details for the app developers.

## Features

- Search for apps on Google Play Store using custom search terms
- Filter apps based on the number of downloads
- Extract detailed app information, including:
  - App name
  - Category
  - Number of downloads
  - Developer email
  - Developer phone number
  - Developer website
  - Developer address
  - Release date
  - App ID
- Scrape phone numbers from developer websites
- Validate and format phone numbers
- Multi-threaded scraping for improved performance
- CSV output of scraped data

## Requirements

- Python 3.6+
- Dependencies (install via `pip install -r requirements.txt`):
  - google-play-scraper
  - requests
  - beautifulsoup4
  - phonenumbers
  - pandas

## Usage

### As a standalone script

1. Clone the repository:
   ```
   git clone https://github.com/your-username/google-play-store-scraper.git
   cd google-play-store-scraper
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the script:
   ```python
   python scraper.py
   ```

4. Modify the main section of the script to customize your search:
   ```python
   if __name__ == '__main__':
       search_term = "digital art"
       min_downloads = 1000
       max_downloads = 1000000
       output_file = "digital_art_apps.csv"
       max_workers = 5

       results = scrape_apps(search_term, min_downloads, max_downloads, output_file, max_workers)
       print(f"Scraped {len(results)} apps.")
   ```

### As an imported module

You can also import and use the scraper in your own Python scripts. Here's how:

1. Ensure the scraper file is in your Python path or in the same directory as your script.

2. Import the `scrape_apps` function:
   ```python
   from Main import scrape_apps
   ```

3. Use the function in your script:
   ```python
   search_term = "fitness apps"
   min_downloads = 10000
   max_downloads = 5000000
   output_file = "fitness_apps.csv"
   max_workers = 10

   results = scrape_apps(search_term, min_downloads, max_downloads, output_file, max_workers)
   
   print(f"Scraped {len(results)} apps.")
   
   # You can now work with the 'results' list, which contains dictionaries of app details
   for app in results:
       print(f"App Name: {app['App Name']}, Downloads: {app['Downloads']}")
   ```

4. You can also import and use individual functions if needed:
   ```python
   from scraper import get_app_details, parse_phone_number

   app_id = "com.example.app"
   app_details = get_app_details(app_id, 1000, 1000000)
   if app_details:
       country_code, phone = parse_phone_number(app_details['Developer Phone'])
       print(f"Developer phone: {phone} (Country code: {country_code})")
   ```

## Output

The script will generate a CSV file with the scraped data. The default filename is `app_leads.csv`, but you can specify a custom filename in the `scrape_apps` function call.

## Disclaimer

This tool is for educational purposes only. Make sure to comply with Google Play Store's terms of service and respect the privacy of app developers when using this scraper.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/your-username/google-play-store-scraper/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenss/mit/)
