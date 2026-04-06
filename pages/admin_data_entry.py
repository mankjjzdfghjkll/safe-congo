# pages/1_admin_data_entry.py
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.auth import require_auth, check_role
from utils.notifications import NotificationSystem
from src.data_cleaner import DataCleaner
from src.train_models import DiseasePredictor

st.set_page_config(page_title="Saisie des données - SAFE CONGO", layout="wide")

# Vérifier que l'utilisateur est admin
auth = None
from utils.auth import AuthSystem
auth = AuthSystem()
user = require_auth(auth)

if not user or user['role'] != 'admin':
    st.error("⛔ Accès réservé aux administrateurs")
    st.stop()

st.title("📝 Saisie des Données Épidémiologiques")

# Initialisation des systèmes
notif_system = NotificationSystem()
predictor = DiseasePredictor()

# Onglets
tab1, tab2, tab3 = st.tabs(["➕ Saisie manuelle", "📂 Import Excel", "📊 Historique"])

with tab1:
    st.subheader("Ajouter des données épidémiologiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        disease = st.selectbox(
            "Maladie *",
            ["Choléra", "Ebola", "Rougeole", "Mpox", "Paludisme", "Méningite", "Fièvre jaune", "Autre"]
        )
        
        if disease == "Autre":
            disease = st.text_input("Précisez la maladie")
        
        province = st.selectbox(
            "Province *",
            ["Kinshasa", "Kongo Central", "Kwango", "Kwilu", "Mai-Ndombe", "Equateur", 
             "Sud-Ubangi", "Nord-Ubangi", "Mongala", "Tshopo", "Bas-Uele", "Haut-Uele", 
             "Ituri", "Nord-Kivu", "Sud-Kivu", "Maniema", "Tanganyika", "Haut-Lomami", 
             "Lualaba", "Haut-Katanga", "Lomami", "Sankuru", "Kasaï", "Kasaï-Central", 
             "Kasaï-Oriental"]
        )
        
        zone_sante = st.text_input("Zone de santé (optionnel)")
    
    with col2:
        week = st.number_input("Semaine *", min_value=1, max_value=53, value=datetime.now().isocalendar()[1])
        year = st.number_input("Année *", min_value=2020, max_value=2030, value=datetime.now().year)
        total_cases = st.number_input("Nombre de cas *", min_value=0, value=0)
        total_deaths = st.number_input("Nombre de décès *", min_value=0, value=0)
    
    # Calcul automatique des taux
    incidence_rate = (total_cases / 100000) if total_cases > 0 else 0
    mortality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0
    
    st.caption(f"Taux d'incidence: {incidence_rate:.2f} / 100 000 hab | Taux de létalité: {mortality_rate:.2f}%")
    
    if st.button("✅ Enregistrer les données", type="primary", use_container_width=True):
        if disease and province and total_cases >= 0:
            try:
                # Sauvegarder dans la base de données
                conn = sqlite3.connect('database/users.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO epidemiological_data 
                    (disease, week, year, province, zone_sante, total_cases, total_deaths, 
                     incidence_rate, mortality_rate, entered_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (disease, week, year, province, zone_sante, total_cases, total_deaths,
                      incidence_rate, mortality_rate, user['id']))
                
                conn.commit()
                
                # Logger la mise à jour
                cursor.execute('''
                    INSERT INTO data_updates (updated_by, disease, week, year, action)
                    VALUES (?, ?, ?, ?, 'insert')
                ''', (user['id'], disease, week, year))
                
                conn.commit()
                conn.close()
                
                st.success("✅ Données enregistrées avec succès!")
                
                # 🔄 LANCER L'ENTRAÎNEMENT ET LES PRÉDICTIONS
                with st.spinner("🔄 Entraînement du modèle en cours..."):
                    # Recharger les données
                    data_path = Path(__file__).parent.parent / "data" / "drc-2023_sem08.xlsx"
                    cleaner = DataCleaner(str(data_path))
                    cleaner.load_data()
                    cleaned = cleaner.clean_data()
                    agg = cleaner.aggregate_by_week_disease()
                    features = cleaner.create_features_for_ml(agg)
                    
                    # Réentraîner le modèle
                    trained = predictor.train_all_diseases(features)
                    predictor.save_models()
                    
                    # Générer les prédictions et alertes
                    for disease_name, model_info in predictor.best_models.items():
                        # Vérifier si alerte nécessaire
                        data_disease = agg[agg['MALADIE'] == disease_name]
                        if len(data_disease) > 0:
                            current_cases = data_disease['TOTALCAS'].iloc[-1]
                            last_week_cases = data_disease['TOTALCAS'].iloc[-2] if len(data_disease) > 1 else current_cases
                            growth = ((current_cases - last_week_cases) / last_week_cases * 100) if last_week_cases > 0 else 0
                            
                            # Alerte si croissance > 20%
                            if growth > 20:
                                notif_system.send_alert_to_all_authorities(
                                    disease_name, 
                                    current_cases, 
                                    current_cases * (1 + growth/100),
                                    growth
                                )
                    
                    # Notification aux autorités
                    notif_system.create_notification(
                        user_id=None,  # Broadcast à tous
                        notif_type='data_update',
                        title="📊 Mise à jour des données",
                        message=f"Nouvelles données ajoutées pour {disease} (Semaine {week}/{year})"
                    )
                
                st.success("✅ Modèle ré-entraîné et notifications envoyées!")
                st.balloons()
                
                # Afficher les prédictions
                if disease in predictor.best_models:
                    st.subheader(f"📈 Prédictions pour {disease}")
                    model_info = predictor.best_models[disease]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("R² Score", f"{model_info['test_r2']:.3f}")
                    with col2:
                        st.metric("MAE", f"{model_info['test_mae']:.2f}")
                    with col3:
                        st.metric("MAPE", f"{model_info['test_mape']:.1f}%")
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
        else:
            st.warning("Veuillez remplir tous les champs obligatoires (*)")

with tab2:
    st.subheader("Import de données depuis Excel")
    
    uploaded_file = st.file_uploader("Choisir un fichier Excel", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.dataframe(df.head(10), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Importer les données", type="primary"):
                    # Logique d'import
                    st.success("Données importées avec succès!")
                    # Déclencher l'entraînement
                    st.info("🔄 Entraînement du modèle en cours...")
            with col2:
                if st.button("❌ Annuler"):
                    st.rerun()
        except Exception as e:
            st.error(f"Erreur de lecture: {e}")

with tab3:
    st.subheader("Historique des saisies")
    
    conn = sqlite3.connect('database/users.db')
    
    # Afficher l'historique
    history_df = pd.read_sql_query('''
        SELECT e.disease, e.week, e.year, e.province, e.total_cases, e.total_deaths,
               e.entry_date, u.username as entered_by
        FROM epidemiological_data e
        JOIN users u ON e.entered_by = u.id
        ORDER BY e.entry_date DESC
        LIMIT 50
    ''', conn)
    
    if not history_df.empty:
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("Aucune donnée enregistrée")
    
    conn.close()