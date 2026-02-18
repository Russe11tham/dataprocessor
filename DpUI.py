import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import os
from Dpbackend import process_single_file, convert_all_pssession_in_folder

root = tk.Tk()
root.title("Photochemistry File Converter")
root.geometry("420x260")

# Center everything with pack and anchor='center' (default)
root.configure(padx=20, pady=20)

single_label = None
single_entry = None

def show_single_name_entry():
    global single_label, single_entry
    if single_entry is not None:
        return
    single_label = tk.Label(root, text="Final CSV name (no .csv):")
    single_label.pack(pady=5)
    single_entry = tk.Entry(root, width=40)
    single_entry.pack(pady=5)

def hide_single_name_entry():
    global single_label, single_entry
    if single_entry is not None:
        single_entry.destroy()
        single_entry = None
    if single_label is not None:
        single_label.destroy()
        single_label = None

def run_single():
    path = filedialog.askopenfilename(
        title="Select input file",
        filetypes=[("All supported", "*.csv *.txt *.pssession"),
                   ("CSV", "*.csv"),
                   ("Text", "*.txt"),
                   ("PalmSens session", "*.pssession")]
    )
    if not path:
        return

    _, ext = os.path.splitext(path)
    filetype = ext[1:].lower()
    if filetype in ("csv", "txt"):
        ncols_str = simpledialog.askstring("Columns", "Enter the number of columns:")
        if not ncols_str:
            return
        try:
            ncols = int(ncols_str)
        except ValueError:
            messagebox.showerror("Error", "Number of columns must be an integer.")
            return
    else:
        ncols = None

    try:
        process_single_file(Path(path), ncols=ncols)
        messagebox.showinfo("Done", "Saved CSV file next to the original.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def run_all():
    hide_single_name_entry()

    folder = filedialog.askdirectory(title="Select folder with .pssession files")
    if not folder:
        return

    try:
        convert_all_pssession_in_folder(folder, experiment_name=None)
        messagebox.showinfo("Done", "Batch conversion complete.\nEach .pssession → same-name .csv")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- UI layout ---

# Welcome message (centered)
welcome_label = tk.Label(root, text="Welcome to Data Processor", font=("Helvetica", 14, "bold"))
welcome_label.pack(pady=(0, 15))

# Buttons (centered by default with pack)
single_btn = tk.Button(root, text="Convert Single File", width=25, command=run_single)
single_btn.pack(pady=5)

all_btn = tk.Button(root, text="Convert All .pssession in Folder", width=25, command=run_all)
all_btn.pack(pady=5)

root.mainloop()

