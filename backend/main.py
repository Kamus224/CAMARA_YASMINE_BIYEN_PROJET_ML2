"""
EcoSort-Search — Backend API (FastAPI).

Sert le site web dynamique (frontend/) et expose une petite API JSON qui
réutilise votre scraper Jumia et votre classifieur IA du projet d'origine :

    GET  /                -> le site (frontend/index.html)
    GET  /api/bins        -> métadonnées des 5 poubelles (couleurs, libellés…)
    GET  /api/search?q=…  -> scrape Jumia, classe chaque produit, renvoie du JSON

Dégradation élégante :
- Si TensorFlow / le modèle .keras ne sont pas installés, la classification
  bascule automatiquement sur une heuristique par mots-clés (le site reste
  100 % fonctionnel pour la démo et le développement).
- Si Jumia est injoignable, l'API renvoie un petit jeu de données de
  démonstration pour que le design reste explorable (champ "demo": true).

Lancement :
    pip install -r requirements.txt
    uvicorn backend.main:app --reload --port 8000
    # puis ouvrez http://localhost:8000
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# --- Rendre les modules du projet importables (app/) --------------------------
ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
FRONTEND_DIR = ROOT / "frontend"
sys.path.insert(0, str(APP_DIR))

from config import BINS  # noqa: E402
from scraper import search_jumia, download_image  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ecosort.api")

app = FastAPI(title="EcoSort-Search API", version="2.0")


# ---------------------------------------------------------------------------
# Classification : IA complète si disponible, sinon repli par mots-clés
# ---------------------------------------------------------------------------
def _classify(product) -> dict:
    """Classe un produit et renvoie un dict JSON-friendly.

    Essaie le classifieur complet (mots-clés D3E + CNN). Si le CNN n'est pas
    disponible (TensorFlow/model absents), retombe sur une heuristique légère.
    """
    try:
        from classifier import classify_product  # import tardif (charge TF)

        image_bytes = download_image(product.image_url) if product.image_url else None
        result = classify_product(product.name, image_bytes)
        return {
            "bin_key": result.bin_key,
            "material": result.material,
            "confidence": round(result.confidence, 4),
            "method": "cnn" if result.material else ("d3e" if result.bin_key == "D3E" else "fallback"),
        }
    except Exception as exc:  # TF absent, modèle manquant, image illisible…
        logger.warning("Classifieur complet indisponible (%s) — repli mots-clés", exc)
        return _classify_lite(product)


def _classify_lite(product) -> dict:
    """Heuristique sans IA lourde : mots-clés D3E + matière devinée par le nom."""
    from config import is_electronic, MATERIAL_TO_BIN

    name = product.name.lower()
    if is_electronic(product.name):
        return {"bin_key": "D3E", "material": None, "confidence": 1.0, "method": "d3e"}

    # Indices de matière dans le nom du produit (approximatif, sans image)
    hints = {
        "verre": "VERTE", "bocal": "VERTE", "pot ": "VERTE", "bouteille en verre": "VERTE",
        "papier": "BLEUE", "cahier": "BLEUE", "livre": "BLEUE", "magazine": "BLEUE",
        "carton": "JAUNE", "canette": "JAUNE", "conserve": "JAUNE", "brique": "JAUNE",
        "bouteille": "JAUNE", "plastique": "JAUNE", "flacon": "JAUNE", "bidon": "JAUNE",
    }
    for key, bin_key in hints.items():
        if key in name:
            return {"bin_key": bin_key, "material": None, "confidence": 0.55, "method": "keyword"}
    return {"bin_key": "MARRON", "material": None, "confidence": 0.4, "method": "keyword"}


# ---------------------------------------------------------------------------
# Jeu de démonstration (si Jumia est injoignable)
# ---------------------------------------------------------------------------
_DEMO_PRODUCTS = [
    ("Bouteille d'eau minérale 1,5L (pack de 6)", "3 500 FCFA", "JAUNE", None, 0.94),
    ("Canette de soda 33cl", "400 FCFA", "JAUNE", "metal", 0.91),
    ("Bocal en verre pour conserves 500ml", "1 200 FCFA", "VERTE", "white-glass", 0.88),
    ("Cahier 200 pages grands carreaux", "900 FCFA", "BLEUE", "paper", 0.9),
    ("Écouteurs Bluetooth sans fil", "12 900 FCFA", "D3E", None, 1.0),
    ("Chargeur USB-C rapide 25W", "6 500 FCFA", "D3E", None, 1.0),
    ("Sachet plastique de riz 5kg", "4 200 FCFA", "MARRON", "trash", 0.6),
]


def _demo_payload(keyword: str) -> dict:
    products = []
    for name, price, bin_key, material, conf in _DEMO_PRODUCTS:
        products.append({
            "name": name,
            "price": price,
            "image_url": "",
            "product_url": "#",
            "bin_key": bin_key,
            "material": material,
            "confidence": conf,
            "method": "cnn" if material else ("d3e" if bin_key == "D3E" else "keyword"),
        })
    return {"query": keyword, "demo": True, "count": len(products), "products": products}


# ---------------------------------------------------------------------------
# Endpoints API
# ---------------------------------------------------------------------------
@app.get("/api/bins")
def get_bins() -> JSONResponse:
    """Renvoie les métadonnées des 5 poubelles (source unique : config.py)."""
    order = ["JAUNE", "VERTE", "BLEUE", "D3E", "MARRON"]
    payload = [{"key": k, **BINS[k]} for k in order]
    return JSONResponse(payload)


@app.get("/api/search")
def search(q: str = Query(..., min_length=1, description="Nom du produit")) -> JSONResponse:
    """Scrape Jumia pour `q`, classe chaque produit, renvoie la liste triée."""
    keyword = q.strip()
    try:
        found = search_jumia(keyword, max_results=8)
    except Exception as exc:
        logger.warning("Jumia injoignable (%s) — bascule en mode démo", exc)
        return JSONResponse(_demo_payload(keyword))

    if not found:
        return JSONResponse({"query": keyword, "demo": False, "count": 0, "products": []})

    products = []
    for p in found:
        verdict = _classify(p)
        products.append({
            "name": p.name,
            "price": p.price,
            "image_url": p.image_url,
            "product_url": p.product_url,
            **verdict,
        })

    return JSONResponse({
        "query": keyword,
        "demo": False,
        "count": len(products),
        "products": products,
    })


# ---------------------------------------------------------------------------
# Frontend : sert le site
# ---------------------------------------------------------------------------
@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


# Fichiers statiques éventuels (images, favicon…) déposés dans frontend/
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
