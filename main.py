from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re, traceback

app = FastAPI(title="Ever Dream Studio API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def fmt_duration(sec):
    if not sec:
        return "?"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def is_url(text: str) -> bool:
    return bool(re.match(r"https?://", text.strip()))

def get_ydl_opts_base():
    """Base yt-dlp options with anti-bot headers"""
    return {
        "quiet": True,
        "no_warnings": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
        # Use cookies workaround for age-restricted / bot-detected videos
        "extractor_args": {"youtube": {"skip": ["dash", "hls"]}},
    }

# ── Health ────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "Ever Dream Studio API", "version": "2.1.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ── Search ────────────────────────────────────────

@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=30)):
    opts = {
        **get_ydl_opts_base(),
        "extract_flat": "in_playlist",
        "default_search": "ytsearch",
        "playlist_items": f"1-{limit}",
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)
        entries = info.get("entries", [])
        results = []
        for e in entries:
            if not e:
                continue
            vid_id = e.get("id", "")
            results.append({
                "id":        vid_id,
                "title":     e.get("title", "Unknown"),
                "channel":   e.get("uploader") or e.get("channel", ""),
                "duration":  fmt_duration(e.get("duration")),
                "duration_s": e.get("duration", 0),
                "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg",
                "url":       e.get("url") or f"https://www.youtube.com/watch?v={vid_id}",
                "view_count": e.get("view_count", 0),
            })
        return JSONResponse({"query": q, "count": len(results), "results": results})
    except Exception as ex:
        tb = traceback.format_exc()
        print(f"[SEARCH ERROR] {ex}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(ex)}")

# ── Info ──────────────────────────────────────────

@app.get("/info")
def info(url: str = Query(...)):
    opts = {**get_ydl_opts_base(), "skip_download": True}
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
            "url":        url,
        }
    except Exception as ex:
        tb = traceback.format_exc()
        print(f"[INFO ERROR] {ex}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Info error: {str(ex)}")

# ── Audio download ────────────────────────────────

@app.get("/audio")
def get_audio(
    url: str = Query(...),
    quality: int = Query(128, ge=64, le=320),
):
    if not is_url(url):
        raise HTTPException(status_code=400, detail="URL tidak valid.")

    tmp_dir = "/tmp"

    # Try 1: with ffmpeg MP3 conversion
    try:
        return _download_mp3(url, quality, tmp_dir)
    except Exception as e1:
        print(f"[AUDIO MP3 FAIL] {e1}\n{traceback.format_exc()}")

    # Try 2: fallback — stream best audio without conversion (webm/m4a/ogg)
    try:
        return _download_raw(url, tmp_dir)
    except Exception as e2:
        print(f"[AUDIO RAW FAIL] {e2}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal download audio. MP3 error: {str(e1)} | Raw error: {str(e2)}"
        )


def _download_mp3(url, quality, tmp_dir):
    opts = {
        **get_ydl_opts_base(),
        "format": "bestaudio/best",
        "outtmpl": f"{tmp_dir}/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": str(quality),
        }],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        vid_id = info["id"]
        title  = info.get("title", vid_id)

    path = f"{tmp_dir}/{vid_id}.mp3"
    if not os.path.exists(path):
        raise FileNotFoundError(f"MP3 not found at {path}")

    safe = re.sub(r'[^\w\s\-]', '', title).strip().replace(' ', '_')[:60]
    return _stream_file(path, "audio/mpeg", f"{safe}.mp3", title, vid_id)


def _download_raw(url, tmp_dir):
    opts = {
        **get_ydl_opts_base(),
        "format": "bestaudio",
        "outtmpl": f"{tmp_dir}/%(id)s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        vid_id = info["id"]
        ext    = info.get("ext", "webm")
        title  = info.get("title", vid_id)

    path = f"{tmp_dir}/{vid_id}.{ext}"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw audio not found at {path}")

    mime_map = {"webm": "audio/webm", "m4a": "audio/mp4", "ogg": "audio/ogg", "opus": "audio/ogg"}
    mime = mime_map.get(ext, "audio/webm")
    safe = re.sub(r'[^\w\s\-]', '', title).strip().replace(' ', '_')[:60]
    return _stream_file(path, mime, f"{safe}.{ext}", title, vid_id)


def _stream_file(path, mime, filename, title, vid_id):
    def iterfile():
        try:
            with open(path, "rb") as f:
                yield from f
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    return StreamingResponse(
        iterfile(),
        media_type=mime,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Video-Title": title,
            "X-Video-ID": vid_id,
        },
    )
