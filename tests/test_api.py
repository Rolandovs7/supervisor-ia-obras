import io
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.services import analysis
from main import app

client = TestClient(app)

SECURE_URL = "https://res.cloudinary.com/demo/image/upload/supervisor-ia/test.png"
OVERLAY_URL = "https://res.cloudinary.com/demo/image/upload/supervisor-ia/overlay.jpg"


PPE_NAMES = {
    0: "Gloves",
    1: "Vest",
    2: "goggles",
    3: "helmet",
    4: "mask",
    5: "safety_shoe",
}
PPE_INDEX = {name.lower(): index for index, name in PPE_NAMES.items()}

MATERIAL_NAMES = {
    7: "truck",
    24: "backpack",
    28: "suitcase",
    44: "bottle",
}
MATERIAL_INDEX = {name: index for index, name in MATERIAL_NAMES.items()}


class _FakeBox:
    def __init__(self, cls, conf=0.97, xyxy=(3.0, 4.0, 20.0, 21.0)):
        self.cls = [cls]
        self.conf = [conf]
        self.xyxy = [list(xyxy)]


class _FakeResult:
    def __init__(self, names, boxes):
        self.names = names
        self.boxes = boxes


class _FakeModel:
    def __init__(self, results):
        self.results = results

    def __call__(self, path, verbose=False):
        return self.results


def _person_result(count=1, material_classes=()):
    boxes = [_FakeBox(0) for _ in range(count)]
    boxes.extend(_FakeBox(MATERIAL_INDEX[name]) for name in material_classes)
    return _FakeResult({0: "person", **MATERIAL_NAMES}, boxes)


def _ppe_result(*classes):
    return _FakeResult(PPE_NAMES, [_FakeBox(PPE_INDEX[name.lower()]) for name in classes])


class _FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class _FakePoseImage:
    def __init__(self, image_format=None, data=None):
        self.image_format = image_format
        self.data = data


class _FakeImageFormat:
    SRGB = "SRGB"


class _FakeMediaPipe:
    Image = _FakePoseImage
    ImageFormat = _FakeImageFormat


class _FakePoseLandmarker:
    def __init__(self, landmarks):
        self.landmarks = landmarks

    def detect(self, image):
        return SimpleNamespace(
            pose_landmarks=[self.landmarks] if self.landmarks else []
        )


def _pose_landmarks(altura=0.6, ancho=0.12, rodillas_junto_al_tronco=False):
    """33 normalized pose points; defaults describe a person standing up."""
    puntos = [_FakeLandmark(0.5, 0.5) for _ in range(33)]
    x_izq, x_der = 0.5 - ancho / 2, 0.5 + ancho / 2
    y_hombros = 0.2
    puntos[11], puntos[12] = _FakeLandmark(x_izq, y_hombros), _FakeLandmark(x_der, y_hombros)
    puntos[23], puntos[24] = _FakeLandmark(x_izq, 0.5), _FakeLandmark(x_der, 0.5)
    y_rodillas = y_hombros if rodillas_junto_al_tronco else y_hombros + altura * 0.6
    puntos[25], puntos[26] = _FakeLandmark(x_izq, y_rodillas), _FakeLandmark(x_der, y_rodillas)
    puntos[27], puntos[28] = (
        _FakeLandmark(x_izq, y_hombros + altura),
        _FakeLandmark(x_der, y_hombros + altura),
    )
    return puntos


def _dummy_png() -> bytes:
    image = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _upload(filename: str, headers: dict, **kwargs):
    return client.post(
        "/upload",
        files={"file": (filename, _dummy_png(), "image/png")},
        headers=headers,
        **kwargs,
    )


