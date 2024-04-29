# Import the modules
# %matplotlib inline
import numpy as np
import smtk.trellis.trellis_plots as trpl
from openquake.hazardlib.gsim import get_available_gsims
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import smtk.trellis.configure as rcfg
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Label
import customtkinter


def get_base_name(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def create_directories(base_folder):
    for category in ['magnitude_comparison', 'distance_analysis', 'pga_analysis']:
        dir_path = os.path.join(base_folder, category)
        os.makedirs(dir_path, exist_ok=True)

# Function to create dynamic label text
def create_label(year, magnitude, pga, distances):
    return (f'Recorded Leyte {year}, {magnitude}\n'
            f'PGA: {pga}\n'
            f'repi: {distances["repi"]}\n'
            f'rjb: {distances["rjb"]}\n'
            f'rrup: {distances["rrup"]}\n'
            f'rx: {distances["rx"]}\n'
            f'ry0: {distances["ry0"]}')


# def create_radio_buttons(container):
#     global pga_radio, sa_radio

#     # Using a frame to group the radio buttons together
#     radio_frame = tk.Frame(container)

#     # Create the radio buttons inside radio_frame
#     pga_radio = tk.Radiobutton(radio_frame, text="PGA", variable=selected_process, value="PGA", state="disabled")
#     pga_radio.grid(row=0, column=0)

#     sa_radio = tk.Radiobutton(radio_frame, text="SA", variable=selected_process, value="SA", state="disabled")
#     sa_radio.grid(row=0, column=1)

#     # Grid the radio_frame itself in the container
#     radio_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

def create_radio_buttons(container):
    global pga_radio, sa_radio

    # Using a frame to group the radio buttons together
    radio_frame = customtkinter.CTkFrame(container, fg_color="transparent")
    

    # Create the radio buttons inside radio_frame
    pga_radio = customtkinter.CTkRadioButton(radio_frame, text="PGA", variable=selected_process, value="PGA")
    pga_radio.grid(row=0, column=0)

    sa_radio = customtkinter.CTkRadioButton(radio_frame, text="SA", variable=selected_process, value="SA")
    sa_radio.grid(row=0, column=1)

    # Grid the radio_frame itself in the container
    radio_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    
def process_data(file_path, year):
    try:
        data = pd.read_csv(file_path)
        
        # Get the directory of the input CSV file
        csv_directory = os.path.dirname(file_path)

        # Create the base folder in the same directory as the CSV file
        base_folder = os.path.join(csv_directory, get_base_name(file_path))
        create_directories(base_folder)
        
        global selected_process  # Make sure to declare the global variable
        process_type = selected_process.get()  # Retrieve the selected value (PGA or SA)
        
        
        # Set up the configuration
        GMPES = get_available_gsims()
        gmpe_list = [
                "AbrahamsonEtAl2014",
                "BooreAtkinson2008",
                "BooreAtkinson2011",
                "BooreEtAl2014",
                "BooreEtAl2014LowQ",
                "CampbellBozorgnia2014",
                "CampbellBozorgnia2014LowQ",
                "ChiouYoungs2008",
                "ChiouYoungs2014",
                "FukushimaTanaka1990",
                "FukushimaTanakaSite1990",
                "SadighEtAl1997",
                "ZhaoEtAl2006Asc"
        ]
        
        gmpe_list_SA = [
                "AbrahamsonEtAl2014",
                "BooreAtkinson2008",
                "BooreAtkinson2011",
                "BooreEtAl2014",
                "BooreEtAl2014LowQ",
                "CampbellBozorgnia2014",
                "CampbellBozorgnia2014LowQ",
                "ChiouYoungs2008",
                "ChiouYoungs2014",
                #"FukushimaTanaka1990",
                #"FukushimaTanakaSite1990",
                "SadighEtAl1997",
                "ZhaoEtAl2006Asc"
        ]
        
        gmpe_list_PGV = [
                "AbrahamsonEtAl2014",
                "BooreAtkinson2008",
                "BooreAtkinson2011",
                "BooreEtAl2014",
                "BooreEtAl2014LowQ",
                "CampbellBozorgnia2014",
                "CampbellBozorgnia2014LowQ",
                "ChiouYoungs2008",
                "ChiouYoungs2014"
        ]

        # Parameters are from SMTK Manual
        # imts_sa = ["SA(0.2)", "SA(1.0)", "SA(2.0)","PGA"] # if included FukushimaTanaka1990 and FukushimaTanakaSite1990 excluded
        imts = ["PGA"] 
        magnitudes = np.arange(4.0,7.1, 0.1)
        pga_data = {gmpe: [] for gmpe in gmpe_list}

        sns.set_theme(style="whitegrid")  # You can try different styles like "whitegrid", "dark", "white", and "ticks"
        
        # Choose the GMPE list based on the selected process type
        if process_type == "SA":
            gmpe_list = gmpe_list_SA
            imts = ["SA(0.2)", "SA(1.0)", "SA(2.0)", "PGA"]  # Uncomment or modify as needed
        else:  # Default to PGA if not SA
            gmpe_list = gmpe_list
            imts = ["PGA"] 

        # Define the markers for each GMPE
        gmpe_styles = {
            "AbrahamsonEtAl2014": {"marker": "o"},
            "BooreAtkinson2008": {"marker": "^"},
            "BooreAtkinson2011": {"marker": "s"},
            "BooreEtAl2014": {"marker": "x"},
            "BooreEtAl2014LowQ": {"marker": "D"},
            "CampbellBozorgnia2014": {"marker": "v"},
            "CampbellBozorgnia2014LowQ": {"marker": "<"},
            "ChiouYoungs2008": {"marker": ">"},
            "ChiouYoungs2014": {"marker": "p"},
            "FukushimaTanaka1990": {"marker": "P"},
            "FukushimaTanakaSite1990": {"marker": "*"},
            "SadighEtAl1997": {"marker": "h"},
            "ZhaoEtAl2006Asc": {"marker": "+"}
        }

        # Create a list of unique markers from the gmpe_styles dictionary
        markers = [style["marker"] for style in gmpe_styles.values()]

        # Use Seaborn's color palette for the markers
        palette = sns.color_palette("deep", len(markers))

        # Combine markers and colors into a dictionary
        marker_colors = dict(zip(markers, palette))

        # Iterate through each row in the CSV and generate plots
        for index, row in data.iterrows():
            # Extract the necessary values from the row
            magnitude = row['magnitude']
            pga = row['pga']
            distances = {"repi": row['repi'], "rjb": row['rjb'], "rrup": row['rrup'], "rx": row['rx'], "ry0": row['ry0']}
            params = {
                "ztor": row['ztor'],
                "hypo_depth": row['hypo_depth'],
                "dip": row['dip'],
                "rake": row['rake'],
                "width": row['width'],
                "vs30": row['vs30'],
                "vs30measured": True,  # Assuming Vs30 value is always measured
                "z1pt0": row['z1pt0'],
                "z2pt5": row['z2pt5']
            }
            
            # Plotting
            mag_plot = trpl.MagnitudeIMTTrellis(magnitudes, distances, gmpe_list, imts, params, dpi=400, figure_size=(20, 15))
            
            # mag_plot.export_to_csv("output.csv")
            
            plt.figure()
                
            mag_plot.plot()
            
            # dis_plot = trpl.DistanceIMTTrellis(magnitude, distances1, gmpe_list, imts, params, distance_type='rjb', plot_type='loglog', dpi=400, figure_size=(20, 15))
            
            rupt1 = rcfg.GSIMRupture(magnitude=magnitude,   # Moment magnitude
                                dip=params['dip'],   # Dip of Rupture
                                aspect=1.5, # Aspect Ratio of Rupture
                                rake=params['rake'],  # Rake of rupture 
                                ztor=params['ztor'],  # Top of rupture depth
                                # strike=0.0,  # Strike of rupture
                                # hypocentre_location=hypo_loc   # Location of hypocentre within rupture plane
                                )
            # It is critical that before running the trellis plots, the site configuration must be run!!!!
            _ = rupt1.get_target_sites_line(200.0, 1.0, params['vs30'])
            # rupt1.plot_model_configuration()
            
            dis_plot = trpl.DistanceIMTTrellis.from_rupture_model(rupt1, gmpe_list, imts, dpi=400, figure_size=(20, 15))

            
            # Find the nearest index for the specified magnitude
            nearest_idx = np.searchsorted(magnitudes, magnitude, side="left")

            # Retrieve and plot the PGA values for each GMPE at the nearest magnitude
            gmvs = mag_plot.get_ground_motion_values()
            
            # List to collect legend handles and labels
            legend_handles_labels = []
            
            # List to collect bar heights and labels
            bar_heights = []
            bar_labels = []
            
            for gmpe_name in gmpe_list:
                if nearest_idx < len(magnitudes) and magnitudes[nearest_idx] == magnitude:
                    # Assume the GMVs are arrays, take the mean value
                    pga_value = np.mean(gmvs[gmpe_name]['PGA'][nearest_idx])
                else:
                    # Handle the case where the exact magnitude is not in the range
                    if nearest_idx == 0 or nearest_idx == len(magnitudes):
                        # Take the mean value for the first or last set of GMVs
                        pga_value = np.mean(gmvs[gmpe_name]['PGA'][nearest_idx])
                    else:
                        # Interpolate between the two nearest sets of GMVs
                        pga_values_below = np.mean(gmvs[gmpe_name]['PGA'][nearest_idx - 1])
                        pga_values_above = np.mean(gmvs[gmpe_name]['PGA'][nearest_idx])
                        pga_value = np.interp(magnitude,
                                            [magnitudes[nearest_idx - 1], magnitudes[nearest_idx]],
                                            [pga_values_below, pga_values_above])
                        
                # Append the PGA value to the list for bar graph
                bar_heights.append(pga_value)
                bar_labels.append(f"{gmpe_name}: {pga_value:.3f}")


                # Plot the PGA value with a distinct marker and color
                style = gmpe_styles.get(gmpe_name, {"marker": "o"})  # Default style if GMPE not in dict
                color = marker_colors.get(style["marker"], "black")  # Use Seaborn color if marker is in the palette
                plot_handle, = plt.plot(magnitude, pga_value, style['marker'], color=color, markersize=12, label=f"{gmpe_name}: {pga_value:.3f}" if index == 0 else "")

                # Append the handle and label to the list
                legend_handles_labels.append((plot_handle, f"{gmpe_name}: {pga_value:.3f}"))

            # Store the PGA value in the dictionary
            pga_data[gmpe_name].append(pga_value)
            
            def ensure_single_value(value):
                if isinstance(value, (list, tuple)) and len(value) == 1:
                    # Return the single element if it's a list or tuple with one element
                    return value[0]
                return value

            # Convert each value in distances to a single value if it's a list or tuple
            distances = {
                "repi": ensure_single_value(row['repi']),
                "rjb": ensure_single_value(row['rjb']),
                "rrup": ensure_single_value(row['rrup']),
                "rx": ensure_single_value(row['rx']),
                "ry0": ensure_single_value(row['ry0'])
            }
            
            plt.axvline(x=magnitude, color='gray', linestyle='--', linewidth=2, alpha=0.5)
            #plt.text(magnitude - 0.3, pga, create_label(2023, magnitude, pga, distances), fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
            #plt.plot(magnitude, pga, '*', markersize=15, color='yellow')
            
            # Add legend entry with yellow star marker and text label
            legend_label = create_label(year, magnitude, pga, distances)
            star_handle, = plt.plot(magnitude, pga, '*', markersize=15, color='#DB4437', label=legend_label)
            legend_handles_labels.append((star_handle, legend_label))
            

            # Customizing the aesthetics of the plot
            plt.title(f"{row['eq_event_id']} - {row['station']}, {magnitude}", fontsize=20)
            plt.xlabel('Magnitude', fontsize=16)
            plt.ylabel('PGA (g)', fontsize=16)
            
            # Add legend entry with yellow star marker and text label
            plt.legend(handles=[handle for handle, _ in legend_handles_labels],
                    labels=[label for _, label in legend_handles_labels], bbox_to_anchor=(1, 1), fontsize=14, frameon=False)
            
            
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            
            file_name = f"plot_{row['eq_event_id']}_{row['station']}_PGA.png"
            file_name = file_name.replace(' ', '_').replace(',', '_').replace('/', '_')
            
            # plt.savefig(file_name)
            
            # plt.show()
            mag_plot_file = os.path.join(base_folder, 'magnitude_comparison', file_name)
            plt.savefig(mag_plot_file)
            plt.clf()
            
            ########################################################################################
            
            plt.figure()

            dis_plot.plot()
            
            # Customizing the aesthetics of the plot
            plt.title(f"{row['eq_event_id']} - {row['station']}, {magnitude}", fontsize=20)
            
            plt.legend(bbox_to_anchor=(1, 1), fontsize=14, frameon=False)
            
            # Save dis_plot
            dis_plot_file_name = f"dis_plot_{row['eq_event_id']}_{row['station']}_PGA.png"
            dis_plot_file_name = dis_plot_file_name.replace(' ', '_').replace(',', '_').replace('/', '_')
            # plt.savefig(dis_plot_file_name)
            
            dis_plot_file = os.path.join(base_folder, 'distance_analysis', dis_plot_file_name)
            plt.savefig(dis_plot_file)
            plt.clf()
            
            ######################################################################################
            
            # Convert bar_heights to a NumPy array
            bar_heights_np = np.array(bar_heights)

            # Find the index of the highest PGA value
            max_index = np.argmax(bar_heights_np)

            # Find the index of the closest PGA value
            closest_index = np.nanargmin(np.abs(bar_heights_np - row['pga']))

            # Plot the bar graph using Seaborn colors
            plt.bar(np.arange(len(gmpe_list)), bar_heights, tick_label=bar_labels, color='gray')
            plt.bar(max_index, bar_heights[max_index], color='#DB4437', label=f'Highest PGA: {bar_labels[max_index]}')

            if not np.isnan(row['pga']):
                plt.bar(closest_index, bar_heights[closest_index], color='#4285F4', label=f'Closest PGA: {bar_labels[closest_index]}')

                # Add a horizontal line for the recorded PGA value
                plt.axhline(y=row['pga'], color='#F4B400', linestyle='--', label=f'Recorded PGA: {row["pga"]:.3f}')  

            # Customizing the aesthetics of the bar graph
            plt.title(f"{row['eq_event_id']} - {row['station']}, {magnitude}", fontsize=20)
            plt.xlabel('GMPE', fontsize=16)
            plt.ylabel('PGA (g)', fontsize=16)

            # Rotate x-axis labels to 45 degrees for better readability
            plt.xticks(rotation=45, ha='right', fontsize=14)

            # Add legend entry with yellow star marker and text label
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=14, ncol=1, frameon=False)

            plt.yticks(fontsize=14)

            file_name = f"bar_plot_{row['eq_event_id']}_{row['station']}_PGA.png"
            file_name = file_name.replace(' ', '_').replace(',', '_').replace('/', '_')

            plt.tight_layout()  # Adjust layout to prevent clipping of the legend
            # plt.savefig(file_name)

            # plt.show()
            
            bar_plot_file = os.path.join(base_folder, '  ', file_name)
            plt.savefig(bar_plot_file)
            plt.clf()

        status_label.configure(text="Status: Done")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_file():
    global pga_radio, sa_radio
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        file_path_label.configure(text=file_path)
        process_button.configure(state="normal")
        pga_radio.configure(state="normal")  # Enable radio buttons if a file is selected
        sa_radio.configure(state="normal")
    else:
        file_path_label.configure(text="No file selected")
        process_button.configure(state="disabled")
        pga_radio.configure(state="disabled")  # Keep radio buttons disabled if no file is selected
        sa_radio.configure(state="disabled")

