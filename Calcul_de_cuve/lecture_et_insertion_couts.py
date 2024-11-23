import pandas as pd
import psycopg2

# Paramètres de connexion
HOST = 'localhost'
DATABASE = 'cashwater'
USER = 'postgres'
PASSWORD = '123'

# Nom du fichier Excel et de la table PostgreSQL
excel_file = "Couts_eau_outil.xlsx"
table_name = "Couts_eau_outil"

try:
    # Connexion à la base de données
    conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )
    cursor = conn.cursor()

    # Vérifier si la table existe
    cursor.execute(f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{table_name.lower()}'
        );
    """)
    table_exists = cursor.fetchone()[0]

    # Créer la table si elle n'existe pas
    if not table_exists:
        print(f"La table '{table_name}' n'existe pas. Création en cours...")
        cursor.execute(f"""
            CREATE TABLE {table_name} (
                Commune VARCHAR(255) NOT NULL,
                eau_et_ass NUMERIC(10, 2) NOT NULL,
                eau_potable NUMERIC(10, 2) NOT NULL
            );
        """)
        conn.commit()
        print(f"Table '{table_name}' créée avec succès.")

    # Charger le fichier Excel
    df = pd.read_excel(excel_file)

    # S'assurer que les colonnes ont les bons noms
    required_columns = ["Commune", "eau_et_ass", "eau_potable"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Le fichier Excel doit contenir les colonnes suivantes : {required_columns}")

    # Boucle d'insertion des données
    for _, row in df.iterrows():
        commune = row["Commune"]
        eau_et_ass = float(str(row["eau_et_ass"]).replace("€", "").replace(",", ".").strip())
        eau_potable = float(str(row["eau_potable"]).replace("€", "").replace(",", ".").strip())

        # Insérer les données dans la table PostgreSQL
        cursor.execute(f"""
            INSERT INTO {table_name} (Commune, eau_et_ass, eau_potable)
            VALUES (%s, %s, %s)
        """, (commune, eau_et_ass, eau_potable))
    
    # Valider les changements
    conn.commit()
    print("Données insérées avec succès.")

except Exception as e:
    print("Erreur :", e)

finally:
    # Fermer la connexion
    if cursor:
        cursor.close()
    if conn:
        conn.close()
