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
import time
from random import uniform
from text_translation import initialize_translator, translate_text
from keyword_filter import filter_text

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
            for i in self.collection.find({"scraped_date": {'$gte':start,'$lt':end}}).limit(10): # limit for 
                print(i["media_type"])
                if i["media_type"] == "image":
                    out_file.write(i["s3_url"]+"\n")
                    #break

class ExtractText(luigi.Task):

    def output(self):
        return luigi.LocalTarget("extracted_text.txt")

    def run(self):
        client = initialize_googleapi()
        with self.output().open("w") as out_file:
            dump = []
            with self.input().open("r") as in_file:
                for url in in_file:
                    url = url.rstrip()
                    text = extract_text(client, url)
                    result = {url:text}
                    dump.append(result)
                out_file.write(json.dumps(dump))
                    #break

    def requires(self):
        return SourceData()

class TranslateText(luigi.Task):
    def output(self):
        return luigi.LocalTarget("translated_text.txt")

    def run(self):
        translator = initialize_translator()
        with self.output().open("w") as out_file:
            dump = []
            with self.input().open("r") as in_file:
                for extracted_text in in_file:
                    extracted_text = json.loads(extracted_text)
                    for url_text in extracted_text:
                        url = list(url_text.keys())[0]
                        text = list(url_text.values())[0]
                        translation = translate_text(text, translator)
                        dump.append({url:translation})
                        time.sleep(uniform(3,5))
                out_file.write(json.dumps(dump))
              
    def requires(self):
        return ExtractText()

class FilterText(luigi.Task):
    def output(self):
        return luigi.LocalTarget("filtered_text.txt")

    def run(self):
        with self.output().open("w") as out_file:
            dump = []
            with self.input().open("r") as in_file:
                for translated_text in in_file:
                    translated_text = json.loads(translated_text)
                    for url_translation in translated_text:
                        url = list(url_translation.keys())[0]
                        text = list(url_translation.values())[0]
                        label = filter_text(text)
                        dump.append({url:label})
                out_file.write(json.dumps(dump))
                        
    def requires(self):
        return TranslateText()