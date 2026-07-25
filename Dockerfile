# ============================================================
# EcoSort-Search — Image de production
# Build : docker build -t ecosort .
# Run   : docker run -p 8501:8501 ecosort
# ============================================================
FROM python:3.11-slim

# Bonnes pratiques Python en conteneur
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1. Dépendances d'abord (couche mise en cache tant que requirements.txt
#    ne change pas -> rebuilds beaucoup plus rapides)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .streamlit /app/.streamlit

# 2. Code de l'application + modèle entraîné au Jalon 1
COPY app/ ./app/
COPY models/ ./models/

# Streamlit
EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Healthcheck : l'enseignant voit tout de suite si le conteneur est sain
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app/app.py"]
