import sqlite3,json
from pathlib import Path
from datetime import datetime,timezone
from app.config import settings
def dbpath():
    u=settings.database_url
    p=Path(u.replace("sqlite:///","",1)) if u.startswith("sqlite:///") else settings.data_dir/"factory.db"
    if not p.is_absolute(): p=Path("/app")/p
    p.parent.mkdir(parents=True,exist_ok=True)
    return str(p)
DB=dbpath()
def conn():
    c=sqlite3.connect(DB,check_same_thread=False); c.row_factory=sqlite3.Row; return c
def init_db():
    with conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,topic TEXT,status TEXT,created_at TEXT,updated_at TEXT,data TEXT,error TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY,created_at TEXT,amount REAL,provider TEXT,job_id TEXT)")
def create_job(i,t,d):
    n=datetime.now(timezone.utc).isoformat()
    with conn() as c: c.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,?)",(i,t,"queued",n,n,json.dumps(d),None))
def update_job(i,status=None,data=None,error=None):
    n=datetime.now(timezone.utc).isoformat()
    with conn() as c:
        r=c.execute("SELECT data FROM jobs WHERE id=?",(i,)).fetchone()
        if not r:return
        d=json.loads(r["data"]); d.update(data or {})
        c.execute("UPDATE jobs SET status=?,updated_at=?,data=?,error=? WHERE id=?",(status or "running",n,json.dumps(d),error,i))
def get_job(i):
    with conn() as c:r=c.execute("SELECT * FROM jobs WHERE id=?",(i,)).fetchone()
    if not r:return None
    d=dict(r);d["data"]=json.loads(d["data"]);return d
def list_jobs():
    with conn() as c:rs=c.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100").fetchall()
    out=[]
    for r in rs:
        d=dict(r);d["data"]=json.loads(d["data"]);out.append(d)
    return out
def add_usage(a,p,j):
    with conn() as c:c.execute("INSERT INTO usage(created_at,amount,provider,job_id) VALUES(?,?,?,?)",(datetime.now(timezone.utc).isoformat(),a,p,j))
def monthly_usage():
    m=datetime.now(timezone.utc).strftime("%Y-%m")
    with conn() as c:r=c.execute("SELECT COALESCE(SUM(amount),0) n FROM usage WHERE substr(created_at,1,7)=?",(m,)).fetchone()
    return float(r["n"])
