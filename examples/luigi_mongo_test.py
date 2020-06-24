import luigi
from luigi import contrib
from luigi.contrib import mongodb
# from contrib.mongodb import MongoTarget
import pandas as pd
import pymongo
from pymongo import MongoClient

class SourceData(luigi.Task):
    filename = luigi.Parameter() # replace with date

    def output(self):
        return luigi.LocalTarget("urls.csv") 

    def run(self):
        df = pd.read_csv(self.filename) 
        # replace with coll = os.system("mongo_access_script.py")
        # filter & load data to df using date parameter
        urls = df["s3_url"] 
        with self.output().open('w') as f:
            for url in urls:
                f.write(url)

class StoreUrl(luigi.Task):
    filename = luigi.Parameter()

    def output(self):
        cli = MongoClient("mongodb+srv://dev_sharechat:epJbUkQu72WHmpLN@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        return mongodb.MongoTarget(mongo_client=cli, index="dev_sharechat", collection="luigi_test")

    def run(self):
        cli = MongoClient("mongodb+srv://dev_sharechat:epJbUkQu72WHmpLN@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        db = cli["dev_sharechat"]
        coll = db["luigi_test"]
        coll.insert_one({"test":"hello"}) 

    def requires(self):
        return SourceData(filename=self.filename)