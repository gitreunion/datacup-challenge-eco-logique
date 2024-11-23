#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# File         : rep_calcul.py
# Created By   : Camille DECHAMPS - Office de l'eau Réunion
# Created Date : Novembre 2024 
# Version      : 1.0
# License      : CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/
# ---------------------------------------------------------------------------
# Description  : Ce script permet de calculer les volumes optimaux de cuves de récupération d'eau de pluie.
#               Les données d'entrées sont la localisation, pour récupérer les données pluviométriques locales, la surface de toiture ainsi que la consommation d'eau de l'usager.
#               Le calcul est une simulation du remplissage et vidage journalier sur 10 ans de différents volumes de cuves
#               Le résultat fait ressortir un graphique du taux de couverture des besoins en fonction des différents volumes de cuve
#               En fonction de ce graphique et de la pente de la courbe, trois volumes recommandés sont déduits
#               D'autres graphiques permettant de visualiser les résultats sont aussi créés, comme l'évolution du stockage au cours de l'année, les économies d'eau et d'argent
# ---------------------------------------------------------------------------


import pandas as pd 
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import requests
import folium

#API BAN, données adresses nationales permettant de rechercher latitude et longitude de l'adresse rentrée
#l'Adresse est un input qui devra être relié au formulaire de la page web
#La lat et long sont reliées par une boucle à un csv reprenant les coordonnées géographiques de tous les pluvios
#et une requête est faite pour chercher celui le plus proche par une division euclidienne


ADDOK_URL = 'http://api-adresse.data.gouv.fr/search/'
params = {
    'q': input("Entrez votre adresse et votre code postal: "),
    'limit': 5
}
response = requests.get(ADDOK_URL, params=params)
j = response.json()
if len(j.get('features')) > 0:
    first_result = j.get('features')[0]
    lon, lat = first_result.get('geometry').get('coordinates')
    first_result_all_infos = { **first_result.get('properties'), **{"lon": lon, "lat": lat}}
    
    commune = first_result.get('properties').get('city','Unknown city')
    
    print(f"Commune:{commune}")
    print(first_result_all_infos)
else:
    print('No result')

#Ajout d'une carte (qui s'ouvre dans une version locale de chrome par ex) 
#Carte d'une partie de la Réunion avec un marqueur sur la localisation de l'adresse fournie, permet de vérifier si addresse rentrée est correcte
carte = folium.Map(location = [lat, lon], zoom_start = 12)
folium.Marker([lat,lon], popup = "Domicile").add_to(carte)
carte.save('carte_loc.html')

#importer csv des coordonnées géographiques de tous les pluvios
#Ce fichier Excel est fourni 
stations = pd.read_excel('FINAL_STATIONS2012_2022.xlsx')

#Données journalières de tous les pluviomètres, données MF Open Source (open.data.meteo.gouv)
#ce fichier xlsx peut également être fourni, issu des données MF Open Sourcé mais déjà formaté
#Intéressant d'également rajouter les données de 2023 et 2024
pluvios = pd.read_excel('data_pluvios_2012-2022.xlsx') 

#Faire une requête pour aller chercher la station la plus proche des coordonnées de l'addresse donnée
def distance_euclidienne(lat1, lon1, lat2, lon2):
    return np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2)

#Lat et Lon proviennent de la réponse fournie par l'API (L19)
latitude_addresse = lat
longitude_addresse = lon

#On rajoute une colonne distance dans le dataframe stations où la distance de l'addresse à chaque station est calculée
stations['DISTANCE']= stations.apply(lambda row: distance_euclidienne(latitude_addresse, longitude_addresse, row['LAT'], row['LON']), axis=1)

station_plus_proche = stations.loc[stations['DISTANCE'].idxmin(),'NOM_STATION']

print(station_plus_proche)
print(f"Station la plus proche :{station_plus_proche}")


#en fonction localisation, aller rechercher la valeur du pluvio correspondante dans le Excel avec toutes les pluvios
if station_plus_proche in pluvios.columns:
    pluvio_locale = pluvios[['DATE', station_plus_proche]]
    
    print(f"Données pluviométriques pour {station_plus_proche}:")
    print(pluvio_locale.head())
    
else: 
    print(f"La station {station_plus_proche} n'existe pas dans les données pluviométriques")

# introduction des variables
# celles qui devraient être introduites par l'utilisateur (input) en m^2

