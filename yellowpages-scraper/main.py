# # from scrapers.yellow_pages_scraper import YellowPagesScraper

# # if __name__ == "__main__":
# #     scraper = YellowPagesScraper(headless=True, delay=3)

# #     # Example: scrape 2 pages of plumbers in New York
# #     df = scraper.scrape(search="plumber", location="New York", pages=2)

# #     print(df.head())
# #     df.to_csv("yellowpages_data.csv", index=False)
# #     print("✅ Data saved to yellowpages_data.csv")

# #     scraper.close()


# from scrapers.yellow_pages_scraper import YellowPagesScraper
# import pandas as pd
# import os

# if __name__ == "__main__":
#     scraper = YellowPagesScraper(headless=True, delay=3)

#     # # Example: scrape 2 pages of plumbers in New York
#     # df = scraper.scrape(search="plumber", location="New York", pages=2)

#     # # Save or append to CSV
#     # csv_file = "yellowpages_data.csv"

#     # if not df.empty:
#     #     if os.path.exists(csv_file):
#     #         # Load old file, append new data, and drop duplicates
#     #         old_df = pd.read_csv(csv_file)
#     #         combined = pd.concat([old_df, df], ignore_index=True)
#     #         combined.drop_duplicates(subset=["name", "phone"], inplace=True)
#     #         combined.to_csv(csv_file, index=False)
#     #         print(f"✅ Appended {len(df)} rows. Total: {len(combined)} rows in {csv_file}")
#     #     else:
#     #         df.to_csv(csv_file, index=False)
#     #         print(f"✅ Saved {len(df)} rows to {csv_file}")
#     # else:
#     #     print("⚠️ No new data scraped.")

#     # scraper.close()

#     scraper.scrape(search_term="plumber", location="New York", pages=2)
#     scraper.close()

from scrapers.yellow_pages_scraper import YellowPagesScraper

if __name__ == "__main__":
    scraper = YellowPagesScraper(headless=True)
    scraper.scrape(search_term="plumber", location="New York", pages=2)
    scraper.close()
