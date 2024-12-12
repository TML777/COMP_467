from argparse import ArgumentParser
import pandas as pd
from csv import writer as csvWriter
import ffmpeg
from subprocess import run as subRun
from os import mkdir
from shutil import rmtree
#from frameioclient import FrameioClient
from pymongo import MongoClient


myclient = MongoClient("mongodb://localhost:27017/")
db = myclient["TheCrucible"]

baselightCollection = db["Baselight"]
xytechCollection = db["Xytech"]


xlsFlag = False
csvFlag = False

fps = 25


def framesToTime(totalFrames):
    returnString = f":{totalFrames%fps:02}"

    time = totalFrames // fps

    returnString = f":{time%60:02}" + returnString

    time = time // 60

    returnString = f":{time%60:02}" + returnString

    time = time // 60

    return f"{time:02}" + returnString




def importXytech(fileName):
    # open first file
    xytech = open(fileName, "r")

    xytechData = []

    infoData = {}


    inLocations = False
    inNotes = False
    notes = ""

    # xytech line by line
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
                inNotes = True
            elif(inLocations and "/" in lineCont[0]):
                xytechData.append({"Location": lineCont[0]})
            elif("Location" in lineCont[0]):
                inLocations = True
            elif("Producer" in lineCont[0]):
                infoData["Producer"] = " ".join(lineCont[1:])
            elif("Operator" in lineCont[0]):
                infoData["Operator"] = " ".join(lineCont[1:])
            elif("Job" in lineCont[0]):
                infoData["Job"] = " ".join(lineCont[1:])

    infoData["Note"] = notes

    xytechData.append(infoData)

    xytechCollection.insert_many(xytechData)



def importBaselight(fileName):
    #open baselight file
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



def startProcess(videoPath):
    probe = ffmpeg.probe(videoPath)
    duration = float(probe['format']['duration'])


    # client = FrameioClient("fio-u-W5pGArD5iT4qCuObzbupqPBFvKNyIn5ZI58kqENCysIWEu8_3wocUTK-vbUsGAmX")
    

    if(xlsFlag or csvFlag):

        finalCSV = [["Producer", "Operator", "job", "notes"],["","","",""],[],["Location","Frame Ranges", "Timecode Ranges", "Thumbnail"]]
        locations = {}

        temp = list(xytechCollection.find({"Location": {"$exists":False}},{"_id":0}))[0]
        finalCSV[1][0] = temp["Producer"]
        finalCSV[1][1] = temp["Operator"]
        finalCSV[1][2] = temp["Job"]
        finalCSV[1][3] = temp["Note"]

        for loc in xytechCollection.find({"Location": {"$exists":True}},{"_id":0}):

            locations['/'.join(loc["Location"].split('/')[3:])] = loc["Location"]
            
        if(xlsFlag):
            df = pd.DataFrame(finalCSV)            

            writer = pd.ExcelWriter('rangesInVideo.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
            worksheet = writer.sheets['Sheet1']


            # temp folder for tumbnails
            mkdir("tempThumbnailFolder")

            excelLocation = 5



    # temp folder for videos
    mkdir("tempVideoFolder")
    
    
    for row in baselightCollection.find({},{"_id":0}):
        frameSplit = row["Frame"].split('-')
        if(len(frameSplit)>1 and int(frameSplit[1])/fps < duration):

            cmd = [
                    "ffmpeg",
                    "-v", "quiet",
                    "-i", videoPath,
                    "-ss", str(int(frameSplit[0])/fps),
                    "-t", str((int(frameSplit[1])-int(frameSplit[0])+1)/fps),
                    "tempVideoFolder/video" + frameSplit[0] + ".mp4"
            ]
            subRun(cmd)

            # client.assets.upload("d1b75dc2-08c1-4b2f-9316-f66ac5d51d29", "tempVideoFolder/video" + frameSplit[0] + ".mp4")
            
            if(xlsFlag):
                startTimecode = framesToTime(int(frameSplit[0]))
                endTimecode = framesToTime(int(frameSplit[1]))
                worksheet.write("A" + str(excelLocation), locations['/'.join(row["Location"].split('/')[2:])])
                worksheet.write("B" + str(excelLocation), row["Frame"])
                worksheet.write("C" + str(excelLocation), startTimecode + '-' + endTimecode)

                midFrame = (int(frameSplit[0]) + int(frameSplit[1]))//2


                cmd = [
                        "ffmpeg",
                        "-v", "quiet",
                        "-i", videoPath,
                        "-ss", str(midFrame/25),
                        "-frames:v", "1",
                        "-s", "96x74",
                        "tempThumbnailFolder/tempImage" + str(excelLocation) + ".png"
                ]
                subRun(cmd)
                    
                worksheet.insert_image("D" + str(excelLocation),"tempThumbnailFolder/tempImage" + str(excelLocation) + ".png")

                excelLocation += 1
        elif(csvFlag):
            finalCSV.append([locations['/'.join(row["Location"].split('/')[2:])], row["Frame"]])


    #################################################
    # Turn on after upload to delete temp files
    # rmtree("tempVideoFolder", ignore_errors=True)
    #################################################


    if(xlsFlag):
        writer.close()
        # delete temp folder
        rmtree("tempThumbnailFolder", ignore_errors=True)

    if(csvFlag):
        finalCSV[3].pop()
        finalCSV[3].pop()
        finalCSV[3][1]= "Frames to fix"

        outputFile = open("excluded.csv", "w")
        outputWriter = csvWriter(outputFile)
        outputWriter.writerows(finalCSV)





parser = ArgumentParser(prog = "The Crucible", 
                        description="Enhancement of a prior project (Project 1) with a focus on integrating workflows for VP (Virtual Production), Gaming, and VFX.")

parser.add_argument('--baselight', 
                    type=str,
                    help= "Location of the baselight file to import into databse")
parser.add_argument('--xytech',
                    type=str,
                    help= "Location of the xytech file to import into databse")
parser.add_argument('--process',
                    type=str,
                    help= "Video file to process")
parser.add_argument('-xls', '--outputXLS',
                    action='store_true',
                    help= "Outputs XLS of all ranges that fall into video")
parser.add_argument('-csv', '--outputCSV',
                    action='store_true',
                    help= "Outputs CSV of all frame/ranges that dont fall into video")


args = parser.parse_args()

if(args.baselight):
    importBaselight(args.baselight)
if(args.xytech):
    importXytech(args.xytech)
if(args.process):
    xlsFlag = args.outputXLS
    csvFlag = args.outputCSV
    startProcess(args.process)







##############Might be important later
# locations[str(lineCont[0][20:])] = lineCont[0]
# current = locations[cell[21:]]