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
```

## 5. How to Run the Script
### Step 1: Install Dependencies
Run the following command:
```sh
pip install selenium pandas webdriver-manager
```
### Step 2: Run the Script
Execute the script using:
```sh
python scraper.py
```
### Step 3: Enter the Number of Categories
When prompted, enter:
```sh
Enter number of categories to scrape (0 for all): 11
```
This ensures the scraper runs for the 11 specified categories.
### Step 4: View and Save Data
- The script will scrape product data and save it in tops_products.jsonl.
- A summary table will be displayed in the console.
### Step 5: Verify the Scraped Data
To view the scraped data, you can run:
```sh
cat tops_products.jsonl | head -n 10
```
This will display the first 10 products in the dataset.

## 6. Challenges Faced & Solutions
###**1️⃣ CAPTCHA / Anti-Scraping Measures**
  Problem: Some pages block automated requests.
  Solution:
  - Used custom user-agents to mimic real users.
  - Added JavaScript scrolling instead of Selenium send_keys().
  - Implemented randomized waits instead of fixed delays.
###**2️⃣ Pagination Issues**
  Problem: Some pages don’t load all products at once.
  Solution:
  - Dynamically scrolls to ensure all products are loaded.
  - Uses WebDriverWait to detect new product loads.
###**3️⃣ Website Structure Changes**
  Problem: HTML elements changed between runs, causing errors.
  Solution:
  - Used try-except blocks to handle missing elements.
  - Updated CSS selectors to fallback versions.
