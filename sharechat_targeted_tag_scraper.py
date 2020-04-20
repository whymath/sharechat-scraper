# API scraper for targeted tag
# Import libraries
import os
import config 
from config import scraper_params
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
import tempfile
from tempfile import mkdtemp
import shutil
import subprocess
import logging

# Main function
def sharechat_targeted_tag_scraper():
    start_time = time.time()
    # Initialize S3 and Mongo DB 
    initializationSuccess = False
    try:
        aws, bucket, s3 = s3_mongo_helper.initialize_s3()
        coll = s3_mongo_helper.initialize_mongo()
        initializationSuccess = True
    except Exception as e:
        print("Initialization failure")
        print(logging.traceback.format_exc())
    # Scrape data from Sharechat tags
    if initializationSuccess:
        sharechat_df = sharechat_helper.get_data(tag_hashes=scraper_params["tag_hashes"],
                                                USER_ID=scraper_params["USER_ID"],
                                                PASSCODE=scraper_params["PASSCODE"],
                                                TRENDING_PAGES=scraper_params["TRENDING_PAGES"], 
                                                FRESH_PAGES=scraper_params["FRESH_PAGES"], 
                                                scrape_by_type=scraper_params["scrape_by_type"],
                                                scrape_by_timestamp=scraper_params["scrape_by_timestamp"],
                                                unix_timestamp=scraper_params["unix_timestamp"])
        
        if len(df) < 1: 
            raise ValueError("get_data() returned empty dataframe. No posts were scraped.")
        else:
            # Save data to S3 & Mongo DB
            s3UploadSuccess = False
            try:
                sharechat_df = sharechat_helper.sharechat_s3_upload(sharechat_df, aws, bucket, s3) # the returned df includes s3 urls
                s3UploadSuccess = True
                print("Data uploaded to S3")
            except Exception as e:
                print("S3 upload failed")
                print(logging.traceback.format_exc())
                pass
            if s3UploadSuccess:
                try: 
                    sharechat_df, sharechat_df_html = sharechat_helper.get_thumbnails(sharechat_df)
                    with open("sharechat_data_preview.html", "w") as f:
                        f.write(sharechat_df_html.data)
                        print("HTML preview file created")
                except Exception as e:
                    print("HTML preview file creation failed")
                    print(logging.traceback.format_exc())
                    pass 
                try:
                    sharechat_helper.sharechat_mongo_upload(sharechat_df, coll)
                    print("Data uploaded to Mongo")            
                except Exception as e:
                    print("Mongo upload failed")
                    print(logging.traceback.format_exc())
                    pass  
            else:
                pass   
            try:
                sharechat_df.to_csv("sharechat_data.csv")
                print("CSV file created")
                print("{} posts scraped".format(len(sharechat_df)))
            except Exception as e:
                print("CSV file creation failed")
                print(logging.traceback.format_exc())
                pass
            print("Time taken: %s seconds" % (time.time() - start_time))
            return sharechat_df

    
    


# Run scraper
if __name__ == "__main__":
    sharechat_targeted_tag_scraper()
