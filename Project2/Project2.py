import argparse
from pymongo import MongoClient
import pandas as pd
import re
from sys import argv as commandLineArguments
from string import punctuation

myclient = MongoClient("mongodb://localhost:27017/")
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

# Returns list from both collections based on query
def getFromBothCollections(query):
    tempList = list(collection1.find(query, {"_id": 0}))
    tempList += list(collection2.find(query, {"_id": 0})) 
    return tempList


# Exports test cases for user to userExport.csv
def exportUser(user):
    exportDF = pd.DataFrame(getUserList(user))
    print(f"Exporting {len(exportDF)} test cases for user {user} to userExport.csv")
    exportDF.to_csv("userExport.csv", index=False)





# Modifies removeList to add all duplicate locations in a list of sentences
# List should not be empty
# Goes thru the list and if the words for a sentence appear on any other sentence before it,
#       it is considered a repeat
# The ratio of how many words need to match can be modified by PERCENTAGE_OF_WORDS
#       1 being 100% of words in current sentence need to apear in 
#           any other sentence before the curent
#           in other wrods the closer to 1 the more give it has
#       (0.85 was tuned with all repeatable bug entries)
# Since list can be two lists connected together, 
#       listDivide is where in list it list divides
#       leftIndex is what the index on of left of dived should be
#       rightIndex is what the index on of left of dived should be
def findDups(list, removeList, listDivide, leftIndex, rightIndex):
    PERCENTAGE_OF_WORDS = 0.85
    if(list):
        temp = str(list[0]).translate(str.maketrans('', '', punctuation))
        temp = temp.lower()
        stringList = temp.split()

        for i in range(1, len(list)):
            match = 0
            unmatch = 0
            temp = str(list[i]).translate(str.maketrans('', '', punctuation))
            temp = temp.lower()
            temp = temp.split()
            
            ratio = len(temp)*PERCENTAGE_OF_WORDS
            for word in temp:
                if(word in stringList):
                    match += 1
                else:
                    unmatch += 1
                    stringList.append(word)
                
                if(match >= ratio or unmatch>=ratio):
                    if(match >= ratio):
                        rowToRemove = i

                        if(rowToRemove < listDivide):
                            rowToRemove += leftIndex*listDivide
                        else:
                            rowToRemove += (rightIndex*listDivide - listDivide)

                        if rowToRemove not in removeList:
                            removeList.append(rowToRemove)
                        
                    break
                
                


# Takes in a list and returns DataFrame without dupelicates
# Since with a big enough database my current method would remove all of the last entries
# So divide the list into partitions and compare those partitions together
# to better the algortithm DIVIDE_AMOUNT can be changed (higher->better)
# to optimize runtime (for current database), 6 should be fine
def dropDupes(list):
    DIVIDE_AMOUNT = 6
    dataFrame = pd.DataFrame(list)
    dataFrame.reset_index(drop=True, inplace=True)

    toRemove = []
    tempList = dataFrame["Test Case"].tolist()
    listDivide = len(tempList)//DIVIDE_AMOUNT
    for i in range(0,DIVIDE_AMOUNT):
        for j in range(DIVIDE_AMOUNT, i, -1):
            
            runList = tempList[i*listDivide:(i+1)*listDivide]
            runList += tempList[j*listDivide:(j+1)*listDivide]

            findDups(runList, toRemove, listDivide, i, j)


    dataFrame.drop(toRemove,  errors='ignore', inplace= True)
    dataFrame.reset_index(drop=True, inplace=True)
    return dataFrame



# Prints test cases for Tigran Manukyan from both Collections
def disMyData():
    tempList = getFromBothCollections({"Test Owner": "Tigran Manukyan"})

    if(tempList):
        dataFrame = dropDupes(tempList)

        print(f"Test Cases for Tigran Manukyan: \n{dataFrame}")

        print(f"Exporting {len(dataFrame)} test cases for Tigran Manukyan to TigranExport.csv")
        dataFrame.to_csv("TigranExport.csv", index=False)
    else:
        print("No test cases found")

# Prints repeatable test cases from both collections
def disRepeatableBugs():
    tempList = getFromBothCollections({"Repeatable?": { "$in" : [re.compile("yes", re.IGNORECASE), re.compile("y", re.IGNORECASE)], "$not": re.compile("no", re.IGNORECASE)}})
    if(tempList):
        dataFrame = dropDupes(tempList)

        print(f"All Repeatable Test Cases: \n{dataFrame}")

        print(f"Exporting {len(dataFrame)} repeatable test cases to RepeatableExport.csv")
        dataFrame.to_csv("RepeatableExport.csv", index=False)

    else:
        print("No repeatable test cases found")

