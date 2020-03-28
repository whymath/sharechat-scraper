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
import os
import pymongo
from pymongo import MongoClient
load_dotenv() 
import wget

# Parameters for API scraper - update as required
USER_ID = os.environ("SHARECHAT_USER_ID")
PASSCODE = os.environ("SHARECHAT_PASSWORD")
temp_tag_hashes = ["1RgBZQ", "5anPZA", "3NE91Z", "pkArae", "X6Pxqx", "bvdlaO", "QqyvJA", "EXGxBg", "3NZwyK"] # CHANGE AS REQUIRED

PAGES = 2 

# Helper functions for scraper
# Generates params for API requests
def generate_requests_dict(tag_hash, USER_ID, PASSCODE):
    requests_dict = {
    "first_request": {
        "tag_body": {
            "bn":"broker3",
            "userId": USER_ID,
            "passCode": PASSCODE, 
            "client":"web",
            "message":{
                "key": "{}".format(tag_hash), 
                "th": "{}".format(tag_hash), 
                "t": 2, 
                "allowOffline": True
                        }},
        "api_url" : "https://restapi1.sharechat.com/requestType66",
        "headers": {"content-type": "application/json", 
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
                   }}, 
    "second_request": {
        "tag_body": {
            "bn":"broker3",
            "userId": USER_ID,
            "passCode": PASSCODE, 
            "client":"web",
            "message":{
                "th": "{}".format(tag_hash), 
                "allowOffline": True}},
        "api_url": "https://restapi1.sharechat.com/getViralPostsSeo",
        "headers": {"content-type": "application/json", 
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
                       }}}
    return requests_dict

# Sends API request to get tag info
def get_first_payload_data(payload_dict):
    tag_name = payload_dict["payload"]["n"]
    tag_translation = payload_dict["payload"]["englishMeaning"]
    tag_genre = payload_dict["payload"]["tagGenre"]
    bucket_name = payload_dict["payload"]["bn"]
    bucket_id = payload_dict["payload"]["bi"]
    return tag_name, tag_translation, tag_genre, bucket_name, bucket_id

# Sends API request to get media links and metadata
def get_second_payload_data(payload_dict):
    media_link = []
    timestamp = []
    language = []
    media_type = []
    external_shares = []
    likes = []
    comments = []
    reposts = []
    post_permalink = []
    virality_metrics = {"usc": external_shares,
                       "lc": likes,
                       "c2": comments,
                       "repostCount": reposts}
    
    for i in payload_dict["payload"]["d"]:
        if (i["t"] == "image") | (i["t"] == "video"):
            timestamp.append(i["o"])
            language.append(i["m"])
            media_type.append(i["t"])
            post_permalink.append(i["permalink"])
            if i["t"] == "image":
                media_link.append(i["g"])
            else:
                media_link.append(i["v"])
                
            for metric in virality_metrics:
                if metric in i.keys():
                    virality_metrics[metric].append(i[metric])
                else:
                    virality_metrics[metric].append(0)
        else:
            pass # skip other content formats
    return media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink


# Gets next offset hash - for scraping subsequent pages
def get_next_offset_hash(payload_dict):
    if "nextOffsetHash" in payload_dict["payload"]:
        next_offset_hash = payload_dict["payload"]["nextOffsetHash"]
    else:
        next_offset_hash=None
    return next_offset_hash

