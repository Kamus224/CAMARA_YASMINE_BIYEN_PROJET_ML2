"""
Téléchargement du dataset "Garbage Classification" depuis Kaggle.

Prérequis (une seule fois par machine) :
1. pip install kaggle
2. Créer un token API sur https://www.kaggle.com/settings (bouton
   "Create New Token") -> télécharge kaggle.json
3. Placer kaggle.json dans ~/.kaggle/ (Linux/macOS) ou
   C:\\Users\\<vous>\\.kaggle\\ (Windows)

Usage :
    python training/download_dataset.py

Le dataset est extrait dans data/garbage_classification/ (ignoré par git).
"""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

DATASET_SLUG = "asdasdasasdas/garbage-classification"
DATA_DIR = Path("data")
TARGET_DIR = DATA_DIR / "garbage_classification"
CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]


def main():
    DATA_DIR.mkdir(exist_ok=True)

    print(f"Téléchargement de {DATASET_SLUG} via l'API Kaggle…")
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", DATASET_SLUG,
         "-p", str(DATA_DIR)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(
            "Échec du téléchargement. Vérifiez que kaggle.json est bien "
            "installé (voir docstring de ce script)."
        )

    zip_path = next(DATA_DIR.glob("*.zip"), None)
    if zip_path is None:
        sys.exit("Aucune archive .zip trouvée dans data/.")

    print(f"Extraction de {zip_path}…")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(DATA_DIR)
    zip_path.unlink()

    # Le zip Kaggle contient parfois un niveau de dossier imbriqué
    # ("Garbage classification/Garbage classification/<classes>") :
    # on normalise vers data/garbage_classification/<classes>.
    candidates = [
        p for p in DATA_DIR.rglob("*")
        if p.is_dir() and all((p / c).is_dir() for c in CLASSES)
    ]
    if not candidates:
        sys.exit(
            "Structure inattendue après extraction : dossiers de classes "
            f"introuvables ({', '.join(CLASSES)}). Inspectez data/ à la main."
        )

    source = candidates[0]
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    shutil.move(str(source), str(TARGET_DIR))

    counts = {c: len(list((TARGET_DIR / c).glob("*"))) for c in CLASSES}
    print("\nDataset prêt dans", TARGET_DIR)
    for cls, n in counts.items():
        print(f"  {cls:<10} {n} images")


if __name__ == "__main__":
    main()
