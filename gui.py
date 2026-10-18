import importlib
import tkinter as tk
from tkinter import ttk

# (tab title, module file name, class name)
TABS = [
    ("Students", "tab_students", "StudentsTab"),
    ("Courses", "tab_courses", "CoursesTab"),
    ("Enrollments", "tab_enrollments", "EnrollmentsTab"),
    ("Progress", "tab_progress", "ProgressTab"),
    ("Early Warning", "tab_warning", "WarningTab"),
    ("Reports", "tab_reports", "ReportsTab"),
    ("Certificates", "tab_certificates", "CertificateTab"),
]


def main():
    root = tk.Tk()
    root.title("E-learning Platform Database")
    root.geometry("940x580")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    for title, module_name, class_name in TABS:
        try:
            module = importlib.import_module(module_name)
            tab = getattr(module, class_name)(notebook)
        except ModuleNotFoundError as e:
            if e.name != module_name:   # a real missing library, not a missing tab file
                raise
            tab = ttk.Frame(notebook)
            ttk.Label(tab, text=f"{title} - coming soon").pack(pady=40)
        notebook.add(tab, text=title)

    root.mainloop()


if __name__ == "__main__":
    main()