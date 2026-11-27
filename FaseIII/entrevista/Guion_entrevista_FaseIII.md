# CHATBOT CIMA — Guion para presentación profesional (Fase III)

**Autor:** Alfredo Salazar · **Duración sugerida:** 7–9 minutos · **Formato:** video MP4 o enlace accesible para evaluación.

> Esta es una guía para grabar una entrevista real. No sustituye el video requerido y no implica que la entrevista ya se realizó.

## Apertura — 60 segundos

**Entrevistador:** Preséntanos un proyecto de IA que hayas desarrollado.

**Respuesta propuesta:** CIMA significa Consultor Inteligente de Movimientos a Adjudicados. Es un prototipo académico que clasifica consultas operativas de pago y las divide en individuales, paquetes, ambiguas y fuera de alcance. El problema que atiende es la necesidad de organizar la atención de manera consistente y trazable. Su principio central es conservar las validaciones deterministas y la revisión humana: CIMA no confirma ni autoriza pagos.

## Arquitectura y tecnología — 90 segundos

**Pregunta:** ¿Por qué seleccionaste TF-IDF con regresión logística en vez de un modelo transformer?

**Respuesta:** En Actividad 4 comparamos tres modelos de clasificación zero-shot; ninguno resultó seguro para decidir por sí solo. Después, en Actividad 5, entrenamos clasificadores supervisados sobre textos sintéticos. La regresión logística permite una inferencia ligera en CPU y fácil auditoría, aunque sus métricas exploratorias son insuficientes para garantizar precisión real. En Fase II la publicamos como FastAPI dentro de Docker, con GitHub Actions y Render.

**Pregunta:** ¿Qué valida la API?

**Respuesta:** El endpoint /health confirma disponibilidad y carga del modelo; /predict recibe texto sintético y devuelve clase, puntaje, umbral y decisión de enrutamiento. La respuesta es informativa. Una consulta puede clasificarse como INDIVIDUAL y aun así enviarse a revisión humana si su puntaje no supera el umbral.

## Evidencias y experimentación — 90 segundos

**Pregunta:** ¿Qué resultados son verificables?

**Respuesta:** En Actividad 6 la regresión logística alcanzó accuracy de 100 % en solo 26 consultas de prueba. Es un resultado del experimento, no una garantía de generalización: la muestra es pequeña y contiene únicamente dos ejemplos ambiguos. En Actividad 8 demostramos tres incidentes simulados y cinco runs de MLflow offline; no los confundimos con monitoreo permanente de Render.

**Pregunta:** ¿Cómo evitarías errores de clasificación peligrosos?

**Respuesta:** Aplicando umbral conservador, revisión humana, controles deterministas, evaluación independiente y monitoreo de falsas elegibilidades. Además, probaría textos fuera de alcance y cadenas sin sentido antes de autorizar una automatización más amplia.

## MLOps, GitOps y despliegue — 90 segundos

**Pregunta:** ¿Cómo sabes qué versión se desplegó?

**Respuesta:** El pipeline de Fase III relaciona el commit con el inventario y las huellas SHA-256 de datos, código y artefactos. Las pruebas y el manifiesto quedan como evidencia. La solicitud de redeploy se mantiene separada de la integración continua y requiere aprobación. En esta entrega, la nueva CI se prueba localmente; la corrida en GitHub debe capturarse después de publicarla, y solo entonces se declarará validación remota.

**Pregunta:** ¿Por qué no reentrenas y despliegas automáticamente al detectar drift?

**Respuesta:** Porque el drift no implica necesariamente pérdida de precisión. Un reentrenamiento requiere datos etiquetados, evaluación independiente, revisión de sesgos y autorización. La capacidad de automatizar no justifica omitir esas aprobaciones.

## Valor, gobernanza y cierre — 90 segundos

**Pregunta:** ¿Cuál es el retorno de negocio?

**Respuesta:** El valor potencial es reducir clasificaciones manuales repetitivas y homogeneizar el tratamiento de las consultas. No existe un ROI medido en producción porque CIMA no opera sobre datos reales. El siguiente paso sería un piloto autorizado con tiempos de atención, precisión por clase, falsas elegibilidades y costos por consulta.

**Pregunta:** ¿Qué harías para que fuera industrial?

**Respuesta:** Incorporaría autenticación, RBAC, origen de datos gobernado, cifrado, observabilidad continua, pruebas de carga, evaluación de fairness con información legalmente autorizada y gestión formal de versiones. La Fase III documenta una ruta, pero no representa un sistema bancario listo para producción.

**Cierre:** Mi criterio para escalar CIMA es medir utilidad real y riesgos antes de aumentar automatización. La entrega demuestra aprendizaje acumulativo: investigación, entrenamiento, validación, despliegue, observabilidad y gobierno.

## Evidencia mínima del video

- Mostrar portada y URL del repositorio público; no exhibir credenciales.
- Navegar entre `FaseIII/README.md`, workflow, resultado verde y manifiesto SHA-256 cuando exista.
- Mostrar dos diapositivas de resultados y explicar por qué los números son exploratorios/simulados.
- Responder al menos cuatro preguntas técnicas y de gestión frente a cámara o con voz.
- Exportar MP4 o enlazar un video con acceso habilitado; colocar el enlace real en `entrevista/enlace_video.txt`.