surface_toit = input("Entrez votre surface de toit connectée à la gouttière, en m^2: ")
personnes = input("Entrez le nombre de personnes vivant dans le foyer: ")

try:
    surface_toit = float(surface_toit)
    personnes = int(personnes)
except ValueError:
    print("Veuillez entrer des valeurs numériques correctes pour la surface du toit et le nombre de personnes. Essayez un point (.) à la place de la virgule (,)")
   
#coefficient rendement avec coeff_ruis pouvant être changé en fonction type de toit

coeff_systeme = 0.9 

toiture_options = {
    'En pente à surface lisse': {'coeff_ruiss': 0.9},
    'En pente à surface rugueuse': {'coeff_ruiss': 0.8},
    'Toit plat': {'coeff_ruiss': 0.8},
    'Toiture végétalisée':{'coeff_ruiss':0.4}
}

print("Veuillez choisir votre type de toiture parmi les options suivantes :")
print("1. Toit en pente à surface lisse (ex métal, verre, ardoise, tuiles vernissées, panneaux solaires")
print("2. Toit en pente à surface rugueuse (ex tuiles en béton")
print("3. Toit plat")
print("4. Toiture végétalisée")

toiture_type = input("Entrez le numéro correspondant à votre type de toiture: ")

if toiture_type == '1':
        choix = 'En pente à surface lisse'
elif toiture_type == '2':
        choix = 'En pente surface rugueuse'
elif toiture_type == '3':
        choix = 'Toit plat'
elif toiture_type == '4':
        choix = 'Toiture végétalisée'
else:
        print("Choix invalide. Veuillez choisir une option valide.")
        
coeff_ruis = toiture_options[choix]['coeff_ruiss']

#Calcul potentiel récupérable en fonction pluvio /1000 et de surface de toit
pluvio_locale = pluvio_locale.copy()
pluvio_locale.loc[:,'RECUPERABLE']= (pluvio_locale.iloc[:,1]/1000)*surface_toit*coeff_ruis*coeff_systeme
pluie_recuperable = pluvio_locale['RECUPERABLE']

#Consommations intérieures (en L)
#Constantes 
#Arriver à faire un bouton ou menu déroulant pour demander si chasse simple ou double commande
WC_simple_commande = 10
WC_double_commande = 5
WC_jour = 4

#si lave-linge connecté
linge = 75
linge_jour = 0.57 #vérifier valeur

#Arrosage
# Définition des coefficients et consommation en fonction du type d'arrosage
volume_base = 20 #l/m^2/sem 


#Demander quels usages sont faits à l'utilisateur et en fonction la somme des usages est calculée 
print("Veuillez sélectionner les usages d'eau de pluie que vous souhaitez inclure dans le calcul:")
wc_usage = input("Voulez-vous raccorder les WC à l'eau de pluie? (Oui/Non): ").strip().lower()
arrosage_usage = input("Utilisez-vous l'arrosage ? (Oui/Non): ").strip().lower()

#faire un choix de différents comportements d'arrosage, relié à des coefficients et une fréquence d'arrosage par semaine
arrosage_options = {
    'Econome': {'coeff_volume': 0.5, 'fois_sem': 1},
    'Raisonné': {'coeff_volume': 1, 'fois_sem': 1},
    'Abondant': {'coeff_volume': 1, 'fois_sem': 2}
}

#Si l'utilisateur répond oui à la question de l'usage de l'arrosage, poser les questions suivantes, sinon, ne pas les poser
if arrosage_usage == "oui":
    
# Demander à l'utilisateur quel type d'arrosage il pratique et la superficie arrosée 
    surface_jardin = input("Entrez la superficie de votre jardin que vous arrosez, en m^2: ")

    print("Veuillez choisir votre type d'arrosage parmi les options suivantes :")
    print("1. Econome")
    print("2. Raisonné")
    print("3. Abondant")

    arrosage_type = input("Entrez le numéro correspondant à votre type d'arrosage: ")

    try:
        surface_jardin = float(surface_jardin)
    except ValueError:
        print("Veuillez entrer des valeurs numériques correctes pour la surface du jardin. Essayez un point (.) à la place de la virgule (,)")
   
