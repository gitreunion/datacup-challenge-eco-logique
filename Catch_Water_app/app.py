from flask import Flask, render_template, request, redirect, url_for
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import requests
import folium
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend 'Agg' pour générer des images sans interface graphique
import psycopg2
from psycopg2 import sql
import re

app = Flask(__name__)

# Charger les données au démarrage de l'application pour éviter de les recharger à chaque requête
stations = pd.read_excel('FINAL_STATIONS2012_2022.xlsx')


pluvios = pd.read_excel('data_pluvios_2012-2022.xlsx')


# Configuration de la base de données
db_config = {
    'host': 'localhost',        # Remplacez par l'hôte de votre base de données
    'dbname': 'project',        # Remplacez par le nom de votre base
    'user': 'postgres',            # Remplacez par votre nom d'utilisateur
    'password': '123',          # Remplacez par votre mot de passe
    'port': 5432                # Port par défaut de PostgreSQL
}

# Nom de la table dans la base de données
table_name = 'jointure_batiments_adresses'

# Fonction pour se connecter à la base de données et récupérer la valeur souhaitée
def get_value_from_db(lat_x, long_x, column_name):
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


def distance_euclidienne(lat1, lon1, lat2, lon2):
    return np.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)

def obtenir_commune_depuis_adresse(adresse):
    ADDOK_URL = 'http://api-adresse.data.gouv.fr/search/'
    params = {
        'q': adresse,
        'limit': 5
    }
    response = requests.get(ADDOK_URL, params=params)
    j = response.json()
    if len(j.get('features')) > 0:
        first_result = j.get('features')[0]
        lon, lat = first_result.get('geometry').get('coordinates')
        commune = first_result.get('properties').get('city', 'Commune inconnue')
        return commune, lat, lon
    else:
        return None, None, None

def generer_graphique_couverture_besoins(X, Y, list_seuil):
    fig, ax = plt.subplots()
    ax.plot(X, Y)
    ax.set_ylim(0,)
    ax.set_title('Taux de couverture des besoins en fonction des différents volumes de cuves')
    ax.set_xticks(np.arange(0.5, 10.5, 0.5))
    ax.set_yticks(np.arange(0, 110, 10))
    ax.set_xlabel('Volumes de cuve (m³)')
    ax.set_ylabel('Taux de couverture des besoins (%)')
    plt.style.use('ggplot')

    ax.axvline(x=list_seuil[0], color='orange', linestyle='--', label=f'Volume économique {list_seuil[0]} m³')
    ax.axvline(x=list_seuil[1], color='blue', linestyle='--', label=f'Volume optimal {list_seuil[1]} m³')
    ax.axvline(x=list_seuil[2], color='green', linestyle='--', label=f'Volume écologique {list_seuil[2]} m³')

    ax.legend()

    # Convertir le graphique en image base64
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graphique_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return graphique_base64

def generer_graphique_economies(volumes_cuves, couts_economises, list_seuil):
    fig, ax = plt.subplots()
    ax.plot(volumes_cuves, couts_economises)
    ax.set_xlabel('Volumes de cuve (m³)')
    ax.set_ylabel('Économies réalisables (€/an)')
    ax.set_title('Potentiel d\'économies en fonction des différents volumes de cuves')
    plt.style.use('ggplot')

    ax.axvline(x=list_seuil[0], color='orange', linestyle='--', label=f'Volume économique {list_seuil[0]} m³')
    ax.axvline(x=list_seuil[1], color='blue', linestyle='--', label=f'Volume optimal {list_seuil[1]} m³')
    ax.axvline(x=list_seuil[2], color='green', linestyle='--', label=f'Volume écologique {list_seuil[2]} m³')

    ax.legend()

    # Convertir le graphique en image base64
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graphique_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return graphique_base64

def generer_graphique_volume_stocke(recent_year, volume_stocke_cuve_optimale, volume_optimal):
    plt.figure(figsize=(10, 6))
    plt.plot(recent_year['DATE'], volume_stocke_cuve_optimale, label=f'Volume Stocké pour Cuve {volume_optimal} m³', color='blue')

    # Titre et étiquettes
    plt.title("Évolution du Volume Stocké au cours de l'année récente pour une cuve de volume optimal")
    plt.xlabel("Date")
    plt.ylabel('Volume Stocké (m³)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Convertir le graphique en image base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graphique_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graphique_base64

def generer_carte(lat, lon):
    carte = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], popup="Domicile").add_to(carte)
    return carte._repr_html_()

