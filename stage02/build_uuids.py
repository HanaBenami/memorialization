import json
from urllib import request, parse
import ssl
import requests

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ssl._create_default_https_context = ssl._create_unverified_context

f = open("uuids.json")
JSONFILE_OBJECT = json.load(f)
uuids = JSONFILE_OBJECT["uuids"]
f.close()


DATA = {}

counter = 0

for i in uuids:
    url = 'https://www.izkor.gov.il/search/memory/presentation/' + i

    x = requests.get(url)

    temp_data = x.json()["data"]
    
    DATA[i] = {
        "uuid": i,
        "full_name": temp_data["full_name"],
        "age": temp_data["age"],
        "has_image": temp_data["has_image"],
        "death_date_year": temp_data["death_date_year"]
    }
    print(f""" {counter} / {len(uuids)} """)
    counter = counter + 1

jsonFile = open("data_uuids.json", "w+")
jsonFile.write(json.dumps(DATA))
jsonFile.close()
