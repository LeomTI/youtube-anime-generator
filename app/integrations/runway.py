import requests,time
from app.config import settings
class RunwayClient:
    # Validate the live API schema/model availability against Runway docs before production.
    def __init__(self):
        self.base=settings.runway_api_base.rstrip("/")
        self.headers={"Authorization":"Bearer "+settings.runway_api_key,"X-Runway-Version":settings.runway_api_version,"Content-Type":"application/json"}
    def create_text_to_video(self,prompt,duration=5,ratio="16:9"):
        if not settings.runway_api_key:raise RuntimeError("RUNWAY_API_KEY missing")
        payload={"model":settings.runway_model,"promptText":prompt,"duration":duration,"ratio":ratio}
        r=requests.post(self.base+"/v1/text_to_video",headers=self.headers,json=payload,timeout=90);r.raise_for_status();return r.json()
    def wait_for_task(self,task_id,timeout=900):
        end=time.time()+timeout
        while time.time()<end:
            r=requests.get(self.base+"/v1/tasks/"+task_id,headers=self.headers,timeout=30);r.raise_for_status()
            d=r.json()
            if d.get("status") in ("SUCCEEDED","FAILED","CANCELED"):return d
            time.sleep(5)
        raise TimeoutError("Runway polling timeout")
