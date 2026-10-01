import os

import gspread
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ----------------------------------------
# 設定の読み込み
# 秘密情報はコードに直接書かず、次のどちらかから読み込みます
#   ・Streamlit Cloud：Secrets（st.secrets）
#   ・ローカル：.env と credentials.json
# ----------------------------------------
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

# 使うタブ（ワークシート）の名前
WORKSHEET_NAME = "Todoリスト"

# スプレッドシートの読み書きだけを許可する設定
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def has_secrets():
    """Streamlit の Secrets にサービスアカウント情報が設定されているか調べる"""
    try:
        return "gcp_service_account" in st.secrets
    except FileNotFoundError:
        # secrets.toml が無いとき（ローカル環境）はここに来る
        return False


def get_worksheet():
    """Googleスプレッドシートの「Todoリスト」タブを取得する"""
    if has_secrets():
        # Streamlit Cloud：Secrets の情報でサービスアカウントとしてログイン
        credentials = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=SCOPES
        )
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
    else:
        # ローカル：credentials.json と .env の情報でログイン
        credentials = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        spreadsheet_id = SPREADSHEET_ID

    client = gspread.authorize(credentials)

    # スプレッドシートIDでファイルを開き、タブ名でシートを選ぶ
    spreadsheet = client.open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(WORKSHEET_NAME)


def get_todos():
    """スプレッドシートの2行目以降からTodoを取得する（古い順）"""
    worksheet = get_worksheet()
    rows = worksheet.get_all_values()  # 全部の行を取得（1行目は見出し）

    todos = []
    # [1:] で1行目（見出し）を飛ばす
    # start=2 で、行番号を2から数える（スプレッドシートの行番号と合わせるため）
    for row_number, row in enumerate(rows[1:], start=2):
        todos.append({"row": row_number, "title": row[0], "content": row[1], "due": row[2]})
    return todos


def add_todo(title, content, due):
    """新しいTodoをスプレッドシートの最終行に追加する"""
    worksheet = get_worksheet()
    worksheet.append_row([title, content, due])


def update_todo(row, title, content, due):
    """指定した行番号のTodoを書き換える（例：row=3 なら A3〜C3 を更新）"""
    worksheet = get_worksheet()
    worksheet.update(range_name=f"A{row}:C{row}", values=[[title, content, due]])


def delete_todo(todo):
    """Todoの行を削除する（削除できたら True、できなければ False を返す）"""
    row = todo["row"]

    # 1行目（見出し）は絶対に削除しない
    if row < 2:
        return False

    worksheet = get_worksheet()

    # 安全確認：今その行に入っている内容が、削除したいTodoと同じかチェックする
    # （画面を開いた後にスプレッドシートが変わっていたら、別のTodoを消さないように中止）
    current = worksheet.row_values(row) + ["", "", ""]  # 空欄があっても3つそろうように補う
    if current[:3] != [todo["title"], todo["content"], todo["due"]]:
        return False

    worksheet.delete_rows(row)
    return True


# ----------------------------------------
# 接続テスト
# ターミナルで「python3 sheets.py」と実行したときだけ動きます
# ----------------------------------------
if __name__ == "__main__":
    worksheet = get_worksheet()
    print("接続に成功しました！")
    print("1行目（見出し）:", worksheet.row_values(1))
