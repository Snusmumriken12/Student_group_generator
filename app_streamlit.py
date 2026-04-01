from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

GROUP_EXPORTS_DIR = Path("group_exports")


# ---------- helpers ----------
def normalize_teacher_name(value: str) -> str:
    return " ".join(value.strip().split()).title()


def teacher_file_path(teacher_name: str) -> Path:
    safe_name = "_".join(teacher_name.strip().lower().split())
    return Path(f"classes_{safe_name}.json")

def create_id() -> str:
    return f"{int(datetime.now().timestamp() * 1000)}-{random.randint(100000, 999999)}"


def normalize_name(value: str) -> str:
    return " ".join(value.strip().split())


def shuffle_items(items: list[str]) -> list[str]:
    result = items[:]
    random.shuffle(result)
    return result


def format_groups(groups: list[list[str]], generated_at: str | None) -> str:
    if not groups:
        return "No groups generated yet."

    lines: list[str] = []
    if generated_at:
        lines.extend([f"Generated: {generated_at}", ""])

    for index, group in enumerate(groups, start=1):
        lines.append(f"Group {index}")
        for student in group:
            lines.append(f"- {student}")
        lines.append("")

    return "\n".join(lines).rstrip()


def ensure_data_shape(classes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Make older saves compatible with this version."""
    normalized: list[dict[str, Any]] = []
    for class_entry in classes:
        normalized.append(
            {
                "id": class_entry.get("id", create_id()),
                "name": class_entry.get("name", "Unnamed class"),
                "students": [
                    {
                        "id": student.get("id", create_id()),
                        "name": student.get("name", "Unnamed student"),
                        "present": bool(student.get("present", student.get("status", True))),
                    }
                    for student in class_entry.get("students", [])
                ],
                "groups": class_entry.get("groups", []),
                "generatedAt": class_entry.get("generatedAt"),
            }
        )
    return normalized


def load_classes(data_file: Path) -> list[dict[str, Any]]:
    if not data_file.exists():
        return []

    try:
        data = json.loads(data_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return ensure_data_shape(data)


def save_classes(classes: list[dict[str, Any]], data_file: Path) -> None:
    data_file.write_text(
        json.dumps(classes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_groups(class_name: str, groups: list[list[str]]) -> str:
    GROUP_EXPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_name = "_".join(class_name.lower().split())
    export_path = GROUP_EXPORTS_DIR / f"{safe_name}_groups.txt"
    export_path.write_text(format_groups(groups, timestamp), encoding="utf-8")
    return timestamp


def get_selected_class(classes: list[dict[str, Any]], selected_class_id: str | None) -> dict[str, Any] | None:
    if selected_class_id is None:
        return None

    for class_entry in classes:
        if class_entry["id"] == selected_class_id:
            return class_entry
    return None


def get_selected_student(selected_class: dict[str, Any] | None, selected_student_id: str | None) -> dict[str, Any] | None:
    if selected_class is None or selected_student_id is None:
        return None

    for student in selected_class["students"]:
        if student["id"] == selected_student_id:
            return student
    return None


def invalidate_groups(class_entry: dict[str, Any]) -> None:
    class_entry["groups"] = []
    class_entry["generatedAt"] = None


def sync_presence_from_widget(selected_class: dict[str, Any]) -> bool:
    changed = False
    for student in selected_class["students"]:
        key = f"present_{selected_class['id']}_{student['id']}"
        widget_value = st.session_state.get(key, bool(student["present"]))
        if bool(student["present"]) != bool(widget_value):
            student["present"] = bool(widget_value)
            changed = True
    return changed


# ---------- session bootstrap ----------
teacher_name_input = st.text_input(
    "Enter your name",
    placeholder="e.g. Linus G"
)

teacher_name = normalize_teacher_name(teacher_name_input)

if not teacher_name:
    st.title("Student Group Generator")
    st.caption("Enter your name to load your own classes.")
    st.stop()

DATA_FILE = teacher_file_path(teacher_name)

if "active_teacher" not in st.session_state:
    st.session_state["active_teacher"] = ""

if "classes" not in st.session_state:
    st.session_state["classes"] = []

if "selected_class_id" not in st.session_state:
    st.session_state["selected_class_id"] = None

if "selected_student_id" not in st.session_state:
    st.session_state["selected_student_id"] = None

if st.session_state["active_teacher"] != teacher_name:
    st.session_state["active_teacher"] = teacher_name
    st.session_state["classes"] = load_classes(DATA_FILE)
    st.session_state["selected_class_id"] = (
        st.session_state["classes"][0]["id"] if st.session_state["classes"] else None
    )
    st.session_state["selected_student_id"] = None

classes: list[dict[str, Any]] = st.session_state["classes"]
selected_class = get_selected_class(classes, st.session_state["selected_class_id"])
# ---------- header ----------
st.title("Student Group Generator")
st.caption("Manage classes, track attendance, and generate random groups.")

left_col, mid_col, right_col = st.columns([1, 1.4, 1.2], gap="large")


# ---------- classes ----------
with left_col:
    st.subheader("Classes")

    new_class_name = st.text_input("New class", placeholder="e.g. 5A", label_visibility="collapsed")
    if st.button("Add Class", use_container_width=True):
        name = normalize_name(new_class_name)
        if not name:
            st.error("Class name cannot be empty.")
        elif any(class_entry["name"].lower() == name.lower() for class_entry in classes):
            st.error("That class already exists.")
        else:
            class_entry = {
                "id": create_id(),
                "name": name,
                "students": [],
                "groups": [],
                "generatedAt": None,
            }
            classes.append(class_entry)
            st.session_state.selected_class_id = class_entry["id"]
            st.session_state.selected_student_id = None
            save_classes(classes, DATA_FILE)
            st.success(f'Class "{name}" added.')
            st.rerun()

    if classes:
        class_options = {class_entry["name"]: class_entry["id"] for class_entry in classes}
        current_name = next(
            (class_entry["name"] for class_entry in classes if class_entry["id"] == st.session_state.selected_class_id),
            classes[0]["name"],
        )
        picked_name = st.radio("Select class", list(class_options.keys()), index=list(class_options.keys()).index(current_name))
        st.session_state.selected_class_id = class_options[picked_name]
        selected_class = get_selected_class(classes, st.session_state.selected_class_id)

        with st.expander("Rename / delete class"):
            renamed_class = st.text_input(
                "Rename class to",
                value=selected_class["name"] if selected_class else "",
                key="rename_class_input",
            )
            rename_col, delete_col = st.columns(2)

            with rename_col:
                if st.button("Rename Class", use_container_width=True):
                    if selected_class is None:
                        st.error("Select a class first.")
                    else:
                        name = normalize_name(renamed_class)
                        if not name:
                            st.error("Class name cannot be empty.")
                        elif any(
                            class_entry["id"] != selected_class["id"] and class_entry["name"].lower() == name.lower()
                            for class_entry in classes
                        ):
                            st.error("That class name already exists.")
                        else:
                            old_name = selected_class["name"]
                            selected_class["name"] = name
                            save_classes(classes, DATA_FILE)
                            st.success(f'Renamed "{old_name}" to "{name}".')
                            st.rerun()

            with delete_col:
                if st.button("Delete Class", use_container_width=True):
                    if selected_class is None:
                        st.error("Select a class first.")
                    else:
                        deleted_id = selected_class["id"]
                        deleted_name = selected_class["name"]
                        st.session_state.classes = [c for c in classes if c["id"] != deleted_id]
                        classes = st.session_state.classes
                        st.session_state.selected_class_id = classes[0]["id"] if classes else None
                        st.session_state.selected_student_id = None
                        save_classes(classes, DATA_FILE)
                        st.success(f'Deleted class "{deleted_name}".')
                        st.rerun()
    else:
        st.info("No classes yet. Add one to get started.")


# ---------- students ----------
with mid_col:
    st.subheader("Students")

    if selected_class is None:
        st.info("Add or select a class to manage its roster.")
    else:
        total = len(selected_class["students"])
        present = sum(1 for student in selected_class["students"] if student["present"])
        st.caption(f"{present} present out of {total} student{'s' if total != 1 else ''}.")

        new_student_name = st.text_input("New student", placeholder="Student name", label_visibility="collapsed")
        if st.button("Add Student", use_container_width=True):
            name = normalize_name(new_student_name)
            if not name:
                st.error("Student name cannot be empty.")
            elif any(student["name"].lower() == name.lower() for student in selected_class["students"]):
                st.error("That student already exists.")
            else:
                selected_class["students"].append({"id": create_id(), "name": name, "present": True})
                invalidate_groups(selected_class)
                save_classes(classes, DATA_FILE)
                st.success(f'Student "{name}" added.')
                st.rerun()

        if selected_class["students"]:
            with st.expander("Select student", expanded=True):
                selected_student_name = st.radio(
                    "Select student",
                    [student["name"] for student in selected_class["students"]],
                    index=next(
                        (
                            idx
                            for idx, student in enumerate(selected_class["students"])
                            if student["id"] == st.session_state.selected_student_id
                        ),
                        0,
                    ),
                    horizontal=False,
                    label_visibility="collapsed",
                )

                for student in selected_class["students"]:
                    if student["name"] == selected_student_name:
                        st.session_state.selected_student_id = student["id"]
                        break

            with st.expander("Attendance", expanded=True):
                for student in selected_class["students"]:
                    key = f"present_{selected_class['id']}_{student['id']}"
                    if key not in st.session_state:
                        st.session_state[key] = bool(student["present"])

                    st.checkbox(student["name"], key=key)

                if st.button("Save attendance changes", use_container_width=True):
                    if sync_presence_from_widget(selected_class):
                        invalidate_groups(selected_class)
                        save_classes(classes, DATA_FILE)
                        st.success("Updated student status.")
                    else:
                        st.info("No attendance changes to save.")

            selected_student = get_selected_student(selected_class, st.session_state.selected_student_id)
            with st.expander("Rename / remove student"):
                rename_value = st.text_input(
                    "Rename student to",
                    value=selected_student["name"] if selected_student else "",
                    key="rename_student_input",
                )
                rename_col, remove_col = st.columns(2)

                with rename_col:
                    if st.button("Rename Student", use_container_width=True):
                        if selected_student is None:
                            st.error("Select a student first.")
                        else:
                            name = normalize_name(rename_value)
                            if not name:
                                st.error("Student name cannot be empty.")
                            elif any(
                                student["id"] != selected_student["id"] and student["name"].lower() == name.lower()
                                for student in selected_class["students"]
                            ):
                                st.error("That student already exists.")
                            else:
                                old_name = selected_student["name"]
                                selected_student["name"] = name
                                invalidate_groups(selected_class)
                                save_classes(classes, DATA_FILE)
                                st.success(f'Renamed "{old_name}" to "{name}".')
                                st.rerun()

                with remove_col:
                    if st.button("Remove Student", use_container_width=True):
                        if selected_student is None:
                            st.error("Select a student first.")
                        else:
                            deleted_name = selected_student["name"]
                            deleted_id = selected_student["id"]
                            selected_class["students"] = [
                                student for student in selected_class["students"] if student["id"] != deleted_id
                            ]
                            st.session_state.selected_student_id = (
                                selected_class["students"][0]["id"] if selected_class["students"] else None
                            )
                            invalidate_groups(selected_class)
                            save_classes(classes, DATA_FILE)
                            st.success(f'Removed "{deleted_name}".')
                            st.rerun()
        else:
            st.info("This class does not have any students yet.")


# ---------- groups ----------
with right_col:
    st.subheader("Group Settings")

    if selected_class is None:
        st.info("Select a class to generate groups.")
    else:
        group_mode_label = st.radio(
            "Grouping mode",
            ["Students per group", "Number of groups"],
            horizontal=False,
        )
        group_mode = "size" if group_mode_label == "Students per group" else "count"
        group_value = st.number_input(
            "Students per group" if group_mode == "size" else "Number of groups",
            min_value=1,
            step=1,
            value=2,
        )

        if st.button("Generate Groups", use_container_width=True):
            sync_presence_from_widget(selected_class)
            present_students = [student["name"] for student in selected_class["students"] if student["present"]]

            if not present_students:
                st.error("No present students in this class.")
            else:
                shuffled = shuffle_items(present_students)
                value = int(group_value)

                if group_mode == "size":
                    groups = [shuffled[index : index + value] for index in range(0, len(shuffled), value)]
                else:
                    if value > len(shuffled):
                        st.error("Cannot have more groups than present students.")
                        groups = None
                    else:
                        groups = [[] for _ in range(value)]
                        for index, student in enumerate(shuffled):
                            groups[index % value].append(student)

                if groups is not None:
                    selected_class["groups"] = groups
                    selected_class["generatedAt"] = save_groups(selected_class["name"], groups)
                    save_classes(classes, DATA_FILE)
                    st.success(f'Groups generated for "{selected_class["name"]}".')

        groups_text = format_groups(selected_class["groups"], selected_class["generatedAt"])
        st.text_area("Groups", value=groups_text, height=500)

        if selected_class["groups"]:
            st.download_button(
                "Download groups as TXT",
                data=groups_text.encode("utf-8"),
                file_name=f"{selected_class['name'].replace(' ', '_').lower()}_groups.txt",
                mime="text/plain",
                use_container_width=True,
            )
