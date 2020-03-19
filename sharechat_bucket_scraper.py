# Import libraries
import os
import requests
import pandas as pd
import numpy as np
import re
from datetime import datetime
import tzlocal
from IPython.display import Image, HTML
import time
from time import sleep
from random import uniform
import json

# Parameters for API bucket scraper - update as required

USER_ID = 348849803 # Sharechat user id
PASSCODE = "e555de8136fb06944f7f" # inspect page > network > bucketFeed or requestType81 > headers > request payload > passcode

# Tag specific params from sharechat.com/tag > inspect ... > request payload 
bucket_dict = {
    "trending/Hindi": {
        "bucket_body": {
            "bn":"broker3","userId": USER_ID,"passCode": PASSCODE,
                        "client":"web","message":{
                            "r":"web", "f": 0, "p":"f"}},
        "api_url" : "https://restapi1.sharechat.com/requestType81"},
    "topic/whatsapp-hindi-238": {
        "bucket_body": {
            "bn":"broker3","userId": USER_ID,"passCode": PASSCODE,
                        "client":"web","message":{
                            "b":238,"allowOffline":True}},
        "api_url": "https://restapi1.sharechat.com/bucketFeed"},
    "topic/news-hindi-125": {
        "bucket_body": {
            "bn":"broker3","userId": USER_ID,"passCode": PASSCODE,
                        "client":"web","message":{
                            "b":125,"allowOffline":True}},
        "api_url": "https://restapi1.sharechat.com/bucketFeed"}}

d = os.getcwd() # Download destination

# Set timezone
local_timezone = tzlocal.get_localzone()

# Buckets to scrape
b = ["topic/news-hindi-125", "topic/whatsapp-hindi-238", "trending/Hindi"]

# Number of pages to scrape
n = 5

# Define helper functions

# Scrapes data from specified tags
def get_data(buckets, pages):
    # Create empty dataframe to collect scraped data
    df = pd.DataFrame(columns = ["link", "timestamp", "lang", 
                                   "media_type", "tag", "thumbnail"])
    print("Scraping data from Sharechat ...")
    for bucket in buckets:
        # Scrape data from each tag
        for _ in range(pages):
            url = bucket_dict[bucket]["api_url"]
            body = bucket_dict[bucket]["tag_body"]
            headers = {"content-type": "application/json", 
                           "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"} 
            response = requests.post(url, json=body, headers=headers)
            response_dict = json.loads(response.text)
            
            link, timestamp, lang, media_type = get_payload_data(response_dict)
            bucket_data = pd.DataFrame(np.column_stack([link, timestamp, lang, media_type]), 
                            columns = ["link", "timestamp", "lang", "media_type"])
            
            # Add bucket column 
            bucket_data["bucket"] = bucket
            # Add thumbnail column
            bucket_data["thumbnail"] = bucket_data["link"]
            # Add bucket data 
            df = df.append(bucket_data)  
            time.sleep(uniform(30, 35)) # random delay after each request
    df["timestamp"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(int(x), local_timezone).strftime("%d-%m-%Y, %H:%M:%S"))
    df.drop_duplicates(inplace = True)
    return df

# Gets image/video data from scraped payload 
def get_payload_data(payload_dict):
    link = []
    timestamp = []
    lang = []
    media_type = []
    for i in payload_dict["payload"]["d"]:
        if (i["t"] == "image") | (i["t"] == "video"):
            timestamp.append(i["o"])
            lang.append(i["m"])
            media_type.append(i["t"])
            if i["t"] == "image":
                link.append(i["g"])
            else:
                link.append(i["v"])
        else:
            pass # skip other content formats
    return link, timestamp, lang, media_type

# Converts links to thumbnails in html
def convert_links_to_thumbnails(df):   
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    image_df = df[df["media_type"] == "image"]
    pd.set_option('display.max_colwidth', -1)
    data_html = HTML(image_df.to_html(escape=False ,formatters=dict(thumbnail=path_to_image_html))) 
    return data_html

# Saves data in csv and html formats
def save_data(df, html):
    with open("sharechat_bucket_data_preview.html", "w") as f:
        f.write(html.data)
    df.drop("thumbnail", axis = 1, inplace = True)
    df.to_csv("sharechat_bucket_data.csv")

# Build API scraper
def sharechat_bucket_scraper(buckets, destination, pages):
    start_time = time.time()
    # Scrape data from each bucket
    sharechat_df = get_data(buckets, n)
    # Generate html file with image thumbnails
    sharechat_data_html = convert_links_to_thumbnails(sharechat_df)
    # Save data 
    save_data(sharechat_df, sharechat_data_html)
    print("{} posts scraped".format(len(sharechat_df)))
    print("Data saved to", destination)
    print("Time taken: %s seconds" % (time.time() - start_time))

# Run scraper
if __name__ == "__main__":
    sharechat_bucket_scraper(b, d, n)

