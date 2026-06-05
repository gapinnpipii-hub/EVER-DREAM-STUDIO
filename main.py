from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, io, os, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def extract_video_id(url: str):
    patterns = [
        r'(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

@app.get("/info")
async def get_info(url: str = Query(...)):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return JSONResponse({
                "id": info.get("id"),
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
            })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal mengambil info: {str(e)}")

@app.get("/search")
async def search(q: str = Query(...)):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch10:{q}", download=False)
            items = []
            for entry in results.get("entries", []):
                if not entry:
                    continue
                items.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "channel": entry.get("uploader") or entry.get("channel"),
                    "duration": entry.get("duration"),
                    "thumbnail": f"https://i.ytimg.com/vi/{entry.get('id')}/mqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                })
            return JSONResponse({"results": items})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pencarian gagal: {str(e)}")

@app.get("/audio")
async def get_audio(url: str = Query(...)):
    # Validasi URL dulu
    if not extract_video_id(url):
        raise HTTPException(status_code=400, detail="URL YouTube tidak valid")
    
    path = None
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = f"/tmp/{info['id']}.mp3"
        
        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="File audio tidak ditemukan setelah download")

        def iterfile():
            try:
                with open(path, 'rb') as f:
                    yield from f
            finally:
                # Selalu hapus file, bahkan jika error
                if path and os.path.exists(path):
                    os.remove(path)

        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    except HTTPException:
        raise
    except Exception as e:
        if path and os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail=f"Gagal mengambil audio: {str(e)}")
