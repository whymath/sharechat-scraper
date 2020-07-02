import os
from dotenv import load_dotenv
load_dotenv()
import pymongo
from pymongo import MongoClient

def initialize_mongo():
    client = MongoClient("mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
    # db and collection must be passed as strings
    #db = os.environ.get("SHARECHAT_DB_NAME")
    #collection = os.environ.get("LUIGI_TEST_COLLECTION")
    return client