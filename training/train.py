"""
Jalon 1 — Entraînement du modèle EcoSort (Transfer Learning MobileNetV2).

Dataset attendu : "Garbage Classification" (Kaggle), organisé ainsi :

    data/
    └── garbage_classification/
        ├── cardboard/   (403 images)
        ├── glass/       (501 images)
        ├── metal/       (410 images)
        ├── paper/       (594 images)
        ├── plastic/     (482 images)
        └── trash/       (137 images)

Téléchargement (voir training/download_dataset.py) puis :

    python training/train.py --data-dir data/garbage_classification

Sortie : models/modele_eco_sort.h5 (chargé ensuite par l'application).

Reproductibilité : seeds fixés, split déterministe, hyperparamètres en CLI.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# ---------------------------------------------------------------------------
# Reproductibilité
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

IMG_SIZE = (224, 224)
CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]


def build_datasets(data_dir: Path, batch_size: int):
    """Charge le dataset avec un split train/validation 80/20 déterministe."""
    common = dict(
        directory=data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASSES,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        seed=SEED,
        validation_split=0.2,
    )
    train_ds = keras.utils.image_dataset_from_directory(
        subset="training", shuffle=True, **common
    )
    val_ds = keras.utils.image_dataset_from_directory(
        subset="validation", shuffle=False, **common
    )

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(autotune)
    val_ds = val_ds.cache().prefetch(autotune)
    return train_ds, val_ds


def build_model(num_classes: int = len(CLASSES)) -> keras.Model:
    """MobileNetV2 pré-entraîné ImageNet + tête de classification custom.

    L'augmentation de données et le preprocessing sont intégrés au modèle :
    l'application n'a donc qu'à fournir des pixels bruts 0-255.
    """
    data_augmentation = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.15),
            layers.RandomContrast(0.1),
        ],
        name="augmentation",
    )

    base = keras.applications.MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # phase 1 : gel du backbone

    inputs = keras.Input(shape=IMG_SIZE + (3,))
    x = data_augmentation(inputs)
    x = keras.applications.mobilenet_v2.preprocess_input(x)  # [-1, 1]
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    return keras.Model(inputs, outputs, name="ecosort_mobilenetv2")


def main():
    parser = argparse.ArgumentParser(description="Entraînement EcoSort")
    parser.add_argument("--data-dir", type=Path, required=True,
                        help="Racine du dataset (dossiers = classes)")
    parser.add_argument("--output", type=Path,
                        default=Path("models/modele_eco_sort.h5"))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=15,
                        help="Époques phase 1 (backbone gelé)")
    parser.add_argument("--fine-tune-epochs", type=int, default=10,
                        help="Époques phase 2 (fine-tuning)")
    parser.add_argument("--fine-tune-at", type=int, default=100,
                        help="Index de couche à partir duquel dégeler")
    args = parser.parse_args()

    train_ds, val_ds = build_datasets(args.data_dir, args.batch_size)
    model = build_model()

    # -------------------------- Phase 1 : tête seule ----------------------
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
        ),
    ]

    print("\n=== Phase 1 : entraînement de la tête (backbone gelé) ===")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
    )

    # -------------------------- Phase 2 : fine-tuning ---------------------
    print("\n=== Phase 2 : fine-tuning des couches hautes de MobileNetV2 ===")
    base = model.get_layer("mobilenetv2_1.00_224")
    base.trainable = True
    for layer in base.layers[: args.fine_tune_at]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-5),  # LR très faible
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.fine_tune_epochs,
        callbacks=callbacks,
    )

    # -------------------------- Évaluation & sauvegarde -------------------
    loss, acc = model.evaluate(val_ds)
    print(f"\nValidation finale — loss: {loss:.4f} | accuracy: {acc:.2%}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    print(f"Modèle sauvegardé : {args.output}")


if __name__ == "__main__":
    main()
