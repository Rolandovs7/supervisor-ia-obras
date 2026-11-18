# Supervisor IA — Supervisor Inteligente de Obras con IA

Plataforma full-stack para la supervisión de seguridad en obras de construcción. Combina visión por computadora, alertas en tiempo real y evidencia offline-first para que un supervisor pueda detectar personas y verificar el uso de equipo de protección personal (EPI), registrar obras, resolver alertas y descargar reportes PDF.

## Componentes

| Directorio | Tecnología | Función |
| --- | --- | --- |
| Raíz | FastAPI + SQLAlchemy-free (Supabase) | API REST, autenticación JWT, WebSockets, procesamiento de imágenes y reportes PDF |
| `frontend/` | React 19 + Vite + TypeScript + TailwindCSS | Panel web SaaS de administración |
| `movil/` | Flutter 3 + Dart | App móvil offline-first para capturar evidencia y sincronizarla |

**Flujo principal:** el usuario sube una imagen (desde el panel web o la app móvil) → se guarda en Cloudinary → YOLOv8 detecta personas → un modelo de EPI detecta casco y chaleco → se persisten el análisis y las alertas en Supabase → se emiten alertas por WebSocket → el supervisor las consulta, resuelve y exporta en PDF.

## Requisitos previos

- Python 3.12 con `venv` y `pip`.
- Node.js 20+ y `npm`.
- Flutter 3.47 / Dart 3.13 y Android SDK (solo para la app móvil).
- Un proyecto de Supabase con Auth habilitado y acceso a la base de datos; `psql` disponible para aplicar el esquema.
- Credenciales de Cloudinary para almacenar imágenes de forma permanente.
- Conexión a internet para descargar dependencias y los pesos de los modelos.

## Configuración

Crea un archivo `.env` en la raíz con tus propias credenciales (este archivo está ignorado por Git). Las variables utilizadas son:

- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `SUPABASE_DB_URL` (usado por `init_db.py` para crear las tablas)
- `CLOUDINARY_URL` o `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- `FRONTEND_ORIGINS` (opcional; orígenes de producción separados por comas)

Para el frontend, copia `frontend/.env.example` a `frontend/.env` y ajusta `VITE_API_URL` si el backend no está en `http://localhost:8000`.

> No versiones archivos `.env` reales ni credenciales. Solo se versionan los ejemplos (`*.env.example`).

### Modelos de IA

`yolov8n.pt` (personas) se descarga automáticamente en la primera inferencia. El modelo de EPI debe descargarse una vez:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
from huggingface_hub import hf_hub_download

origen = hf_hub_download(
    repo_id="wntrsldr/yolov8n-ppe-detection-6classes",
    filename="best.pt",
)
Path(origen).replace("ppe_model.pt")
PY
```

Ambos archivos `.pt` quedan en la raíz y están ignorados por Git.

## Backend

```bash
python3.12 -m venv .venv
./.venv/bin/pip install --no-cache-dir -r requirements.txt \
  --extra-index-url https://download.pytorch.org/whl/cpu
./.venv/bin/pip install --force-reinstall --no-deps opencv-python-headless==5.0.0.93

./.venv/bin/python init_db.py     # aplica el esquema en Supabase
./.venv/bin/python main.py        # uvicorn con reload en http://localhost:8000
```

El segundo `pip install` garantiza que `opencv-python-headless` sea el que proporcione `cv2` (evita errores de GUI en servidores).

## Frontend web

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

El panel usa el JWT devuelto por `/login`, guardado en `localStorage`, y se conecta a `ws://localhost:8000/ws/alertas` para el feed en vivo.

## App móvil

```bash
cd movil
flutter pub get
flutter run                 # requiere emulador/dispositivo Android
flutter build apk --debug   # genera build/app/outputs/apk/debug/app-debug.apk
```

`lib/config.dart` define `apiUrl = 'http://10.0.2.2:8000'`, la dirección con la que el emulador de Android alcanza el backend del equipo host. En un dispositivo físico o en producción, cámbiala por la IP/dominio correspondiente. La app guarda las fotos en SQLite y las sube cuando hay conexión y hay sesión activa.

## Verificación

```bash
# Backend
pytest -q
./.venv/bin/pip check

# Web
cd frontend && npm run build

# Móvil
cd movil && flutter analyze
```

## Notas

- Todas las rutas excepto `/`, `/register` y `/login` requieren un token Bearer válido de Supabase Auth.
- El resultado de cada análisis también se mantiene en memoria en `analysis_results` (se pierde al reiniciar el backend).
- Las imágenes se suben a Cloudinary en segundo plano; el archivo temporal se elimina al finalizar el análisis.
