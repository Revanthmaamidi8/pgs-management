# PG Management System

A full-stack PG (Paying Guest) management platform built with FastAPI, PostgreSQL, React, and TypeScript.

## Phase 1 completed

This repository currently includes the initial foundation for the application:

- FastAPI backend structure
- SQLAlchemy 2 + PostgreSQL configuration
- Alembic migration setup
- JWT authentication with password hashing
- Role-based authorization foundation
- Docker Compose setup for local PostgreSQL and backend development

## Tech stack

Backend:
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- Pydantic
- PostgreSQL
- Alembic
- JWT

Frontend (planned next):
- React + TypeScript
- Vite
- Tailwind CSS

## Local development

1. Copy the environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Start PostgreSQL and backend:
   ```bash
   docker compose up --build
   ```

3. API docs:
   - Swagger UI: http://localhost:8000/docs
   - OpenAPI: http://localhost:8000/openapi.json

## Authentication

Endpoints available in this phase:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

## Notes

This is the foundation phase. Additional PG, room, tenant, rent, and reporting modules will be built in subsequent phases.
