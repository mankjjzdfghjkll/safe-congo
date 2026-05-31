# SAFE CONGO

Plateforme de surveillance epidemiologique et de coordination sanitaire pour la Republique Democratique du Congo.

## Objectif du projet
SAFE CONGO centralise la lecture des signaux sanitaires, facilite la saisie terrain, produit des alertes lisibles pour les autorites et soutient la coordination des actions de reponse. Le depot GitHub versionne volontairement le coeur applicatif et l'architecture technique du projet, pas les donnees locales d'exploitation ni les artefacts produits pendant les essais.

## Architecture 3 tiers
Le projet suit une lecture en 3 tiers simple et defendable.

### 1. Couche presentation
- `app.py` : point d'entree Streamlit.
- `pages/` : pages publiques, admin et autorites.
- `utils/admin_ui.py`, `utils/authority_ui.py`, `utils/public_ui.py`, `utils/sidebar_brand.py` : composants d'interface et theming.

### 2. Couche metier
- `src/alert_system.py` : logique des alertes.
- `src/config.py` : configuration applicative et seuils.
- `src/pdf_generator.py` : generation de rapports PDF.
- `src/pipeline/data_cleaner.py` et `src/pipeline/train_models.py` : preparation des donnees et apprentissage.
- `utils/auth.py`, `utils/navigation.py`, `utils/chart_helpers.py` : authentification, navigation et helpers transverses.

### 3. Couche donnees
- `database/schema.sql` : schema relationnel versionne.
- Les bases SQLite locales, donnees brutes, donnees traitees, logs et modeles entraines restent hors GitHub pour garder un depot propre, portable et academiquement presentable.

## Fonctionnalites principales
- Detection rapide des signaux epidemiologiques.
- Analyse et restitution visuelle des tendances sanitaires.
- Diffusion d'alertes ciblees pour les autorites concernees.
- Saisie terrain et suivi operationnel via une interface admin.
- Parcours public, administratif et autorite clairement separes.

## Contenu versionne sur GitHub
Le depot conserve uniquement les elements necessaires pour comprendre, executer et evaluer l'architecture logicielle.

- Code source de l'application.
- Configuration et dependances.
- Schema de base de donnees.
- README et documentation essentielle.
- Scripts utiles au fonctionnement principal de l'application.

## Contenu garde en local
Les elements suivants ne sont pas obliges d'etre publies sur GitHub et sont exclus du depot propre.

- Donnees brutes et donnees traitees locales.
- Bases SQLite d'execution.
- Logs d'entrainement et fichiers EDA.
- Modeles entraines et matrices d'evaluation exportees.
- Scripts ponctuels d'inspection, de presentation ou d'exploration.

## Stack technique
- Python 3
- Streamlit
- SQLite
- Pandas
- Plotly
- ReportLab

## Lancement local
1. Cloner le depot.
   ```sh
   git clone https://github.com/mankjjzdfghjkll/safe-congo.git
   cd safe-congo
   ```
2. Installer les dependances.
   ```sh
   pip install -r requirements.txt
   ```
3. Definir si besoin les mots de passe bootstrap avant le premier lancement.
   ```sh
   set SAFE_CONGO_BOOTSTRAP_ADMIN_PASSWORD=VotreMotDePasseAdmin
   set SAFE_CONGO_BOOTSTRAP_AUTHORITY_PASSWORD=VotreMotDePasseAutorites
   ```
4. Lancer l'application.
   ```sh
   streamlit run app.py
   ```

## Securite et base de donnees
- Les mots de passe sont haches avec `scrypt` avec migration des anciens hachages a la connexion.
- Le schema SQL versionne est defini dans `database/schema.sql`.
- Les cles etrangeres SQLite sont activees a l'ouverture des connexions.

## Structure du depot
- `app.py`
- `pages/`
- `src/`
- `utils/`
- `database/`
- `scripts/train.py`
- `scripts/show_global_perf.py`
- `requirements.txt`

## Note de depot
Ce depot GitHub est un depot de code et d'architecture. Les fichiers d'exploitation locale et les sorties produites pendant les tests sont volontairement exclus pour conserver un historique propre, lisible et professionnel.
