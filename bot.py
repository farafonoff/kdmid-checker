# vocr is built from https://github.com/srirangav/vocr

import time
import subprocess
import os
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By

def checkSlots(id, cd):
    # initializing webdriver for Chrome
    driver = webdriver.Chrome()

    badStr="нет свободного времени"


    driver.get(f'https://trabzon.kdmid.ru/queue/OrderInfo.aspx?id={id}&cd={cd}')
    
    time.sleep(5)

    #nzElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtID"]')
    #codElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtUniqueID"]')


    with open('captcha.jpg', 'wb') as file:
        file.write(driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]').screenshot_as_png)

    result = subprocess.check_output(['./vocr', 'captcha.jpg'])

    captcha = result.decode('ascii')

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
        if text.find(badStr) == -1:
            noSlots=True
    if noSlots:
        driver.save_screenshot("fail.png")
    else:
        driver.save_screenshot("success.png")
    driver.save_screenshot("screenshot.png")
    driver.close()
    return not noSlots
    # closing browser

id=os.environ["MID_ID"]
cd=os.environ["MID_CODE"]

for i in range(20):
    try:
        success = checkSlots(id, cd)
        break;
    except:
        print("error happened, retry")

botkey=os.environ["MID_BOTKEY"]
mychannel=os.environ["MID_CHANNEL"]

tgapi=f'https://api.telegram.org/bot{botkey}/sendMessage'
payload={
  "text": f'Has slots!!! {id}' if success else f'No slots {id}',
  "parse_mode": "HTML",
  "disable_web_page_preview": False,
  "disable_notification": False,
  "chat_id": mychannel
}

requests.post(tgapi, json=payload)