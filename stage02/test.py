import json
from urllib import request, parse
import ssl
import requests

f = open("data_uuids.json")
JSONFILE_OBJECT = json.load(f)

f.close()

print(JSONFILE_OBJECT["en_974958287c8d12c2ef98e331234d34ba"]["full_name"])