# Vérifier le choix de l'utilisateur et appliquer les valeurs correspondantes
    if arrosage_type == '1':
        choix = 'Econome'
    elif arrosage_type == '2':
        choix = 'Raisonné'
    elif arrosage_type == '3':
        choix = 'Abondant'
    else:
        print("Choix invalide. Veuillez choisir une option valide.")
    
    coeff_volume = arrosage_options[choix]['coeff_volume']
    fois_sem = arrosage_options[choix]['fois_sem']

    arrosage_jour = (volume_base*coeff_volume*fois_sem)/7
    arrosage_jour = (arrosage_jour/1000)*surface_jardin #conversion en m^3/jour

# Arrosage n'est compté que durant la saison sèche 
### Voir pour paramétrer les périodes de saison sèche / saison des pluies    
    
#Calcul consommation en fonction des usages
#ici on n'ajoute pas le lave-linge car expérimental 
conso_jour = 0 

if wc_usage == 'oui':
    conso_wc = (WC_double_commande * WC_jour * personnes) / 1000
    conso_jour += conso_wc
    print(f"Consommation des WC: {conso_wc:.2f} m3/jour")
else: 
    conso_wc = 0
    
if arrosage_usage == 'oui':
    conso_jour += arrosage_jour
    print(f"Consommation d'arrosage: {arrosage_jour:.2f} m3/jour")  

else: 
    arrosage_jour = 0
    
arrosage_jour_valeur = arrosage_jour if arrosage_usage =='oui' else 0

print(f"\nConsommation journalière totale: {conso_jour:.2f} m3/jour")

#Tableau calculant consommation par jour sur les 11ans (4018 jours et calcul au pas de temps journalier)
dates = pd.date_range(start='2012-01-01', periods=4018, freq='D')
conso = pd.DataFrame({
    'DATE': dates,
    'WC': conso_wc,  # Si WC, consommation appliquée, sinon 0
    #'LAVE_LINGE': (linge/1000)*linge_jour,
    'ARROSAGE':0.0  
})

conso['ARROSAGE'] = conso['ARROSAGE'].astype(float)

#Arrosage seulement durant période sèche (de mai à novembre)
#### Pouvoir paramétrer ces valeurs dans un fichier de conf
if arrosage_usage == 'oui':
    mask_arrosage = (conso['DATE'].dt.month >= 5) & (conso['DATE'].dt.month <= 11)
    conso.loc[mask_arrosage, 'ARROSAGE'] = arrosage_jour_valeur  # Appliquer la consommation d'arrosage sur la période choisie
 
conso['TOTAL_JOUR']=conso[['WC', 'ARROSAGE']].sum(axis=1)

#Tableau avec cuves différentes tailles 
#Au besoin, il est possible d'augmenter l'échantillon et d'inclure de plus grands volumes
start_volume = 0.5
end_volume = 10 #cuve taille max = 10m^3
step = 0.5

volumes_cuves = np.arange(start_volume, end_volume + step, step)

#Simulation du remplissage et vidage de cuve pour les différents volumes de cuves établis, sur 10ans, de manière journalières
#Dataframe pour stocker les résultats
simulation_cuves = pd.DataFrame({'DATE': dates})

#Dictionnaire pour stocker toutes les colonnes générées (à cause d'un PerformanceWarning)
simulation_cols = {}

#Simulation de chaque volume de cuve et chaque date
for volume_cuve in volumes_cuves:
   
    # Listes pour stocker données simulation quotidiennes pour chaque volume de cuve
    Vj_1_list = [] #volume stocke le jour - 1
    Vstocke_list = []
    besoins_list = [] 
    trop_plein_list = []
    eau_reseau_list = [] #eau potable du réseau pour pallier aux besoins 
    pluie_conso_list = [] #volume d'eau de pluie consommée ce jour-là 
    
   
    Vj_1 = 0
    # simulation jour par jour (mon calcul)
    for index in range(len(dates)):
        pluie_jour = pluie_recuperable.iloc[index] #Pluie récupérable pour le jour j
        besoins_jour = conso['TOTAL_JOUR'].iloc[index] #consommation du jour j
        
     
    # Si le volume récupéré plus le volume stocké dépasse la capacité de la cuve
        if pluie_jour + Vj_1 >= volume_cuve:
            Vstocke = volume_cuve  # Le volume stocké atteint la capacité maximale de la cuve
            trop_plein = pluie_jour + Vj_1 - volume_cuve  # Excès d'eau non stocké
        else:
            Vstocke = pluie_jour + Vj_1  # Tout peut être stocké
            trop_plein = 0

        # Calcul de la consommation d'eau : si l'eau stockée + récupérée est suffisante
        if Vstocke >= besoins_jour:
            pluie_conso = besoins_jour
            eau_reseau = 0
            Vstocke -= besoins_jour
        else:
            pluie_conso = Vstocke
            eau_reseau = besoins_jour - pluie_conso
            Vstocke = 0    


