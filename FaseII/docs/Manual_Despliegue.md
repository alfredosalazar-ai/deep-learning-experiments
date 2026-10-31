# Manual de despliegue en la nube — Fase II CIMA

## Requisitos

- Repositorio GitHub público o autorizado para Render.
- GitHub Actions habilitado.
- Cuenta en Render y disponibilidad del plan que se vaya a utilizar.
- Carpeta `FaseII/` publicada en la rama de despliegue.

No se necesita Docker instalado localmente: GitHub Actions construye y prueba la imagen en infraestructura alojada por GitHub.

## A. Publicar los archivos

1. Crear `FaseII/` en la raíz de `deep-learning-experiments`.
2. Subir todos los archivos y subcarpetas del proyecto.
3. Subir `.github/workflows/fase2-docker.yml` al directorio `.github/workflows/` de la raíz.
4. Realizar commit.

## B. Ejecutar la validación remota

1. Abrir la pestaña **Actions** del repositorio.
2. Seleccionar el workflow **Fase II - prueba y construcción Docker**.
3. Esperar a que finalicen los trabajos `pytest`, construcción Docker y prueba HTTP.
4. Si falla, abrir el paso en rojo, guardar el mensaje íntegro y corregir antes de desplegar.

## C. Crear el servicio Render

1. Entrar al dashboard de Render y seleccionar **New → Web Service**.
2. Conectar el repositorio `deep-learning-experiments`.
3. Elegir runtime **Docker**.
4. Configurar `FaseII` como directorio del servicio, o indicar el Dockerfile y contexto `FaseII` según los campos de la interfaz.
5. Configurar `/health` como ruta de comprobación de salud cuando esté disponible.
6. Revisar región, plan, límites y posibles costos antes de crear el servicio.
7. Crear el servicio y observar el log de build y el de arranque.

## D. Validar servicio publicado

Reemplazar `<servicio>` por el dominio asignado por Render:

- `https://<servicio>.onrender.com/`
- `https://<servicio>.onrender.com/health`
- `https://<servicio>.onrender.com/docs`

Desde `/docs`, ejecutar `POST /predict` con una consulta sintética. Guardar capturas del resultado de salud, la documentación OpenAPI, la inferencia y el despliegue. Solo después de observar una respuesta real puede registrarse el despliegue como exitoso.

## E. Mantenimiento y limitaciones

Los cambios publicados en el repositorio pueden activar un nuevo despliegue según la configuración. No incluir secretos en código ni en el repositorio. El prototipo no implementa autenticación ni es apto para uso productivo financiero. Todas las decisiones de elegibilidad siguen sujetas a reglas deterministas y revisión humana.
