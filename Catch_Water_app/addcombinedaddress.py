import pandas as pd
import time
import sys

# Charger le fichier Excel
input_file_path = 'jointure_batiments_adresses.xlsx'  # Remplacez par le chemin de votre fichier Excel
output_file_path = 'new_jointure_batiments_adresses.xlsx'  # Chemin pour sauvegarder le fichier modifié

# Lire les données depuis le fichier .xlsx
df = pd.read_excel(input_file_path)

# Vérifier si les colonnes nécessaires sont présentes
required_columns = ['numero', 'rep', 'nom_voie']
if all(col in df.columns for col in required_columns):
    # Créer une nouvelle colonne "adresse" à partir des colonnes 'numero', 'rep', 'nom_voie'
    df['rep'] = df['rep'].fillna('')  # Remplacer les valeurs manquantes dans 'rep' par une chaîne vide

    total_rows = len(df)
    for index, row in df.iterrows():
        df.at[index, 'adresse'] = f"{row['numero']} {row['rep']} {row['nom_voie']}".replace('  ', ' ').strip()
        
        # Afficher la barre de chargement
        progress = (index + 1) / total_rows * 100
        sys.stdout.write(f"\rProgression : [{int(progress // 2) * '#'}{int(50 - progress // 2) * ' '}] {progress:.2f}%")
        sys.stdout.flush()
        time.sleep(0.05)

    # Ajouter la nouvelle colonne à la fin du DataFrame
    df = df[[*df.columns, 'adresse']]

    # Sauvegarder le fichier mis à jour
    df.to_excel(output_file_path, index=False)
    print(f"\nLe fichier modifié a été sauvegardé ici : {output_file_path}")
else:
    print("Les colonnes requises ne sont pas présentes dans le fichier.")
