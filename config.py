import os
from dotenv import load_dotenv
load_dotenv() 
from manager import scraper_manager

# UPDATE AS REQUIRED
scraper_params = {
    "USER_ID": os.environ.get("SHARECHAT_USER_ID"),
    "PASSCODE": os.environ.get("SHARECHAT_PASSWORD"), 
    "tag_hashes": ["5anPZA", "3NZwyK", "3NE91Z", "X6Pxqx", # tags to scrape
    "pkArae", "grGlpz", "GEpNKd", "0eXrv", "Kyweq"],
    "content_to_scrape": "virality", # trending / fresh / virality / ml
    "pages": 2, # used when content_to_scrape == trending / fresh / ml
    "unix_timestamp": "1587034967", # used when content_to_scrape == fresh
    "data_path": "/Users/kruttikanadig/Documents/Tattle/sharechat-scraper/sharechat_data.csv", # used when content_to_scrape == virality
    }


if __name__ == "__main__":
    scraper_manager(scraper_params)
