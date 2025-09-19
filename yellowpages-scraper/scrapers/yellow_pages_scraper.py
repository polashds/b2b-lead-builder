# import time
# import pandas as pd
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager


# class YellowPagesScraper:
#     def __init__(self, headless: bool = True, delay: int = 2):
#         self.delay = delay
#         chrome_options = Options()
#         if headless:
#             chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("start-maximized")
#         chrome_options.add_argument("disable-infobars")
#         chrome_options.add_argument("--disable-extensions")

#         self.driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=chrome_options,
#         )

#     def get_page(self, url: str):
#         self.driver.get(url)
#         time.sleep(self.delay)  # wait for JS to load
#         return self.driver.page_source

#     # def parse_results(self, html: str):
#     #     soup = BeautifulSoup(html, "lxml")
#     #     results = []

#     #     listings = soup.select("div.result")  # Yellow Pages result containers
#     #     for listing in listings:
#     #         name = listing.select_one("a.business-name")
#     #         phone = listing.select_one("div.phones.phone.primary")
#     #         address = listing.select_one("div.street-address")

#     #         results.append({
#     #             "name": name.get_text(strip=True) if name else None,
#     #             "phone": phone.get_text(strip=True) if phone else None,
#     #             "address": address.get_text(strip=True) if address else None,
#     #         })
#     #     return results

#     # def parse_results(self, html: str):
#     #     soup = BeautifulSoup(html, "lxml")
#     #     results = []

#     #     # each listing
#     #     listings = soup.select("div.srp-listing")  # updated container class
#     #     for listing in listings:
#     #         name = listing.select_one("a.business-name")
#     #         phone = listing.select_one("div.phones")
#     #         address = listing.select_one("p.adr")

#     #         results.append({
#     #             "name": name.get_text(strip=True) if name else None,
#     #             "phone": phone.get_text(strip=True) if phone else None,
#     #             "address": address.get_text(strip=True) if address else None,
#     #         })
#     #     return results

#     def parse_results(self, html: str):
#         soup = BeautifulSoup(html, "lxml")
#         results = []

#         # Yellow Pages sometimes uses different container classes
#         listings = soup.select("div.srp-listing, div.result")  
#         for listing in listings:
#             # Try multiple patterns for business name
#             name = (
#                 listing.select_one("a.business-name") or
#                 listing.select_one("h2.n") or
#                 listing.select_one("a[class*='business']")
#             )

#             # Try multiple patterns for phone
#             phone = (
#                 listing.select_one("div.phones") or
#                 listing.select_one("div.phones.phone.primary") or
#                 listing.select_one("p.phone")
#             )

#             # Try multiple patterns for address
#             address = (
#                 listing.select_one("p.adr") or
#                 listing.select_one("div.street-address") or
#                 listing.select_one("span.address")
#             )

#             results.append({
#                 "name": name.get_text(strip=True) if name else None,
#                 "phone": phone.get_text(strip=True) if phone else None,
#                 "address": address.get_text(strip=True) if address else None,
#             })

#         # Debug: if no results found, print snippet for inspection
#         if not results:
#             print("⚠️ No listings found. Here's a snippet of the page:")
#             print(soup.prettify()[:2000])

#         return results



#     def scrape(self, search: str, location: str, pages: int = 1):
#         all_data = []
#         for page in range(1, pages + 1):
#             url = f"https://www.yellowpages.com/search?search_terms={search}&geo_location_terms={location}&page={page}"
#             print(f"🔎 Scraping: {url}")
#             html = self.get_page(url)
#             data = self.parse_results(html)
#             all_data.extend(data)
#         return pd.DataFrame(all_data)

#     def close(self):
#         self.driver.quit()



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
