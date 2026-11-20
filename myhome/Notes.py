from datetime import datetime

import streamlit as st

from storage import local_mode, read, update


NOTES_FILE = "notes.txt"
TODO_FILE = "todo.txt"


def legacy_notes(file):
    if not local_mode():
        return []
    try:
        with open(file, encoding="utf-8") as f:
            return [line.strip().split("|", 3) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def load(file):
    return read(file, lambda: legacy_notes(file))


def change(file, transform):
    update(file, lambda: legacy_notes(file), transform)


def edit(file, original, replacement=None):
    def apply(items):
        if original in items:
            index = items.index(original)
            if replacement is None:
                items.pop(index)
            else:
                items[index] = replacement
        return items

    change(file, apply)


def add(file, kind, text, status="pending"):
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    text = text.replace("|", "/").replace("\n", " ")
    status = status.replace("|", "/")
    change(file, lambda items: items + [[kind, now, status, text]])


def show_task(i, n):
    c1, c2 = st.columns([12, 1])
    done = c1.checkbox(n[3], value=(n[2] == "done"), key=f"c{i}")

    if done != (n[2] == "done"):
        edit(TODO_FILE, n, [n[0], n[1], "done" if done else "pending", n[3]])
        st.rerun()

    if c2.button("🗑️", key=f"d{i}"):
        edit(TODO_FILE, n)
        st.rerun()


def run():
    st.title("📝 Notes")
    notes = load(NOTES_FILE)
    tasks = load(TODO_FILE)
    tab1, tab2 = st.tabs(["📝 Notes", "✅ To-Do"])

    with tab1:
        with st.form("note_form", clear_on_submit=True):
            title = st.text_input("Title")
            body = st.text_area("Write a note")
            saved = st.form_submit_button("Save note")
            if saved and (title.strip() or body.strip()):
                add(NOTES_FILE, "THOUGHT", body, title.strip() or "Untitled")
                st.rerun()

        st.subheader("📚 History")
        thoughts = [(i, n) for i, n in enumerate(notes) if n[0] == "THOUGHT"]
        if not thoughts:
            st.caption("No notes yet.")

        for i, n in reversed(thoughts):
            name = "Untitled" if n[2] == "pending" else n[2]
            with st.expander(f"📄 {name}  •  {n[1]}"):
                st.write(n[3])
                if st.button("🗑️ Delete note", key=f"t{i}"):
                    edit(NOTES_FILE, n)
                    st.rerun()

        if notes:
            st.download_button(
                "⬇️ Download notes.txt", export(notes), file_name="notes.txt"
            )

    with tab2:
        with st.form("todo_form", clear_on_submit=True):
            task = st.text_input("New task")
            if st.form_submit_button("Add task") and task.strip():
                add(TODO_FILE, "TODO", task)
                st.rerun()

        todos = [(i, n) for i, n in enumerate(tasks) if n[0] == "TODO"]
        pending = [(i, n) for i, n in todos if n[2] != "done"]
        finished = [(i, n) for i, n in todos if n[2] == "done"]

        st.subheader(f"⏳ Pending ({len(pending)})")
        for i, n in pending:
            show_task(i, n)

        st.subheader(f"✅ Done ({len(finished)})")
        for i, n in finished:
            show_task(i, n)

        if tasks:
            st.download_button(
                "⬇️ Download todo.txt", export(tasks), file_name="todo.txt"
            )


def export(items):
    return "".join("|".join(item) + "\n" for item in items)
