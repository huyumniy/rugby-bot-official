import re

text = 'CATEGORY 1 - STANDING'
print(re.compile('\d').findall(text)[-1])