import csv


# final document to be outputed as csv
finalCSV = [["Producer", "Operator", "job", "notes"],["","","",""],[],["show location","frames to fix"]]

# open first file
xytech = open("Xytech_fall2024.txt", "r")

# open second file
baseLight = open("Baselight_export_pickups_fall2024.txt", "r")



inLocations = False
inNotes = False
locations = {}

# reading first file
for line in xytech.readlines():

    # spliting lines to make it easear to read
    lineCont = line.split()

    # checking to see if line isn't empty
    if(len(lineCont) > 0):

        # checking what the line is and adding it to its proper location
        if(inNotes):
            # setting notes in proper location
            finalCSV[1][3] = finalCSV[1][3] + line
        elif("Note" in lineCont[0]):\
            # set notes flag
            inNotes = True
        elif(inLocations and "/" in lineCont[0]):
            # adding to locations map
            # key: what it will share with the baselight file
            # value: the actual location
            locations[str(lineCont[0][20:])] = lineCont[0]
        elif("Location" in lineCont[0]):
            # set location flag
            inLocations = True
        elif("Producer" in lineCont[0]):
            # setting producer name in proper location
            finalCSV[1][0] = " ".join(lineCont[1:])
        elif("Operator" in lineCont[0]):
            # setting operator name in proper location
            finalCSV[1][1] = " ".join(lineCont[1:])
        elif("Job" in lineCont[0]):
            # setting job in proper location
            finalCSV[1][2] = " ".join(lineCont[1:])




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
                finalCSV.append([current, str(start)])
            else:
                finalCSV.append([current, str(start) + "-" + str(last)])

            # reset start and last
            start = -1
            last = -1

        # setting 
        current = locations[cell[21:]]
    else:
        #finalCSV.append([current, cell])

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
                    finalCSV.append([current, str(start)])
                else:
                    finalCSV.append([current, str(start) + "-" + str(last)])
                
                start = cellNum
                last = cellNum
                
# last cell being added if there is anything to add
if(start != -1):
    # start == last then single cell to be added 
    # start != last then range needs to be added
    if(start == last):
            finalCSV.append([current, str(start)])
    else:
        finalCSV.append([current, str(start) + "-" + str(last)])
        
        
            
# output everything to csv file
outputFile = open("job_2.csv", "w")
outputWriter = csv.writer(outputFile)
outputWriter.writerows(finalCSV)