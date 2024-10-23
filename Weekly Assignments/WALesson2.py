file = open("ingest_this.txt", "r")

text = file.read()

vowels = {'a', 'e', 'i', 'o', 'u'}

count = 0
newText = ""

for let in text:
    if(let.isalpha() and not vowels.__contains__(let.lower())):
        newText += "2"
        count+=1
    else:
        newText += let

print(newText)
print(count)


"""
22i2 2222o2 222i22​
I2 2o222e2e22 a2a2i22​
2i2e 22o2e22o2 22a2a​
36
"""