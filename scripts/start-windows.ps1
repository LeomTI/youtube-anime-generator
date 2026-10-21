$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env. Add GROQ_API_KEY before generating episodes." -ForegroundColor Yellow
}
docker info | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop is not running. Start it and retry." }
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw "Docker Compose failed. Check the error above." }
Write-Host "Dashboard: http://localhost:8501"
Write-Host "API docs:  http://localhost:8000/docs"
Write-Host "Logs:      docker compose logs -f"
