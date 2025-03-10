# ScrapeMonster.tech - Big C Web Scraping Assignment

## 1. Approach Used
This script scrapes product data from Big C’s online store using **Selenium** and **Python**.  
The step-by-step process includes:
- **Extracting Categories:** Fetches all main categories and subcategories.
- **Handling Pagination:** Uses infinite scrolling with JavaScript to dynamically load products.
- **Extracting Product Pages:** Extracts product name, price, image, promotions, and more.
- **Anti-Scraping Protections:**  
  - Uses a **custom user-agent** to mimic a real browser.  
  - Implements **dynamic waits** to avoid being flagged.  
  - Runs **headless Chrome** to improve speed.

## 2. Total Product Count
- **Total products listed on the website:** `______`
- **Total products successfully scraped:** `______`

## 3. Duplicate Handling Logic
The script ensures **no duplicate products** using the following techniques:
- **Checks Product URLs:** Before saving, it verifies if the product URL has already been scraped.
- **Incremental Updates:** If a product exists in the dataset, it updates **price changes and promotions** instead of duplicating.
- **JSONL Format:** The output is stored in `.jsonl` format for efficient appending without duplication.

## 4. Dependencies
Ensure you have the following libraries installed:

| Library           | Version |
|------------------|---------|
| selenium        | latest  |
| pandas         | latest  |
| webdriver-manager | latest  |

To install dependencies, run:
```sh
pip install selenium pandas webdriver-manager
