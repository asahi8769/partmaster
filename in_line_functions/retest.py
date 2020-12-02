import re

i = "RING ASSY-TRIPLE CONE(1ST_O2 Cooler)"

name = re.sub(
    "(NO)(\.)[0-9]+|[0-9][A-Z]{2}($|[\s,.\-_)])|[0-9\xa0\u3000\n?!\-+_,()=]", ' ', re.sub("(O2)", 'OXYGEN', i))


print(name)

a = "1 31  2"
print(a.split(" "))