import pandas as pd
import folium
import os
from geopy.distance import distance
import numpy as np

# Orders list and corresponding CSV
orders = {
    'Diptera': 'Diptera.csv',
    'Lepidoptera': 'Lepidoptera.csv',
    'Coleoptera': 'Coleoptera.csv',
    'Hymenoptera': 'Hymenoptera.csv',
    'Orthoptera': 'Orthoptera.csv',
    'Hemiptera': 'Hemiptera.csv',
    'Mantodea': 'Mantodea.csv',
    'Neuroptera': 'Neuroptera.csv',
    'Trichoptera': 'Trichoptera.csv',
    'Phasmida': 'Phasmida.csv',
    'Odonata': 'Odonata.csv',
    'Megaloptera': 'Megaloptera.csv'
}

# Create a map centered on a starting point (here, coordinates (0, 0))
m = folium.Map(location=[0, 0], zoom_start=2)

# Define a color palette for the different insect orders
colors = {
    'Diptera': 'blue',
    'Lepidoptera': 'red',
    'Coleoptera': 'green',
    'Hymenoptera': 'orange',
    'Orthoptera': 'purple',
    'Hemiptera': 'yellow',
    'Mantodea': 'pink',
    'Neuroptera': 'brown',
    'Trichoptera': 'cyan',
    'Phasmida': 'magenta',
    'Odonata': 'lime',
    'Megaloptera': 'black'
}

# List to store all aggregated data
grouped_data = []

# Dictionary to store layers (FeatureGroups) by insect order
insect_layers = {}

lgd_txt = '<span style="color: {col};">{txt}</span>'

# Load and aggregate data from each CSV file
for order, csv_file in orders.items():
    path_to_csv = os.path.join("/Path/to/csv/folder", csv_file)
    df = pd.read_csv(path_to_csv)
    df['insect_order'] = order  # Add the 'insect_order' column

    df = df.dropna(subset=['latitude', 'longitude'])

    # Aggregate data within a 50 km radius
    grouped = {}
    for _, row in df.iterrows():
        key_found = False
        for key, group in grouped.items():
            if not np.isnan(row['latitude']) and not np.isnan(row['longitude']):
                if distance((group['latitude'], group['longitude']), (row['latitude'], row['longitude'])).km <= 100:
                    group['number_of_observations'] += 1
                    key_found = True
                    break
        if not key_found:
            grouped[(row['latitude'], row['longitude'])] = {
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'number_of_observations': 1,
                'insect_order': order
            }

    grouped_data.extend(grouped.values())

# Add aggregated circles to the map and organize them into layers by insect order
for group in grouped_data:
    if group['insect_order'] not in insect_layers:
        insect_layers[group['insect_order']] = folium.FeatureGroup(name=lgd_txt.format(txt=group['insect_order'], col=colors.get(group['insect_order'], 'grey')))
    folium.CircleMarker(
        location=[group['latitude'], group['longitude']],
        radius=group['number_of_observations'] * 0.1,  # Adjust this factor according to your data
        color=colors.get(group['insect_order'], 'grey'),  # Use 'grey' if the order is not in the list
        fill=True,
        fill_color=colors.get(group['insect_order'], 'grey'),
        popup=(f"Order: {group['insect_order']}<br>"
               f"Observations: {group['number_of_observations']}<br>"
               f"Latitude: {group['latitude']}<br>"
               f"Longitude: {group['longitude']}"),
    ).add_to(insect_layers[group['insect_order']])

# Add each layer to the map
for layer in insect_layers.values():
    layer.add_to(m)

# Add layer control to select insect orders
folium.LayerControl(collapsed=False).add_to(m)

# Save the map to an HTML file
m.save('grouped_insects_map.html')

