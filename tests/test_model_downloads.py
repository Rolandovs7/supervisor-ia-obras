"""Missing model weights are downloaded without performing real network calls."""

from pathlib import Path

from app.services import analysis


def _fake_downloads(monkeypatch, tmp_path):
    model = tmp_path / "yolov8n.pt"
    ppe = tmp_path / "ppe_model.pt"
    pose = tmp_path / "pose_landmarker.task"
    cached = tmp_path / "best.pt"
    cached.write_bytes(b"ppe")
    calls = []

    def fake_retrieve(url, destination):
        calls.append(url)
        Path(destination).write_bytes(b"yolo")

    def fake_hf_download(**kwargs):
        calls.append(kwargs)
        return str(cached)

    monkeypatch.setattr(analysis, "MODEL_PATH", model)
    monkeypatch.setattr(analysis, "PPE_MODEL_PATH", ppe)
    monkeypatch.setattr(analysis, "POSE_MODEL_PATH", pose)
    monkeypatch.setattr(analysis.urllib.request, "urlretrieve", fake_retrieve)
    monkeypatch.setattr(analysis, "hf_hub_download", fake_hf_download)
    return model, ppe, pose, calls


def test_ensure_models_downloads_missing_weights(monkeypatch, tmp_path):
    model, ppe, pose, calls = _fake_downloads(monkeypatch, tmp_path)

    analysis.ensure_models()

    assert model.read_bytes() == b"yolo"
    assert ppe.read_bytes() == b"ppe"
    assert pose.read_bytes() == b"yolo"
    assert calls[0] == analysis.MODEL_URL
    assert calls[1]["repo_id"] == "wntrsldr/yolov8n-ppe-detection-6classes"
    assert calls[1]["filename"] == "best.pt"
    assert calls[2] == analysis.POSE_MODEL_URL

    # A second call is a no-op because all files already exist.
    analysis.ensure_models()
    assert len(calls) == 3


def test_ensure_models_failure_is_not_fatal(monkeypatch, tmp_path, capsys):
    _fake_downloads(monkeypatch, tmp_path)

    def fail(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(analysis, "_download_person_model", fail)
    analysis.ensure_models()
    assert "WARN" in capsys.readouterr().out
