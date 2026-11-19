"""Local USB camera capture wired into the standard analysis pipeline."""

import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

import cv2
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.schemas import CamaraCaptureResponse
from app.services.analysis import analyze_image
from app.services.database import save_imagen

router = APIRouter(tags=["camaras"])

_CAMARA_NO_DISPONIBLE = (
    "Cámara local no disponible. Conecta una cámara USB e inténtalo de nuevo."
)


def _capture_frame() -> bytes:
    """Read and JPEG-encode one frame from the local USB camera (index 0)."""
    capture: Any = None
    try:
        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=_CAMARA_NO_DISPONIBLE,
            )

        ok, frame = capture.read()
        if not ok or frame is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo capturar una imagen desde la cámara local.",
            )

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo codificar la imagen capturada.",
            )
        return encoded.tobytes()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"No se pudo acceder a la cámara local: {exc}",
        ) from exc
    finally:
        if capture is not None:
            capture.release()


@router.get("/camaras/capturar", response_model=CamaraCaptureResponse)
async def capturar_desde_camara(
    obra_id: str | None = None,
    user: Any = Depends(get_current_user),
) -> CamaraCaptureResponse:
    """Capture a frame, register it and run the same pipeline as ``/upload``."""
    frame = await asyncio.to_thread(_capture_frame)
    filename = f"camara_{uuid.uuid4().hex}.jpg"

    fd, name = tempfile.mkstemp(prefix="camara-", suffix=".jpg", dir="/tmp")
    image_path = Path(name)
    try:
        with os.fdopen(fd, "wb") as destination:
            destination.write(frame)
        imagen = save_imagen(filename, str(image_path), obra_id)
    except Exception:
        image_path.unlink(missing_ok=True)
        raise

    # ``analyze_image`` uploads to Cloudinary, persists the analysis/alerts and
    # removes the temp file. Run it off the event loop like any other pipeline.
    payload = await asyncio.to_thread(
        analyze_image, image_path, filename, imagen["id"], obra_id
    )
    return CamaraCaptureResponse(filename=filename, secure_url=payload["secure_url"])
