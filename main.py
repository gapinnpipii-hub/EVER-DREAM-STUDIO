from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re, httpx, tempfile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── COOKIES (embedded langsung, tidak perlu file eksternal) ──
COOKIES_CONTENT = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1815167892	PREF	tz=Asia.Jakarta
.youtube.com	TRUE	/	TRUE	1815169177	LOGIN_INFO	AFmmF2swRQIhAL2Jkt8ozmZvr9r-9kwY4HVILJ1MTd2oxaP6UsRzz4EeAiBLakurMld7KyexDJQNWY4UoVivfrvmVeh4WKcyIHYcnQ:QUQ3MjNmemZTMXRFdkswYWtfektlbHVwaGdnQ1h2Zms0RDNyaHpJaXhSNk9jeE5Cdkd0d2ppRFlHcFc2cW1JeVFzbnN0THVXWXM5aDdsUmdIQjZtbER5Z2lOLUotNU0zVjBveHlFZnByeDhYb2plNG5XQ1NfeC0xZm5STXBCa0ZvYmZ0NEZPeld0a1ZFTEc3Njc3SXlKZ2FBQnMyYlRFc1hR
.youtube.com	TRUE	/	FALSE	1812164067	SIDCC	AKEyXzUKmaCFR8O6BwTSLdYtKSMGW3Qr9pYiCRDGrkJpk2PXbIjs9UbB7Mhkl9TtuQHR1QDpuw
.youtube.com	TRUE	/	TRUE	1812164067	__Secure-1PSIDCC	AKEyXzW9FsxS9UzaNXtKAwDPeIkXfxT-s1_VSbsgjsaUazl8FTWoeoZglZSQk1QSlF8qgFNHFQ
.youtube.com	TRUE	/	TRUE	1812164067	__Secure-3PSIDCC	AKEyXzX3nK_V7eTn9jZf3GaiGaTnSS5X4ajI17bcEGPnmj4md-uYcplsC3gDfseCk-S3CqpfiA
.youtube.com	TRUE	/	FALSE	1815189079	SID	g.a000-wicOB4uZjdqEKk9ybiakHgwCa1F3_Q7ICTxS_Hwk4aGj1cq9pceR2ksDvsg3lMK4-LwGAACgYKAZsSARQSFQHGX2MiQNTWnJ46NjtzwfAAchHj4BoVAUF8yKrD0OO15_-H9rFCCBJpqb7o0076
.youtube.com	TRUE	/	TRUE	1812165079	__Secure-1PSIDTS	sidts-CjUBhkeRd3UXr4QKy_pkKeaE6ltWqQ6akkWSFa0z2hLsPRAEoKzDzsetBSQJ6duXP2URRI-3KxAA
.youtube.com	TRUE	/	TRUE	1812165079	__Secure-3PSIDTS	sidts-CjUBhkeRd3UXr4QKy_pkKeaE6ltWqQ6akkWSFa0z2hLsPRAEoKzDzsetBSQJ6duXP2URRI-3KxAA
.youtube.com	TRUE	/	TRUE	1815189079	__Secure-1PSID	g.a000-wicOB4uZjdqEKk9ybiakHgwCa1F3_Q7ICTxS_Hwk4aGj1cq6rLEAgbz8Zcd07x-h52xlgACgYKAYESARQSFQHGX2MiLIpusdlQUR9AaH5Wa9oxeRoVAUF8yKoYKZq9fBmEjVThGs3sG4mX0076
.youtube.com	TRUE	/	TRUE	1815189079	__Secure-3PSID	g.a000-wicOB4uZjdqEKk9ybiakHgwCa1F3_Q7ICTxS_Hwk4aGj1cqWWYE3-gZyy93xnMiPTQPHwACgYKAfQSARQSFQHGX2MiJAWbmUJxhEIvJRq-iKA8kxoVAUF8yKqQ0q_lfvZj5gW9pJyaOIL-0076
.youtube.com	TRUE	/	FALSE	1815189079	HSID	A_wa0OMZlfOvjw6oI
.youtube.com	TRUE	/	TRUE	1815189079	SSID	Ay7ttDzd3cOCpRNV-
.youtube.com	TRUE	/	FALSE	1815189079	APISID	xJ7RFTOV1FyFez1i/AL4TUQghVBaqJsATK
.youtube.com	TRUE	/	TRUE	1815189079	SAPISID	VAMssWN6YEvWcwQw/AhrhkFcnykTS7s7Q1
.youtube.com	TRUE	/	TRUE	1815189079	__Secure-1PAPISID	VAMssWN6YEvWcwQw/AhrhkFcnykTS7s7Q1
.youtube.com	TRUE	/	TRUE	1815189079	__Secure-3PAPISID	VAMssWN6YEvWcwQw/AhrhkFcnykTS7s7Q1
.youtube.com	TRUE	/	TRUE	0	YSC	Wa2Jse90ZQg
.youtube.com	TRUE	/	TRUE	1796159890	VISITOR_INFO1_LIVE	iG7GALMB5Jc
.youtube.com	TRUE	/	TRUE	1796159890	VISITOR_PRIVACY_METADATA	CgJJRBIEGgAgDg%3D%3D
.youtube.com	TRUE	/	TRUE	1796158755	__Secure-YNID	19.YT=WRikCqWWdDXtB4fBBCSd7mWMYqxxXw9igikP234QQtS2eppKrLBVQlSWeDucLea252p0lEIsT1N1gL3PsXibHuDCPUSB5KkpuPrpoXRa4mqiBUaMx-UZDGWn7_FKYKCpjAr2mHui_JBJDEN8ivK8CG6WIWQsFY8CaHL34SzO2GwpIwbGUWwkKLkmV2bOfZxkLWv0AcuPEHCBv_PJBIhqhAPKL4UPyA3ipHbTQIrAYA7Ndu7bpaJ-vmCfya0TcMpEbPw-Z_XLYC_k6sEFsi1GU2N0V8W_SjLuiXFDXvgIik2SAAOv9nt0MuiZuFcj5qPPHbl2R-NsKdXkX-fTs3kPsw
.youtube.com	TRUE	/	TRUE	1796158755	__Secure-ROLLOUT_TOKEN	CM7y24jjuLX2VBDoupeJve6UAxjHuq2Jve6UAw%3D%3D
"""

# Tulis cookies ke file temporer saat startup
_COOKIE_FILE = None

def get_cookie_file():
    global _COOKIE_FILE
    if _COOKIE_FILE is None or not os.path.exists(_COOKIE_FILE):
        tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, prefix='yt_cookies_'
        )
        tmp.write(COOKIES_CONTENT)
        tmp.flush()
        tmp.close()
        _COOKIE_FILE = tmp.name
    return _COOKIE_FILE

def extract_video_id(url: str):
    m = re.search(r'(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})', url)
    return m.group(1) if m else None

def get_ydl_opts(extra={}):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': get_cookie_file(),
        'format': 'bestaudio/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'tv_embedded', 'ios'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }
    opts.update(extra)
    return opts

def pick_stream_url(info: dict) -> str:
    formats = info.get('formats') or []

    # Prioritas 1: audio only (opus/m4a/webm), ambil bitrate tertinggi
    audio_only = [
        f for f in formats
        if f.get('acodec') != 'none'
        and f.get('vcodec') in ('none', None)
        and f.get('url')
    ]
    if audio_only:
        # sort by abr (audio bitrate), ambil tertinggi
        audio_only.sort(key=lambda f: f.get('abr') or f.get('tbr') or 0)
        return audio_only[-1]['url']

    # Prioritas 2: format apapun yang punya audio
    with_audio = [
        f for f in formats
        if f.get('acodec') != 'none' and f.get('url')
    ]
    if with_audio:
        with_audio.sort(key=lambda f: f.get('abr') or f.get('tbr') or 0)
        return with_audio[-1]['url']

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
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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
