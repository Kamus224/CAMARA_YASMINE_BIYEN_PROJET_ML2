"""
theme.py — Identité visuelle "EcoSort" (inspirée d'ecosort.org)
Fond sombre, accent vert, titres en majuscules, cartes arrondies.

Usage dans app.py :
    from theme import inject_global_css, apply_bin_theme
    inject_global_css()               # juste après st.set_page_config
    apply_bin_theme(current_bin)      # remplace votre ancienne fonction
"""

import streamlit as st

ACCENT = "#22c55e"
BG = "#060a07"
SURFACE = "#0e1510"
BORDER = "rgba(34, 197, 94, 0.25)"
TEXT = "#e8f0ea"
MUTED = "#93a89b"


def inject_global_css() -> None:
    """CSS global : à appeler une seule fois, en haut de app.py."""
    st.markdown(
        f"""
        <style>
        /* ---------- Fond & texte ---------- */
        .stApp {{
            background:
                radial-gradient(1200px 500px at 50% -10%,
                                rgba(34,197,94,0.10), transparent 60%),
                {BG};
            color: {TEXT};
        }}

        /* ---------- Largeur du contenu en mode wide ---------- */
        .block-container {{
            max-width: 1200px;
            padding-top: 1.5rem;
            margin: 0 auto;
        }}

        /* ---------- Titres façon ecosort.org : majuscules, espacés ---------- */
        h1, h2, h3 {{
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 800 !important;
        }}
        h1 {{
            background: linear-gradient(90deg, {TEXT}, {ACCENT});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* ---------- Légendes / texte secondaire ---------- */
        .stCaption, [data-testid="stCaptionContainer"] p {{
            color: {MUTED} !important;
        }}

        /* ---------- Cartes produit ---------- */
        [data-testid="stHorizontalBlock"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 14px;
        }}

        /* ---------- Boutons ---------- */
        .stButton > button, .stFormSubmitButton > button {{
            background: {ACCENT};
            color: #04140a;
            font-weight: 700;
            border: none;
            border-radius: 10px;
            transition: transform .12s ease, box-shadow .12s ease;
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(34,197,94,.35);
            color: #04140a;
        }}

        /* ---------- Champ de recherche ---------- */
        .stTextInput input {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 10px;
            color: {TEXT};
        }}
        .stTextInput input:focus {{
            border-color: {ACCENT};
            box-shadow: 0 0 0 2px rgba(34,197,94,.25);
        }}

        /* ---------- Séparateurs & expander ---------- */
        hr {{ border-color: {BORDER}; }}
        [data-testid="stExpander"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 12px;
        }}

        /* ---------- Barres de progression (probabilités) ---------- */
        [data-testid="stProgressBar"] > div > div {{
            background: {ACCENT};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_bin_theme(bin_key: str | None, bins: dict) -> None:
    """
    Verdict de tri : au lieu de repeindre tout l'écran (illisible sur un
    thème sombre), on affiche un bandeau/carte aux couleurs de la poubelle
    et on colore l'accent de la page.
    """
    if bin_key is None:
        return
    bin_info = bins[bin_key]
    color = bin_info["color"]
    st.markdown(
        f"""
        <style>
        /* Halo de la couleur du bac en haut de page */
        .stApp {{
            background:
                radial-gradient(1200px 500px at 50% -10%,
                                {color}33, transparent 60%),
                {BG} !important;
        }}
        /* Le H2/H3 du verdict prend la couleur du bac */
        h1 {{
            background: linear-gradient(90deg, {TEXT}, {color});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        /* Bordures des cartes assorties */
        [data-testid="stHorizontalBlock"],
        [data-testid="stExpander"] {{
            border-color: {color}66 !important;
        }}
        [data-testid="stProgressBar"] > div > div {{
            background: {color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )