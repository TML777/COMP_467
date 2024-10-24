import pymongo
import pandas as pd
import argparse
import sys

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["BugReports"]

collection1 = db["Collection1"]
collection2 = db["Collection2"]



parser = argparse.ArgumentParser(description='The Reckoning parser')
parser.add_argument('--file', type = str, required=False, 
                    help = 'Directory to csv or xlsx to import into datablse')
parser.add_argument('--collection', type = str,choices=["Collection1", "Collection2"],
                     required='--file' in sys.argv, help = 'Collectoin name')
parser.add_argument('--export_user', type = str, help = 'Export to a csv file a specific user')

args = parser.parse_args()

if(args.file):
    collection = db[args.collection]
    
    if(".xlsx" in args.file):
        df = pd.read_excel(args.file)
    elif(".csv" in args.file):
        df = pd.read_csv(args.file)

    data = df.to_dict(orient='records')
    
    if data:
        collection.insert_many(data)
        print(f"Successfully inserted {len(data)} records into MongoDB")
    else:
        print("No data to insert.")
    

if(args.export):
    myList = list(collection1.find({"Test #": 0}, {"_id": 0}))
    print(myList)