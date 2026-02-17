# YouTube Long2Short Studio

Webapp simple (FastAPI + frontend) pour:
- détecter des vidéos YouTube longues et potentiellement tendances,
- générer un short vertical (9:16),
- ajouter une narration automatique (optionnel),
- télécharger la vidéo short et le résumé texte.

## Important (pour débutant)

Si YouTube/ffmpeg ne fonctionne pas sur ta machine, l'app propose aussi un **mode démo**:
- tu colles un texte long,
- l'app génère un résumé téléchargeable.

Ça te permet de vérifier que l'app marche déjà, même sans pipeline vidéo complet.

## Installation pas à pas

### 1) Créer l'environnement Python

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3) Vérifier les dépendances système

- `ffmpeg` (obligatoire pour créer le short vidéo)
- accès internet (YouTube + TTS)

### 4) Lancer l'application

```bash
uvicorn app.main:app --reload
```

Ouvre `http://127.0.0.1:8000`.

## Utilisation

1. **État système**: regarde les indicateurs FastAPI / yt-dlp / gTTS.
2. **Détection YouTube**: cherche un sujet.
3. **Génération du short réel**: colle une URL YouTube.
4. **Mode démo**: si le réel échoue, génère au moins le résumé téléchargeable.

## API

- `GET /api/health` : statut dépendances
- `POST /api/analyze`
- `POST /api/create-short`
- `POST /api/demo-short`
- `GET /downloads/{filename}`

## Limites

- Le scoring "tendance" est heuristique (vues, fraîcheur, durée), sans API YouTube officielle.
- La narration utilise gTTS en français.
