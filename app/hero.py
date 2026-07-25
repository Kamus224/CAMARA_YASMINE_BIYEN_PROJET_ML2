"""
hero.py — Section d'accueil façon ecosort.org (format grand écran).

- Titre en dégradé vert -> cyan animé horizontalement (effet shine)
- Cartes statistiques larges, alignées à gauche, style "features"
- Boule lumineuse qui dérive doucement de gauche à droite en arrière-plan

Usage dans app.py (remplace st.title + st.caption) :
    from hero import render_hero
    render_hero()
"""

import streamlit as st

# Adaptez librement ces chiffres à votre projet réel.
STATS = [
    ("5", "Poubelles de tri couvertes",
     "Jaune, verte, bleue, bac D3E et marron — les catégories officielles."),
    ("2", "IA combinées",
     "Détection D3E par mots-clés + CNN MobileNetV2 sur l'image produit."),
    ("< 3 s", "Pour un verdict de tri",
     "De la recherche Jumia à la bonne poubelle, instantanément."),
]


def render_hero() -> None:
    stats_html = "".join(
        f"""
        <div class="eco-stat">
            <div class="eco-stat-value">{value}</div>
            <div class="eco-stat-title">{title}</div>
            <div class="eco-stat-desc">{desc}</div>
        </div>
        """
        for value, title, desc in STATS
    )

    st.markdown(
        f"""
        <style>
        /* ---------- Boule lumineuse qui dérive de gauche à droite ---------- */
        .eco-orb {{
            position: fixed;
            top: 8vh;
            left: 0;
            width: 420px;
            height: 420px;
            border-radius: 50%;
            background: radial-gradient(circle,
                        rgba(34,197,94,.32) 0%,
                        rgba(45,212,191,.14) 45%,
                        transparent 70%);
            filter: blur(70px);
            pointer-events: none;
            z-index: 0;
            animation: eco-drift 22s ease-in-out infinite alternate;
        }}
        @keyframes eco-drift {{
            from {{ transform: translate(-15vw, 0); }}
            to   {{ transform: translate(75vw, 6vh); }}
        }}

        /* ---------- Hero ---------- */
        .eco-hero {{
            text-align: center;
            padding: 60px 10px 26px 10px;
            position: relative;
            z-index: 1;
        }}
        .eco-hero-badge {{
            display: inline-block;
            padding: 5px 14px;
            border: 1px solid rgba(34,197,94,.4);
            border-radius: 999px;
            color: #22c55e;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: 18px;
        }}
        .eco-hero-title {{
            font-size: clamp(2.4rem, 7vw, 4.5rem);
            font-weight: 900;
            line-height: 1.05;
            letter-spacing: .04em;
            text-transform: uppercase;
            background: linear-gradient(
                90deg,
                #22c55e 0%,
                #2dd4bf 35%,
                #38bdf8 50%,
                #2dd4bf 65%,
                #22c55e 100%
            );
            background-size: 200% 100%;
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 14px 0;
            animation: eco-shine 6s linear infinite;
        }}
        @keyframes eco-shine {{
            from {{ background-position: 200% 0; }}
            to   {{ background-position: -200% 0; }}
        }}
        .eco-hero-sub {{
            color: #93a89b;
            font-size: 1.08rem;
            max-width: 620px;
            margin: 0 auto 34px auto;
            line-height: 1.55;
        }}

        /* ---------- Cartes stats format grand écran (style features) ---------- */
        .eco-stats {{
            display: flex;
            justify-content: center;
            gap: 18px;
            flex-wrap: wrap;
        }}
        .eco-stat {{
            flex: 1 1 220px;
            max-width: 340px;
            background: rgba(14, 21, 16, .85);
            border: 1px solid rgba(34,197,94,.35);
            border-radius: 14px;
            padding: 22px 24px;
            text-align: left;
            transition: transform .15s ease, border-color .15s ease,
                        box-shadow .15s ease;
        }}
        .eco-stat:hover {{
            transform: translateY(-3px);
            border-color: rgba(34,197,94,.7);
            box-shadow: 0 10px 30px rgba(34,197,94,.15);
        }}
        .eco-stat-value {{
            font-size: 2.1rem;
            font-weight: 800;
            background: linear-gradient(90deg, #22c55e, #2dd4bf);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .eco-stat-title {{
            font-weight: 700;
            font-size: 1.02rem;
            color: #22c55e;
            margin-top: 6px;
        }}
        .eco-stat-desc {{
            font-size: .86rem;
            color: #93a89b;
            margin-top: 6px;
            line-height: 1.5;
        }}

        @media (prefers-reduced-motion: reduce) {{
            .eco-orb, .eco-hero-title {{ animation: none; }}
        }}
        @media (prefers-reduced-motion: no-preference) {{
            .eco-hero {{ animation: eco-fade .5s ease both; }}
            @keyframes eco-fade {{
                from {{ opacity: 0; transform: translateY(8px); }}
                to   {{ opacity: 1; transform: none; }}
            }}
        }}
        </style>

        <div class="eco-orb"></div>
        <div class="eco-hero">
            <div class="eco-hero-badge">♻️ Tri intelligent par IA</div>
            <h1 class="eco-hero-title">EcoSort-Search</h1>
            <p class="eco-hero-sub">
                Recherchez un produit sur Jumia, sélectionnez-le, et laissez
                l'IA vous indiquer instantanément la bonne poubelle de tri.
            </p>
            <div class="eco-stats">{stats_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )