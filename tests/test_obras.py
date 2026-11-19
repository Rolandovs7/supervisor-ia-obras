import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.api import obras as obras_routes
from main import app

client = TestClient(app)

PLANO_URL = "https://res.cloudinary.com/demo/image/upload/supervisor-ia/plano.png"


def _png() -> bytes:
    buffer = io.BytesIO()
    Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8)).save(buffer, format="PNG")
    return buffer.getvalue()

OBRA = {
    "nombre": "Torre Norte",
    "ubicacion": "Av. Principal 123",
    "fecha_inicio": "2026-01-10",
    "fecha_fin": "2026-12-20",
}


def test_create_obra(fake_supabase, auth_headers):
    response = client.post("/obras", json=OBRA, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == OBRA["nombre"]
    assert body["fecha_inicio"] == OBRA["fecha_inicio"]

    row = fake_supabase.store["obras"][0]
    assert row["nombre"] == OBRA["nombre"]
    assert row["fecha_fin"] == OBRA["fecha_fin"]


def test_list_and_get_obra(fake_supabase, auth_headers):
    created = client.post("/obras", json=OBRA, headers=auth_headers).json()

    listing = client.get("/obras", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    detail = client.get(f"/obras/{created['id']}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["nombre"] == OBRA["nombre"]


def test_get_obra_not_found(auth_headers):
    response = client.get("/obras/no-existe", headers=auth_headers)
    assert response.status_code == 404


def test_obras_require_token():
    assert client.get("/obras").status_code == 401
    assert client.post("/obras", json=OBRA).status_code == 401


def test_subir_plano(monkeypatch, fake_supabase, auth_headers):
    monkeypatch.setattr(obras_routes, "upload_to_cloudinary", lambda path: PLANO_URL)
    creada = client.post("/obras", json=OBRA, headers=auth_headers).json()

    response = client.post(
        f"/obras/{creada['id']}/plano",
        files={"file": ("plano.png", _png(), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["plano_url"] == PLANO_URL
    assert fake_supabase.store["obras"][0]["plano_url"] == PLANO_URL

    detalle = client.get(f"/obras/{creada['id']}", headers=auth_headers)
    assert detalle.json()["plano_url"] == PLANO_URL


def test_subir_plano_obra_no_existe(monkeypatch, auth_headers):
    monkeypatch.setattr(obras_routes, "upload_to_cloudinary", lambda path: PLANO_URL)
    response = client.post(
        "/obras/no-existe/plano",
        files={"file": ("plano.png", _png(), "image/png")},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_subir_plano_requiere_token():
    response = client.post(
        "/obras/obras-1/plano",
        files={"file": ("plano.png", _png(), "image/png")},
    )
    assert response.status_code == 401
