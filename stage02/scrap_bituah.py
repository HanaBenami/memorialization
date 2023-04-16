from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

from selenium.webdriver.common.by import By  
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os
import json
import re
import time

url = "https://laad.btl.gov.il/Web/He/TerrorVictims/Default.aspx" 
 

options = webdriver.ChromeOptions() 
options.headless = False 

DATA = {"DATA":[]}

with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver: 
    driver.get(url)
    
    for i in range(212): # 5 pages
    
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nofel-article"))
        )
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rdpPageNext"))
        )
        
        articles = driver.find_elements(By.CLASS_NAME, "nofel-article")
        
        
        for item in articles:
            #print(item.get_attribute('innerHTML'))
            title = item.find_element(By.XPATH, ".//h3[@class='title']").get_attribute('innerText')
            about = item.find_element(By.XPATH, ".//section[@class='about']").get_attribute('innerText')
            img_src = item.find_element(By.XPATH, ".//img").get_attribute('src')
            about = os.linesep.join(
                [
                    line for line in about.splitlines()
                    if line
                ]
            )
            print(title)
            print(about)
            print(img_src)
            
            pattern = "[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}"

            #Will return all the strings that are matched
            dates = re.findall(pattern, about)
            
            found_date = ""
            for date in dates:
                if "-" in date:
                    day, month, year = map(int, date.split("-"))
                else:
                    day, month, year = map(int, date.split("/"))
                if 1 <= day <= 31 and 1 <= month <= 12:
                    print(date)
                    found_date = date
            
            found_year = ""
            if found_date != "":
                found_year = found_date.split('/')[2]
            
            DATA["DATA"].append({
                "full_name": title,
                "about": about,
                "date": found_date,
                "year": found_year,
                "img_src": img_src
            })
            
            jsonFile = open("bituh_data.json", "w+")
            jsonFile.write(json.dumps(DATA))
            jsonFile.close()
            
        #t = driver.find_elements(By.CLASS_NAME, "ps-scrollbar-y-rail")
        nextBtn = driver.find_element(By.XPATH, "//input[@class='rdpPageNext']")
        #driver.execute_script("document.querySelector('.ps-scrollbar-y-rail').style.top = '5500px';")

        #nextBtn = driver.find_element(By.XPATH, "//input[@class='rdpPageNext']")
        time.sleep(1)
        #driver.execute_script("document.querySelector('div.layout-innerpage').scrollTo(0, 9999);")
        
        #actions = ActionChains(driver)
    # actions.move_to_element(nextBtn).perform()
        
        
        driver.execute_script("arguments[0].scrollIntoView();", nextBtn)        
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@class='rdpPageNext']"))).click()


