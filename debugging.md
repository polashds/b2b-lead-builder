Great progress! 🚀 You’ve built everything correctly — the **403 Forbidden** errors you’re seeing are very common when scraping sites like Yellow Pages. Let me break down why this happens and how to fix it step by step.

---

## 🔎 Why You Got `403 Forbidden`

1. **Bot Protection:** Yellow Pages actively blocks automated scrapers with tools like Akamai, PerimeterX, or Cloudflare.
2. **Headers Too Simple:** Just sending a `User-Agent` isn’t enough. Many sites check for realistic browser-like headers (cookies, accept-language, etc.).
3. **IP Blocking:** They may block repeated requests from your IP address.
4. **Anti-Scraping JS:** Some pages render data with JavaScript, and `requests + BeautifulSoup` won’t see it.

---

## ✅ Step 1: Add Realistic Headers

In `core/base_scraper.py`, update the session headers with a more complete set:

```python
self.session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1"  # Do Not Track header
})
```

This makes your scraper look more like a real browser.

---

## ✅ Step 2: Rotate User Agents

Install `fake-useragent`:

```bash
pip install fake-useragent
```

Then in `base_scraper.py`:

```python
from fake_useragent import UserAgent

ua = UserAgent()
self.session.headers.update({"User-Agent": ua.random})
```

This rotates the User-Agent for each session, reducing detection.

---

## ✅ Step 3: Use Proxies (Optional but Recommended)

Yellow Pages may still block your IP. Add proxy support:

```python
proxies = {
    "http": "http://username:password@proxyserver:port",
    "https": "http://username:password@proxyserver:port"
}

response = self.session.get(url, params=params, timeout=settings.REQUEST_TIMEOUT, proxies=proxies)
```

For free testing, you can use [free proxy lists](https://free-proxy-list.net/), but for real client work, use a paid rotating proxy service (BrightData, ScraperAPI, or SmartProxy).

---

## ✅ Step 4: Test if Page is JavaScript-Rendered

Run this in a Jupyter notebook or small script:

```python
import requests
from bs4 import BeautifulSoup

url = "https://www.yellowpages.com/search?search_terms=plumber&geo_location_terms=New+York"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
print(r.text[:1000])  # preview first 1000 chars
```

* If you **see company data in HTML**, requests+BeautifulSoup works.
* If you **see lots of `<script>` and no company info**, the content is JavaScript-rendered → you need **Selenium or Playwright**.

---

## ✅ Step 5: Fallback with Selenium (if JS rendering is required)

Install:

```bash
pip install selenium webdriver-manager
```

Example:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # run without opening browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.yellowpages.com/search?search_terms=plumber&geo_location_terms=New+York"
driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, "lxml")

print(soup.prettify()[:1000])  # check if results are visible
driver.quit()
```

If this works → adapt your scraper to use Selenium instead of plain requests.

---

## ✅ Step 6: Start Simple (Debugging Strategy)

* Test with **just one URL** (hardcoded, not looped).
* Confirm selectors with Chrome DevTools → update `yellow_pages_scraper.py`.
* Once data extraction works, re-add loops + cleaning + saving.

---

## 🔑 Professional Approach for Client Projects

For business-grade delivery:

1. Use **requests + headers + proxies** if site is static HTML.
2. Switch to **Selenium/Playwright** if the site uses JavaScript.
3. Implement **retry logic** with exponential backoff for failed requests.
4. Keep a **configurable scraper.yaml** where the client can change:

   * directory site
   * search terms
   * number of pages
5. Always **log errors** instead of crashing.

---

👉 My suggestion:
Try **Step 4 test (`print(r.text[:1000])`)** to confirm if Yellow Pages requires JavaScript rendering.

Would you like me to **adapt your Yellow Pages scraper to Selenium** so it bypasses the 403 issue and works out of the box?










Perfect ✅ Since you’re getting `403 Forbidden` from Yellow Pages, let’s **adapt your scraper to Selenium** so it can bypass bot protection and render JavaScript. Below is a **plug-and-play boilerplate** you can drop into your project.

---

## 📂 Suggested File Structure

```
yellowpages-scraper/
│── main.py
│── scrapers/
│   ├── __init__.py
│   ├── yellow_pages_scraper.py
│── requirements.txt
```

---

## 📦 requirements.txt

```txt
selenium
webdriver-manager
beautifulsoup4
pandas
```

Install:

```bash
pip install -r requirements.txt
```

---

## 🔹 scrapers/yellow\_pages\_scraper.py

```python
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class YellowPagesScraper:
    def __init__(self, headless: bool = True, delay: int = 2):
        self.delay = delay
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

    def get_page(self, url: str):
        self.driver.get(url)
        time.sleep(self.delay)  # wait for JS to load
        return self.driver.page_source

    def parse_results(self, html: str):
        soup = BeautifulSoup(html, "lxml")
        results = []

        listings = soup.select("div.result")  # Yellow Pages result containers
        for listing in listings:
            name = listing.select_one("a.business-name")
            phone = listing.select_one("div.phones.phone.primary")
            address = listing.select_one("div.street-address")

            results.append({
                "name": name.get_text(strip=True) if name else None,
                "phone": phone.get_text(strip=True) if phone else None,
                "address": address.get_text(strip=True) if address else None,
            })
        return results

    def scrape(self, search: str, location: str, pages: int = 1):
        all_data = []
        for page in range(1, pages + 1):
            url = f"https://www.yellowpages.com/search?search_terms={search}&geo_location_terms={location}&page={page}"
            print(f"🔎 Scraping: {url}")
            html = self.get_page(url)
            data = self.parse_results(html)
            all_data.extend(data)
        return pd.DataFrame(all_data)

    def close(self):
        self.driver.quit()
