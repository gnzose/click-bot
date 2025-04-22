import os
import random
import time
from datetime import datetime

# ランダムな実行時間を生成
def get_random_time():
    hour = random.randint(0, 23)  # 0〜23時間
    minute = random.randint(0, 59)  # 0〜59分
    return f"{hour:02}:{minute:02}"  # "HH:MM" の形式で返す

# 既存のタスクを削除
def delete_existing_task():
    os.system('SCHTASKS /DELETE /TN "MyRandomTask" /F')

# スケジュールタスクの作成
def schedule_task():
    random_time = get_random_time()
    
    # 既存のタスクを削除
    delete_existing_task()
    
    # タスクスケジューラのコマンド
    task_command = f'SCHTASKS /CREATE /SC DAILY /TN "MyRandomTask" /TR "python C:\\Users\\gnzos\\OneDrive\\デスクトップ\\Project\\click\\blog_clicker.py" /ST {random_time} /F'
    
    # タスクを作成
    os.system(task_command)
    print(f'📅 スクリプトは毎日 {random_time} に実行予定')

# メイン関数
if __name__ == '__main__':
    schedule_task()
