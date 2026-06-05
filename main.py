from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re, httpx, tempfile, shutil, subprocess

def find_ffmpeg():
    path = shutil.which('ffmpeg')
    if path:
        print(f"[ffmpeg] found via which: {path}")
        return os.path.dirname(path)
    for p in ['/usr/local/bin', '/usr/bin', '/bin',
              '/nix/var/nix/profiles/default/bin',
              '/root/.nix-profile/bin']:
        if os.path.exists(os.path.join(p, 'ffmpeg')):
            print(f"[ffmpeg] found at: {p}")
            return p
    for search_dir in ['/nix', '/usr']:
        try:
            result = subprocess.run(
                ['find', search_dir, '-name', 'ffmpeg', '-type', 'f'],
                capture_output=True, text=True, timeout=10
            )
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            if lines:
                found = lines[0]
                print(f"[ffmpeg] found via find: {found}")
                return os.path.dirname(found)
        except Exception as e:
            print(f"[ffmpeg] find error in {search_dir}: {e}")
    print("[ffmpeg] NOT FOUND anywhere!")
    return None

FFMPEG_PATH = find_ffmpeg()
print(f"[startup] FFMPEG_PATH = {FFMPEG_PATH}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SC_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://soundcloud.com/',
}

def base_ydl_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'http_headers': SC_HEADERS,
    }

def pick_best_http_url(info: dict):
    """
    Cari format audio yang punya URL HTTP biasa (bukan HLS/m3u8/dash).
    Return (url, ext, abr) atau None kalau tidak ada.
    """
    formats = info.get('formats') or []

    # Prioritas: audio-only, non-HLS, bitrate tertinggi
    candidates = []
    for f in formats:
        url = f.get('url', '')
        proto = f.get('protocol', '')
        # Skip HLS dan DASH
        if 'm3u8' in url or 'mpd' in url:
            continue
        if proto in ('m3u8', 'm3u8_native', 'dash', 'http_dash_segments'):
            continue
        if f.get('acodec') in (None, 'none'):
            continue
        candidates.append(f)

    if candidates:
        # Sort by bitrate desc
        candidates.sort(key=lambda f: f.get('abr') or f.get('tbr') or 0, reverse=True)
        best = candidates[0]
        return best.get('url'), best.get('ext', 'mp3'), best.get('abr', 0)

    return None, None, None

def pick_stream_url(info: dict) -> str:
    """Fallback: ambil URL apapun termasuk HLS."""
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
    return info.get('url')


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
# Mengembalikan stream_url + is_hls flag supaya frontend tahu cara memutar
@app.get("/stream-url")
async def get_stream_url(url: str = Query(...)):
    if 'soundcloud.com' not in url:
        raise HTTPException(status_code=400, detail="URL SoundCloud tidak valid")
    try:
        opts = base_ydl_opts()
        opts['skip_download'] = True

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Coba cari URL HTTP biasa dulu
            http_url, ext, abr = pick_best_http_url(info)
            if http_url:
                return JSONResponse({
                    "stream_url": http_url,
                    "is_hls": False,
                    "ext": ext,
                    "abr": abr,
                    "title": info.get("title"),
                    "channel": info.get("uploader"),
                    "duration": info.get("duration"),
                    "thumbnail": info.get("thumbnail"),
                })

            # Fallback ke HLS/apapun
            stream_url = pick_stream_url(info)
            if not stream_url:
                raise HTTPException(status_code=500, detail="Stream URL tidak ditemukan")

            is_hls = 'm3u8' in stream_url or 'mpd' in stream_url
            return JSONResponse({
                "stream_url": stream_url,
                "is_hls": is_hls,
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
            })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil stream URL: {str(e)}")


# ── PROXY AUDIO (untuk playback & process dari search) ──
# Sekarang menggunakan yt-dlp download langsung ke memory via pipe
@app.get("/proxy-audio")
async def proxy_audio(url: str = Query(...)):
    if 'soundcloud.com' not in url:
        raise HTTPException(status_code=400, detail="URL tidak valid")
    try:
        opts = base_ydl_opts()
        opts['skip_download'] = True

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Coba HTTP URL biasa dulu — bisa di-stream langsung
            http_url, ext, abr = pick_best_http_url(info)
            if http_url:
                async def stream_direct():
                    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
                        async with client.stream("GET", http_url, headers=SC_HEADERS) as r:
                            if r.status_code >= 400:
                                raise HTTPException(status_code=502, detail=f"Upstream error {r.status_code}")
                            async for chunk in r.aiter_bytes(chunk_size=65536):
                                yield chunk

                return StreamingResponse(
                    stream_direct(),
                    media_type="audio/mpeg",
                    headers={"Cache-Control": "no-cache"}
                )

            # Fallback: kalau HLS, harus download dulu pakai ffmpeg
            stream_url = pick_stream_url(info)
            if not stream_url:
                raise HTTPException(status_code=500, detail="Stream URL tidak ditemukan")

            is_hls = 'm3u8' in stream_url or 'mpd' in stream_url
            if not is_hls:
                # Stream biasa tapi tidak terdeteksi di atas, coba langsung
                async def stream_fallback():
                    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
                        async with client.stream("GET", stream_url, headers=SC_HEADERS) as r:
                            async for chunk in r.aiter_bytes(chunk_size=65536):
                                yield chunk
                return StreamingResponse(stream_fallback(), media_type="audio/mpeg")

            # HLS: perlu ffmpeg untuk convert ke mp3
            if not FFMPEG_PATH:
                raise HTTPException(status_code=500, detail="ffmpeg tidak tersedia untuk decode HLS")

            ffmpeg_bin = os.path.join(FFMPEG_PATH, 'ffmpeg')
            cmd = [
                ffmpeg_bin, '-y',
                '-headers', ''.join(f'{k}: {v}\r\n' for k, v in SC_HEADERS.items()),
                '-i', stream_url,
                '-vn',
                '-acodec', 'libmp3lame',
                '-ab', '128k',
                '-f', 'mp3',
                'pipe:1'
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )

            async def stream_ffmpeg():
                try:
                    while True:
                        chunk = await proc.stdout.read(65536)
                        if not chunk:
                            break
                        yield chunk
                finally:
                    try:
                        proc.kill()
                    except Exception:
                        pass

            return StreamingResponse(stream_ffmpeg(), media_type="audio/mpeg")

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
            path = f"/tmp/{vid_id}.mp3"
            if not os.path.exists(path):
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
