import os
from dotenv import load_dotenv
load_dotenv() 
from manager import scraper_manager

# UPDATE AS REQUIRED
scraper_params = {
    "USER_ID": os.environ.get("SHARECHAT_USER_ID"),
    "PASSCODE": os.environ.get("SHARECHAT_PASSWORD"), 
    "tag_hashes": [],
    "content_to_scrape": "virality", # trending / fresh / virality / ml
    "pages": 2, # used when content_to_scrape == trending / fresh / ml
    "unix_timestamp": "", # used when content_to_scrape == fresh
    "data_path": "", # used when content_to_scrape == virality
    }


if __name__ == "__main__":
    scraper_manager(scraper_params)
