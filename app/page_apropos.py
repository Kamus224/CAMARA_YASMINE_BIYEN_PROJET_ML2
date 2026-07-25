"""Page À propos."""

import streamlit as st

st.title("À propos du projet")

st.markdown(
    """
EcoSort-Search est un projet de tri intelligent des déchets par IA :
recherche de produits sur Jumia, classification de la matière par CNN
(MobileNetV2), et affectation à l'une des 5 poubelles officielles.
    """
)