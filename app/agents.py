import json
from app.integrations.groq import GroqClient
from app.integrations.tts import synthesize
from app.services.render import render_episode,make_short
from app.config import settings
SYSTEM="You are a careful children's story editor. Create original, age-appropriate stories. Never use copyrighted anime characters, franchises, celebrity voices, existing plots or lyrics. Avoid frightening, violent, manipulative or unsafe instructions. Return valid JSON only."
def generate_story(topic,languages,job_dir):
    c=GroqClient()
    prompt=f'''Create an original anime-inspired children's story about: {topic}. Target age 6-10. Main language {languages[0] if languages else "en"}. 3-5 minute narration, 450-650 words, compelling first 5 seconds, emotional arc, gentle humor and positive resolution. Return JSON keys: title,logline,narration,scenes,youtube_title,youtube_description,tags,safety_notes. scenes must contain 8-12 objects with title,visual_prompt,narration_excerpt. Characters/world must be original. Never solicit personal information from children.'''
    d=c.complete_json(SYSTEM,prompt)
    if not d.get("narration") or not d.get("scenes"):raise ValueError("Groq output missing narration/scenes")
    d["scenes"]=d["scenes"][:settings.max_scenes]
    (job_dir/"story.json").write_text(json.dumps(d,indent=2,ensure_ascii=False))
    (job_dir/"script.txt").write_text(d["narration"])
    return d
def create_assets(story,languages,job_dir):
    c=GroqClient();audios=[]
    for lang in languages or ["en"]:
        text=story["narration"]
        if lang!="en":
            d=c.complete_json("Translate children's narration naturally and faithfully. Return JSON {narration:string}.",f"Translate to language code {lang}; preserve names and meaning:\n{text}")
            text=d["narration"];(job_dir/f"script_{lang}.txt").write_text(text)
        audio=job_dir/f"narration_{lang}.mp3";synthesize(text,lang,audio);audios.append((lang,audio))
    long=render_episode(story["scenes"],audios[0][1],job_dir/"episode_16x9.mp4",settings.episode_minutes)
    short=make_short(long,job_dir/"short_9x16.mp4")
    return long,short,audios
