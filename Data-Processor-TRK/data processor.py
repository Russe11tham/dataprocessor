#Importing required Libraries
import csv  #csv operations
import os #renaming
import chardet #for encoding detetction
import pandas as pd #import pandas
import pypalmsens as ps
from pathlib import Path
from typing import Optional

#if csv function
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

# if txt
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

#if pssession function
def ifpssession(pssession_path: str, csv_path: str, experiment_name: Optional[str] = None):
    """
    Custom ifpssession replacement using PyPalmSens.
    Loads .pssession, extracts DataFrames (3 cols for CA: Time, Potential, Current),
    saves combined CSV with measurement labels.
    
    Args:
        pssession_path: Path to .pssession file
        csv_path: Output CSV path
        experiment_name: Optional filter; uses first if None
    """
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

#for all ps session function
def convert_all_pssession_in_folder(folder: str, experiment_name=None):
    """
    Find all .pssession files in 'folder' and convert each to a UTF-8 CSV
    with the same base name in the same folder.
    """
    folder_path = Path(folder)

    # Safety check
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Folder not found or not a directory: {folder}")
        return

    pssession_files = list(folder_path.glob("*.pssession"))

    if not pssession_files:
        print("No .pssession files found in this folder.")
        return

    for pss_file in pssession_files:
        csv_path = pss_file.with_suffix(".csv")  # same name, .csv extension
        print(f"Converting {pss_file.name} → {csv_path.name}")

        # Your existing converter; should write UTF-8 CSV
        ifpssession(str(pss_file), str(csv_path), experiment_name=experiment_name)

        # Optional: re-save explicitly as UTF-8 if ifpssession didn't enforce it
        # For example, using pandas:
        # import pandas as pd
        # df = pd.read_csv(csv_path)
        # df.to_csv(csv_path, index=False, encoding="utf-8")

    print("Conversion complete.")

#renaming function
def renaming(old_name, finalname):
    new_name = f"{finalname}.csv"
    os.rename(old_name, new_name)

#main function
def main():
    print("Welcome to Photochemistry File Converter")
    print("file options: csv / txt / pssession / all")

    mode = input("Enter mode (single/all): ").strip().lower()

    if mode == "all":
        folder = input("Enter folder path ('.' for current folder): ").strip()
        convert_all_pssession_in_folder(folder, experiment_name=None)
        return

    # single-file mode (original behaviour)
    input_file = input("Enter current file name (with extension): ")
    finalname = input("Enter desired final file name (without .csv): ")
    output_tmp = "output.csv"

    # Auto-detect filetype from extension
    _, ext = os.path.splitext(input_file)
    filetype = ext[1:].lower()  # e.g., 'csv', 'txt', 'pssession'
    
    print("DEBUG: detected filetype =", filetype)

    if filetype == "csv":
        print("DEBUG: in csv branch")
        nrows = int(input("Enter the number of columns: "))
        ifcsv(input_file, output_tmp, nrows)
        renaming(output_tmp, finalname)

    elif filetype == "txt":
        print("DEBUG: in txt branch")
        nrows = int(input("Enter the number of columns: "))
        iftxt(input_file, output_tmp, nrows)
        renaming(output_tmp, finalname)
        
    elif filetype == "pssession":
        print("DEBUG: in pssession branch")
        csv_path = output_tmp
        ifpssession(input_file, csv_path, experiment_name=None)
        renaming(output_tmp, finalname)

    else:
        print(f"Invalid extension '.{filetype}', please use csv/txt/pssession.")

main()