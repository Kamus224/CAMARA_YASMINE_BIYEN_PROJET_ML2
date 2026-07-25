# 📦 models/

Ce dossier doit contenir **`modele_eco_sort.h5`**, le modèle produit par le
Jalon 1 :

```bash
python training/download_dataset.py
python training/train.py --data-dir data/garbage_classification
```

Sans ce fichier, l'application démarre mais la classification échouera au
premier produit sélectionné. Si le fichier dépasse 100 Mo, ne le poussez pas
directement sur GitHub : utilisez une **Release** ou **Git LFS** et
documentez le lien de téléchargement dans le README principal.
