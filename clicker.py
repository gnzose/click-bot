# --- ライブラリ読み込み ---
import time
import random
import threading
import csv
import os
from datetime import datetime
from selenium import webdriver
from collections import Counter
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException

# --- 外部モジュール ---
from urls_by_column import Lists
from user_agents import USER_AGENTS
#from ip_checker import log_ip_change

# ==========================
#        設定セクション
# ==========================
CLICK_WAIT_RANGE = (0.1, 1.5)#impの待ち時間
CLICK_PROBABILITY_RANGE = (0.87, 1.0)
CLICK_LOOP_BASE = 1200

SPECIAL_CLICK_RATE = (0.1, 0.23)
SPECIAL_CLICK_COUNT = random.randint(
    int(CLICK_LOOP_BASE * SPECIAL_CLICK_RATE[0]),
    int(CLICK_LOOP_BASE * SPECIAL_CLICK_RATE[1])
)

MAX_THREADS = 6
CHROMEDRIVER_PATH = "C:/Users/gnzos/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
TIMEOUT_THRESHOLD = 60
LOG_FILE = "progress_log.csv"

# ==========================
#        グローバル管理
# ==========================
thread_status = {}
thread_objects = {}
thread_lock = threading.Lock()
completed_threads = set()

# ==========================
#        共通関数群
# ==========================

# ==========================
#     ログ記録（メモリ保持型）
# ==========================
all_logs = []
log_lock = threading.Lock()

def write_log(thread_id, loop_idx, url):
    with log_lock:
        all_logs.append([datetime.now(), thread_id, loop_idx, url])


def create_driver():
    ua = random.choice(USER_AGENTS)
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument(f"user-agent={ua}")
    options.add_argument("--start-minimized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-infobars")
    options.add_argument("window-position=3000,0")  # ウィンドウを画面外へ
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    # ウィンドウを明示的に最小化
    #driver.minimize_window()

    return driver

def safe_get(driver, url, retries=2):
    for _ in range(retries):
        try:
            driver.get(url)
            return True
        except (TimeoutException, WebDriverException):
            time.sleep(10)
    return False

def human_scroll(driver, min_height=300, max_height=800, min_step=80, max_step=120):
    height = random.randint(min_height, max_height)
    pos = 0
    while pos < height:
        step = min(random.randint(min_step, max_step), height - pos)
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(random.uniform(0.05, 0.15))
        pos += step

# ==========================
#     アフィリクリック処理
# ==========================
def click_affiliate_link(driver, url, thread_name, loop_index, lst_index):
    if not safe_get(driver, url):
        return
    human_scroll(driver)
    time.sleep(random.uniform(1.0, 1.5))
    try:
        entry = driver.find_element(By.CSS_SELECTOR, "div.entry-content.cf")
        a_tag = entry.find_element(By.TAG_NAME, "a")
        link = a_tag.get_attribute("href")
        if link:
            print(f"➡️ アフィリリンククリック: {link}")
            if safe_get(driver, link):
                human_scroll(driver, 400, 1200, 100, 180)
                time.sleep(random.uniform(1.0, 1.5))
        else:
            msg = f"{url}（アフィリリンク取得失敗：リンクなし）"
            print(f"⚠️ {msg}")
            write_log(lst_index + 1, loop_index, msg)
    except (NoSuchElementException, StaleElementReferenceException) as e:
        msg = f"{url}（アフィリリンク取得失敗: {type(e).__name__}）"
        print(f"⚠️ {msg}")
        write_log(lst_index + 1, loop_index, msg)
    except Exception as e:
        msg = f"{url}（アフィリクリック例外: {type(e).__name__}）"
        print(f"❌ {msg}")
        write_log(lst_index + 1, loop_index, msg)




