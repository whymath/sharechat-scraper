from manager import scraper_manager
import os
from dotenv import load_dotenv
load_dotenv()

scraper_params = {
    "USER_ID": os.environ.get("SHARECHAT_USER_ID"),
    "PASSCODE": os.environ.get("SHARECHAT_PASSWORD"),
    "tag_hashes": ["5anPZA", "Kyweq", "njWVe", "6aj68", "e5jM8", "0eXrv", "EXG63e",
    "Dek4p", "PP0Vz", "n4xXd", "jRRG6k", "B04WOk", "grNEGQ", "0z1aV3"],
    "bucket_ids": [],
    "content_to_scrape": "trending",
    "pages": 1,
    "unix_timestamp": "",
    "data_path": "",
    "mode": "local",
    "targeting": "tag",
    "is_cron_job": True
}


if __name__ == "__main__":
    scraper_manager(scraper_params)
