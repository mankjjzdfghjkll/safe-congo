# SAFE CONGO

Plateforme digitale de surveillance épidémiologique et de coordination sanitaire en République Démocratique du Congo.

## Présentation
SAFE CONGO est un réseau digital qui anticipe, protège et connecte tous les acteurs de la santé publique en RDC. La plateforme permet la veille, l’analyse intelligente, la réponse coordonnée et le pilotage des alertes sanitaires sur l’ensemble du territoire national.

## Fonctionnalités principales
- **Détection rapide** : Identification précoce des signaux d’alerte épidémiologique.
- **Analyse intelligente** : Traitement et visualisation des données sanitaires pour une lecture claire des tendances et risques.
- **Réponse coordonnée** : Alertes prioritaires et outils de pilotage pour mobiliser rapidement les ressources de santé publique.
- **Accès rapide** : Connexion et inscription simplifiées pour les autorités sanitaires.

## Technologies
- Python 3.8+
- Streamlit 1.56+
- HTML/CSS personnalisés (animations, design premium)
- Organisation modulaire (src/, utils/, models/, data/)

## Lancement local
1. Cloner le dépôt :
   ```sh
   git clone https://github.com/mankjjzdfghjkll/safe-congo.git
   cd safe-congo
   ```
2. Installer les dépendances :
   ```sh
   pip install -r requirements.txt
   ```
3. Optionnel : définir les mots de passe bootstrap avant le premier lancement :
   ```sh
   set SAFE_CONGO_BOOTSTRAP_ADMIN_PASSWORD=VotreMotDePasseAdmin
   set SAFE_CONGO_BOOTSTRAP_AUTHORITY_PASSWORD=VotreMotDePasseAutorites
   ```
4. Lancer l’application :
   ```sh
   streamlit run app.py
   ```

## Sécurité backend
- SQLite reste utilisé comme base locale; SQLAlchemy n'est pas requis pour sécuriser l'application.
- Les mots de passe sont désormais hachés avec `scrypt` et les anciens hachages SHA-256 sont migrés à la connexion.
- Le schéma SQL versionné est défini dans `database/schema.sql` et les clés étrangères SQLite sont activées à l'ouverture des connexions.

## Structure du projet
- `app.py` : Point d’entrée principal (UI, navigation, rendu des blocs)
- `src/` : Scripts d’entraînement et de gestion des modèles
- `data/` : Données agrégées et nettoyées
- `utils/` : Authentification, navigation, UI admin/autorités
- `pages/` : Pages secondaires (auth, dashboard, etc.)
- `models/` : Modèles ML/statistiques
- `database/` : Schémas SQL

## Personnalisation & Design
- Interface premium, harmonisée, responsive
- Animations CSS (fadeIn, hover, surbrillance)
- Couleurs pastel et bleu SAFE CONGO
- Icônes SVG modernes

## Contribution
Toute contribution est la bienvenue ! Merci de créer une issue ou une pull request pour toute suggestion ou amélioration.

## Licence
© 2026 SAFE CONGO. Tous droits réservés.
