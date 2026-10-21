from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
p=Path("secrets/client_secret.json")
if not p.exists():raise SystemExit("Save Google OAuth Desktop JSON as secrets/client_secret.json")
flow=InstalledAppFlow.from_client_secrets_file(str(p),["https://www.googleapis.com/auth/youtube.upload"])
c=flow.run_local_server( host="0.0.0.0",  port=8080, open_browser=False)
Path("secrets/token.json").write_text(c.to_json())
print("Saved secrets/token.json; keep it private.")
