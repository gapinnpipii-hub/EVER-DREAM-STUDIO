from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp, os, re

app = FastAPI(title="Ever Dream Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────

def fmt_duration(sec):
    if not sec:
        return "?"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def is_url(text: str) -> bool:
    return bool(re.match(r"https?://", text.strip()))

# ─────────────────────────────────────────
#  Root — health check
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "Ever Dream Studio API", "version": "2.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ─────────────────────────────────────────
#  Search YouTube
#  GET /search?q=keyword&limit=10
# ─────────────────────────────────────────

@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=30)):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "default_search": "ytsearch",
        "playlist_items": f"1-{limit}",
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{q}", download=False)
        entries = info.get("entries", [])
        results = []
        for e in entries:
            if not e:
                continue
            results.append({
                "id":        e.get("id", ""),
                "title":     e.get("title", "Unknown"),
                "channel":   e.get("uploader") or e.get("channel", ""),
                "duration":  fmt_duration(e.get("duration")),
                "duration_s": e.get("duration", 0),
                "thumbnail": e.get("thumbnail", f"https://i.ytimg.com/vi/{e.get('id','')}/mqdefault.jpg"),
                "url":       e.get("url") or f"https://www.youtube.com/watch?v={e.get('id','')}",
                "view_count": e.get("view_count", 0),
            })
        return JSONResponse({"query": q, "count": len(results), "results": results})
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# ─────────────────────────────────────────
#  Info — metadata only (no download)
#  GET /info?url=https://youtu.be/xxx
# ─────────────────────────────────────────

@app.get("/info")
def info(url: str = Query(...)):
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return {
            "id":        info.get("id"),
            "title":     info.get("title"),
            "channel":   info.get("uploader"),
            "duration":  fmt_duration(info.get("duration")),
            "duration_s": info.get("duration", 0),
            "thumbnail": info.get("thumbnail"),
            "url":       url,
            "formats":   [
                {"format_id": f["format_id"], "ext": f["ext"], "abr": f.get("abr"), "vbr": f.get("vbr")}
                for f in info.get("formats", [])
                if f.get("acodec") != "none"
            ][-5:],  # last 5 audio formats
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# ─────────────────────────────────────────
#  Audio download — stream MP3
#  GET /audio?url=https://youtu.be/xxx&quality=128
# ─────────────────────────────────────────

@app.get("/audio")
def get_audio(
    url: str = Query(...),
    quality: int = Query(128, ge=64, le=320),
):
    if not is_url(url):
        raise HTTPException(status_code=400, detail="Parameter 'url' harus berupa URL YouTube yang valid.")

    tmp_dir = "/tmp"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{tmp_dir}/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": str(quality),
        }],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info["id"]
            title = info.get("title", video_id)

        path = f"{tmp_dir}/{video_id}.mp3"
        if not os.path.exists(path):
            raise HTTPException(status_code=500, detail="File audio tidak ditemukan setelah proses download.")

        safe_title = re.sub(r'[^\w\s\-]', '', title).strip().replace(' ', '_')[:60]

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
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_title}.mp3"',
                "X-Video-Title": title,
                "X-Video-ID": video_id,
            },
        )
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
