# Runbook
```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/health
curl -X POST http://localhost:8000/v1/simulations -H 'x-api-key: change-me' -H 'Content-Type: application/json' --data-binary @examples/journey.json
pytest -q
ruff check .
docker compose logs -f api
docker compose down
```
