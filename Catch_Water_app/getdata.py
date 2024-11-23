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

def get_value(lat_x, long_x, column_name):
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour récupérer la valeur de la colonne spécifiée pour les coordonnées données
        query = sql.SQL("""
            SELECT {} FROM {}
            WHERE lat_x = %s AND lon_x = %s
            LIMIT 1;
        """).format(sql.Identifier(column_name), sql.Identifier(table_name))
        cursor.execute(query, (str(lat_x), str(long_x)))
        result = cursor.fetchone()

        # Vérifier que des résultats ont été trouvés
        if result:
            return str(result[0])
        else:
            return "Aucune donnée trouvée pour les coordonnées spécifiées."

    except Exception as e:
        return f"Erreur : {e}"

    finally:
        # Fermer la connexion
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

import pandas as pd
import psycopg2
from psycopg2 import sql
import re

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

def get_value_by_address(address, column_name):
    try:
        # Nettoyage de l'adresse pour retirer les suffixes "bis", "ter", etc.
        cleaned_address = re.sub(r'\b(bis|ter|quater|quinquies)\b', '', address, flags=re.IGNORECASE).strip()

        # Split de l'adresse pour séparer le numéro de la voie
        split_address = cleaned_address.split(' ', 1)
        if len(split_address) < 2:
            return "Erreur : L'adresse ne contient pas de numéro et de nom de voie valides."

        numero = split_address[0]
        nom_voie = split_address[1]

        # Connexion à PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour récupérer la valeur de la colonne spécifiée pour l'adresse donnée
        query = sql.SQL("""
            SELECT {} FROM {}
            WHERE numero = %s AND nom_voie = %s
            LIMIT 1;
        """).format(sql.Identifier(column_name), sql.Identifier(table_name))
        cursor.execute(query, (numero, nom_voie))
        result = cursor.fetchone()

        # Vérifier que des résultats ont été trouvés
        if result:
            return str(result[0])
        else:
            return "Aucune donnée trouvée pour l'adresse spécifiée."

    except Exception as e:
        return f"Erreur : {e}"

    finally:
        # Fermer la connexion
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def main():
    # Variables pour les coordonnées
    lat_x = -21.2169  # Exemple de latitude
    long_x = 55.354  # Exemple de longitude

    # Appel de la méthode pour récupérer et afficher la valeur d'une colonne spécifiée par coordonnées
    column_name = 'surface_m2'  # Exemple de colonne

    # Adresse pour l'exemple
    address = "10 Rue Paul Hermann"
    # Appel de la méthode pour récupérer et afficher la valeur d'une colonne spécifiée par adresse
    value_by_address = get_value_by_address(address, column_name)
    print(f"Valeur de '{column_name}' pour l'adresse '{address}' : {value_by_address}")

if __name__ == "__main__":
    main()
