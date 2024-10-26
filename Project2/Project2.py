import pymongo
import re
import pandas as pd
import argparse
import sys
import string

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["BugReports"]

collection1 = db["Collection1"]
collection2 = db["Collection2"]

# Adds data from file to collection in BugReports database
# file can be .xlsx or .csv
def dataDump(file, collection):
    if(".xlsx" in file):
        importDF = pd.read_excel(file)
        importDF['Build #'] = pd.to_datetime(importDF['Build #'], errors='coerce')
        importDF['Build #'] = importDF['Build #'].dt.strftime('%m/%d/%Y')
    elif(".csv" in file):
        importDF = pd.read_csv(file)

    data = importDF.to_dict(orient='records')
    
    if data:
        collection.insert_many(data)
        print(f"Successfully inserted {len(data)} records into {collection.name}")
    else:
        print("No data to insert.")


# Returns a list of all test cases with Test Owner: user from Collection2
def getUserList(user):
    return list(collection2.find({"Test Owner": user}, {"_id": 0}))


# Exports test cases for user to userExport.csv
def exportUser(user):
    exportDF = pd.DataFrame(getUserList(user))
    print(f"Exporting {len(exportDF)} test cases for user {user} to userExport.csv")
    exportDF.to_csv("userExport.csv", index=False)



# Returns a list of all duplicate locations in a list
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


# Prints test cases for Tigran Manukyan from both Collections
def disMyData():
    myList = list(collection1.find({"Test Owner": "Tigran Manukyan"}, {"_id": 0}))
    myList += getUserList("Tigran Manukyan")

    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame = dataFrame.drop(findDups(dataFrame["Test Case"]))
        print(f"Test Cases for Tigran Manukyan: \n{dataFrame}")
    else:
        print("No test cases found")

# Prints repeatable test cases from both collections
def disRepeatableBugs():
    myList = list(collection1.find({"Repeatable?": { "$in" : [re.compile("yes", re.IGNORECASE), re.compile("y", re.IGNORECASE)], "$not": re.compile("no", re.IGNORECASE)}}, {"_id": 0}))
    myList += list(collection2.find({"Repeatable?": { "$in" : [re.compile("yes", re.IGNORECASE), re.compile("y", re.IGNORECASE)], "$not": re.compile("no", re.IGNORECASE)}}, {"_id": 0}))
    
    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame = dataFrame.drop(findDups(dataFrame["Test Case"]))
        print(f"All Repeatable Test Cases: \n{dataFrame}")
        #dataFrame.to_csv("RepeatableExport.csv", index=False)

    else:
        print("No repeatable test cases found")

# Prints blocker test cases from both collections
def disBlockerBugs():
    myList = list(collection1.find({"Blocker?": { "$in" : [re.compile("yes", re.IGNORECASE), re.compile("y", re.IGNORECASE)], "$not": re.compile("no", re.IGNORECASE)}}, {"_id": 0}))
    myList += list(collection2.find({"Blocker?": { "$in" : [re.compile("yes", re.IGNORECASE), re.compile("y", re.IGNORECASE)], "$not": re.compile("no", re.IGNORECASE)}}, {"_id": 0}))
    
    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame = dataFrame.drop(findDups(dataFrame["Test Case"]))
        print(f"All Blocker Test Cases: \n{dataFrame}")
        #dataFrame.to_csv("BlockerExport.csv", index=False)

    else:
        print("No bloker test cases found")

# Prints test cases from both collections on date 10/8/24
def disAllOnDate():
    myList = list(collection1.find({"Build #": {"$in" : ["10/8/24", "10/08/2024"]}}, {"_id": 0}))
    myList += list(collection2.find({"Build #": {"$in" : ["10/8/24", "10/08/2024"]}}, {"_id": 0}))

    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame = dataFrame.drop(findDups(dataFrame["Test Case"]))
        print(dataFrame)
        print(f"All Repeatable Test Cases: \n{dataFrame}")

        dataFrame.to_csv("DateExport.csv", index=False)

    else:
        print("No test cases on date")



# Prints:
# 1st test case of Matthew Bellman
# middle test case of Sergio Garcia
# last of Denise Pacheco
def printTripleHeader():
    myList = getUserList("Matthew Bellman")
    
    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame.sort_values(by='Build #', inplace=True) 
        print(f"The first test case for Mattew Bellman: \n{dataFrame.loc[0]}")
    else:
        print("No test cases for Mattew Bellman")

    myList = getUserList("Sergio Garcia")
    
    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame.sort_values(by='Build #', inplace=True) 
        print(f"The first test case for Sergio Garcia: \n{dataFrame.loc[len(dataFrame) // 2]}")
    else:
        print("No test cases for Sergio Garcia")


    myList = getUserList("Denise Pacheco")
    
    if(myList):
        dataFrame = pd.DataFrame(myList)
        dataFrame.sort_values(by='Build #', inplace=True) 
        print(f"The first test case for Denise Pacheco: \n{dataFrame.loc[len(dataFrame)-1]}")
    else:
        print("No test cases for Denise Pacheco")



## parser 
parser = argparse.ArgumentParser(description='The Reckoning parser')
parser.add_argument('--file', type = str, required=False, 
                    help = 'Directory to csv or xlsx to import into datablse')
parser.add_argument('--collection', type = str,choices=["Collection1", "Collection2"],
                     required='--file' in sys.argv, help = 'Collection name')
parser.add_argument('--export_user', type = str, help = 'Export to a csv file a specific user')
parser.add_argument('--my_data', action='store_true', help = "Generates all work by me, aka Tigran Manukyan")
parser.add_argument('--all_repeatable', action='store_true', help = "Generates all repeatable test cases")
parser.add_argument('--all_blockers', action='store_true', help = "Generates all blocker test cases")
parser.add_argument('--all_on_date', action='store_true', help = "Generates all test cases on 10/8/24")
parser.add_argument('--triple_header', action='store_true', 
                    help = "Prints 1st test case of Matthew Bellman, middle test case of Sergio Garcia, last of Denise Pacheco")

args = parser.parse_args()

# if statements for parser
if(args.file):
    dataDump(args.file, db[args.collection])

if(args.export_user):
    exportUser(args.export_user)

if(args.my_data):
    disMyData()

if(args.all_repeatable):
    disRepeatableBugs()
    
if(args.all_blockers):
    disBlockerBugs()

if(args.all_on_date):
    disAllOnDate()

if(args.triple_header):
    printTripleHeader()