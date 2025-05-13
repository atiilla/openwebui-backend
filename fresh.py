#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import sys

# Docker-compose content
DOCKER_COMPOSE_CONTENT = """version: '3'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama  
    volumes:
      - ollama_data:/root/.ollama
    pull_policy: always
    restart: unless-stopped
    ports:
      - "11434:11434"
    networks:
      - app-network

  backend:
    build:
      context: ./
      dockerfile: Dockerfile
    container_name: open-webui-backend
    volumes:
      - backend_data:/app/backend/data
    depends_on:
      - ollama
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=your_secret_key_here
      - ENV=dev
    networks:
      - app-network
    restart: unless-stopped

volumes:
  ollama_data: {}
  backend_data: {}

networks:
  app-network:
    driver: bridge 
"""

# Dockerfile content
DOCKERFILE_CONTENT = """FROM python:3.11-slim-bookworm AS base

# Environment variables
ENV ENV=prod \\
    PORT=8080 \\
    HOST=0.0.0.0 \\
    WHISPER_MODEL="base" \\
    WHISPER_MODEL_DIR="/app/backend/data/cache/whisper/models" \\
    RAG_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \\
    RAG_RERANKING_MODEL="" \\
    SENTENCE_TRANSFORMERS_HOME="/app/backend/data/cache/embedding/models" \\
    TIKTOKEN_ENCODING_NAME="cl100k_base" \\
    TIKTOKEN_CACHE_DIR="/app/backend/data/cache/tiktoken" \\
    HF_HOME="/app/backend/data/cache/embedding/models" \\
    OLLAMA_BASE_URL="/ollama" \\
    OPENAI_API_BASE_URL="" \\
    OPENAI_API_KEY="" \\
    WEBUI_SECRET_KEY="" \\
    SCARF_NO_ANALYTICS=true \\
    DO_NOT_TRACK=true \\
    ANONYMIZED_TELEMETRY=false

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
    git \\
    build-essential \\
    pandoc \\
    gcc \\
    netcat-openbsd \\
    curl \\
    jq \\
    python3-dev \\
    # For RAG OCR
    ffmpeg \\
    libsm6 \\
    libxext6 && \\
    # cleanup
    rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /app/backend/data
RUN mkdir -p /root/.cache/chroma
RUN echo -n 00000000-0000-0000-0000-000000000000 > /root/.cache/chroma/telemetry_user_id

# Copy requirements first (for better caching)
COPY ./backend/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir uv && \\
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir && \\
    uv pip install --system -r requirements.txt --no-cache-dir && \\
    python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['RAG_EMBEDDING_MODEL'], device='cpu')" && \\
    python -c "import os; from faster_whisper import WhisperModel; WhisperModel(os.environ['WHISPER_MODEL'], device='cpu', compute_type='int8', download_root=os.environ['WHISPER_MODEL_DIR'])" && \\
    python -c "import os; import tiktoken; tiktoken.get_encoding(os.environ['TIKTOKEN_ENCODING_NAME'])"

# Copy backend files
COPY ./backend .

EXPOSE 8080

HEALTHCHECK CMD curl --silent --fail http://localhost:${PORT:-8080}/health | jq -ne 'input.status == true' || exit 1

CMD [ "bash", "start.sh"] 
"""

# Main dockerignore content
DOCKERIGNORE_CONTENT = """.github
.DS_Store
docs
kubernetes
node_modules
/.svelte-kit
/package
.env
.env.*
vite.config.js.timestamp-*
vite.config.ts.timestamp-*
__pycache__
.idea
venv
_old
uploads
.ipynb_checkpoints
**/*.db
_test
backend/data/*
"""

# Backend dockerignore content
BACKEND_DOCKERIGNORE_CONTENT = """__pycache__
.env
_old
uploads
.ipynb_checkpoints
*.db
_test
!/data
/data/*
!/data/litellm
/data/litellm/*
!data/litellm/config.yaml

!data/config.json
"""

def run_command(command):
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, check=True)
    return process

def list_directory_structure(path, prefix="", is_last=True, max_depth=2, current_depth=0):
    """List directory structure recursively up to max_depth."""
    files = sorted(os.listdir(path))
    
    # Filter out some common directories we don't need to show
    if '__pycache__' in files:
        files.remove('__pycache__')
    if '.git' in files:
        files.remove('.git')
    
    result = []
    
    if current_depth > max_depth:
        if files:
            result.append(f"{prefix}{'└── ' if is_last else '├── '}... ({len(files)} more items)")
        return result
    
    for i, file in enumerate(files):
        is_last_file = i == len(files) - 1
        file_path = os.path.join(path, file)
        
        if os.path.isdir(file_path):
            result.append(f"{prefix}{'└── ' if is_last else '├── '}{file}/")
            if current_depth < max_depth:
                ext_prefix = prefix + ('    ' if is_last else '│   ')
                subfolder = list_directory_structure(file_path, ext_prefix, is_last_file, max_depth, current_depth + 1)
                result.extend(subfolder)
        else:
            result.append(f"{prefix}{'└── ' if is_last else '├── '}{file}")
    
    return result

def main():
    # Create the Docker files with embedded content
    print("Creating Docker files...")
    
    # Write docker-compose.yaml
    with open("docker-compose.yaml", "w") as f:
        f.write(DOCKER_COMPOSE_CONTENT)
    print("Created docker-compose.yaml")
    
    # Write Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(DOCKERFILE_CONTENT)
    print("Created Dockerfile")
    
    # Write .dockerignore
    with open(".dockerignore", "w") as f:
        f.write(DOCKERIGNORE_CONTENT)
    print("Created .dockerignore")
    
    # Create backend directory
    os.makedirs("backend", exist_ok=True)
    print("Created backend/ directory")
    
    # Write backend/.dockerignore
    os.makedirs("backend", exist_ok=True)
    with open("backend/.dockerignore", "w") as f:
        f.write(BACKEND_DOCKERIGNORE_CONTENT)
    print("Created backend/.dockerignore")
    
    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository
        repo_url = "https://github.com/open-webui/open-webui.git"
        clone_cmd = f"git clone {repo_url} {temp_dir}"
        
        try:
            run_command(clone_cmd)
        except subprocess.CalledProcessError:
            print("Failed to clone the repository")
            return 1
            
        # Create backend directory structure
        backend_src = os.path.join(temp_dir, "backend")
        if os.path.exists(backend_src):
            # Copy backend contents except for __pycache__ and other unnecessary files
            for item in os.listdir(backend_src):
                item_path = os.path.join(backend_src, item)
                
                # Skip __pycache__ and other unnecessary directories
                if item in ['__pycache__', '.git']:
                    continue
                    
                if os.path.isdir(item_path):
                    # Copy directories
                    dest_path = os.path.join("backend", item)
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(item_path, dest_path)
                    print(f"Copied directory: backend/{item}/")
                else:
                    # Copy files
                    shutil.copy2(item_path, os.path.join("backend", item))
                    print(f"Copied file: backend/{item}")
            
            # Ensure backend/data directory exists
            os.makedirs(os.path.join("backend", "data"), exist_ok=True)
            print("Ensured backend/data/ directory exists")
        else:
            print("Warning: backend directory not found in repository")
            
    print("\nSetup completed successfully!")
    print("The Docker files have been created with embedded content, and the backend directory structure has been set up.")
    print("To build and run the containers, use: docker-compose up -d")
    return 0

if __name__ == "__main__":
    sys.exit(main())

