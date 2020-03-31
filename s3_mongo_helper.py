import os
import boto3
from boto3 import client
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv() 

# Helper functions to upload to Mongo and S3

def initialize_s3():
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY_ID")
    aws = os.environ.get("AWS_BASE_URL")
    bucket = os.environ.get("AWS_BUCKET")
    s3 = boto3.client("s3", aws_access_key_id = aws_access_key_id,
                          aws_secret_access_key= aws_secret_access_key) 
    return aws, bucket, s3
    
def initialize_mongo():
    mongo_url = "mongodb+srv://"+os.environ.get("DB_USERNAME")+":"+os.environ.get("DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"   
    cli = MongoClient(mongo_url)
    db = os.environ.get("DB_NAME")
    coll = db[os.environ.get("DB_COLLECTION")]
    return cli, db, coll 
    

def upload_to_s3(file, filename, bucket, content_type):
    with open(file, "rb")as data:
        s3.upload_fileobj(Fileobj = data, 
                          Bucket = bucket,
                          Key = filename,
                          ExtraArgs={'ContentType': content_type,
                                    'ACL': 'public-read'})  
               
def upload_to_mongo(data):
    coll.insert_one(data) 

