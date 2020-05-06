# Import libraries
import os
import requests
import pandas as pd
import numpy as np
import re
import datetime
from datetime import datetime, date
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
load_dotenv() 
import pymongo
from pymongo import MongoClient
import wget
import sharechat_helper
import s3_mongo_helper 
import tempfile
from tempfile import mkdtemp
import shutil
import subprocess
import logging
import pickle
from tqdm import tqdm

# Trending content scraper
def trending_content_scraper(USER_ID, PASSCODE, tag_hashes, pages):
    start_time = time.time()
    # Initialize S3 and Mongo DB 
    print("Initializing ...")
    initializationSuccess = False
    try:
        aws, bucket, s3 = s3_mongo_helper.initialize_s3()
        coll = s3_mongo_helper.initialize_mongo()
        initializationSuccess = True
        print("Initialized successfully")
    except Exception as e:
        print("Initialization failure")
        print(logging.traceback.format_exc())
    # Scrape data from Sharechat tags
    if initializationSuccess:
        print("Scraping in progress ...")
        sharechat_df = sharechat_helper.get_trending_data(
                                                USER_ID,
                                                PASSCODE,
                                                tag_hashes,
                                                pages)
        
        if len(sharechat_df) < 1: 
            raise ValueError("get_data() returned empty dataframe. No posts were scraped.")
        else:
            # Save data to S3 & Mongo DB
            s3UploadSuccess = False
            try:
                print("S3 upload in progress ...")
                sharechat_df = sharechat_helper.sharechat_s3_upload(sharechat_df, aws, bucket, s3) # the returned df includes s3 urls
                s3UploadSuccess = True
                print("Data uploaded to S3")
            except Exception as e:
                print("S3 upload failed")
                print(logging.traceback.format_exc())
                pass
            if s3UploadSuccess:
                try: 
                    print("HTML preview file creation in progress ...")
                    sharechat_df, sharechat_df_html = sharechat_helper.get_thumbnails(sharechat_df)
                    with open("sharechat_trending_data_preview.html", "w") as f:
                        f.write(sharechat_df_html.data)
                        print("HTML preview file created")
                except Exception as e:
                    print("HTML preview file creation failed")
                    print(logging.traceback.format_exc())
                    pass 
                try:
                    print("MongoDB upload in progress ...")
                    sharechat_helper.sharechat_mongo_upload(sharechat_df, coll)
                    print("Data uploaded to MongoDB")            
                except Exception as e:
                    print("MongoDB upload failed")
                    print(logging.traceback.format_exc())
                    pass  
            else:
                pass   
            try:
                print("CSV file creation in progress ... ")
                sharechat_df.to_csv("sharechat_trending_data.csv")
                print("CSV file created")
                print("{} posts scraped".format(len(sharechat_df)))
            except Exception as e:
                print("CSV file creation failed")
                print(logging.traceback.format_exc())
                pass
            print("Scraping complete")
            print("Time taken: %s seconds" % (time.time() - start_time))
            return sharechat_df

# Fresh content scraper
def fresh_content_scraper(USER_ID, PASSCODE, tag_hashes, pages, unix_timestamp):
    start_time = time.time()
    # Initialize S3 and Mongo DB 
    print("Initializing ...")
    initializationSuccess = False
    try:
        aws, bucket, s3 = s3_mongo_helper.initialize_s3()
        coll = s3_mongo_helper.initialize_mongo()
        initializationSuccess = True
        print("Initialized successfully")
    except Exception as e:
        print("Initialization failure")
        print(logging.traceback.format_exc())
    # Scrape data from Sharechat tags
    if initializationSuccess:
        print("Scraping in progress ...")
        sharechat_df = sharechat_helper.get_fresh_data(
                                                USER_ID,
                                                PASSCODE,
                                                tag_hashes,
                                                pages,
                                                unix_timestamp)


        if len(sharechat_df) < 1:          
            raise ValueError("get_data() returned empty dataframe. No posts were scraped.")
        else:
            # Save data to S3 & Mongo DB
            s3UploadSuccess = False
            try:
                print("S3 upload in progress ...")
                sharechat_df = sharechat_helper.sharechat_s3_upload(sharechat_df, aws, bucket, s3) # the returned df includes s3 urls
                s3UploadSuccess = True
                print("Data uploaded to S3")
            except Exception as e:
                print("S3 upload failed")
                print(logging.traceback.format_exc())
                pass
            if s3UploadSuccess:
                try: 
                    print("HTML preview file creation in progress ...")
                    sharechat_df, sharechat_df_html = sharechat_helper.get_thumbnails(sharechat_df)
                    with open("sharechat_fresh_data_preview.html", "w") as f:
                        f.write(sharechat_df_html.data)
                        print("HTML preview file created")
                except Exception as e:
                    print("HTML preview file creation failed")
                    print(logging.traceback.format_exc())
                    pass 
                try:
                    print("MongoDB upload in progress ...")
                    sharechat_helper.sharechat_mongo_upload(sharechat_df, coll)
                    print("Data uploaded to MongoDB")            
                except Exception as e:
                    print("MongoDB upload failed")
                    print(logging.traceback.format_exc())
                    pass  
            else:
                pass   
            try:
                print("CSV file creation in progress ... ")
                sharechat_df.to_csv("sharechat_fresh_data.csv")
                print("CSV file created")
                print("{} posts scraped".format(len(sharechat_df)))
            except Exception as e:
                print("CSV file creation failed")
                print(logging.traceback.format_exc())
                pass
            print("Scraping complete")
            print("Time taken: %s seconds" % (time.time() - start_time))
            return sharechat_df

