import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Paramètres de connexion à la base PostgreSQL
db_config = {
    'host': 'localhost',        # Adresse de votre serveur PostgreSQL
    'port': '5432',             # Port PostgreSQL (par défaut : 5432)
    'database': 'project',    # Nom de la base de données
    'user': 'postgres',         # Nom d'utilisateur
    'password': '123'           # Mot de passe
}

# Construire l'URL de connexion
connection_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Créer un moteur SQLAlchemy
engine = create_engine(connection_url, echo=True)

# Définir la base pour les modèles
Base = declarative_base()

# Définir le modèle ORM pour la table 'stations'
class Station(Base):
    __tablename__ = 'stations'

    NUM_POSTE = Column(Integer, primary_key=True)
    NOM_STATION = Column(String)
    LAT = Column(Float)
    LON = Column(Float)
    ALTI = Column(Integer)

# Créer la table dans la base de données si elle n'existe pas déjà
Base.metadata.create_all(engine)

# Charger les données CSV dans un DataFrame pandas
csv_file = "FINAL_STATIONS2012_2022.csv"  # Remplacez par le chemin réel du fichier CSV
try:
    # Spécifiez explicitement le séparateur (points-virgules)
    df = pd.read_csv(csv_file, sep=';')  # Changez 'sep' à ';' pour correspondre au séparateur de colonnes dans votre CSV

    # Afficher les colonnes et le nombre de colonnes
    print(f"Noms des colonnes détectées dans le fichier CSV : {df.columns.tolist()}")
    print(f"Nombre de colonnes dans le fichier CSV : {len(df.columns)}")

    # Nettoyer les noms des colonnes
    df.columns = df.columns.str.strip()

    # Mapper les colonnes si nécessaire
    df.rename(columns={
        'Num_Poste': 'NUM_POSTE',
        'Nom_Station': 'NOM_STATION',
        'Lat': 'LAT',
        'Lon': 'LON',
        'Alti': 'ALTI'
    }, inplace=True)

    # Vérifier les colonnes attendues
    required_columns = {'NUM_POSTE', 'NOM_STATION', 'LAT', 'LON', 'ALTI'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Le fichier CSV doit contenir les colonnes : {required_columns}")
except Exception as e:
    print(f"Erreur lors de la lecture du fichier CSV : {e}")
    exit(1)

# Créer une session SQLAlchemy pour insérer les données
Session = sessionmaker(bind=engine)
session = Session()

# Insérer les données dans la base de données
try:
    for _, row in df.iterrows():
        station = Station(
            NUM_POSTE=row['NUM_POSTE'],
            NOM_STATION=row['NOM_STATION'],
            LAT=row['LAT'],
            LON=row['LON'],
            ALTI=row['ALTI']
        )
        session.add(station)

    # Commit des modifications dans la base de données
    session.commit()
    print("Les données ont été insérées avec succès dans la table 'stations'.")
except Exception as e:
    session.rollback()  # Annuler les transactions en cas d'erreur
    print(f"Une erreur s'est produite lors de l'insertion des données : {e}")
finally:
    session.close()  # Fermer la session
