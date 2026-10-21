def test_cpu_encoder_override(monkeypatch):
    from app.services import render
    monkeypatch.setenv("VIDEO_ENCODER", "cpu")
    assert render.video_encoder() == ("libx264", ["-preset", "veryfast"])
