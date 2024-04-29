import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import *
import pandas as pd
import numpy as np
import csv
from openquake.hazardlib.geo import (
    Point, Line, PlanarSurface, MultiSurface, SimpleFaultSurface,
    ComplexFaultSurface, RectangularMesh
)
from matplotlib import pyplot
from mpl_toolkits.basemap import Basemap
import time
from threading import Thread
import os  # Import the os module for file existence check
import customtkinter

# Your processing function
def process_eqrm_data_and_find_closest(row, sites_df):
    # Create PlanarSurface from the row data
    surf = PlanarSurface(
        strike=row['strike'], dip=row['dip'],
        top_left=Point(row['top_left_lon'], row['top_left_lat'], row['top_left_depth']),
        top_right=Point(row['top_right_lon'], row['top_right_lat'], row['top_right_depth']),
        bottom_left=Point(row['bottom_left_lon'], row['bottom_left_lat'], row['bottom_left_depth']),
        bottom_right=Point(row['bottom_right_lon'], row['bottom_right_lat'], row['bottom_right_depth'])
    )
    
    # Define buffer and delta for the grid
    buf = 1.8
    delta = 0.001

    # Get bounding box
    min_lon, max_lon, max_lat, min_lat = surf.get_bounding_box()
    min_lon -= buf
    max_lon += buf
    min_lat -= buf
    max_lat += buf

    # Create grid of points
    lons = np.arange(min_lon, max_lon + delta, delta)
    lats = np.arange(min_lat, max_lat + delta, delta)
    lons, lats = np.meshgrid(lons, lats)
    mesh = RectangularMesh(lons=lons, lats=lats, depths=None)

    # Calculate distances
    r_rup = surf.get_min_distance(mesh)
    r_jb = surf.get_joyner_boore_distance(mesh)
    r_x = surf.get_rx_distance(mesh)
    r_y0 = surf.get_ry0_distance(mesh)

    # Flatten the arrays
    lats_flattened = np.ravel(mesh.lats)
    lons_flattened = np.ravel(mesh.lons)
    r_rup_flattened = np.ravel(r_rup)
    r_jb_flattened = np.ravel(r_jb)
    r_x_flattened = np.ravel(r_x)
    r_y0_flattened = np.ravel(r_y0)

    # Flatten the arrays and combine them into a single array
    combined_array = np.column_stack((lats_flattened, lons_flattened, r_rup_flattened, r_jb_flattened, r_x_flattened, r_y0_flattened))

    # Write the combined array to a CSV file for each event
    with open(f"{row['eqe_name']}.csv", 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['LAT', 'LONG', 'Rrup', 'Rjb', 'Rx', 'Ry0'])
        for data_row in combined_array:
            csvwriter.writerow(data_row)

    # Find the closest grid point for each site
    closest_points = []
    for _, site in sites_df.iterrows():
        distances = np.sqrt((lats_flattened - site['Lat'])**2 + (lons_flattened - site['Long'])**2)
        closest_idx = np.argmin(distances)
        closest_points.append({
            'eqe_name': row['eqe_name'],
            'Strong Motion Site': site['Strong Motion Site'],
            'SiteLat': site['Lat'],
            'SiteLong': site['Long'],
            'Rrup': r_rup_flattened[closest_idx],
            'Rjb': r_jb_flattened[closest_idx],
            'Rx': r_x_flattened[closest_idx],
            'Ry0': r_y0_flattened[closest_idx]
        })

    return closest_points

# Set up the GUI
root = customtkinter.CTk()
root.title("EQRM Data Processor")
root.geometry("600x400")  # Set window size
# root.configure(bg='#f0f0f0')  # Set background color

customtkinter.set_appearance_mode("dark")

# Padding
padx, pady = 10, 5

# Create a label for displaying results or messages
# Outside of any function, where your widgets are initialized
result_label = customtkinter.CTkLabel(root, text="")
result_label.pack(pady=pady)  # Separate the packing to its own line

# # Loading indicator (initially empty)
loading_label = customtkinter.CTkLabel(root, text="")
loading_label.pack(pady=pady)


def select_file(entry_widget):
    filename = filedialog.askopenfilename()
    entry_widget.delete(0, END)  # Clear the current text
    if filename:
        entry_widget.insert(0, filename)  # Insert the new filename
    else:
        entry_widget.insert(0, "No file selected")  # Display default text

