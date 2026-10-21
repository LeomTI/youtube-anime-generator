
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import edge_tts
from app.config import settings


async def _speak(text, voice, path):
    await edge_tts.Communicate(text, voice).save(str(path))


def _run_speech(text, voice, path):
    """Run speech synthesis with limited retries."""
    last_error = None

    for attempt in range(3):
        try:
            asyncio.run(_speak(text, voice, path))

            output = Path(path)
            if not output.exists() or output.stat().st_size == 0:
                raise RuntimeError("TTS completed but produced no audio file.")

            return path

        except Exception as exc:
            last_error = exc
            error_text = str(exc)

            # A 403 is generally a rejected service handshake.
            # Repeating the same request is unlikely to fix it.
            if "403" in error_text:
                raise RuntimeError(
                    "Microsoft Edge TTS rejected the connection (HTTP 403). "
                    "Update edge-tts or configure another TTS provider."
                ) from exc

            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        f"Speech synthesis failed after 3 attempts: {last_error}"
    ) from last_error


def synthesize(text, lang, path):
    voice = settings.tts_voice_map.get(
        lang,
        settings.tts_voice_map.get("en", "en-US-AriaNeural")
    )

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return _run_speech(text, voice, path)

    # If called from an existing async event loop, use a separate thread.
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_speech, text, voice, path)
        return future.result()
