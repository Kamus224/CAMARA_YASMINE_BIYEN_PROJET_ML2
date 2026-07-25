"""
Évaluation du modèle entraîné : rapport de classification et matrice de
confusion sur le split de validation (utile pour le rapport du projet).

Usage :
    pip install scikit-learn matplotlib
    python training/evaluate.py --data-dir data/garbage_classification \
        --model models/modele_eco_sort.h5
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras

SEED = 42
IMG_SIZE = (224, 224)
CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path,
                        default=Path("models/modele_eco_sort.h5"))
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    val_ds = keras.utils.image_dataset_from_directory(
        args.data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASSES,
        image_size=IMG_SIZE,
        batch_size=args.batch_size,
        seed=SEED,
        validation_split=0.2,
        subset="validation",
        shuffle=False,
    )

    model = keras.models.load_model(args.model)

    y_true, y_pred = [], []
    for images, labels in val_ds:
        probs = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(probs, axis=1))

    from sklearn.metrics import classification_report, confusion_matrix

    print("\n=== Rapport de classification ===")
    print(classification_report(y_true, y_pred, target_names=CLASSES))

    cm = confusion_matrix(y_true, y_pred)
    print("=== Matrice de confusion (lignes = vérité, colonnes = prédit) ===")
    header = " " * 11 + " ".join(f"{c[:5]:>6}" for c in CLASSES)
    print(header)
    for cls, row in zip(CLASSES, cm):
        print(f"{cls:<10}" + " ".join(f"{v:>6}" for v in row))

    # Figure optionnelle pour le rapport
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(cm, cmap="Greens")
        ax.set_xticks(range(len(CLASSES)), CLASSES, rotation=45, ha="right")
        ax.set_yticks(range(len(CLASSES)), CLASSES)
        ax.set_xlabel("Classe prédite")
        ax.set_ylabel("Classe réelle")
        ax.set_title("Matrice de confusion — EcoSort")
        for i in range(len(CLASSES)):
            for j in range(len(CLASSES)):
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="black" if cm[i, j] < cm.max() / 2 else "white")
        fig.colorbar(im)
        fig.tight_layout()
        out = Path("training/confusion_matrix.png")
        fig.savefig(out, dpi=150)
        print(f"\nFigure sauvegardée : {out}")
    except ImportError:
        print("\n(matplotlib non installé : figure non générée)")


if __name__ == "__main__":
    main()
