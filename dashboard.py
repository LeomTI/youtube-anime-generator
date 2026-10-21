import os,requests,streamlit as st
API=os.getenv("API_BASE_URL","http://api:8000")
st.set_page_config(page_title="Anime YouTube Factory",page_icon="🎬",layout="wide")
st.title("🎬 Anime YouTube Factory")
st.caption("Original children's stories · Shorts + episodes · human-approved publishing")
def call(m,p,**kw):
    try:
        r=requests.request(m,API+p,timeout=30,**kw)
        if r.status_code>=400:st.error(f"API {r.status_code}: {r.text}")
        r.raise_for_status();return r.json()
    except requests.RequestException as e:st.error(f"Backend unavailable: {e}")
health=call("GET","/health");jobs=call("GET","/jobs") or []
a,b,c=st.columns(3);a.metric("Jobs",len(jobs));b.metric("Awaiting approval",sum(x["status"]=="pending_approval" for x in jobs));c.metric("Published",sum(x["status"]=="published" for x in jobs))
with st.sidebar:
    st.header("Create episode")
    topic=st.text_area("Story idea",placeholder="A shy fox discovers a floating library...")
    langs=st.multiselect("Narration languages",["en","es","fr","de","pt","hi"],["en"])
    shorts=st.checkbox("Create vertical Short",True)
    if st.button("✨ Generate episode",type="primary",use_container_width=True):
        if len(topic.strip())<3:st.warning("Enter a story idea.")
        else:
            res=call("POST","/jobs",json={"topic":topic,"languages":langs or ["en"],"make_shorts":shorts})
            if res:st.success("Queued "+res["job_id"])
st.subheader("Production queue")
for j in jobs:
    with st.expander(f'{j["topic"]} · {j["status"]} · {j["id"][:8]}',expanded=j["status"]=="pending_approval"):
        st.write("Created:",j["created_at"])
        if j.get("error"):st.error(j["error"])
        d=j["data"]
        if d.get("title"):st.write("Title:",d["title"])
        if d.get("files"):st.json(d["files"])
        if j["status"]=="pending_approval":
            st.warning("Review story, narration and MP4 under data/jobs before approving.")
            if st.button("Approve episode",key="a"+j["id"]):call("POST",f'/jobs/{j["id"]}/approve');st.rerun()
        if j["status"]=="approved":
            asset=st.selectbox("Video format",["episode","short"],key="f"+j["id"])
            vis=st.selectbox("Visibility",["private","unlisted","public"],key="v"+j["id"])
            if st.button("Upload to YouTube",key="p"+j["id"]):
                res=call("POST",f'/jobs/{j["id"]}/publish',json={"privacy_status":vis,"asset":asset})
                if res:st.success("Uploaded");st.rerun()
        if d.get("youtube_url"):st.markdown(f'[Open video]({d["youtube_url"]})')
st.divider()
st.info("Fallback visuals are animated story cards. Configure provider credentials and review all children's content before publication.")
if st.button("Refresh"):st.rerun()