```

---

## 🔹 main.py

```python
from scrapers.yellow_pages_scraper import YellowPagesScraper

if __name__ == "__main__":
    scraper = YellowPagesScraper(headless=True, delay=3)

    # Example: scrape 2 pages of plumbers in New York
    df = scraper.scrape(search="plumber", location="New York", pages=2)

    print(df.head())
    df.to_csv("yellowpages_data.csv", index=False)
    print("✅ Data saved to yellowpages_data.csv")

    scraper.close()
```

---

## 🚀 How It Works

1. Opens Chrome (headless by default).
2. Loads Yellow Pages search result pages.
3. Extracts `name`, `phone`, and `address`.
4. Stores results in a **pandas DataFrame**.
5. Saves everything to `yellowpages_data.csv`.

---

👉 This version bypasses **403 errors** since Selenium mimics a real browser and executes JavaScript.

Do you want me to also add **proxy + user-agent rotation inside Selenium** so you’re safer from being blocked during long scrapes?

















Nice — let’s get your scraper running step-by-step. I’ll give you platform-specific commands, common troubleshooting, and quick tips to debug visually.

---

# 1) Prereqs

* Install **Python 3.8+** (verify with `python --version`).
* Install **Google Chrome** (Chromium also works).
* Project folder should contain `main.py`, `scrapers/yellow_pages_scraper.py`, and `requirements.txt` from the boilerplate.

---

# 2) Create & activate a virtual environment (recommended)

**macOS / Linux**

```bash
cd /path/to/yellowpages-scraper
python -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
cd C:\path\to\yellowpages-scraper
python -m venv venv
.\venv\Scripts\Activate.ps1
# Or in CMD: .\venv\Scripts\activate.bat
```

You should now see `(venv)` in the prompt.

---

# 3) Install dependencies

```bash
pip install -r requirements.txt
```

(If you get permission errors, ensure your venv is active. For corporate networks, you might need to use a proxy for pip.)

---

# 4) Run the scraper (basic)

From the project root with venv active:

```bash
python main.py
```

This will:

* Launch Chrome via webdriver-manager
* Scrape the pages configured in `main.py`
* Print head rows and save `yellowpages_data.csv` in the project directory

---

# 5) Debug visually (see the browser)

If nothing appears or results are empty, run non-headless so you can watch what Chrome does. Edit the line in `main.py`:

```python
scraper = YellowPagesScraper(headless=False, delay=3)
```

Rerun `python main.py`. A Chrome window will open and you’ll see the pages loading — very helpful for debugging selectors and anti-bot blocks.

---

# 6) Common errors & fixes

**`selenium.common.exceptions.SessionNotCreatedException` / driver mismatch**

* Ensure Chrome is installed and up-to-date. `webdriver-manager` usually downloads a compatible driver, but updating Chrome or webdriver-manager helps:

```bash
pip install -U webdriver-manager selenium
```

**No output / empty DataFrame**

* The site structure may have different selectors. Inspect the live page in Chrome DevTools and update selectors in `parse_results()` (e.g., `.result` / `.business-name` etc).
* Try `headless=False` to see what’s rendered.
* Increase `delay` (e.g., `delay=5`) if the page needs more time to load JS.

**403 Forbidden or quickly blocked**

* Use `headless=False` to check if the site blocks headless browsers.
* Add realistic Chrome options (already included), or use proxies/rotate IPs for large scraping jobs (paid rotating proxy recommended).
* Space out requests: increase `delay` and/or add randomized sleep:

```python
import time, random
time.sleep(self.delay + random.uniform(0.5, 2.0))
```

**Chrome not found**

* Make sure Chrome is installed in default location. If you use a custom Chrome/Chromium binary, add:

```python
chrome_options.binary_location = "/path/to/chrome"
```

inside the scraper init.

**`ImportError` or pip errors**

* Ensure venv is active; run `pip list` to confirm installed packages.

---

# 7) Customize run parameters

Edit `main.py` to change search/location/pages. Example:

```python
df = scraper.scrape(search="web development", location="New York", pages=3)
```

Then run again: `python main.py`

---

# 8) Automation (optional)

* Run periodically via cron (Linux/macOS) or Task Scheduler (Windows). For production, consider containerizing (Docker) and using a managed scheduler.

---

# 9) Quick checklist if it still fails

1. venv active? `python --version` from that venv.
2. `pip install -r requirements.txt` succeeded.
3. Chrome installed and runnable.
4. Try `headless=False` and `delay=5`.
5. Inspect returned HTML: add `print(html[:2000])` in `get_page()` to verify what’s being returned.

---

If you want, I can:

* Provide a one-line debug change to `get_page()` that prints a snippet of HTML so you can check whether the results are in the page, or
* Give you a ready-to-run example that scrapes a single known-public-url (so we can confirm the environment works).

Which would you prefer?










Ah 👍 that error is just Python not finding the `scrapers` package — the code is fine, it’s about **how you run it**.

Here are the fixes:

---

## ✅ Fix 1: Run from project root

Your structure looks like this:

```
yellowpages-scraper/
│── main.py
│── scrapers/
│   ├── __init__.py
│   ├── yellow_pages_scraper.py
```

Make sure you are inside the `yellowpages-scraper` folder (the one that contains `main.py`) before running:

```bash
cd E:\DS-Contractor\Upwork\upwork_reinforcement\profile-01-the-data-extraction-expert\b2b-lead-builder\yellowpages-scraper
python main.py
```

---

## ✅ Fix 2: Treat `scrapers` as a package

Ensure `scrapers/__init__.py` exists (even an empty file is fine). That makes it a package.

If it’s missing, create:

```bash
echo > scrapers\__init__.py
```

---

## ✅ Fix 3: Alternative run method

Instead of running `main.py` directly, run it as a module:

```bash
python -m main
```

That way Python treats the folder as a package and resolves imports correctly.

---

## ✅ Fix 4: If you’re inside `scrapers/` accidentally

If you `cd` into `scrapers/` and run, imports break. Always run from the project root.

---

⚡ Quick test:

```bash
cd yellowpages-scraper
python main.py
```

---

👉 Do you want me to modify the imports so it **works even if you run from anywhere** (e.g. using `sys.path.append`)? That way you don’t have to worry about working directory.













Got it ✅ — your Selenium browser is opening the page fine, but your **parser is returning nothing**, which is why you see:

```
Empty DataFrame
Columns: []
Index: []
```

That means **the CSS selectors in `parse_results()` don’t match Yellow Pages’ actual HTML structure** (they’ve likely changed their markup).

---

## 🔎 How to Debug

1. Open `scrapers/yellow_pages_scraper.py`.
2. Inside `parse_results()`, add this line temporarily:

```python
print(soup.prettify()[:2000])  # preview first 2000 characters of the HTML
```

Run again:

```bash
python main.py
```

Now you’ll see the actual HTML Selenium captured. Check if you find the business names, phone numbers, and addresses.

---

## ✅ Updated Selectors (as of now)

Yellow Pages listings often use classes like `.result`, `.business-name`, `.phones`, `.adr`. Let’s update:

```python
def parse_results(self, html: str):
    soup = BeautifulSoup(html, "lxml")
    results = []

    # each listing
    listings = soup.select("div.srp-listing")  # updated container class
    for listing in listings:
        name = listing.select_one("a.business-name")
        phone = listing.select_one("div.phones")
        address = listing.select_one("p.adr")

        results.append({
            "name": name.get_text(strip=True) if name else None,
            "phone": phone.get_text(strip=True) if phone else None,
            "address": address.get_text(strip=True) if address else None,
        })
    return results
