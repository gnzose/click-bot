########################
#アフィリリンクをクリック#
########################
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

from ip_checker import get_current_ip, log_ip_change
from user_agents import USER_AGENTS
from urls_by_column import Lists  # ← ここが変更点

# --- ランダムなUser-Agentを設定 ---
selected_user_agent = random.choice(USER_AGENTS)
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={selected_user_agent}")
# options.add_argument("--headless")  # 非表示モード（必要なら）

# --- ドライバー設定 ---
service = Service("C:/Users/gnzos/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(30)

# IPログ初期化
previous_ip = log_ip_change(None)

# --- 人間っぽいスクロール関数 ---
def human_scroll(driver, min_height=200, max_height=600, min_step=50, max_step=100):
    scroll_height = random.randint(min_height, max_height)
    scroll_step = random.randint(min_step, max_step)
    scroll_delay = random.uniform(0.05, 0.15)
    current_scroll_pos = 0
    while current_scroll_pos < scroll_height:
        scroll_amount = min(scroll_step, scroll_height - current_scroll_pos)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        current_scroll_pos += scroll_amount
        time.sleep(scroll_delay)

# --- URLアクセス関数（リトライ付き） ---
def safe_get(driver, url, retries=2):
    for i in range(retries):
        try:
            driver.get(url)
            return True
        except (TimeoutException, WebDriverException) as e:
            print(f"[Retry {i+1}] アクセス失敗：{url} → {e}")
            time.sleep(2)
    print(f"[ERROR] 最終的にアクセス失敗：{url}")
    return False

# === 30〜45周、全体のリストをループ ===
total_rounds = random.randint(30, 45)
print(f"🔁 全体を {total_rounds} 回ループします")

try:
    for round_idx in range(total_rounds):
        print(f"---- 🌀 {round_idx + 1}周目 ----")
        for lst in Lists:
            for url in lst:
                try:
                    previous_ip = log_ip_change(previous_ip)

                    if not safe_get(driver, url):
                        continue

                    # 軽いスクロール
                    human_scroll(driver)
                    time.sleep(random.uniform(1, 2.5))

                    # 記事内リンクをクリック
                    try:
                        entry_content = driver.find_element(By.CSS_SELECTOR, "div.entry-content.cf")
                        first_link = entry_content.find_element(By.TAG_NAME, "a")
                        link_url = first_link.get_attribute("href")

                        if link_url:
                            print(f"→ 詳細ページへ移動中: {link_url}")
                            if not safe_get(driver, link_url):
                                continue

                            # 詳細ページスクロール
                            human_scroll(driver, min_height=300, max_height=1000, min_step=80, max_step=150)
                            time.sleep(random.uniform(1.5, 3.0))
                        else:
                            print("⚠ 記事リンクが見つかりませんでした")

                    except NoSuchElementException:
                        print(f"[ERROR] 要素が見つかりません：{url}")
                    except StaleElementReferenceException:
                        print(f"[ERROR] 要素が無効です（ページ遷移後）：{url}")
                    except Exception as e:
                        print(f"[ERROR] 記事リンク取得中の例外：{url} → {e}")

                except Exception as outer_e:
                    print(f"[ERROR] URL処理中の予期せぬ例外：{url} → {outer_e}")
                    continue

finally:
    driver.quit()
    print("✅ 全処理完了。ドライバを終了しました。")
