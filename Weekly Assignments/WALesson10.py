import subprocess
import shlex

command = 'ls -l /Users/tiko/Python_Code'

process = subprocess.Popen(
    shlex.split(command),
    stdout = subprocess.PIPE,

    stderr = subprocess.STDOUT,  # Redirect STDERR to STDOUT, conjoining the two streams​
)

for line in iter(process.stdout.readline, ''):
    print(line)