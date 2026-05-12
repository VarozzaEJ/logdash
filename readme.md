# Logdash

A lightweight, self-hosted log aggregation tool. A Python sidecar container
tails logs from all running Docker containers and streams them in real time
to a React dashboard via Supabase.

## Architecture

- **Daemon**: Python 3.11, reads the Docker socket directly, batches and uploads log entries every 2 seconds with retry logic
- **Storage**: Supabase Postgres with Realtime enabled — no polling required
- **Frontend**: React + TypeScript + Vite, subscribes to live inserts via Supabase Realtime

## Demo

[link to your Vercel deploy]

<img width="1919" height="1075" alt="Image" src="https://github.com/user-attachments/assets/98f4103e-f4f5-48d8-9222-8c187a0ba07a" />

## Running locally

### Prerequisites

- Docker Desktop
- Node 22+
- A free Supabase project

### Supabase setup

1. Create a new Supabase project
2. Run the migration in `supabase/migrations/001_create_logs_table.sql`
3. Run `supabase/migrations/002_enable_realtime.sql`

### Environment variables

Copy both example files and fill in your Supabase credentials:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

### Start everything

```bash
docker compose up --build
```

Open `http://localhost:8080` to see logs streaming live.

### Frontend development

```bash
cd frontend
npm install
npm run dev
```

## What I learned

- Reading the Docker socket directly from Python without a third-party library
- Python asyncio — running a blocking log stream in a thread executor alongside an async upload loop
- Supabase Realtime subscriptions in React
- Docker multi-stage builds and the sidecar container pattern