# Stocker les valeurs pour ce jour dans les listes 
        Vj_1_list.append(Vj_1)
        Vstocke_list.append(Vstocke)
        besoins_list.append(besoins_jour)
        trop_plein_list.append(trop_plein)
        eau_reseau_list.append(eau_reseau)
        pluie_conso_list.append(pluie_conso)
        
        # Mettre à jour Vs_j-1 pour le prochain jour
        Vj_1 = Vstocke
    
    #ajouter les résultats pour ce volume de cuve dans le dictionnaire 'simulation_cols'
    simulation_cols[f'Vj_1_{volume_cuve}'] = Vj_1_list
    simulation_cols[f'VSTOCKE_{volume_cuve}'] = Vstocke_list
    simulation_cols[f'TROP_PLEIN_{volume_cuve}'] = trop_plein_list
    simulation_cols[f'EAU_RESEAU_{volume_cuve}'] = eau_reseau_list
    simulation_cols[f'PLUIE_CONSO_{volume_cuve}'] = pluie_conso_list

#Convertir le dictionnaire en DF et concaténer les nouvelles colonnes à "simulation_cuves"
simulation_df = pd.DataFrame(simulation_cols)

simulation_cuves = pd.concat([simulation_cuves, simulation_df], axis=1)

#Faire les ratios pour déterminer le volume optimal
#d'abord faire ressortir la consommation moyenne par an et la pluie potentiellement récupérable par an
#extraire l'année dans le dataframe afin de grouper les données par années
conso['YEAR']= conso['DATE'].dt.year

pluvio_locale=pluvio_locale.copy()
pluvio_locale['YEAR']=pluvio_locale['DATE'].dt.year

#calcul de la consommation totale et de la pluie récupérable pour chaque année 
conso_totale_an = conso.groupby('YEAR')['TOTAL_JOUR'].sum()
pluie_recuperable_an = pluvio_locale.groupby('YEAR')['RECUPERABLE'].sum()
pluie_recuperable_total = pluvio_locale['RECUPERABLE'].sum()

print("Consommation totale par an :")
print(conso_totale_an)

print("Potentiel récupérable moyen par an :")
print(pluie_recuperable_an)

#Moyenne de conso totale et pluie récupérable sur les 10ans
conso_totale_moy= conso_totale_an.mean()
pluie_recuperable_moy= pluie_recuperable_an.mean()

print(conso_totale_moy)
print(pluie_recuperable_moy)


#Ratios pour chaque volume de cuve 
#Création d'un dataframe comprenant des listes pour chaque ratio calculé
list_ratios = []

for volume_cuve in volumes_cuves:
    
    #Total 10 ans
    pluie_conso_totale = simulation_cuves[f'PLUIE_CONSO_{volume_cuve}'].sum()
    eau_reseau_totale = simulation_cuves[f'EAU_RESEAU_{volume_cuve}'].sum()
    conso_totale = conso['TOTAL_JOUR'].sum()
  
    #Moyennes 
    pluie_conso_moy = simulation_cuves[f'PLUIE_CONSO_{volume_cuve}'].mean() 
    eau_reseau_moy = simulation_cuves[f'EAU_RESEAU_{volume_cuve}'].mean()
    
    #calculs ratios et %
    recup_conso = (pluie_recuperable_total/pluie_conso_totale)
    couverture_besoins = (pluie_conso_totale/ conso_totale)*100
    besoins_couverts_pluie = (pluie_recuperable_moy/conso_totale_moy)*100 
    
    
# ajout des valeurs sous forme de dictionnaire à la liste
# Les valeurs moyennes par années sont divisées par 11 car pour le moment la simulation se fait sur 11 ans de données pluvio
# Peut être rendu dynamique 
    list_ratios.append({
        'CUVES':volume_cuve,
        'RECUP/CONSO':recup_conso,
        'COUVERTURE_BESOINS':couverture_besoins,
        'V_ECONOMISE':pluie_conso_totale/11,
        'V_EAU_RESEAU':eau_reseau_totale/11,
        '%BESOINS_PLUIE_UTILISE':((pluie_conso_totale/11)/conso_totale_moy)*100, 
        })

df_ratios = pd.DataFrame(list_ratios)

print(df_ratios)

