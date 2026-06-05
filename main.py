from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re, httpx

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

def get_ydl_opts(extra={}):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv_embedded', 'ios'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
        },
    }
    opts.update(extra)
    return opts

def pick_stream_url(info: dict) -> str:
    """Ambil URL audio terbaik dari info, dengan banyak fallback."""
    formats = info.get('formats') or []
    
    # Prioritas 1: audio only webm/m4a
    for fmt in reversed(formats):
        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none' and fmt.get('url'):
            return fmt['url']
    
    # Prioritas 2: format apapun yang punya audio
    for fmt in reversed(formats):
        if fmt.get('acodec') != 'none' and fmt.get('url'):
            return fmt['url']
    
    # Prioritas 3: url langsung dari info
    if info.get('url'):
        return info['url']
    
    return None

# ── SEARCH ──
@app.get("/search")
async def search(q: str = Query(...), limit: int = 10):
    try:
        opts = get_ydl_opts({
            'skip_download': True,
            'extract_flat': True,
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            results = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)
            items = []
            for entry in (results.get("entries") or []):
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

# ── STREAM URL ──
@app.get("/stream-url")
async def get_stream_url(url: str = Query(...)):
    if not extract_video_id(url):
        raise HTTPException(status_code=400, detail="URL YouTube tidak valid")
    try:
        opts = get_ydl_opts({'skip_download': True})
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = pick_stream_url(info)
            if not stream_url:
                raise HTTPException(status_code=500, detail="Stream URL tidak ditemukan")
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

# ── PROXY AUDIO ──
@app.get("/proxy-audio")
async def proxy_audio(url: str = Query(...)):
    if not extract_video_id(url):
        raise HTTPException(status_code=400, detail="URL tidak valid")
    try:
        opts = get_ydl_opts({'skip_download': True})
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = pick_stream_url(info)
            if not stream_url:
                raise HTTPException(status_code=500, detail="Stream URL tidak ditemukan")

        async def stream_audio():
            async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
                async with client.stream("GET", stream_url, headers={
                    "User-Agent": "Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version",
                    "Referer": "https://www.youtube.com/",
                }) as r:
                    async for chunk in r.aiter_bytes(chunk_size=65536):
                        yield chunk

        return StreamingResponse(stream_audio(), media_type="audio/webm")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy gagal: {str(e)}")

# ── AUDIO DOWNLOAD MP3 ──
@app.get("/audio")
async def get_audio(url: str = Query(...)):
    if not extract_video_id(url):
        raise HTTPException(status_code=400, detail="URL YouTube tidak valid")
    path = None
    try:
        opts = get_ydl_opts({
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        })
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = f"/tmp/{info['id']}.mp3"

        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="File tidak ditemukan")

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
        raise HTTPException(status_code=500, detail=f"Gagal: {str(e)}")
