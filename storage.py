from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
CLASSES_FILE = BASE_DIR / "classes.json"
STUDENTS_FILE = BASE_DIR / "students.json"


def _create_id() -> str:
    return f"{int(datetime.now().timestamp() * 1000)}-{random.randint(100000, 999999)}"


def _normalize_name(value: str) -> str:
    return " ".join(str(value).strip().split())


def _upgrade_classes(raw_data: Any) -> list[dict[str, Any]]:
    """Convert old classes.json formats into the GUI format.

    Supported old format:
    {
        "4A": [
            {"name": "Alice", "status": true}
        ]
    }
    """
    if isinstance(raw_data, list):
        upgraded: list[dict[str, Any]] = []

        for class_entry in raw_data:
            if not isinstance(class_entry, dict):
                continue

            class_name = _normalize_name(class_entry.get("name", "")) or "Unnamed Class"
            students_raw = class_entry.get("students", [])
            upgraded_students: list[dict[str, Any]] = []

            if isinstance(students_raw, list):
                for student in students_raw:
                    if not isinstance(student, dict):
                        continue
                    student_name = _normalize_name(student.get("name", ""))
                    if not student_name:
                        continue
                    upgraded_students.append(
                        {
                            "id": str(student.get("id") or _create_id()),
                            "name": student_name,
                            "present": bool(student.get("present", student.get("status", True))),
                        }
                    )

            upgraded.append(
                {
                    "id": str(class_entry.get("id") or _create_id()),
                    "name": class_name,
                    "students": upgraded_students,
                    "groups": class_entry.get("groups", []),
                    "generatedAt": class_entry.get("generatedAt"),
                }
            )

        return upgraded

    if isinstance(raw_data, dict):
        upgraded = []
        for class_name, students_raw in raw_data.items():
            students: list[dict[str, Any]] = []
            if isinstance(students_raw, list):
                for student in students_raw:
                    if not isinstance(student, dict):
                        continue
                    student_name = _normalize_name(student.get("name", ""))
                    if not student_name:
                        continue
                    students.append(
                        {
                            "id": _create_id(),
                            "name": student_name,
                            "present": bool(student.get("present", student.get("status", True))),
                        }
                    )

            upgraded.append(
                {
                    "id": _create_id(),
                    "name": _normalize_name(class_name) or "Unnamed Class",
                    "students": students,
                    "groups": [],
                    "generatedAt": None,
                }
            )
        return upgraded

    return []


def save_students(student_list: list[dict[str, Any]]) -> None:
    with STUDENTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(student_list, file, indent=4, ensure_ascii=False)


def load_students() -> list[dict[str, Any]]:
    try:
        with STUDENTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    return data if isinstance(data, list) else []


def save_classes(classes: list[dict[str, Any]]) -> None:
    with CLASSES_FILE.open("w", encoding="utf-8") as file:
        json.dump(classes, file, indent=4, ensure_ascii=False)



def load_classes() -> list[dict[str, Any]]:
    try:
        with CLASSES_FILE.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)
    except FileNotFoundError:
        return []

    classes = _upgrade_classes(raw_data)

    # Auto-save once after upgrade so the file matches the GUI's expected format.
    if raw_data != classes:
        save_classes(classes)

    return classes



def save_groups(class_id_or_name: str, groups: list[list[str]]) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_name = _normalize_name(class_id_or_name).replace(" ", "_") or "class"
    filename = BASE_DIR / f"{safe_name}_groups.json"

    data = {
        "class": class_id_or_name,
        "groups": groups,
        "generatedAt": timestamp,
    }

    with filename.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return timestamp
