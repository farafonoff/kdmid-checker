# vocr is built from https://github.com/srirangav/vocr

import time
import subprocess
import os
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True

try:
    baseurl=os.environ['MID_URL']
except:
    baseurl="https://trabzon.kdmid.ru/queue/OrderInfo.aspx"


botkey=os.environ["MID_BOTKEY"]
mychannel=os.environ["MID_CHANNEL"]
id=os.environ["MID_ID"]
cd=os.environ["MID_CODE"]


def send_photo(TOKEN, chat_id, image_path, image_caption=""):
    data = {"chat_id": chat_id, "caption": image_caption}
    url = "https://api.telegram.org/bot%s/sendPhoto" % TOKEN
    with open(image_path, "rb") as image_file:
        ret = requests.post(url, data=data, files={"photo": image_file})

def checkSlots(id, cd):
    # initializing webdriver for Chrome
    driver = webdriver.Chrome(options=options)

    badStr="нет свободного времени"
    badStr2="Свободное время в системе записи отсутствует"
    url=f'{baseurl}?id={id}&cd={cd}'
    print("Opening url " + url)
    driver.get(url)
    
    time.sleep(5)

    #nzElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtID"]')
    #codElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtUniqueID"]')


    with open('captcha.jpg', 'wb') as file:
        file.write(driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]').screenshot_as_png)

    print("Solving captcha")

    result = subprocess.check_output(['./vocr', 'captcha.jpg'])

    captcha = result.decode('ascii')
    print("my solution " + captcha)
    captchaSolution = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtCode"]')
    captchaSolution.clear()
    captchaSolution.send_keys(captcha)
    time.sleep(1)
    #captchaSolution.submit()
    submitElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonA"]')
    submitElement.click()
    time.sleep(1)
    signInElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonB"]')
    signInElement.click()
    time.sleep(1)

    pElements = driver.find_elements(By.TAG_NAME, 'p')
    noSlots=False
    for element in pElements:
        # print(element.text)
        text = element.text
        if text.find(badStr) != -1:
            noSlots=True
        if text.find(badStr2) != -1:
            noSlots=True            
#    if noSlots:
#        driver.save_screenshot("fail.png")
#    else:
#        driver.save_screenshot("success.png")
    print("Has no slots" if noSlots else "Found slots")
    driver.save_screenshot("screenshot.png")
    hasSlots = not noSlots
    try:
        radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
        print(len(radios))
        if (len(radios) > 0): 
            radios[0].click()
        
        driver.save_screenshot("screenshot1.png")
        time.sleep(1)
        send_photo(botkey, mychannel, "./screenshot1.png", f'{id} Clicked radiobutton')
        # allInputs = driver.find_elements(By.TAG_NAME, "input")
        mainButton = driver.find_element(By.ID, "ctl00_MainContent_Button1")
        mainButton.click()
        driver.save_screenshot("screenshot2.png")
        time.sleep(1)
        send_photo(botkey, mychannel, "./screenshot2.png", f'{id} Clicked main button')

        """for input in allInputs:
            print(input)
            print(input.get_attribute("id"))
            print(input.get_attribute("name")) """
    except:
        print("Registration process failed")
    driver.close()
    return hasSlots
    # closing browser

for i in range(20):
    try:
        success = checkSlots(id, cd)
        break;
    except:
        print("error happened, retry")

send_photo(botkey, mychannel, "./screenshot.png", f'Has slots!!! {id}' if success else f'No slots {id}')