# ML scraper (modified version of trending content scraper)
def ml_scraper(USER_ID, PASSCODE, tag_hashes, pages):
    start_time = time.time()
    print("Initializing ...")
    initializationSuccess = False
    try:
        coll = sharechat_helper.ml_initialize_mongo()
        aws, bucket, s3 = sharechat_helper.ml_initialize_s3()
        initializationSuccess = True
        print("Initialized successfully")
    except Exception as e:
        print("Initialization failure")
        print(logging.traceback.format_exc())
    # Scrape data from tags
    if initializationSuccess:
        print("Scraping in progress ...")
        sharechat_df = sharechat_helper.get_trending_data(
                                                USER_ID,
                                                PASSCODE,
                                                tag_hashes,
                                                pages)
        # Save data to S3 
        if len(sharechat_df) < 1: 
            raise ValueError("get_data() returned empty dataframe. No posts were scraped.")
        else:
            s3UploadSuccess = False
            try:
                print("S3 upload in progress ... ")
                sharechat_df = sharechat_helper.ml_sharechat_s3_upload(sharechat_df, aws, bucket, s3) 
                s3UploadSuccess = True
                print("Data uploaded to S3")
            except Exception as e:
                print("S3 upload failed")
                print(logging.traceback.format_exc())
                pass
            if s3UploadSuccess:
                try: 
                    print("HTML preview file creation in progress ...")
                    sharechat_df, sharechat_df_html = sharechat_helper.get_thumbnails(sharechat_df)
                    with open("sharechat_ml_data_preview.html", "w") as f:
                        f.write(sharechat_df_html.data)
                        print("HTML preview file created")
                except Exception as e:
                    print("HTML preview file creation failed")
                    print(logging.traceback.format_exc())
                    pass 
                try:
                    print("MongoDB upload in progress ...")
                    sharechat_helper.sharechat_mongo_upload(sharechat_df, coll)
                    print("Data uploaded to MongoDB")            
                except Exception as e:
                    print("MongoDB upload failed")
                    print(logging.traceback.format_exc())
                    pass  
            else:
                pass
            try:
                print("CSV file creation in progress ... ")
                sharechat_df.to_csv("sharechat_ml_data.csv")
                print("CSV file created")
                print("{} posts scraped".format(len(sharechat_df)))
            except Exception as e:
                print("CSV file creation failed")
                print(logging.traceback.format_exc())
                pass
            print("Scraping complete")
            print("Time taken: %s seconds" % (time.time() - start_time))
            return sharechat_df
    
# Virality metrics scraper
def virality_scraper(USER_ID, PASSCODE, data_path):
    print("Loading data ...")
    start_time = time.time()
    # Load data
    df = pd.read_csv(data_path)
    df.reset_index(drop=True, inplace=True)
    today = str(date.today())
    # Get timestamp for day t
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    timestamp = df["timestamp"][0]
    # Calculate days since t
    diff = str((pd.Timestamp("today")-timestamp).days)
    # Initialize df to hold current metrics
    result_df = pd.DataFrame(columns = ["comments_t+"+diff,
                                         "external_shares_t+"+diff,
                                         "likes_t+"+diff,
                                         "reposts_t+"+diff,
                                         "views_t+"+diff])
    # Get current virality metrics for each post
    print("Scraping current virality metrics ...")
    failed = 0
    with tqdm(total=len(df)) as pbar:
        for i in df["post_permalink"]:
            try:
                result = sharechat_helper.get_current_metrics(USER_ID, PASSCODE, i)
                result_df = result_df.append(pd.DataFrame(result, 
                                                    columns = result_df.columns, 
                                                    ), sort = True)
                pbar.update(1)
            except Exception:
                result_df = result_df.append(pd.Series(), ignore_index=True)
                failed += 1
                pass
                pbar.update(1)
    # Add scraped metrics to data
    new_df = pd.concat([df.reset_index(drop=True), result_df.reset_index(drop=True)], axis = 1)
    # Save combined data
    "Saving scraped metrics ..."
    sharechat_helper.save_updated_df(new_df, today)
    total = len(df)
    print("Scraping complete")
    print("Updated virality metrics for {} out of {} posts".format(total-failed, total))
    print("Time taken: %s seconds" % (time.time() - start_time))
    return new_df

    
    