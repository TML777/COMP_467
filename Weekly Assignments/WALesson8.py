def framesToTime(totalFrames, fps):
    returnString = f":{totalFrames%fps:02}"

    time = totalFrames // fps

    returnString = f":{time%60:02}" + returnString

    time = time // 60

    returnString = f":{time%60:02}" + returnString

    time = time // 60

    return f"{time:02}" + returnString




fps = 24

totalFrames = 35
print(f"{totalFrames} -> {framesToTime(totalFrames, fps)}")

totalFrames = 1569
print(f"{totalFrames} -> {framesToTime(totalFrames, fps)}")

totalFrames = 14000
print(f"{totalFrames} -> {framesToTime(totalFrames, fps)}")


"""
35 -> 00:00:01:11
1569 -> 00:01:05:09
14000 -> 00:09:43:08
"""