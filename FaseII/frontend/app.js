const form = document.getElementById('predictionForm');
const textInput = document.getElementById('texto');
const count = document.getElementById('charCount');
const button = document.getElementById('submitButton');
const errorBox = document.getElementById('errorBox');
const resultPanel = document.getElementById('resultPanel');

textInput.addEventListener('input', () => {
  count.textContent = `${textInput.value.length} / 5000`;
});

async function checkHealth() {
  const badge = document.getElementById('healthBadge');
  try {
    const response = await fetch('/health');
    const data = await response.json();
    badge.textContent = data.model_loaded ? 'API y modelo disponibles' : 'API disponible; modelo no cargado';
  } catch {
    badge.textContent = 'No se pudo verificar la API';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  resultPanel.hidden = true;
  button.disabled = true;
  button.textContent = 'Procesando…';

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto: textInput.value })
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map(item => item.msg).join('; ')
        : (data.detail || 'Error al consultar la API.');
      throw new Error(detail);
    }

    document.getElementById('predictedClass').textContent = data.clase_predicha;
    document.getElementById('operationalDecision').textContent = data.decision_operativa;
    document.getElementById('individualScore').textContent = data.puntaje_individual == null ? 'No disponible' : Number(data.puntaje_individual).toFixed(4);
    document.getElementById('threshold').textContent = Number(data.umbral_individual).toFixed(6);
    document.getElementById('humanReview').textContent = data.requiere_revision_humana ? 'Sí' : 'No';
    document.getElementById('warningText').textContent = data.advertencia;
    resultPanel.hidden = false;
  } catch (error) {
    errorBox.textContent = error.message || 'No fue posible comunicarse con la API.';
    errorBox.hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = 'Evaluar consulta';
  }
});

checkHealth();
