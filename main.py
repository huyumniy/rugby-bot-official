import re
import time
import json
import random
import sys, os
import shutil
import tempfile
import requests
import threading
import pandas as pd
import soundfile as sf
import sounddevice as sd
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException


PROXY = ('proxy.soax.com', 9000, 'mZ7COGLGDP04INBs', 'wifi;;;;')


class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)

        background_js = self.background_js % (host, port, user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)


def read_proxy_file(file_path):
    with open(file_path, 'r') as file:
        proxy_lines = file.readlines()
    return proxy_lines

def choose_random_proxy(proxy_lines):
    random_proxy = random.choice(proxy_lines).strip()
    domain, port, login, password = random_proxy.split(':')
    return (domain, int(port), login, password)


def selenium_connect():
  options = webdriver.ChromeOptions()
  options.add_argument("--start-maximized")
  #options.add_argument("--incognito")
  options.add_argument("--disable-blink-features=AutomationControlled")
  options.add_argument("--log-level=3")
  options.add_argument("--disable-web-security")
  options.add_argument("--disable-site-isolation-trials")
  options.add_argument('--ignore-certificate-errors')
  options.add_argument('--lang=EN')
  #pergfan:6ofKZOXwL7qSTGNZ@proxy.packetstream.io:31112
  # proxy = choose_random_proxy(read_proxy_file('./proxies.txt'))
  # proxy_extension = ProxyExtension(*proxy)
  options.add_argument(f"--load-extension=D:\\projects\\rugby-bot-resale\\NopeCHA")

  prefs = {"credentials_enable_service": False,
      "profile.password_manager_enabled": False}
  options.add_experimental_option("prefs", prefs)

  # Create the WebDriver with the configured ChromeOptions
  driver = webdriver.Chrome(
      options=options,
      enable_cdp_events=True,
  )

  screen_width, screen_height = driver.execute_script(
      "return [window.screen.width, window.screen.height];")
  
  desired_width = int(screen_width / 2)
  driver.set_window_position(0, 0)
  driver.set_window_size(desired_width, screen_height)
  driver.get('https://nopecha.com/setup#sub_1NnGb4CRwBwvt6ptDqqrDlul|enabled=true|disabled_hosts=%5B%5D|hcaptcha_auto_open=true|hcaptcha_auto_solve=true|hcaptcha_solve_delay=true|hcaptcha_solve_delay_time=3000|recaptcha_auto_open=true|recaptcha_auto_solve=true|recaptcha_solve_delay=true|recaptcha_solve_delay_time=1000|recaptcha_solve_method=Image|funcaptcha_auto_open=true|funcaptcha_auto_solve=true|funcaptcha_solve_delay=true|funcaptcha_solve_delay_time=0|awscaptcha_auto_open=true|awscaptcha_auto_solve=true|awscaptcha_solve_delay=true|awscaptcha_solve_delay_time=0|textcaptcha_auto_solve=true|textcaptcha_solve_delay=true|textcaptcha_solve_delay_time=0|textcaptcha_image_selector=|textcaptcha_input_selector=')
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


def pass_data(driver, data, selector):
  while True:
    try:
      iframe = driver.find_element(By.CSS_SELECTOR, 'iframe[title=reCAPTCHA]')
      driver.switch_to.frame(iframe)
      if not wait_for_element(driver, '#rc-anchor-container', wait=5):
        driver.switch_to.default_content()
        element = check_for_element(driver, selector, click=True)
        if not element: break
        element.clear()
        for k in data:
          element.send_keys(k)
          time.sleep(.1)
        contButton = driver.find_element(By.CSS_SELECTOR, '#edit-submit')
        contButton.click()
        break
      else:
        if not wait_for_element(driver, 'span[id="recaptcha-anchor"][aria-checked="true"]', wait=60): raise Exception
        driver.switch_to.default_content()
        element = check_for_element(driver, selector, click=True)
        if not element: break
        element.clear()
        for k in data:
          element.send_keys(k)
          time.sleep(.1)
        contButton = driver.find_element(By.CSS_SELECTOR, '#edit-submit')
        contButton.click()
        break
    except:
      driver.switch_to.default_content()
      driver.refresh()
      continue


