from pydantic import BaseModel,Field
from typing import List,Optional
class JobRequest(BaseModel):
    topic:str=Field(min_length=3,max_length=240)
    languages:List[str]=["en"]
    make_shorts:bool=True
class PublishRequest(BaseModel):
    privacy_status:str="private"
    publish_at:Optional[str]=None
    asset:str="episode"
