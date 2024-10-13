import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Charger et nettoyer les données
@st.cache_data
def load_data():
    data_path = "dvf.csv"
    DVF = pd.read_csv(data_path, encoding="UTF-8")
    return DVF

# Charger et nettoyer les données
df = load_data()

# Interface utilisateur avec Streamlit
st.title("Évolution du Prix au m² en France")

# Sélectionner la commune
communes = df['nom_commune'].unique()
commune_selectionnee = st.selectbox("Sélectionnez une commune :", communes)

# Filtrer les données pour la commune sélectionnée
data_commune = df[df['nom_commune'] == commune_selectionnee]

# Vérifier s'il y a des données
if not data_commune.empty:
    st.subheader(f"Évolution du prix immobilier à {commune_selectionnee}")

    # Création des onglets pour basculer entre Appartement et Maison
    tab1, tab2 = st.tabs(["Appartements", "Maisons"])
    annee = 2024

    # Calcul des variations comparatives avec la dernière année
    def calcul_variations_comparatives(prix_m2_annuel):
        variations = {}
        prix_m2_annuel = prix_m2_annuel.sort_values(by='annee')  # Tri par année

        # Obtenir l'année maximale
        max_annee = prix_m2_annuel['annee'].max()
        prix_max_annee = prix_m2_annuel[prix_m2_annuel['annee'] == max_annee]['prixm2'].values[0]
        # Calculer les variations par rapport à l'année max
        for i in range(len(prix_m2_annuel) - 1):
            annee_courante = prix_m2_annuel.iloc[i]['annee']
            prix_courant = prix_m2_annuel.iloc[i]['prixm2']

            # Calcul de la variation en pourcentage
            variation = (prix_max_annee - prix_courant) / prix_courant * 100
            variations[f'{int(annee_courante)}-{max_annee}'] = {
                'variation': variation,
                'prix_courant': prix_courant,
                'prix_max_annee': prix_max_annee
            }

        return variations

    with tab1:
        data_appartement = data_commune[data_commune['type'] == 'Appartement']
        if not data_appartement.empty:
            # Vérification de l'existence de données pour éviter l'erreur
            if len(data_appartement) > 0:
                variations_appartement = calcul_variations_comparatives(data_appartement)

                st.metric(label=f"Prix au m² moyen en {annee}", 
                        value=f"{data_appartement['prixm2'].iloc[-1]:,.0f}€/m²",
                        delta=f"{data_appartement['prixm2'].pct_change().iloc[-1] * 100:.2f}% depuis 12 mois")
            
                # Affichage des variations sur une même ligne
                cols = st.columns(len(variations_appartement)) 

                for i, (periode, variation_app) in enumerate(variations_appartement.items()):
                    with cols[i]: 
                        st.metric(label=periode, 
                                value="", 
                                delta=f"{variation_app['variation']:.2f}%")

                # Création de la courbe avec zone remplie et points (markers)
                fig_appartement = px.area(data_appartement, x='annee', y='prixm2',
                                        labels={'annee': 'Année', 'prixm2': 'Prix au m² (€)'},
                                        title=f'Prix au m² des appartements à {commune_selectionnee}',
                                        markers=True,
                                        line_shape='spline')

                # Ajout des informations de survol personnalisées
                fig_appartement.update_traces(hovertemplate='<b>%{x}</b>: %{y:,.0f}€/m²')

                # Mettre à jour les ticks de l'axe des années pour afficher des années pleines
                fig_appartement.update_layout(xaxis=dict(tickmode='linear', tick0=data_appartement['annee'].min(), dtick=1),
                yaxis=dict(range=[data_appartement['prixm2'].min() * 0.95, data_appartement['prixm2'].max() * 1.05])
        )

                # Afficher le graphique
                st.plotly_chart(fig_appartement, config={'modeBarButtonsToRemove': ['zoom', 'pan','lasso2d','select','zoomIn','zoomOut', 'autoScale'],
                                                         'displaylogo': False})
        else:
            st.write("Aucune donnée pour les appartements dans cette commune.")
    
    with tab2:
        data_maison = data_commune[data_commune['type'] == 'Maison']
        if not data_maison.empty:
            # Vérification de l'existence de données pour éviter l'erreur
            if len(data_maison) > 0:
               
                variations_maison = calcul_variations_comparatives(data_maison)

                st.metric(label=f"Prix au m² moyen en {annee}", 
                        value=f"{data_maison['prixm2'].iloc[-1]:,.0f}€/m²",
                        delta=f"{data_maison['prixm2'].pct_change().iloc[-1] * 100:.2f}% depuis 12 mois")


                # Affichage des variations sur une même ligne
                cols = st.columns(len(variations_maison)) 

                for i, (periode, variation_app) in enumerate(variations_maison.items()):
                    with cols[i]: 
                        st.metric(label=periode, 
                                value="", 
                                delta=f"{variation_app['variation']:.2f}%")

                # Création de la courbe avec zone remplie et points (markers)
                fig_maison = px.area(data_maison, x='annee', y='prixm2',
                                    labels={'annee': 'Année', 'prixm2': 'Prix au m² (€)'},
                                    title=f'Prix au m² des maisons à {commune_selectionnee}',
                                    markers=True,
                                    line_shape='spline')

                # Ajout des informations de survol personnalisées
                fig_maison.update_traces(hovertemplate='<b>%{x}</b>: %{y:,.0f}€')

                # Mettre à jour les ticks de l'axe des années pour afficher des années pleines
                fig_maison.update_layout(xaxis=dict(tickmode='linear', tick0=data_maison['annee'].min(), dtick=1),
                yaxis=dict(range=[data_maison['prixm2'].min() * 0.95, data_maison['prixm2'].max() * 1.05])
        )

                # Afficher le graphique
                st.plotly_chart(fig_maison,config={'modeBarButtonsToRemove': ['zoom', 'pan','lasso2d','select','zoomIn','zoomOut', 'autoScale'],
                                                         'displaylogo': False})
        else:
            st.write("Aucune donnée pour les maisons dans cette commune.")
else:
    st.write("Aucune donnée disponible pour cette commune.")
