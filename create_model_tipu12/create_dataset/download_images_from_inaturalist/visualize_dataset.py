import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def count_images_per_class(data_dir):
    class_counts = {}
    for subset in ['train', 'test', 'val']:
        subset_dir = os.path.join(data_dir, subset)
        for class_name in os.listdir(subset_dir):
            class_dir = os.path.join(subset_dir, class_name)
            if os.path.isdir(class_dir):
                num_images = len([f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))])
                if class_name not in class_counts:
                    class_counts[class_name] = {'train': 0, 'test': 0, 'val': 0}
                class_counts[class_name][subset] += num_images
    return class_counts

data_dir = '/home/anthony/Anthony/Recup-dataset/Tipu-12'  # Remplacez par le chemin de votre dataset
class_counts = count_images_per_class(data_dir)

df = pd.DataFrame(class_counts).T
df['total'] = df.sum(axis=1)
df = df.reset_index().rename(columns={'index': 'class'})
print(df)

sns.set(style="whitegrid")

plt.figure(figsize=(15, 10))
sns.barplot(x='class', y='total', data=df)
plt.title('Nombre total d\'images par classe')
plt.xlabel('Classe')
plt.ylabel('Nombre d\'images')
plt.xticks(rotation=45)
plt.show()

df_melted = df.melt(id_vars=['class'], value_vars=['train', 'test', 'val'], var_name='subset', value_name='count')

plt.figure(figsize=(15, 10))
sns.barplot(x='class', y='count', hue='subset', data=df_melted)
plt.title('Répartition des images par sous-ensemble et par classe')
plt.xlabel('Classe')
plt.ylabel('Nombre d\'images')
plt.xticks(rotation=45)
plt.show()