#  Graphiques de sortie

#Graphique volume d'eau économisé
volumes_economises = df_ratios['V_ECONOMISE'].values
 
fig,ax4 = plt.subplots()
ax4.plot(volumes_cuves,volumes_economises)

color = 'tab:blue'
ax4.set_xlabel('Volumes de cuve (m^3)')
ax4.set_ylabel('Volumes d eau économisés (m^3/an)')
#ax3.plot(X, Y, color=color)
#ax3.tick_params(axis='y', labelcolor=color)
ax4.set_title('Potentiel d économies en eau en fonction des différents volumes de cuves')
plt.style.use('ggplot')
plt.show()

# Ajouter avec et sans WC! (faciliter la comparaison)

# Graphique couverture des besoins et dérivée
# calcul d'optimisation, de la dérivée avec différences finies 
#Ce graphique n'est PAS à montrer sur l'interface, sert plutôt à visualiser la pente

X = volumes_cuves
Y = df_ratios['COUVERTURE_BESOINS']
 
dY = np.diff(Y)/np.diff(X)

X_mid = (np.array(X[:-1]) + np.array(X[1:])) / 2

# Tracer la courbe originale
fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('Volumes de cuve')
ax1.set_ylabel('Taux de couverture des besoins (%)', color=color)
ax1.plot(X, Y, color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_title('Taux de couverture des besoins et sa dérivée')

# Tracer la dérivée
ax2 = ax1.twinx()  # Crée un second axe qui partage le même axe x
color = 'tab:red'
ax2.set_ylabel('Dérivée', color=color)  # Le label de l'axe y pour la dérivée
ax2.plot(X_mid, dY, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
plt.show()


# Calcul des volumes recommandés

# Méthode : examine le point où la pente commence à ralentir, utilise un % de réduction de pente au lieu d'un seuil fixe (entre 30 et 50%)
# Calcule la pente pour chaque intervalle de volume
dY = np.diff(Y) / np.diff(X)

l =[]
for i in range(len(dY)-1): 
    variation_pente = abs(dY[i+1]-dY[i])
    l.append(variation_pente)
    
print(l)

seuil1 = 2 #Pour le volume économique
seuil3 = 0.2 #pour le volume écologique

list_seuil = []

# Pour le volume ECONOMIQUE

for i in range(len(l)-1):
    if l[i]<seuil1:
        print("Volume économique:",X[i])
        list_seuil.append(X[i])
        break 

# Pour le volume OPTIMAL

# Calculer la pente initiale pour référence (15% premiers volumes de cuves)
pente_initiale = np.mean(dY[:int(len(dY) * 0.15)])

# Définir un seuil de réduction progressive (40% de la pente initiale)
seuil_pente_transition = 0.4 * pente_initiale

# Trouver le premier point où la pente descend sous le seuil de réduction (idx = index)
idx_transition = np.where(dY <= seuil_pente_transition)[0]

if len(idx_transition) > 0:
    # Utiliser le premier indice où la pente passe sous le seuil de transition
    volume_optimal_idx = idx_transition[0]
else:
    # Si aucun point ne respecte le seuil, on prend une valeur de fallback basée sur le minimum de pente
    volume_optimal_idx = np.argmin(np.abs(dY))

# Calculer le volume correspondant
volume_optimal_calculé = X[volume_optimal_idx + 1]  # Correction pour l'indice de la différence

# Trouver le volume dans volumes_cuves le plus proche du volume optimal calculé
volume_optimal = min(volumes_cuves, key=lambda x: abs(x - volume_optimal_calculé))

list_seuil.append(volume_optimal)
print(f"Le volume optimal estimé est : {volume_optimal} m³")

# Pour le volume ECOLOGIQUE

for i in range(len(l)-1):
    if l[i]<seuil3:
        print("Volume écologique:",X[i])
        list_seuil.append(X[i])
        break
    
if list_seuil[2] == list_seuil[1]:
    print("Le volume optimal et le volume écologique sont équivalents.")

# Graphique taux de couverture avec la visualisation des volumes recommandés
# Graphique important à montrer dans les résultats
#Cette visualisation est importante car permet une meilleure représentation graphique
#Il est possible de modifier les graphes pour les rendre plus attrayants
fig,ax = plt.subplots()
ax.plot(X,Y)

ax.set_ylim(0,)

ax.set_title('Taux de couverture des besoins en fonction des différents volumes de cuves')

ax.set_xticks([0.5,1,2,3,4,5,6,7,8,9,10])
ax.set_yticks([0,10,20,30,40,50,60,70,80,90,100])
ax.set_xlabel('Volumes de cuve')
ax.set_ylabel('Taux de couverture des besoins (%)')
plt.style.use('ggplot')

ax.axvline(x=list_seuil[0], color='orange', linestyle='--', label=f'Volume économique {list_seuil[0]} m³')
ax.axvline(x=list_seuil[1], color='blue', linestyle='--', label=f'Volume optimal {list_seuil[1]} m³')
ax.axvline(x=list_seuil[2], color='green', linestyle='--', label=f'Volume écologique {list_seuil[2]} m³')

ax.legend()
plt.show()

# Graphique évolution du stockage dans la cuve optimale
# l'année choisie est la dernière année des données pluvio (ici 2022)
recent_year = simulation_cuves.tail(365)

volume_stocke_cuve_optimale = recent_year[f'VSTOCKE_{volume_optimal}']

plt.figure(figsize=(10, 6))
plt.plot(recent_year['DATE'], volume_stocke_cuve_optimale, label=f'Volume Stocké pour Cuve {volume_optimal} m³', color='blue')

# Titre et étiquettes
plt.title("Évolution du Volume Stocké au cours d'une année récenté pour une cuve de volume optimal")
plt.xlabel("Mois de l'année récente")
plt.ylabel('Volume Stocké (m³)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()


# Ajouter les coûts et économies 
# Ficher xlsx est fourni par l'Office de l'Eau
couts_eau = pd.read_excel('Couts_eau_outil.xlsx')

#Poser question assainissment collectif ou non
def question_assainissment(question):
    response = ""
    while response not in ["oui","non"]:
        response=input(question + "(oui/non): ").lower()
    return response

# La commune identifiée lors de la géolocalisation de l'adresse est reprise ici
### Utiliser le code INSEE pour éviter les problèmes d'ortographe ?

def rechercher_commune (couts_eau, commune): 
    ligne_commune = couts_eau[couts_eau['Commune']== commune]
    
    if ligne_commune.empty:
        print(f"Commune '{commune}' non trouvée. Essayez de l'écrire sans espace, avec tirets, accent et apostrophe.")
        return None
    else:
        cout_eau_et_ass = ligne_commune['eau_et_ass'].values[0]
        cout_eau_potable = ligne_commune['eau_potable'].values[0]
        return cout_eau_et_ass, cout_eau_potable

cout_eau_et_ass, cout_eau_potable = rechercher_commune(couts_eau, commune)

if cout_eau_et_ass is not None and cout_eau_potable is not None:
    response = question_assainissment("Etes-vous connecté à un système d'assainissment collectif?")
    
    if response in ["oui","o"]:
        cout = cout_eau_et_ass
        print(f"Pour la commune {commune}:")
        print(f" - Coût de l'eau avec assainissement : {cout_eau_et_ass} €/m³")
        
    else: 
        cout = cout_eau_potable
        print(f"Pour la commune {commune}:")
        print(f" - Coût de l'eau potable : {cout_eau_potable} €/m³")

else: 
    print("Données indisponibles pour la commune demandée.")


# Graphique des économies potentielles en fonction taille de la cuve
#on calcule, en fonction du volume économisé pour les différentes cuves, ce que ça vaut en €

volumes_economises = df_ratios['V_ECONOMISE'].values
couts_economises= volumes_economises*cout

economies = pd.DataFrame({
    'CUVES':  volumes_cuves,
    'V_ECONOMISE':volumes_economises,
    'COUTS_ECONOMISE': couts_economises
})

#Graphique courbe des économies €
fig,ax3 = plt.subplots()
ax3.plot(volumes_cuves,couts_economises)

color = 'tab:red'
ax3.set_xlabel('Volumes de cuve')
ax3.set_ylabel('Economies réalisables (€/an)')
ax3.set_title('Potentiel d économies en fonction des différents volumes de cuves')
plt.style.use('ggplot')

ax3.axvline(x=list_seuil[0], color='orange', linestyle='--', label=f'Volume économique {list_seuil[0]} m³')
ax3.axvline(x=list_seuil[1], color='blue', linestyle='--', label=f'Volume optimal {list_seuil[1]} m³')
ax3.axvline(x=list_seuil[2], color='green', linestyle='--', label=f'Volume écologique {list_seuil[2]} m³')

plt.show()














