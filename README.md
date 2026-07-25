# CAMARA_YASMINE_BIYEN_PROJET_ML2
# ♻️ EcoSort-Search

Application web containerisée d'aide au tri sélectif. L'utilisateur saisit le
nom d'un produit, l'application interroge **Jumia** en direct, puis un modèle
de **Deep Learning** (Transfer Learning MobileNetV2) attribue au produit
sélectionné sa consigne de tri en colorant l'écran aux couleurs de la poubelle
correspondante.

## Nouveau : site web dynamique (FastAPI + frontend)

En plus de l'interface Streamlit, le projet dispose maintenant d'un **vrai site
web dynamique** avec un design soigné : un backend **FastAPI** réutilise le
scraper Jumia et le classifieur IA, et sert un frontend moderne et animé.

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
# puis ouvrez http://localhost:8000
```

Points clés :

- **`frontend/index.html`** — site en un seul fichier (HTML/CSS/JS, sans build).
  Le signature visuel : un « plan de tri » où chaque produit trouvé tombe dans
  sa poubelle colorée (jaune, verte, bleue, bac D3E, marron).
- **`backend/main.py`** — API JSON :
  - `GET /api/search?q=…` → scrape Jumia, classe chaque produit, renvoie du JSON.
  - `GET /api/bins` → couleurs et libellés des 5 poubelles (source : `app/config.py`).
- **Dégradation élégante** : si TensorFlow ou le modèle ne sont pas installés, la
  classification bascule sur une heuristique par mots-clés ; si Jumia est
  injoignable, l'API renvoie un jeu de démonstration. Le site reste toujours
  fonctionnel.
- Ouvrir `frontend/index.html` **directement** (double-clic) affiche le site en
  mode démo, sans backend — pratique pour prévisualiser le design.

L'ancienne interface Streamlit reste disponible :

```bash
streamlit run app/app.py
```

---

## Démarrage rapide (Docker, interface Streamlit d'origine)

```bash
docker build -t ecosort .
docker run -p 8501:8501 ecosort
```

ou

```bash
docker-compose up -d --build
```

Puis ouvrir **http://localhost:8501**.

> Le fichier `models/modele_eco_sort.h5` doit être présent (produit par le
> Jalon 1, voir ci-dessous). Il est inclus dans le dépôt ou téléchargeable
> depuis l'onglet *Releases* de GitHub s'il dépasse 100 Mo.

## Structure du dépôt

```
ecosort-search/
├── app/
│   ├── app.py          # Interface Streamlit (recherche, sélection, verdict)
│   ├── scraper.py      # Scraping Jumia (Requests + BeautifulSoup)
│   ├── classifier.py   # Chargement du modèle + décision de poubelle
│   └── config.py       # Catégories de tri, couleurs, mots-clés D3E
├── training/
│   ├── download_dataset.py  # Téléchargement du dataset Kaggle
│   ├── train.py             # Entraînement reproductible (Jalon 1)
│   └── evaluate.py          # Rapport de classif + matrice de confusion
├── models/             # modele_eco_sort.h5 (sortie du Jalon 1)
├── docs/CONTRIBUTING.md # Workflow Git de l'équipe
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .gitignore
```

## Jalon 1 — Entraînement du modèle

Dataset : [Garbage Classification](https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification)
(Kaggle) — classes `cardboard, glass, metal, paper, plastic, trash`.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt kaggle scikit-learn matplotlib

# 1. Télécharger le dataset (nécessite ~/.kaggle/kaggle.json)
python training/download_dataset.py

# 2. Entraîner (2 phases : tête gelée puis fine-tuning)
python training/train.py --data-dir data/garbage_classification

# 3. Évaluer
python training/evaluate.py --data-dir data/garbage_classification
```

Le modèle est sauvegardé dans `models/modele_eco_sort.h5`. Le preprocessing
MobileNetV2 et l'augmentation de données sont **intégrés dans le modèle** :
l'application lui envoie directement des pixels bruts 0-255.

## Jalon 2 — Scraping & application

- `app/scraper.py` interroge `https://www.jumia.ci/catalog/?q=<mot-clé>` et
  extrait 3 à 5 produits (nom, prix, image, lien) avec des sélecteurs CSS de
  secours, la structure du site évoluant régulièrement.
- Test rapide : `python app/scraper.py "bouteille d'eau"`.
- Adapter `BASE_URL` dans `scraper.py` selon le pays (jumia.ci, jumia.com.ng…).

### Logique de décision de tri

1. **D3E d'abord** : si le nom du produit contient un mot-clé électronique
   (chargeur, écouteurs, mixeur…), verdict immédiat *Bac Électronique* —
   le dataset Kaggle ne contenant pas de classe électronique, cette catégorie
   est cartographiée par mots-clés, comme le permet le sujet.
2. Sinon, l'**image du produit** est classée par le CNN parmi les 6 matières,
   puis mappée vers la poubelle officielle :

| Matière prédite | Poubelle |
| --- | --- |
| plastic, metal, cardboard | 🟡 JAUNE |
| glass | 🟢 VERTE |
| paper | 🔵 BLEUE |
| trash | ⚫ MARRON / NOIRE |
| *(mots-clés électroniques)* | 🎛️ Bac D3E |

## Équipe & workflow Git

Voir [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) : trois branches de travail,
zéro push direct sur `main`, toute contribution passe par une Pull Request
relue et validée par au moins un autre membre.

| Membre | Branche | Rôle principal |
| --- | --- | --- |
| Étudiant 1 | `feature/model` | Jalon 1 : dataset, entraînement, évaluation |
| Étudiant 2 | `feature/scraping` | Jalon 2 : scraper Jumia, robustesse |
| Étudiant 3 | `feature/app-docker` | Interface Streamlit, Dockerfile, intégration |

## Échéance

Date butoir : **25/07/2026 à 23h59:59** (bonus 0,5 pt/jour d'avance, plafonné
à 5 ; pénalité 2 pts/jour de retard).

