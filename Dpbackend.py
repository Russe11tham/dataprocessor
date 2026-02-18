#Importing required Libraries
import csv  #csv operations
import os #renaming
import chardet #for encoding detetction
import pandas as pd #import pandas
from pathlib import Path
from typing import Optional
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

#boilerplate for installer
try:
    import pypalmsens as ps
except ImportError:
    ps = None

#update check:
APP_VERSION = "1.0.0"  # current version of your app
UPDATE_URL = "https://raw.githubusercontent.com/yourname/dataprocessor/main/latest.txt"


def ifcsv(input_file, output_file, nrows):
    # Detect encoding first
    with open(input_file, 'rb') as f:
        raw_data = f.read(10000)  # Sample for speed
        detected = chardet.detect(raw_data)
        encoding = detected['encoding']

    # Read all values into a flat list using detected encoding
    values = []
    with open(input_file, newline="", encoding=encoding) as f:
        reader = csv.reader(f)
        for row in reader:
            values.extend(row)

    # Write out nrows values per row as UTF-8
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        while values:
            writer.writerow(values[:{nrows}])
            values = values[{nrows}:]

    print(f"Output saved to {output_file} as UTF-8")

def iftxt(input_file, output_file, nrows):
    # Read text and split by comma
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    values = [v.strip() for v in text.split(",") if v.strip()]

    # Write to CSV: every nrows values become one row
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        while values:
            writer.writerow(values[:nrows])
            values = values[nrows:]

def ifpssession(pssession_path: str, csv_path: str, experiment_name: Optional[str] = None):
    if ps is None:
        raise RuntimeError(
            "PalmSens .pssession conversion is not available in this build.\n"
            "Run the Python version with pypalmsens installed, or use the Windows app."
        )
    
    path = Path(pssession_path)
    if not path.exists():
        raise FileNotFoundError(f"{pssession_path} not found")
    
    measurements = ps.load_session_file(pssession_path)
    if not measurements:
        raise ValueError("No measurements found in pssession")
    
    frames = []
    frame_names = []
    for measurement in measurements:
        df = measurement.dataset.to_dataframe()
        name = experiment_name or measurement.title or f"exp_{len(frames)+1}"
        frames.append(df)
        frame_names.append(name)
        print(f"Loaded: {name}, curves: {len(measurement.curves)}, points: {len(df)}")
    
    if frames:
        combined_df = pd.concat(frames, keys=frame_names, names=['Measurement', None])
        combined_df.to_csv(csv_path, index=True)  # Index preserves measurement labels
        print(f"Saved {combined_df.shape[0]} rows, {combined_df.shape[1]} cols to {csv_path}")
    else:
        raise ValueError("No data extracted")


def process_single_file(input_file: str, ncols: int | None = None):
    """
    Detect file type and convert to <stem>-converted.csv in same folder.
    """
    input_file = str(input_file)
    input_path = Path(input_file)

    # always: <original_name>-converted.csv
    final_csv_path = input_path.with_name(input_path.stem + "-converted.csv")

    _, ext = os.path.splitext(input_file)
    filetype = ext[1:].lower()

    if filetype == "csv":
        if ncols is None:
            raise ValueError("ncols is required for CSV.")
        ifcsv(input_file, str(final_csv_path), nrows=ncols)

    elif filetype == "txt":
        if ncols is None:
            raise ValueError("ncols is required for TXT.")
        iftxt(input_file, str(final_csv_path), nrows=ncols)

    elif filetype == "pssession":
        ifpssession(input_file, str(final_csv_path), experiment_name=None)

    else:
        raise ValueError(f"Invalid extension '.{filetype}', use csv/txt/pssession.")


def convert_all_pssession_in_folder(folder: str, experiment_name=None):
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"Folder not found or not a directory: {folder}")

    pssession_files = list(folder_path.glob("*.pssession"))
    if not pssession_files:
        return

    for pss_file in pssession_files:
        # <name>-converted.csv for each .pssession
        csv_path = pss_file.with_name(pss_file.stem + "-converted.csv")
        ifpssession(str(pss_file), str(csv_path), experiment_name=experiment_name)
