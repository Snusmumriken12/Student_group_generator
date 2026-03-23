import tkinter as tk
from tkinter import messagebox
import random

from storage import load_classes, save_classes, save_groups


class StudentGroupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Group Generator")
        self.root.geometry("1100x700")

        self.classes = load_classes()
        self.selected_class = None

        self.build_ui()
        self.refresh_class_list()

    # -----------------------------
    # UI
    # -----------------------------
    def build_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        # LEFT PANEL - CLASSES
        left_frame = tk.Frame(self.root, bd=2, relief="groove", padx=8, pady=8)
        left_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=10)

        tk.Label(left_frame, text="Classes", font=("Arial", 14, "bold")).pack(anchor="w")

        self.class_listbox = tk.Listbox(left_frame, width=22, height=25)
        self.class_listbox.pack(fill="both", expand=True, pady=8)
        self.class_listbox.bind("<<ListboxSelect>>", self.on_class_select)

        class_btn_frame = tk.Frame(left_frame)
        class_btn_frame.pack(fill="x", pady=5)

        tk.Button(class_btn_frame, text="Add Class", command=self.add_class_popup).pack(fill="x", pady=2)
        tk.Button(class_btn_frame, text="Rename Class", command=self.rename_class_popup).pack(fill="x", pady=2)
        tk.Button(class_btn_frame, text="Delete Class", command=self.delete_class).pack(fill="x", pady=2)

        # TOP CENTER - STUDENT INPUT
        top_frame = tk.Frame(self.root, bd=2, relief="groove", padx=10, pady=10)
        top_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 5))

        tk.Label(top_frame, text="Student Name").grid(row=0, column=0, sticky="w")

        self.student_entry = tk.Entry(top_frame, width=35)
        self.student_entry.grid(row=1, column=0, padx=(0, 8), pady=5, sticky="ew")
        self.student_entry.bind("<Return>", lambda event: self.add_student())

        tk.Button(top_frame, text="Add Student", command=self.add_student).grid(row=1, column=1, padx=4)
        tk.Button(top_frame, text="Rename Student", command=self.rename_student_popup).grid(row=1, column=2, padx=4)
        tk.Button(top_frame, text="Remove Student", command=self.remove_student).grid(row=1, column=3, padx=4)

        self.feedback_label = tk.Label(top_frame, text="", fg="green")
        self.feedback_label.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        top_frame.grid_columnconfigure(0, weight=1)

        # RIGHT PANEL - PRESENT / ABSENT
        right_frame = tk.Frame(self.root, bd=2, relief="groove", padx=8, pady=8)
        right_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)

        tk.Label(right_frame, text="Present", font=("Arial", 14, "bold")).pack(anchor="w")

        # RIGHT PANEL - PRESENT / ABSENT
        right_frame = tk.Frame(self.root, bd=2, relief="groove", padx=8, pady=8)
        right_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)

        tk.Label(right_frame, text="Present", font=("Arial", 14, "bold")).pack(anchor="w")

        # Scrollable frame (because 20+ kids = chaos otherwise)
        canvas = tk.Canvas(right_frame)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.students_frame = tk.Frame(canvas)

        self.students_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.students_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        tk.Button(right_frame, text="Toggle Present/Absent", command=self.toggle_student_status).pack(fill="x")

        # MIDDLE CONTROLS - GROUP OPTIONS
        controls_frame = tk.Frame(self.root, bd=2, relief="groove", padx=10, pady=10)
        controls_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        tk.Label(controls_frame, text="Group Settings", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )

        self.group_mode = tk.StringVar(value="size")

        tk.Radiobutton(
            controls_frame, text="Group size", variable=self.group_mode, value="size",
            command=self.update_group_label
        ).grid(row=1, column=0, sticky="w", pady=4)

        tk.Radiobutton(
            controls_frame, text="Number of groups", variable=self.group_mode, value="count",
            command=self.update_group_label
        ).grid(row=1, column=1, sticky="w", pady=4)

        self.group_value_label = tk.Label(controls_frame, text="Students per group:")
        self.group_value_label.grid(row=2, column=0, sticky="w", pady=(10, 4))

        self.group_value_entry = tk.Entry(controls_frame, width=10)
        self.group_value_entry.grid(row=2, column=1, sticky="w", pady=(10, 4))

        tk.Button(controls_frame, text="Generate Groups", command=self.generate_groups).grid(
            row=2, column=2, padx=10, pady=(10, 4)
        )

        # BOTTOM - GROUP OUTPUT
        bottom_frame = tk.Frame(self.root, bd=2, relief="groove", padx=10, pady=10)
        bottom_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=(5, 10))

        tk.Label(bottom_frame, text="Groups", font=("Arial", 14, "bold")).pack(anchor="w")

        self.groups_text = tk.Text(bottom_frame, wrap="word", height=18)
        self.groups_text.pack(fill="both", expand=True, pady=8)

        tk.Button(bottom_frame, text="Clear Output", command=self.clear_groups_output).pack(anchor="e")

    # -----------------------------
    # Helpers
    # -----------------------------
    def show_feedback(self, message, color="green"):
        self.feedback_label.config(text=message, fg=color)
        self.root.after(5000, lambda: self.feedback_label.config(text=""))

    def get_current_students(self):
        if self.selected_class is None:
            return []
        return self.classes[self.selected_class]

    def refresh_class_list(self):
        self.class_listbox.delete(0, tk.END)
        for class_name in sorted(self.classes.keys()):
            self.class_listbox.insert(tk.END, class_name)

    def refresh_student_list(self):
        # Clear old widgets
        for widget in self.students_frame.winfo_children():
            widget.destroy()

        if self.selected_class is None:
            return

        self.student_vars = {}

        for student in self.classes[self.selected_class]:
            var = tk.BooleanVar(value=student["status"])
            self.student_vars[student["name"]] = var

            cb = tk.Checkbutton(
                self.students_frame,
                text=student["name"],
                variable=var,
                command=lambda name=student["name"], v=var: self.update_status(name, v)
            )
            cb.pack(anchor="w")
    def update_status(self, student_name, var):
        for student in self.classes[self.selected_class]:
            if student["name"] == student_name:
                student["status"] = var.get()
                break

        save_classes(self.classes)
        self.show_feedback(f"Updated '{student_name}'")

    def update_group_label(self):
        if self.group_mode.get() == "size":
            self.group_value_label.config(text="Students per group:")
        else:
            self.group_value_label.config(text="Number of groups:")

    def clear_groups_output(self):
        self.groups_text.delete("1.0", tk.END)

    # -----------------------------
    # Class actions
    # -----------------------------
    def on_class_select(self, event=None):
        selection = self.class_listbox.curselection()
        if not selection:
            return

        self.selected_class = self.class_listbox.get(selection[0])
        self.refresh_student_list()

    def add_class_popup(self):
        self.simple_input_popup("Add Class", "Class name:", self.add_class)

    def add_class(self, class_name):
        class_name = class_name.strip().title()
        if not class_name:
            messagebox.showerror("Error", "Class name cannot be empty.")
            return

        if class_name in self.classes:
            messagebox.showerror("Error", "That class already exists.")
            return

        self.classes[class_name] = []
        save_classes(self.classes)
        self.refresh_class_list()
        self.show_feedback(f"Class '{class_name}' added.")

    def rename_class_popup(self):
        if self.selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        self.simple_input_popup("Rename Class", "New class name:", self.rename_class)

    def rename_class(self, new_name):
        new_name = new_name.strip().title()
        if not new_name:
            messagebox.showerror("Error", "Class name cannot be empty.")
            return

        if new_name in self.classes:
            messagebox.showerror("Error", "That class name already exists.")
            return

        old_name = self.selected_class
        self.classes[new_name] = self.classes.pop(old_name)
        self.selected_class = new_name

        save_classes(self.classes)
        self.refresh_class_list()
        self.refresh_student_list()
        self.show_feedback(f"Renamed '{old_name}' to '{new_name}'.")

    def delete_class(self):
        if self.selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        confirm = messagebox.askyesno("Confirm", f"Delete class '{self.selected_class}'?")
        if not confirm:
            return

        del self.classes[self.selected_class]
        deleted_name = self.selected_class
        self.selected_class = None

        save_classes(self.classes)
        self.refresh_class_list()
        self.refresh_student_list()
        self.clear_groups_output()
        self.show_feedback(f"Deleted class '{deleted_name}'.")

    # -----------------------------
    # Student actions
    # -----------------------------
    def add_student(self):
        if self.selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        name = self.student_entry.get().strip().title()
        if not name:
            messagebox.showerror("Error", "Student name cannot be empty.")
            return

        students = self.get_current_students()
        existing_names = {student["name"] for student in students}

        if name in existing_names:
            messagebox.showerror("Error", "That student already exists.")
            return

        students.append({
            "name": name,
            "status": True
        })

        save_classes(self.classes)
        self.refresh_student_list()
        self.student_entry.delete(0, tk.END)
        self.show_feedback(f"Student '{name}' added.")

    def get_selected_student_name(self):
        if self.selected_class is None:
            return None

        selection = self.student_listbox.curselection()
        if not selection:
            return None

        raw_text = self.student_listbox.get(selection[0])
        return raw_text.split(" (")[0]

    def remove_student(self):
        if self.selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        student_name = self.get_selected_student_name()
        if not student_name:
            messagebox.showerror("Error", "Select a student first.")
            return

        students = self.get_current_students()

        for student in students:
            if student["name"] == student_name:
                students.remove(student)
                break

        save_classes(self.classes)
        self.refresh_student_list()
        self.show_feedback(f"Removed '{student_name}'.")

    def rename_student_popup(self):
        if self.selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        student_name = self.get_selected_student_name()
        if not student_name:
            messagebox.showerror("Error", "Select a student first.")
            return

        self.simple_input_popup(
            "Rename Student",
            f"New name for '{student_name}':",
            lambda new_name: self.rename_student(student_name, new_name)
        )

    def rename_student(self, old_name, new_name):
        new_name = new_name.strip().title()
        if not new_name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        students = self.get_current_students()
        existing_names = {student["name"] for student in students}

        if new_name in existing_names:
            messagebox.showerror("Error", "That name already exists.")
            return

        for student in students:
            if student["name"] == old_name:
                student["name"] = new_name
                break

        save_classes(self.classes)
        self.refresh_student_list()
        self.show_feedback(f"Renamed '{old_name}' to '{new_name}'.")

    # -----------------------------
    # Group generation
    # -----------------------------
    def generate_groups(self):
        if self.selected_class is None:
            messagebox.showerror("Error", "Select a class first.")
            return

        students = self.get_current_students()
        present_students = [student["name"] for student in students if student["status"]]

        if not present_students:
            messagebox.showerror("Error", "No present students in this class.")
            return

        try:
            value = int(self.group_value_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number for grouping.")
            return

        if value <= 0:
            messagebox.showerror("Error", "Value must be greater than 0.")
            return

        shuffled = present_students[:]
        random.shuffle(shuffled)

        if self.group_mode.get() == "size":
            groups = []
            for i in range(0, len(shuffled), value):
                groups.append(shuffled[i:i + value])
        else:
            if value > len(shuffled):
                messagebox.showerror("Error", "Cannot have more groups than present students.")
                return

            groups = [[] for _ in range(value)]
            for i, student in enumerate(shuffled):
                groups[i % value].append(student)

        self.clear_groups_output()

        for i, group in enumerate(groups, start=1):
            self.groups_text.insert(tk.END, f"Group {i}\n")
            for student in group:
                self.groups_text.insert(tk.END, f" - {student}\n")
            self.groups_text.insert(tk.END, "\n")

        save_groups(self.selected_class, groups)
        self.show_feedback(f"Groups generated and saved for '{self.selected_class}'.")

    # -----------------------------
    # Reusable popup
    # -----------------------------
    def simple_input_popup(self, title, label_text, callback):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("300x120")
        popup.grab_set()

        tk.Label(popup, text=label_text).pack(pady=(10, 5))

        entry = tk.Entry(popup, width=30)
        entry.pack(pady=5)
        entry.focus_set()

        def submit():
            value = entry.get()
            callback(value)
            popup.destroy()

        tk.Button(popup, text="OK", command=submit).pack(pady=10)
        entry.bind("<Return>", lambda event: submit())


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentGroupGUI(root)
    root.mainloop()