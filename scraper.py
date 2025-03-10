import os
import json
import logging
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    filename="scraper.log", level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Base URL for scraping
BASE_URL = "https://www.tops.co.th/en"
OUTPUT_FILE = "tops_products.jsonl"

def setup_driver():
    """Setup Selenium WebDriver with user-agent spoofing for anti-bot evasion."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_category_links():
    """Extract category names and URLs with improved handling for slow page loads."""
    driver = setup_driver()
    driver.get(BASE_URL)

    try:
        # Ensure the page is fully loaded
        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Wait for category elements
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".shop-by-category__card a"))
        )

        categories = {}
        category_elements = driver.find_elements(By.CSS_SELECTOR, ".shop-by-category__card a")

        for element in category_elements:
            category_name = element.get_attribute("aria-label").strip()
            category_url = element.get_attribute("href")
            if category_url:
                categories[category_name] = category_url

        return categories
    except Exception as e:
        logging.error(f"Error loading categories: {e}")
        return {}
    finally:
        driver.quit()


def scroll_until_all_products_loaded(driver, expected_count, max_attempts=50):
    """Scroll until all expected products are loaded."""
    attempts = 0
    prev_count = 0

    while attempts < max_attempts:
        products = driver.find_elements(By.CLASS_NAME, "product-item")
        current_count = len(products)

        logging.info(f"Scrolling... Loaded {current_count}/{expected_count}")

        if current_count >= expected_count:
            break

        if current_count == prev_count:
            attempts += 1
            if attempts >= 5:
                logging.warning(f"Stopping scroll early: Expected {expected_count}, Got {current_count}")
                break
        else:
            attempts = 0

        prev_count = current_count
        driver.execute_script("window.scrollBy(0, window.innerHeight);")

        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, "product-item")) > current_count
            )
        except:
            logging.warning("Timeout while waiting for more products. Trying again...")

def extract_product_data(product_element, category):
    """Extract product details with error handling."""
    try:
        name = product_element.find_element(By.CLASS_NAME, "product-tile__name").text.strip()
        image = product_element.find_element(By.TAG_NAME, "img").get_attribute("src")
        price = product_element.find_element(By.CLASS_NAME, "price-number").text.strip() if product_element.find_elements(By.CLASS_NAME, "price-number") else "N/A"
        quantity = product_element.find_element(By.CLASS_NAME, "price-label").text.strip() if product_element.find_elements(By.CLASS_NAME, "price-label") else "N/A"
        product_url = product_element.find_element(By.TAG_NAME, "a").get_attribute("href")
        promotions = product_element.find_element(By.CLASS_NAME, "product-item-promo-name").text.strip() if product_element.find_elements(By.CLASS_NAME, "product-item-promo-name") else "N/A"
        badges = product_element.find_element(By.CLASS_NAME, "product-item-badge").get_attribute("alt") if product_element.find_elements(By.CLASS_NAME, "product-item-badge") else "N/A"
        brand = product_element.find_element(By.CLASS_NAME, "brand-name").text.strip() if product_element.find_elements(By.CLASS_NAME, "brand-name") else "Unknown"
        rating = product_element.find_element(By.CLASS_NAME, "product-rating").text.strip() if product_element.find_elements(By.CLASS_NAME, "product-rating") else "No rating"
        date_scraped = datetime.utcnow().isoformat()

        return {
            "product_name": name,
            "brand": brand,
            "rating": rating,
            "product_url": product_url,
            "image_url": image,
            "quantity": quantity,
            "price": price,
            "promotions": promotions,
            "badges": badges,
            "category": category,
            "date_scraped": date_scraped
        }
    except Exception as e:
        logging.error(f"Error extracting product data: {e}")
        return None

def scrape_products(subcategory_name, subcategory_url, expected_count):
    """Scrape products for a single subcategory with retries."""
    driver = setup_driver()
    driver.get(subcategory_url)

    scroll_until_all_products_loaded(driver, expected_count)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "product-item"))
    )

    product_elements = driver.find_elements(By.CLASS_NAME, "product-item")
    logging.info(f"Found {len(product_elements)} products in {subcategory_name}")

    products = [extract_product_data(pe, subcategory_name) for pe in product_elements]

    driver.quit()
    return products

def save_to_jsonl(data, filename):
    """Save scraped data to a JSONL file."""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")
        logging.info(f"Saved {len(data)} records to {filename}")
    except Exception as e:
        logging.error(f"Failed to save data: {e}")

def display_summary(summary):
    """Display scraped data summary in tabular format."""
    df = pd.DataFrame(summary)
    print("\n=== Scraping Summary ===")
    print(df.to_markdown(index=False))

def main(num_categories=0):
    """Main function to scrape multiple subcategories in parallel."""
    categories = get_category_links()

    if num_categories > 0:
        categories = dict(list(categories.items())[:num_categories])

    all_products = []
    summary = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for category, category_url in categories.items():
            driver = setup_driver()
            driver.get(category_url)

            subcategories = {}
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ais-RefinementList-item a"))
            )

            for element in driver.find_elements(By.CLASS_NAME, "ais-RefinementList-item a"):
                subcategory_name = element.find_element(By.CLASS_NAME, "ais-RefinementList-label").text.strip()
                subcategory_url = element.get_attribute("href")
                try:
                    count_text = element.find_element(By.CLASS_NAME, "ais-RefinementList-count").text.strip()
                    product_count = int(count_text.replace(",", "")) if count_text.isdigit() else 0
                except:
                    product_count = 0  

                if subcategory_url:
                    futures.append(executor.submit(scrape_products, subcategory_name, subcategory_url, product_count))
                    summary.append({"Category": category, "Subcategory": subcategory_name, "Listed": product_count, "Scraped": 0})

            driver.quit()

        for future, entry in zip(futures, summary):
            products = future.result()
            entry["Scraped"] = len(products)
            all_products.extend(products)

    save_to_jsonl(all_products, OUTPUT_FILE)
    display_summary(summary)

if __name__ == "__main__":
    num_categories_to_scrape = int(input("Enter number of categories to scrape (0 for all): "))
    main(num_categories=num_categories_to_scrape)
