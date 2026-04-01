from __future__ import annotations

import random
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog
from typing import Any
import streamlit as st
import pandas as pd
import numpy as np
from storage import load_classes, save_classes, save_groups

st.title('Uber pickups in NYC')

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


class StudentGroupGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Student Group Generator")
        self.root.geometry("1500x900")
        self.root.minsize(1200, 760)

        self.classes: list[dict[str, Any]] = load_classes()
        self.selected_class_id: str | None = self.classes[0]["id"] if self.classes else None
        self.selected_student_id: str | None = None
        self.student_vars: dict[str, tk.BooleanVar] = {}
        self.feedback_after_id: str | None = None

        self.group_mode = tk.StringVar(value="size")
        self.new_class_var = tk.StringVar()
        self.new_student_var = tk.StringVar()
        self.group_value_var = tk.StringVar()

        self.build_ui()
        self.refresh_class_list()
        self.refresh_student_list()
        self.refresh_groups_output()

    def build_ui(self) -> None:
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_columnconfigure(2, weight=1)

        header = tk.Frame(self.root, padx=16, pady=12)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_block = tk.Frame(header)
        title_block.grid(row=0, column=0, sticky="w")

        tk.Label(title_block, text="Student Group Generator", font=("Arial", 20, "bold")).pack(anchor="w")
        tk.Label(
            title_block,
            text="Manage classes, track attendance, and generate random groups.",
            fg="#555555",
        ).pack(anchor="w", pady=(2, 0))

        self.feedback_label = tk.Label(header, text="", fg="#15803d", font=("Arial", 11, "bold"))
        self.feedback_label.grid(row=0, column=1, sticky="e")

        main = tk.Frame(self.root, padx=12, pady=12)
        main.grid(row=1, column=0, columnspan=3, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=0)
        main.grid_columnconfigure(1, weight=1)
        main.grid_columnconfigure(2, weight=1)

        self.build_class_panel(main)
        self.build_student_panel(main)
        self.build_group_panel(main)

    def build_class_panel(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bd=2, relief="groove", padx=10, pady=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame.grid_rowconfigure(3, weight=1)

        tk.Label(frame, text="Classes", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")

        entry_row = tk.Frame(frame)
        entry_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        entry_row.grid_columnconfigure(0, weight=1)

        self.class_entry = tk.Entry(
        entry_row,
        textvariable=self.new_class_var,
        bg="#808588",   # light gray
        fg="black",
        insertbackground="black"  # cursor color (otherwise invisible lol)
        )
        self.class_entry.grid(row=0, column=0, sticky="ew")
        self.class_entry.bind("<Return>", lambda event: self.add_class())

        tk.Button(entry_row, text="Add Class", command=self.add_class).grid(row=0, column=1, padx=(8, 0))

        button_row = tk.Frame(frame)
        button_row.grid(row=2, column=0, sticky="ew", pady=(10, 8))
        button_row.grid_columnconfigure((0, 1), weight=1)

        tk.Button(button_row, text="Rename Class", command=self.rename_class).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        tk.Button(button_row, text="Delete Class", command=self.delete_class).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        self.class_listbox = tk.Listbox(frame, height=20, activestyle="none")
        self.class_listbox.grid(row=3, column=0, sticky="nsew")
        self.class_listbox.bind("<<ListboxSelect>>", self.on_class_select)

        self.class_empty_label = tk.Label(
            frame,
            text="No classes yet. Add one to get started.",
            fg="#666666",
            justify="left",
            wraplength=220,
        )
        self.class_empty_label.grid(row=3, column=0, sticky="nsew")
        self.class_empty_label.lower(self.class_listbox)

    def build_student_panel(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bd=2, relief="groove", padx=10, pady=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=10)
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tk.Label(frame, text="Students", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")

        self.student_summary_label = tk.Label(frame, text="Select a class to manage its roster.", fg="#555555")
        self.student_summary_label.grid(row=1, column=0, sticky="w", pady=(2, 8))

        entry_row = tk.Frame(frame)
        entry_row.grid(row=2, column=0, sticky="ew")
        entry_row.grid_columnconfigure(0, weight=1)

        self.student_entry = tk.Entry(
        entry_row,
        textvariable=self.new_student_var,
        bg="#808588",
        fg="black",
        insertbackground="black"
    )
        self.student_entry.grid(row=0, column=0, sticky="ew")
        self.student_entry.bind("<Return>", lambda event: self.add_student())

        tk.Button(entry_row, text="Add Student", command=self.add_student).grid(row=0, column=1, padx=(8, 0))

        button_row = tk.Frame(frame)
        button_row.grid(row=3, column=0, sticky="ew", pady=(10, 8))
        button_row.grid_columnconfigure((0, 1), weight=1)

        tk.Button(button_row, text="Rename Student", command=self.rename_student).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        tk.Button(button_row, text="Remove Student", command=self.remove_student).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        list_container = tk.Frame(frame)
        list_container.grid(row=4, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        self.student_canvas = tk.Canvas(list_container, highlightthickness=0)
        self.student_scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.student_canvas.yview)
        self.students_frame = tk.Frame(self.student_canvas)

        self.students_frame.bind(
            "<Configure>",
            lambda event: self.student_canvas.configure(scrollregion=self.student_canvas.bbox("all")),
        )

        self.student_canvas.create_window((0, 0), window=self.students_frame, anchor="nw")
        self.student_canvas.configure(yscrollcommand=self.student_scrollbar.set)

        self.student_canvas.grid(row=0, column=0, sticky="nsew")
        self.student_scrollbar.grid(row=0, column=1, sticky="ns")

        self.student_canvas.bind("<Enter>", self.bind_student_mousewheel)
        self.student_canvas.bind("<Leave>", self.unbind_student_mousewheel)
        self.students_frame.bind("<Enter>", self.bind_student_mousewheel)
        self.students_frame.bind("<Leave>", self.unbind_student_mousewheel)

    def bind_student_mousewheel(self, _event: tk.Event | None = None) -> None:
        self.student_canvas.bind_all("<MouseWheel>", self.on_student_mousewheel)
        self.student_canvas.bind_all("<Button-4>", self.on_student_mousewheel)
        self.student_canvas.bind_all("<Button-5>", self.on_student_mousewheel)

    def unbind_student_mousewheel(self, _event: tk.Event | None = None) -> None:
        self.student_canvas.unbind_all("<MouseWheel>")
        self.student_canvas.unbind_all("<Button-4>")
        self.student_canvas.unbind_all("<Button-5>")

    def on_student_mousewheel(self, event: tk.Event) -> str:
        if getattr(event, "num", None) == 4:
            self.student_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.student_canvas.yview_scroll(1, "units")
        elif getattr(event, "delta", 0):
            step = -1 if event.delta > 0 else 1
            self.student_canvas.yview_scroll(step, "units")
        return "break"

    def build_group_panel(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bd=2, relief="groove", padx=10, pady=10)
        frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tk.Label(frame, text="Group Settings", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")

        modes = tk.Frame(frame)
        modes.grid(row=1, column=0, sticky="w", pady=(10, 0))

        tk.Radiobutton(
            modes,
            text="Students per group",
            value="size",
            variable=self.group_mode,
            command=self.update_group_label,
        ).pack(anchor="w")
        tk.Radiobutton(
            modes,
            text="Number of groups",
            value="count",
            variable=self.group_mode,
            command=self.update_group_label,
        ).pack(anchor="w", pady=(4, 0))

        input_row = tk.Frame(frame)
        input_row.grid(row=2, column=0, sticky="ew", pady=(10, 8))
        input_row.grid_columnconfigure(0, weight=1)

        self.group_value_label = tk.Label(input_row, text="Students per group:")
        self.group_value_label.grid(row=0, column=0, sticky="w")

        self.group_value_entry = tk.Entry(
    input_row,
    textvariable=self.group_value_var,
    width=12,
    bg="#808588",
    fg="black",
    insertbackground="black"
)
        self.group_value_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        tk.Button(input_row, text="Generate Groups", command=self.generate_groups).grid(
            row=1, column=1, padx=(8, 0), pady=(4, 0)
        )

        output_frame = tk.Frame(frame)
        output_frame.grid(row=3, column=0, sticky="nsew")
        
        output_frame.grid_columnconfigure(0, weight=1)

        tk.Label(output_frame, text="Groups", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")

        text_container = tk.Frame(output_frame)
        text_container.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        output_frame.grid_rowconfigure(1, weight=1)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        self.groups_text = tk.Text(text_container, wrap="word", height=18, font=("Consolas", 11))
        groups_scrollbar = tk.Scrollbar(text_container, orient="vertical", command=self.groups_text.yview)
        self.groups_text.configure(yscrollcommand=groups_scrollbar.set)

        self.groups_text.grid(row=0, column=0, sticky="nsew")
        groups_scrollbar.grid(row=0, column=1, sticky="ns")

        tk.Button(output_frame, text="Clear Output", command=self.clear_groups_output).grid(
            row=2, column=0, sticky="e", pady=(8, 0)
        )

    def get_selected_class(self) -> dict[str, Any] | None:
        if self.selected_class_id is None:
            return None

        for class_entry in self.classes:
            if class_entry["id"] == self.selected_class_id:
                return class_entry

        return None

    def get_selected_student(self) -> dict[str, Any] | None:
        selected_class = self.get_selected_class()
        if selected_class is None or self.selected_student_id is None:
            return None

        for student in selected_class["students"]:
            if student["id"] == self.selected_student_id:
                return student

        return None

    def invalidate_groups(self, class_entry: dict[str, Any]) -> None:
        class_entry["groups"] = []
        class_entry["generatedAt"] = None

    def show_feedback(self, message: str, tone: str = "success") -> None:
        color = "#15803d" if tone == "success" else "#b91c1c"
        self.feedback_label.configure(text=message, fg=color)

        if self.feedback_after_id is not None:
            self.root.after_cancel(self.feedback_after_id)

        self.feedback_after_id = self.root.after(4000, self.clear_feedback)

    def clear_feedback(self) -> None:
        self.feedback_label.configure(text="")
        self.feedback_after_id = None

    def update_group_label(self) -> None:
        if self.group_mode.get() == "size":
            self.group_value_label.configure(text="Students per group:")
        else:
            self.group_value_label.configure(text="Number of groups:")

    def refresh_class_list(self) -> None:
        self.class_listbox.delete(0, tk.END)

        for class_entry in self.classes:
            self.class_listbox.insert(tk.END, class_entry["name"])

        if not self.classes:
            self.class_listbox.grid_remove()
            self.class_empty_label.grid()
            self.selected_class_id = None
            return

        self.class_empty_label.grid_remove()
        self.class_listbox.grid()

        selected_index = None
        for index, class_entry in enumerate(self.classes):
            if class_entry["id"] == self.selected_class_id:
                selected_index = index
                break

        if selected_index is None:
            selected_index = 0
            self.selected_class_id = self.classes[0]["id"]

        self.class_listbox.selection_clear(0, tk.END)
        self.class_listbox.selection_set(selected_index)
        self.class_listbox.activate(selected_index)
        self.class_listbox.see(selected_index)

    def refresh_student_list(self) -> None:
        for widget in self.students_frame.winfo_children():
            widget.destroy()

        self.student_vars = {}

        selected_class = self.get_selected_class()
        if selected_class is None:
            self.student_summary_label.configure(text="Select a class to manage its roster.")
            placeholder = tk.Label(
                self.students_frame,
                text="Add a class to start building a roster.",
                fg="#666666",
                wraplength=420,
                justify="left",
            )
            placeholder.pack(anchor="nw", padx=4, pady=4)
            self.selected_student_id = None
            self.refresh_groups_output()
            return

        total = len(selected_class["students"])
        present = sum(1 for student in selected_class["students"] if student["present"])
        self.student_summary_label.configure(text=f"{present} present out of {total} student{'s' if total != 1 else ''}.")

        if not selected_class["students"]:
            placeholder = tk.Label(
                self.students_frame,
                text="This class does not have any students yet.",
                fg="#666666",
                wraplength=420,
                justify="left",
            )
            placeholder.pack(anchor="nw", padx=4, pady=4)
            self.selected_student_id = None
            self.refresh_groups_output()
            return

        selected_exists = False

        for student in selected_class["students"]:
            if student["id"] == self.selected_student_id:
                selected_exists = True

            active = student["id"] == self.selected_student_id
            bg = "#1f2937" if active else "#374151"

            row = tk.Frame(self.students_frame, bg=bg, bd=1, relief="solid", padx=8, pady=6)
            row.pack(fill="x", padx=4, pady=3)

            var = tk.BooleanVar(value=bool(student["present"]))
            self.student_vars[student["id"]] = var

            check = tk.Checkbutton(
                row,
                variable=var,
                command=lambda sid=student["id"], value=var: self.update_status(sid, value),
                bg=bg,
                activebackground=bg,
            )
            check.pack(side="left")

            text_block = tk.Frame(row, bg=bg)
            text_block.pack(side="left", fill="x", expand=True, padx=(8, 0))

            name_label = tk.Label(text_block, text=student["name"], bg=bg, anchor="w", font=("Arial", 11, "bold"))
            name_label.pack(anchor="w")

            status_text = "Present" if student["present"] else "Absent"
            status_color = "#15803d" if student["present"] else "#6b7280"
            status_label = tk.Label(text_block, text=status_text, bg=bg, fg=status_color, anchor="w")
            status_label.pack(anchor="w")

            side_label = tk.Label(
                row,
                text="Selected" if active else ("Included" if student["present"] else "Skipped"),
                bg=bg,
                fg="#1d4ed8" if active else ("#15803d" if student["present"] else "#6b7280"),
                font=("Arial", 9),
            )
            side_label.pack(side="right")

            def select_student(_event: tk.Event | None = None, sid: str = student["id"]) -> str:
                self.selected_student_id = sid
                self.refresh_student_list()
                return "break"

            for widget in (row, text_block, name_label, status_label, side_label):
                widget.bind("<Button-1>", select_student)

            check.bind("<Button-1>", lambda _event: None)

        if not selected_exists:
            self.selected_student_id = None

        self.refresh_groups_output()

    def refresh_groups_output(self) -> None:
        selected_class = self.get_selected_class()

        self.groups_text.configure(state="normal")
        self.groups_text.delete("1.0", tk.END)

        if selected_class is None:
            self.groups_text.insert(tk.END, "Select a class to see generated groups.")
        else:
            self.groups_text.insert(tk.END, format_groups(selected_class["groups"], selected_class["generatedAt"]))

        self.groups_text.configure(state="disabled")

    def clear_groups_output(self) -> None:
        self.groups_text.configure(state="normal")
        self.groups_text.delete("1.0", tk.END)
        self.groups_text.insert(tk.END, "")
        self.groups_text.configure(state="disabled")

    def on_class_select(self, _event: tk.Event | None = None) -> None:
        selection = self.class_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < 0 or index >= len(self.classes):
            return

        class_entry = self.classes[index]
        if class_entry["id"] == self.selected_class_id:
            return

        self.selected_class_id = class_entry["id"]
        self.selected_student_id = None
        self.refresh_student_list()
        self.refresh_groups_output()

    def add_class(self) -> None:
        name = normalize_name(self.new_class_var.get())
        if not name:
            messagebox.showerror("Error", "Class name cannot be empty.")
            return

        if any(class_entry["name"].lower() == name.lower() for class_entry in self.classes):
            messagebox.showerror("Error", "That class already exists.")
            return

        class_entry = {
            "id": create_id(),
            "name": name,
            "students": [],
            "groups": [],
            "generatedAt": None,
        }

        self.classes.append(class_entry)
        self.selected_class_id = class_entry["id"]
        self.selected_student_id = None
        self.new_class_var.set("")
        save_classes(self.classes)
        self.refresh_class_list()
        self.refresh_student_list()
        self.refresh_groups_output()
        self.show_feedback(f'Class "{name}" added.')

    def rename_class(self) -> None:
        selected_class = self.get_selected_class()
        if selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        next_name = simpledialog.askstring("Rename Class", "New class name:", initialvalue=selected_class["name"], parent=self.root)
        if next_name is None:
            return

        name = normalize_name(next_name)
        if not name:
            messagebox.showerror("Error", "Class name cannot be empty.")
            return

        if any(
            class_entry["id"] != selected_class["id"] and class_entry["name"].lower() == name.lower()
            for class_entry in self.classes
        ):
            messagebox.showerror("Error", "That class name already exists.")
            return

        old_name = selected_class["name"]
        selected_class["name"] = name
        save_classes(self.classes)
        self.refresh_class_list()
        self.show_feedback(f'Renamed "{old_name}" to "{name}".')

    def delete_class(self) -> None:
        selected_class = self.get_selected_class()
        if selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        confirmed = messagebox.askyesno("Confirm", f'Delete class "{selected_class["name"]}"?')
        if not confirmed:
            return

        deleted_name = selected_class["name"]
        deleted_id = selected_class["id"]

        self.classes = [class_entry for class_entry in self.classes if class_entry["id"] != deleted_id]
        self.selected_class_id = self.classes[0]["id"] if self.classes else None
        self.selected_student_id = None

        save_classes(self.classes)
        self.refresh_class_list()
        self.refresh_student_list()
        self.refresh_groups_output()
        self.show_feedback(f'Deleted class "{deleted_name}".')

    def add_student(self) -> None:
        selected_class = self.get_selected_class()
        if selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        name = normalize_name(self.new_student_var.get())
        if not name:
            messagebox.showerror("Error", "Student name cannot be empty.")
            return

        if any(student["name"].lower() == name.lower() for student in selected_class["students"]):
            messagebox.showerror("Error", "That student already exists.")
            return

        student = {"id": create_id(), "name": name, "present": True}
        selected_class["students"].append(student)
        self.invalidate_groups(selected_class)
        self.new_student_var.set("")
        save_classes(self.classes)
        self.refresh_student_list()
        self.refresh_groups_output()
        self.show_feedback(f'Student "{name}" added.')

    def rename_student(self) -> None:
        selected_class = self.get_selected_class()
        selected_student = self.get_selected_student()

        if selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        if selected_student is None:
            messagebox.showerror("Error", "Select a student first.")
            return

        next_name = simpledialog.askstring(
            "Rename Student",
            f'New name for "{selected_student["name"]}":',
            initialvalue=selected_student["name"],
            parent=self.root,
        )
        if next_name is None:
            return

        name = normalize_name(next_name)
        if not name:
            messagebox.showerror("Error", "Student name cannot be empty.")
            return

        if any(
            student["id"] != selected_student["id"] and student["name"].lower() == name.lower()
            for student in selected_class["students"]
        ):
            messagebox.showerror("Error", "That student already exists.")
            return

        old_name = selected_student["name"]
        selected_student["name"] = name
        self.invalidate_groups(selected_class)
        save_classes(self.classes)
        self.refresh_student_list()
        self.refresh_groups_output()
        self.show_feedback(f'Renamed "{old_name}" to "{name}".')

    def remove_student(self) -> None:
        selected_class = self.get_selected_class()
        selected_student = self.get_selected_student()

        if selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        if selected_student is None:
            messagebox.showerror("Error", "Select a student first.")
            return

        confirmed = messagebox.askyesno("Confirm", f'Remove student "{selected_student["name"]}"?')
        if not confirmed:
            return

        deleted_name = selected_student["name"]
        deleted_id = selected_student["id"]

        selected_class["students"] = [student for student in selected_class["students"] if student["id"] != deleted_id]
        self.selected_student_id = None
        self.invalidate_groups(selected_class)
        save_classes(self.classes)
        self.refresh_student_list()
        self.refresh_groups_output()
        self.show_feedback(f'Removed "{deleted_name}".')

    def update_status(self, student_id: str, var: tk.BooleanVar) -> None:
        selected_class = self.get_selected_class()
        if selected_class is None:
            return

        for student in selected_class["students"]:
            if student["id"] == student_id:
                student["present"] = bool(var.get())
                break

        self.invalidate_groups(selected_class)
        save_classes(self.classes)
        self.refresh_student_list()
        self.refresh_groups_output()
        self.show_feedback("Updated student status.")

    def generate_groups(self) -> None:
        selected_class = self.get_selected_class()
        if selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        present_students = [student["name"] for student in selected_class["students"] if student["present"]]
        if not present_students:
            messagebox.showerror("Error", "No present students in this class.")
            return

        try:
            value = int(self.group_value_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number for grouping.")
            return

        if value <= 0:
            messagebox.showerror("Error", "Value must be greater than 0.")
            return

        shuffled = shuffle_items(present_students)

        if self.group_mode.get() == "size":
            groups = [shuffled[index : index + value] for index in range(0, len(shuffled), value)]
        else:
            if value > len(shuffled):
                messagebox.showerror("Error", "Cannot have more groups than present students.")
                return

            groups = [[] for _ in range(value)]
            for index, student in enumerate(shuffled):
                groups[index % value].append(student)

        selected_class["groups"] = groups
        selected_class["generatedAt"] = save_groups(selected_class["name"], groups)
        self.refresh_groups_output()
        self.show_feedback(f'Groups generated for "{selected_class["name"]}".')


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentGroupGUI(root)
    root.mainloop()