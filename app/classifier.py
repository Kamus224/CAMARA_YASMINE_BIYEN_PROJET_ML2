"""
Classifieur EcoSort — pont entre le modèle du Jalon 1 et l'application.

Logique de décision :
1. Si le nom du produit contient un mot-clé D3E  -> Bac Électronique.
   (le dataset Kaggle ne contient pas de classe électronique : on cartographie
   cette catégorie par mots-clés, comme autorisé par le sujet)
2. Sinon, l'image du produit est passée au CNN qui prédit la matière parmi
   {cardboard, glass, metal, paper, plastic, trash}.
3. La matière est mappée vers la poubelle officielle via MATERIAL_TO_BIN.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass

import numpy as np
from PIL import Image

from config import (
    BINS,
    IMG_SIZE,
    MATERIAL_TO_BIN,
    MODEL_CLASSES,
    MODEL_PATH,
    is_electronic,
)

logger = logging.getLogger(__name__)

_model = None  # cache du modèle (chargé une seule fois)


@dataclass
class SortResult:
    bin_key: str          # "JAUNE", "VERTE", "BLEUE", "D3E", "MARRON"
    material: str | None  # matière prédite (None si décision D3E)
    confidence: float     # confiance de la prédiction (1.0 si D3E)
    probabilities: dict[str, float]  # distribution complète (vide si D3E)

    @property
    def bin(self) -> dict:
        return BINS[self.bin_key]


def load_model():
    """Charge le modèle Keras une seule fois (lazy loading)."""
    global _model
    if _model is None:
        import tensorflow as tf  # import tardif : accélère le démarrage
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

        logger.info("Chargement du modèle : %s", MODEL_PATH)
        _model = tf.keras.models.load_model(
            MODEL_PATH,
            custom_objects={"preprocess_input": preprocess_input},
            compile=False,   # pas besoin de l'optimiseur pour prédire
            safe_mode=False, # requis pour désérialiser une couche Lambda
        )
    return _model


def _preprocess(image_bytes: bytes) -> np.ndarray:
    """Prépare l'image pour MobileNetV2 : RGB, 224x224, batch de 1.

    NB : la normalisation [-1, 1] est intégrée DANS le modèle
    (couche preprocess_input), on envoie donc les pixels bruts 0-255.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.asarray(img, dtype=np.float32)
    return np.expand_dims(arr, axis=0)


def predict_material(image_bytes: bytes) -> tuple[str, float, dict[str, float]]:
    """Prédit la matière d'un emballage à partir de l'image produit."""
    model = load_model()
    batch = _preprocess(image_bytes)
    probs = model.predict(batch, verbose=0)[0]

    distribution = {cls: float(p) for cls, p in zip(MODEL_CLASSES, probs)}
    best_idx = int(np.argmax(probs))
    return MODEL_CLASSES[best_idx], float(probs[best_idx]), distribution


def classify_product(product_name: str, image_bytes: bytes | None) -> SortResult:
    """
    Décision finale de tri pour un produit sélectionné par l'utilisateur.
    """
    # Règle 1 : détection D3E par mots-clés (prioritaire)
    if is_electronic(product_name):
        logger.info("Produit '%s' détecté comme D3E (mots-clés)", product_name)
        return SortResult(
            bin_key="D3E", material=None, confidence=1.0, probabilities={}
        )

    # Règle 2 : prédiction de la matière par le CNN
    if image_bytes is None:
        # Pas d'image exploitable -> déchet résiduel par prudence
        logger.warning("Aucune image pour '%s' : fallback MARRON", product_name)
        return SortResult(
            bin_key="MARRON", material=None, confidence=0.0, probabilities={}
        )

    material, confidence, distribution = predict_material(image_bytes)
    bin_key = MATERIAL_TO_BIN[material]
    logger.info(
        "Produit '%s' -> matière=%s (%.1f%%) -> poubelle %s",
        product_name, material, confidence * 100, bin_key,
    )
    return SortResult(
        bin_key=bin_key,
        material=material,
        confidence=confidence,
        probabilities=distribution,
    )
