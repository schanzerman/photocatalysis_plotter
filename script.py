#%% SETUP
# Set the directory path where the CSV files are located
directory = "Set the directory path where the CSV files are located"

sample = directory.split('/')[-1]

#%% DEFINITIONS
def plotting(directory,sample):
    import matplotlib.pyplot as plt
    from matplotlib import cm

    # Create a figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Split the groups into two halves
    groups = list(result.groupby('file_name'))
    first_half = groups[:9]
    second_half = groups[9:]

    # Define color maps
    color_map1 = cm.get_cmap('tab20', 9)
    color_map2 = cm.get_cmap('Set2', 9)

    # Plot the first half in the left subplot with the first color map
    for i, (name, group) in enumerate(first_half):
        short_name = name[4:7]
        ax1.plot(group['wavelength'], group['absorbance'], label=short_name, color=color_map1(i))

    # Plot the second half in the right subplot with the second color map
    for i, (name, group) in enumerate(second_half):
        short_name = name[4:7]
        ax2.plot(group['wavelength'], group['absorbance'], label=short_name, color=color_map2(i))

    # Set plot titles, labels, and x-axis range for both subplots
    ax1.set_title("250 nm UV source")
    ax1.set_xlabel("Wavelength (nm)", fontsize=14)
    ax1.set_ylabel("Absorbance (%)", fontsize=14)
    ax1.set_xlim(peak_at_where-7, peak_at_where+7)
    ax1.set_ylim(abs_min*0.99, abs_max*1.01)  # Ensure abs_min and abs_max are defined
    ax1.legend()

    ax2.set_title("310 nm UV source")
    ax2.set_xlabel("Wavelength (nm)", fontsize=14)
    ax2.set_ylabel("Absorbance (%)", fontsize=14)
    ax2.set_xlim(peak_at_where-7, peak_at_where+7)
    ax2.set_ylim(abs_min*0.99, abs_max*1.01)  # Ensure abs_min and abs_max are defined
    ax2.legend()

    # Adjust the sizes
    ax1.legend(fontsize='12')  # Adjust size as needed
    ax2.legend(fontsize='12')  # Adjust size as needed
    ax1.tick_params(axis='both', labelsize=12)  # Adjust size as needed
    ax2.tick_params(axis='both', labelsize=12)  # Adjust size as needed
    # ax.set_title("Title", fontsize=16)

    # Adjust layout for better display
    plt.tight_layout()
    plt.savefig(f'{directory}/{sample}.png', dpi=600)
    plt.show()

def degradation(directory,sample):
    import pandas as pdA
    import numpy as np
    import re

    # Assuming 'peak_data' is your DataFrame
    # Extract the numeric time value from 'file_name' and create a new column
    peak_data['time'] = peak_data['file_name'].apply(lambda x: int(re.findall(r'_(\d+)', x)[0]))

    # Separate the data into two groups based on '250' and '310' in 'file_name'
    group_250 = peak_data[peak_data['file_name'].str.contains('250')]
    group_310 = peak_data[peak_data['file_name'].str.contains('310')]

    # Function to process each group
    def process_group(group):
        # Find the reference absorbance (time = 000)
        ref_absorbance = group[group['time'] == 0]['absorbance'].iloc[0]

        group['normalized_diff'] = (group['absorbance'] / ref_absorbance)
        # Handle division by zero by setting those values to NaN or zero
        group['normalized_diff'].replace([float('inf'), -float('inf')], np.nan, inplace=True)

        return group

    # Apply the function to each group
    group_250_processed = process_group(group_250)
    group_310_processed = process_group(group_310)

    # Combine the groups back into a single DataFrame
    processed_peak_data = pd.concat([group_250_processed, group_310_processed])

    # Display the processed DataFrame
    processed_peak_data

    import matplotlib.pyplot as plt

    plt.rc('font', family='serif')
    plt.rc('xtick', labelsize='x-small')
    plt.rc('ytick', labelsize='x-small')

    fig = plt.figure(figsize=(4, 3))

    # Plotting the '250' group
    plt.plot(group_250_processed['time'], group_250_processed['normalized_diff'], label='250 nm UV', color='k', ls='solid')

    # Plotting the '310' group
    plt.plot(group_310_processed['time'], group_310_processed['normalized_diff'], label='310 nm UV', color='.5', ls='dashed')

    # Adding title and labels
    # plt.title('Normalized Absorbance Difference Over Time')
    plt.xlabel('Time (min)')
    plt.ylabel('C$_t$/C$_0$')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'{directory}/{sample}_deg.png', dpi=600)
    plt.show()


#%% DATA WRANGLING
import csv
import os
import pandas as pd

# Create an empty list to store the DataFrames
dataframes = []

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a CSV
    if filename.endswith(".csv"):
        # Open the file
        with open(os.path.join(directory, filename), 'r') as file:
            # Create a DataFrame from the CSV file
            df = pd.read_csv(file, sep=';')
            df['file_name'] = filename
            df = df.drop(0, axis=0)
            # Append the DataFrame to the list
            dataframes.append(df)


# Concatenate all the DataFrames into one
result = pd.concat(dataframes)


# result = result.rename(columns={'rée comme nouveau jeu de données': 'wavelength'})
result = result.rename(columns={result.columns[0]: 'wavelength'})
result['merged_column'] = result['TiO2 + 250'].combine_first(result['TiO2 + 310'])
result = result.rename(columns={'merged_column': 'absorbance'})
result.drop(columns=['TiO2 + 310','TiO2 + 250'], inplace=True)


#Replace the decimal point and make them number for wavelength
result['wavelength'] = result['wavelength'].apply(lambda x: x.replace(',', '.'))
result['wavelength'] = result['wavelength'].apply(lambda x: float(x))
result['wavelength'] = result['wavelength'].apply(lambda x: int(x))

# Do the same for absorbance values
result['absorbance'] = result['absorbance'].apply(lambda x: x.replace(',', '.'))
result['absorbance'] = result['absorbance'].apply(lambda x: float(x))

#Drop the reference rows
result = result[result['file_name'].str.contains("%") == False]
result = result.sort_values(by=['wavelength'], ascending=True)

list_ref = result[result.values == 800]

l2 = []

for i in list(range(0,len(result))):
    for j in list(range(0,len(list_ref))):
        if result['file_name'].iloc[[i]].values[0] == list_ref['file_name'].iloc[[j]].values[0]:
            a = result['absorbance'].iloc[[i]].values[0] - list_ref['absorbance'].iloc[[j]].values[0]
            l2.append(a)
            
result['absorbance'] = l2

list_range = result[result['wavelength'].values > 400]
list_range = list_range[list_range['wavelength'].values < 600]
peak_at_where = list_range['wavelength'][list_range['absorbance'].idxmax()].values[0]
print(peak_at_where)
    
peak_data = result[result['wavelength'].values == peak_at_where].sort_values('file_name')
peak_data['file_name'] = peak_data['file_name'].str.slice(0, 7)
peak_data

abs_min = min(peak_data['absorbance'])
abs_max = max(peak_data['absorbance'])

plotting(directory,sample)
degradation(directory,sample)
