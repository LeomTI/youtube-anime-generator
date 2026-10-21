from fastapi import FastAPI,HTTPException,BackgroundTasks
import uuid
from app import db
from app.models import JobRequest,PublishRequest
from app.workflow import run_job
from app.config import settings
from app.integrations.youtube import upload_video
app=FastAPI(title="Anime YouTube Factory",version="1.0.0")
@app.on_event("startup")
def startup():db.init_db()
@app.get("/health")
def health():return {"status":"ok","app":"anime-youtube-factory"}
@app.post("/jobs",status_code=202)
def create(req:JobRequest,tasks:BackgroundTasks):
    if db.monthly_usage()+settings.cost_groq_job>settings.monthly_budget:raise HTTPException(402,"Monthly estimated AI budget reached")
    jid=str(uuid.uuid4());db.create_job(jid,req.topic,{"languages":req.languages,"make_shorts":req.make_shorts})
    db.add_usage(settings.cost_groq_job,"groq_estimate",jid);tasks.add_task(run_job,jid,req.topic,req.languages,req.make_shorts)
    return {"job_id":jid,"status":"queued"}
@app.get("/jobs")
def jobs():return db.list_jobs()
@app.get("/jobs/{jid}")
def job(jid):
    d=db.get_job(jid)
    if not d:raise HTTPException(404,"Job not found")
    return d
@app.post("/jobs/{jid}/approve")
def approve(jid):
    d=db.get_job(jid)
    if not d:raise HTTPException(404,"Job not found")
    if d["status"]!="pending_approval":raise HTTPException(409,"Not awaiting approval")
    db.update_job(jid,"approved",{"approved":True});return {"status":"approved"}
@app.post("/jobs/{jid}/publish")
def publish(jid,req:PublishRequest):
    d=db.get_job(jid)
    if not d:raise HTTPException(404,"Job not found")
    if d["status"]!="approved" or not d["data"].get("approved"):raise HTTPException(409,"Approve before publishing")
    try:
        x=upload_video(d["data"]["files"]["episode"],d["data"]["title"],d["data"]["description"],d["data"]["tags"],req.privacy_status,req.publish_at)
        db.update_job(jid,"published",{"youtube_video_id":x.get("id"),"youtube_url":"https://youtube.com/watch?v="+x.get("id",""),"published_asset":req.asset})
        return {"status":"published","youtube":x}
    except Exception as e:
        db.update_job(jid,"publish_failed",error=str(e));raise HTTPException(502,"YouTube upload failed: "+str(e))
