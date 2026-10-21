from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.config import settings
SCOPES=["https://www.googleapis.com/auth/youtube.upload"]
def youtube_service():
    secret=Path(settings.youtube_client_secret);token=Path(settings.youtube_token_file)
    if not secret.exists():raise RuntimeError("YouTube OAuth client JSON missing: "+str(secret))
    creds=Credentials.from_authorized_user_file(str(token),SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:creds.refresh(Request())
    if not creds or not creds.valid:
        flow=InstalledAppFlow.from_client_secrets_file(str(secret),SCOPES)
        #creds=flow.run_local_server(port=0)
        creds = flow.run_local_server( host="0.0.0.0",  port=8080, open_browser=False)
        token.parent.mkdir(parents=True,exist_ok=True);token.write_text(creds.to_json())
    return build("youtube","v3",credentials=creds)
def upload_video(path,title,description,tags=None,privacy_status="private",publish_at=None):
    service=youtube_service()
    status={"privacyStatus":privacy_status,"selfDeclaredMadeForKids":settings.youtube_made_for_kids}
    if publish_at:status.update({"privacyStatus":"private","publishAt":publish_at})
    body={"snippet":{"title":title[:100],"description":description[:5000],"tags":(tags or [])[:500],"categoryId":"1"},"status":status}
    media=MediaFileUpload(str(path),chunksize=-1,resumable=True,mimetype="video/mp4")
    req=service.videos().insert(part="snippet,status",body=body,media_body=media);res=None
    while res is None:_,res=req.next_chunk()
    return res