def update_loading_label():
    global loading_label
    # Update the label with moving ellipses
    loading_text = "Processing" + "." * ((update_loading_label.count % 4) + 1)
    loading_label.configure(text=loading_text)
    update_loading_label.count += 1
    if processing:
        # Schedule this function to be called again after 500ms
        root.after(500, update_loading_label)
update_loading_label.count = 0

def process_files_thread():
    global processing
    processing = True

    start_time = time.time()  # Start time measurement

    try:        
        sites_file = sites_label.get()
        events_file = events_label.get()

        # Load data with error checks
        sites_df = pd.read_csv(sites_file)
        input_events_df = pd.read_csv(events_file)
        

        # Check for required columns in sites_df
        required_sites_columns = ['Lat', 'Long', 'Strong Motion Site']
        if not all(column in sites_df.columns for column in required_sites_columns):
            raise ValueError("Sites CSV file does not contain required columns.")

        # Check for required columns in input_events_df
        required_events_columns = ['strike', 'dip', 'top_left_lon', 'top_left_lat', 'top_left_depth',
                                   'top_right_lon', 'top_right_lat', 'top_right_depth',
                                   'bottom_left_lon', 'bottom_left_lat', 'bottom_left_depth',
                                   'bottom_right_lon', 'bottom_right_lat', 'bottom_right_depth', 'eqe_name']
        if not all(column in input_events_df.columns for column in required_events_columns):
            raise ValueError("Events CSV file does not contain required columns.")

        # Process data
        closest_data = []
        for _, row in input_events_df.iterrows():
            closest_data.extend(process_eqrm_data_and_find_closest(row, sites_df))

        # Convert to DataFrame and save
        closest_df = pd.DataFrame(closest_data)
        closest_df.to_csv('output_closest_points.csv', index=False)

    except Exception as e:
        result_label.configure(text=f"Error: {e}")
        processing = False
        root.after(0, lambda: loading_label.configure(text=""))
        return

    end_time = time.time()  # End time measurement
    elapsed_time = end_time - start_time  # Calculate elapsed time

    processing = False  # Stop loading animation
    root.after(0, lambda: loading_label.configure(text=""))  # Clear loading label
    result_label.configure(text=f"Processing complete! File saved as 'output_closest_points.csv'\nTime elapsed: {elapsed_time:.2f} seconds")

def process_files():
    global result_label
    # sites_file = sites_label.cget("text")
    # events_file = events_label.cget("text")
    sites_file = sites_label.get()  
    events_file = events_label.get()  
    
    # Check if both files are selected
    if sites_file == "No file selected" or events_file == "No file selected":
        result_label.configure(text="Error: Please add both files as they are required for the process.")
        return

    # Check if the selected files exist
    if not os.path.exists(sites_file) or not os.path.exists(events_file):
        result_label.configure(text="Error: One or both files do not exist.")
        return

    # If checks pass, start processing in a separate thread
    Thread(target=process_files_thread, daemon=True).start()
    update_loading_label()

# Variable for setting text in CTkEntry
events_text = tk.StringVar()
sites_text = tk.StringVar()

# Set initial text for CTkEntry widgets
events_text.set("No file selected")
sites_text.set("No file selected")

customtkinter.CTkLabel(root, text="Select Site CSV:").pack(pady=pady)
# sites_label = customtkinter.CTkLabel(root, text="No file selected")
# sites_label.pack(pady=pady)
sites_label = customtkinter.CTkEntry(root, state='normal', width=400)
sites_label.insert(0, "No file selected")
sites_label.pack(pady=pady)
customtkinter.CTkButton(root, text="Browse", command=lambda: select_file(sites_label)).pack(pady=pady)

customtkinter.CTkLabel(root, text="Select Events CSV:").pack(pady=pady)
# events_label = customtkinter.CTkLabel(root, text="No file selected")
# events_label.pack(pady=pady)
events_label = customtkinter.CTkEntry(root, state='normal', width=400)
events_label.insert(0, "No file selected")
events_label.pack(pady=pady)
customtkinter.CTkButton(root, text="Browse", command=lambda: select_file(events_label)).pack(pady=pady)

process_button = customtkinter.CTkButton(root, text="Process", command=lambda: process_files()).pack(pady=15)

processing = False  # Flag to indicate if processing is happening

# Run the application
root.mainloop()