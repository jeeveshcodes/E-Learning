import tkinter as tk
from tkinter import ttk, messagebox

import psycopg2

import db


class StudentsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None          # id of the student chosen in the table

        # ----- form -----
        form = ttk.LabelFrame(self, text="Student details")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Name").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=8)

        ttk.Label(form, text="Email").grid(row=0, column=2, padx=8, sticky="e")
        self.email_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.email_var, width=32).grid(row=0, column=3, padx=8)

        buttons = ttk.Frame(form)
        buttons.grid(row=1, column=0, columnspan=4, pady=(0, 8))
        ttk.Button(buttons, text="Add", command=self.add).pack(side="left", padx=5)
        ttk.Button(buttons, text="Update", command=self.update).pack(side="left", padx=5)
        ttk.Button(buttons, text="Delete", command=self.delete).pack(side="left", padx=5)
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left", padx=5)

        # ----- table -----
        columns = ("id", "name", "email", "joined")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col, text, width in [("id", "ID", 60), ("name", "Name", 220),
                                 ("email", "Email", 280), ("joined", "Joined on", 120)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load()

    # ----- helpers -----
    def load(self):
        """Reload the table from the database."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            for s in db.get_students():
                self.tree.insert("", "end",
                                 values=(s["student_id"], s["name"], s["email"], s["joined_on"]))
        except Exception as e:
            messagebox.showerror("Database error", str(e))

    def on_select(self, event):
        """When a row is clicked, copy its values into the form."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])["values"]
        self.selected_id = values[0]
        self.name_var.set(values[1])
        self.email_var.set(values[2])

    def clear(self):
        self.selected_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.tree.selection_remove(self.tree.selection())

    def read_form(self):
        """Return (name, email) if valid, otherwise show a message and return None."""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Please enter the student's name.")
            return None
        if "@" not in email:
            messagebox.showwarning("Invalid email", "Please enter a valid email address.")
            return None
        return name, email

    # ----- button actions -----
    def add(self):
        data = self.read_form()
        if not data:
            return
        try:
            db.add_student(*data)
        except psycopg2.errors.UniqueViolation:
            messagebox.showerror("Duplicate", "A student with this email already exists.")
            return
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        self.clear()
        self.load()

    def update(self):
        if self.selected_id is None:
            messagebox.showinfo("Select a student", "Click a student in the table first.")
            return
        data = self.read_form()
        if not data:
            return
        try:
            db.update_student(self.selected_id, *data)
        except psycopg2.errors.UniqueViolation:
            messagebox.showerror("Duplicate", "Another student already uses this email.")
            return
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        self.clear()
        self.load()

    def delete(self):
        if self.selected_id is None:
            messagebox.showinfo("Select a student", "Click a student in the table first.")
            return
        name = self.name_var.get()
        if not messagebox.askyesno(
                "Confirm delete",
                f"Delete {name}?\nTheir enrollments, progress and certificates will also be deleted."):
            return
        try:
            db.delete_student(self.selected_id)
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        self.clear()
        self.load()