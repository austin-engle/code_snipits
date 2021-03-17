"""
This script will scrub the data in the json file to be clean when putting into GitHub
"""

import json
import string
import random


digits = string.digits

with open('data.json', 'r') as file:
    data = json.load(file)

for item in data:
    randomDigits = ''.join(random.choice(digits) for i in range(5))

    item['name'] = f'RandomName-{randomDigits}'
    item['Networks'] = f'RandomNetwork-{randomDigits}'


with open('data.json', 'w') as outfile:
    json.dump(data, outfile)


