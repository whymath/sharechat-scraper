# API scraper for specific tags within a content bucket
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
import lxml
from lxml import etree
import selenium
from selenium import webdriver

# Parameters for API scraper - update as required
USER_ID = 348849803 # Sharechat user id
PASSCODE = "e555de8136fb06944f7f" # inspect page > network > bucketFeed or requestType81 > headers > request payload > passcode
PATH = os.getcwd()
CHROMEDRIVER_PATH = os.path.join(PATH, "chromedriver")

# Download destination - TO UPDATE
d = "/Users/kruttikanadig/Desktop"

# Set timezone
local_timezone = tzlocal.get_localzone()

buckets = {"hindi_coronavirus": "https://sharechat.com/buckets/125?referrer=explorePage",
          "hindi_news": "https://sharechat.com/buckets/1284?referrer=bucketViewPage"}

# Helper functions for scraper
def get_tag_hashes(buckets): 
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

def get_first_payload_data(payload_dict):
    tag_name = payload_dict["payload"]["n"]
    tag_translation = payload_dict["payload"]["englishMeaning"]
    tag_genre = payload_dict["payload"]["tagGenre"]
    bucket_name = payload_dict["payload"]["bn"]
    bucket_id = payload_dict["payload"]["bi"]
    return tag_name, tag_translation, tag_genre, bucket_name, bucket_id


def get_second_payload_data(payload_dict):
    link = []
    timestamp = []
    language = []
    media_type = []
    for i in payload_dict["payload"]["d"]:
        if (i["t"] == "image") | (i["t"] == "video"):
            timestamp.append(i["o"])
            language.append(i["m"])
            media_type.append(i["t"])
            if i["t"] == "image":
                link.append(i["g"])
            else:
                link.append(i["v"])
        else:
            pass # skip other content formats
    return link, timestamp, language, media_type

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
    with open("sharechat_tag_data_preview.html", "w") as f:
        f.write(html.data)
    df.drop("thumbnail", axis = 1, inplace = True)
    df.to_csv("sharechat_tag_data.csv")

# Get tag data
def get_data(tag_hashes):
    # Create empty dataframe to collect scraped data
    df = pd.DataFrame(columns = ["link", "timestamp", "language", 
                                   "media_type", "tag_name", "tag_translation", "tag_genre", "bucket_name", "bucket_id", "thumbnail"])
    print("Scraping data from Sharechat ...")
    for tag_hash in tag_hashes:
        requests_dict = generate_requests_dict(tag_hash, USER_ID, PASSCODE)
        # Send API request to check tag type
        first_url = requests_dict["first_request"]["api_url"]
        first_body = requests_dict["first_request"]["tag_body"]
        first_headers = requests_dict["first_request"]["headers"]
        time.sleep(uniform(30,35)) # random time delay between requests
        first_response = requests.post(url=first_url, json=first_body, headers=first_headers)
        first_response_dict = json.loads(first_response.text)
        if (first_response_dict["payload"]["bi"] == 1284) or (first_response_dict["payload"]["tagCategory"] == "Temporary"):
            tag_name, tag_translation, tag_genre, bucket_name, bucket_id = get_first_payload_data(first_response_dict)
            second_url = requests_dict["second_request"]["api_url"]
            second_body = requests_dict["second_request"]["tag_body"]
            second_headers = requests_dict["second_request"]["headers"] 
            time.sleep(uniform(0.5,2))
            second_response = requests.post(url=second_url, json=second_body, headers=second_headers)
            second_response_dict = json.loads(second_response.text)
            link, timestamp, language, media_type = get_second_payload_data(second_response_dict)
            tag_data = pd.DataFrame(np.column_stack([link, timestamp, language, media_type]), 
                            columns = ["link", "timestamp", "language", "media_type"])
            tag_data["tag_name"] = tag_name
            tag_data["tag_translation"] = tag_translation
            tag_data["tag_genre"] = tag_genre
            tag_data["bucket_name"] = bucket_name
            tag_data["bucket_id"] = int(bucket_id)
            tag_data["thumbnail"] = tag_data["link"]
            df = df.append(tag_data)
    df["timestamp"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(int(x), local_timezone).strftime("%d-%m-%Y, %H:%M:%S"))
    df.drop_duplicates(inplace = True)
    return df

    
# Build scraper 
def sharechat_tag_scraper(buckets, destination):
    start_time = time.time()
    # Get tag hashes
    tag_hashes = get_tag_hashes(buckets)
    # Scrape data from each tag
    sharechat_df = get_data(tag_hashes)
    # Generate html file with image thumbnails
    sharechat_data_html = convert_links_to_thumbnails(sharechat_df)
    # Save data 
    save_data(sharechat_df, sharechat_data_html)
    print("{} posts scraped".format(len(sharechat_df)))
    if len(sharechat_df) > 0:
        print("Data saved to", destination)
    else:
        print("No relevant data found!")
    print("Time taken: %s seconds" % (time.time() - start_time))

# Run scraper
if __name__ == "__main__":
    sharechat_tag_scraper(buckets, d)