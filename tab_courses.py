import tkinter as tk
from tkinter import ttk, messagebox
import db


class CoursesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None
        self.instructors = {}          # instructor name -> id

        form = ttk.Frame(self)
        form.pack(pady=10)

        self.title_e = ttk.Entry(form, width=40)
        self.desc_e = ttk.Entry(form, width=40)
        self.instr_c = ttk.Combobox(form, width=37, state="readonly")
        self.hours_e = ttk.Entry(form, width=40)

        fields = [("Title", self.title_e), ("Description", self.desc_e),
                  ("Instructor", self.instr_c), ("Duration (hours)", self.hours_e)]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            widget.grid(row=i, column=1, pady=2)

        btns = ttk.Frame(self)
        btns.pack()
        ttk.Button(btns, text="Add", command=self.add).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Update", command=self.update).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete", command=self.delete).grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Clear", command=self.clear).grid(row=0, column=3, padx=5)

        cols = ("id", "title", "description", "instructor", "hours")
        self.table = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols:
            self.table.heading(c, text=c.title())
        self.table.column("id", width=40)
        self.table.column("hours", width=60)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.on_select)

        self.load()

    def load(self):
        self.instructors = {i["name"]: i["instructor_id"] for i in db.get_instructors()}
        self.instr_c["values"] = list(self.instructors.keys())
        self.table.delete(*self.table.get_children())
        for c in db.get_courses():
            self.table.insert("", "end", values=(
                c["course_id"], c["title"], c["description"] or "",
                c["instructor"] or "", c["duration_hours"]))

    def read_form(self):
        title = self.title_e.get().strip()
        if not title:
            raise ValueError("Title is required")
        hours = int(self.hours_e.get())
        instructor_id = self.instructors.get(self.instr_c.get())
        return title, self.desc_e.get().strip(), instructor_id, hours

    def on_select(self, event):
        sel = self.table.selection()
        if not sel:
            return
        v = self.table.item(sel[0])["values"]
        self.selected_id = v[0]
        self.title_e.delete(0, "end");  self.title_e.insert(0, v[1])
        self.desc_e.delete(0, "end");   self.desc_e.insert(0, v[2])
        self.instr_c.set(v[3])
        self.hours_e.delete(0, "end");  self.hours_e.insert(0, v[4])

    def add(self):
        try:
            db.add_course(*self.read_form())
            self.load(); self.clear()
        except Exception as ex:
            messagebox.showerror("Error", f"Could not add course.\n{ex}")

    def update(self):
        if self.selected_id is None:
            return messagebox.showwarning("Select", "Select a course first")
        try:
            db.update_course(self.selected_id, *self.read_form())
            self.load(); self.clear()
        except Exception as ex:
            messagebox.showerror("Error", f"Could not update course.\n{ex}")

    def delete(self):
        if self.selected_id is None:
            return messagebox.showwarning("Select", "Select a course first")
        if not messagebox.askyesno("Confirm", "Delete this course?"):
            return
        try:
            db.delete_course(self.selected_id)
            self.load(); self.clear()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def clear(self):
        self.selected_id = None
        for e in (self.title_e, self.desc_e, self.hours_e):
            e.delete(0, "end")
        self.instr_c.set("")