import re
import time
import json
import random
import sys, os
import requests
import threading
import pandas
import soundfile as sf
import sounddevice as sd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException


def selenium_connect(ads):
  f = 5
  # print(selections)
  open_url = f"http://local.adspower.net:5032{f}/api/v1/browser/start?user_id={ads}"
  close_url = f"http://local.adspower.net:5032{f}/api/v1/browser/stop?user_id={ads}"

  resp = requests.get(open_url).json()
  if resp["code"] != 0:
    print(resp["msg"])
    print("please check ads_id")
    sys.exit()

  chrome_driver = resp["data"]["webdriver"]
  chrome_options = Options()
  chrome_options.add_argument("--ignore-certificate-errors")
  chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
  driver = webdriver.Chrome(chrome_driver, options=chrome_options)
  driver.get('https://nopecha.com/setup#sub_1NnGb4CRwBwvt6ptDqqrDlul|enabled=true|disabled_hosts=%5B%5D|hcaptcha_auto_open=true|hcaptcha_auto_solve=true|hcaptcha_solve_delay=true|hcaptcha_solve_delay_time=3000|recaptcha_auto_open=false|recaptcha_auto_solve=false|recaptcha_solve_delay=false|recaptcha_solve_delay_time=1000|recaptcha_solve_method=Image|funcaptcha_auto_open=true|funcaptcha_auto_solve=true|funcaptcha_solve_delay=true|funcaptcha_solve_delay_time=0|awscaptcha_auto_open=true|awscaptcha_auto_solve=true|awscaptcha_solve_delay=true|awscaptcha_solve_delay_time=0|textcaptcha_auto_solve=true|textcaptcha_solve_delay=true|textcaptcha_solve_delay_time=0|textcaptcha_image_selector=|textcaptcha_input_selector=')
  return driver


def check_for_element(driver, selector, click=False, xpath=False):
  try:
    if xpath: element = driver.find_element(By.XPATH, selector)
    else: element = driver.find_element(By.CSS_SELECTOR, selector)
    if click: click_button_safe(driver, element)
    return element
  except: return False


def wait_for_element(driver, selector, wait=30, click=False):
  try:
    element = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    if click: click_button_safe(driver, element)
    return element
  except: return False


def click_button_safe(driver, button):
  try:
    button.click()
  except WebDriverException:
    # Scroll to the button to make it clickable
    driver.execute_script("arguments[0].scrollIntoView();", button)

    button.click()


def mchtms(h3):
  for idt in range(65,91):
    uj='v'+chr(idt)
    if uj in h3:
      ujidx=h3.index(uj)
      new_h3=[h3[:ujidx],h3[ujidx+1:]]
      return new_h3


# def check_for_403(driver):
#   try:
#     if driver.find_element(By.TAG_NAME, 'h1').text == "403 ERROR" or driver.find_elements(By.TAG_NAME, 'h1')[3].text == "We are working to restore it as soon as possible":
#       return True
#   except: False


# def check_for_captcha(driver):
#     try:
#         driver.find_element(By.CSS_SELECTOR, '#captcha-container')
#         return True
#     except:
#         return False


# def check_for_captcha_and_403(driver):
#   while True:
#     if check_for_captcha:
#       time.sleep(1)
#       continue
#     break
#   while True:
#     if check_for_403(driver):
#       print('403')
#       time.sleep(30)
#       driver.refresh()
#       continue
#     break


def pass_data(driver, data, selector):
  while True:
    try:
      element = check_for_element(driver, selector, click=True)
      element.clear()
      for k in data:
          element.send_keys(k)
          time.sleep(.1)
      wait_for_element(driver, 'div[data-state="solved"]')
      contButton = driver.find_element(By.CSS_SELECTOR, '#edit-submit')
      contButton.click()
      break
    except:
      driver.refresh()
      continue


def login_page(driver, email, password):
  while True:
    # check_for_captcha_and_403(driver)
    if check_for_element(driver, 'input[name="name"]'): pass_data(driver, email, 'input[name="name"]')
    if check_for_element(driver, 'input[type="password"]'): pass_data(driver, password, 'input[type="password"]')
    if driver.current_url != 'https://tickets.rugbyworldcup.com/en/user/login?destination=/en/home': break


def read_excel():
  detx = pandas.read_excel('r.xlsx').values.tolist()
  detx = pandas.read_excel('r.xlsx').values.tolist()
  selections = []

  for x in detx:
    ttl = x[1]
    dct = {}
    ctgs = []

    for i, y in enumerate(x[2:]):
      if i < 4:  # Check if i is within the valid range
        i = [1, 2, 3, 4][::-1][i]
        try:
          dct[str(i)] = int(y)
          ctgs.append(i)
        except:
          pass

    if ctgs != []:
      selections.append([ttl, dct, ctgs])
  return selections


