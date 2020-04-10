# API scraper for targeted tag
# Import libraries
import os
import requests
import pandas as pd
import numpy as np
import re
import datetime
from datetime import datetime
from IPython.display import Image, HTML
import time
from time import sleep
from random import uniform
import json
import urllib
import uuid
import boto
import boto3
from boto3 import client
from PIL import Image
import io
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
load_dotenv() 
import wget
import sharechat_helper
import s3_mongo_helper 

USER_ID = os.environ.get("SHARECHAT_USER_ID")
PASSCODE = os.environ.get("SHARECHAT_PASSWORD")
temp_tag_hashes = ["5anPZA", "3NE91Z", 
                   "pkArae", "X6Pxqx", "3NZwyK", 
                    "EXrjQQ", "Wvmx9m", "0zw6BG"]  # CHANGE AS REQUIRED
MORE_PAGES = 1 # number of pages to scrape in addition to landing page
scrape_by_type = True 

# Main function
def sharechat_targeted_tag_scraper(temp_tag_hashes):
    start_time = time.time()
    # Scrape data from tags
    sharechat_df = sharechat_helper.get_data(temp_tag_hashes, USER_ID, PASSCODE, MORE_PAGES, scrape_by_type=True)
    # Save data to S3 & Mongo DB
    if len(sharechat_df) > 0:
        complete_df = sharechat_helper.sharechat_s3_upload(sharechat_df) # this df includes the s3 urls
        sharechat_helper.sharechat_mongo_upload(complete_df)
        complete_df_html = sharechat_helper.convert_links_to_thumbnails(complete_df)
        sharechat_helper.save_data_to_disk(complete_df, complete_df_html)
        print("{} posts scraped and saved".format(len(complete_df)))
        print("Time taken: %s seconds" % (time.time() - start_time))
    else:
        print("No posts scraped!")
    return complete_df
    # sharechat_df_html = sharechat_helper.convert_links_to_thumbnails(sharechat_df)
    # sharechat_helper.save_data_to_disk(sharechat_df, sharechat_df_html)
    # print("Time taken: %s seconds" % (time.time() - start_time))
    #return sharechat_df

# Run scraper
if __name__ == "__main__":
    sharechat_targeted_tag_scraper(temp_tag_hashes)
