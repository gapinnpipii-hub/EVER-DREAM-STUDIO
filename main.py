from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def extract_video_id(url: str):
    m = re.search(r'(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})', url)
    return m.group(1) if m else None

def fmt_duration(sec):
    if not sec: return '—'
    sec = int(sec)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

# ── SEARCH ──
@app.get("/search")
async def search(q: str = Query(...), limit: int = 10):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)
            items = []
            for entry in results.get("entries", []):
                if not entry:
                    continue
                vid_id = entry.get("id")
                items.append({
                    "id": vid_id,
                    "title": entry.get("title"),
                    "channel": entry.get("uploader") or entry.get("channel"),
                    "duration": entry.get("duration"),
                    "view_count": entry.get("view_count"),
                    "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                })
            return JSONResponse({"results": items, "count": len(items)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pencarian gagal: {str(e)}")

# ── STREAM URL (untuk decode audio di browser) ──
@app.get("/stream-url")
async def get_stream_url(url: str = Query(...)):
    if not extract_video_id(url):
        raise HTTPException(status_code=400, detail="URL YouTube tidak valid")
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
            'quiet': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Cari format audio terbaik
            formats = info.get('formats', [])
            audio_fmt = next(
                (f for f in reversed(formats)
                 if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url')),
                None
            )
            stream_url = (audio_fmt or {}).get('url') or info.get('url')

            if not stream_url:
                raise HTTPException(status_code=500, detail="Tidak dapat menemukan stream URL")

            return JSONResponse({
                "stream_url": stream_url,
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
            })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil stream URL: {str(e)}")

# ── AUDIO DOWNLOAD (download langsung MP3) ──
@app.get("/audio")
async def get_audio(url: str = Query(...)):
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
                if path and os.path.exists(path):
                    os.remove(path)

        title = info.get('title', 'audio').replace('/', '_')
        return StreamingResponse(
            iterfile(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f'attachment; filename="{title}.mp3"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        if path and os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail=f"Gagal mengambil audio: {str(e)}")
