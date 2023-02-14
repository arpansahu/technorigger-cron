import os
import time

codeList = ["TR", "US-C", "US", "US-W", "CA", "CA-W", "FR", "DE", "NL", "NO", "RO", "CH", "GB", "HK"]
import random

from django.conf import settings

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By


def connect_to_vpn():
    try:
        vpn_choice_code = random.choice(codeList)
        os.system("windscribe connect " + vpn_choice_code)
    except:
        print('--------------------Error in Connecting to VPN-------------------------')


def re_connect_to_vpn():
    try:
        os.system("windscribe disconnect")
        vpn_choice_code = random.choice(codeList)
        os.system("windscribe connect " + vpn_choice_code)
    except:
        print('-----------------------Some Error Occurred in Re Connecting VPN---------------------------------')


def disconnect_to_vpn():
    os.system("windscribe disconnect")


def get_driver_with_vpn():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_extension('windscribe.crx')
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument("enable-features=NetworkServiceInProcess")
    driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=chrome_options)
    driver.maximize_window()

    cond_ext = True
    while cond_ext:
        try:
            time.sleep(5)
            driver.get('chrome-extension://hnmpcagpplmpfojmgmnngilcnanddlhb/popup.html')
            cond_ext = False
        except:
            print('Blocked Extension by Chromium')

    time.sleep(5)
    body = driver.find_elements(By.TAG_NAME, 'body')
    login = body[0].find_element(By.XPATH, '//*[@id="app-frame"]/div/button[2]')
    login.click()

    cond = True
    retry_login_cond = 0

    while cond:
        try:
            retry_login_cond += 1
            username = body[0].find_element(By.XPATH, '//*[@id="app-frame"]/div/div/form/div[1]/div[2]/input')
            username.clear()
            username.send_keys(settings.WINDSCRIBE_USERNAME)
            time.sleep(2)
            password = body[0].find_element(By.XPATH, '//*[@id="app-frame"]/div/div/form/div[2]/div[2]/input')
            password.clear()
            password.send_keys(settings.WINDSCRIBE_PASSWORD)
            time.sleep(2)
            final_login = body[0].find_element(By.XPATH, '//*[@id="app-frame"]/div/div/form/div[3]/button')
            final_login.click()
        except:
            print('Error in Login Page of WindScribe')
            if retry_login_cond > 50:
                print('Something is Wrong')
                exit()
            driver.get('chrome-extension://hnmpcagpplmpfojmgmnngilcnanddlhb/popup.html')
        try:

            skip = driver.find_elements(By.TAG_NAME, 'body')
            time.sleep(3)
            if 'Login' in skip[0].text:
                cond = True
            else:
                cond = False
                print('Login SuccessFull in WindScribe')

        except Exception as e:
            print('Failed to Login in WindScribe Trying Again')
    return driver


def change_vpn_location(driver):
    driver.get('chrome-extension://hnmpcagpplmpfojmgmnngilcnanddlhb/popup.html')
    time.sleep(3)

    body = driver.find_elements(By.TAG_NAME, 'body')
    location_button = body[0].find_element(By.XPATH,
                                           '//*[@id="app-frame"]/div/div[4]/div[1]/div[1]/div[1]/div/div['
                                           '2]/button/div/div[1]')
    location_button.click()
    time.sleep(2)

    len_of_regions = 1

    cond_region = True

    while cond_region:
        try:
            region_element = body[0].find_element(By.XPATH,
                                                  f'//*[@id="app-frame"]/div/div[2]/div/div/div[{len_of_regions}]')
            len_of_regions += 1
        except:
            cond_region = False

    random_index_region = random.randint(2, len_of_regions)

    print(len_of_regions, random_index_region)

    selected_region = body[0].find_element(By.XPATH,
                                           f'//*[@id="app-frame"]/div/div[2]/div/div/div[{random_index_region}]')
    selected_region.click()

    cond_location = True

    location_count = 1

    while cond_location:
        try:
            location_element = body[0].find_element(By.XPATH,
                                                    f'//*[@id="app-frame"]/div/div[2]/div/div/div[{random_index_region}]/div[2]/div[{location_count}]')
            location_count += 1
        except:
            cond_location = False

    random_index_location = random.randint(1, location_count)
    print(location_count, random_index_location)

    time.sleep(2)

    selected_location = body[0].find_element(By.XPATH,
                                             f'//*[@id="app-frame"]/div/div[2]/div/div/div[{random_index_region}]/div[2]/div[{random_index_location}]')
    selected_location.click()
