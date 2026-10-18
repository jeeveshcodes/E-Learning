import tkinter as tk
from tkinter import ttk, messagebox

import psycopg2

import db

STATUSES = ["active", "completed", "dropped"]


class EnrollmentsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.student_ids = {}        # dropdown label -> student_id
        self.course_ids = {}         # dropdown label -> course_id
        self.selected_id = None      # enrollment chosen in the table

        # ----- enroll form -----
        form = ttk.LabelFrame(self, text="Enroll a student in a course")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Student").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.student_box = ttk.Combobox(form, state="readonly", width=30)
        self.student_box.grid(row=0, column=1, padx=8)

        ttk.Label(form, text="Course").grid(row=0, column=2, padx=8, sticky="e")
        self.course_box = ttk.Combobox(form, state="readonly", width=30)
        self.course_box.grid(row=0, column=3, padx=8)

        ttk.Button(form, text="Enroll", command=self.enroll).grid(row=0, column=4, padx=8)

        # ----- manage the selected enrollment -----
        manage = ttk.LabelFrame(self, text="Selected enrollment")
        manage.pack(fill="x", padx=10, pady=(0, 10))

        ttk.Label(manage, text="Status").grid(row=0, column=0, padx=8, pady=8)
        self.status_box = ttk.Combobox(manage, values=STATUSES, state="readonly", width=14)
        self.status_box.grid(row=0, column=1, padx=8)
        ttk.Button(manage, text="Set status", command=self.set_status).grid(row=0, column=2, padx=8)
        ttk.Button(manage, text="Remove enrollment", command=self.remove).grid(row=0, column=3, padx=8)
        ttk.Button(manage, text="Refresh", command=self.refresh).grid(row=0, column=4, padx=8)

        # ----- table -----
        columns = ("id", "student", "course", "date", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col, text, width in [("id", "ID", 50), ("student", "Student", 200),
                                 ("course", "Course", 240), ("date", "Enrolled on", 110),
                                 ("status", "Status", 90)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # reload the lists every time this tab is shown, so new students/courses appear
        self.bind("<Map>", lambda event: self.refresh())
        self.refresh()

    # ----- helpers -----
    def refresh(self):
        """Reload both dropdowns and the enrollments table from the database."""
        try:
            students = db.get_students()
            courses = db.get_courses()
            enrollments = db.get_enrollments()
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return

        self.student_ids = {f"{s['name']} (ID {s['student_id']})": s["student_id"]
                            for s in students}
        self.course_ids = {f"{c['title']} (ID {c['course_id']})": c["course_id"]
                           for c in courses}
        self.student_box["values"] = list(self.student_ids)
        self.course_box["values"] = list(self.course_ids)

        self.selected_id = None
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in enrollments:
            self.tree.insert("", "end", values=(e["enrollment_id"], e["student"], e["course"],
                                                e["enrolled_on"], e["status"]))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])["values"]
        self.selected_id = values[0]
        self.status_box.set(values[4])

    # ----- button actions -----
    def enroll(self):
        student = self.student_box.get()
        course = self.course_box.get()
        if not student or not course:
            messagebox.showwarning("Missing choice", "Choose both a student and a course.")
            return
        try:
            db.enroll_student(self.student_ids[student], self.course_ids[course])
        except psycopg2.errors.UniqueViolation:
            messagebox.showinfo("Already enrolled", "This student is already in that course.")
            return
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        self.refresh()

    def set_status(self):
        if self.selected_id is None:
            messagebox.showinfo("Select an enrollment", "Click a row in the table first.")
            return
        status = self.status_box.get()
        if not status:
            messagebox.showwarning("Missing status", "Choose a status first.")
            return
        try:
            db.set_enrollment_status(self.selected_id, status)
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        self.refresh()

    def remove(self):
        if self.selected_id is None:
            messagebox.showinfo("Select an enrollment", "Click a row in the table first.")
            return
        if not messagebox.askyesno("Confirm", "Remove this enrollment?"):
            return
        try:
            db.delete_enrollment(self.selected_id)
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        self.refresh()