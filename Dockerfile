FROM python:3.11-slim

# System deps for Manim (Text rendering via Pango + Cairo, video via ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    build-essential \
    fonts-noto \
    fonts-noto-cjk \
    fontconfig \
    texlive-latex-base \
    texlive-fonts-recommended \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
