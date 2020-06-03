import os 
from dotenv import load_dotenv
load_dotenv() 
from manager import scraper_manager

# UPDATE AS REQUIRED
scraper_params = {
    "USER_ID": os.environ.get("SHARECHAT_USER_ID"),
    "PASSCODE": os.environ.get("SHARECHAT_PASSWORD"), 
    "tag_hashes": ["", ""], # insert tag hashes as strings
    "content_to_scrape": "trending", # select one from: trending / fresh / virality / ml
"pages": 1, # used when content_to_scrape == trending / fresh / ml
    "unix_timestamp": "", # 10 digit unix timestamp. used when content_to_scrape == fresh
    "data_path": "", # path to existing Sharechat data csv. used when content_to_scrape == virality
    "mode": "local" # select from: local / archive
    }


if __name__ == "__main__":
    scraper_manager(scraper_params)
