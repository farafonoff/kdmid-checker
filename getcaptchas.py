# vocr is built from https://github.com/srirangav/vocr

import time
import subprocess
import os
import requests
import shutil
import traceback
import uuid

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
options = Options()
# options.headless = True
options.add_argument("--headless=new")
#options.add_argument("--proxy-server=socks4://212.26.225.114:80")

try:
    baseurl=os.environ['MID_URL']
except:
    baseurl="https://trabzon.kdmid.ru/queue/OrderInfo.aspx"


id=os.environ["MID_ID"]
cd=os.environ["MID_CODE"]

driver = webdriver.Chrome(options=options)

def initDriver():
    url=f'{baseurl}?id={id}&cd={cd}'
    print("Opening url " + url)
    driver.get(url)
    time.sleep(10)

ctmp = f"{uuid.uuid4()}.png"

def checkSlots(id, cd):
    # initializing webdriver for Chrome

    #nzElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtID"]')
    #codElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtUniqueID"]')

    captchaSolved = False

    while not captchaSolved:
        with open(ctmp, 'wb') as file:
            file.write(driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]').screenshot_as_png)

        print("Solving captcha")

        result = subprocess.check_output(['./vocr', ctmp])

        captcha = result.decode('ascii')
        print("my solution " + captcha)
        captchaSolution = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtCode"]')
        captchaSolution.clear()
        captchaSolved = True
        captchaSolution.send_keys(captcha)
        time.sleep(1)
        #captchaSolution.submit()
        submitElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonA"]')
        submitElement.click()
        time.sleep(1)        
        try:
            captchaErrorElements = driver.find_elements(By.XPATH, '//*[@id="ctl00_MainContent_lblCodeErr"]')
            if len(captchaErrorElements) and captchaErrorElements[0].text.find("Символы с картинки") != -1:
                captchaSolved = False
        except NoSuchElementException:
            captchaSolved = True
    
    if (captchaSolved):
        print(f"solution {captcha} correct")
        shutil.move(ctmp, f"captcha_images/{captcha}.png")
    else:
        print(f"solution {captcha} incorrect")
        shutil.rmtree(ctmp)

    return captchaSolved

initDriver()
for i in range(500):
    try:
        success = checkSlots(id, cd)
        if success:
            driver.back()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        driver.close()
        driver = webdriver.Chrome(options=options)
        initDriver()

driver.close()