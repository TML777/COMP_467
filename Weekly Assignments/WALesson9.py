import subprocess

cmd = [
    "ffmpeg",
    "-i", "input.mp4",
    "-ss", "00:00:11.8",
    "-frames:v", "1",
    "image.png"
]
subprocess.run(cmd)


cmd = [
    "ffmpeg",
    "-i", "input.mp4",
    "-ss", "00:00:5",
    "-t", "15",
    "output1.mp4"
]
subprocess.run(cmd)

cmd = [
    "ffmpeg",
    "-i", "input.mp4",
    "-filter:v", "crop=500:500:50:50",
    "output2.mp4"
]

subprocess.run(cmd)