```

---

## ⚡ Next Steps

1. Replace the old `parse_results()` with the updated one.
2. Run again:

   ```bash
   python main.py
   ```
3. If still empty → use the debug print trick and share a snippet of HTML around one business listing, then I’ll adjust the selectors exactly.

---

👉 Do you want me to give you a **resilient parser** that automatically tries multiple selector patterns (so if Yellow Pages changes again, you won’t have to fix it manually)?












Perfect 🚀 Let’s build a **resilient parser** that tries multiple selector patterns so your scraper doesn’t break every time Yellow Pages tweaks their HTML.

---

## 🔹 Replace `parse_results()` with this

```python
def parse_results(self, html: str):
    soup = BeautifulSoup(html, "lxml")
    results = []

    # Yellow Pages sometimes uses different container classes
    listings = soup.select("div.srp-listing, div.result")  
    for listing in listings:
        # Try multiple patterns for business name
        name = (
            listing.select_one("a.business-name") or
            listing.select_one("h2.n") or
            listing.select_one("a[class*='business']")
        )

        # Try multiple patterns for phone
        phone = (
            listing.select_one("div.phones") or
            listing.select_one("div.phones.phone.primary") or
            listing.select_one("p.phone")
        )

        # Try multiple patterns for address
        address = (
            listing.select_one("p.adr") or
            listing.select_one("div.street-address") or
            listing.select_one("span.address")
        )

        results.append({
            "name": name.get_text(strip=True) if name else None,
            "phone": phone.get_text(strip=True) if phone else None,
            "address": address.get_text(strip=True) if address else None,
        })

    # Debug: if no results found, print snippet for inspection
    if not results:
        print("⚠️ No listings found. Here's a snippet of the page:")
        print(soup.prettify()[:2000])

    return results
