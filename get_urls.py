##########################
# 有効URLのみ取得するコード#
#####出力：URLのリスト#####
##########################
import csv
import re
import glob  # glob モジュールをインポート

# CSVファイル名のパターン
CSV_FILE_PATTERN = '*.csv'
# URLリストを書き出すファイル名
OUTPUT_FILE = 'urls.py'

def extract_urls_from_csv(csv_file):
    """CSVファイルからURLを抽出する関数"""
    urls = set()  # 重複を避けるためにsetを使用
    try:
        with open(csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    # URLっぽい文字列を正規表現で検索
                    url_match = re.search(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', cell)
                    if url_match:
                        urls.add(url_match.group(0))
    except FileNotFoundError:
        print(f"エラー: ファイル '{csv_file}' が見つかりませんでした。")
    return sorted(list(urls)) # 重複を削除してソート

def write_urls_to_file(urls, output_file):
    """抽出したURLをファイルに指定の書式で書き出す関数"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('URL_LIST = [\n')
        for url in urls:
            f.write(f'"{url}",\n')
        f.write(']')
    print(f"URLリストを '{output_file}' に書き出しました。")

if __name__ == "__main__":
    csv_files = glob.glob(CSV_FILE_PATTERN)  # パターンに一致するファイル名のリストを取得
    all_extracted_urls = set()
    if csv_files:
        print("以下のCSVファイルを処理します:")
        for file in csv_files:
            print(f"- {file}")
            extracted_urls = extract_urls_from_csv(file)
            all_extracted_urls.update(extracted_urls)  # 複数のファイルからURLを収集
        sorted_urls = sorted(list(all_extracted_urls))
        write_urls_to_file(sorted_urls, OUTPUT_FILE)
    else:
        print(f"エラー: '{CSV_FILE_PATTERN}' に一致するCSVファイルが見つかりませんでした。")