def rechercher_commune(couts_eau, commune):
    ligne_commune = couts_eau[couts_eau['Commune'] == commune]
    if ligne_commune.empty:
        return None, None
    else:
        cout_eau_et_ass = ligne_commune['eau_et_ass'].values[0]
        cout_eau_potable = ligne_commune['eau_potable'].values[0]
        return cout_eau_et_ass, cout_eau_potable

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        adresse = request.form.get('adresse', '').strip()
        #surface_toit = request.form['surface_toit']
        personnes = request.form['personnes']
        toiture_type = request.form.get('toiture_type')
        
        arrosage_usage = request.form.get('arrosage_usage', 'non')
        surface_jardin = request.form.get('surface_jardin', '0')
        arrosage_type = request.form.get('arrosage_type')
        assainissement = request.form.get('assainissement', 'non')

        wc_usage = request.form.get('wc_usage', None)

        # Définir la valeur selon la case cochée ou non
        if wc_usage == 'on':
            wc_usage = 'oui'
        else:
            wc_usage = 'non'

        print(toiture_type)

        # Stocker les données dans la session ou les passer à la fonction de calcul
        return redirect(url_for('results', 
                                adresse=adresse, 
                                #surface_toit=surface_toit, 
                                personnes=personnes, 
                                toiture_type=toiture_type, 
                                wc_usage=wc_usage, 
                                arrosage_usage=arrosage_usage,
                                surface_jardin=surface_jardin,
                                arrosage_type=arrosage_type,
                                assainissement=assainissement))
    return render_template('index.html')



def obtenir_couts_eau(commune):
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Requête pour obtenir les valeurs de 'eau_et_ass' et 'eau_potable' pour la commune spécifiée
        query = """
            SELECT eau_et_ass, eau_potable 
            FROM Couts_eau_outil 
            WHERE Commune = %s;
        """
        cursor.execute(query, (commune,))
        result = cursor.fetchone()

        # Vérifier que des résultats ont été trouvés
        if result:
            cout_eau_et_ass, cout_eau_potable = result
            return float(cout_eau_et_ass), float(cout_eau_potable)
        else:
            return None, None
    except Exception as e:
        print(f"Erreur lors de la recherche de la commune : {e}")
        return None, None
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def obtenir_station_plus_proche(lat_addresse, lon_addresse):
    # Calculer la distance pour chaque station
    stations['DISTANCE'] = stations.apply(
        lambda row: distance_euclidienne(lat_addresse, lon_addresse, row['LAT'], row['LON']),
        axis=1
    )
    # Trouver l'index de la station avec la distance minimale
    idx_min = stations['DISTANCE'].idxmin()
    # Récupérer le nom de la station et la distance
    station_plus_proche = stations.loc[idx_min, 'NOM_STATION']
    distance_min = stations.loc[idx_min, 'DISTANCE']
    return station_plus_proche, distance_min


