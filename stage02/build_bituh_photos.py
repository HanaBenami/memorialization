
from PIL import Image, ImageFont, ImageDraw, ImageOps
font_type_1 = ImageFont.truetype("Rubik-Regular.ttf", 47, layout_engine=ImageFont.Layout.RAQM)
font_type_1_sm = ImageFont.truetype("Rubik-Regular.ttf", 40, layout_engine=ImageFont.Layout.RAQM)
font_type_2 = ImageFont.truetype("Rubik-Regular.ttf", 54, layout_engine=ImageFont.Layout.RAQM)
font_type_2_sm = ImageFont.truetype("Rubik-Regular.ttf", 49, layout_engine=ImageFont.Layout.RAQM)
font_type_3 = ImageFont.truetype("Rubik-Regular.ttf", 32, layout_engine=ImageFont.Layout.RAQM)

import json
import urllib.request
import multiprocessing

import textwrap
import ssl
import os
import re
import datetime

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

from selenium.webdriver.common.by import By  
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ssl._create_default_https_context = ssl._create_unverified_context

_id = "en_974958287c8d12c2ef98e331234d34ba"
 
def get_side_details(uuid):
    url = "https://www.izkor.gov.il/r/" + uuid 
    options = webdriver.ChromeOptions() 
    options.headless = True 
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver: 
        driver.get(url)
        WebDriverWait(driver, timeout=3).until(EC.text_to_be_present_in_element((By.XPATH,"//div[@class='fellon-desc']"), 'מ'))
        
        elements = driver.find_element(By.XPATH, "//div[@class='fellon-desc']") 
        return elements.text

def get_object_by_uuid(uuid):
    f = open("data.json")
    data = json.load(f)

    return list(filter(lambda x: x["uuid"] == _id,data["fallenSearch"]["data"]))[0]

def get_more_details(uuid):

    url = "https://www.izkor.gov.il/search/memory/presentation/" + uuid
    r = urllib.request.urlopen(url)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    return data["data"]

def normalize_legacy_id(legacy_id):
    if len(str(legacy_id)) < 6:
        zeros_to_add = 6 - len(str(legacy_id))
        zeros = ""
        for i in range(zeros_to_add):
            zeros += "0"
        legacy_id = zeros + str(legacy_id)
        return legacy_id
    return legacy_id
    
def download_person_image(imgsrc,name):
    print("Downloading image for name: " + name)
    urllib.request.urlretrieve(
    f"""{imgsrc}""",
    f"""{name}.jpg""")
    if "nopic" in imgsrc:
        return Image.open(f"""{name}.jpg""")
    
    return ImageOps.grayscale(Image.open(f"""{name}.jpg"""))