def on_process_click():
    file_path = file_path_label.cget("text")
    year = year_entry.get()
    if not year.isdigit():
        messagebox.showerror("Error", "Invalid year. Please enter a valid year.")
        return
    status_label.configure(text="Status: Processing...")
    root.update_idletasks()
    process_data(file_path, year)

## Create the main window
root = customtkinter.CTk()
root.title("SMTK GMPE Analysis")
root.geometry("700x200")  # Adjust the size as needed

# Set default window size and start position (center screen)
window_width = 800
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# Styling Variables
font_style = "Arial"
font_size = 12
padding = 10
font_tuple = (font_style, font_size)

# Initialize the global variable after creating the root window
selected_process = tk.StringVar(value="PGA")

# # Create a Frame for input widgets
# input_frame = tk.Frame(root)
# input_frame.pack(padx=10, pady=10)

# Create a Frame for input widgets
input_frame = customtkinter.CTkFrame(root, fg_color="transparent")
input_frame.pack(padx=20, pady=20)

# # Create widgets inside input_frame
# file_path_label = tk.Label(input_frame, text="No file selected", font=(font_style, font_size))
# browse_button = tk.Button(input_frame, text="Browse CSV", command=browse_file, font=(font_style, font_size))
# # Create a label for the year input
# year_label = tk.Label(input_frame, text="Enter Year:", font=(font_style, font_size))
# year_entry = tk.Entry(input_frame, font=(font_style, font_size))
# process_button = tk.Button(input_frame, text="Process Data", command=on_process_click, state="disabled", font=(font_style, font_size))
# status_label = tk.Label(input_frame, text="Status: Idle", font=(font_style, font_size))

