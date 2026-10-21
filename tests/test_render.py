from app.services.render import scene_png
def test_scene_png(tmp_path):
    p=tmp_path/"scene.png";scene_png("Friendly dragon","A star shines.",1,p)
    assert p.exists() and p.stat().st_size>100
