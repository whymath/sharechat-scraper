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

class SourceData(luigi.Task):
    # filename = luigi.Parameter() 

    # def output(self):
    #     print("hello")
    #     return luigi.LocalTarget("urls.txt") 

    # def run(self):
    #     df = pd.read_csv(self.filename) 
    #     urls = df["s3_url"] 
    #     with self.output().open('w') as f:
    #         for url in urls:
    #             f.write(url)
    cli = MongoClient("mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
    db = cli[os.environ.get("SHARECHAT_DB_NAME")]
    collection = db[os.environ.get("SHARECHAT_DB_COLLECTION")]

    def output(self):
        return luigi.LocalTarget('urls.txt')
        
    def run(self):
        end = datetime.utcnow()
        start = end - timedelta(days=1)
        with self.output().open("w") as f:
            for i in self.collection.find({"scraped_date": {'$gte':start,'$lt':end}}):
                if i["media_type"] == "image":
                    f.write(i["s3_url"]+"\n")

