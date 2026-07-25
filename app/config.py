"""
config.py — Les 5 catégories strictes de tri EcoSort-Search.

Chaque produit est classé dans exactement l'une de ces 5 poubelles :
- JAUNE  : emballages ménagers légers  → plastic, metal, cardboard
- VERTE  : verre d'emballage           → glass
- BLEUE  : papiers graphiques propres  → paper
- D3E    : électronique                → détection par mots-clés (ou classe CNN dédiée)
- MARRON : déchets résiduels           → trash

Les couleurs servent d'accent (halo, titre, bordures) sur le thème sombre.
"""

BINS = {
    "JAUNE": {
        "label": "Poubelle jaune — Emballages recyclables",
        "emoji": "🟡",
        "color": "#f5c518",
        "text_color": "#1a1a1a",
        "description": (
            "Tous les emballages ménagers légers : bouteilles de soda et d'eau, "
            "canettes de boisson, boîtes de conserve, briques de lait, flacons "
            "de shampooing, cartons de colis. Videz-les bien, inutile de les laver."
        ),
    },
    "VERTE": {
        "label": "Poubelle verte — Verre",
        "emoji": "🟢",
        "color": "#16a34a",
        "text_color": "#04140a",
        "description": (
            "Uniquement le verre d'emballage : bouteilles de jus ou de vin en "
            "verre, pots de confiture, bocaux de conserve. ⚠️ Vaisselle cassée, "
            "vitres et miroirs interdits : ils vont dans la poubelle marron."
        ),
    },
    "BLEUE": {
        "label": "Poubelle bleue — Papier",
        "emoji": "🔵",
        "color": "#3b82f6",
        "text_color": "#ffffff",
        "description": (
            "Tous les papiers graphiques propres : prospectus publicitaires, "
            "journaux, magazines, cahiers, livres, enveloppes. Le papier gras "
            "ou souillé va dans la poubelle marron."
        ),
    },
    "D3E": {
        "label": "Bac électronique — D3E",
        "emoji": "🎛️",
        "color": "#a78bfa",
        "text_color": "#0e0a1f",
        "description": (
            "Tout produit fonctionnant avec des piles, une batterie ou une prise "
            "électrique : smartphones, écouteurs, chargeurs, mixeurs, montres. "
            "À déposer en point de collecte D3E ou en magasin, jamais dans une "
            "poubelle classique."
        ),
    },
    "MARRON": {
        "label": "Poubelle marron / noire — Résiduels",
        "emoji": "⚫",
        "color": "#b45309",
        "text_color": "#ffffff",
        "description": (
            "Déchets résiduels non recyclables : restes alimentaires, emballages "
            "plastiques souples (sachets, films), produits d'hygiène, objets "
            "multicouches. C'est la poubelle du « quand on ne sait pas »."
        ),
    },
}

# ---------------------------------------------------------------------------
# Correspondance classe CNN (dataset) → poubelle
# ---------------------------------------------------------------------------
MATERIAL_TO_BIN = {
    # Poubelle JAUNE — emballages légers
    "plastic": "JAUNE",
    "metal": "JAUNE",
    "cardboard": "JAUNE",
    # Poubelle VERTE — verre d'emballage (les 3 teintes)
    "brown-glass": "VERTE",
    "green-glass": "VERTE",
    "white-glass": "VERTE",
    # Poubelle BLEUE — papier
    "paper": "BLEUE",
    # Bac D3E — classe dédiée du dataset
    "battery": "D3E",
    # Poubelle MARRON — résiduels
    "biological": "MARRON",
    "clothes": "MARRON",
    "shoes": "MARRON",
    "trash": "MARRON",
}

# ---------------------------------------------------------------------------
# Paramètres du modèle CNN (Jalon 1)
# ---------------------------------------------------------------------------
# ⚠️ Adaptez MODEL_PATH au chemin réel de votre modèle entraîné.
MODEL_PATH = "models/ecosort_mobilenetv2.keras"

# Taille d'entrée MobileNetV2
IMG_SIZE = (224, 224)

# Classes du dataset Kaggle, dans l'ordre appris par le modèle
# (ordre alphabétique = ordre par défaut de image_dataset_from_directory).
MODEL_CLASSES = [
    "battery", "biological", "brown-glass", "cardboard", "clothes",
    "green-glass", "metal", "paper", "plastic", "shoes",
    "trash", "white-glass",
]

# ---------------------------------------------------------------------------
# Mots-clés D3E : si l'un d'eux apparaît dans le nom du produit,
# le verdict D3E est prioritaire sur le CNN.
# ---------------------------------------------------------------------------
D3E_KEYWORDS = [
    # Alimentation électrique
    "pile", "piles", "batterie", "battery", "rechargeable", "chargeur",
    "charger", "usb", "câble", "cable", "adaptateur", "secteur", "power bank",
    "powerbank",
    # Téléphonie & audio
    "smartphone", "téléphone", "telephone", "phone", "iphone", "samsung",
    "tablette", "tablet", "écouteur", "ecouteur", "écouteurs", "ecouteurs",
    "earbuds", "airpods", "casque", "headphone", "enceinte", "speaker",
    "bluetooth", "sans fil", "wireless",
    # Informatique
    "ordinateur", "laptop", "pc", "clavier", "keyboard", "souris", "mouse",
    "écran", "ecran", "monitor", "imprimante", "disque dur", "clé usb",
    "cle usb", "webcam", "routeur", "modem",
    # Électroménager & divers
    "mixeur", "blender", "bouilloire", "fer à repasser", "ventilateur",
    "micro-onde", "micro onde", "réfrigérateur", "refrigerateur", "frigo",
    "climatiseur", "télévision", "television", "tv", "télécommande",
    "telecommande", "montre connectée", "smartwatch", "montre digitale",
    "lampe led", "ampoule", "torche", "console", "manette", "drone",
    "caméra", "camera", "appareil photo", "rasoir électrique",
    "tondeuse électrique", "sèche-cheveux", "seche-cheveux", "lisseur",
    "électrique", "electrique", "électronique", "electronique",
]


def is_electronic(product_name: str) -> bool:
    """Vrai si le nom du produit contient un mot-clé D3E.

    La comparaison est insensible à la casse. Les mots-clés courts et
    ambigus ("tv", "pc", "usb") sont vérifiés comme mots entiers pour
    éviter les faux positifs ("pcs", "tvxq"…) ; les autres par simple
    inclusion, ce qui couvre pluriels et variantes.
    """
    name = f" {product_name.lower()} "
    short_ambiguous = {"tv", "pc", "usb", "led"}
    for kw in D3E_KEYWORDS:
        if kw in short_ambiguous:
            if f" {kw} " in name:
                return True
        elif kw in name:
            return True
    return False
