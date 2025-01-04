# Marks Automation

## Overview
Automation script in Python that automates 4 manual positions in seconds. Python code reads proprietary data from Baselight machines to calculate the filesystem locations of frames. All requests are saved to a database and can be used for data analysis and worker efficiency. Exports are basic CSV files to XLS files with timecode and thumbnail preview uploaded to Frame.IO

## Instruction
1. Reuse Proj 1​
2. Add argparse
3. Populate new database with 2 collections: One for Baselight (Location/Frames) and Xytech (Workorder/Location) 
4. Download Demo ​
5. Run script with argparse command --process <video file>  ​
6. From (5) Call the populated database from (3), find all ranges only that fall in the length of video from (4)
7. Using ffmpeg, to extract timecode from video and write your own timecode method to convert marks to timecode​
8. New argparse--outputXLS parameter for XLS with flag from (5) should export same CSV export as proj 1 (matching xytech/baselight locations), but in XLS with new column from files found from (6) and export their timecode ranges as well​
9. Create Thumbnail (96x74) from each entry in (6), but middle most frame or closest to. Add to XLS file to it's corresponding range in new column ​
10. Render out each shot from (6) using (7) and manually upload them to frame.io
11. Create CSV file (using --outputCSV) and show all ranges/individual frames that were not uploaded from  (10) (so show location and frame/ranges)

## FrameIO Upload 
<img width="1378" alt="Screenshot 2024-12-04 at 7 40 56 PM" src="https://github.com/user-attachments/assets/5d878a28-7e9f-49f6-a346-b3a0740812f8" />
