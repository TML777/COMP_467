from argparse import ArgumentParser
import pandas as pd
import re
from string import punctuation
import csv

from pymongo import MongoClient
myclient = MongoClient("mongodb://localhost:27017/")
db = myclient["TheCrucible"]

baselightCollection = db["Baselight"]
xytechCollection = db["Xytech"]


# final document to be outputed as csv
finalCSV = [["Producer", "Operator", "job", "notes"],["","","",""],[],["show location","frames to fix"]]
locations = {}




def importXytech(fileName):
    # open first file
    xytech = open(fileName, "r")

    xytechData = []


    inLocations = False
    inNotes = False
    notes = ""

    # reading first file
    for line in xytech.readlines():

        # spliting lines to make it easear to read
        lineCont = line.split()

        # checking to see if line isn't empty
        if(len(lineCont) > 0):

            # checking what the line is and adding it to its proper location
            if(inNotes):
                # setting notes in proper location
                notes = notes + line
            elif("Note" in lineCont[0]):
                # set notes flag
                inNotes = True
            elif(inLocations and "/" in lineCont[0]):
                # adding to locations map
                # key: what it will share with the baselight file
                # value: the actual location
                xytechData.append({"Location": lineCont[0]})
            elif("Location" in lineCont[0]):
                # set location flag
                inLocations = True
            elif("Producer" in lineCont[0]):
                # setting producer name in proper location
                xytechData.append({"Producer": " ".join(lineCont[1:])})
            elif("Operator" in lineCont[0]):
                # setting operator name in proper location
                xytechData.append({"Operator": " ".join(lineCont[1:])})
            elif("Job" in lineCont[0]):
                # setting job in proper location
                xytechData.append({"Job": " ".join(lineCont[1:])})

    xytechData.append({"Note": notes})

    xytechCollection.insert_many(xytechData)



def importBaselight(fileName):
    #open second file
    baseLight = open(fileName, "r")

    baselightData = []


    current = ""
    start = -1
    last = -1

    # reading each file cell by cell
    for cell in baseLight.read().split():

        # if cell contains '/', 
        if('/' in cell):
            
            # -1 represents that nothing to be added 
            # otherwise add last itterated cells
            if(start != -1):
                # start == last then single cell to be added 
                # start != last then range needs to be added
                if(start == last):
                    baselightData.append({"Location": current, "Frame": str(start)})
                else:
                    baselightData.append({"Location": current, "Frame": str(start) + "-" + str(last)})

                # reset start and last
                start = -1
                last = -1

            # setting 
            current = cell
        else:

            # make sure current cell is a number
            if(cell.isnumeric()):
                cellNum = int(cell)

                # if start == -1 then its the first cell so set start and last
                # if current cell is equal last cell + 1 then we have a range so change last cell and continue
                # otherwise we add it to the list 
                if(start == -1):
                    start = cellNum
                    last = cellNum
                elif(cellNum == last + 1):
                    last = cellNum
                else:
                    # start == last then single cell to be added 
                    # start != last then range needs to be added
                    if(start == last):
                        baselightData.append({"Location": current, "Frame": str(start)})
                    else:
                        baselightData.append({"Location": current, "Frame": str(start) + "-" + str(last)})
                    
                    start = cellNum
                    last = cellNum
                    
    # last cell being added if there is anything to add
    if(start != -1):
        # start == last then single cell to be added 
        # start != last then range needs to be added
        if(start == last):
            baselightData.append({"Location": current, "Frame": str(start)})
        else:
            baselightData.append({"Location": current, "Frame": str(start) + "-" + str(last)})

    baselightCollection.insert_many(baselightData)
            
        




def exportcsv():
    # output everything to csv file
    outputFile = open("job_2.csv", "w")
    outputWriter = csv.writer(outputFile)
    outputWriter.writerows(finalCSV)



parser = ArgumentParser(prog = "The Crucible", 
                        description="Enhancement of a prior project (Project 1) with a focus on integrating workflows for VP (Virtual Production), Gaming, and VFX.")

parser.add_argument('--baselight', 
                    type=str,
                    help= "Location of the baselight file to import into databse")
parser.add_argument('--xytech',
                    type=str,
                    help= "Location of the xytech file to import into databse")

parser.add_argument('-v', '--verbose',
                    action='store_true')

args = parser.parse_args()

if(args.baselight):
    importBaselight(args.baselight)
if(args.xytech):
    importXytech(args.xytech)
print(args.verbose)





##############Might be important later
# locations[str(lineCont[0][20:])] = lineCont[0]
# current = locations[cell[21:]]