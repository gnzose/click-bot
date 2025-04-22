###################################################
######### 有効URLを列ごとに取得するコード############
#####出力：リストの中にアカウントごとにリストでURL#####
###################################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
from gspread_formatting import get_effective_format
from gspread.utils import rowcol_to_a1
import time

# URL判定用の正規表現
URL_PATTERN = re.compile(r'https?://[^\s]+')

# Google Sheets 認証
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('sheets-bot-456316-baa9c2cc15b0.json', scope)
client = gspread.authorize(creds)

# スプレッドシートとワークシート指定
spreadsheet = client.open("お小遣い案件（ROFL）")
worksheet = spreadsheet.worksheet("2025/4分　依頼案件")

# 全データ取得
all_values = worksheet.get_all_values()

# === リクエスト制御のためのセットアップ ===
MIN_INTERVAL = 1.2  # リクエスト間隔（秒）
last_request_time = 0

def wait_if_needed():
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < MIN_INTERVAL:
        wait_time = MIN_INTERVAL - elapsed
        print(f"⏳ 次のリクエストまで {round(wait_time, 2)} 秒待機中...")
        time.sleep(wait_time)
    last_request_time = time.time()

# === 列ごとのURLリスト作成 ===
num_cols = max(len(row) for row in all_values)
Lists = [[] for _ in range(num_cols)]  # 各列のリストを準備

MAX_RETRIES = 3  # リトライ最大回数

for row_idx, row in enumerate(all_values, start=1):
    for col_idx, cell_value in enumerate(row, start=1):
        if URL_PATTERN.match(cell_value):
            cell_a1 = rowcol_to_a1(row_idx, col_idx)
            for attempt in range(MAX_RETRIES):
                try:
                    wait_if_needed()
                    fmt = get_effective_format(worksheet, cell_a1)
                    bg = fmt.backgroundColor

                    # 背景色が未設定 or 完全な白のみOK
                    if not bg or (round(bg.red, 2), round(bg.green, 2), round(bg.blue, 2)) == (1.0, 1.0, 1.0):
                        Lists[col_idx - 1].append(cell_value)
                    break  # 成功したらリトライ終了
                except Exception as e:
                    print(f"⚠️ {cell_a1} の背景色取得に失敗（{attempt+1}回目）: {e}")
                    time.sleep(2)  # 少し待って再試行

# 空リストは除外（列にURLが一つもない場合）
Lists = [lst for lst in Lists if lst]

# Pythonファイルとして出力
with open("urls_by_column.py", "w", encoding="utf-8") as f:
    f.write("# 列ごとに分割されたURLリスト\n")
    f.write("Lists = [\n")
    for lst in Lists:
        f.write("    [\n")
        for url in lst:
            f.write(f"        '{url}',\n")
        f.write("    ],\n")
    f.write("]\n")

# 経過時間の表示
elapsed_time = time.time() - last_request_time
print("✅ urls_by_column.py に列ごとのURLリストを出力しました（背景色が白or未設定のセルのみ）")
print(f"🕒 実行時間: {round(elapsed_time, 2)} 秒")
