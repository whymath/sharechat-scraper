from manager import scraper_manager
import os
from dotenv import load_dotenv
load_dotenv()

scraper_params = {
    "USER_ID": os.environ.get("SHARECHAT_USER_ID"),
    "PASSCODE": os.environ.get("SHARECHAT_PASSWORD"),
    "tag_hashes": [],
    "bucket_ids": ["125", "1284", "371", "1075", "1274", "515", "1244", "1281", "648", "127"],
    "content_to_scrape": "trending",
    "pages": 2,
    "unix_timestamp": "",
    "data_path": "",
    "mode": "archive",
    "targeting": "bucket",
    "is_cron_job": True
}


if __name__ == "__main__":
    scraper_manager(scraper_params)
