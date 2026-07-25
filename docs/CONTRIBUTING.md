# 🤝 Workflow Git de l'équipe EcoSort

Règles imposées par le sujet : historique fluide sur **trois branches
distinctes**, **zéro push direct sur `main`**, toute contribution passe par
une **Pull Request relue et validée par au moins un autre membre**, et un
`.gitignore` correct dès le premier jour.

## 1. Mise en place (une seule fois, par le créateur du dépôt)

```bash
git init ecosort-search && cd ecosort-search
# ... ajouter les fichiers du squelette ...
git add . && git commit -m "chore: squelette initial du projet"
git branch -M main
git remote add origin git@github.com:<orga>/ecosort-search.git
git push -u origin main
```

Puis sur GitHub : **Settings → Branches → Add branch ruleset** sur `main` :
- ✅ Require a pull request before merging
- ✅ Require at least **1 approval**
- ✅ Block force pushes

## 2. Branches de travail

Chaque membre travaille sur sa branche, créée depuis `main` :

```bash
git checkout main && git pull
git checkout -b feature/model      # Yasmine Diallo
git checkout -b feature/scraping   # Biyen abdoul
git checkout -b feature/app-docker # Camara Alpha Oumar
```

## 3. Cycle quotidien

```bash
git checkout feature/scraping
git pull origin main          # rester à jour avec main
# ... coder ...
git add app/scraper.py
git commit -m "feat(scraper): extraction du prix et fallback de sélecteurs"
git push -u origin feature/scraping
```

Commits **petits et fréquents** (l'enseignant évalue la fluidité de
l'historique et la contribution individuelle). Convention de messages :
`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.

## 4. Pull Requests

1. Ouvrir la PR sur GitHub : `feature/xxx` → `main`.
2. Décrire **quoi** et **pourquoi**, et comment tester.
3. Demander la revue d'un autre membre (bouton *Reviewers*).
4. Le relecteur commente, demande des changements si besoin, puis **Approve**.
5. Merge (préférer *Squash and merge* pour un `main` propre), puis supprimer
   la branche distante et recréer une branche fraîche pour la suite.

## 5. À ne JAMAIS commiter

- Le dataset Kaggle (`data/`) — plusieurs centaines de Mo
- Les environnements virtuels (`.venv/`, `__pycache__/`)
- Les secrets (`kaggle.json`, `.env`)

Tout cela est déjà couvert par le `.gitignore`. Si le modèle `.h5` dépasse
100 Mo (limite GitHub), le publier via **Releases** ou **Git LFS** et le
documenter dans le README.

## 6. Répartition indicative des rôles

| Membre | Périmètre | Livrables principaux |
| --- | --- | --- |
| Étudiant 1 | IA / Jalon 1 | `training/*.py`, `models/modele_eco_sort.h5`, métriques |
| Étudiant 2 | Scraping / Jalon 2 | `app/scraper.py`, robustesse, tests manuels |
| Étudiant 3 | App & Ops | `app/app.py`, `app/classifier.py`, `Dockerfile`, `docker-compose.yml` |

Chacun relit au moins les PR d'un autre membre : la note étant individuelle,
les trois doivent apparaître comme auteurs **et** relecteurs dans l'historique.
