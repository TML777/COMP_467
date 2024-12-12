import subprocess
import shlex

command = 'ls -l /Users/tiko/Python_Code'

process = subprocess.Popen(
    shlex.split(command),
    stdout = subprocess.PIPE,

    stderr = subprocess.STDOUT,  # Redirect STDERR to STDOUT, conjoining the two streams​
)

largest = []

for line in iter(process.stdout.readline, b''):
    tempLine = line.decode().split()
    
    if(largest == [] and len(tempLine) > 2):
        largest = tempLine
    elif(len(tempLine) > 2 and int(largest[4])<int(tempLine[4])):
        largest = tempLine


if(len(largest)> 2):
    print(f"Largest file is {largest[8]} and its size is {largest[4]} bytes.")
else:
    print("No files in folder.")


"""
Largest file is input.txt and its size is 15399 bytes.
"""