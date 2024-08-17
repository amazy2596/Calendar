from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium import webdriver
from dotenv import load_dotenv
import pyperclip
import sqlite3
import json
import time
import re
import os

data = {}

def open_browser():

    options = Options()
    # options.add_argument("--headless")  # 如果需要无界面模式，取消注释

    service = Service(os.getenv("driver_path"))
    
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def sign_in(driver):
    
    email = os.getenv("email_address")
    password = os.getenv("email_password")

    url = "https://developer.microsoft.com/en-us/graph/graph-explorer"
    driver.get(url)
    
    sign_in_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "root-151"))
    )
    
    ActionChains(driver)\
        .click(sign_in_button)\
        .perform()
        
    original_window = driver.current_window_handle
    all_windows = driver.window_handles
    
    for window in all_windows:
        if window != original_window:
            driver.switch_to.window(window)
            break
    
    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "i0116"))
    )
    
    next_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "idSIButton9"))
    )
    
    ActionChains(driver)\
        .send_keys_to_element(email_input, email)\
        .pause(1)\
        .click(next_button)\
        .pause(1)\
        .perform()
    
    time.sleep(1)
    
    password_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "i0118"))
    )
    
    sign_in_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "idSIButton9"))
    )
    
    ActionChains(driver)\
        .send_keys_to_element(password_input, password)\
        .pause(1)\
        .click(sign_in_button)\
        .pause(1)\
        .perform()
        
    stay_signed_in_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "acceptButton"))
    )
    
    ActionChains(driver)\
        .click(stay_signed_in_button)\
        .pause(3)\
        .perform()
        
    driver.switch_to.window(original_window)
        
    driver.refresh()
    
    try: 
        
        sign_in_button = driver.find_element("css selector", ".root-151")
        
        while True:
            
            try:
                
                sign_in_button = driver.find_element("css selector", ".root-151")
                
                ActionChains(driver)\
                    .pause(1)\
                    .click(sign_in_button)\
                    .pause(1)\
                    .perform()
                
                all_windows = driver.window_handles
                
                for window in all_windows:
                    if window != original_window:
                        driver.switch_to.window(window)
                        break
                
                email_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "i0116"))
                )
                
                next_button = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "idSIButton9"))
                )
                
                ActionChains(driver)\
                    .send_keys_to_element(email_input, email)\
                    .pause(1)\
                    .click(next_button)\
                    .pause(3)\
                    .perform()
                
                driver.switch_to.window(original_window)                    

                driver.refresh()
                
            except NoSuchElementException:
                break
            
    except NoSuchElementException:
        pass
        
    search_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//*[@placeholder = 'Search sample queries']"))
    )
    
    ActionChains(driver)\
        .click(search_box)\
        .pause(1)\
        .send_keys("安排会议")\
        .perform()
    
    global post_event
    post_event = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//*[text()='安排会议']"))
    )
    
    global request_body_tab
    request_body_tab = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'view-lines') and contains(@class, 'monaco-mouse-cursor-text')]"))
    )
    
    global run_query
    run_query = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//*[text() = 'Run query']"))
    )
    
def create_event(driver, name, time):
    
    time -= timedelta(hours=8)
    time = time.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    
    request_body = {
        "subject": name,
        "start": {
            "dateTime": time,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": time,
            "timeZone": "UTC"
        }
    }
    
    pyperclip.copy(json.dumps(request_body, indent=4))
    
    ActionChains(driver)\
        .click(post_event)\
        .pause(1)\
        .click(request_body_tab)\
        .pause(1)\
        .key_down(Keys.CONTROL)\
        .send_keys("a")\
        .send_keys("v")\
        .key_up(Keys.CONTROL)\
        .pause(1)\
        .click(run_query)\
        .perform()

def store_event(driver):
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    database_path = os.path.join(data_dir, 'event.db')
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(''' create table if not exists events(
        time text,
        name text
    )''')
    for name, time in data.items():
        cursor.execute("select * from events where name = ?", (name,))
        result = cursor.fetchone()
        if not result:
            create_event(driver, name, time)
            cursor.execute("insert into events values(?, ?)", (time, name))
            conn.commit()
    
