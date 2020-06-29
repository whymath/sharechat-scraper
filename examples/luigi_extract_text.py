from dotenv import load_dotenv
load_dotenv()
import os
import pymongo
from pymongo import MongoClient
import luigi 
from luigi import contrib
from luigi.contrib import mongodb
import pandas as pd
import datetime
from datetime import datetime
from datetime import timedelta
import text_extraction
from text_extraction import initialize_googleapi, extract_text
import requests
import json

class SourceData(luigi.Task):
    cli = MongoClient("mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
    db = cli[os.environ.get("SHARECHAT_DB_NAME")]
    collection = db[os.environ.get("SHARECHAT_DB_COLLECTION")]

    def output(self):
        return luigi.LocalTarget('urls.txt')
        
    def run(self):
        end = datetime.utcnow()
        start = end - timedelta(days=1)
        with self.output().open("w") as out_file:
            for i in self.collection.find({"scraped_date": {'$gte':start,'$lt':end}}):
                if i["media_type"] == "image":
                    out_file.write(i["s3_url"]+"\n")
                    #break

class ExtractText(luigi.Task):

    def output(self):
        return luigi.LocalTarget("extracted_text.txt")

    def run(self):
        client = initialize_googleapi()
        with self.output().open('w') as out_file:
            with self.input().open('r') as in_file:
                for line in in_file:
                    line = line.rstrip()
                    text = extract_text(client, line)
                    result = {line:text}
                    out_file.write(json.dumps(result))
                    out_file.write("\n")
                    #break

    def requires(self):
        return SourceData()