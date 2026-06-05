from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re, httpx, tempfile, shutil, subprocess

def find_ffmpeg():
    # Coba which dulu
    path = shutil.which('ffmpeg')
    if path:
        return os.path.dirname(path)
    # Coba path umum Nix di Railway
    for p in ['/usr/bin', '/usr/local/bin', '/nix/var/nix/profiles/default/bin', '/root/.nix-profile/bin']:
        if os.path.exists(os.path.join(p, 'ffmpeg')):
            return p
    # Coba find
    try:
        result = subprocess.run(['find', '/nix', '-name', 'ffmpeg', '-type', 'f'], 
                                capture_output=True, text=True, timeout=5)
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        if lines:
            return os.path.dirname(lines[0])
    except Exception:
        pass
    return None

FFMPEG_PATH = find_ffmpeg()
print(f"[startup] ffmpeg location: {FFMPEG_PATH}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def base_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

def extract_sc_id(url: str) -> bool:
    return 'soundcloud.com' in url

def pick_stream_url(info: dict) -> str:
    formats = info.get('formats') or []

    audio_only = [
        f for f in formats
        if f.get('acodec') not in (None, 'none')
        and f.get('vcodec') in (None, 'none')
        and f.get('url')
    ]
    if audio_only:
        audio_only.sort(key=lambda f: f.get('abr') or f.get('tbr') or 0)
        return audio_only[-1]['url']

    with_audio = [
        f for f in formats
        if f.get('acodec') not in (None, 'none') and f.get('url')
    ]
    if with_audio:
        with_audio.sort(key=lambda f: f.get('abr') or f.get('tbr') or 0)
        return with_audio[-1]['url']

    if info.get('url'):
        return info['url']

    return None


# ── SEARCH ──
@app.get("/search")
async def search(q: str = Query(...), limit: int = 10):
    try:
        opts = base_ydl_opts()
        opts['skip_download'] = True
        opts['extract_flat'] = True
        with yt_dlp.YoutubeDL(opts) as ydl:
            results = ydl.extract_info(f"scsearch{limit}:{q}", download=False)
            items = []
            for entry in (results.get("entries") or []):
                if not entry:
                    continue
                items.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "channel": entry.get("uploader") or entry.get("channel"),
                    "duration": entry.get("duration"),
                    "view_count": entry.get("view_count"),
                    "thumbnail": entry.get("thumbnail") or "",
                    "url": entry.get("url") or entry.get("webpage_url") or "",
                })
            return JSONResponse({"results": items, "count": len(items)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pencarian gagal: {str(e)}")


# ── STREAM URL ──
@app.get("/stream-url")
async def get_stream_url(url: str = Query(...)):
    if 'soundcloud.com' not in url:
        raise HTTPException(status_code=400, detail="URL SoundCloud tidak valid")
    try:
        opts = base_ydl_opts()
        opts['skip_download'] = True

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
    if 'soundcloud.com' not in url:
        raise HTTPException(status_code=400, detail="URL tidak valid")
    try:
        opts = base_ydl_opts()
        opts['skip_download'] = True

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = pick_stream_url(info)
            if not stream_url:
                raise HTTPException(status_code=500, detail="Stream URL tidak ditemukan")

        async def stream_audio():
            async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
                async with client.stream("GET", stream_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Referer": "https://soundcloud.com/",
                }) as r:
                    async for chunk in r.aiter_bytes(chunk_size=65536):
                        yield chunk

        return StreamingResponse(stream_audio(), media_type="audio/mpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy gagal: {str(e)}")


# ── AUDIO DOWNLOAD MP3 ──
@app.get("/audio")
async def get_audio(url: str = Query(...)):
    if 'soundcloud.com' not in url:
        raise HTTPException(status_code=400, detail="URL SoundCloud tidak valid")
    path = None
    try:
        opts = base_ydl_opts()
        opts['format'] = 'bestaudio/best'
        opts['outtmpl'] = '/tmp/%(id)s.%(ext)s'
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
        if FFMPEG_PATH:
            opts['ffmpeg_location'] = FFMPEG_PATH

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_id = info.get('id', 'audio')
            # cari file mp3
            path = f"/tmp/{vid_id}.mp3"
            if not os.path.exists(path):
                # coba ext lain
                for ext in ['mp3', 'm4a', 'opus', 'ogg']:
                    p = f"/tmp/{vid_id}.{ext}"
                    if os.path.exists(p):
                        path = p
                        break

        if not path or not os.path.exists(path):
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
