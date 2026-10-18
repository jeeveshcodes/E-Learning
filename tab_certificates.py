import tkinter as tk
from tkinter import ttk, messagebox

import db


class CertificateTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Verify a certificate",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))

        row = ttk.Frame(self)
        row.pack(anchor="w", padx=20, pady=5)
        self.code_var = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.code_var, width=30)
        entry.pack(side="left")
        entry.bind("<Return>", lambda event: self.verify())
        ttk.Button(row, text="Verify", command=self.verify).pack(side="left", padx=8)

        self.result = tk.Label(self, text="", font=("Segoe UI", 12), justify="left")
        self.result.pack(anchor="w", padx=20, pady=15)

    def verify(self):
        code = self.code_var.get().strip()
        if not code:
            self.result.config(text="Enter a certificate code.", fg="gray")
            return
        try:
            info = db.verify_certificate(code)
        except Exception as e:
            messagebox.showerror("Database error", str(e))
            return
        if info:
            self.result.config(
                text=(f"VALID\nStudent: {info['student']}\n"
                      f"Course: {info['course']}\nIssued on: {info['issued_on']}"),
                fg="green")
        else:
            self.result.config(text="INVALID: no certificate with this code", fg="red")