# -*- coding: utf-8 -*-
# vocr is built from https://github.com/srirangav/vocr

import time
import subprocess
import os
import requests
import shutil
import traceback
import mlcaptcha

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def makeOptions():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return options

options = makeOptions()

try:
    baseurl=os.environ['MID_URL']
except:
    baseurl="https://trabzon.kdmid.ru/queue/OrderInfo.aspx"

blacklist=['https://istanbul.kdmid.ru/queue/OrderInfo.aspx']

if not (baseurl in blacklist):
    try:
        proxy=os.environ['MID_PROXY']
        print(f'Trying with proxy {proxy}')
        options.add_argument(f'--proxy-server={proxy}')
    except:
        print("No proxy specified")

botkey=os.environ["MID_BOTKEY"]
mychannel=os.environ["MID_CHANNEL"]
id=os.environ["MID_ID"]
cd=os.environ["MID_CODE"]

url=f'{baseurl}?id={id}&cd={cd}'

def send_photo(TOKEN, chat_id, image_path, image_caption="", notification = True):
    data = {"chat_id": chat_id, "caption": image_caption, "disable_notification": not notification}
    url = "https://api.telegram.org/bot%s/sendPhoto" % TOKEN
    with open(image_path, "rb") as image_file:
        ret = requests.post(url, data=data, files={"photo": image_file})

def checkSlots(id, cd):
    # initializing webdriver for Chrome
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    try:

        badStr="нет свободного времени"
        badStr2="Свободное время в системе записи отсутствует"
        
        print("Opening url " + url)
        driver.get(url)

        try:
            print("waiting for page to load")
            wait = WebDriverWait(driver, 60)
            wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_ButtonA')))
            print("page loaded")
        except TimeoutException as error:
            # not loaded
            print("page not loaded")
            driver.save_screenshot("noload.png")
            send_photo(botkey, mychannel, "./noload.png", f'Unexpected screen {id} {url}', True)
            raise error


        
        driver.execute_script('window.alert = function() {}')

        #nzElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtID"]')
        #codElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtUniqueID"]')

        captchaSolved = False
        while not captchaSolved:
    #        with open('captcha.png', 'wb') as file:
    #            file.write(driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]').screenshot_as_png)
            time.sleep(1) # sleep just in case image not fully loaded
            pngstring = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_imgSecNum"]').screenshot_as_png
            print("Solving captcha")

            # result = subprocess.check_output(['./vocr', 'captcha.png'])

            # captcha = result.decode('ascii')

            captcha = mlcaptcha.solvePngString(pngstring)

            print("my solution " + captcha)
            captchaSolution = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_txtCode"]')
            captchaSolution.clear()
            captchaSolved = True
            captchaSolution.send_keys(captcha)
            #time.sleep(1)
            #captchaSolution.submit()
            submitElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonA"]')
            submitElement.click()
            #time.sleep(1)
            try:
                captchaErrorElements = driver.find_elements(By.XPATH, '//*[@id="ctl00_MainContent_lblCodeErr"]')
                if len(captchaErrorElements):
                    print(captchaErrorElements[0].text)
                    if captchaErrorElements[0].text.find("имволы с картинки") != -1:
                        captchaSolved = False
            except NoSuchElementException as captchaError:
                captchaSolved = True
        
        try:
            print("Trying click blue button")
            signInElement = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_ButtonB"]')
            signInElement.click()
            #time.sleep(1)
        except NoSuchElementException as stateError:
            # either success or inconsistent state
            driver.save_screenshot("hz.png")
            send_photo(botkey, mychannel, "./hz.png", f'Unexpected screen {id} {url}', True)
            raise stateError
        

        # shutil.copy("./captcha.png", f'/Users/farafona/Projects/captchas/{captcha}.png')
        time.sleep(1)
        print("Testing results screen")
        pElements = driver.find_elements(By.TAG_NAME, 'p')
        noSlots=False
        for element in pElements:
            # print(element.text)
            text = element.text
            print(text)
            if text.find(badStr) != -1:
                noSlots=True
            if text.find(badStr2) != -1:
                noSlots=True
            if text.find("invalid response")!= -1:
                raise ValueError(text)
    #    if noSlots:
    #        driver.save_screenshot("fail.png")
    #    else:
    #        driver.save_screenshot("success.png")
        print("Has no slots" if noSlots else "Found slots")
        driver.save_screenshot("screenshot.png")
        hasSlots = not noSlots
        if hasSlots:
            try:
                radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                print(len(radios))
                if (len(radios) > 0): 
                    radios[0].click()
                time.sleep(1)
                driver.save_screenshot("screenshot1.png")
                send_photo(botkey, mychannel, "./screenshot1.png", f'{id} Clicked radiobutton')
                # allInputs = driver.find_elements(By.TAG_NAME, "input")
                mainButton = driver.find_element(By.ID, "ctl00_MainContent_Button1")
                mainButton.click()
                time.sleep(1)
                driver.save_screenshot("screenshot2.png")
                send_photo(botkey, mychannel, "./screenshot2.png", f'{id} Clicked main button')

                """for input in allInputs:
                    print(input)
                    print(input.get_attribute("id"))
                    print(input.get_attribute("name")) """
            except:
                print("Registration process failed")
        return hasSlots
    finally:                
        driver.close()
    # closing browser

success = False
exception = False
fail = True
for i in range(4):
    try:
        success = checkSlots(id, cd)
        fail = False
        break;
    except Exception as err:
        print(f'attempt #{i} failed')
        print(f"Unexpected {err=}, {type(err)=}")
        if (i==0):
            print("removing proxy if it was")
            options=makeOptions()
        exception = err
#        traceback.print_exception(err)
if fail:
    raise exception
send_photo(botkey, mychannel, "./screenshot.png", f'Has slots!!! {id} {url}' if success else f'No slots {id} {url}', success)