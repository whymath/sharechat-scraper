import os
from dotenv import load_dotenv
load_dotenv() 

# UPDATE AS REQUIRED
scraper_params = {"USER_ID": os.environ.get("SHARECHAT_USER_ID"),
                  "PASSCODE": os.environ.get("SHARECHAT_PASSWORD"), 
                  "scrape_by_type": True,
                  "MORE_PAGES": 3,
                  "tag_hashes": ["ekz6a8", "pkArae", "Wm3D1", "0eXrv", "Ay8xa"]
                  }



