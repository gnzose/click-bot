import threading

# 実行対象モジュールの関数をインポート
from blog_clicker import start_detailed_clicker
from simple_clicker import start_simple_clicker

# --- 実行設定 ---
USE_PARALLEL = True  # 並列実行するならTrue（複数ドライバが立ち上がる）

if USE_PARALLEL:
    print("🔃 並列モードで実行します")
    t1 = threading.Thread(target=start_detailed_clicker)
    t2 = threading.Thread(target=start_simple_clicker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
else:
    print("▶️ 詳細ページ付きのクリック処理を実行")
    start_detailed_clicker()

    print("▶️ シンプルなループクリック処理を実行")
    start_simple_clicker()

print("✅ index.py: 全処理が完了しました")
