import os
import pandas as pd 
import numpy as np 
import datetime
from datetime import date
import pickle
import requests
import json
import time
from random import uniform
from dotenv import load_dotenv
load_dotenv() 

USER_ID = os.environ.get("SHARECHAT_USER_ID")
PASSCODE = os.environ.get("SHARECHAT_PASSWORD")
today = pd.Timestamp("today")
metrics = ["external_shares", "likes", "comments", "reposts", "views"]
sample_size = 50

def create_sample_df(main_df, n):
    # Create sample data
    sample_df = main_df.sample(n)
    sample_df.reset_index(inplace=True)
    # Save sample df
    today = str(date.today())
    pd.to_pickle(sample_df, "sample_df_{}.pkl".format(today))

def generate_requests_dict(post_key):
    requests_dict = {
        "post_body": {
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
    return requests_dict

def save_updated_df(df, today):
    pd.to_pickle(df, "sample_df_{}.pkl".format(today))
    df.to_csv("sample_df_{}.csv".format(today))

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

def get_current_metrics(post_permalink):
    post_key = post_permalink.split("/")[-1]
    requests_dict = generate_requests_dict(post_key)
    # Send API request 
    url = requests_dict["api_url"]
    body = requests_dict["post_body"]
    headers = requests_dict["headers"]
    response = requests.post(url=url, json=body, headers=headers)
    time.sleep(uniform(30,35))
    response_dict = json.loads(response.text)
    # Scrape current metrics for post
    result = scrape_metrics(response_dict)
    return result

def virality_tracker(sample_df_path, today):
    print("Scraping current virality metrics...")
    start_time = time.time()
    # Load sample data
    sample_df = pd.read_pickle(sample_df_path)
    # Get timestamp for day t
    sample_df["scraped_date"] = pd.to_datetime(sample_df["scraped_date"])
    timestamp = sample_df["scraped_date"][0]
    # Calculate days since t
    diff = str((today-timestamp).days)
    # Initialize df to hold current metrics
    result_df = pd.DataFrame(columns = ["comments_t+"+diff,
                                         "external_shares_t+"+diff,
                                         "likes_t+"+diff,
                                         "reposts_t+"+diff,
                                         "views_t+"+diff])
    # Get current virality metrics for each post
    for i in sample_df["post_permalink"]:
        result = get_current_metrics(i)
        result_df = result_df.append(pd.DataFrame(result, 
                                                columns = result_df.columns, 
                                                ), sort = True)
    # Add scraped metrics to sample data
    new_df = pd.concat([sample_df.reset_index(drop=True), result_df.reset_index(drop=True)], axis = 1)
    # Save combined data
    save_updated_df(new_df, today)
    print("Time taken: %s seconds" % (time.time() - start_time))
    return new_df

main_df = pd.read_csv(os.environ.get("MAIN_DF"))
create_sample_df(main_df, sample_size)

virality_tracker(os.environ.get("SAMPLE_DF_PKL_PATH"), today)