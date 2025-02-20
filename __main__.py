from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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
    
    # ✅ 1. **无界面模式（headless），提升性能**
    # options.add_argument("--headless=new")  # 旧版写法 "--headless"，新版推荐 "--headless=new"

    # ✅ 2. **禁用 GPU（仅在非 headless 模式下有用）**
    options.add_argument("--disable-gpu")  

    # ✅ 3. **减少资源占用**
    options.add_argument("--no-sandbox")  # 解决权限问题，减少沙盒机制的开销
    options.add_argument("--disable-dev-shm-usage")  # 解决 `/dev/shm` 内存不足问题
    options.add_argument("--disable-software-rasterizer")  # 禁用 GPU 软光栅化，减少 CPU 负担

    # ✅ 4. **限制 Chrome 进程数，防止 CPU 过载**
    options.add_argument("--disable-background-networking")  # 禁止 Chrome 进行后台网络操作
    options.add_argument("--disable-background-timer-throttling")  # 禁止后台 Tab 降低性能
    options.add_argument("--disable-backgrounding-occluded-windows")  # 禁用后台窗口优化
    options.add_argument("--disable-renderer-backgrounding")  # 禁止后台渲染优化
    options.add_argument("--disable-extensions")  # 禁用所有扩展，提高启动速度
    options.add_argument("--disable-sync")  # 禁用 Google 账户同步，提高性能

    # ✅ 5. **减少加载时间**
    options.add_argument("--disable-blink-features=AutomationControlled")  # 伪装成普通浏览器，避免被检测
    options.add_argument("--disable-ipc-flooding-protection")  # 取消 IPC 限制，提升性能
    options.add_argument("--disable-features=Translate,InfiniteSessionRestore,AutofillServerCommunication")  # 禁用翻译、自动填充等功能
    options.add_argument("--disk-cache-size=10000000")  # 限制缓存大小，减少 IO 负担

    # ✅ 6. **最大化窗口，提高页面可见区域**
    options.add_argument("--start-maximized")  # 启动时最大化窗口

    # ✅ 7. **自定义 User-Agent，避免被检测**
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.60 Safari/537.36")

    # ✅ 8. **禁用图片加载，提高加载速度**
    # options.add_argument("--blink-settings=imagesEnabled=false")

    # ✅ 9. **禁用日志，减少 CPU 负担**
    options.add_argument("--log-level=3")  # 降低日志级别，只显示严重错误
    options.add_argument("--silent")  # 关闭控制台日志输出

    # ✅ 10. **避免 Chrome 提示“正在自动化”**
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def log_in(driver):
    
    url = "https://developer.microsoft.com/en-us/graph/graph-explorer"
    driver.get(url)
    
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    
    time.sleep(3)
    
    # ms-Icon root-89 css-158 ms-Button-icon icon-155
    sign_in_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'ms-Icon') and contains(@class, 'root-89') and contains(@class, 'css-158') and contains(@class, 'ms-Button-icon') and contains(@class, 'icon-155')]"))
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
        
    email_input = WebDriverWait(driver, timeout=30).until(
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
    
    SIButton = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "idSIButton9"))
    )
    
    ActionChains(driver)\
        .send_keys_to_element(password_input, password)\
        .pause(1)\
        .click(SIButton)\
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
        
        sign_in_button = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'ms-Icon') and contains(@class, 'root-89') and contains(@class, 'css-158') and contains(@class, 'ms-Button-icon') and contains(@class, 'icon-155')]"))
        )
        
        while True:
            
            try:
                sign_in_button = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'ms-Icon') and contains(@class, 'root-89') and contains(@class, 'css-158') and contains(@class, 'ms-Button-icon') and contains(@class, 'icon-155')]"))
                )
                
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
                
            except (TimeoutException, NoSuchElementException):
                break
            
    except (TimeoutException, NoSuchElementException):
        pass

def prepare_query(driver):
    
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
    
    current_dir = os.path.dirname(__file__)
    database_path = os.path.join(current_dir, 'added.db')
    
    global conn, cursor
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(''' 
        create table if not exists events(
        time text,
        name text
        )
    ''')
    conn.commit()
    for name, time in data.items():
        cursor.execute("select * from events where name = ?", (name,))
        result = cursor.fetchone()
        if not result:
            print(time, name)
            create_event(driver, name, time)
            cursor.execute("insert into events values(?, ?)", (datetime.strftime(time, "%Y-%m-%d %H:%M:%S"), name))
            conn.commit()
    
def get_codeforces_contest(driver):
    url = "https://codeforces.com/contests?complete=true"
    driver.get(url)
    
    WebDriverWait(driver, 5).until(
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
                # print(time, name)
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
            # print(time, name)
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
            # print(time, name)
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
            # print(time, name)
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
            # print(time, name)
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
            # print(time, name)
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
            # print(time, name)
            data[name] = time
    
def store_sorted_entries(sorted_entries):
    for entry in sorted_entries:
        cursor.execute("insert into events (time, name) values(?, ?)", (entry[0], entry[1]))
        conn.commit()
    
def sort_table():
    cursor.execute("select * from events")
    entries = cursor.fetchall()
    sorted_entries = sorted(entries, key = lambda x : datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"))
    cursor.execute("delete from events")
    conn.commit()
    store_sorted_entries(sorted_entries)

if __name__ == "__main__":
    
    load_dotenv()
    
    driver = open_browser()

    get_codeforces_contest(driver)
    
    get_nowcoder_contest(driver)
    
    get_atcoder_contest(driver)
    
    get_luogu_contest(driver)
    
    get_lanqiao_contest(driver)
    
    get_acwing_contest(driver)
        
    log_in(driver)
    
    prepare_query(driver)
        
    store_event(driver)
    
    sort_table()
    
    driver.quit()
