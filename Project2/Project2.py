import pymongo
import pandas as pd
import argparse
import sys
import string

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["BugReports"]

collection1 = db["Collection1"]
collection2 = db["Collection2"]


def dataDump(file, collection):
    if(".xlsx" in file):
        importDF = pd.read_excel(file, date_format="%m/%d/%Y")
    elif(".csv" in file):
        importDF = pd.read_csv(file)

    data = importDF.to_dict(orient='records')
    
    if data:
        collection.insert_many(data)
        print(f"Successfully inserted {len(data)} records into {collection.name}")
    else:
        print("No data to insert.")


def exportUser(user):
    myList = list(collection2.find({"Test Owner": user}, {"_id": 0}))
    
    exportDF = pd.DataFrame(myList)

    exportDF.to_csv("userExport.csv", index=False)



def findDups(list):
    
    toRemove = []
    temp = list[0].translate(str.maketrans('', '', string.punctuation))
    temp = temp.lower()

    
    
    stringList = temp.split()
    for i in range(1, len(list)):
        match = 0
        unmatch = 0

        temp = list[i].translate(str.maketrans('', '', string.punctuation))
        temp = temp.lower()
        temp = temp.split()

        ratio = len(temp)*.90
        for word in temp:
            
            if(match >= ratio or unmatch>=ratio):
                if(match >= ratio):
                    toRemove.append(i)
                break
            
            if(word in stringList):
                match += 1
            else:
                unmatch += 1
        
        stringList += temp

    return toRemove




parser = argparse.ArgumentParser(description='The Reckoning parser')
parser.add_argument('--file', type = str, required=False, 
                    help = 'Directory to csv or xlsx to import into datablse')
parser.add_argument('--collection', type = str,choices=["Collection1", "Collection2"],
                     required='--file' in sys.argv, help = 'Collectoin name')
parser.add_argument('--export_user', type = str, help = 'Export to a csv file a specific user')
parser.add_argument('--the_details', action='store_true', help = "Generates specific details from both collections")

args = parser.parse_args()

if(args.file):
    dataDump(args.file, db[args.collection])

if(args.export_user):
    exportUser(args.export_user)

if(args.the_details):
    myList = list(collection1.find({"Test Owner": "Tigran Manukyan"}, {"_id": 0}))
    myList += list(collection2.find({"Test Owner": "Tigran Manukyan"}, {"_id": 0}))

    df = pd.DataFrame(myList)
    print(df)

    df = df.drop(findDups(df["Test Case"]))
    print(df)




