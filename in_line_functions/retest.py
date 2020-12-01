import re


a = re.sub("[0-9][A-Z]{2}[\s,.\-_]", ' ', "2ND_ 3PT , S/BELT")
b = re.sub("(NO)(\.)[0-9]+", ' ', "NO.113")

print(a)
print(b)