def login_page(driver, email, password):
  while True:
    # check_for_captcha_and_403(driver)
    if check_for_element(driver, 'input[name="name"]'): pass_data(driver, email, 'input[name="name"]')
    if check_for_element(driver, 'input[type="password"]'): pass_data(driver, password, 'input[type="password"]')
    if 'https://tickets.rugbyworldcup.com/en/user/login' not in driver.current_url: break


def read_excel(file_path):
    df = pd.read_excel(file_path)
    matches_data = []

    for i in range(len(df)):
        match_info = df.iloc[i, :].tolist()
        match_data = {
            "match": match_info[1],
            "categories": {
                1: match_info[2],
                2: match_info[3],
                3: match_info[4],
                4: match_info[5]
            },
            "link": match_info[6]
        }
        matches_data.append(match_data)

    return matches_data


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
    data = []
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


def get_random_email_and_password(file_path):
  emails_and_passwords = []

  # Read the file and extract emails and passwords
  with open(file_path, 'r') as file:
    for line in file:
      email, password = line.strip().split('````')
      emails_and_passwords.append((email, password))

  # Choose a random email and password
  random_email, random_password = random.choice(emails_and_passwords)
  return random_email, random_password


def main(link, categories):
  driver = selenium_connect()
  
  while True:
    driver.get(link)
    email, password = get_random_email_and_password('./accounts.txt')
    print(email, password)
    while True:
        if check_for_element(driver, '#captcha-container'): time.sleep(5)
        else: break
    while True:
        if check_for_element(driver, "//*[contains(text(), '403 ERROR')]", xpath=True): 
            time.sleep(30)
            continue
        else: break
    wait_for_element(driver, '#onetrust-accept-btn-handler', wait=3, click=True)
    if check_for_element(driver, 'a[class="btn user-account-login"]', click=True): login_page(driver, email, password)
    
    if not check_for_element(driver, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]', xpath=True): continue
    avctg = [int(re.compile('\d').findall(c.text)[-1]) for c in driver.find_elements(By.XPATH, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//div[@class="title"]')]
    wanted = []
    for key in categories.keys():
      if key in avctg:
        check_for_element(driver, f'//*[@class="filter-wrapper info-category"]//*[@class="first-letter-cap"][contains(text(),"Y {key}")]', click=True, xpath=True)
        wanted.append(key)
    if wanted == []:
      print('no match')
      continue
    category = int(random.choice(wanted))
    if not check_for_element(driver, f'//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//*[contains(text(),"Y {category}")]', click=True, xpath=True): continue
    for _ in range(0, int(categories[category])): check_for_element(driver, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//span[@class="operator more active"]', click=True, xpath=True)
    check_for_element(driver, '//*[@class="ticket-category-list js-block-list-categories"]//li[not(.//*[contains(text(),"Unavailable")])]//button[@class="btn btn-primary js-category-auto noloader"]', click=True, xpath=True)
    if driver.current_url == 'https://tickets.rugbyworldcup.com/en/cart': 
      success(driver, email, password, 'general')
      print('waiting for 20 min')
      time.sleep(1200)
    

if __name__ == "__main__":
  matches_data = read_excel("./r.xlsx")
  threads = []
  option = input('Choose one option [ONE|ALL]: ')
  if option in ["all", "ALL"]: 
    for row in matches_data:
      link = row["link"]
      if not pd.notna(link): continue
      categories = row["categories"]
      types = []
      for value in categories.values():
          if pd.notna(value): types.append(value)
      if types == []: continue
      match = row["match"]
      thread = threading.Thread(target=main, args=(link, categories))
      thread.start()
      threads.append(thread)


      delay = random.uniform(5, 10)
      time.sleep(delay)
    for thread in threads:
      thread.join()
  elif option in ['one', 'ONE']:
    for row_index in range(len(matches_data)):
      link = matches_data[row_index]["link"]
      if not pd.notna(link): continue
      categories = matches_data[row_index]["categories"]
      types = []
      for value in categories.values():
          if pd.notna(value): types.append(value)
      if types == []: continue
      match = matches_data[row_index]["match"]
      print(row_index, match)
    row_index = input('Index: ')
    link = matches_data[int(row_index)]['link']
    categories = matches_data[int(row_index)]['categories']
    thread = threading.Thread(target=main, args=(link,categories))
    thread.start()
    threads.append(thread)
