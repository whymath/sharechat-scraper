import sys,os,json
from dotenv import load_dotenv
load_dotenv()
import pymongo
from pymongo import MongoClient
from google.cloud import vision
from google.protobuf.json_format import MessageToJson
import requests
import logging
import googletrans
from googletrans import Translator
import re

def initialize_mongo():
    client = MongoClient("mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
    #db = os.environ.get("SHARECHAT_DB_NAME")
    #collection = os.environ.get("LUIGI_TEST_COLLECTION")
    return client

def initialize_googleapi():
    return vision.ImageAnnotatorClient()

def extract_text(client, img_url):
    def image_from_url(img_url):
        resp = requests.get(img_url)
        img_bytes = resp.content 
        return img_bytes

    def detect_text(img_bytes):
        image_data = vision.types.Image(content=img_bytes)
        resp = client.text_detection(image=image_data)
        resp = json.loads(MessageToJson(resp))
        text = resp.get('fullTextAnnotation',{}).get('text','')
        return text

    try:
        img_bytes = image_from_url(img_url)
        text = detect_text(img_bytes)
        return text
    except:
        print(logging.traceback.format_exc())
        pass

def initialize_translator():
    return Translator()

def translate_text(text, translator):
    return translator.translate(text).text

keywords =  ["bjp" , "people", "modi" ,"social media", "media", "medium", "temple", "verification" ,"state" , "stock","statement",
"virus", "corona", "box", "coronavirus", "student" , "coro", "china" , "message", "india", "post",
 "muslim", "country", "lockdown", "rally", "riot", "president" , "house", "shah", "police", "name", "child" ,
 "woman", "girl", "man","leader", "worker" ,"rumor" ,"khan", "death", "gandhi", "minister", "election", "event", 
  "rahul gandhi" , "prime minister", "body", "vote" , "communal", "rape", "time", "army", "evidence",
  "food" ,  "mock" , "mock drill", "drill" , "day" , "footage", "delhi", "caa", "protest", "government" ,
 "person" ,"attack" ,"congress" ,"kashmir" , "money" ,"pradesh", "violence", "vaccine", "mob", "mosque",
 "party", "yogi", "hindus" "rss", "baton", "nrc", "assam", "party", "bihar", "suicide", "campaign", "photograph",
 "sonia", "priyanka", "murder", "bill", "kill", "scene", "cctv", "trump", "baby", "chief minister", "flag",
 "shaheen bagh", "fire", "speech", "case", "incident", "mla", "drug", "bangaldesh", "italy","youth", "airport",
 "performance", "slogan","soldier","maharashtra","crore", "bomb","indian", "strike", "celebration", "republic",
 "force", "nehru", "account", "run", "data", "report", "support", "old photo", "old photos", "islam", 
 "kejriwal", "story", "poster", "protester", "family", "photoshop", "tweet", "number", "bottle", "newspaper",
 "citizenship", "road", "jamia", "information", "jnu","patient", "bank", "member", "mla", "health", "ram",
 "mumbai","hospital","world","ministry", "community", "disease", "mother", "wrong", "infection", "law","hand",
 "datum", "stone", "sri", "kolkata", "gujarat", "doctor", "water", "show", "anil", "sharing", "hotel", "opposition"]

def get_keywords():
    return keywords

def filter_text(text):
    keywords = get_keywords()
    text = re.sub("[^a-zA-Z]", " ", text).lower().split()
    if len(set(keywords).intersection(set(text))) > 0:
        label = 1
    else:
        label = 0
    return label