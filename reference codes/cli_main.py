# cli_main.py
import os
from Dpbackend import process_single_file

def main():
    print("Welcome to Photochemistry File Converter")
    print("Supported file types: csv / txt / pssession")

    input_file = input("Enter current file name (with extension): ").strip()
    finalname = input("Enter desired final file name (without .csv): ").strip()

    if not input_file or not finalname:
        print("Input file and final name are required.")
        return

    # Detect file type from extension
    _, ext = os.path.splitext(input_file)
    filetype = ext[1:].lower()

    # Number of columns only needed for csv/txt
    if filetype in ("csv", "txt"):
        ncols_str = input("Enter the number of columns: ").strip()
        try:
            ncols = int(ncols_str)
        except ValueError:
            print("Number of columns must be an integer.")
            return
    else:
        ncols = None

    try:
        process_single_file(input_file, finalname, ncols=ncols)
        print(f"Done. Saved '{finalname}.csv'.")
    except Exception as e:
        print("Error during conversion:", e)

if __name__ == "__main__":
    main()
