import os
from dotenv import load_dotenv
load_dotenv()
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta

""" For debugging """

cli = MongoClient("mongodb+srv://"+os.environ.get("SHARECHAT_DB_USERNAME")+":"+os.environ.get("SHARECHAT_DB_PASSWORD")+"@tattle-data-fkpmg.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
db = cli[os.environ.get("SHARECHAT_DB_NAME")]
collection = db[os.environ.get("SHARECHAT_DB_COLLECTION")]
end = datetime.utcnow() - timedelta(days=30)
start = end - timedelta(days=1)
collection.aggregate([{"$match": {"scraped_date": {'$gte':start,'$lt':end}}}, {"$out": "luigi_testing"}])
collection = db["luigi_testing"]
print(collection.count_documents({}))
#print(collection.find_one())
# c=0
# for i in collection.find({"keyword_filter":{"$exists": True}}):
#     c+=1
# print(c)
# collection.updateMany({}, {"$unset": {"keyword_filter":1}})