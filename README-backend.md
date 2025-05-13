# Open WebUI Backend API

This is the backend-only version of Open WebUI, providing the API functionality without the frontend.

## Features

- Full API compatibility with the original Open WebUI
- Integration with Ollama for running local AI models
- Built-in RAG (Retrieval Augmented Generation) for document Q&A
- Support for voice input and output
- Document processing capabilities

## Prerequisites

- Docker and Docker Compose
- Ollama (included in Docker setup)

## Quick Start

### Using Docker (Recommended)

**On Linux/macOS:**

```bash
chmod +x run-backend.sh
./run-backend.sh
```

**On Windows:**

```
run-backend.bat
```

The backend API will be available at http://localhost:8080.

### Manual Setup (Without Docker)

1. Install Python 3.11 or later
2. Install the required dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```
3. Run the backend:
   ```
   cd backend
   ./start.sh
   ```
   
   On Windows:
   ```
   cd backend
   start_windows.bat
   ```

## Configuration

The backend can be configured via environment variables:

- `OLLAMA_BASE_URL`: URL for Ollama API (default: `/ollama`)
- `WEBUI_SECRET_KEY`: Secret key for the WebUI
- `PORT`: Port to run the API server (default: 8080)
- `HOST`: Host to run the API server (default: 0.0.0.0)

Check the Dockerfile for other available configuration options.

## API Documentation

API documentation is available at http://localhost:8080/docs when the server is running.

## Using the API

You can interact with the API using any HTTP client, such as curl, Postman, or a custom frontend.

Example: Get available models
```bash
curl http://localhost:8080/api/models
```

## License

See the LICENSE file for details. 