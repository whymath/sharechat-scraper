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

# For targeted tag scraper

# Generates params for API requests
def generate_requests_dict(tag_hash, USER_ID, PASSCODE, content_type=None):
    requests_dict = {
    "first_request": { # gets tag info 
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
    "second_request": { # gets media & metadata from trending section within tag 
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
                       }},
    "third_request": {# gets media & metadata by content type within tag (image/video/text)
        "tag_body": {
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
                       },
        }}
    return requests_dict

# Gets tag info
def get_first_payload_data(payload_dict):
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
        else:
            pass 
    return media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page


# Gets next offset hash for scraping the next page
def get_next_offset_hash(payload_dict):
    if "nextOffsetHash" in payload_dict["payload"]:
        next_offset_hash = payload_dict["payload"]["nextOffsetHash"]
    else:
        next_offset_hash=None
    return next_offset_hash

# Main function to get tag data 
def get_data(temp_tag_hashes, USER_ID, PASSCODE, MORE_PAGES, scrape_by_type=True):
    # Create empty dataframe to collect scraped data
    df = pd.DataFrame(columns = ["media_link", "timestamp", "language", 
                                   "media_type", "tag_name", "tag_translation", 
                                 "tag_genre", "bucket_name", "bucket_id", 
                                "external_shares", "likes", "comments", 
                                 "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
    print("Scraping data from Sharechat ...")
    for tag_hash in temp_tag_hashes:
        requests_dict = generate_requests_dict(tag_hash, USER_ID, PASSCODE, content_type=None)
    # Send API request to scrape tag info
        first_url = requests_dict["first_request"]["api_url"]
        first_body = requests_dict["first_request"]["tag_body"]
        first_headers = requests_dict["first_request"]["headers"]
        first_response = requests.post(url=first_url, json=first_body, headers=first_headers)
        first_response_dict = json.loads(first_response.text)
        tag_name, tag_translation, tag_genre, bucket_name, bucket_id = get_first_payload_data(first_response_dict)

    # Send API requests to scrape tag media & metadata from multiple pages

        second_url = requests_dict["second_request"]["api_url"]
        second_body = requests_dict["second_request"]["tag_body"]
        second_headers = requests_dict["second_request"]["headers"] 
        time.sleep(uniform(0.5,2))
        second_response = requests.post(url=second_url, json=second_body, headers=second_headers)
        second_response_dict = json.loads(second_response.text)
        media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page = get_second_payload_data(second_response_dict)
        next_offset_hash = get_next_offset_hash(second_response_dict)
        tag_data = pd.DataFrame(np.column_stack([media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page]),
        columns = ["media_link", "timestamp", "language", "media_type", 
        "external_shares", "likes", "comments", 
        "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
        tag_data["tag_name"] = tag_name
        tag_data["tag_translation"] = tag_translation
        tag_data["tag_genre"] = tag_genre
        tag_data["bucket_name"] = bucket_name
        tag_data["bucket_id"] = int(bucket_id)
        df = df.append(tag_data, sort = True)
        time.sleep(uniform(30,35)) # random time delay between requests

        for i in range(MORE_PAGES): 
            if next_offset_hash is not None:
                second_url = requests_dict["second_request"]["api_url"]
                second_body = requests_dict["second_request"]["tag_body"]
                second_body["message"]["nextOffsetHash"] = "{}".format(next_offset_hash)
                second_headers = requests_dict["second_request"]["headers"] 
                time.sleep(uniform(0.5,2))
                second_response = requests.post(url=second_url, json=second_body, headers=second_headers)
                second_response_dict = json.loads(second_response.text)
                media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page = get_second_payload_data(second_response_dict)
                next_offset_hash = get_next_offset_hash(second_response_dict)
                tag_data = pd.DataFrame(np.column_stack([media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page]), 
                                columns = ["media_link", "timestamp", "language", "media_type", 
                                           "external_shares", "likes", "comments", 
                                             "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
                tag_data["tag_name"] = tag_name
                tag_data["tag_translation"] = tag_translation
                tag_data["tag_genre"] = tag_genre
                tag_data["bucket_name"] = bucket_name
                tag_data["bucket_id"] = int(bucket_id)
                df = df.append(tag_data, sort = True)
                time.sleep(uniform(30,35)) # random time delay between requests

            else:
                continue
        
        if scrape_by_type == True:
            # Scrape more content from tag by content type
            content_types = ["image", "video", "text"] # add image, video and others if required
            try:
                for i in content_types:
                    requests_dict["third_request"]["tag_body"]["message"]["type"] = "{}".format(i)
                    third_url = requests_dict["third_request"]["api_url"]
                    third_body = requests_dict["third_request"]["tag_body"]
                    third_headers = requests_dict["third_request"]["headers"] 
                    third_response = requests.post(url=third_url, json=third_body, headers=third_headers)
                    third_response_dict = json.loads(third_response.text)
                    media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page = get_second_payload_data(third_response_dict)
                    tag_data = pd.DataFrame(np.column_stack([media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page]), 
                    columns = ["media_link", "timestamp", "language", "media_type", 
                                "external_shares", "likes", "comments", 
                                    "reposts", "post_permalink", "caption", "text", "views", "profile_page"])
                    tag_data["tag_name"] = tag_name
                    tag_data["tag_translation"] = tag_translation
                    tag_data["tag_genre"] = tag_genre
                    tag_data["bucket_name"] = bucket_name
                    tag_data["bucket_id"] = int(bucket_id)
                    df = df.append(tag_data, sort = True)
                    time.sleep(uniform(30,35)) 
            except Exception:
                pass

        else:
            continue

    if len(df) > 0:
        df.drop_duplicates(inplace = True)
        df["timestamp"] = df["timestamp"].apply(lambda x: datetime.utcfromtimestamp(int(x)))
        df["filename"] = [str(uuid.uuid4()) for x in range(len(df))]  
        df["scraped_date"] = datetime.utcnow()
    else:
        pass
    return df

# Saves data locally in csv and html formats
def save_data_to_disk(df, html):
    with open("sharechat_tag_data_preview.html", "w") as f:
        f.write(html.data)
    df.drop("thumbnail", axis = 1, inplace = True)
    df.to_csv("sharechat_tag_data.csv")

# Converts links to thumbnails in html
def convert_links_to_thumbnails(df): 
    df["thumbnail"] = df["media_link"]
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    image_df = df[df["media_type"] == "image"]
    pd.set_option('display.max_colwidth', -1)
    data_html = HTML(image_df.to_html(index = False, escape=False ,formatters=dict(thumbnail=path_to_image_html), render_links = True)) 
    return data_html

# S3 upload function for targeted tag scraper
def sharechat_s3_upload(df):
    aws, bucket, s3 = s3_mongo_helper.initialize_s3()
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
        elif (row["media_type"] == "text"):
                # Create S3 file name
            filename = row["filename"]+".txt"
                # Create text file
            with open("temp.txt", "w+") as f:
                f.write(row["text"])
                # Upload media to S3
            s3_mongo_helper.upload_to_s3(s3=s3, file="temp.txt", filename=filename, bucket=bucket, content_type=row["media_type"])
            os.remove("temp.txt")
        else:
            pass
    # Add S3 urls with correct extensions
    df.reset_index(inplace = True)
    df.loc[df["media_type"] == "image", "s3_url"] = aws+bucket+"/"+df["filename"]+".jpg"
    df.loc[df["media_type"] == "video", "s3_url"] = aws+bucket+"/"+df["filename"]+".mp4"
    df.loc[df["media_type"] == "text", "s3_url"] = aws+bucket+"/"+df["filename"]+".txt"
    return df # return df with s3 urls added

# Mongo upload function for targeted tag scraper
def sharechat_mongo_upload(df):
    coll = s3_mongo_helper.initialize_mongo()
    for i in df.to_dict("records"):
        s3_mongo_helper.upload_to_mongo(data=i, coll=coll) 


# Generate html file with thumbnails for image and video posts
# Ensure temp_dir remains in the same directory as the generated html
def get_thumbnails(df):
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    thumbnail = []
    temp_dir = mkdtemp(dir = os.getcwd())
    for link in df["media_link"]:
        if link == link: 
            if link.split(".")[-1] == "mp4":
                video_input_path = link
                img_output_path = temp_dir.split("/")[-1]+"/"+link.split("/")[-1].split(".")[0]+".jpg"
                subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:00.000', '-vframes', '1', img_output_path])
                thumbnail.append(img_output_path)
            else:
                thumbnail.append(link) 
        else: # if NaN
            thumbnail.append(None)
    df['thumbnail'] = np.array(thumbnail)
    pd.set_option('display.max_colwidth', -1)
    df_html = HTML(df.to_html(index = False, escape=False ,formatters=dict(thumbnail=path_to_image_html), render_links = True))
    with open("df.html", "w") as f:
        f.write(df_html.data)
        