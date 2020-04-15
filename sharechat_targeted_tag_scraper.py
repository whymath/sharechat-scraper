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

# Main function
def sharechat_targeted_tag_scraper():
    start_time = time.time()
    # Scrape data from tags
    try:
        sharechat_df = sharechat_helper.get_data(tag_hashes=scraper_params["tag_hashes"],
                                                 USER_ID=scraper_params["USER_ID"],
                                                 PASSCODE=scraper_params["PASSCODE"],
                                                 MORE_PAGES=scraper_params["MORE_PAGES"], 
                                                 scrape_by_type=scraper_params["scrape_by_type"])
        # Save data to S3 & Mongo DB
        if len(sharechat_df) < 1:
            print("No posts scraped!")
        else:
            s3UploadSuccess = False
            try:
                sharechat_df = sharechat_helper.sharechat_s3_upload(sharechat_df) # the returned df includes s3 urls
                s3UploadSuccess = True
                print("Data uploaded to S3")
            except Exception:
                print("S3 upload failed")
                pass
            if s3UploadSuccess:
                try:
                    sharechat_helper.sharechat_mongo_upload(sharechat_df)
                    print("Data uploaded to Mongo")            
                except Exception:
                    print("Mongo upload failed")
                    pass 
                try:
                    sharechat_df_html = sharechat_helper.convert_links_to_thumbnails(sharechat_df)
                    print("HTML file created")
                    with open("sharechat_data_preview.html", "w") as f:
                        f.write(sharechat_df_html.data)
                except Exception:
                    print("HTML file creation failed")
                    pass 
            else:
                pass   
            try:
                sharechat_df.to_csv("sharechat_data.csv")
                print("{} posts scraped and saved".format(len(sharechat_df)))
            except Exception:
                print("csv file creation failed")
            print("Time taken: %s seconds" % (time.time() - start_time))
            return sharechat_df
    except Exception:
        print("Failed to get tag data")
    
    


# Run scraper
if __name__ == "__main__":
    sharechat_targeted_tag_scraper()
