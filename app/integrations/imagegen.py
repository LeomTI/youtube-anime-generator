"""Per-scene anime artwork generation. Requires STABILITY_API_KEY or OPENAI_API_KEY."""
import base64
import os
from pathlib import Path
import requests

def generate_anime_image(prompt: str, output: Path, scene_index: int, character_description: str = ""):
    style = ("Original high-quality 2D Japanese anime film frame, hand-drawn cel animation, "
             "detailed background art, expressive original characters, cinematic composition, "
             "rich color, coherent lighting, clean line art, widescreen 16:9. "
             "One distinct shot; no text, subtitles, logos, watermarks, panels or collage. ")
    continuity = f"Keep character designs consistent with this character guide: {character_description}. " if character_description else ""
    full_prompt = style + continuity + f"Scene {scene_index}. {prompt}"
    stability_key = os.getenv("STABILITY_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if stability_key:
        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={"Authorization": f"Bearer {stability_key}", "Accept": "image/*"},
            files={"none": ("", b"")},
            data={"prompt": full_prompt, "aspect_ratio": "16:9", "output_format": "png"},
            timeout=180)
        response.raise_for_status()
        output.write_bytes(response.content)
    elif openai_key:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json={"model": os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
                  "prompt": full_prompt, "size": "1536x1024", "quality": "medium", "n": 1},
            timeout=240)
        response.raise_for_status()
        output.write_bytes(base64.b64decode(response.json()["data"][0]["b64_json"]))
    else:
        raise RuntimeError("Anime image generation is not configured. Add STABILITY_API_KEY or OPENAI_API_KEY to .env; refusing to render placeholder backgrounds.")
    if not output.exists() or output.stat().st_size < 1000:
        raise RuntimeError(f"Image provider returned an invalid image for scene {scene_index}")
    return output
