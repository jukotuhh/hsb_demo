FROM python:3.11-slim

WORKDIR /app

# System-Deps für scipy/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements zuerst (Cache-Layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Ports: 8501 = Streamlit, 8888 = Jupyter
EXPOSE 8501 8888

# Standard: Streamlit starten
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--browser.gatherUsageStats", "false"]
