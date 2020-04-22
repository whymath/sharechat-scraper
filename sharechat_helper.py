# Common helper functions for various Sharechat scrapers
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
from PIL import Image
import io
from dotenv import load_dotenv
load_dotenv() 
import wget
import s3_mongo_helper
import selenium
from selenium import webdriver
import tempfile
from tempfile import mkdtemp
import shutil
import subprocess
import logging
from tqdm import tqdm

# For targeted tag scraper

# Generates params for API requests
def generate_requests_dict(USER_ID, PASSCODE, tag_hash=None, content_type=None, unix_timestamp=None, post_key=None):
    requests_dict = {
    "tag_data_request": { # gets tag info 
        "body": {
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
    "trending_posts_request": { # gets media & metadata from trending section within tag 
        "body": {
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
                       }},
    "type_specific_request": {# gets media & metadata by content type within tag (image/video/text)
        "body": {
            "bn":"broker3",
            "userId": USER_ID,
            "passCode": PASSCODE, 
            "client":"web",
            "message":{
                "tagHash": "{}".format(tag_hash), 
                "feed": True,
                "allowOffline": True,
                "type": "{}".format(content_type)}},
        "api_url": "https://restapi1.sharechat.com/requestType88",
        "headers": {"content-type": "application/json", 
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
                       }},
    "fresh_posts_request": {# gets media & metadata by timestamp ("fresh" content)
        "body": {
            "bn":"broker3",
            "userId": USER_ID,
            "passCode": PASSCODE, 
            "client":"web",
            "message":{
                "th": "{}".format(tag_hash), 
                "s": "{}".format(unix_timestamp),
                "allowOffline": True}},
        "api_url": "https://restapi1.sharechat.com/requestType25",
        "headers": {"content-type": "application/json", 
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
                       }},
    "virality_metrics_request": { # gets current virality metrics for a post
        "body": {
            "bn":"broker3",
            "userId": USER_ID,
            "passCode": PASSCODE, 
            "client":"web",
            "message":{
                "key": "{}".format(post_key), 
                "ph": "{}".format(post_key), 
                "allowOffline": True
                        }},
        "api_url" : "https://restapi1.sharechat.com/requestType45",
        "headers": {"content-type": "application/json", 
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
                   }}        
        }
    return requests_dict

def get_response_dict(requests_dict, request_type):
    url = requests_dict[request_type]["api_url"]
    body = requests_dict[request_type]["body"]
    headers = requests_dict[request_type]["headers"]
    if request_type == "trending_posts_request" and next_offset_hash is not None:
        body["message"]["nextOffsetHash"] = "{}".format(next_offset_hash)
    else: 
        pass 
    response = requests.post(url=url, json=body, headers=headers)
    response_dict = json.loads(response.text)
    return response_dict

# Gets tag info
def get_tag_data(payload_dict):
    tag_name = payload_dict["payload"]["n"]
    tag_translation = payload_dict["payload"]["englishMeaning"]
    tag_genre = payload_dict["payload"]["tagGenre"]
    bucket_name = payload_dict["payload"]["bn"]
    bucket_id = payload_dict["payload"]["bi"]
    return tag_name, tag_translation, tag_genre, bucket_name, bucket_id

# Gets payload metadata that is common across content types
def get_common_metadata(payload_key, timestamp, language, media_type, post_permalink, caption, external_shares, likes, comments, reposts, views, profile_page):
    timestamp.append(payload_key["o"])
    language.append(payload_key["m"])
    media_type.append(payload_key["t"])
    post_permalink.append(payload_key["permalink"])
    profile_page.append("https://sharechat.com/profile/"+payload_key["ath"]["h"])
    if "c" in payload_key.keys():
        caption.append(payload_key["c"])
    else:
        caption.append(None)
    virality_metrics = {"usc": external_shares,
                       "lc": likes,
                       "c2": comments,
                       "repostCount": reposts,
                       "l": views}
    for metric in virality_metrics:
        if metric in payload_key.keys():
            virality_metrics[metric].append(payload_key[metric])
        else:
            virality_metrics[metric].append(0)


# Gets tag contents i.e. metadata for each post 
def get_post_data(payload_dict, tag_name, tag_translation, tag_genre, bucket_name, bucket_id):
    media_link = []
    timestamp = []
    language = []
    media_type = []
    external_shares = []
    likes = []
    comments = []
    reposts = []
    post_permalink = []
    caption = []
    text = []
    views = []
    profile_page  = []
    
    for i in payload_dict["payload"]["d"]:
        if i["t"] == "image":
            get_common_metadata(i, timestamp, language, media_type, post_permalink, caption, external_shares, likes, comments, reposts, views, profile_page)
            media_link.append(i["g"])
            text.append(None)
        elif i["t"] == "video":
            get_common_metadata(i, timestamp, language, media_type, post_permalink, caption, external_shares, likes, comments, reposts, views, profile_page)
            media_link.append(i["v"])
            text.append(None)
        elif i["t"] == "text": 
            if "x" in i.keys(): # if post metadata contains the text
                get_common_metadata(i, timestamp, language, media_type, post_permalink, caption, external_shares, likes, comments, reposts, views, profile_page)
                text.append(i["x"])
                media_link.append(None)
            else:
                pass
        elif i["t"] == "link":
            if "ld" in i.keys(): # if post metadata contains link description
                get_common_metadata(i, timestamp, language, media_type, post_permalink, caption, external_shares, likes, comments, reposts, views, profile_page)
                media_link.append(i["hl"])
                text.append(i["ld"])
            else:
                pass
        else:
            pass 
    post_data = pd.DataFrame(np.column_stack([media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page]), 
                                columns = ["media_link", "timestamp", "language", "media_type", 
                                            "external_shares", "likes", "comments", 
                                             "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
    post_data["tag_name"] = tag_name
    post_data["tag_translation"] = tag_translation
    post_data["tag_genre"] = tag_genre
    post_data["bucket_name"] = bucket_name
    post_data["bucket_id"] = int(bucket_id)
    return post_data


# Gets next offset hash for scraping the next page
def get_next_offset_hash(payload_dict):
    if "nextOffsetHash" in payload_dict["payload"]:
        next_offset_hash = payload_dict["payload"]["nextOffsetHash"]
    else:
        next_offset_hash=None
    return next_offset_hash

# Gets next timestamp for scraping the next page
def get_next_timestamp(payload_dict):
    if "n" in payload_dict["payload"]:
        next_timestamp = payload_dict["payload"]["n"]
    else:
        next_timestamp=None
    return next_timestamp

# Gets trending tag data
def get_trending_data(USER_ID, PASSCODE, tag_hashes, pages):
    # Create empty dataframe to collect scraped data
    df = pd.DataFrame(columns = ["media_link", "timestamp", "language", 
                                   "media_type", "tag_name", "tag_translation", 
                                 "tag_genre", "bucket_name", "bucket_id", 
                                "external_shares", "likes", "comments", 
                                 "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
    
    content_types = ["image", "video", "text"] # add others if required
    for tag_hash in tag_hashes:
        tagDataScraped = False
        try:
            # Send API request to scrape tag info
            requests_dict = generate_requests_dict(USER_ID, PASSCODE, tag_hash=tag_hash, content_type=None, unix_timestamp=None, post_key=None)
            tag_data_response_dict = get_response_dict(requests_dict=requests_dict, request_type="tag_data_request")
            tag_name, tag_translation, tag_genre, bucket_name, bucket_id = get_tag_data(tag_data_response_dict)
            tagDataScraped = True
        except Exception as e:
            print("Could not scrape data from '{}'".format(tag_name))
            print("Continuing ...")
            pass 
        # Send API requests to scrape tag media & metadata 
        if tagDataScraped:
            next_offset_hash = None
            # Scrape trending pages 
            for i in range(pages): 
                try:
                    post_data_response_dict = get_response_dict(requests_dict=requests_dict, request_type="trending_posts_request")
                    post_data = get_post_data(post_data_response_dict, tag_name, tag_translation, tag_genre, bucket_name, bucket_id)
                    next_offset_hash = get_next_offset_hash(post_data_response_dict)
                    df = df.append(post_data, sort = True)
                    time.sleep(uniform(30,35)) # random time delay between requests
                    
                    # Scrape additional content by content type
                    try:
                        for i in content_types:
                            requests_dict["type_specific_request"]["body"]["message"]["type"] = "{}".format(i)
                            type_specific_response_dict = get_response_dict(requests_dict=requests_dict, request_type="type_specific_request")
                            post_data = get_post_data(type_specific_response_dict, tag_name, tag_translation, tag_genre, bucket_name, bucket_id)
                            df = df.append(post_data, sort = True)
                            time.sleep(uniform(30,35)) 
                    except Exception:
                        pass
                except Exception:
                    pass
        else:
            pass
    df.drop_duplicates(inplace = True)
    df["timestamp"] = df["timestamp"].apply(lambda x: datetime.utcfromtimestamp(int(x)))
    df["filename"] = [str(uuid.uuid4()) for x in range(len(df))]  
    df["scraped_date"] = datetime.utcnow()
    return df

        
# Gets fresh tag data
def get_fresh_data(USER_ID, PASSCODE, tag_hashes, pages, unix_timestamp):
    # Create empty dataframe to collect scraped data
    print("Getting fresh data ...")
    df = pd.DataFrame(columns = ["media_link", "timestamp", "language", 
                                   "media_type", "tag_name", "tag_translation", 
                                 "tag_genre", "bucket_name", "bucket_id", 
                                "external_shares", "likes", "comments", 
                                 "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
    for tag_hash in tag_hashes:
        tagDataScraped = False
        try:
            # Send API request to scrape tag info
            requests_dict = generate_requests_dict(USER_ID, PASSCODE, tag_hash=tag_hash, content_type=None, unix_timestamp=unix_timestamp, post_key=None)
            tag_data_response_dict = get_response_dict(requests_dict=requests_dict, request_type="tag_data_request")
            tag_name, tag_translation, tag_genre, bucket_name, bucket_id = get_tag_data(tag_data_response_dict)
            tagDataScraped = True
        except Exception as e:
            print("Could not scrape data from '{}'".format(tag_name))
            print("Continuing ...")
            pass 
        # Send API requests to scrape tag media & metadata 
        if tagDataScraped:
        # Scrape fresh pages 
            for i in range(pages): 
                try:
                    requests_dict["fresh_posts_request"]["body"]["message"]["s"] = "{}".format(unix_timestamp)
                    fresh_posts_response_dict = get_response_dict(requests_dict=requests_dict, request_type="fresh_posts_request")
                    fresh_posts_data = get_post_data(fresh_posts_response_dict, tag_name, tag_translation, tag_genre, bucket_name, bucket_id)
                    unix_timestamp = get_next_timestamp(fresh_posts_response_dict)
                    df = df.append(fresh_posts_data, sort = True)
                    time.sleep(uniform(30,35))
                except Exception:
                    pass           
        else:
            pass
    df.drop_duplicates(inplace = True)
    df["timestamp"] = df["timestamp"].apply(lambda x: datetime.utcfromtimestamp(int(x)))
    df["filename"] = [str(uuid.uuid4()) for x in range(len(df))]  
    df["scraped_date"] = datetime.utcnow()
    return df


        


# S3 upload function for targeted tag scraper
def sharechat_s3_upload(df, aws, bucket, s3):
    #aws, bucket, s3 = s3_mongo_helper.initialize_s3()
    for index, row in df.iterrows():
        if (row["media_type"] == "image"):
                # Create S3 file name 
            filename = row["filename"]+".jpg"
                # Get media
            temp = wget.download(row["media_link"])
                # Upload media to S3
            s3_mongo_helper.upload_to_s3(s3=s3, file=temp, filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove(temp)
        elif (row["media_type"] == "video"):
                # Create S3 file name
            filename = row["filename"]+".mp4"
                # Get media
            temp = wget.download(row["media_link"])
                # Upload media to S3
            s3_mongo_helper.upload_to_s3(s3=s3, file=temp, filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove(temp)
        else: # for text posts and media links
                # Create S3 file name
            filename = row["filename"]+".txt"
                # Create text file
            with open("temp.txt", "w+") as f:
                f.write(row["text"])
                # Upload media to S3
            s3_mongo_helper.upload_to_s3(s3=s3, file="temp.txt", filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove("temp.txt")
    # Add S3 urls with correct extensions
    df.reset_index(inplace = True)
    df.loc[df["media_type"] == "image", "s3_url"] = aws+bucket+"/"+df["filename"]+".jpg"
    df.loc[df["media_type"] == "video", "s3_url"] = aws+bucket+"/"+df["filename"]+".mp4"
    df.loc[df["media_type"] == "text", "s3_url"] = aws+bucket+"/"+df["filename"]+".txt"
    return df # return df with s3 urls added

# Mongo upload function for targeted tag scraper
def sharechat_mongo_upload(df, coll):
    #coll = s3_mongo_helper.initialize_mongo()
    for i in df.to_dict("records"):
        s3_mongo_helper.upload_to_mongo(data=i, coll=coll) 


# Generate html file with thumbnails for image and video posts     
def get_thumbnails(df):
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    thumbnail = []
    aws, bucket, s3 = s3_mongo_helper.initialize_s3()
    temp_dir = tempfile.mkdtemp(dir=os.getcwd())
    for link in df["s3_url"]:
        if link == link: 
            if link.split(".")[-1] == "mp4":
                video_input_path = link
                img_output_path = temp_dir.split("/")[-1]+"/"+link.split("/")[-1].split(".")[0]+".jpg"
                filename = link.split("/")[-1].split(".")[0]+".jpg"
                subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:00.000', '-vframes', '1', img_output_path])
                s3_mongo_helper.upload_to_s3(s3=s3, file=img_output_path, filename=filename, bucket=bucket, content_type="image")
                thumbnail.append(aws+bucket+"/"+filename)
            elif link.split(".")[-1] == "txt":
                thumbnail.append(None)
            else: # if jpg/jpeg/png
                thumbnail.append(link) 
        else: # if NaN
            thumbnail.append(None)
    df['thumbnail'] = np.array(thumbnail)
    pd.set_option('display.max_colwidth', -1)
    df_html = HTML(df.to_html(index = False, escape=False ,formatters=dict(thumbnail=path_to_image_html), render_links = True))
    shutil.rmtree(temp_dir)
    return df, df_html

# Virality scraper helper functions
def save_updated_df(df, today):
    pd.to_pickle(df, "virality_df_{}.pkl".format(today))
    df.to_csv("virality_df_{}.csv".format(today))

def scrape_metrics(response_dict):
    virality_metrics = {"c2": "comments",
                        "usc": "external_shares",
                       "lc": "likes",
                       "repostCount": "reposts",
                       "l": "views"}
    values = [[]]
    for key in virality_metrics:
        if key in response_dict["payload"]["d"].keys():
            res = int(response_dict["payload"]["d"][key])
            values[0].append(res)
        else:
            values[0].append(0)
    return values

def get_current_metrics(USER_ID, PASSCODE, post_permalink):
    post_key = post_permalink.split("/")[-1] 
    requests_dict = generate_requests_dict(USER_ID, PASSCODE, tag_hash=None, content_type=None, unix_timestamp=None, post_key=post_key)
    # Send API request & get response 
    virality_metrics_response_dict = get_response_dict(requests_dict=requests_dict, request_type="virality_metrics_request")
    # Scrape current metrics for post 
    result = scrape_metrics(virality_metrics_response_dict)
    time.sleep(uniform(30,35))
    return result
 


# s3 upload functions for ML scraper

def ml_initialize_s3():
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY_ID")
    aws = os.environ.get("AWS_BASE_URL")
    bucket = os.environ.get("AWS_ML_BUCKET") # changed bucket
    s3 = boto3.client("s3", aws_access_key_id = aws_access_key_id,
                          aws_secret_access_key= aws_secret_access_key) 
    return aws, bucket, s3

def ml_upload_to_s3(s3, file, filename, bucket, content_type):
    with open(file, "rb")as data:
        s3.upload_fileobj(Fileobj = data, 
                          Bucket = bucket,
                          Key = "machinelearning-negatives/"+filename)  

def ml_sharechat_s3_upload(df):
    aws, bucket, s3 = ml_initialize_s3()  
    for index, row in df.iterrows():
        if (row["media_type"] == "image"):
                # Create S3 file name 
            filename = row["filename"]+".jpg"
                # Get media
            temp = wget.download(row["media_link"])
                # Upload media to S3
            ml_upload_to_s3(s3=s3, file=temp, filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove(temp)
        elif (row["media_type"] == "video"):
                # Create S3 file name
            filename = row["filename"]+".mp4"
                # Get media
            temp = wget.download(row["media_link"])
                # Upload media to S3
            ml_upload_to_s3(s3=s3, file=temp, filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove(temp)
        elif (row["media_type"] == "text"):
                # Create S3 file name
            filename = row["filename"]+".txt"
                # Create text file
            with open("temp.txt", "w+") as f:
                f.write(row["text"])
                # Upload media to S3
            ml_upload_to_s3(s3=s3, file="temp.txt", filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove("temp.txt")
        else:
            pass
    # Add S3 urls with correct extensions
    df.reset_index(inplace = True)
    df.loc[df["media_type"] == "image", "s3_url"] = aws+bucket+"/machinelearning-negatives/"+df["filename"]+".jpg"
    df.loc[df["media_type"] == "video", "s3_url"] = aws+bucket+"/machinelearning-negatives/"+df["filename"]+".mp4"
    df.loc[df["media_type"] == "text", "s3_url"] = aws+bucket+"/machinelearning-negatives/"+df["filename"]+".txt"
    return df # return df with s3 urls added

# Old helper functions
# Saves data locally in csv and html formats
def save_data_to_disk(df, html):
    with open("sharechat_data_preview.html", "w") as f:
        f.write(html.data)
    df.drop("thumbnail", axis = 1, inplace = True)
    df.to_csv("sharechat_data.csv")


# Converts links to thumbnails in html
def convert_links_to_thumbnails(df): 
    df["thumbnail"] = df["media_link"]
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    image_df = df[df["media_type"] == "image"]
    pd.set_option('display.max_colwidth', -1)
    data_html = HTML(image_df.to_html(index = False, escape=False ,formatters=dict(thumbnail=path_to_image_html), render_links = True)) 
    return data_html