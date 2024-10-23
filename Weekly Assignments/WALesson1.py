import random


randomArray = []
for _ in range(25):
    randomArray.append(random.randint(0, 10000))

maxInArray = max(randomArray) 


print(randomArray)
print("Array Max: ", maxInArray)


"""
[7256, 9211, 3422, 7836, 4074, 8209, 9591, 1098, 7455, 5515, 9497, 8825, 820, 669, 361, 1183, 155, 8562, 8596, 8681, 517, 7571, 6576, 4562, 8162]
Array Max:  9591
"""