# Prints blocker test cases from both collections
def disBlockerBugs():
    tempList = getFromBothCollections({"Blocker?": { "$in" : [re.compile("yes", re.IGNORECASE), re.compile("y", re.IGNORECASE)], "$not": re.compile("no", re.IGNORECASE)}})
    if(tempList):
        dataFrame = dropDupes(tempList)
        print(f"All Blocker Test Cases: \n{dataFrame}")

        print(f"Exporting {len(dataFrame)} blocker test cases to BlockerExport.csv")
        dataFrame.to_csv("BlockerExport.csv", index=False)

    else:
        print("No bloker test cases found")


# Prints test cases from both collections on date 10/8/24
def disAllOnDate():
    tempList = getFromBothCollections({"Build #": {"$in" : ["10/8/24", "10/08/2024"]}})
    if(tempList):
        dataFrame = dropDupes(tempList)
        (f"All test cases on 10/8/24: \n{dataFrame}")

        print(f"Exporting {len(dataFrame)} test cases on 10/8/24 to DateExport.csv")
        dataFrame.to_csv("DateExport.csv", index=False)

    else:
        print("No test cases on date")



# Prints and exports to csv:
# 1st test case of Matthew Bellman
# middle test case of Sergio Garcia
# last of Denise Pacheco
def printTripleHeader():
    userList = getUserList("Matthew Bellman")
    
    if(userList):
        dataFrame = pd.DataFrame(userList)
        dataFrame.sort_values(by='Build #', inplace=True) 
        print(f"The first test case for Mattew Bellman: \n{dataFrame.loc[0]}")

        print(f"Exporting first test case for Matthew Bellman to BellmanExport.csv")
        dataFrame.iloc[[0]].to_csv("BellmanExport.csv", index=False)
    else:
        print("No test cases for Mattew Bellman")

    userList = getUserList("Sergio Garcia")
    
    if(userList):
        dataFrame = pd.DataFrame(userList)
        dataFrame.sort_values(by='Build #', inplace=True) 
        print(f"\nThe first test case for Sergio Garcia: \n{dataFrame.loc[len(dataFrame) // 2]}")

        print(f"Exporting middle test case for Sergio Garcia to GarciaExport.csv")
        dataFrame.iloc[[len(dataFrame) // 2]].to_csv("GarciaExport.csv", index=False)
    else:
        print("No test cases for Sergio Garcia")


    userList = getUserList("Denise Pacheco")
    
    if(userList):
        dataFrame = pd.DataFrame(userList)
        dataFrame.sort_values(by='Build #', inplace=True) 
        print(f"\nThe last test case for Denise Pacheco: \n{dataFrame.loc[len(dataFrame)-1]}")

        print(f"Exporting last test case for Denis Pacheco to PachecoExport.csv")
        dataFrame.iloc[[len(dataFrame)-1]].to_csv("PachecoExport.csv", index=False)
    else:
        print("No test cases for Denise Pacheco")



## parser 
parser = argparse.ArgumentParser(description='The Reckoning Parser')
parser.add_argument('--file', type = str, required=False, 
                    help = 'Directory to csv or xlsx to import into datablse')
parser.add_argument('--collection', type = str,choices=["Collection1", "Collection2"],
                     required='--file' in commandLineArguments, help = 'Collection name')
parser.add_argument('--my_data', action='store_true', help = "Generates all work by me, aka Tigran Manukyan")
parser.add_argument('--all_repeatable', action='store_true', help = "Generates all repeatable test cases")
parser.add_argument('--all_blocker', action='store_true', help = "Generates all blocker test cases")
parser.add_argument('--all_on_date', action='store_true', help = "Generates all test cases on 10/8/24")
parser.add_argument('--triple_header', action='store_true', 
                    help = "Prints 1st test case of Matthew Bellman, middle test case of Sergio Garcia, last of Denise Pacheco")
parser.add_argument('--export_user', type = str, help = 'Export to a csv file a specific user')


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
    
if(args.all_blocker):
    disBlockerBugs()

if(args.all_on_date):
    disAllOnDate()

if(args.triple_header):
    printTripleHeader()




"""
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py -h                                        
usage: Project2.py [-h] [--file FILE] [--collection {Collection1,Collection2}] [--my_data] [--all_repeatable] [--all_blocker] [--all_on_date]
                   [--triple_header] [--export_user EXPORT_USER]

The Reckoning Parser

options:
  -h, --help            show this help message and exit
  --file FILE           Directory to csv or xlsx to import into datablse
  --collection {Collection1,Collection2}
                        Collection name
  --my_data             Generates all work by me, aka Tigran Manukyan
  --all_repeatable      Generates all repeatable test cases
  --all_blocker         Generates all blocker test cases
  --all_on_date         Generates all test cases on 10/8/24
  --triple_header       Prints 1st test case of Matthew Bellman, middle test case of Sergio Garcia, last of Denise Pacheco
  --export_user EXPORT_USER
                        Export to a csv file a specific user
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --file Oct7.csv --collection Collection1  
Successfully inserted 7 records into Collection1
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --file Oct14.csv --collection Collection1  
Successfully inserted 7 records into Collection1
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --file Oct20.csv --collection Collection1  
Successfully inserted 9 records into Collection1
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --file EG4-DBDump_Fall2024.xlsx --collection Collection2
Successfully inserted 1600 records into Collection2
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --my_data                                              
Test Cases for Tigran Manukyan: 
    Test #   Build #                        Category  ... Repeatable? Blocker?       Test Owner
0        0   10/7/24           Deck Builder Tutorial  ...         Yes       No  Tigran Manukyan
1        1   10/8/24           Deck Builder Tutorial  ...         yes      yes  Tigran Manukyan
2        2   10/8/24  Tutorial/Deck Builder Tutorial  ...         NaN       No  Tigran Manukyan
3        3   10/8/24                           Arena  ...         Yes       No  Tigran Manukyan
4        4   10/8/24                           Arena  ...         NaN       No  Tigran Manukyan
5        5   10/8/24                    Edit Profile  ...         Yes       No  Tigran Manukyan
6        6   10/8/24              Home Page/Settings  ...         Yes       No  Tigran Manukyan
7        0  10/14/24              Arena\Battle Phase  ...         Yes       No  Tigran Manukyan
8        1  10/15/24              Arena\Battle Phase  ...          No      Yes  Tigran Manukyan
9        2  10/15/24              Arena\Battle Phase  ...          No       No  Tigran Manukyan
10       3  10/15/24                Arena\Main Phase  ...         Yes      Yes  Tigran Manukyan
11       4  10/15/24                Arena\Main Phase  ...         Yes      No   Tigran Manukyan
12       5  10/15/24              Arena\Battle Phase  ...          No      Yes  Tigran Manukyan
13       6  10/15/24              Arena\Battle Phase  ...         Yes       No  Tigran Manukyan
14       0  10/20/24                Arena\Main Phase  ...          No       No  Tigran Manukyan
15       1  10/20/24                Arena\Main Phase  ...         Yes       No  Tigran Manukyan
16       2  10/20/24         Arena\Specian Abilities  ...         Yes       No  Tigran Manukyan
17       3  10/20/24                    Arena\Battle  ...         Yes      Yes  Tigran Manukyan
18       4  10/20/24                      Arena\Draw  ...         Yes       No  Tigran Manukyan
19       5  10/20/24             Arean\Defeat Screen  ...         Yes       No  Tigran Manukyan
20       6  10/20/24                   Arena\Options  ...         Yes       No  Tigran Manukyan
21       7  10/20/24                Arena\Main Phase  ...         Yes       No  Tigran Manukyan
22       8  10/20/24                      Arena\Draw  ...        Yes        No  Tigran Manukyan

[23 rows x 9 columns]
Exporting 23 test cases for Tigran Manukyan to TigranExport.csv
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --all_repeatable
All Repeatable Test Cases: 
    Test #     Build #               Category  ... Repeatable? Blocker?        Test Owner
0        0     10/7/24  Deck Builder Tutorial  ...         Yes       No   Tigran Manukyan
1        1     10/8/24  Deck Builder Tutorial  ...         yes      yes   Tigran Manukyan
2        3     10/8/24                  Arena  ...         Yes       No   Tigran Manukyan
3        5     10/8/24           Edit Profile  ...         Yes       No   Tigran Manukyan
4        6     10/8/24     Home Page/Settings  ...         Yes       No   Tigran Manukyan
..     ...         ...                    ...  ...         ...      ...               ...
425      3  10/15/2024                   Game  ...         yes       no  Robert Stevenson
426      4  10/14/2024      Arena/Matchmaking  ...         Yes      Yes           Shervin
427      3  10/13/2024                  Login  ...         yes       no     Dakota Wagner
428      4  10/13/2024              Main Page  ...         yes       no     Dakota Wagner
429      5  10/13/2024                  Login  ...         yes       no     Dakota Wagner

[430 rows x 9 columns]
Exporting 430 repeatable test cases to RepeatableExport.csv
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --all_blocker 
All Blocker Test Cases: 
     Test #     Build #               Category  ... Repeatable? Blocker?        Test Owner
0       1.0     10/8/24  Deck Builder Tutorial  ...         yes      yes   Tigran Manukyan
1       1.0    10/15/24     Arena\Battle Phase  ...          No      Yes   Tigran Manukyan
2       3.0    10/15/24       Arena\Main Phase  ...         Yes      Yes   Tigran Manukyan
3       5.0    10/15/24     Arena\Battle Phase  ...          No      Yes   Tigran Manukyan
4       3.0    10/20/24           Arena\Battle  ...         Yes      Yes   Tigran Manukyan
..      ...         ...                    ...  ...         ...      ...               ...
203     NaN  10/15/2024                GAME UI  ...         yes      yes  AB Paxtor Garcia
204     1.0  10/15/2024                  Login  ...      yes/no      yes   Alberto Santana
205     3.0  10/14/2024           Deck Builder  ...         Yes      Yes            Matteo
206     4.0  10/14/2024      Arena/Matchmaking  ...         Yes      Yes           Shervin
207     3.0         NaN       Adventure Select  ...          NO      YES    Dhruv Vagadiya

[208 rows x 9 columns]
Exporting 208 blocker test cases to BlockerExport.csv
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --all_on_date
All test cases on 10/8/24: 
    Test #     Build #                        Category  ... Repeatable? Blocker?        Test Owner
0      1.0     10/8/24           Deck Builder Tutorial  ...         yes      yes   Tigran Manukyan
1      2.0     10/8/24  Tutorial/Deck Builder Tutorial  ...         NaN       No   Tigran Manukyan
2      3.0     10/8/24                           Arena  ...         Yes       No   Tigran Manukyan
3      4.0     10/8/24                           Arena  ...         NaN       No   Tigran Manukyan
4      5.0     10/8/24                    Edit Profile  ...         Yes       No   Tigran Manukyan
..     ...         ...                             ...  ...         ...      ...               ...
74    14.0  10/08/2024                              UI  ...         NaN      NaN  Robert Stevenson
75     1.0  10/08/2024                          Login   ...        Yes        No    Shawn Takhirov
76     2.0  10/08/2024                       Main Page  ...          No       No    Shawn Takhirov
77     3.0  10/08/2024                            Game  ...         Yes       No    Shawn Takhirov
78     4.0  10/08/2024                            Game  ...         Yes       No    Shawn Takhirov

[79 rows x 9 columns]
Exporting 79 test cases on 10/8/24 to DateExport.csv
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --triple_header
The first test case for Mattew Bellman: 
Test #                                                             1
Build #                                                   10/08/2024
Category                                                       Login
Test Case                     Login page for wallet seems unhelpful.
Expected Result    Either for the site to redirect me to the exte...
Actual Result      A popup that shows a usless QR code for mobile...
Repeatable?                                                      Yes
Blocker?                                                          No
Test Owner                                           Matthew Bellman
Name: 0, dtype: object
Exporting first test case for Matthew Bellman to BellmanExport.csv

The first test case for Sergio Garcia: 
Test #                                                             2
Build #                                                   10/08/2024
Category                                                        Game
Test Case              user case:  not enough ways to counter enemy 
Expected Result    there is more ways to counteract situations su...
Actual Result      when faced with no cards on deck it seem like ...
Repeatable?                                                      yes
Blocker?                                                          no
Test Owner                                             Sergio Garcia
Name: 4, dtype: object
Exporting middle test case for Sergio Garcia to GarciaExport.csv

The last test case for Denise Pacheco: 
Test #                                                             4
Build #                                                   10/12/2024
Category                                         Arena/UI/EndersGate
Test Case          Improvement: The scroll bar should stop at the...
Expected Result        Scroller stops after last card is fully shown
Actual Result               Scroller bar goes far past the last item
Repeatable?                                                      yes
Blocker?                                                          no
Test Owner                                            Denise Pacheco
Name: 8, dtype: object
Exporting last test case for Denis Pacheco to PachecoExport.csv
tiko@Tikos-MacBook-Pro Project2 % python3 Project2.py --export_user "Kevin Chaja"
Exporting 25 test cases for user Kevin Chaja to userExport.csv
tiko@Tikos-MacBook-Pro Project2 % 

"""