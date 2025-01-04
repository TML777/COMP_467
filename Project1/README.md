# Import/Export Script

## Overview
This script facilitates the parsing, computation, and export of data between Baselight and Xytech work orders, transitioning file storage from local Baselight systems to facility storage. It handles errors in third-party data and ensures accurate processing of frame ranges and locations.

## Instruction
* Import file created from baselight (Baselight_export_fall2024.txt)​
* Import xytech work order (Xytech_fall2024.txt)​
* Script parses data ​
* Computation done to match shareholder request, to replace file system from local baselight to facility storage (remember color correcter's prefer local storage for bandwidth issues)​
* Dealing with 3rd party data, so some errors in the data might occur, deal with it
* Export CSV file ('/' indicates columns): ​
  * Line 1: Producer / Operator / job /notes​
  * Line 4: show location / frames to fix​
* Frames and frame ranges processed in consecutive/numerical order shown (from baselight_export_fall2024.txt) as either:
  * ranges (i.e /filesystem/Deadpool3/PartA/1920x1080  32-35) 
  * individually (i.e  /filesystem/Deadpool3/PartA/1920x1080   41)​
* Frames shown need to reflect their proper location and not mix with ranges from another location