# Create widgets inside input_frame
file_path_label = customtkinter.CTkLabel(input_frame, text="No file selected", font=font_tuple)
browse_button = customtkinter.CTkButton(input_frame, text="Browse CSV", command=browse_file, font=font_tuple)
# Create a label for the year input
year_label = customtkinter.CTkLabel(input_frame, text="Enter Year:", font=font_tuple)
year_entry = customtkinter.CTkEntry(input_frame, font=font_tuple)
process_button = customtkinter.CTkButton(input_frame, text="Process Data", command=on_process_click, state="disabled", font=font_tuple)
status_label = customtkinter.CTkLabel(input_frame, text="Status: Idle", font=font_tuple)

# Create radio buttons
create_radio_buttons(input_frame)

# # Layout the widgets using grid
# file_path_label.grid(row=0, column=0, sticky="w", pady=padding)
# browse_button.grid(row=0, column=1, sticky="e", padx=padding)
# year_label.grid(row=1, column=0, sticky="w")  # Align the new label to the left
# year_entry.grid(row=1, column=1, sticky="ew", pady=padding)  # Place the year entry next to the label
# process_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=padding)
# status_label.grid(row=4, column=0, columnspan=2, sticky="ew", pady=padding)

# Layout the widgets using grid
file_path_label.grid(row=0, column=0, sticky="w", pady=padding)
browse_button.grid(row=0, column=1, sticky="e", padx=padding)
year_label.grid(row=1, column=0, sticky="w")
year_entry.grid(row=1, column=1, sticky="ew", pady=padding)
process_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=padding)
status_label.grid(row=4, column=0, columnspan=2, sticky="ew", pady=padding)

# Start the application
root.mainloop()