# ==========================
#     各スレッド処理関数
# ==========================
def run_browser(lst_index, url_list):
    driver = None
    thread_name = f"スレッド{lst_index + 1}"
    special_clicks_remaining = SPECIAL_CLICK_COUNT

    try:
        driver = create_driver()
        driver.set_page_load_timeout(30)

        for i in range(CLICK_LOOP_BASE):
            with thread_lock:
                thread_status[lst_index] = time.time()

            if not url_list:
                print(f"⚠️ {thread_name} 空のリスト → 終了")
                break

            url = url_list[i % len(url_list)]

            try:
                # ✅ アフィリクリック処理（修正済）
                if special_clicks_remaining > 0 and random.random() < (SPECIAL_CLICK_COUNT / CLICK_LOOP_BASE):
                    click_affiliate_link(driver, url, thread_name, i + 1, lst_index)
                    special_clicks_remaining -= 1
                    write_log(lst_index + 1, i + 1, f"{url}（アフィリクリック）")

                # ✅ 通常クリック処理
                elif random.random() < random.uniform(*CLICK_PROBABILITY_RANGE):
                    if safe_get(driver, url):
                        write_log(lst_index + 1, i + 1, url)
                        time.sleep(random.uniform(*CLICK_WAIT_RANGE))

                # ✅ スキップ
                else:
                    write_log(lst_index + 1, i + 1, url + "（スキップ）")

            except Exception as e:
                write_log(lst_index + 1, i + 1, url + f"（例外: {type(e).__name__}）")

        with thread_lock:
            completed_threads.add(lst_index)
        print(f"[{thread_name}] ✅ 完了")

    finally:
        if driver:
            try:
                driver.quit()
            except:
                os.system("taskkill /im chrome.exe /f")


# ==========================
#     スレッド制御関数
# ==========================
def start_thread(idx, url_list):
    with thread_lock:
        if idx in completed_threads:
            print(f"⚠️ スレッド {idx+1} は既に完了済み")
            return
        if not url_list:
            print(f"⚠️ スレッド {idx+1} のリストが空 → 起動スキップ")
            return
        t = threading.Thread(target=run_browser, args=(idx, url_list))
        t.start()
        thread_objects[idx] = t
        thread_status[idx] = time.time()

def monitor_threads():
    while True:
        time.sleep(60)
        now = time.time()
        with thread_lock:
            for idx in list(thread_status):
                last_active = thread_status[idx]
                t = thread_objects.get(idx)
                if (not t or not t.is_alive()) and (now - last_active > TIMEOUT_THRESHOLD):
                    if idx not in completed_threads:
                        print(f"⚠️ スレッド {idx+1} フリーズ検出 → 再起動")
                        start_thread(idx, Lists[idx])

# ==========================
#          実行部
# ==========================
# 実行時間計測開始
overall_start = time.time()

# ログファイル初期化（なければ）
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["timestamp", "thread_id", "loop_index", "url"])
# スレッド起動
for idx, lst in enumerate(Lists):
    if not lst:
        continue
    while threading.active_count() - 1 >= MAX_THREADS:
        time.sleep(1)
    start_thread(idx, lst)

# モニター用スレッド起動（フリーズ監視）
monitor = threading.Thread(target=monitor_threads, daemon=True)
monitor.start()

# 全スレッドの完了待ち
for idx in range(len(Lists)):
    t = thread_objects.get(idx)
    if t:
        t.join()

# 実行時間計測終了
overall_end = time.time()
elapsed = overall_end - overall_start
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)

# ログから統計情報を生成
def generate_summary():
    if not os.path.exists(LOG_FILE):
        print("⚠️ ログファイルが見つかりません")
        return

    error_count = 0
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダー行スキップ
            for row in reader:
                if len(row) >= 4:
                    message = row[3]
                    if any(x in message for x in ["例外", "失敗"]):
                        error_count += 1
    except Exception as e:
        print(f"❌ ログ読み取り中にエラー: {e}")
        return

    print("📋 実行レポート")
    print(f"🕒 所要時間         : {minutes}分 {seconds}秒")
    print(f"❌ エラー           : {error_count}")


print("🎉 全スレッド完了")

# ==========================
#     ログ一括書き出し
# ==========================
with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(all_logs)

generate_summary()