def choose_match(driver, selections):
  try:
    h3x='//*[@class="list-ticket-content"][.//*[contains(text(),"View")]]//h3'
    check_for_element(driver, h3x, xpath=True)
    h3s=[' v '.join(mchtms(h3.text)) for h3 in driver.find_elements(By.XPATH,h3x)]
    match_data = random.choice([x for x in selections if x[0] in h3s])
    t = match_data[0].split(' v ')
    return (t, match_data)
      
  except: return False


def get_cart_data(driver, email, password, name):
  try:
    info_head = driver.find_elements(By.CSS_SELECTOR, '#cart-summary-form > ul > li')
    for info in info_head:
      price = info.find_element(By.CSS_SELECTOR, 'div.product-unit-price.d-none.d-lg-flex')
      quantity = info.find_element(By.CSS_SELECTOR, 'div.product-qty.d-none.d-lg-flex')
      title = info.find_element(By.CLASS_NAME, 'product-title-wrapper')
      seats = info.find_element(By.CSS_SELECTOR, '.seat-content')
      category = info.find_element(By.CSS_SELECTOR, '.product-category')
      print("price ", price.text, "quantity ", quantity.text, "title ", title.text, 'seat ',
             seats.text, 'category', category.text)
      data.append({"title": title.text, "price": price.text,
                   "quantity": quantity.text, "seat-content": seats.text, "user": name,
                   "category": category.text, "account_name": email, "account_password": password})
    return data
  except: return False


def success(driver, email, password, name):
  data, fs = sf.read('noti.wav', dtype='float32')  
  sd.play(data, fs)
  status = sd.wait()
  data = get_cart_data(driver, email, password, name)
  try: json_data = json.dumps(data)
  except Exception as e: print(e)
  headers = {"Content-Type": "application/json"}

  # Send the POST request
  try:
    response = requests.post("http://localhost:500/book", data=json_data, headers=headers)
    print(response)
  except Exception as e: print(e)
  # Check the response status code
  if response.status_code == 200: print("POST request successful!")
  else: print("POST request failed.")
  print('waiting for 20 min')
  time.sleep(1200)


def main(email, password, ads, name):
  driver = selenium_connect(ads)
  base_url = 'https://tickets.rugbyworldcup.com/en'
  selections = read_excel()
  while True:
    driver.get(base_url)
    # check_for_captcha_and_403(driver)
    wait_for_element(driver, '#onetrust-accept-btn-handler', wait=3, click=True)
    if check_for_element(driver, 'a[class="btn user-account-login"]', click=True): login_page(driver, email, password)
    t, match_data = choose_match(driver, selections)
    t1 = t[0]
    t2 = t[-1]
    if not check_for_element(driver, f'//*[@class="list-ticket-content"][.//span[1][contains(text(),"{t1}")]][.//span[3][contains(text(),"{t2}")]]//*[contains(text(),"View")]', click=True, xpath=True): continue
    if not check_for_element(driver, '//*[@role="dialog"]//*[@class="ticketing-info"]/a', click=True, xpath=True): continue
    # check_for_captcha_and_403(driver)
    if not check_for_element(driver, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]', xpath=True): continue
    avctg = [int(re.compile('\d').findall(c.text)[-1]) for c in driver.find_elements(By.XPATH, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//div[@class="title"]')]
    wanted = [x1 for x1 in match_data[-1] if x1 in avctg]
    
    if wanted == []:
      print('no match')
      continue
    category = str(random.choice(wanted))
    if not check_for_element(driver, f'//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//*[contains(text(),"Y {category}")]', click=True, xpath=True): continue
    seats = match_data[1][category]
    for _ in range(0, seats): check_for_element(driver, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//span[@class="operator more active"]', click=True, xpath=True)
    check_for_element(driver, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//button[@class="btn btn-primary js-category-auto noloader"]', click=True, xpath=True)
    if driver.current_url == 'https://tickets.rugbyworldcup.com/en/cart': 
      success(driver, email, password, name)
      print('waiting for 20 min')
      time.sleep(1200)
    

if __name__ == "__main__":
  try: file = open('accounts.txt', 'r', encoding='utf-8').readlines()
  except Exception as e:
    print('Не можу розпiзнати, що написано в accounts.txt!')
    print(e)
    time.sleep(15)
    exit()
  
  threads = []
  for el in file:
    data = el.strip()
    email, password, ads, name = data.split('````')
    print(email, password, ads, name)

    thread = threading.Thread(target=main, args=(email, password, ads, name,))
    thread.start()
    threads.append(thread)

    delay = random.uniform(5, 10)
    time.sleep(delay)
  
  for thread in threads:
    thread.join()
