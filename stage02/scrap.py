from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 

from selenium.webdriver.common.by import By  
url = "https://www.izkor.gov.il/r/en_63feefc57f27ae4c22b4cffefa5b508a" 
 

options = webdriver.ChromeOptions() 
options.headless = True 
with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver: 
	driver.get(url)
 
 
	print("Page URL:", driver.current_url) 
	print("Page Title:", driver.title)
 
 
	elements = driver.find_element(By.XPATH, "//div[@class='fellon-desc']") 
	print(elements.text)

