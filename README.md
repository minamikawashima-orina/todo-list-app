# 📝 Todoリスト

ブラウザからTodoを **登録・表示・編集・削除** できる、シンプルなWebアプリです。
Python と Streamlit で作成し、データの保存先として **Googleスプレッドシート** を使用しています。
アプリを閉じても、登録したTodoはスプレッドシートに残ります。

---

## 主な機能

- **Todoの登録**：タイトル・内容・期日を入力して登録（すべて入力必須）
- **Todoの一覧表示**：登録したTodoを一覧で表示
- **新しいTodoを上に表示**：新しく登録したものほど上に表示
- **Todoの編集**：「編集」ボタンから内容を変更して保存
- **Todoの削除**：「削除」ボタンを押すと確認が表示され、「削除する」で確定
- **Googleスプレッドシートへの保存・読み込み**：登録・編集・削除の結果はスプレッドシートに反映

---

## 使用技術

| 技術 | 用途 |
|---|---|
| Python | プログラミング言語 |
| Streamlit | Python だけでWeb画面を作るためのライブラリ |
| Googleスプレッドシート | Todoデータの保存先 |
| gspread | Python からスプレッドシートを読み書きするライブラリ |
| google-auth | サービスアカウントでGoogleにログイン（認証）するライブラリ |
| python-dotenv | `.env` ファイルから設定を読み込むライブラリ |

---

## データの流れ

```
ブラウザ  →  Streamlit（app.py）  →  Googleスプレッドシート
（入力・表示）   （画面と処理）     sheets.py 経由で読み書き
```

1. ブラウザでTodoを入力し、ボタンを押します
2. Streamlit（`app.py`）が入力内容をチェックします
3. `sheets.py` が Google Sheets API を使って、スプレッドシートに保存・更新・削除します
4. 最新のTodoをスプレッドシートから読み込み、ブラウザに表示します

---

## ファイル構成

```
.
├── app.py            # 画面と操作（登録・一覧・編集・削除）
├── sheets.py         # Googleスプレッドシートとの接続・読み書き
├── requirements.txt  # 必要なライブラリの一覧
├── .gitignore        # GitHubに公開しないファイルの指定
├── .env              # 設定（スプレッドシートIDなど）※GitHubには含まれません
└── credentials.json  # サービスアカウントの認証情報 ※GitHubには含まれません
```

---

## セキュリティ

秘密情報はコードに直接書かず、別ファイルで管理しています。

- `.env`（スプレッドシートIDなどの設定）
- `credentials.json`（サービスアカウントの認証情報）

これらは `.gitignore` に登録しているため、**GitHubには公開されません**。
このリポジトリをダウンロードした場合は、自分で用意する必要があります（下記「起動方法」参照）。

---

## 起動方法

### 1. 必要なもの

- Python 3.9 以上
- Googleアカウント
- Google Cloud のサービスアカウント（Google Sheets API を有効にしたもの）

### 2. リポジトリをダウンロード

```bash
git clone https://github.com/minamikawashima-orina/todo-list-app.git
cd todo-list-app
```

### 3. ライブラリをインストール

```bash
pip3 install -r requirements.txt
```

### 4. Googleスプレッドシートを準備

1. 新しいスプレッドシートを作成します（ファイル名は自由）
2. 画面下の **タブ名** を `Todoリスト` に変更します
3. 1行目に見出しを入力します

   | A1 | B1 | C1 |
   |---|---|---|
   | タイトル | 内容 | 期日 |

4. 「共有」から、サービスアカウントのメールアドレスを **編集者** として追加します

### 5. 認証情報と設定ファイルを用意

1. Google Cloud でダウンロードしたサービスアカウントのJSONキーを、`credentials.json` という名前でこのフォルダに置きます
2. このフォルダに `.env` ファイルを作成し、以下のように書きます

```
SPREADSHEET_ID=ここにスプレッドシートIDを入力
GOOGLE_CREDENTIALS_PATH=credentials.json
```

> スプレッドシートIDは、スプレッドシートのURL
> `https://docs.google.com/spreadsheets/d/【この部分】/edit` です。

### 6. 接続テスト（任意）

```bash
python3 sheets.py
```

「接続に成功しました！」と表示されればOKです。

### 7. アプリを起動

```bash
streamlit run app.py
```

ブラウザが自動で開き、アプリが表示されます（開かない場合は `http://localhost:8501` にアクセス）。

---

## 今回の課題で学んだこと

- **Streamlit**：Python だけで、入力フォームやボタンのあるWeb画面を作れること。ボタンを押すたびにコードが上から実行し直される仕組みと、`st.session_state` で状態を覚えておく方法
- **Googleスプレッドシートとの連携**：Google Cloud でAPIを有効にし、サービスアカウントを作ってスプレッドシートを共有することで、Python から読み書きできること
- **正しい行を操作する工夫**：画面の表示順とスプレッドシートの行の順番が違っても、行番号を覚えておくことで正しいTodoを編集・削除できること。削除前に中身を確認して、別の行を消さないようにすること
- **環境変数・秘密情報の管理**：認証情報やIDをコードに直接書かず、`.env` や `credentials.json` に分け、`.gitignore` でGitHubに公開しないようにすること
- **GitHub**：`git add` → `git status` で確認 → `git commit` → `git push` の流れで、コードを安全に公開すること
