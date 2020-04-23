import os
import boto3
from boto3 import client
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv() 
import sys

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
    mongo_url = "mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"   
    cli = MongoClient(mongo_url)
    db = cli[os.environ.get("SHARECHAT_DB_NAME")]
    coll = db[os.environ.get("SHARECHAT_DB_COLLECTION")]
    if coll.count_documents({}) > 0:
        return coll 
    else:
        print("Error accessing Mongo collection")
        sys.exit()
        

def upload_to_s3(s3, file, filename, bucket, content_type):
    with open(file, "rb")as data:
        s3.upload_fileobj(Fileobj = data, 
                          Bucket = bucket,
                          Key = filename,
                          ExtraArgs={'ContentType': content_type,
                                    'ACL': 'public-read'})  
               
def upload_to_mongo(data, coll):
    coll.insert_one(data) 

def count_s3_files(s3, bucket):
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket)
    file_count = 0
    for page in pages:
        for obj in page['Contents']:
            file_count += 1
    return file_count

# Get files uploaded to S3 in a date range
# Date format - datetime.datetime(YYYY, M, D, %h, %m, %s, tzinfo=tzutc()
def filter_s3_files(s3, bucket, start_date, end_date):
    objects = s3.list_objects_v2(Bucket=bucket)
    files = [{'Key': o['Key']} for o in objects['Contents'] if end_date > o['LastModified'] > start_date]
    return files

def delete_s3_files(s3, bucket, start_date, end_date):
    keys_to_delete = filter_s3_files(s3, bucket, start_date, end_date)
    s3.delete_objects(Bucket=bucket, Delete={'Objects': keys_to_delete})
    print("{} S3 files deleted".format(len(keys_to_delete)))


