import requests
import threading
from datetime import datetime

# 各スレッドごとのIP履歴を記録（スレッドセーフ）
ip_history = {}
ip_lock = threading.Lock()

def get_current_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] IP取得失敗: {e}")
        return None

def log_ip_change(thread_name):
    current_ip = get_current_ip()

    if current_ip is None:
        return "0.0.0.0"

    with ip_lock:
        previous_ip = ip_history.get(thread_name)

        # 初回 or IP変更検出
        if previous_ip is None:
            print(f"[INFO] [{thread_name}] 開始時IP: {current_ip}（{datetime.now()}）")
        elif previous_ip != current_ip:
            print(f"[INFO] [{thread_name}] IP変更検出: {previous_ip} → {current_ip}（{datetime.now()}）")

        ip_history[thread_name] = current_ip

    return current_ip