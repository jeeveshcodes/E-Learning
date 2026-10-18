import tkinter as tk
from tkinter import ttk, messagebox

import db

# row background colours: red / orange / green
COLORS = {"High": "#f4b6b6", "Medium": "#fcd9a0", "Low": "#bfe5bf"}


class WarningTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)
        ttk.Label(top, text="Students at risk",
                  font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.load).pack(side="right")

        columns = ("name", "modules", "avg", "risk", "reason")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        for col, text, width in [("name", "Student", 160), ("modules", "Modules done", 100),
                                 ("avg", "Avg score", 90), ("risk", "Risk", 80),
                                 ("reason", "Reason", 400)]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        for level, color in COLORS.items():
            self.tree.tag_configure(level, background=color)
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.load()

    def load(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            rows = db.get_early_warning()
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        for r in rows:
            avg = r["avg_score"] if r["avg_score"] is not None else "-"
            self.tree.insert("", "end",
                             values=(r["name"], r["modules_done"], avg, r["risk"], r["reason"]),
                             tags=(r["risk"],))