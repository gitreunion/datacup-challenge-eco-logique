import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
import dash_table
from dash.dependencies import Input, Output

# Fonction pour créer le réseau
def create_network(num_months, rainfall_data, demand_data, storage_capacity):
    G = nx.DiGraph()
    G.add_node('s')  # Source
    G.add_node('t')  # Puits
    for i in range(num_months):
        G.add_node(f'collect_{i}')
        G.add_node(f'storage_{i}')
        G.add_node(f'demand_{i}')
        G.add_edge('s', f'collect_{i}', capacity=rainfall_data[i])
        G.add_edge(f'collect_{i}', f'storage_{i}', capacity=storage_capacity)
        if i < num_months - 1:
            G.add_edge(f'storage_{i}', f'storage_{i+1}', capacity=storage_capacity)
        G.add_edge(f'storage_{i}', f'demand_{i}', capacity=demand_data[i])
        G.add_edge(f'demand_{i}', 't', capacity=demand_data[i])
    return G

# Fonction pour calculer le flux maximal
def max_flow(G, source, sink):
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    return flow_value, flow_dict
# Fonction pour visualiser les indicateurs par mois
def visualize_indicators_by_year(num_months, rainfall_data, demand_data, flux_dict, flux_maximal, year_label):
    months = [f"Mois {i+1}" for i in range(num_months)]
    collect_data = [flux_dict['s'].get(f'collect_{i}', 0) for i in range(num_months)]
    demand_met = [flux_dict.get(f'storage_{i}', {}).get(f'demand_{i}', 0) for i in range(num_months)]
    storage_used = [flux_dict.get(f'collect_{i}', {}).get(f'storage_{i}', 0) for i in range(num_months)]

    fig = go.Figure()

    fig.add_trace(go.Bar(x=months, y=collect_data, name='Collecte (m3)', marker_color='blue'))
    fig.add_trace(go.Bar(x=months, y=demand_data, name='Demande (m3)', marker_color='orange'))
    fig.add_trace(go.Scatter(x=months, y=storage_used, mode='lines+markers',
                             name='Stockage utilisé (m3)', line=dict(color='green', width=2)))

    fig.update_layout(
        title=f"Indicateurs du Réseau d'Eau - {year_label}",
        xaxis_title="Mois",
        yaxis_title="Volume (m3)",
        barmode='group',
        template="plotly_dark",
        margin=dict(t=80),  # Augmenter l'espace en haut pour le titre et les annotations
    )
    
    fig.add_annotation(
        text=f"Visualisation des données du réseau d'eau pour {year_label}.",
        xref="paper", yref="paper", x=0.5, y=1.2, showarrow=False,
        font=dict(size=14, color="white"),
        align="center",
        bgcolor="rgba(0,0,0,0.6)",
        borderpad=10,
        bordercolor="white",
        borderwidth=2
    )
    return fig

# Fonction pour générer un tableau interactif
def generate_interactive_table(consumption_data, rainfall_data, year_labels):
    # Créer le DataFrame
    df = pd.DataFrame({
        'Année': year_labels,
        'Consommation totale (m3)': consumption_data,
        'Potentiel récupérable moyen (m3)': rainfall_data,
    })
    
    return df

# Paramètres pour l'exemple
num_months = 12

# Année 1 - Données fictives
rainfall_data_1 = [100, 120, 110, 90, 80, 60, 50, 40, 90, 110, 120, 100]
demand_data_1 = [80, 90, 95, 85, 70, 60, 50, 40, 70, 90, 100, 85]
storage_capacity = 200

# Année 2 - Données fictives
rainfall_data_2 = [120, 130, 125, 110, 100, 90, 80, 70, 110, 130, 140, 120]
demand_data_2 = [85, 95, 100, 90, 75, 65, 55, 45, 75, 95, 105, 90]

# Année 3 - Données fictives
rainfall_data_3 = [90, 100, 95, 80, 70, 50, 40, 30, 80, 100, 110, 90]
demand_data_3 = [75, 85, 90, 80, 65, 55, 45, 35, 65, 85, 95, 80]

# Calcul du flux pour chaque année
years_data = [(rainfall_data_1, demand_data_1), (rainfall_data_2, demand_data_2), (rainfall_data_3, demand_data_3)]
year_labels = ["Année 1", "Année 2", "Année 3"]
flux_values = []
flux_dicts = []

# Calcul des flux et des indicateurs pour chaque année
consumption_data = []
rainfall_data_years = []
for i, (rainfall_data, demand_data) in enumerate(years_data):
    G = create_network(num_months, rainfall_data, demand_data, storage_capacity)
    flux_maximal, flux_dict = max_flow(G, 's', 't')
    flux_values.append(flux_maximal)
    flux_dicts.append(flux_dict)  # Ajouter flux_dict à flux_dicts

    # Calcul de la consommation totale annuelle
    total_consumption = sum(demand_data)
    consumption_data.append(total_consumption)

    # Calcul du potentiel récupérable moyen par an
    avg_rainfall = sum(rainfall_data) / len(rainfall_data)
    rainfall_data_years.append(avg_rainfall)

# Générer le tableau interactif
df = generate_interactive_table(consumption_data, rainfall_data_years, year_labels)

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Layout de l'application Dash
app.layout = html.Div([
    html.H1("Tableau des Consommations et Potentiels par Année"),
    html.Div([
        html.Div([
            dash_table.DataTable(
                id='consumption-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'height': '400px', 'overflowY': 'auto'},  # Ajouter un défilement si nécessaire
                style_cell={'textAlign': 'center', 'padding': '5px'},
                row_selectable='single',  # Permet de sélectionner une ligne
                selected_rows=[]  # Aucune ligne sélectionnée par défaut
            ),
        ], className="six columns"),
    ]),
    dcc.Graph(id='monthly-graph'),
])

# Callback pour mettre à jour le graphique en fonction de l'année sélectionnée
@app.callback(
    Output('monthly-graph', 'figure'),
    [Input('consumption-table', 'selected_rows')]
)
def update_graph(selected_rows):
    if not selected_rows:  # Si aucune ligne n'est sélectionnée
        return go.Figure()  # Afficher un graphique vide
    selected_year = selected_rows[0]
    year_label = df.iloc[selected_year]['Année']

    # Récupérer les données de l'année sélectionnée
    year_index = year_labels.index(year_label)
    rainfall_data = years_data[year_index][0]
    demand_data = years_data[year_index][1]
    flux_dict = flux_dicts[year_index]  # Accès correct à flux_dicts
    flux_maximal = flux_values[year_index]

    # Générer le graphique pour l'année sélectionnée
    return visualize_indicators_by_year(num_months, rainfall_data, demand_data, flux_dict, flux_maximal, year_label)

# Démarrer le serveur Dash
if __name__ == '__main__':
    app.run_server(debug=True)
    
# Dans Navigateur pour afficher le dash: http://127.0.0.1:8050/