# Get tag data 
def get_data(temp_tag_hashes):
    # Create empty dataframe to collect scraped data
    df = pd.DataFrame(columns = ["media_link", "timestamp", "language", 
                                   "media_type", "tag_name", "tag_translation", 
                                 "tag_genre", "bucket_name", "bucket_id", 
                                "external_shares", "likes", "comments", 
                                 "reposts", "post_permalink"])
    print("Scraping data from Sharechat ...")
    for tag_hash in temp_tag_hashes:
        requests_dict = generate_requests_dict(tag_hash, USER_ID, PASSCODE)
    # Send API request to scrape tag info
        first_url = requests_dict["first_request"]["api_url"]
        first_body = requests_dict["first_request"]["tag_body"]
        first_headers = requests_dict["first_request"]["headers"]
        first_response = requests.post(url=first_url, json=first_body, headers=first_headers)
        first_response_dict = json.loads(first_response.text)
        tag_name, tag_translation, tag_genre, bucket_name, bucket_id = get_first_payload_data(first_response_dict)
    # Send API requests to scrape tag media & metadata
        second_url = requests_dict["second_request"]["api_url"]
        second_body = requests_dict["second_request"]["tag_body"]
        second_headers = requests_dict["second_request"]["headers"] 
        time.sleep(uniform(0.5,2))
        second_response = requests.post(url=second_url, json=second_body, headers=second_headers)
        second_response_dict = json.loads(second_response.text)
        media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink = get_second_payload_data(second_response_dict)
        next_offset_hash = get_next_offset_hash(second_response_dict)
        tag_data = pd.DataFrame(np.column_stack([media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink]), 
                        columns = ["media_link", "timestamp", "language", "media_type", 
                                   "external_shares", "likes", "comments", 
                                     "reposts", "post_permalink"])
        tag_data["tag_name"] = tag_name
        tag_data["tag_translation"] = tag_translation
        tag_data["tag_genre"] = tag_genre
        tag_data["bucket_name"] = bucket_name
        tag_data["bucket_id"] = int(bucket_id)
        df = df.append(tag_data, sort = True)
        time.sleep(uniform(30,35)) # random time delay between requests
        
        for _ in range(PAGES): # scrape from multiple pages
            if next_offset_hash is not None:
                second_url = requests_dict["second_request"]["api_url"]
                second_body = requests_dict["second_request"]["tag_body"]
                second_body["message"]["nextOffsetHash"] = "{}".format(next_offset_hash)
                second_headers = requests_dict["second_request"]["headers"] 
                time.sleep(uniform(0.5,2))
                second_response = requests.post(url=second_url, json=second_body, headers=second_headers)
                second_response_dict = json.loads(second_response.text)
                media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink = get_second_payload_data(second_response_dict)
                next_offset_hash = get_next_offset_hash(second_response_dict)
                tag_data = pd.DataFrame(np.column_stack([media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink]), 
                                columns = ["media_link", "timestamp", "language", "media_type", 
                                           "external_shares", "likes", "comments", 
                                             "reposts", "post_permalink"])
                tag_data["tag_name"] = tag_name
                tag_data["tag_translation"] = tag_translation
                tag_data["tag_genre"] = tag_genre
                tag_data["bucket_name"] = bucket_name
                tag_data["bucket_id"] = int(bucket_id)
                df = df.append(tag_data, sort = True)
                time.sleep(uniform(30,35)) # random time delay between requests
            else:
                continue
    df.drop_duplicates(inplace = True)
    df["timestamp"] = df["timestamp"].apply(lambda x: datetime.utcfromtimestamp(int(x)))
    df["filename"] = [str(uuid.uuid4()) for x in range(len(df))]  
    df["scraped_date"] = datetime.utcnow()
    return df

# Converts links to thumbnails in html - use this to visualise scraped data
def convert_links_to_thumbnails(df): 
    df["thumbnail"] = df["media_link"]
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    image_df = df[df["media_type"] == "image"]
    pd.set_option('display.max_colwidth', -1)
    data_html = HTML(image_df.to_html(escape=False ,formatters=dict(thumbnail=path_to_image_html))) 
    return data_html

# Uploads media to S3
def upload_to_s3(df):
    s3 = boto3.client("s3", aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key= os.environ["AWS_SECRET_ACCESS_KEY_ID"])
    aws = "https://s3.ap-south-1.amazonaws.com/"
    bucket = "sharechat-scraper.tattle.co.in"
    for index, row in df.iterrows():
        df.at[index, "s3_url"] = aws+bucket+"/"+row["filename"]
        if (row["media_type"] == "image"):
            temp = wget.download(row["media_link"])
            with open(temp, "rb") as data:
                s3.upload_fileobj(data,
                                Bucket = bucket,
                                Key = row["filename"]+".jpg",
                                ExtraArgs={'ContentType': row["media_type"],
                                    'ACL': 'public-read'})
            os.remove(temp)
        else:
            temp = wget.download(row["media_link"])
            with open(temp, "rb") as data:
                s3.upload_fileobj(data,
                                Bucket = bucket,
                                Key = row["filename"]+".mp4",
                                ExtraArgs={'ContentType': row["media_type"],
                                    'ACL': 'public-read'})
            os.remove(temp)
    return df

# Uploads media metadata to Mongo db
def upload_to_mongo(df):
    mongo_url = "mongodb+srv://"+os.environ.get("DB_USERNAME")+":"+os.environ.get("DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"   
    cli = MongoClient(mongo_url)
    db = cli[os.environ.get("DB_NAME")]
    coll = db[os.environ.get("DB_COLLECTION")]
    for i in df.to_dict("records"):
        coll.insert_one(i)
        
def save_data(df):
    df = upload_to_s3(df)
    upload_to_mongo(df)
    return df

# Main function
def sharechat_targeted_tag_scraper(temp_tag_hashes):
    start_time = time.time()
    # Scrape data from tags
    sharechat_df = get_data(temp_tag_hashes)
    # Save data to S3 & Mongo DB
    save_data(sharechat_df)
    if len(sharechat_df) > 0:
        print("{} posts scraped and saved".format(len(sharechat_df)))
    else:
        print("No relevant data found!")
    print("Time taken: %s seconds" % (time.time() - start_time))
    return sharechat_df


# Run scraper
if __name__ == "__main__":
    sharechat_targeted_tag_scraper(temp_tag_hashes)
