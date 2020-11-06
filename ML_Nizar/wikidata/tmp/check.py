import re

file = open('wikidatamapping-nonENNL.txt', "r", encoding="utf-8")
lines = file.readlines()
i = 0
for line in lines:
    i = i + 1
    line = re.sub(r'^.*?:', '', line)
    if not line.strip():
        print(line)
        print(i)