FROM python:3.11-slim-bookworm AS base

# Environment variables
ENV ENV=prod \
    PORT=8080 \
    HOST=0.0.0.0 \
    WHISPER_MODEL="base" \
    WHISPER_MODEL_DIR="/app/backend/data/cache/whisper/models" \
    RAG_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
    RAG_RERANKING_MODEL="" \
    SENTENCE_TRANSFORMERS_HOME="/app/backend/data/cache/embedding/models" \
    TIKTOKEN_ENCODING_NAME="cl100k_base" \
    TIKTOKEN_CACHE_DIR="/app/backend/data/cache/tiktoken" \
    HF_HOME="/app/backend/data/cache/embedding/models" \
    OLLAMA_BASE_URL="/ollama" \
    OPENAI_API_BASE_URL="" \
    OPENAI_API_KEY="" \
    WEBUI_SECRET_KEY="" \
    SCARF_NO_ANALYTICS=true \
    DO_NOT_TRACK=true \
    ANONYMIZED_TELEMETRY=false

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    pandoc \
    gcc \
    netcat-openbsd \
    curl \
    jq \
    python3-dev \
    # For RAG OCR
    ffmpeg \
    libsm6 \
    libxext6 && \
    # cleanup
    rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /app/backend/data
RUN mkdir -p /root/.cache/chroma
RUN echo -n 00000000-0000-0000-0000-000000000000 > /root/.cache/chroma/telemetry_user_id

# Copy requirements first (for better caching)
COPY ./backend/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir uv && \
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir && \
    uv pip install --system -r requirements.txt --no-cache-dir && \
    python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')" && \
    python -c "import os; from faster_whisper import WhisperModel; WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])" && \
    python -c "import os; import tiktoken; tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])"

# Copy backend files
COPY ./backend .

EXPOSE 8080

HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health | jq -ne 'input.status == true' || exit 1

CMD [ "bash", "start.sh"] 