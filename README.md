# Anime YouTube Factory v1.0

Dockerized human-supervised production starter for original anime-inspired children's stories.

## Run
1. `cp .env.example .env`; set `GROQ_API_KEY`.
2. `docker compose up --build`
3. Dashboard http://localhost:8501; API docs http://localhost:8000/docs.
4. Create an episode. Review files under `data/jobs/<id>/`, approve, then upload.

## Features
FastAPI, Streamlit dashboard, Groq script/story metadata generation, multilingual Edge TTS, FFmpeg 16:9 episode and 9:16 teaser, SVG story-card visual fallback, optional Runway adapter, YouTube OAuth upload, SQLite persistence, budget estimate guard and tests.

The fallback is animated story cards, not full anime animation. Connect an image-generation service and validate Runway's current API schema to get actual character animation. This project is a runnable foundation; external credentials and account setup are required.

## YouTube OAuth
Enable YouTube Data API v3 in Google Cloud, create OAuth Desktop credentials, save as `secrets/client_secret.json`, then run `python scripts/youtube_auth.py` on a machine with a browser. This writes `secrets/token.json`. Upload defaults to private. Test privately first.

## Runway
Set `ENABLE_RUNWAY=true`, `RUNWAY_API_KEY`, and verify current endpoint/model schema at https://docs.dev.runwayml.com/. Runway model availability, pricing and API schemas change. The standard workflow currently uses the deterministic FFmpeg fallback; the adapter is provided for integration work.

## Budget
Default monthly budget is $80. Groq estimated job cost and Runway second cost are configurable. This is an application-side estimate guard, not a billing guarantee. Check provider dashboards. Keep routine video production on FFmpeg and reserve paid video generation for selected scenes.

## API
- `POST /jobs` body `{"topic":"...","languages":["en","es"],"make_shorts":true}`
- `GET /jobs`, `GET /jobs/{id}`
- `POST /jobs/{id}/approve`
- `POST /jobs/{id}/publish` body `{"privacy_status":"private","asset":"episode"}`; asset can be `short`
- `GET /health`

## Safety
Original characters/stories only; no copyrighted characters, franchises, celebrity voices or music. Correctly declare made-for-kids status. Children's content has restricted features and ad targeting; don't rely on comments or personalized ads. No fake likes/views/comments/subscribers or engagement manipulation. Human approval is required before publication.

## Before public production
Add user authentication, managed PostgreSQL, Redis + durable worker queue, object storage, HTTPS, secrets manager, backups, monitoring, per-user authorization and stronger content moderation. SQLite and in-process background tasks suit a single-instance starter, not horizontal scale.


## Windows 11 + NVIDIA local setup

1. Elevated PowerShell: `wsl --install`, then `wsl --update`; reboot if requested.
2. Install a current NVIDIA Windows driver with WSL support. Verify `nvidia-smi` in PowerShell and WSL.
3. Install Docker Desktop, enable its WSL2 engine, and enable WSL Integration for your Linux distribution.
4. Optional 16 GB tuning: copy `scripts/.wslconfig.example` to `%USERPROFILE%\\.wslconfig`, then run `wsl --shutdown`. It caps WSL at 8 GB, 6 processors and 4 GB swap.
5. In PowerShell in the project folder: `Copy-Item .env.example .env`; add your Groq key.
6. Start: `powershell -ExecutionPolicy Bypass -File .\\scripts\\start-windows.ps1`.
7. Dashboard: http://localhost:8501; API docs: http://localhost:8000/docs.
8. Diagnose GPU: `powershell -ExecutionPolicy Bypass -File .\\scripts\\diagnose-gpu.ps1`.

Compose reserves the GPU for the API/video container. The renderer probes NVENC and selects it when working; it otherwise uses CPU encoding. If GPU passthrough causes startup errors, remove the `deploy.resources.reservations.devices` block from the API service and set `VIDEO_ENCODER=cpu` in `.env`.