def get_codeforces_contest(driver):
    url = "https://codeforces.com/contests?complete=true"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "datatable"))
    )
    contests = driver.find_elements("css selector", ".datatable tbody tr")
    for contest in contests:
        if re.search(r'Round \d+( \(Div. \d\)| \(Rated for Div. \d\))', contest.text) is not None:
            name = contest.find_elements("css selector", "td")[0].text
            time = contest.find_elements("css selector", "td")[2].text
            
            time = re.sub(r'UTC\+\d+', "", time)
            time = datetime.strptime(time, "%b/%d/%Y %H:%M")
            
            if time > datetime.now():
                print(name, time)
                data[name] = time
                
def get_nowcoder_contest(driver):
    url = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "platform-mod"))
    )
    
    contests = driver.find_elements("css selector", ".js-item")
    for contest in contests:
        name = contest.find_element("css selector", "h4 a").text
        time = contest.find_element("css selector", ".match-time-icon").text
        
        time = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', time).group(0)
        time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        
        if time > datetime.now():
            print(name, time)
            data[name] = time
            
    url = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=14"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "platform-mod"))
    )
    
    contests = driver.find_elements("css selector", ".js-item")
    for contest in contests:
        name = contest.find_element("css selector", "h4 a").text
        time = contest.find_element("css selector", ".match-time-icon").text
        
        time = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', time).group(0)
        time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        
        if time > datetime.now():
            print(name, time)
            data[name] = time
            
def get_atcoder_contest(driver):
    url = "https://atcoder.jp/contests/"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "contest-table-upcoming"))
    )
    
    contests = driver.find_elements("css selector", "#contest-table-upcoming tbody tr")
    for contest in contests:
        name = contest.find_element("css selector", "td:nth-child(2) a").text
        time = contest.find_element("css selector", ".fixtime-full").text
        
        time = datetime.strptime(time, "%Y-%m-%d(%a) %H:%M")
        
        if time > datetime.now():
            print(name, time)
            data[name] = time
            
def get_luogu_contest(driver):
    url = "https://www.luogu.com.cn/contest/list"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "row-wrap"))
    )
    
    contests = driver.find_element("css selector", ".row-wrap").find_elements("css selector", ".row")
    for contest in contests:
        name = contest.find_elements("css selector", "a")[0].text
        time = contest.find_elements("css selector", ".time")[0].text
        
        time = time.split(" ~")[0]
        time = str(datetime.now().year) + "-" + time
        time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        
        if time > datetime.now():
            print(name, time)
            data[name] = time
            
def get_lanqiao_contest(driver):
    url = "https://www.lanqiao.cn/oj-contest/"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "oj-contest-card-wrap"))
    )
    
    contests = driver.find_elements("css selector", ".oj-contest-card-wrap")
    for contest in contests:
        
        name = contest.find_element("css selector", ".title").text
        time = contest.find_element("css selector", ".time").text
        
        time = re.search(r'\d{2}月\d{2}日 \d{2}:\d{2}', time).group(0)
        time = str(datetime.now().year) + "-" + time.split("月")[0] + "-" + time.split("月")[1].split("日")[0] + " " + time.split(" ")[1]
        
        time = datetime.strptime(time, "%Y-%m-%d %H:%M")
        
        if time > datetime.now():
            print(name, time)
            data[name] = time
            
def get_acwing_contest(driver):
    url = "https://www.acwing.com/activity/1/competition/"
    driver.get(url)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "activity-index-block"))
    )
    
    contests = driver.find_elements("css selector", ".activity-index-block")
    for contest in contests:
        
        name = contest.find_element("css selector", ".activity_title").text
        time = contest.find_elements("css selector", ".activity_td")[1].text
        
        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        
        if time > datetime.now():
            print(name, time)
            data[name] = time

if __name__ == "__main__":
    
    load_dotenv()
    
    driver = open_browser()

    get_codeforces_contest(driver)
    
    get_nowcoder_contest(driver)
    
    get_atcoder_contest(driver)
    
    get_luogu_contest(driver)
    
    get_lanqiao_contest(driver)
    
    get_acwing_contest(driver)
        
    sign_in(driver)
        
    store_event(driver)
    
    driver.quit()
