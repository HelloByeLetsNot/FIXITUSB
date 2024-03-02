import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk

def zero_fill_drive():
    try:
        selected_drive = drive_var.get()
        if selected_drive:
            # Get the size of the drive
            drive_size = os.path.getsize(selected_drive)
            with open(selected_drive, "wb") as f:
                for _ in range(100):
                    # Write zeros to the entire drive (in chunks to update progress bar)
                    f.write(b'\0' * (drive_size // 100))
                    progress_var.set(progress_var.get() + 1)
                    progress_bar.update()
            result_label.config(text="Zero-fill process completed successfully.")
        else:
            result_label.config(text="Please select a drive first.")
    except Exception as e:
        result_label.config(text="Error: " + str(e))

def format_drive():
    selected_drive = drive_var.get()
    selected_filesystem = filesystem_var.get()

    if selected_drive and selected_filesystem:
        confirmed = messagebox.askyesno("Confirmation", f"Are you sure you want to format {selected_drive} as {selected_filesystem}? This will erase all data on the drive.")
        if confirmed:
            try:
                subprocess.run(["mkfs." + selected_filesystem, "-F", selected_drive], check=True)
                result_label.config(text="Drive formatted successfully.")
            except subprocess.CalledProcessError as e:
                result_label.config(text=f"Error: {e}")
        else:
            result_label.config(text="Operation cancelled.")
    else:
        result_label.config(text="Please select a drive and filesystem first.")

def check_bad_sectors():
    selected_drive = drive_var.get()
    if selected_drive:
        if os.name == 'nt':  # Windows
            try:
                subprocess.run(["chkdsk", selected_drive], check=True)
                result_label.config(text="Bad sector check completed successfully.")
            except subprocess.CalledProcessError as e:
                result_label.config(text=f"Error: {e}")
        else:  # Linux
            try:
                subprocess.run(["badblocks", selected_drive], check=True)
                result_label.config(text="Bad sector check completed successfully.")
            except subprocess.CalledProcessError as e:
                result_label.config(text=f"Error: {e}")
    else:
        result_label.config(text="Please select a drive first.")

def recover_data():
    selected_drive = drive_var.get()
    if selected_drive:
        if os.name == 'nt':  # Windows
            try:
                import win32file
                import win32api

                disk = r"\\.\%s:" % selected_drive[0]
                sectors_per_cluster, bytes_per_sector, _, _, _ = win32file.GetDiskFreeSpace(disk)
                cluster_size = sectors_per_cluster * bytes_per_sector
                with open(selected_drive, "rb") as f:
                    data = f.read()
                    recovered_file = os.path.join(os.getcwd(), "recovered_data")
                    with open(recovered_file, "wb") as recovered:
                        recovered.write(data)
                result_label.config(text=f"Data recovered successfully to {recovered_file}")
            except Exception as e:
                result_label.config(text=f"Error: {e}")
        else:  # Linux
            result_label.config(text="Data recovery feature is not supported on Linux yet.")
    else:
        result_label.config(text="Please select a drive first.")

def refresh_drives():
    drives = [chr(i) + ":" for i in range(65, 91) if os.path.exists(chr(i) + ":")]
    drive_dropdown['values'] = drives

# Create the main window
root = ThemedTk(theme="breeze-dark")
root.title("FixIt Usb by Kozaworld.com")

# Create frames
main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

# Drive selection dropdown
drive_var = tk.StringVar()
drive_dropdown = ttk.Combobox(main_frame, textvariable=drive_var, state="readonly", width=20)
drive_dropdown.grid(column=0, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))
drive_dropdown.bind("<Button-1>", lambda event: refresh_drives())

# Refresh button
refresh_button = ttk.Button(main_frame, text="Refresh", command=refresh_drives)
refresh_button.grid(column=1, row=0, padx=5, pady=5, sticky=(tk.W, tk.E))

# Filesystem selection dropdown
filesystem_var = tk.StringVar()
filesystem_dropdown = ttk.Combobox(main_frame, textvariable=filesystem_var, state="readonly", width=20)
filesystem_dropdown.grid(column=0, row=1, padx=5, pady=5, sticky=(tk.W, tk.E))
filesystem_dropdown['values'] = ["NTFS", "FAT32"]  # Add more options as needed

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100)
progress_bar.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

# Zero-fill button
zero_fill_button = ttk.Button(main_frame, text="Zero Fill", command=zero_fill_drive)
zero_fill_button.grid(column=0, row=3, padx=5, pady=5, sticky=(tk.W, tk.E))

# Format button
format_button = ttk.Button(main_frame, text="Format Drive", command=format_drive)
format_button.grid(column=1, row=3, padx=5, pady=5, sticky=(tk.W, tk.E))

# # Check bad sectors button
check_bad_sectors_button = ttk.Button(main_frame, text="Check Bad Sectors", command=check_bad_sectors, width=20)
check_bad_sectors_button.grid(column=0, row=4, padx=(10, 5), pady=10, sticky=(tk.W, tk.E))  # Adjust padx to provide additional padding on the left side

# Recover data button
recover_data_button = ttk.Button(main_frame, text="Recover Data", command=recover_data)
recover_data_button.grid(column=1, row=4, padx=5, pady=5, sticky=(tk.W, tk.E))

# Result label
result_label = ttk.Label(main_frame, text="", wraplength=250)
result_label.grid(column=0, row=5, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

# Start the GUI event loop
root.mainloop()