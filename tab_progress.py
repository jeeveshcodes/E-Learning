import tkinter as tk
from tkinter import ttk, messagebox
import db


class ProgressTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.students = {}   # label -> student_id
        self.courses = {}    # label -> course_id
        self.modules = {}    # label -> module_id

        form = ttk.Frame(self)
        form.pack(pady=10)

        self.student_c = ttk.Combobox(form, width=40, state="readonly")
        self.course_c = ttk.Combobox(form, width=40, state="readonly")
        self.module_c = ttk.Combobox(form, width=40, state="readonly")
        self.score_e = ttk.Entry(form, width=43)

        fields = [("Student", self.student_c), ("Course", self.course_c),
                  ("Module", self.module_c), ("Score (0-100)", self.score_e)]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            widget.grid(row=i, column=1, pady=2)

        self.course_c.bind("<<ComboboxSelected>>", self.load_modules)

        btns = ttk.Frame(self)
        btns.pack(pady=5)
        ttk.Button(btns, text="Mark complete & save score",
                   command=self.save).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Issue certificate",
                   command=self.issue).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Refresh",
                   command=self.refresh).grid(row=0, column=2, padx=5)

        cols = ("student", "module", "completed", "score", "date")
        self.table = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c in cols:
            self.table.heading(c, text=c.title())
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh()

    def refresh(self):
        """Reload dropdowns and the progress table."""
        self.students = {f"{s['student_id']} - {s['name']}": s["student_id"]
                         for s in db.get_students()}
        self.courses = {f"{c['course_id']} - {c['title']}": c["course_id"]
                        for c in db.get_courses()}
        self.student_c["values"] = list(self.students.keys())
        self.course_c["values"] = list(self.courses.keys())

        self.table.delete(*self.table.get_children())
        rows = db.run_query("""
            SELECT s.name AS student, m.title AS module, p.completed,
                   p.score, p.completed_on
            FROM progress p
            JOIN students s ON s.student_id = p.student_id
            JOIN modules  m ON m.module_id  = p.module_id
            ORDER BY p.progress_id DESC
        """)
        for r in rows:
            self.table.insert("", "end", values=(
                r["student"], r["module"], "Yes" if r["completed"] else "No",
                r["score"], r["completed_on"]))

    def load_modules(self, event=None):
        course_id = self.courses[self.course_c.get()]
        mods = db.get_modules(course_id)
        self.modules = {f"{m['module_order']}. {m['title']}": m["module_id"] for m in mods}
        self.module_c["values"] = list(self.modules.keys())
        self.module_c.set("")

    def save(self):
        try:
            student_id = self.students[self.student_c.get()]
            module_id = self.modules[self.module_c.get()]
            score = float(self.score_e.get())
            if not 0 <= score <= 100:
                raise ValueError("Score must be between 0 and 100")
        except KeyError:
            return messagebox.showwarning("Missing", "Choose a student, course and module")
        except ValueError as ex:
            return messagebox.showwarning("Check input", str(ex))
        try:
            db.record_progress(student_id, module_id, score)
            self.refresh()
            messagebox.showinfo("Saved", "Progress saved")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def issue(self):
        try:
            student_id = self.students[self.student_c.get()]
            course_id = self.courses[self.course_c.get()]
        except KeyError:
            return messagebox.showwarning("Missing", "Choose a student and a course")
        try:
            code = db.issue_certificate(student_id, course_id)
            if code:
                messagebox.showinfo("Certificate", f"Certificate code: {code}")
            else:
                messagebox.showwarning("Not yet",
                    "This student has not completed every module of the course.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))