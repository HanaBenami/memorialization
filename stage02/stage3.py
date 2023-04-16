from instabot import Bot
import time
import os
from pathlib import Path
import json
import urllib
import ssl
import traceback


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ssl._create_default_https_context = ssl._create_unverified_context

f = open("data_uuids.json")
DATA_UUIDS_OBJECT = json.load(f)
f.close()
f = open("bituh_data.json")
DATA_BITUH_OBJECT = json.load(f)["DATA"]
f.close()

def get_more_details(uuid):

    url = "https://www.izkor.gov.il/search/memory/presentation/" + uuid
    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    return data["data"]

bot=Bot()
bot.login(username="israelisraeli6558",password="Aa123456")
time.sleep(0.2)

years = range(1800,2023)

for year in years:
    
    try:
        if os.path.isdir("results/" + str(year)):
            results = os.listdir("results/" + str(year) + "/")
            
            for item in results:
                if os.path.isdir("results/" + str(year) + "/" + str(item)):
                    
                    photo = Path("results/" + str(year) + "/" + str(item) + "/" + str(item) + ".jpg")
                    if photo.exists():
                        print(photo)
                        if item in DATA_UUIDS_OBJECT:
                            
                            obj = get_more_details(item)
                            
                            full_name = DATA_UUIDS_OBJECT[item]["full_name"]
                            hebrew_date = obj["death_date_hebrew"]
                            date = obj["death_date"].replace("-",".")
                            link = f"""https://www.izkor.gov.il/-/{item}"""
                            caption = f"""
                            {full_name} ז״ל, נפל ביום {hebrew_date} ({date})
                            
                            #{full_name.replace(" ", '')} #לזכרם #יוםהזיכרון #יוםהזיכרון2023 #חללזכרונות #יוםהזכרוןהתשפג
                            """
                            
                            print(caption)
                            bot.upload_photo(photo,caption=caption)
                            time.sleep(0.5)
    except Exception as e:
        print(str(e))
        traceback.print_exc()
    
    try:
        if os.path.isdir("results/bituh/" + str(year)):
            print("bituh: " + str(year))
            bituh_results = list(filter(lambda x: '.jpg' in x, os.listdir("results/bituh/" + str(year) + "/")))
        
            for item in bituh_results:
                photo = Path("results/bituh/" + str(year) + "/" + item)
                if photo.exists():
                    print(photo)
                    temp = item.split("_")
                    name = temp[0] + " " + temp[1]
                    
                    try:
                        obj = list(filter(lambda x: name in x["full_name"] and str(year) == str(x["year"]) ,DATA_BITUH_OBJECT))[0]
                    except:
                        print("not found object for: " + name + " " + year)
                        
                    full_name = obj["full_name"]
                    try:
                        #shortname = obj["full_name"].split("")[0].replace(" ", '')[:-1]
                        shortname = name.replace(" ", '')
                    except:
                        shortname = full_name
                    date = obj["year"]
                    #link = f"""https://www.izkor.gov.il/-/{item}"""
                    caption = f"""
                    {full_name}, נפל בתאריך {date}
                    
                    #{shortname} #לזכרם #יוםהזיכרון #יוםהזיכרון2023 #חללזכרונות #יוםהזכרוןהתשפג
                    """
                    
                    print(caption)
                    bot.upload_photo(photo,caption=caption)
                    time.sleep(0.5)
    except Exception as e:
        traceback.print_exc()