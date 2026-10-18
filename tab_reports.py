import tkinter as tk
from tkinter import ttk, messagebox

import db

ALL = "All courses"


class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.course_ids = {}          # course title -> course_id

        # ----- report 1: course completion rate -----
        box1 = ttk.LabelFrame(self, text="Course completion rate")
        box1.pack(fill="x", padx=10, pady=10)

        columns = ("course", "enrolled", "completed", "rate", "bar")
        self.completion_tree = ttk.Treeview(box1, columns=columns, show="headings", height=5)
        for col, text, width in [("course", "Course", 240), ("enrolled", "Enrolled", 90),
                                 ("completed", "Completed", 100), ("rate", "Rate", 80),
                                 ("bar", "", 300)]:
            self.completion_tree.heading(col, text=text)
            self.completion_tree.column(col, width=width, anchor="w")
        self.completion_tree.pack(fill="x", padx=8, pady=8)

        # ----- report 2: top scorers -----
        box2 = ttk.LabelFrame(self, text="Top scorers (average score)")
        box2.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        controls = ttk.Frame(box2)
        controls.pack(fill="x", padx=8, pady=8)
        ttk.Label(controls, text="Course").pack(side="left")
        self.course_box = ttk.Combobox(controls, state="readonly", width=32)
        self.course_box.pack(side="left", padx=8)
        self.course_box.bind("<<ComboboxSelected>>", lambda event: self.load_scorers())
        ttk.Button(controls, text="Refresh", command=self.refresh).pack(side="left")

        columns = ("rank", "name", "modules", "avg")
        self.scorer_tree = ttk.Treeview(box2, columns=columns, show="headings", height=6)
        for col, text, width in [("rank", "Rank", 60), ("name", "Student", 240),
                                 ("modules", "Modules done", 120), ("avg", "Average score", 120)]:
            self.scorer_tree.heading(col, text=text)
            self.scorer_tree.column(col, width=width, anchor="w")
        self.scorer_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # reload every time this tab is shown, so the numbers are always current
        self.bind("<Map>", lambda event: self.refresh())
        self.refresh()

    # ----- loading -----
    def refresh(self):
        try:
            completion = db.get_course_completion()
            courses = db.get_courses()
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        # report 1
        for item in self.completion_tree.get_children():
            self.completion_tree.delete(item)
        for r in completion:
            bar = "█" * round(r["rate"] / 10)
            self.completion_tree.insert("", "end", values=(
                r["title"], r["enrolled"], r["completed"], f"{r['rate']}%", bar))

        # course dropdown for report 2 (keep the current choice if there is one)
        current = self.course_box.get() or ALL
        self.course_ids = {c["title"]: c["course_id"] for c in courses}
        self.course_box["values"] = [ALL] + list(self.course_ids)
        self.course_box.set(current if current in self.course_box["values"] else ALL)
        self.load_scorers()

    def load_scorers(self):
        choice = self.course_box.get()
        course_id = self.course_ids.get(choice)      # None when "All courses"
        try:
            rows = db.get_top_scorers(course_id)
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        for item in self.scorer_tree.get_children():
            self.scorer_tree.delete(item)
        for rank, r in enumerate(rows, start=1):
            self.scorer_tree.insert("", "end",
                                    values=(rank, r["name"], r["modules_done"], r["avg_score"]))