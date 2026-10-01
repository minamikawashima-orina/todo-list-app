import datetime

import streamlit as st

from sheets import add_todo, delete_todo, get_todos, update_todo

# ページの基本設定（ブラウザのタブに表示されるタイトルなど）
st.set_page_config(page_title="Todoリスト", page_icon="📝")

# 今どのTodoを編集中か（スプレッドシートの行番号）を覚えておく
# None のときは「編集中のTodoなし」
if "editing_row" not in st.session_state:
    st.session_state.editing_row = None

# 今どのTodoを削除しようとしているか（確認画面を出すため）
# 行番号だけでなく、Todoの内容ごと覚えておく（別のTodoを消さないため）
if "deleting_todo" not in st.session_state:
    st.session_state.deleting_todo = None


def to_date(text):
    """「2026-10-05」のような文字を日付に変換する（変換できなければ None）"""
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return None


# ----------------------------------------
# タイトル
# ----------------------------------------
st.title("📝 Todoリスト")

# ----------------------------------------
# 入力フォーム
# ----------------------------------------
with st.form("todo_form"):
    title = st.text_input("タイトル")
    content = st.text_area("内容")
    # value=None にすると、最初は空欄になります（未入力チェックができるように）
    due = st.date_input("期日", value=None)
    submitted = st.form_submit_button("Todoを登録")

# ボタンが押されたときの処理
if submitted:
    # 未入力の項目を調べる（strip() で前後の空白を取り除いてからチェック）
    if title.strip() == "" or content.strip() == "" or due is None:
        st.error("タイトル、内容、期日をすべて入力してください")
    else:
        # Googleスプレッドシートに1行追加して保存
        add_todo(title, content, str(due))
        st.success("Todoを登録しました")

# ----------------------------------------
# 登録したTodoの一覧
# ----------------------------------------
st.header("登録したTodo")

# 編集・削除の直後なら、メッセージを1回だけ表示する
if st.session_state.get("message"):
    st.success(st.session_state.message)
    st.session_state.message = None
if st.session_state.get("error"):
    st.error(st.session_state.error)
    st.session_state.error = None

# スプレッドシートからTodoを読み込む
todos = get_todos()
# スプレッドシートは古い順に並んでいるので、reverse() で新しい順にする
todos.reverse()

for todo in todos:
    row = todo["row"]  # このTodoがスプレッドシートの何行目か

    # 枠線つきの箱の中に1件ずつ表示
    with st.container(border=True):
        if st.session_state.editing_row == row:
            # ---- 編集中：入力欄に今の内容を入れて表示 ----
            with st.form(f"edit_form_{row}"):
                new_title = st.text_input("タイトル", value=todo["title"])
                new_content = st.text_area("内容", value=todo["content"])
                new_due = st.date_input("期日", value=to_date(todo["due"]))
                save = st.form_submit_button("保存")
                cancel = st.form_submit_button("キャンセル")

            if save:
                if new_title.strip() == "" or new_content.strip() == "" or new_due is None:
                    st.error("タイトル、内容、期日をすべて入力してください")
                else:
                    # スプレッドシートの同じ行を書き換える
                    update_todo(row, new_title, new_content, str(new_due))
                    st.session_state.editing_row = None
                    st.session_state.message = "Todoを更新しました"
                    st.rerun()  # 画面を読み込み直して、最新の内容を表示
            if cancel:
                st.session_state.editing_row = None
                st.rerun()
        else:
            # ---- 通常の表示 ----
            st.subheader(todo["title"])
            st.write(todo["content"])
            st.caption(f"期日：{todo['due']}")

            if st.session_state.deleting_todo == todo:
                # ---- 削除の確認 ----
                st.warning("このTodoを削除しますか？")
                col1, col2 = st.columns(2)
                if col1.button("削除する", key=f"confirm_delete_{row}", type="primary"):
                    if delete_todo(st.session_state.deleting_todo):
                        st.session_state.message = "Todoを削除しました"
                    else:
                        st.session_state.message = None
                        st.session_state.error = "削除できませんでした。画面を再読み込みしてからもう一度お試しください"
                    st.session_state.deleting_todo = None
                    st.rerun()  # 画面を読み込み直して、最新の一覧を表示
                if col2.button("キャンセル", key=f"cancel_delete_{row}"):
                    st.session_state.deleting_todo = None
                    st.rerun()
            else:
                # key はボタンを区別するための名前（行番号を使って、どのTodoのボタンか分かるようにする）
                col1, col2 = st.columns(2)
                if col1.button("編集", key=f"edit_{row}"):
                    st.session_state.editing_row = row
                    st.session_state.deleting_todo = None
                    st.rerun()
                if col2.button("削除", key=f"delete_{row}"):
                    st.session_state.deleting_todo = todo
                    st.session_state.editing_row = None
                    st.rerun()
