# ================== СТАДИЯ 1: СБОРКА ==================
FROM python:3.11-slim AS builder

WORKDIR /app

# 1. Ставим инструменты для сборки (они НЕ попадут в финальный образ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Копируем список зависимостей
COPY requirements.txt .

# 3. Устанавливаем Python-пакеты в ИЗОЛИРОВАННУЮ папку /install
#    Все временные файлы и кеш останутся здесь
RUN pip install --no-cache-dir --target=/install \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# 4. Качаем модель spaCy (тоже в /install)
RUN PYTHONPATH=/install python -m spacy download ru_core_news_sm --target /install

# ================== СТАДИЯ 2: ФИНАЛ ==================
FROM python:3.11-slim

WORKDIR /app

# Убеждаемся, что pip и python видят пакеты из /install
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
ENV PATH=/usr/local/lib/python3.11/site-packages/bin:$PATH

# 1. Копируем готовые пакеты из стадии сборки
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# 2. Копируем вашу модель e5-large (она и так готова)
COPY models/e5-large-lite /app/models/e5-large

# 3. Копируем код проекта
COPY src/ ./src/
COPY ui/ ./ui/
COPY data/ ./data/
COPY .env.example ./

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.address=0.0.0.0"]