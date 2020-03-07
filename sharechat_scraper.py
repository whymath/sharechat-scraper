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

# Parameters for API scraper - update as required

USER_ID = 341972726 # Sharechat user id
PASSCODE = "dcdb36a4dc99d6a39547" # inspect page > network > bucketFeed or requestType81 > headers > request payload > passcode

# Tag specific params from sharechat.com/tag > inspect ... > request payload 
tag_dict = {
    "trending/Hindi": {
        "tag_body": {
            "bn":"broker3","userId": USER_ID,"passCode": PASSCODE,
                        "client":"web","message":{
                            "r":"web", "f": 0, "p":"f"}},
        "api_url" : "https://restapi1.sharechat.com/requestType81"},
    "topic/whatsapp-hindi-238": {
        "tag_body": {
            "bn":"broker3","userId": USER_ID,"passCode": PASSCODE,
                        "client":"web","message":{
                            "b":238,"allowOffline":True}},
        "api_url": "https://restapi1.sharechat.com/bucketFeed"},
    "topic/news-hindi-125": {
        "tag_body": {
            "bn":"broker3","userId": USER_ID,"passCode": PASSCODE,
                        "client":"web","message":{
                            "b":238,"allowOffline":True}},
        "api_url": "https://restapi1.sharechat.com/bucketFeed"}}

d = os.getcwd() # Download destination

# Set timezone
local_timezone = tzlocal.get_localzone()

# Tags to scrape
t = ["topic/news-hindi-125", "topic/whatsapp-hindi-238", "trending/Hindi"]

# Number of pages to scrape
n = 10

# Define helper functions

# Scrapes data from specified tags
def get_data(tags, pages):
    # Create empty dataframe to collect scraped data
    df = pd.DataFrame(columns = ["link", "timestamp", "lang", 
                                   "media_type", "tag", "thumbnail"])
    print("Scraping data from Sharechat ...")
    for _ in range(pages):
        # Scrape data from each tag
        for tag in tags: 
            url = tag_dict[tag]["api_url"]
            body = tag_dict[tag]["tag_body"]
            headers = {"content-type": "application/json", 
                           "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"} 
            response = requests.post(url, json=body, headers=headers)
            response_dict = json.loads(response.text)
            
            link, timestamp, lang, media_type = get_payload_data(response_dict)
            tag_data = pd.DataFrame(np.column_stack([link, timestamp, lang, media_type]), 
                            columns = ["link", "timestamp", "lang", "media_type"])
            
            # Add tag column 
            tag_data["tag"] = tag
            # Add thumbnail column
            tag_data["thumbnail"] = tag_data["link"]
            # Add tag data 
            df = df.append(tag_data)  
            time.sleep(uniform(5, 10)) # random delay after each request
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
    with open("sharechat_data_preview.html", "w") as f:
        f.write(html.data)
    df.drop("thumbnail", axis = 1, inplace = True)
    df.to_csv("sharechat_data.csv")

# Build API scraper
def sharechat_scraper(tags, destination, pages):
    start_time = time.time()
    # Scrape data from each tag
    sharechat_df = get_data(tags, n)
    # Generate html file with image thumbnails
    sharechat_data_html = convert_links_to_thumbnails(sharechat_df)
    # Save data 
    save_data(sharechat_df, sharechat_data_html)
    print("{} posts scraped".format(len(sharechat_df)))
    print("Data saved to", destination)
    print("Time taken: %s seconds" % (time.time() - start_time))

# Run scraper
if __name__ == "__main__":
    sharechat_scraper(t, d, n)

