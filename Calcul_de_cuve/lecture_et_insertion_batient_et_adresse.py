import pandas as pd
import psycopg2
from psycopg2 import sql

# Paramètres de connexion à PostgreSQL
db_config = {
    'host': 'localhost',        # Remplacez par l'hôte de votre base de données
    'dbname': 'project',        # Remplacez par le nom de votre base
    'user': 'postgres',            # Remplacez par votre nom d'utilisateur
    'password': '123',          # Remplacez par votre mot de passe
    'port': 5432                # Port par défaut de PostgreSQL
}

# Nom de la table dans la base de données
table_name = 'jointure_batiments_adresses'

# Chemin vers le fichier Excel
excel_file_path = r'jointure_batiments_adresses.xlsx'

try:
    # Affichez le chemin pour vérifier
    print(f"Lecture du fichier Excel : {excel_file_path}")

    # Charger le fichier Excel dans un DataFrame
    df = pd.read_excel(excel_file_path)

    # Connexion à PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Créer la table si elle n'existe pas
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f'"{col}" TEXT' for col in df.columns])}
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Insérer les données ligne par ligne
    for index, row in df.iterrows():
        insert_query = sql.SQL(f"""
        INSERT INTO {table_name} ({', '.join([f'"{col}"' for col in df.columns])})
        VALUES ({', '.join(['%s'] * len(df.columns))});
        """)
        cursor.execute(insert_query, tuple(row))

    # Valider les changements
    conn.commit()

    print(f"Les données ont été insérées avec succès dans la table {table_name}.")

except FileNotFoundError as fnf_error:
    print(f"Erreur : Fichier introuvable. Vérifiez le chemin : {excel_file_path}")
except Exception as e:
    print(f"Erreur : {e}")

finally:
    # Fermer la connexion
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn:
        conn.close()
