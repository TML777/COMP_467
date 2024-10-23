import os
import time
import datetime



while(True):
    folder = os.listdir("lesson3")
    
    if(len(folder)>0):
        break

    time.sleep(1)



print("File found!")
print("File type: ", os.path.splitext(folder[0])[1])
print("Time: ", datetime.datetime.now())

"""
File found!
File type:  .txt
Time:  2024-09-28 18:52:56.370076
"""




