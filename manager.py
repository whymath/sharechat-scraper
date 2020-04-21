# from trending_content_scraper import trending_content_scraper
# from fresh_content_scraper import fresh_content_scraper
# from ml_scraper import ml_scraper
# from virality_scraper import virality_scraper
from sharechat_scrapers import trending_content_scraper, fresh_content_scraper, ml_scraper, virality_scraper
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
import selenium
from selenium import webdriver

def scraper_manager(scraper_params):
    try:
        if scraper_params["content_to_scrape"] == "trending":
            trending_content_scraper(USER_ID=scraper_params["USER_ID"],
                                     PASSCODE=scraper_params["PASSCODE"],
                                     tag_hashes=scraper_params["tag_hashes"],
                                     pages=scraper_params["pages"])
        elif scraper_params["content_to_scrape"] == "fresh":
            fresh_content_scraper(USER_ID=scraper_params["USER_ID"],
                                     PASSCODE=scraper_params["PASSCODE"],
                                     tag_hashes=scraper_params["tag_hashes"],
                                     pages=scraper_params["pages"],
                                     unix_timestamp=scraper_params["unix_timestamp"]
                                     )
        elif scraper_params["content_to_scrape"] == "virality":
            virality_scraper(USER_ID=scraper_params["USER_ID"], PASSCODE=scraper_params["PASSCODE"], data_path=scraper_params["data_path"])
        elif scraper_params["content_to_scrape"] == "ml":
            ml_scraper(USER_ID=scraper_params["USER_ID"],
                       PASSCODE=scraper_params["PASSCODE"],
                       tag_hashes=scraper_params["tag_hashes"],
                       pages=scraper_params["pages"])
        else:
            raise ValueError("Invalid value entered for content_to_scrape. Select one from: trending, fresh, virality_metrics, ml")
    except Exception as e:
        print(logging.traceback.format_exc())