def _mock_pipeline(
    monkeypatch,
    person_count=1,
    ppe_classes=("helmet", "Vest"),
    material_classes=(),
    caida=False,
    landmarks=None,
):
    monkeypatch.setattr(
        analysis,
        "_model",
        _FakeModel([_person_result(person_count, material_classes)]),
    )
    monkeypatch.setattr(analysis, "_ppe_model", _FakeModel([_ppe_result(*ppe_classes)]))
    monkeypatch.setattr(analysis, "upload_to_cloudinary", lambda path: SECURE_URL)
    monkeypatch.setattr(
        analysis,
        "generar_overlay",
        lambda path, obra_id, url=None: OVERLAY_URL,
    )
    monkeypatch.setattr(analysis, "_mediapipe_module", _FakeMediaPipe)
    if landmarks is None:
        landmarks = (
            _pose_landmarks(altura=0.08, ancho=0.55)
            if caida
            else _pose_landmarks()
        )
    monkeypatch.setattr(
        analysis, "get_pose_landmarker", lambda: _FakePoseLandmarker(landmarks)
    )


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    response = _upload("upload_test.png", auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "queued"

    imagen = fake_supabase.store["imagenes"][0]
    assert imagen["filename"] == "upload_test.png"
    assert imagen["temp_path"] == response.json()["temp_path"]
    assert imagen["secure_url"] == SECURE_URL
    assert not Path(response.json()["temp_path"]).exists()


def test_results(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    assert _upload("results_test.png", auth_headers).status_code == 200

    response = client.get("/results/results_test.png", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["person_count"] == 1
    assert response.json()["material_count"] == 0
    assert response.json()["caida_detectada"] is False
    assert response.json()["detections"][0]["class"] == "person"
    assert response.json()["secure_url"] == SECURE_URL

    assert len(fake_supabase.store["analisis"]) == 1
    assert fake_supabase.store["analisis"][0]["person_count"] == 1

    alerta = fake_supabase.store["alertas"][0]
    assert alerta["tipo"] == "seguridad"
    assert alerta["descripcion"] == "Personas detectadas en la imagen"
    assert alerta["nivel"] == "baja"
    assert alerta["resuelta"] is False


def test_materiales_detectados(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(
        monkeypatch,
        material_classes=("truck", "bottle", "suitcase"),
    )
    assert _upload("materiales.png", auth_headers).status_code == 200

    response = client.get("/results/materiales.png", headers=auth_headers)
    payload = response.json()
    assert payload["material_count"] == 3
    assert [item["class"] for item in payload["detections"]] == [
        "person",
        "truck",
        "bottle",
        "suitcase",
        "helmet",
        "vest",
    ]
    assert fake_supabase.store["analisis"][0]["material_count"] == 3


def test_upload_with_obra_id_form(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    response = _upload(
        "con_obra.png", auth_headers, data={"obra_id": "obras-1"}
    )
    assert response.status_code == 200
    assert response.json()["obra_id"] == "obras-1"
    assert fake_supabase.store["imagenes"][0]["obra_id"] == "obras-1"
    assert fake_supabase.store["alertas"][0]["obra_id"] == "obras-1"


def test_upload_with_obra_id_query(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    response = _upload("por_query.png", auth_headers, params={"obra_id": "obras-9"})
    assert response.status_code == 200
    assert fake_supabase.store["imagenes"][0]["obra_id"] == "obras-9"


def test_overlay_url_guardada_en_resultados_y_analisis(
    monkeypatch, fake_supabase, auth_headers
):
    _mock_pipeline(monkeypatch)
    assert _upload(
        "con_overlay.png", auth_headers, data={"obra_id": "obras-1"}
    ).status_code == 200

    payload = client.get("/results/con_overlay.png", headers=auth_headers).json()
    assert payload["overlay_url"] == OVERLAY_URL
    assert fake_supabase.store["analisis"][0]["overlay_url"] == OVERLAY_URL


def test_sin_overlay_sin_obra_id(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    assert _upload("sin_overlay.png", auth_headers).status_code == 200

    payload = client.get("/results/sin_overlay.png", headers=auth_headers).json()
    assert payload["overlay_url"] is None
    assert fake_supabase.store["analisis"][0]["overlay_url"] is None


def test_results_not_found(auth_headers):
    response = client.get("/results/does-not-exist.png", headers=auth_headers)
    assert response.status_code == 404


def test_ppe_detecciones_guardadas_en_resultados(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    assert _upload("ppe_detecciones.png", auth_headers).status_code == 200

    response = client.get("/results/ppe_detecciones.png", headers=auth_headers)
    payload = response.json()
    assert [item["class"] for item in payload["detections"]] == [
        "person",
        "helmet",
        "vest",
    ]
    assert payload["ppe_model"] == "ppe_model.pt"


def test_alerta_alta_sin_casco_y_chaleco(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch, ppe_classes=())
    assert _upload(
        "ppe_sin_casco.png", auth_headers, data={"obra_id": "obras-7"}
    ).status_code == 200

    alertas = fake_supabase.store["alertas"]
    assert len(alertas) == 2
    alta = alertas[1]
    assert alta["nivel"] == "alta"
    assert alta["descripcion"] == "Posible falta de casco detectada y falta de chaleco"
    assert alta["obra_id"] == "obras-7"


def test_alerta_alta_por_proporcion_de_cascos(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(
        monkeypatch,
        person_count=2,
        ppe_classes=("helmet", "Vest", "Vest"),
    )
    assert _upload("ppe_proporcion.png", auth_headers).status_code == 200

    alerta = fake_supabase.store["alertas"][1]
    assert alerta["nivel"] == "alta"
    assert alerta["descripcion"] == "Posible falta de casco detectada"


def test_sin_alerta_alta_si_hay_casco(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch, ppe_classes=("helmet",))
    assert _upload("ppe_con_casco.png", auth_headers).status_code == 200

    alertas = fake_supabase.store["alertas"]
    assert len(alertas) == 1
    assert alertas[0]["nivel"] == "baja"


def test_sin_alertas_sin_personas(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch, person_count=0, ppe_classes=())
    assert _upload("ppe_sin_personas.png", auth_headers).status_code == 200

    assert fake_supabase.store["alertas"] == []


def test_sin_caida_con_persona_de_pie(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch)
    assert _upload("sin_caida.png", auth_headers).status_code == 200

    payload = client.get("/results/sin_caida.png", headers=auth_headers).json()
    assert payload["caida_detectada"] is False
    assert all(alerta["tipo"] != "caida" for alerta in fake_supabase.store["alertas"])


def test_caida_detectada_genera_alerta_alta(monkeypatch, fake_supabase, auth_headers):
    _mock_pipeline(monkeypatch, caida=True)
    assert _upload(
        "caida.png", auth_headers, data={"obra_id": "obras-3"}
    ).status_code == 200

    payload = client.get("/results/caida.png", headers=auth_headers).json()
    assert payload["caida_detectada"] is True

    alerta = next(a for a in fake_supabase.store["alertas"] if a["tipo"] == "caida")
    assert alerta["descripcion"] == "Posible caída de personal detectada"
    assert alerta["nivel"] == "alta"
    assert alerta["resuelta"] is False
    assert alerta["obra_id"] == "obras-3"


def test_heuristica_caida_cuerpo_horizontal(monkeypatch, fake_supabase, auth_headers):
    # Torso vertical pero muy ancho: la proporción delata la caída.
    _mock_pipeline(monkeypatch, landmarks=_pose_landmarks(altura=0.5, ancho=0.75))
    assert _upload("caida_horizontal.png", auth_headers).status_code == 200

    payload = client.get("/results/caida_horizontal.png", headers=auth_headers).json()
    assert payload["caida_detectada"] is True


def test_heuristica_caida_rodillas_junto_a_hombros(
    monkeypatch, fake_supabase, auth_headers
):
    _mock_pipeline(
        monkeypatch,
        landmarks=_pose_landmarks(rodillas_junto_al_tronco=True),
    )
    assert _upload("caida_rodillas.png", auth_headers).status_code == 200

    payload = client.get("/results/caida_rodillas.png", headers=auth_headers).json()
    assert payload["caida_detectada"] is True


def test_detectar_caida_sin_pose(monkeypatch, tmp_path):
    monkeypatch.setattr(analysis, "_mediapipe_module", _FakeMediaPipe)
    monkeypatch.setattr(
        analysis, "get_pose_landmarker", lambda: _FakePoseLandmarker([])
    )
    imagen = tmp_path / "vacia.png"
    imagen.write_bytes(_dummy_png())

    assert analysis.detectar_caida(imagen) is False
