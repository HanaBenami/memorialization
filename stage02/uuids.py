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

arr = [1938, 1943, 1948, 1949, 1956, 1967, 1968, 1969, 1970, 1971, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1987, 1988, 1989, 1990, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 2000, 2001, 2002, 2003, 2006]

for i in arr:

    url = 'https://www.izkor.gov.il/search/extended'
    myobj = {
        "death_date":i,
        "death_date_to":i,
        "full_name":"ח"
    }

    x = requests.post(url, json = myobj)

    temp_data = x.json()["fallenSearch"]["data"]

    request_uuids = list(map(lambda x: x["uuid"] ,temp_data))

    resulting_list = list(request_uuids)
    resulting_list.extend(x for x in JSONFILE_OBJECT["uuids"] if x not in request_uuids)

    print("requested uuids: " + str(len(request_uuids)))
    print("finnaly: " + str(len(resulting_list)))
    
    if len(request_uuids) == 200:
        arr.append(i)

    JSONFILE_OBJECT["uuids"] = resulting_list

jsonFile = open("uuids.json", "w+")
jsonFile.write(json.dumps(JSONFILE_OBJECT))
jsonFile.close()

print(arr)
