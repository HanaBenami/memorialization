
from PIL import Image, ImageFont, ImageDraw
font_type_1 = ImageFont.truetype("Rubik-Regular.ttf", 47, layout_engine=ImageFont.Layout.RAQM)
font_type_2 = ImageFont.truetype("Rubik-Regular.ttf", 58, layout_engine=ImageFont.Layout.RAQM)
font_type_3 = ImageFont.truetype("Rubik-Regular.ttf", 32, layout_engine=ImageFont.Layout.RAQM)

import json
import urllib.request
import multiprocessing

import textwrap
import ssl
import os

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
    
def download_person_image(legacy_id):
    
    legacy_id = normalize_legacy_id(legacy_id)
    
    print("Downloading image for legacy_id: " + legacy_id)
    urllib.request.urlretrieve(
    f"""https://izkorcdn.azureedge.net/Data/korot/Image/{legacy_id}.jpg""",
    f"""{legacy_id}.jpg""")
    
    return Image.open(f"""{legacy_id}.jpg""")

def create_image(obj):
    gender = obj["gender"]
    
    baseimage = "female.png"
    if gender == "ז":
        baseimage = "male.png"
    print("Choosed baseimage: " + baseimage)
    
    temp = get_side_details(obj["uuid"]).splitlines()
    side_details = []
    for item in temp:
        wrapped = textwrap.wrap(item, width=41)
        side_details = side_details + wrapped
        
    print(side_details)
    
    with Image.open(baseimage) as image: 

        width, height = image.size 
        
        if obj["has_image"]:
            person = download_person_image(obj["legacy_id"])
        else:
            print("No image, choosed default..")
            person = Image.open("no_image_default.jpeg")    
        
        width, height = person.size  
        
        correct_width = 300
        ratio = height / width
        person = person.resize((correct_width, int(correct_width * ratio))) 
        image.paste(person, (670, 140))   
        
        draw = ImageDraw.Draw(image)
        
        if obj["rank"] != None:
            rank_text = obj["rank"]
            _width, _height = font_type_1.getsize(rank_text)
            draw.text((630 - _width, 150),rank_text,(255,255,255),font=font_type_1)
            
        name_text = obj["full_name"]
        _width, _height = font_type_2.getsize(name_text)
        draw.text((630 - _width, 214),name_text,(255,255,255),direction='rtl',align='right',features='rtla',font=font_type_2,stroke_width=1,stroke_fill="white")
        
        gender_prefix = "בן" if obj["gender"] == "ז" else "בת"
        
        if obj["mother_name"] or obj["father_name"]:
            if obj["mother_name"] != None and obj["mother_name"] == None:
                parents_text = f"""{gender_prefix} {obj["mother_name"]}"""
            elif obj["mother_name"] == None and obj["mother_name"] != None:
                parents_text = f"""{gender_prefix} {obj["father_name"]}"""
            else:
                parents_text = f"""{gender_prefix} {obj["mother_name"]} ו{obj["father_name"]}"""
        
            _width, _height = font_type_1.getsize(parents_text)
            draw.text((630 - _width, 290),parents_text,(255,255,255),font=font_type_1)
        
        line1_text = side_details[0]
        _width, _height = font_type_3.getsize(line1_text)
        draw.text((630 - _width, 350),line1_text,(255,255,255),font=font_type_3)
        
        if len(side_details) >= 2:
            line2_text = side_details[1]
            _width, _height = font_type_3.getsize(line2_text)
            draw.text((630 - _width, 390),line2_text,(255,255,255),font=font_type_3)
            
            if len(side_details) >= 3:
                line3_text = side_details[2]
                _width, _height = font_type_3.getsize(line3_text)
                draw.text((630 - _width, 430),line3_text,(255,255,255),font=font_type_3)
                
                if len(side_details) >= 4:
                    line4_text = side_details[3]
                    _width, _height = font_type_3.getsize(line4_text)
                    draw.text((630 - _width, 470),line4_text,(255,255,255),font=font_type_3)
                    
                    if len(side_details) >= 5:
                        line5_text = side_details[4]
                        _width, _height = font_type_3.getsize(line5_text)
                        draw.text((630 - _width, 510),line5_text,(255,255,255),font=font_type_3)
                
        
        rgb_im = image.convert('RGB')
        rgb_im.save('results/' + str(obj["death_date_year"]) + "/" + obj["uuid"] + '/' + obj["uuid"] + '.jpg')
        
        if obj["has_image"]:
            legacy_id = normalize_legacy_id(obj["legacy_id"])
            os.remove(f"""{legacy_id}.jpg""")

            
def proccess(item):
    uuid = item["uuid"]
    year = str(item["death_date_year"])
    if not os.path.isdir("results/" + year + "/" + uuid):
        os.makedirs("results/" + year + "/" + uuid)
        
        try:
            print(uuid)
            obj_detailed = get_more_details(uuid)
            #print(obj_detailed)
            create_image(obj_detailed)
        except Exception as e:
            print(str(e))
    
    
        
def main():
    #obj = get_object_by_uuid(_id)
    
    # obj_detailed = get_more_details(_id)
    # print(obj_detailed)
    # create_image(obj_detailed)
    
    #years = [2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013]
    years = list(range(2018,1930,-1))
    print(years)
    f = open("data_uuids.json")
    data = json.load(f)
    f.close()
    
    for year in years:
        year = str(year)
        data_for_year = []
        for item in data:
            if data[item]["death_date_year"] == int(year):
                data_for_year.append(data[item])
        
        if not os.path.isdir("results/" + year):
            os.makedirs("results/" + year)
            
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
        pool_obj.map(proccess,data_for_year)
        pool_obj.close()

            
    
if __name__ == "__main__":
    main()

