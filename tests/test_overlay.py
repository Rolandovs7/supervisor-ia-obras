"""Overlay generation: blend photos with an obra's floor plan without network."""

from pathlib import Path
from types import SimpleNamespace

import numpy as np

from app.services import analysis

ORIGINAL_URL = "https://res.cloudinary.com/demo/image/upload/supervisor-ia/foto.png"
OVERLAY_URL = "https://res.cloudinary.com/demo/image/upload/supervisor-ia/overlay.jpg"
PLANO_URL = "https://res.cloudinary.com/demo/image/upload/supervisor-ia/plano.png"


class _FakeCv2:
    """Records blend arguments; ``imread`` returns queued frames in order."""

    def __init__(self, frames):
        self.frames = list(frames)
        self.sizes = []
        self.weights = []
        self.written = []
        self.read_paths = []

    def imread(self, path):
        self.read_paths.append(path)
        return self.frames.pop(0) if self.frames else None

    def resize(self, image, size):
        self.sizes.append(size)
        return np.zeros((size[1], size[0], 3), dtype=np.uint8)

    def addWeighted(self, plano, alpha, foto, beta, gamma):
        self.weights.append((alpha, beta, gamma))
        return plano

    def imwrite(self, path, image):
        self.written.append(path)
        return True


def _mock_overlay(monkeypatch, cv2_fake, plano_url=PLANO_URL, upload_url=OVERLAY_URL):
    monkeypatch.setattr(analysis, "get_obra", lambda obra_id: {"plano_url": plano_url})
    monkeypatch.setattr(analysis, "cv2", cv2_fake)
    descargas = []

    def fake_retrieve(url, destination):
        descargas.append((url, destination))
        Path(destination).write_bytes(b"plano")

    monkeypatch.setattr(analysis.urllib.request, "urlretrieve", fake_retrieve)
    monkeypatch.setattr(analysis, "upload_to_cloudinary", lambda path: upload_url)
    return descargas


def _foto():
    return np.zeros((60, 30, 3), dtype=np.uint8)


def _plano():
    return np.zeros((10, 20, 3), dtype=np.uint8)


def test_generar_overlay_sin_plano_devuelve_url_original(monkeypatch, tmp_path):
    cv2_fake = _FakeCv2([])
    _mock_overlay(monkeypatch, cv2_fake, plano_url=None)
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"foto")

    assert analysis.generar_overlay(imagen, "obras-1", ORIGINAL_URL) == ORIGINAL_URL
    assert cv2_fake.read_paths == []


def test_generar_overlay_fusiona_al_50_50(monkeypatch, tmp_path):
    cv2_fake = _FakeCv2([_foto(), _plano()])
    descargas = _mock_overlay(monkeypatch, cv2_fake)
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"foto")

    resultado = analysis.generar_overlay(imagen, "obras-1", ORIGINAL_URL)

    assert resultado == OVERLAY_URL
    assert descargas[0][0] == PLANO_URL
    # La foto se redimensiona al tamaño del plano (ancho, alto).
    assert cv2_fake.sizes == [(20, 10)]
    assert cv2_fake.weights == [(0.5, 0.5, 0)]
    assert len(cv2_fake.written) == 1
    assert cv2_fake.written[0].endswith("overlay.jpg")


def test_generar_overlay_imagen_ilegible_devuelve_original(monkeypatch, tmp_path):
    cv2_fake = _FakeCv2([None])
    _mock_overlay(monkeypatch, cv2_fake)
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"foto")

    assert analysis.generar_overlay(imagen, "obras-1", ORIGINAL_URL) == ORIGINAL_URL


def test_generar_overlay_plano_ilegible_devuelve_original(monkeypatch, tmp_path):
    cv2_fake = _FakeCv2([_foto(), None])
    _mock_overlay(monkeypatch, cv2_fake)
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"foto")

    assert analysis.generar_overlay(imagen, "obras-1", ORIGINAL_URL) == ORIGINAL_URL


def test_generar_overlay_no_rompe_si_falla_la_descarga(monkeypatch, tmp_path):
    def falla(url, destination):
        raise OSError("sin red")

    monkeypatch.setattr(analysis, "get_obra", lambda obra_id: {"plano_url": PLANO_URL})
    monkeypatch.setattr(analysis, "cv2", _FakeCv2([_foto()]))
    monkeypatch.setattr(analysis.urllib.request, "urlretrieve", falla)
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"foto")

    assert analysis.generar_overlay(imagen, "obras-1", ORIGINAL_URL) == ORIGINAL_URL


def test_generar_overlay_obra_inexistente(monkeypatch, tmp_path):
    monkeypatch.setattr(analysis, "get_obra", lambda obra_id: None)
    imagen = tmp_path / "foto.png"
    imagen.write_bytes(b"foto")

    assert analysis.generar_overlay(imagen, "obras-1", ORIGINAL_URL) == ORIGINAL_URL
