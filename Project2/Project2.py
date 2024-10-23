import pymongo
import argparse

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["BugReports"]

collection1 = db["Collection1"]
collection2 = db["Collection2"]


cursor = collection1.find({})
for ent in cursor:
    print(ent["Test #"])

