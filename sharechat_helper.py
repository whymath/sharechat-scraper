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


# For targeted tag scraper
# Generates params for api requests
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

# Gets tag info
def get_first_payload_data(payload_dict):
    tag_name = payload_dict["payload"]["n"]
    tag_translation = payload_dict["payload"]["englishMeaning"]
    tag_genre = payload_dict["payload"]["tagGenre"]
    bucket_name = payload_dict["payload"]["bn"]
    bucket_id = payload_dict["payload"]["bi"]
    return tag_name, tag_translation, tag_genre, bucket_name, bucket_id

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


# Gets next offset hash i.e. enables multi page scraping
def get_next_offset_hash(payload_dict):
    if "nextOffsetHash" in payload_dict["payload"]:
        next_offset_hash = payload_dict["payload"]["nextOffsetHash"]
    else:
        next_offset_hash=None
    return next_offset_hash

# Main function to get tag data 
def get_data(temp_tag_hashes, USER_ID, PASSCODE, PAGES):
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
    data_html = HTML(image_df.to_html(escape=False ,formatters=dict(thumbnail=path_to_image_html))) 
    return data_html

def get_tag_hashes(buckets): # for bucket scraper
    tag_hashes = []
    for bucket in buckets:
        hashes = []
        bucket_page = buckets[bucket]
        driver = webdriver.Chrome(executable_path = CHROMEDRIVER_PATH)
        driver.get(bucket_page)
        driver.find_element_by_xpath('/html/body/div[1]/div[1]/main/div/div/div[1]').click()
        time.sleep(10)
        html = driver.page_source
        driver.quit()
        tree = etree.HTML(html)
        links = tree.xpath("//a[contains(@href, 'tag')]/@href")
        del(links[-1])
        pattern = re.compile(r'(?<=tag/).*?(?=\?)')
        for link in links:
            t_hash = re.findall(pattern, link)
            hashes.extend(t_hash)
        tag_hashes.extend(hashes)
    tag_hashes = list(set(tag_hashes))
    return tag_hashes