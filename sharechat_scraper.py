# Import libraries
import os
from os.path import basename
import requests
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import re
from datetime import datetime
import tzlocal
from IPython.display import Image, HTML

# Set timezone
local_timezone = tzlocal.get_localzone()

# Define helper functions

# Scrapes data from specified tags
def get_data(tags):
    # Create empty dataframe to collect scraped data
    data = pd.DataFrame(columns = ["img_link", "timestamp", "tag", "thumbnail"])
    # Scrape data from each tag
    for tag in tags: 
        print("Scraping recent images from https://sharechat.com/"+tag+" ...")
        soup = get_parsed_page(tag) 
        img_links, timestamps = get_images_with_timestamps(soup)  
        # Save tag data as dataframe
        tag_data = pd.DataFrame(np.column_stack([img_links, timestamps]), 
                            columns = ["img_link", "timestamp"])
        # Add tag column 
        tag_data["tag"] = tag
        # Add thumbnail column
        tag_data["thumbnail"] = tag_data["img_link"]   
        # Add tag data 
        data = data.append(tag_data)
    return data

# Returns parsed web page
def get_parsed_page(tag):
    r = requests.get("https://sharechat.com/"+tag)
    c = r.content
    soup = BeautifulSoup(c, "lxml") 
    return soup

# Returns images with timestamps
def get_images_with_timestamps(soup):
    # Initialize empty lists to hold data
    img_links = []
    timestamps = []
    # Find image
    images = soup.findAll("img", {"src": re.compile(".jpg")}) 
    for image in images:
        # Add image link
        img_links.append(image["src"]) 
        # Find timestamp
        unix_ts = re.findall("\d{13}", image["src"]) 
        if (len(unix_ts) > 0): # If link contains timestamp
        # Reformat and save timestamp
            local_time = datetime.fromtimestamp(int("".join(unix_ts))/1000, local_timezone).strftime("%d:%m:%Y, %H:%M:%S")
            timestamps.append(local_time) 
        else:
            timestamps.append(None)
    return img_links, timestamps

# Adds image thumbnails for quick viewing
def convert_links_to_thumbnails(df):   
    def path_to_image_html(path):
        return '<img src="'+ path + '"width="200" >' 
    data_html = HTML(df.to_html(escape=False ,formatters=dict(thumbnail=path_to_image_html))) 
    return data_html

# Saves scraped data in csv and html formats
def save_data(df, html):
    with open("sharechat_data_html.html", "w") as f:
        f.write(html.data)
    df.drop("thumbnail", axis = 1, inplace = True)
    df.to_csv("sharechat_data.csv")


# Define scraper function
def sharechat_scraper(tags, destination):
    # Scrape data from specified tags
    sharechat_df = get_data(tags)
    # Generate html file with image thumbnails
    sharechat_data_html = convert_links_to_thumbnails(sharechat_df)
    # Save data 
    save_data(sharechat_df, sharechat_data_html)
    print("{} images scraped".format(len(sharechat_df)))
    print("Data saved to", destination)

# Define scraper arguments
t = ["topic/news-hindi-125", "topic/whatsapp-hindi-238", "trending/Hindi"] # tags to scrape
d = os.getcwd() # download destination

# Run scraper
if __name__ == "__main__":
    sharechat_scraper(t, d)

