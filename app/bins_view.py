"""
bins_view.py — Blocs de poubelles colorés, cartes produits horizontales.

Après la recherche, chaque produit est classé automatiquement par l'IA
puis affiché dans le bloc de la poubelle correspondante. À l'intérieur
d'un bloc, les produits sont présentés en cartes verticales alignées
horizontalement (style boutique Jumia), avec une grande image.

Usage dans app.py :
    from bins_view import classify_all, render_bin_blocks
    classified = classify_all(products)      # [(product, SortResult), ...]
    render_bin_blocks(classified)
"""

import html
import logging

import streamlit as st

from classifier import classify_product
from config import BINS
from scraper import download_image

logger = logging.getLogger(__name__)

# Ordre d'affichage des blocs
BIN_ORDER = ["JAUNE", "VERTE", "BLEUE", "D3E", "MARRON"]


def classify_all(products: list) -> list:
    """Classe chaque produit et retourne [(product, SortResult), ...]."""
    classified = []
    progress = st.progress(0.0, text="Analyse des produits par l'IA…")
    for i, product in enumerate(products):
        try:
            image_bytes = (
                download_image(product.image_url) if product.image_url else None
            )
        except Exception as exc:  # image indisponible -> le classifieur gère
            logger.warning("Image indisponible pour '%s' : %s", product.name, exc)
            image_bytes = None
        result = classify_product(product.name, image_bytes)
        classified.append((product, result))
        progress.progress(
            (i + 1) / len(products),
            text=f"Analyse des produits par l'IA… ({i + 1}/{len(products)})",
        )
    progress.empty()
    return classified


def _product_card(product, result, accent: str) -> str:
    """HTML d'une carte produit verticale (image en haut, infos dessous)."""
    name = html.escape(product.name)
    price = html.escape(str(product.price)) if product.price else "—"

    if product.image_url:
        img = (
            f'<img src="{html.escape(product.image_url)}" alt="" '
            'style="width:100%;height:150px;object-fit:contain;'
            'border-radius:10px 10px 0 0;background:#ffffff;display:block;">'
        )
    else:
        img = (
            '<div style="width:100%;height:150px;border-radius:10px 10px 0 0;'
            'background:rgba(255,255,255,.08);display:flex;align-items:center;'
            'justify-content:center;font-size:2rem;">🖼️</div>'
        )

    if result.material is not None:
        detail = (
            f'<span style="background:{accent}22;color:{accent};'
            'padding:2px 8px;border-radius:999px;font-size:.72rem;'
            f'font-weight:700;">{html.escape(result.material)} '
            f"· {result.confidence:.0%}</span>"
        )
    elif result.bin_key == "D3E":
        detail = (
            f'<span style="background:{accent}22;color:{accent};'
            'padding:2px 8px;border-radius:999px;font-size:.72rem;'
            'font-weight:700;">mots-clés D3E</span>'
        )
    else:
        detail = (
            '<span style="opacity:.6;font-size:.72rem;">'
            "image indisponible</span>"
        )

    return (
        '<div style="flex:0 0 180px;max-width:180px;background:rgba(255,255,255,.05);'
        f'border:1px solid {accent}33;border-radius:10px;overflow:hidden;'
        'display:flex;flex-direction:column;">'
        f"{img}"
        '<div style="padding:10px 10px 12px 10px;display:flex;'
        'flex-direction:column;gap:5px;flex:1;">'
        '<div style="font-weight:600;font-size:.82rem;line-height:1.3;'
        'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;'
        f'overflow:hidden;min-height:2.6em;">{name}</div>'
        f'<div style="font-weight:700;font-size:.9rem;">{price}</div>'
        f"<div>{detail}</div>"
        "</div>"
        "</div>"
    )


def render_bin_blocks(classified: list) -> None:
    """Affiche les 5 blocs de poubelles avec leurs produits en cartes."""
    st.subheader("Tri automatique — chaque produit dans sa poubelle")

    # Regroupement par poubelle
    grouped: dict[str, list] = {key: [] for key in BIN_ORDER}
    for product, result in classified:
        grouped.setdefault(result.bin_key, []).append((product, result))

    for bin_key in BIN_ORDER:
        items = grouped.get(bin_key, [])
        bin_info = BINS[bin_key]
        color = bin_info["color"]
        count = len(items)

        if items:
            cards = "".join(_product_card(p, r, color) for p, r in items)
            body = (
                '<div style="display:flex;gap:12px;overflow-x:auto;'
                'justify-content:center;padding:12px 2px 6px 2px;">'
                f"{cards}</div>"
            )
        else:
            body = (
                '<div style="font-size:.85rem;opacity:.5;margin-top:8px;">'
                "Aucun produit de cette recherche dans cette catégorie.</div>"
            )

        st.markdown(
            (
                '<div style="background:#0e1510;'
                f"border:1px solid {color}66;"
                f"border-left:6px solid {color};"
                "border-radius:14px;padding:16px 18px;margin-bottom:14px;"
                f'opacity:{"1" if items else ".55"};">'
                '<div style="display:flex;justify-content:space-between;'
                'align-items:center;gap:10px;flex-wrap:wrap;">'
                '<div style="font-weight:800;letter-spacing:.05em;'
                f'text-transform:uppercase;color:{color};">'
                f'{bin_info["emoji"]} {html.escape(bin_info["label"])}</div>'
                f'<div style="background:{color};color:{bin_info["text_color"]};'
                'font-weight:700;font-size:.78rem;padding:2px 10px;'
                f'border-radius:999px;">{count} produit{"s" if count > 1 else ""}</div>'
                "</div>"
                f"{body}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )