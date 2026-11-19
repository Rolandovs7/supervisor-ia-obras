"""Local camera endpoint tests; no real webcam is ever opened."""

from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.api import camaras
from app.api.websockets import manager
from main import app
from tests.test_api import SECURE_URL, _mock_pipeline

client = TestClient(app)


class _FakeCamera:
    def __init__(self, index, *, abierto=True, con_frame=True):
        assert index == 0
        self.abierto = abierto
        self.con_frame = con_frame
        self.liberada = False

    def isOpened(self):
        return self.abierto

    def read(self):
        if not self.con_frame:
            return False, None
        return True, np.zeros((32, 32, 3), dtype=np.uint8)

    def release(self):
        self.liberada = True


@pytest.fixture(autouse=True)
def clean_connections():
    manager.active_connections.clear()
    yield
    manager.active_connections.clear()


def _usar_camara(monkeypatch, camara):
    monkeypatch.setattr(camaras.cv2, "VideoCapture", lambda index: camara)


def test_capturar_desde_camara(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    camara = _FakeCamera(0)
    _usar_camara(monkeypatch, camara)

    response = client.get("/camaras/capturar", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["secure_url"] == SECURE_URL
    assert body["filename"].startswith("camara_")

    imagen = fake_supabase.store["imagenes"][0]
    assert imagen["filename"] == body["filename"]
    assert imagen["secure_url"] == SECURE_URL
    assert not Path(imagen["temp_path"]).exists()
    assert camara.liberada

    resultados = client.get(
        f"/results/{body['filename']}", headers=auth_headers
    )
    assert resultados.status_code == 200
    assert resultados.json()["person_count"] == 1
    assert fake_supabase.store["alertas"][0]["descripcion"] == (
        "Personas detectadas en la imagen"
    )


def test_capturar_desde_camara_con_obra(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    _usar_camara(monkeypatch, _FakeCamera(0))

    response = client.get(
        "/camaras/capturar",
        params={"obra_id": "obras-3"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert fake_supabase.store["imagenes"][0]["obra_id"] == "obras-3"
    assert fake_supabase.store["alertas"][0]["obra_id"] == "obras-3"


def test_camara_desconectada(monkeypatch, fake_supabase, auth_headers):
    camara = _FakeCamera(0, abierto=False)
    _usar_camara(monkeypatch, camara)

    response = client.get("/camaras/capturar", headers=auth_headers)

    assert response.status_code == 503
    assert "Cámara local no disponible" in response.json()["detail"]
    assert camara.liberada
    assert fake_supabase.store["imagenes"] == []


def test_camara_sin_frame(monkeypatch, fake_supabase, auth_headers):
    camara = _FakeCamera(0, con_frame=False)
    _usar_camara(monkeypatch, camara)

    response = client.get("/camaras/capturar", headers=auth_headers)

    assert response.status_code == 503
    assert "No se pudo capturar" in response.json()["detail"]
    assert camara.liberada


def test_capturar_sin_token(monkeypatch, fake_supabase):
    response = client.get("/camaras/capturar")

    assert response.status_code == 401


def test_ws_recibe_alerta_de_camara(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    _usar_camara(monkeypatch, _FakeCamera(0))
    token = auth_headers["Authorization"].split(" ", 1)[1]

    with client.websocket_connect(f"/ws/alertas?token={token}") as websocket:
        response = client.get("/camaras/capturar", headers=auth_headers)
        assert response.status_code == 200
        message = websocket.receive_json()

    assert message["type"] == "alerta"
    assert message["alerta"]["descripcion"] == "Personas detectadas en la imagen"
    assert message["alerta"] == fake_supabase.store["alertas"][0]