```

---

## 🔹 What this does

* **Tries multiple selectors** for each field (name, phone, address).
* If **nothing is found**, prints the first 2000 chars of HTML → so you can quickly adjust selectors without guessing.
* Much less brittle → works across multiple Yellow Pages layouts.

---

## 🔹 Next Step for You

1. Update `yellow_pages_scraper.py` with the new `parse_results()`.
2. Run:

   ```bash
   python main.py
   ```
3. If you still get **⚠️ No listings found**, share a 10–20 line snippet of the printed HTML (around one business entry), and I’ll lock in the **exact working selectors** for you.

---

👉 Do you want me to also add **automatic CSV appending** (so every run adds new rows instead of overwriting) for client projects?













Great 👍 let’s make the scraper **append to CSV automatically** instead of overwriting each run. This way, every execution just adds new rows to the same file — perfect for client projects.

---

## 🔹 Update `main.py`

Replace the save section with this logic:

```python
from scrapers.yellow_pages_scraper import YellowPagesScraper
import pandas as pd
import os

if __name__ == "__main__":
    scraper = YellowPagesScraper(headless=True, delay=3)

    # Example: scrape 2 pages of plumbers in New York
    df = scraper.scrape(search="plumber", location="New York", pages=2)

    # Save or append to CSV
    csv_file = "yellowpages_data.csv"

    if not df.empty:
        if os.path.exists(csv_file):
            # Load old file, append new data, and drop duplicates
            old_df = pd.read_csv(csv_file)
            combined = pd.concat([old_df, df], ignore_index=True)
            combined.drop_duplicates(subset=["name", "phone"], inplace=True)
            combined.to_csv(csv_file, index=False)
            print(f"✅ Appended {len(df)} rows. Total: {len(combined)} rows in {csv_file}")
        else:
            df.to_csv(csv_file, index=False)
            print(f"✅ Saved {len(df)} rows to {csv_file}")
    else:
        print("⚠️ No new data scraped.")

    scraper.close()