def create_image(obj):
    folder_name = '_'.join(obj["full_name"].split(" ")[:2])
    gender = 'נ'
    if 'בן' in obj["about"] or 'בן' in obj["full_name"] or 'נהרג' in obj["about"]: 
        gender = 'ז'
    
    baseimage = "female.png"
    if gender == "ז":
        baseimage = "male.png"
    print("Choosed baseimage: " + baseimage)
    
    obj["about"] = obj["about"].replace("\nלהרחבה",'')
    print(obj["about"])
    temp = obj["about"].splitlines()
    side_details = []
    for item in temp:
        wrapped = textwrap.wrap(item, width=41)
        side_details = side_details + wrapped
        
    #The regex pattern that we created
    # pattern = "[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}"

    # #Will return all the strings that are matched
    # dates = re.findall(pattern, obj["about"])
    
    # found_date = ""
    # print(f"""dates: {dates}""")
    # for date in dates:
    #     if "-" in date:
    #         day, month, year = map(int, date.split("-"))
    #     else:
    #         day, month, year = map(int, date.split("/"))
    #     if 1 <= day <= 31 and 1 <= month <= 12:
    #         print(date)
    #         found_date = date
        
    # print(f"""found_date: {found_date}""")
    # print(side_details)
    
    # found_year = ""
    # if found_date != "":
    #     found_year = found_date.split('/')[2]
        
    with Image.open(baseimage) as image: 

        width, height = image.size 
        
        person = download_person_image(obj["img_src"], folder_name)
        
        width, height = person.size  
        
        correct_width = 300
        ratio = height / width
        person = person.resize((correct_width, int(correct_width * ratio))) 
        image.paste(person, (670, 140))   
        
        draw = ImageDraw.Draw(image)
        
            
        name_text = obj["full_name"].splitlines()[0]
        _width, _height = font_type_2.getsize(name_text)
        f = font_type_2
        if _width >= 550:
            _width, _height = font_type_2_sm.getsize(name_text)
            f = font_type_2_sm
        draw.text((630 - _width, 150),name_text,(255,255,255),direction='rtl',align='right',features='rtla',font=f,stroke_width=1,stroke_fill="white")
        
        # gender_prefix = "בן" if obj["gender"] == "ז" else "בת"
        
        # if obj["mother_name"] or obj["father_name"]:
        #     if obj["mother_name"] != None and obj["mother_name"] == None:
        #         parents_text = f"""{gender_prefix} {obj["mother_name"]}"""
        #     elif obj["mother_name"] == None and obj["mother_name"] != None:
        #         parents_text = f"""{gender_prefix} {obj["father_name"]}"""
        #     else:
        #         parents_text = f"""{gender_prefix} {obj["mother_name"]} ו{obj["father_name"]}"""
        
        offset = "75"
        if len(obj["full_name"].splitlines()) >= 2:
            parents_text = obj["full_name"].splitlines()[1]
            _width, _height = font_type_1.getsize(parents_text)
            f2 = font_type_1
            if _width >= 550:
                _width, _height = font_type_2_sm.getsize(name_text)
                f2 = font_type_1_sm
            draw.text((630 - _width, 215),parents_text,(255,255,255),font=f2)
            offset = 0
        
        
        line1_text = side_details[0]
        _width, _height = font_type_3.getsize(line1_text)
        draw.text((630 - _width, 290-offset),line1_text,(255,255,255),font=font_type_3)
        
        if len(side_details) >= 2:
            line2_text = side_details[1]
            _width, _height = font_type_3.getsize(line2_text)
            draw.text((630 - _width, 330-offset),line2_text,(255,255,255),font=font_type_3)
            
            if len(side_details) >= 3:
                line3_text = side_details[2]
                _width, _height = font_type_3.getsize(line3_text)
                draw.text((630 - _width, 370-offset),line3_text,(255,255,255),font=font_type_3)
                
                if len(side_details) >= 4:
                    line4_text = side_details[3]
                    _width, _height = font_type_3.getsize(line4_text)
                    draw.text((630 - _width, 410-offset),line4_text,(255,255,255),font=font_type_3)
                    
                    if len(side_details) >= 5:
                        line5_text = side_details[4]
                        _width, _height = font_type_3.getsize(line5_text)
                        draw.text((630 - _width, 450-offset),line5_text,(255,255,255),font=font_type_3)
                
        
        rgb_im = image.convert('RGB')
        
        
        if not os.path.isdir("results/bituh/" + str(obj["year"])):
            os.makedirs("results/bituh/" + str(obj["year"]))   
        
        rgb_im.save('results/bituh/' + str(obj["year"]) + "/" + folder_name+"_"+str(obj["year"])+'.jpg')
        
        os.remove(f"""{folder_name}.jpg""")

            
def proccess(item):
    #folder_name = ''.join(item["full_name"].split(" ")[:2])
    # print(folder_name)
    # if not os.path.isdir("results/bituh/" + folder_name):
    #     os.makedirs("results/bituh/" + folder_name)     
        
    try:
        create_image(item)
    except Exception as e:
        print(str(e))
    
    
        
def main():
    f = open("bituh_data.json")
    data = json.load(f)
    f.close()
    DATA = data["DATA"]
    
    # for item in DATA:
        
        # if not os.path.isdir("results/bituh/" + item["full_name"].replace(" ", '')):
        #     os.makedirs("results/bituh" + item["full_name"].replace(" ", ''))
            
        # counter = 0
        # print(data_for_year)
        # for item in data_for_year:
        #     uuid = item["uuid"]
        #     print(uuid)
        #     if not os.path.isdir("results/" + year + "/" + uuid):
        #         os.makedirs("results/" + year + "/" + uuid)
                
        #         obj_detailed = get_more_details(uuid)
        #         print(obj_detailed)
        #         create_image(obj_detailed)
        #     else:
        #         counter = counter + 1
        #         print("slredy creted: " + uuid)
                
    pool_obj = multiprocessing.Pool()
    pool_obj.map(proccess,DATA)
    pool_obj.close()

            
    
if __name__ == "__main__":
    main()

