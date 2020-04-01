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

# Parameters for API scraper - update as required
USER_ID = os.environ.get("SHARECHAT_USER_ID")
PASSCODE = os.environ.get("SHARECHAT_PASSWORD")
temp_tag_hashes = ["1RgBZQ", "5anPZA", "3NE91Z", 
                    "pkArae", "X6Pxqx", "3NZwyK", 
                    "EXrjQQ", "Wvmx9m"]  # CHANGE AS REQUIRED
PAGES = 2 # numbers of pages to scrape

aws, bucket, s3 = s3_mongo_helper.initialize_s3()
cli, db, coll = s3_mongo_helper.initialize_mongo()

# Scraper-specific data saving functions
def sharechat_s3_upload(df):
    for index, row in df.iterrows():
        if (row["media_type"] == "image"):
                # Create S3 file name 
            name = row["filename"]+".jpg"
                # Get media
            temp = wget.download(row["media_link"])
                # Upload media to S3
            s3_mongo_helper.upload_to_s3(s3=s3, file=temp, filename=name, bucket=bucket, content_type=row["media_type"])
            os.remove(temp)
                # Create S3 URL
            url = aws+bucket+"/"+name
                # Add S3 url to dataframe
            df.at[index, "s3_url"] = url
        else:
                # Create S3 file name
            name = row["filename"]+".mp4"
                # Get media
            temp = wget.download(row["media_link"])
                # Upload media to S3
            s3_mongo_helper.upload_to_s3(s3=s3, file=temp, filename=name, bucket=bucket, content_type=row["media_type"])
            os.remove(temp)
                # Create S3 URL
            url = aws+bucket+"/"+name
                # Add S3 url to dataframe
            df.at[index, "s3_url"] = url
    return df # return df with s3 urls added

def sharechat_mongo_upload(df):
    for i in df.to_dict("records"):
        s3_mongo_helper.upload_to_mongo(data=i, coll=coll) 


# Main function
def sharechat_targeted_tag_scraper(temp_tag_hashes):
    start_time = time.time()
    # Scrape data from tags
    sharechat_df = sharechat_helper.get_data(temp_tag_hashes, USER_ID, PASSCODE, PAGES)
    # Save data to S3 & Mongo DB
    complete_df = sharechat_s3_upload(sharechat_df) # this df includes the s3 urls
    sharechat_mongo_upload(complete_df)
    complete_df_html = sharechat_helper.convert_links_to_thumbnails(complete_df)
    sharechat_helper.save_data_to_disk(complete_df, complete_df_html)
    print("")
    print("{} posts scraped and saved".format(len(complete_df)))
    print("Time taken: %s seconds" % (time.time() - start_time))
    return complete_df

# Run scraper
if __name__ == "__main__":
    sharechat_targeted_tag_scraper(temp_tag_hashes)
