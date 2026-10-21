import os, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
def flag(k, d=False): return os.getenv(k,str(d)).lower() in ("1","true","yes","on")
class Settings:
    app_env=os.getenv("APP_ENV","development")
    data_dir=Path(os.getenv("DATA_DIR","./data"))
    database_url=os.getenv("DATABASE_URL","sqlite:///./data/factory.db")
    groq_api_key=os.getenv("GROQ_API_KEY","")
    groq_model=os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")
    groq_base_url=os.getenv("GROQ_BASE_URL","https://api.groq.com/openai/v1")
    runway_api_key=os.getenv("RUNWAY_API_KEY","")
    runway_api_base=os.getenv("RUNWAY_API_BASE","https://api.dev.runwayml.com")
    runway_api_version=os.getenv("RUNWAY_API_VERSION","2024-11-06")
    runway_model=os.getenv("RUNWAY_MODEL","gen4_turbo")
    enable_runway=flag("ENABLE_RUNWAY")
    youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET","/app/secrets/client_secret.json")
    youtube_token_file=os.getenv("YOUTUBE_TOKEN_FILE","/app/secrets/token.json")
    youtube_privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS","private")
    youtube_made_for_kids=flag("YOUTUBE_MADE_FOR_KIDS",True)
    monthly_budget=float(os.getenv("MONTHLY_BUDGET_USD","80"))
    cost_groq_job=float(os.getenv("COST_PER_GROQ_JOB_USD","0.02"))
    max_scenes=int(os.getenv("MAX_SCENES","12"))
    episode_minutes=int(os.getenv("EPISODE_MINUTES","4"))
    try: tts_voice_map=json.loads(os.getenv("TTS_VOICE_MAP",'{"en":"en-US-AriaNeural"}'))
    except ValueError: tts_voice_map={"en":"en-US-AriaNeural"}
settings=Settings()
settings.data_dir.mkdir(parents=True,exist_ok=True)
