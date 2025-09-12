# Conta (AR) — MVP v0.1

Monorepo con:
- Backend: FastAPI
- Worker: RQ/Redis
- Desktop: Tauri + React

## Desarrollo
1) `docker compose -f infra/docker-compose.dev.yml up -d`
2) Backend:
```
cd services/api
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
uvicorn app.main:app --reload
```
3) Desktop:
```
cd apps/desktop
npm i
npm run tauri dev
```

## Build
```
cd apps/desktop
npm run build
tauri build
```

## Salud
- API: `GET http://127.0.0.1:8000/health`
## Dependencias OCR (instalación)
- Necesitás **Tesseract** instalado en el sistema:
  - macOS (brew): `brew install tesseract`
  - Windows: instalar binarios de Tesseract y agregar a PATH.
- Python: `pip install -e services/api` (usa pyproject con `pytesseract`, `opencv-python`, `Pillow`, `numpy`).

## Exportadores
- Genera `libro_iva_*.xlsx` y `eeff_*.xlsx` en `services/api/exports/` al invocar los endpoints:
  - `POST /eeff/libro-iva`
  - `POST /eeff/export`
