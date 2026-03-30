# DocGen

DocGen is a constrained LLM-based contract drafting system. The project is aimed at generating standardized contract documents from a free-form user prompt, while keeping the process template-driven and controlled rather than allowing unrestricted text generation.

The repository combines:
- a FastAPI backend for orchestration and document generation,
- a React + Vite frontend for user interaction,
- a PostgreSQL service for persistence,
- a local `llama.cpp`-based model runtime for prompt processing,
- a DOCX transformation pipeline that produces the final contract file.

## Project Goal

The main idea behind the project is to automate drafting of typical contracts based on existing examples and templates. The intended MVP follows several important constraints:

- the system focuses on a limited set of contract types,
- contracts are generated from templates rather than from scratch,
- the LLM is used as an assistive parsing and rewriting component,
- the output should stay structured, validated, and suitable for human review,
- the final artifact is a DOCX document that can later be converted or extended.

This direction is reflected both in the codebase and in the design notes inside `description_docs/`.

## How It Works

At a high level, the generation flow is:

1. A user enters a free-form prompt in the frontend.
2. The frontend sends the prompt to the backend endpoint.
3. The backend passes the prompt to the extractor prompt and local LLM.
4. The extracted structured fields are validated and normalized.
5. A replacer prompt is assembled from the extracted values.
6. The backend opens the source DOCX template from `docs/raw.docx`.
7. The text chunks of the document are transformed with the LLM-assisted replacer pipeline.
8. The processed file is saved to `docs/processed.docx`.
9. The backend returns the generated DOCX file to the frontend for download.

## Current Architecture

The architecture described in `description_docs/project_architecture.md` and `description_docs/project_arch_dan.md` positions the system as a controlled drafting platform where AI is an assistive layer, not the source of truth.

In the current repository, the main runtime components are:

- `frontend/`: React application with a prompt input and download flow
- `api/`: FastAPI application, routing, settings, and endpoint wiring
- `pipelines/`: end-to-end contract generation pipeline
- `services/`: LLM wrapper, extraction validation, and DOCX transformation logic
- `schemas/`: request and extraction schemas
- `db/`: SQLAlchemy session and database-related modules
- `docs/`: source and generated DOCX files
- `models/`: local GGUF model files used by `llama_cpp`
- `description_docs/`: planning notes, architecture drafts, and product reasoning

## Backend Responsibilities

The backend currently handles:

- receiving generation requests,
- running the extractor prompt against the local LLM,
- validating structured contract data,
- preparing the replacer prompt,
- rewriting the source DOCX document,
- saving the generated contract,
- returning the final `.docx` file to the client.

The main API route is:

- `POST /contracts/generate`

This endpoint accepts a JSON payload with a single `prompt` field and returns the generated DOCX file.

## Frontend Responsibilities

The frontend provides a minimal interface for:

- entering a contract-generation prompt,
- sending the request to the backend,
- receiving the processed file,
- downloading the generated document.

During local development, the Vite dev server proxies `/contracts/*` requests to the FastAPI backend on port `8000`.

## Tech Stack

- Backend: Python, FastAPI, Pydantic, SQLAlchemy
- Model runtime: `llama_cpp` with a local GGUF model
- Document processing: `python-docx`
- Database: PostgreSQL
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Containerization: Docker, Docker Compose

## Repository Structure

```text
.
├── api/                 FastAPI app, config, routing, endpoints
├── db/                  database session and models
├── description_docs/    architecture notes and planning materials
├── docs/                input and output DOCX files
├── frontend/            React + Vite frontend
├── models/              local GGUF model files
├── pipelines/           contract generation pipeline
├── schemas/             request and extraction schemas
├── services/            LLM, extraction, and document processing services
├── utils/               logging, exceptions, helpers
├── docker-compose.yml   local orchestration
└── Dockerfile           backend container image
```

## Launch Guide

### Prerequisites

Before starting, make sure you have:

- Docker and Docker Compose installed,
- Node.js and npm installed for the frontend,
- the required local model file available in `models/`,
- the source document available in `docs/raw.docx`.

### 1. Build the backend containers

From the project root:

```bash
docker-compose build
```

### 2. Start backend and database services

From the project root:

```bash
docker-compose up
```

This starts:

- the FastAPI backend on `http://localhost:8000`
- the PostgreSQL container used by the application

### 3. Start the frontend

Open another terminal, move into the frontend directory, and run:

```bash
cd frontend
npm run dev
```

The Vite development server will start and expose the frontend locally. In dev mode, requests to `/contracts/generate` are proxied to the backend running on port `8000`.

## Typical Local Workflow

1. Run `docker-compose build`
2. Run `docker-compose up`
3. In a second terminal:

```bash
cd frontend
npm run dev
```

4. Open the frontend in the browser using the local Vite URL shown in the terminal.
5. Enter a prompt describing the contract details.
6. Submit the request and download the generated DOCX file.

## Important Project Notes

- The system is designed as a constrained generator, not a free-form legal text writer.
- The intended workflow assumes template-based generation and structured validation.
- Human review remains important even when the model output looks correct.
- Several files in `description_docs/` describe future directions such as multi-tenant architecture, stronger rule engines, richer validation, and broader jurisdiction support.

## Current Status

The repository already contains the core pieces of the MVP:

- a working backend service,
- a frontend prompt UI,
- a document generation pipeline, needs to be modified
- local model integration,
- DOCX output delivery through the API.

At the same time, some of the broader ideas from the architecture notes, such as richer template management, enterprise security controls, advanced rule engines, and multi-tenant workflows, remain future-facing design directions rather than fully implemented features.
