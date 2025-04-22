import time
import random
import threading
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from urls_by_column import Lists
from user_agents import USER_AGENTS
from ip_checker import log_ip_change
import os
from datetime import datetime

# --- 設定 ---
CLICK_WAIT_RANGE = (0.25, 1.0)
CLICK_PROBABILITY_RANGE = (0.7, 1.0)
CLICK_LOOP_BASE = 1000
MAX_THREADS = 5
CHROMEDRIVER_PATH = "C:/Users/gnzos/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
TIMEOUT_THRESHOLD = 60
LOG_FILE = "progress_log.csv"

# スレッド管理
thread_status = {}
thread_objects = {}
thread_lock = threading.Lock()
completed_threads = set()  # 完了したスレッドIDを追跡

# --- ログ出力用 ---
def write_log(thread_id, loop_idx, url):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), thread_id, loop_idx, url])

# --- 各スレッド実行 ---
def run_browser(lst_index, url_list):
    driver = None
    thread_name = f"スレッド{lst_index + 1}"

    try:
        selected_user_agent = random.choice(USER_AGENTS)
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={selected_user_agent}")
        options.add_argument("--start-minimized")  # ウィンドウ最小化
        options.add_argument("--ignore-certificate-errors")

        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
        driver.set_page_load_timeout(30)

        print(f"🧵 {thread_name} 開始（URL数: {len(url_list)}）")

        for i in range(CLICK_LOOP_BASE):
            with thread_lock:
                thread_status[lst_index] = time.time()

            url = url_list[i % len(url_list)]
            current_ip = log_ip_change(thread_name)

            if random.random() < random.uniform(*CLICK_PROBABILITY_RANGE):
                try:
                    driver.get(url)
                    wait_time = random.uniform(*CLICK_WAIT_RANGE)
                    print(f"[{thread_name}-{i+1}] ✅ アクセス: {url}（IP: {current_ip}）")
                    write_log(lst_index+1, i+1, url)
                    time.sleep(wait_time)
                except TimeoutException:
                    print(f"[{thread_name}-{i+1}] ⚠️ タイムアウト: {url}（IP: {current_ip}）")
                except Exception as e:
                    print(f"[{thread_name}-{i+1}] ❌ アクセス失敗: {url}（IP: {current_ip}） → {e}")
            else:
                print(f"[{thread_name}-{i+1}] ⏭️ スキップ: {url}（IP: {current_ip}）")
                write_log(lst_index+1, i+1, url + "（スキップ）")

        with thread_lock:
            completed_threads.add(lst_index)  # スレッド完了を記録

        print(f"[{thread_name}] ✅ 完了")

    except Exception as e:
        print(f"[{thread_name}] ❌ エラー発生: {e}")
        time.sleep(5)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"[{thread_name}] ⚠️ driver.quit()失敗: {e}")
                os.system("taskkill /im chrome.exe /f")


# --- スレッド起動 ---
def start_thread(idx, url_list):
    with thread_lock:
        if idx in completed_threads:
            print(f"⚠️ スレッド {idx+1} は既に完了しているため再起動しません。")
            return
        t = threading.Thread(target=run_browser, args=(idx, url_list))
        t.start()
        thread_objects[idx] = t
        thread_status[idx] = time.time()

# --- スレッド監視 ---
def monitor_threads():
    while True:
        time.sleep(60)
        now = time.time()
        with thread_lock:
            for idx in list(thread_status.keys()):
                last_active = thread_status.get(idx, 0)
                t = thread_objects.get(idx)

                if (not t or not t.is_alive()) and (now - last_active > TIMEOUT_THRESHOLD):
                    print(f"⚠️ スレッド {idx+1} が停止またはフリーズ、再起動します")
                    if idx not in completed_threads:  # 完了していないスレッドだけ再起動
                        start_thread(idx, Lists[idx])
                    print(f"🔁 スレッド {idx+1} 再起動完了")

# --- メイン処理 ---
# ログファイル初期化（なければ作成）
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "thread_id", "loop_index", "url"])

threads = []

for idx, lst in enumerate(Lists):
    if not lst:
        continue

    while threading.active_count() - 1 >= MAX_THREADS:
        time.sleep(1)

    start_thread(idx, lst)

# 監視スレッド起動
monitor = threading.Thread(target=monitor_threads, daemon=True)
monitor.start()

# 初期スレッド終了を待機
for idx in range(len(Lists)):
    t = thread_objects.get(idx)
    if t:
        t.join()

print("🎉 全ブラウザ処理完了")