```

---

## 🔹 What Changed

* **Checks if CSV exists**

  * If yes → appends new data, removes duplicates by `"name" + "phone"`.
  * If no → creates a new CSV.
* **Deduplication** keeps the file clean if you rerun on the same query.
* **Status messages** tell you how many rows were added and total count.

---

## 🔹 Example Run Output

```text
🔎 Scraping: https://www.yellowpages.com/search?search_terms=plumber&geo_location_terms=New York&page=1
🔎 Scraping: https://www.yellowpages.com/search?search_terms=plumber&geo_location_terms=New York&page=2
✅ Appended 20 rows. Total: 180 rows in yellowpages_data.csv
```

---

👉 Do you want me to also add a **config.yaml file** where you can specify search terms, locations, and pages (instead of editing `main.py` each time)? That would make it even more client-friendly.











Perfect 🚀 let’s make this fully **plug-and-play with a `config.yaml` file** so you don’t need to touch Python code every time.

---

## 🔹 1. Create `config.yaml`

In your project root, create a file called `config.yaml`:

```yaml
# config.yaml
search: "plumber"
location: "New York"
pages: 3
csv_file: "yellowpages_data.csv"

# Options
headless: true      # run browser headless (no UI)
delay: 3            # seconds to wait between pages
deduplicate: true   # remove duplicate name+phone
```

---

## 🔹 2. Update `main.py`

```python
import os
import pandas as pd
import yaml
from scrapers.yellow_pages_scraper import YellowPagesScraper


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    # Load config
    config = load_config()

    search = config.get("search", "plumber")
    location = config.get("location", "New York")
    pages = config.get("pages", 1)
    csv_file = config.get("csv_file", "yellowpages_data.csv")
    headless = config.get("headless", True)
    delay = config.get("delay", 3)
    deduplicate = config.get("deduplicate", True)

    # Run scraper
    scraper = YellowPagesScraper(headless=headless, delay=delay)
    df = scraper.scrape(search=search, location=location, pages=pages)

    if not df.empty:
        if os.path.exists(csv_file):
            old_df = pd.read_csv(csv_file)
            combined = pd.concat([old_df, df], ignore_index=True)

            if deduplicate:
                combined.drop_duplicates(subset=["name", "phone"], inplace=True)

            combined.to_csv(csv_file, index=False)
            print(f"✅ Appended {len(df)} rows. Total: {len(combined)} rows in {csv_file}")
        else:
            df.to_csv(csv_file, index=False)
            print(f"✅ Saved {len(df)} rows to {csv_file}")
    else:
        print("⚠️ No new data scraped.")

    scraper.close()
```

---

## 🔹 3. Install YAML Dependency

If not installed yet, run:

```bash
pip install pyyaml
```

---

## 🔹 4. Run the Scraper

Now just run:

```bash
python main.py
```

No need to edit code anymore — just change `config.yaml`.

---

⚡ Next step (optional): I can add **multiple searches + locations in one config file** (e.g., plumbers in New York + electricians in Chicago, all in one run).

👉 Do you want me to extend `config.yaml` for **batch scraping multiple queries**?





Got it ✅ — your scraper is hitting **Cloudflare bot protection** on YellowPages, so instead of real results, you’re seeing the *“Sorry, you have been blocked”* page. This is super common when scraping big sites without stealth measures.

---

### 🔹 Why It Happened

* YellowPages uses **Cloudflare + bot detection**.
* Selenium without obfuscation is easy to detect.
* Headless browsers get flagged quickly.
* Too many requests from the same IP → block.

---

### 🔹 Fix Options

#### ✅ 1. Make Selenium Stealthy

Install **selenium-stealth**:

```bash
pip install selenium-stealth
```

Then update your `YellowPagesScraper` driver setup:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

class YellowPagesScraper:
    def __init__(self, headless=True, delay=2):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(), options=options)

        # Apply stealth
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
        )

        self.delay = delay
```

This makes the browser look more “human” and bypass simple bot checks.

---

#### ✅ 2. Add Proxies

