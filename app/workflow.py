from pathlib import Path
from app.config import settings
from app import db
from app.agents import generate_story,create_assets
def run_job(job_id,topic,languages,make_shorts):
    folder=settings.data_dir/"jobs"/job_id;folder.mkdir(parents=True,exist_ok=True)
    try:
        db.update_job(job_id,"generating_script")
        story=generate_story(topic,languages,folder)
        db.update_job(job_id,"rendering",{"title":story.get("youtube_title",story["title"]),"description":story.get("youtube_description",""),"tags":story.get("tags",[]),"story_title":story["title"]})
        long,short,audios=create_assets(story,languages,folder)
        db.update_job(job_id,"pending_approval",{"files":{"episode":str(long),"short":str(short) if make_shorts else None,"story":str(folder/"story.json"),"script":str(folder/"script.txt"),"audio":[str(a[1]) for a in audios]},"languages":languages,"approved":False})
    except Exception as e:db.update_job(job_id,"failed",error=f"{type(e).__name__}: {e}")
