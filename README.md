# YouTube Long2Short Studio

Webapp complète (FastAPI + frontend vanilla) pour:
- détecter des vidéos YouTube longues et potentiellement tendances,
- générer un short vertical (9:16),
- ajouter une narration automatique (optionnel),
- télécharger la vidéo short et le résumé texte.

## Lancer

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Ouvre `http://127.0.0.1:8000`.

## Dépendances système

- `ffmpeg` (pour créer le short)
- accès internet (YouTube + TTS)

## API

- `POST /api/analyze`
- `POST /api/create-short`
- `GET /downloads/{filename}`

## Limites

- Le scoring "tendance" est heuristique (vues, fraîcheur, durée), sans API YouTube officielle.
- La narration utilise gTTS en français.
