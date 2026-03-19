FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8510
ENV STREAMLIT_SERVER_HEADLESS=true
ENV CHALLENGE_ADMIN_SECRET=hsb2026

EXPOSE ${PORT}

CMD streamlit run app/challenge_app.py --server.address 0.0.0.0 --server.port ${PORT} --browser.gatherUsageStats false
