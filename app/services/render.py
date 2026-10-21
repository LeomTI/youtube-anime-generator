from pathlib import Path
import subprocess,html,cairosvg,os

def video_encoder():
    # Probe actual NVENC initialization; fall back if the driver/runtime is unavailable.
    if os.getenv("VIDEO_ENCODER", "auto").lower() != "cpu":
        try:
            p = subprocess.run(
                ["ffmpeg","-hide_banner","-loglevel","error","-f","lavfi","-i",
                 "color=c=black:s=64x64:d=0.1","-frames:v","1","-c:v","h264_nvenc","-f","null","-"],
                capture_output=True, text=True, timeout=20)
            if p.returncode == 0:
                return "h264_nvenc", ["-preset","p4"]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    return "libx264", ["-preset","veryfast"]

def run(cmd):subprocess.run(cmd,check=True,capture_output=True,text=True)
def scene_png(title,body,index,path):
    t=html.escape(str(title)[:90]);b=html.escape(str(body)[:240])
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><defs><linearGradient id="g"><stop stop-color="#18284e"/><stop offset="1" stop-color="#84518a"/></linearGradient></defs><rect width="1280" height="720" fill="url(#g)"/><circle cx="1050" cy="130" r="75" fill="#ffe8a3"/><path d="M0 570 Q300 420 650 570 T1280 540 V720 H0Z" fill="#1b3b50"/><text x="85" y="125" font-family="DejaVu Sans" font-size="30" fill="#f9dca5">ORIGINAL STORY · SCENE {index}</text><foreignObject x="85" y="205" width="1100" height="170"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:DejaVu Sans;font-size:54px;font-weight:bold;color:white">{t}</div></foreignObject><foreignObject x="85" y="405" width="1100" height="230"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family:DejaVu Sans;font-size:29px;line-height:1.5;color:#f2efff">{b}</div></foreignObject></svg>'''
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(path))
def render_episode(scenes,audio,output,minutes=4):
    tmp=output.parent/(output.stem+"_tmp");tmp.mkdir(exist_ok=True)
    each=max(5,minutes*60/max(1,len(scenes)));clips=[]
    encoder,preset=video_encoder()
    for i,s in enumerate(scenes,1):
        png=tmp/f"s{i}.png";clip=tmp/f"s{i}.mp4"
        scene_png(s.get("title","A New Adventure"),s.get("visual_prompt",""),i,png)
        run(["ffmpeg","-y","-loop","1","-i",str(png),"-t",str(each),"-vf","scale=1920:1080,zoompan=z='min(zoom+0.0005,1.08)':d=1:s=1920x1080:fps=25,format=yuv420p","-r","25","-an","-c:v",encoder,*preset,str(clip)])
        clips.append(clip)
    concat=tmp/"concat.txt";concat.write_text("".join("file '"+p.as_posix()+"'\n" for p in clips))
    silent=tmp/"silent.mp4";run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    run(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-shortest","-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",str(output)])
    return output
def make_short(source,out):
    encoder,preset=video_encoder()
    cmd=["ffmpeg","-y","-i",str(source),"-t","55","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920","-c:v",encoder,*preset,"-c:a","aac","-movflags","+faststart",str(out)]
    try:
        run(cmd)
    except subprocess.CalledProcessError:
        if encoder != "h264_nvenc": raise
        run(["ffmpeg","-y","-i",str(source),"-t","55","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920","-c:v","libx264","-preset","veryfast","-c:a","aac","-movflags","+faststart",str(out)])
    return out
