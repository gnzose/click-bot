import csv
from collections import defaultdict

log_file = "progress_log.csv"  # ファイル名を修正済みの前提
completion_threshold = 560   # これ以上なら完了とみなす

# スレッドごとのアクセス回数をカウント
thread_counts = defaultdict(int)

with open(log_file, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # ヘッダー行をスキップ
    for row in reader:
        if len(row) >= 2:  # 2列目があることを確認
            try:
                thread_id = int(row[1])  # スレッドIDを取得
                thread_counts[thread_id] += 1
            except ValueError:
                continue  # 数字に変換できない場合はスキップ

# スレッドごとの進捗確認
for thread_id in sorted(thread_counts.keys()):
    count = thread_counts[thread_id]
    if count >= completion_threshold:
        print(f"スレッド{thread_id}: {count} ✅ 完了")
    else:
        print(f"スレッド{thread_id}: {count} ❌ 未完了（あと {completion_threshold - count}）")