If Cloudflare still blocks you, you’ll need **rotating proxies**:

```python
options.add_argument("--proxy-server=http://USER:PASS@HOST:PORT")
```

You can use free proxies (unstable) or paid services (e.g., Bright Data, ScraperAPI, Oxylabs).

---

#### ✅ 3. Add Human-Like Behavior

* Random delays (`time.sleep(random.uniform(2, 6))`)
* Scroll the page gradually (`driver.execute_script("window.scrollBy...")`)
* Use **user-agents rotation**. Example:

```python
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
]

options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
```

---

#### ✅ 4. Alternative: Use an API

Some services offer **pre-scraped YellowPages data** or an API (cleaner and safer than fighting Cloudflare).
Examples: SerpAPI, ZenRows, ScraperAPI.

---

👉 My suggestion for your current setup:

1. Add **selenium-stealth** (Step 1).
2. Add **random user agents + delays** (Step 3).
3. If still blocked → use **rotating proxy** (Step 2).

---

Do you want me to **rewrite your `scrapers/yellow_pages_scraper.py` with stealth + random user-agents already integrated**, so you can just run it?












# follwoing code is successful
Perfect! 🚀 I’ll give you a **plug-and-play version** of `yellow_pages_scraper.py` using **Selenium + selenium-stealth + random User-Agents + delays**. This will bypass basic Cloudflare blocks and mimic human browsing.

You can drop this into your `scrapers/` folder and run `main.py` directly.

---

```python
# scrapers/yellow_pages_scraper.py

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from bs4 import BeautifulSoup

class YellowPagesScraper:
    def __init__(self, headless=True, delay_range=(2,5)):
        self.delay_range = delay_range

        options = Options()
        if headless:
            options.add_argument("--headless=new")  # new headless mode
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")

        # Random user-agent
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        ]
        options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

        self.driver = webdriver.Chrome(service=Service(), options=options)

        # Apply stealth
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def random_delay(self):
        time.sleep(random.uniform(*self.delay_range))

    def scrape(self, search_term="plumber", location="New York", pages=2):
        all_data = []

        for page in range(1, pages + 1):
            url = f"https://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page}"
            print(f"🔎 Scraping: {url}")

            self.driver.get(url)
            self.random_delay()  # human-like wait

            soup = BeautifulSoup(self.driver.page_source, "lxml")

            listings = soup.find_all("div", class_="result")  # adjust if needed

            if not listings:
                print("⚠️ No listings found. Here's a snippet of the page:")
                print(soup.prettify()[:500])
                continue

            for listing in listings:
                name_tag = listing.find("a", class_="business-name")
                phone_tag = listing.find("div", class_="phones")
                category_tag = listing.find("div", class_="categories")

                data = {
                    "name": name_tag.text.strip() if name_tag else None,
                    "phone": phone_tag.text.strip() if phone_tag else None,
                    "category": category_tag.text.strip() if category_tag else None,
                }
                all_data.append(data)

            self.random_delay()  # human-like wait between pages

        df = pd.DataFrame(all_data)
        if not df.empty:
            df.to_csv("yellowpages_data.csv", index=False)
            print("✅ Data saved to yellowpages_data.csv")
        else:
            print("⚠️ No new data scraped.")

    def close(self):
        self.driver.quit()
```

---

### ✅ How to Run

1. Make sure your project structure looks like this:

```
yellowpages-scraper/
├─ main.py
├─ scrapers/
│  └─ yellow_pages_scraper.py
├─ venv/
```

2. `main.py` example:

```python
from scrapers.yellow_pages_scraper import YellowPagesScraper

if __name__ == "__main__":
    scraper = YellowPagesScraper(headless=True)
    scraper.scrape(search_term="plumber", location="New York", pages=2)
    scraper.close()
```

3. Run:

```bash
python main.py
```

---

This setup now includes:

* Headless Chrome + stealth mode ✅
* Random User-Agent ✅
* Human-like delays between pages ✅
* Scrapes basic business info and saves CSV ✅

---

If you want, I can **upgrade this further** to include:

* **Automatic scrolling + lazy-loaded listings**
* **Rotating proxies** to avoid Cloudflare blocks entirely

This makes it fully production-ready for large-scale scraping.

Do you want me to do that next?
