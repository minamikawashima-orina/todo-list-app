import datetime

import streamlit as st

from sheets import PRIORITIES, add_todo, delete_todo, get_todos, update_todo

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


# 一覧で重要度を見分けやすくするためのマーク
PRIORITY_ICONS = {"高": "🔴", "中": "🟡", "低": "🔵"}


def priority_label(priority):
    """重要度を「🔴 高」のような表示用の文字にする（未入力のTodoは「未設定」）"""
    if priority in PRIORITY_ICONS:
        return f"{PRIORITY_ICONS[priority]} {priority}"
    return "未設定"


def priority_index(priority):
    """選択欄の初期位置を決める（重要度が未入力・不正なTodoは「中」を選んだ状態にする）"""
    if priority in PRIORITIES:
        return PRIORITIES.index(priority)
    return PRIORITIES.index("中")


# 並び替えの選択肢
SORT_OPTIONS = ["新しい順", "期日が近い順", "重要度が高い順"]


def sort_todos(todos, sort_order):
    """Todoを選んだ順番に並び替える（画面の表示順だけ変える。スプレッドシートはそのまま）

    todos は「新しい順」に並んだリストを受け取る。
    sorted() は同じ値どうしの順番を変えないので、期日や重要度が同じTodoは新しい順のまま並ぶ。
    """
    if sort_order == "期日が近い順":
        # 期日が早いものを上に。期日が未設定・読めないTodoは最後にする
        def due_key(todo):
            due = to_date(todo["due"])
            return (due is None, due or datetime.date.max)

        return sorted(todos, key=due_key)

    if sort_order == "重要度が高い順":
        # 高→中→低→未設定 の順にする（未設定は PRIORITIES に無いので一番後ろ）
        def priority_key(todo):
            if todo["priority"] in PRIORITIES:
                return PRIORITIES.index(todo["priority"])
            return len(PRIORITIES)

        return sorted(todos, key=priority_key)

    # 「新しい順」はそのまま
    return todos


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
    # 重要度は「高・中・低」から選ぶ（最初は「中」を選んだ状態）
    priority = st.radio("重要度", PRIORITIES, index=priority_index("中"), horizontal=True)
    submitted = st.form_submit_button("Todoを登録")

# ボタンが押されたときの処理
if submitted:
    # 未入力の項目を調べる（strip() で前後の空白を取り除いてからチェック）
    if title.strip() == "" or content.strip() == "" or due is None:
        st.error("タイトル、内容、期日をすべて入力してください")
    else:
        # Googleスプレッドシートに1行追加して保存
        add_todo(title, content, str(due), priority)
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

# 並び替え方法を選ぶ（横並びのボタンなので、スマートフォンでもタップしやすい）
# key をつけると、編集・削除で画面が読み込み直されても選んだ並び順が保たれる
sort_order = st.radio("並び替え", SORT_OPTIONS, horizontal=True, key="sort_order")

# スプレッドシートからTodoを読み込む
todos = get_todos()
# スプレッドシートは古い順に並んでいるので、reverse() で新しい順にする
todos.reverse()
# 選んだ並び順に並び替える（スプレッドシートのデータの順番は変えない）
todos = sort_todos(todos, sort_order)

for todo in todos:
    row = todo["row"]  # このTodoがスプレッドシートの何行目か

    # 枠線つきの箱の中に1件ずつ表示
    with st.container(border=True):
        if st.session_state.editing_row == row:
            # ---- 編集中：入力欄に今の内容を入れて表示 ----
            with st.form(f"edit_form_{row}"):
                # 入力欄の key にも行番号を使う（表示位置ではなく、このTodo専用の入力欄にする）
                new_title = st.text_input("タイトル", value=todo["title"], key=f"edit_title_{row}")
                new_content = st.text_area("内容", value=todo["content"], key=f"edit_content_{row}")
                new_due = st.date_input("期日", value=to_date(todo["due"]), key=f"edit_due_{row}")
                new_priority = st.radio(
                    "重要度",
                    PRIORITIES,
                    index=priority_index(todo["priority"]),
                    horizontal=True,
                    key=f"edit_priority_{row}",
                )
                save = st.form_submit_button("保存", key=f"save_{row}")
                cancel = st.form_submit_button("キャンセル", key=f"cancel_edit_{row}")

            if save:
                if new_title.strip() == "" or new_content.strip() == "" or new_due is None:
                    st.error("タイトル、内容、期日をすべて入力してください")
                else:
                    # スプレッドシートの同じ行を書き換える
                    update_todo(row, new_title, new_content, str(new_due), new_priority)
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
            st.caption(f"重要度：{priority_label(todo['priority'])}　｜　期日：{todo['due']}")

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
