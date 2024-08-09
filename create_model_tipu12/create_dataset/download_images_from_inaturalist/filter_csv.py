import pandas as pd
import os

input_folder = 'Path/to/folder/with/all/observations.csv'
output_folder = 'Path/to/folder/with/all/output/filtered_observations.csv'
max_samples = 1500

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def count_photos(file_path, output_path):
    df = pd.read_csv(file_path)
    return len(df)

def filter_csv(file_path, step, output_path):
    df = pd.read_csv(file_path)

    # Select each stepth line
    filtered_df = df.iloc[::step, :]
    filtered_df.to_csv(output_path, index=False)

# Run for all csv
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)
        num_rows = count_photos(input_file_path, output_file_path)

        step = int(num_rows/max_samples)
        print("num_rows: ", num_rows)
        print("step: ", step)
        filter_csv(input_file_path, step, output_file_path)


print('Filtering done !')
