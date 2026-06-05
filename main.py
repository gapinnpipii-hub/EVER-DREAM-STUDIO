from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yt_dlp, re, traceback

app = FastAPI(title="Ever Dream Studio API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

YDL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def fmt_duration(sec):
    if not sec:
        return "?"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

# ── Health ────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "Ever Dream Studio API", "version": "3.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ── Search ────────────────────────────────────────

@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=30)):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
        "http_headers": YDL_HEADERS,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)
        results = []
        for e in (info.get("entries") or []):
            if not e:
                continue
            vid_id = e.get("id", "")
            results.append({
                "id":         vid_id,
                "title":      e.get("title", "Unknown"),
                "channel":    e.get("uploader") or e.get("channel", ""),
                "duration":   fmt_duration(e.get("duration")),
                "duration_s": e.get("duration", 0),
                "thumbnail":  e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                "url":        f"https://www.youtube.com/watch?v={vid_id}",
                "view_count": e.get("view_count", 0),
            })
        return JSONResponse({"query": q, "count": len(results), "results": results})
    except Exception as ex:
        print(f"[SEARCH ERROR] {ex}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(ex))

# ── Stream URL (main endpoint) ────────────────────
# Returns direct audio stream URL from YouTube CDN
# Frontend fetches audio directly — no Railway bandwidth/timeout

@app.get("/stream-url")
def stream_url(url: str = Query(...)):
    """Extract direct audio stream URL from YouTube. Frontend fetches directly."""
    if not re.match(r"https?://", url):
        raise HTTPException(status_code=400, detail="URL tidak valid.")

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "http_headers": YDL_HEADERS,
        # prefer m4a/webm audio only formats
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Pick best audio format
        formats = info.get("formats", [])
        audio_formats = [
            f for f in formats
            if f.get("acodec") and f.get("acodec") != "none"
            and (not f.get("vcodec") or f.get("vcodec") == "none")
        ]
        # Sort by audio bitrate descending
        audio_formats.sort(key=lambda f: f.get("abr") or 0, reverse=True)

        if not audio_formats:
            # fallback: use requested format url
            stream = info.get("url")
            ext = info.get("ext", "webm")
        else:
            best = audio_formats[0]
            stream = best.get("url")
            ext = best.get("ext", "webm")

        if not stream:
            raise ValueError("Tidak ada stream URL yang ditemukan.")

        return JSONResponse({
            "title":      info.get("title", ""),
            "channel":    info.get("uploader", ""),
            "duration_s": info.get("duration", 0),
            "duration":   fmt_duration(info.get("duration")),
            "thumbnail":  info.get("thumbnail", ""),
            "stream_url": stream,
            "ext":        ext,
            "abr":        audio_formats[0].get("abr") if audio_formats else None,
        })
    except Exception as ex:
        print(f"[STREAM-URL ERROR] {ex}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(ex))

# ── Info ──────────────────────────────────────────

@app.get("/info")
def info(url: str = Query(...)):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "http_headers": YDL_HEADERS,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        return {
            "id":         data.get("id"),
            "title":      data.get("title"),
            "channel":    data.get("uploader"),
            "duration":   fmt_duration(data.get("duration")),
            "duration_s": data.get("duration", 0),
            "thumbnail":  data.get("thumbnail"),
        }
    except Exception as ex:
        print(f"[INFO ERROR] {ex}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(ex))
PYEOF
echo "Done"
