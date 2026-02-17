const healthEl = document.querySelector('#health');
const analyzeForm = document.querySelector('#analyze-form');
const videosEl = document.querySelector('#videos');
const shortForm = document.querySelector('#short-form');
const demoForm = document.querySelector('#demo-form');
const outputEl = document.querySelector('#output');

async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    const deps = data.dependencies;
    healthEl.innerHTML = `
      FastAPI: ${deps.fastapi ? '✅' : '❌'} ·
      yt-dlp: ${deps.yt_dlp ? '✅' : '❌'} ·
      gTTS: ${deps.gtts ? '✅' : '❌'}<br>
      Pipeline complet: <strong>${deps.ready_for_full_pipeline ? 'OK' : 'NON'}</strong>
    `;
  } catch (error) {
    healthEl.textContent = `Impossible de vérifier l'état: ${error}`;
  }
}

analyzeForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  videosEl.innerHTML = 'Analyse en cours...';

  const payload = {
    topic: document.querySelector('#topic').value,
    min_duration_minutes: Number(document.querySelector('#minDuration').value),
    max_results: Number(document.querySelector('#maxResults').value),
  };

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      videosEl.textContent = data.detail || 'Erreur';
      return;
    }

    videosEl.innerHTML = data.videos
      .map(
        (video) => `
      <article class="card">
        <strong>${video.title}</strong><br>
        <small>${video.channel} · ${video.duration_minutes} min · score ${video.score}</small>
        <p>${video.description || ''}</p>
        <button onclick="document.querySelector('#videoUrl').value='${video.url}'">Utiliser cette vidéo</button>
      </article>
    `,
      )
      .join('');
  } catch (error) {
    videosEl.textContent = `Erreur réseau: ${error}`;
  }
});

shortForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  outputEl.textContent = 'Création du short...';

  const payload = {
    video_url: document.querySelector('#videoUrl').value,
    include_narration: document.querySelector('#narration').checked,
    custom_summary: document.querySelector('#customSummary').value || null,
  };

  try {
    const res = await fetch('/api/create-short', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      outputEl.textContent = data.detail || 'Erreur';
      return;
    }

    outputEl.innerHTML = `
      <h3>${data.title}</h3>
      <p>${data.summary}</p>
      <p><a href="${data.short_download}">Télécharger le short</a></p>
      <p><a href="${data.summary_download}">Télécharger le résumé</a></p>
      ${data.narration_download ? `<p><a href="${data.narration_download}">Télécharger la narration</a></p>` : ''}
    `;
  } catch (error) {
    outputEl.textContent = `Erreur réseau: ${error}`;
  }
});

demoForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  outputEl.textContent = 'Génération du résumé démo...';

  const payload = {
    title: document.querySelector('#demoTitle').value,
    long_description: document.querySelector('#demoDescription').value,
  };

  try {
    const res = await fetch('/api/demo-short', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      outputEl.textContent = data.detail || 'Erreur';
      return;
    }

    outputEl.innerHTML = `
      <h3>${data.title}</h3>
      <p>${data.message}</p>
      <p>${data.summary}</p>
      <p><a href="${data.summary_download}">Télécharger le résumé démo</a></p>
    `;
  } catch (error) {
    outputEl.textContent = `Erreur réseau: ${error}`;
  }
});

checkHealth();