@app.route('/results')
def results():
    # Récupérer les paramètres de la requête
    adresse = request.args.get('adresse')
   # surface_toit = float(request.args.get('surface_toit'))
    personnes = int(request.args.get('personnes'))
    toiture_type = request.args.get('toiture_type')
    wc_usage = request.args.get('wc_usage', 'non').lower()
    arrosage_usage = request.args.get('arrosage_usage', 'non').lower()
    # Pour une requête POST
    surface_jardin = float(request.form.get('surface_jardin', '0'))

    arrosage_type = request.args.get('arrosage_type')
    assainissement = request.args.get('assainissement', 'non').lower()

    # Obtenir la commune, latitude et longitude
    commune, lat, lon = obtenir_commune_depuis_adresse(adresse)
    if not commune:
        return "Adresse invalide ou commune non trouvée."


    

    # Calculs principaux

    # Calcul de la station la plus proche
    stations['DISTANCE'] = stations.apply(lambda row: distance_euclidienne(lat, lon, row['LAT'], row['LON']), axis=1)
    station_plus_proche = stations.loc[stations['DISTANCE'].idxmin(), 'NOM_STATION']

    #station_plus_proche = obtenir_station_plus_proche(lat,lon)

    address = "10 Rue Paul Hermann"
    # Appel de la méthode pour récupérer et afficher la valeur d'une colonne spécifiée par adresse
    value_by_address = get_value_by_address(adresse, 'surface_m2')

    surface_toit = float(value_by_address)

    # Extraire les données pluviométriques pour la station la plus proche
    if station_plus_proche in pluvios.columns:
        pluvio_locale = pluvios[['DATE', station_plus_proche]]
    else:
        return f"La station {station_plus_proche} n'existe pas dans les données pluviométriques"

    # Coefficient de ruissellement en fonction du type de toiture
    toiture_options = {
        '1': {'type': 'En pente à surface lisse', 'coeff_ruiss': 0.9},
        '2': {'type': 'En pente à surface rugueuse', 'coeff_ruiss': 0.8},
        '3': {'type': 'Toit plat', 'coeff_ruiss': 0.8},
        '4': {'type': 'Toiture végétalisée', 'coeff_ruiss': 0.4}
    }
    choix_toiture = toiture_options.get(toiture_type)
    if choix_toiture:
        coeff_ruis = choix_toiture['coeff_ruiss']
    else:
        return "Type de toiture invalide. Veuillez choisir une option valide."

    coeff_systeme = 0.9  # Coefficient système

    # Calcul potentiel récupérable
    pluvio_locale = pluvio_locale.copy()
    pluvio_locale['RECUPERABLE'] = (pluvio_locale.iloc[:, 1] / 1000) * surface_toit * coeff_ruis * coeff_systeme
    pluie_recuperable = pluvio_locale['RECUPERABLE']

    # Consommations intérieures (en L)
    WC_double_commande = 5
    WC_jour = 4

    # Calcul de la consommation journalière
    conso_wc = 0
    arrosage_jour = 0
    conso_jour = 0

    if wc_usage == 'oui':
        conso_wc = (WC_double_commande * WC_jour * personnes) / 1000  # en m³/jour
        conso_jour += conso_wc

    if arrosage_usage == 'oui':
        # Arrosage options
        arrosage_options = {
            '1': {'type': 'Econome', 'coeff_volume': 0.5, 'fois_sem': 1},
            '2': {'type': 'Raisonné', 'coeff_volume': 1, 'fois_sem': 1},
            '3': {'type': 'Abondant', 'coeff_volume': 1, 'fois_sem': 2}
        }
        choix_arrosage = arrosage_options.get(arrosage_type)
        if choix_arrosage:
            coeff_volume = choix_arrosage['coeff_volume']
            fois_sem = choix_arrosage['fois_sem']
            volume_base = 20  # l/m²/sem
            arrosage_jour = (volume_base * coeff_volume * fois_sem) / 7
            arrosage_jour = (arrosage_jour / 1000) * surface_jardin  # conversion en m³/jour
            conso_jour += arrosage_jour
        else:
            return "Type d'arrosage invalide. Veuillez choisir une option valide."

    # Créer le DataFrame des consommations sur les 4018 jours
    dates = pd.date_range(start='2012-01-01', periods=4018, freq='D')
    conso = pd.DataFrame({
        'DATE': dates,
        'WC': conso_wc,
        'ARROSAGE': 0.0
    })
    if arrosage_usage == 'oui':
        mask_arrosage = (conso['DATE'].dt.month >= 5) & (conso['DATE'].dt.month <= 11)
        conso.loc[mask_arrosage, 'ARROSAGE'] = arrosage_jour

    conso['TOTAL_JOUR'] = conso[['WC', 'ARROSAGE']].sum(axis=1)

    # Simulation pour différents volumes de cuve
    start_volume = 0.5
    end_volume = 10  # m³
    step = 0.5
    volumes_cuves = np.arange(start_volume, end_volume + step, step)

    # Simulations des cuves
    simulation_cuves = pd.DataFrame({'DATE': dates})
    simulation_cols = {}

    for volume_cuve in volumes_cuves:
        Vj_1_list = []
        Vstocke_list = []
        trop_plein_list = []
        eau_reseau_list = []
        pluie_conso_list = []

        Vj_1 = 0
        for index in range(len(dates)):
            pluie_jour = pluie_recuperable.iloc[index]
            besoins_jour = conso['TOTAL_JOUR'].iloc[index]

            if pluie_jour + Vj_1 >= volume_cuve:
                Vstocke = volume_cuve
                trop_plein = pluie_jour + Vj_1 - volume_cuve
            else:
                Vstocke = pluie_jour + Vj_1
                trop_plein = 0

            if Vstocke >= besoins_jour:
                pluie_conso = besoins_jour
                eau_reseau = 0
                Vstocke -= besoins_jour
            else:
                pluie_conso = Vstocke
                eau_reseau = besoins_jour - pluie_conso
                Vstocke = 0

            Vj_1_list.append(Vj_1)
            Vstocke_list.append(Vstocke)
            trop_plein_list.append(trop_plein)
            eau_reseau_list.append(eau_reseau)
            pluie_conso_list.append(pluie_conso)

            Vj_1 = Vstocke

        simulation_cols[f'VSTOCKE_{volume_cuve}'] = Vstocke_list
        simulation_cols[f'EAU_RESEAU_{volume_cuve}'] = eau_reseau_list
        simulation_cols[f'PLUIE_CONSO_{volume_cuve}'] = pluie_conso_list

    simulation_df = pd.DataFrame(simulation_cols)
    simulation_cuves = pd.concat([simulation_cuves, simulation_df], axis=1)

    # Calcul des ratios
    conso['YEAR'] = conso['DATE'].dt.year
    pluvio_locale['YEAR'] = pluvio_locale['DATE'].dt.year

    conso_totale_an = conso.groupby('YEAR')['TOTAL_JOUR'].sum()
    pluie_recuperable_an = pluvio_locale.groupby('YEAR')['RECUPERABLE'].sum()
    pluie_recuperable_total = pluvio_locale['RECUPERABLE'].sum()

    conso_totale_moy = conso_totale_an.mean()
    pluie_recuperable_moy = pluie_recuperable_an.mean()

    list_ratios = []

    for volume_cuve in volumes_cuves:
        pluie_conso_totale = simulation_cuves[f'PLUIE_CONSO_{volume_cuve}'].sum()
        eau_reseau_totale = simulation_cuves[f'EAU_RESEAU_{volume_cuve}'].sum()
        conso_totale = conso['TOTAL_JOUR'].sum()

        recup_conso = (pluie_recuperable_total / pluie_conso_totale)
        couverture_besoins = (pluie_conso_totale / conso_totale) * 100

        list_ratios.append({
            'CUVES': volume_cuve,
            'RECUP/CONSO': recup_conso,
            'COUVERTURE_BESOINS': couverture_besoins,
            'V_ECONOMISE': pluie_conso_totale / 11,
            'V_EAU_RESEAU': eau_reseau_totale / 11,
            '%BESOINS_PLUIE_UTILISE': ((pluie_conso_totale / 11) / conso_totale_moy) * 100,
        })

    df_ratios = pd.DataFrame(list_ratios)

    # Calcul des volumes recommandés
    X = volumes_cuves
    Y = df_ratios['COUVERTURE_BESOINS']

    dY = np.diff(Y) / np.diff(X)
    l = [abs(dY[i+1] - dY[i]) for i in range(len(dY)-1)]

    seuil1 = 2
    seuil3 = 0.2
    list_seuil = []

    # Volume économique
    for i in range(len(l)-1):
        if l[i] < seuil1:
            list_seuil.append(X[i])
            break

    # Volume optimal
    pente_initiale = np.mean(dY[:int(len(dY) * 0.15)])
    seuil_pente_transition = 0.4 * pente_initiale
    idx_transition = np.where(dY <= seuil_pente_transition)[0]

    if len(idx_transition) > 0:
        volume_optimal_idx = idx_transition[0]
    else:
        volume_optimal_idx = np.argmin(np.abs(dY))

    volume_optimal_calculé = X[volume_optimal_idx + 1]
    volume_optimal = min(volumes_cuves, key=lambda x: abs(x - volume_optimal_calculé))
    list_seuil.append(volume_optimal)

    # Volume écologique
    for i in range(len(l)-1):
        if l[i] < seuil3:
            list_seuil.append(X[i])
            break

    # Calcul des coûts et économies
    cout_eau_et_ass, cout_eau_potable = obtenir_couts_eau(commune) 

    libelle_acheminement = "test"
    if cout_eau_et_ass is not None and cout_eau_potable is not None:
        if assainissement == 'oui':
            cout = cout_eau_et_ass
        else:
            cout = cout_eau_potable
    else:
        cout = 0  # Valeur par défaut si données manquantes

    volumes_economises = df_ratios['V_ECONOMISE'].values
    couts_economises = volumes_economises * cout

    # Graphiques
    graph_couverture_besoins = generer_graphique_couverture_besoins(X, Y, list_seuil)
    graph_economies = generer_graphique_economies(volumes_cuves, couts_economises, list_seuil)

    # Graphique évolution du stockage
    recent_year = simulation_cuves.tail(365)
    volume_stocke_cuve_optimale = recent_year[f'VSTOCKE_{volume_optimal}']
    graph_volume_stocke = generer_graphique_volume_stocke(recent_year, volume_stocke_cuve_optimale, volume_optimal)

    # Carte Folium
    carte_folium = generer_carte(lat, lon)

    # Passer les résultats au template
    return render_template('results.html',
                           commune=commune,
                           libelle_acheminement=libelle_acheminement,
                           graph_couverture_besoins=graph_couverture_besoins,
                           graph_economies=graph_economies,
                           graph_volume_stocke=graph_volume_stocke,
                           carte_folium=carte_folium,
                           tableau_resultats=df_ratios.to_html(classes='table table-striped', index=False),
                           data1 = list_seuil[0],
                           data2 = list_seuil[1],
                           data3 = list_seuil[2]
                           )

if __name__ == '__main__':
    app.run(debug=True)