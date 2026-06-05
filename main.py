<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audio Processing — Ever Dream Studio by GAVINSKIE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<script src="https://cdn.jsdelivr.net/npm/lamejs@1.2.1/lame.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/soundtouchjs@0.1.30/dist/soundtouch.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest/dist/hls.min.js"></script>
<style>
:root {
  --bg:#0d0b1a;--bg2:#0f0d1e;--surface:#13111f;--card-solid:#171526;
  --border:rgba(255,255,255,0.06);--border2:rgba(255,255,255,0.12);
  --accent:#7864ff;--accent2:#b0aaff;--green:#1db954;--red:#ff4757;
  --text:#ffffff;--text2:rgba(255,255,255,0.55);--text3:rgba(255,255,255,0.2);
  --mono:'JetBrains Mono',monospace;--sans:'DM Sans',sans-serif;--display:'Syne',sans-serif;
  --player-h:84px;--sidebar-w:250px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:var(--sans);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.bg-layer{position:fixed;inset:0;z-index:0;pointer-events:none}
.bg-base{position:absolute;inset:0;background:#0d0b1a}
.bg-g1{position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 80% 10%,rgba(120,80,255,0.22) 0%,transparent 60%)}
.bg-g2{position:absolute;inset:0;background:radial-gradient(ellipse 60% 70% at 10% 90%,rgba(80,40,180,0.18) 0%,transparent 60%)}
.bg-g3{position:absolute;inset:0;background:radial-gradient(ellipse 50% 40% at 50% 50%,rgba(60,30,120,0.12) 0%,transparent 70%)}
.bg-g4{position:absolute;inset:0;background:radial-gradient(ellipse 35% 35% at 90% 80%,rgba(160,100,255,0.1) 0%,transparent 60%)}
.bg-mesh{position:absolute;inset:0;background-image:linear-gradient(rgba(140,120,255,0.05) 1px,transparent 1px),linear-gradient(90deg,rgba(140,120,255,0.05) 1px,transparent 1px);background-size:40px 40px;mask-image:radial-gradient(ellipse 90% 90% at 60% 40%,black 30%,transparent 80%)}
.bg-lines{position:absolute;inset:0;overflow:hidden;opacity:0.06}
.bg-lines svg{width:100%;height:100%}
.app{position:relative;z-index:1;display:grid;grid-template-columns:var(--sidebar-w) 1fr;grid-template-rows:1fr var(--player-h);height:100vh;overflow:hidden}
.sidebar{grid-row:1/2;background:rgba(10,8,22,0.75);border-right:1px solid rgba(255,255,255,0.07);display:flex;flex-direction:column;overflow:hidden;backdrop-filter:blur(16px)}
.sidebar-top{padding:22px 16px 18px;flex-shrink:0}
.logo-wrap{display:flex;align-items:center;gap:12px;margin-bottom:22px;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,0.04);border:1px solid rgba(232,201,106,0.18)}
.logo-box{width:44px;height:44px;border-radius:9px;background:rgba(14,12,28,0.9);border:1px solid rgba(232,201,106,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-family:Georgia,serif;font-size:13px;font-weight:700;color:#e8c96a;letter-spacing:.5px}
.logo-txt .name{font-size:13px;font-weight:700;color:#e8c96a;letter-spacing:-.01em;line-height:1.2}
.logo-txt .sub{font-size:10px;color:rgba(255,255,255,0.45);letter-spacing:.05em;font-family:var(--mono);margin-top:2px}
.nav{display:flex;flex-direction:column;gap:2px}
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 13px;border-radius:9px;cursor:pointer;font-size:13px;font-weight:500;color:var(--text2);transition:all .2s;border:none;background:none;width:100%;text-align:left}
.nav-item i{font-size:17px;flex-shrink:0}
.nav-item:hover{background:rgba(255,255,255,0.05);color:var(--text)}
.nav-item.active{background:rgba(120,100,255,0.18);color:#fff}
.nav-item.active i{color:var(--accent2)}
.sidebar-divider{height:1px;background:rgba(255,255,255,0.07);margin:12px 16px;flex-shrink:0}
.now-playing-side{padding:0 14px;flex:1;overflow:hidden;display:none;flex-direction:column;min-height:0}
.now-playing-side.visible{display:flex}
.nps-label{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:11px}
.nps-card{border-radius:12px;overflow:hidden;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08)}
.nps-art{width:100%;aspect-ratio:1;background:linear-gradient(135deg,#1a1640,#2e2860);display:flex;align-items:center;justify-content:center;font-size:40px;color:rgba(255,255,255,0.15);position:relative;overflow:hidden}
.nps-art img{width:100%;height:100%;object-fit:cover;position:absolute;inset:0}
.nps-meta{padding:12px 14px 13px}
.nps-title{font-size:12px;font-weight:600;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nps-artist{font-size:11px;color:rgba(255,255,255,0.5);margin-top:3px}
.sidebar-bottom{padding:12px 14px 16px;flex-shrink:0}
.sidebar-user{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07)}
.sidebar-avatar{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#b090ff);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;font-family:var(--display);flex-shrink:0}
.sidebar-uname{font-size:12px;font-weight:600;color:var(--text)}
.sidebar-urole{font-size:10px;font-family:var(--mono);color:var(--accent2);letter-spacing:.04em}
.main{grid-row:1/2;overflow:hidden;display:flex;flex-direction:column}
.topbar{display:flex;align-items:center;gap:12px;padding:18px 22px 12px;flex-shrink:0;position:relative;z-index:10}
.search-wrap{flex:1;position:relative;max-width:400px}
.search-input{width:100%;padding:10px 40px 10px 38px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:100px;color:var(--text);font-family:var(--sans);font-size:13px;font-weight:500;outline:none;transition:all .2s}
.search-input:focus{border-color:var(--accent);background:rgba(120,100,255,0.1);box-shadow:0 0 0 3px rgba(120,100,255,0.12)}
.search-input::placeholder{color:rgba(255,255,255,0.35)}
.search-icon-left{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:rgba(255,255,255,0.4);font-size:15px;pointer-events:none}
.search-clear{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;color:rgba(255,255,255,0.35);cursor:pointer;font-size:14px;display:none;padding:2px;transition:color .2s}
.search-clear:hover{color:var(--text)}
.search-clear.visible{display:block}
.status-badge{display:flex;align-items:center;gap:6px;padding:6px 13px;background:rgba(29,185,84,0.08);border:1px solid rgba(29,185,84,0.2);border-radius:100px;font-size:10px;font-weight:700;font-family:var(--mono);color:#1db954;letter-spacing:.06em;margin-left:auto}
.status-dot{width:5px;height:5px;border-radius:50%;background:#1db954;box-shadow:0 0 5px #1db954;animation:pulse 2s ease-in-out infinite}
.panel{display:none;flex:1;overflow:hidden}
.panel.active{display:flex;flex-direction:column}
.search-hero{padding:0 22px 14px;flex-shrink:0}
.search-hero h1{font-family:var(--display);font-size:24px;font-weight:800;letter-spacing:-.02em;margin-bottom:3px}
.search-hero p{font-size:12px;color:var(--text2)}
.source-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;background:rgba(255,0,0,0.08);border:1px solid rgba(255,0,0,0.18);border-radius:100px;font-size:10px;font-weight:700;font-family:var(--mono);color:rgba(255,140,140,0.95);letter-spacing:.06em;margin-top:7px;width:fit-content}
.results-area{flex:1;overflow-y:auto;padding:0 22px 20px;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,0.08) transparent}
.results-area::-webkit-scrollbar{width:3px}
.results-area::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:2px}
.list-hd{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;padding:0 2px}
.list-hd span{font-size:10px;font-family:var(--mono);color:rgba(255,255,255,0.4);letter-spacing:.08em;text-transform:uppercase}
.track-row{display:grid;grid-template-columns:32px 48px 1fr auto;align-items:center;gap:12px;padding:7px 10px;border-radius:10px;cursor:pointer;border:1px solid transparent;margin-bottom:2px;transition:background .15s;position:relative}
.track-row:hover{background:rgba(255,255,255,0.04)}
.track-row.playing{background:rgba(120,100,255,0.1);border-color:rgba(120,100,255,0.22)}
.track-num{font-family:var(--mono);font-size:12px;color:rgba(255,255,255,0.4);text-align:center;transition:opacity .15s}
.track-row:hover .track-num,.track-row.playing .track-num{opacity:0}
.track-play-icon{position:absolute;left:16px;font-size:14px;color:var(--text2);opacity:0;transition:opacity .15s}
.track-row.playing .track-play-icon{color:var(--accent2)}
.track-row:hover .track-play-icon,.track-row.playing .track-play-icon{opacity:1}
.track-thumb{width:42px;height:42px;border-radius:8px;flex-shrink:0;background:var(--card-solid);display:flex;align-items:center;justify-content:center;font-size:18px;color:rgba(255,255,255,0.2);position:relative;overflow:hidden}
.track-thumb img{width:100%;height:100%;object-fit:cover;position:absolute;inset:0}
.track-info{min-width:0}
.track-title{font-size:13px;font-weight:600;color:#f0f0fa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:-.01em;margin-bottom:2px}
.track-row.playing .track-title{color:var(--accent2)}
.track-artist{font-size:11px;color:var(--text2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.track-right{display:flex;align-items:center;gap:7px}
.track-dur{font-family:var(--mono);font-size:11px;color:rgba(255,255,255,0.45);white-space:nowrap}
.btn-process{display:flex;align-items:center;gap:4px;padding:5px 11px;border-radius:100px;background:rgba(120,100,255,0.14);border:1px solid rgba(120,100,255,0.28);color:var(--accent2);font-size:11px;font-weight:600;cursor:pointer;white-space:nowrap;font-family:var(--sans);transition:all .2s}
.btn-process:hover{background:rgba(120,100,255,0.28);border-color:rgba(120,100,255,0.5);color:#fff}
.btn-process.loading{opacity:.6;pointer-events:none}
@keyframes spin{to{transform:rotate(360deg)}}
.spin{display:inline-block;animation:spin .7s linear infinite}
.empty-state{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:40px;text-align:center}
.empty-icon{width:70px;height:70px;background:rgba(255,255,255,0.04);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;color:var(--text3);margin-bottom:4px}
.empty-state h3{font-family:var(--display);font-size:18px;font-weight:700}
.empty-state p{font-size:13px;color:var(--text2);line-height:1.6}
.skel{background:linear-gradient(90deg,rgba(255,255,255,0.04) 25%,rgba(255,255,255,0.08) 50%,rgba(255,255,255,0.04) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:4px}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
#panel-upload{overflow-y:auto;padding:0 22px 20px;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,0.08) transparent}
#panel-upload::-webkit-scrollbar{width:3px}
#panel-upload::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:2px}
.upload-hero{margin-bottom:16px;flex-shrink:0}
.upload-hero h1{font-family:var(--display);font-size:24px;font-weight:800;letter-spacing:-.02em;margin-bottom:3px}
.upload-hero p{font-size:12px;color:var(--text2)}
.from-search-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;background:rgba(120,100,255,0.1);border:1px solid rgba(120,100,255,0.25);border-radius:100px;font-size:10px;font-weight:700;font-family:var(--mono);color:var(--accent2);letter-spacing:.06em;margin-top:6px;width:fit-content}
.dropzone{border:2px dashed rgba(120,100,255,0.3);border-radius:14px;padding:32px 20px;text-align:center;cursor:pointer;transition:all .25s;background:rgba(120,100,255,0.03);margin-bottom:16px;flex-shrink:0;position:relative;overflow:hidden}
.dropzone:hover,.dropzone.drag{border-color:var(--accent);background:rgba(120,100,255,0.08)}
.dropzone-icon{width:56px;height:56px;margin:0 auto 14px;background:rgba(120,100,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;color:var(--accent2)}
.dropzone h3{font-family:var(--display);font-size:16px;font-weight:700;margin-bottom:5px}
.dropzone p{font-size:12px;color:var(--text2);margin-bottom:5px}
.dropzone small{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.06em}
.fetch-overlay{position:absolute;inset:0;background:rgba(13,11,26,0.88);display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;border-radius:12px}
.fetch-overlay.show{display:flex}
.fetch-title{font-family:var(--display);font-size:14px;font-weight:700;color:var(--accent2);text-align:center;padding:0 16px}
.fetch-sub{font-size:11px;font-family:var(--mono);color:var(--text3)}
.selected-file{display:none;align-items:center;gap:12px;padding:12px 16px;background:rgba(120,100,255,0.08);border:1.5px solid rgba(120,100,255,0.2);border-radius:12px;margin-bottom:14px}
.selected-file.show{display:flex}
.sf-icon{width:40px;height:40px;background:rgba(120,100,255,0.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;color:var(--accent2);flex-shrink:0}
.sf-info{flex:1;min-width:0}
.sf-name{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:2px}
.sf-meta{font-size:10px;font-family:var(--mono);color:var(--text3)}
.btn-clear-file{background:none;border:none;color:var(--text3);cursor:pointer;font-size:17px;padding:5px;border-radius:50%;transition:all .2s;display:flex;align-items:center;justify-content:center}
.btn-clear-file:hover{color:var(--red);background:rgba(255,71,87,0.1)}
.wave-wrap{background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:12px;padding:12px;margin-bottom:14px}
canvas{width:100%;height:56px;display:block;border-radius:6px}
.chips{display:none;gap:10px;margin-bottom:14px}
.chips.show{display:flex}
.chip{flex:1;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:10px;padding:10px 12px}
.chip-lbl{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px}
.chip-val{font-size:15px;font-weight:800;font-family:var(--mono)}
.section-label{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.1em;text-transform:uppercase;display:flex;align-items:center;gap:12px;margin-bottom:12px;margin-top:16px}
.section-label::after{content:'';flex:1;height:1px;background:var(--border)}
.controls-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}
.ctrl-card{background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:12px;padding:14px}
.ctrl-card.full{grid-column:1/-1}
.ctrl-lbl{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between}
.ctrl-val{font-size:22px;font-weight:900;font-family:var(--display);margin-bottom:10px;line-height:1}
input[type=range]{width:100%;-webkit-appearance:none;height:3px;border-radius:2px;background:rgba(255,255,255,0.1);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:#fff;border:none;box-shadow:0 2px 6px rgba(0,0,0,0.5);cursor:pointer;transition:transform .15s}
input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.3)}
.range-labels{display:flex;justify-content:space-between;font-size:10px;font-family:var(--mono);color:var(--text3);margin-top:5px}
input[type=number]{width:100%;padding:6px 10px;background:rgba(255,255,255,0.05);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:var(--mono);font-size:12px;font-weight:600;outline:none;text-align:center;transition:border-color .2s;margin-top:5px}
input[type=number]:focus{border-color:var(--accent)}
.fmt-pills{display:flex;gap:6px;margin-bottom:8px}
.fmt-pill{flex:1;padding:7px;font-family:var(--sans);font-size:11px;font-weight:700;cursor:pointer;border-radius:100px;border:1px solid var(--border);background:transparent;color:var(--text2);transition:all .2s}
.fmt-pill.active{background:#fff;border-color:#fff;color:#000}
select{width:100%;padding:7px 10px;background:rgba(255,255,255,0.05);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:var(--mono);font-size:12px;outline:none;cursor:pointer}
.prog-wrap{height:2px;background:rgba(255,255,255,0.07);border-radius:100px;overflow:hidden;display:none;margin-bottom:8px}
.prog-bar{height:100%;width:0%;background:linear-gradient(90deg,var(--accent),#a78bfa);border-radius:100px;transition:width .3s}
.status-txt{font-family:var(--mono);font-size:11px;color:var(--text3);text-align:center;margin-bottom:12px;min-height:14px}
.btn-main{width:100%;padding:14px;background:linear-gradient(135deg,var(--accent),#a78bfa);border:none;border-radius:12px;color:#fff;font-family:var(--display);font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:9px;transition:all .2s;box-shadow:0 6px 24px rgba(120,100,255,0.3)}
.btn-main:hover{transform:translateY(-1px);box-shadow:0 10px 32px rgba(120,100,255,0.4)}
.btn-main:active{transform:translateY(0)}
.btn-main:disabled{opacity:.3;cursor:not-allowed;transform:none;box-shadow:none}
.out-section{margin-top:16px;display:none}
.out-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.out-card{border-radius:12px;padding:14px;border:1px solid}
.out-a{background:rgba(120,100,255,0.05);border-color:rgba(120,100,255,0.2)}
.out-b{background:rgba(29,185,84,0.05);border-color:rgba(29,185,84,0.2)}
.out-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 8px;border-radius:100px;font-size:10px;font-weight:700;font-family:var(--mono);letter-spacing:.06em;margin-bottom:8px}
.out-a .out-badge{background:rgba(120,100,255,0.15);color:var(--accent2)}
.out-b .out-badge{background:rgba(29,185,84,0.15);color:#1db954}
.out-title{font-size:12px;font-weight:700;margin-bottom:2px}
.out-sub{font-size:10px;font-family:var(--mono);color:var(--text3);margin-bottom:10px}
audio{width:100%;border-radius:6px;margin-bottom:6px;height:30px;accent-color:var(--accent)}
.out-info{font-family:var(--mono);font-size:10px;color:var(--text3);margin-bottom:8px}
.btn-dl{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;padding:8px;border-radius:8px;font-family:var(--sans);font-size:12px;font-weight:700;cursor:pointer;border:1px solid;text-decoration:none;transition:all .2s}
.btn-dl-a{background:rgba(120,100,255,0.1);border-color:rgba(120,100,255,0.3);color:var(--accent2)}
.btn-dl-a:hover{background:rgba(120,100,255,0.2)}
.btn-dl-b{background:rgba(29,185,84,0.1);border-color:rgba(29,185,84,0.3);color:#1db954}
.btn-dl-b:hover{background:rgba(29,185,84,0.2)}
.footer-panel{overflow-y:auto;padding:0 22px 20px;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,0.08) transparent}
.footer-panel::-webkit-scrollbar{width:3px}
.footer-panel::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:2px}
.footer-hero{margin-bottom:20px}
.footer-hero h1{font-family:var(--display);font-size:24px;font-weight:800;letter-spacing:-.02em;margin-bottom:3px}
.footer-hero p{font-size:12px;color:var(--text2)}
.jasa-card{background:rgba(120,100,255,0.05);border:1px solid rgba(120,100,255,0.15);border-radius:14px;padding:20px;margin-bottom:14px}
.jasa-title{font-family:var(--display);font-size:14px;font-weight:800;color:var(--accent2);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.jasa-list{display:flex;flex-direction:column;gap:7px}
.jasa-item{display:flex;align-items:center;gap:9px;font-size:13px;color:var(--text2)}
.jasa-item::before{content:'●';color:var(--accent2);font-size:7px;flex-shrink:0}
.divider-line{height:1px;background:var(--border);margin:18px 0}
.kontak-title{font-family:var(--display);font-size:14px;font-weight:800;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.kontak-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.kontak-card{display:flex;align-items:center;gap:12px;padding:14px 16px;border-radius:12px;border:1px solid var(--border);background:rgba(255,255,255,0.03);text-decoration:none;transition:all .2s;cursor:pointer}
.kontak-card:hover{border-color:var(--border2);background:rgba(255,255,255,0.06);transform:translateY(-2px)}
.kontak-icon{width:38px;height:38px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.k-discord .kontak-icon{background:rgba(88,101,242,0.15);color:#5865f2}
.k-tiktok .kontak-icon{background:rgba(255,0,80,0.1);color:#ff0050}
.k-wa .kontak-icon{background:rgba(37,211,102,0.1);color:#25d366}
.k-yt .kontak-icon{background:rgba(255,0,0,0.1);color:#ff0000}
.kontak-info{min-width:0}
.kontak-platform{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px}
.kontak-handle{font-size:13px;font-weight:700;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.server-card{display:flex;align-items:center;gap:12px;padding:16px 18px;border-radius:12px;background:rgba(88,101,242,0.08);border:1px solid rgba(88,101,242,0.2);text-decoration:none;transition:all .2s;margin-top:10px}
.server-card:hover{border-color:rgba(88,101,242,0.4);transform:translateY(-2px)}
.server-card-icon{width:44px;height:44px;background:rgba(88,101,242,0.2);border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:22px;color:#5865f2;flex-shrink:0}
.server-card-info{flex:1;min-width:0}
.server-card-label{font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px}
.server-card-name{font-family:var(--display);font-size:14px;font-weight:800;color:var(--text)}
.server-card-arrow{color:var(--text3);font-size:17px}
.player{grid-column:1/-1;grid-row:2/3;background:rgba(10,8,22,0.88);border-top:1px solid rgba(255,255,255,0.07);backdrop-filter:blur(16px);display:grid;grid-template-columns:1fr 2fr 1fr;align-items:center;padding:0 22px;gap:12px}
.player-track{display:flex;align-items:center;gap:11px;min-width:0}
.player-thumb{width:40px;height:40px;border-radius:7px;background:rgba(120,100,255,0.15);flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:17px;color:rgba(255,255,255,0.2);overflow:hidden}
.player-thumb img{width:100%;height:100%;object-fit:cover}
.player-info{min-width:0}
.player-title{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:2px}
.player-artist{font-size:11px;color:var(--text2)}
.player-eq{display:flex;align-items:flex-end;gap:2px;height:14px;margin-left:7px;flex-shrink:0}
.player-eq-b{width:3px;border-radius:1px;background:var(--accent2)}
.player-controls{display:flex;flex-direction:column;align-items:center;gap:7px}
.player-btns{display:flex;align-items:center;gap:16px}
.player-btn{background:none;border:none;color:rgba(255,255,255,0.45);cursor:pointer;font-size:18px;padding:3px;transition:all .15s;display:flex;align-items:center;justify-content:center;border-radius:50%}
.player-btn:hover{color:#fff}
.player-btn.play{width:34px;height:34px;background:#fff;color:#0c0a20;border-radius:50%;font-size:15px}
.player-btn.play:hover{transform:scale(1.06)}
.player-progress{display:flex;align-items:center;gap:9px;width:100%}
.player-time{font-family:var(--mono);font-size:10px;color:rgba(255,255,255,0.45);white-space:nowrap;min-width:30px}
.player-bar{flex:1;height:2px;background:rgba(255,255,255,0.1);border-radius:100px;cursor:pointer;position:relative}
.player-bar-fill{height:100%;width:0%;background:var(--accent2);border-radius:100px;transition:width .1s linear;pointer-events:none}
.player-right{display:flex;align-items:center;justify-content:flex-end;gap:9px}
.vol-wrap{display:flex;align-items:center;gap:8px}
.vol-icon{color:rgba(255,255,255,0.4);font-size:15px}
.vol-slider{width:70px}
.toast{position:fixed;bottom:calc(var(--player-h) + 16px);left:50%;transform:translateX(-50%) translateY(20px);background:var(--card-solid);border:1px solid var(--border2);border-radius:100px;padding:10px 20px;font-size:12px;font-weight:600;box-shadow:0 10px 32px rgba(0,0,0,0.5);transition:all .35s cubic-bezier(.16,1,.3,1);z-index:9999;opacity:0;pointer-events:none;white-space:nowrap}
.toast.show{transform:translateX(-50%) translateY(0);opacity:1}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.85)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.fade-up{animation:fadeUp .3s cubic-bezier(.16,1,.3,1) both}
</style>
</head>
<body>

<div class="bg-layer">
  <div class="bg-base"></div><div class="bg-g1"></div><div class="bg-g2"></div>
  <div class="bg-g3"></div><div class="bg-g4"></div><div class="bg-mesh"></div>
  <div class="bg-lines">
    <svg viewBox="0 0 1200 768" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <circle cx="900" cy="120" r="280" fill="none" stroke="rgba(160,130,255,0.5)" stroke-width="0.5"/>
      <circle cx="900" cy="120" r="420" fill="none" stroke="rgba(160,130,255,0.3)" stroke-width="0.5"/>
      <circle cx="900" cy="120" r="560" fill="none" stroke="rgba(160,130,255,0.2)" stroke-width="0.5"/>
      <circle cx="120" cy="650" r="200" fill="none" stroke="rgba(120,100,255,0.4)" stroke-width="0.5"/>
      <circle cx="120" cy="650" r="320" fill="none" stroke="rgba(120,100,255,0.25)" stroke-width="0.5"/>
      <line x1="0" y1="280" x2="1200" y2="520" stroke="rgba(180,150,255,0.07)" stroke-width="1"/>
      <line x1="0" y1="460" x2="1200" y2="200" stroke="rgba(180,150,255,0.05)" stroke-width="1"/>
      <line x1="300" y1="0" x2="800" y2="768" stroke="rgba(180,150,255,0.05)" stroke-width="1"/>
    </svg>
  </div>
</div>

<div class="app">
  <aside class="sidebar">
    <div class="sidebar-top">
      <div class="logo-wrap">
        <div class="logo-box">EDS</div>
        <div class="logo-txt">
          <div class="name">Ever Dream Studio</div>
          <div class="sub">Audio Processing</div>
        </div>
      </div>
      <nav class="nav">
        <button class="nav-item active" onclick="switchTab('search')"><i class="ti ti-search"></i> Cari Musik</button>
        <button class="nav-item" onclick="switchTab('upload')"><i class="ti ti-upload"></i> Upload & Convert</button>
        <button class="nav-item" onclick="switchTab('info')"><i class="ti ti-info-circle"></i> Info & Kontak</button>
      </nav>
    </div>
    <div class="sidebar-divider"></div>
    <div class="now-playing-side" id="npSide">
      <div class="nps-label">Now Playing</div>
      <div class="nps-card">
        <div class="nps-art" id="npArt"><i class="ti ti-music"></i></div>
        <div class="nps-meta">
          <div class="nps-title" id="npSideTitle">—</div>
          <div class="nps-artist" id="npSideArtist">—</div>
        </div>
      </div>
    </div>
    <div style="flex:1"></div>
    <div class="sidebar-bottom">
      <div class="sidebar-user">
        <div class="sidebar-avatar">G</div>
        <div><div class="sidebar-uname">GAVINSKIE</div><div class="sidebar-urole">CREATOR</div></div>
      </div>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="search-wrap" id="searchWrap">
        <i class="ti ti-search search-icon-left"></i>
        <input class="search-input" id="searchInput" type="text"
          placeholder="Cari lagu, artis di SoundCloud..."
          onkeydown="if(event.key==='Enter')doSearch()"
          oninput="toggleClear()">
        <button class="search-clear" id="searchClear" onclick="clearSearch()"><i class="ti ti-x"></i></button>
      </div>
      <div class="status-badge"><span class="status-dot"></span> Online</div>
    </div>

    <!-- SEARCH PANEL -->
    <div class="panel active" id="panel-search">
      <div class="search-hero">
        <h1 id="searchHeading">Temukan Musik</h1>
        <p id="searchSub">Cari lagu lalu process langsung ke converter</p>
        <div class="source-badge"><i class="ti ti-brand-soundcloud" style="font-size:10px"></i> SoundCloud Search</div>
      </div>
      <div class="results-area" id="resultsArea">
        <div class="empty-state">
          <div class="empty-icon"><i class="ti ti-music-search"></i></div>
          <h3>Mulai Pencarian</h3>
          <p>Ketik judul lagu atau nama artis<br>di kolom pencarian di atas</p>
        </div>
      </div>
    </div>

    <!-- UPLOAD PANEL -->
    <div class="panel" id="panel-upload">
      <div class="upload-hero">
        <h1 id="uploadHeroTitle">Upload & Convert</h1>
        <p id="uploadHeroSub">Upload file audio atau video, convert ke MP3 dengan efek profesional</p>
        <div class="from-search-badge" id="fromSearchBadge" style="display:none">
          <i class="ti ti-brand-soundcloud" style="font-size:10px"></i>
          <span id="fromSearchLabel">Dari SoundCloud</span>
        </div>
      </div>
      <div class="dropzone" id="dropZone" onclick="document.getElementById('fileIn').click()">
        <div class="dropzone-icon"><i class="ti ti-file-music"></i></div>
        <h3 id="dropLabel">Seret atau klik untuk upload</h3>
        <p>Pilih file dari perangkat kamu</p>
        <small>MP3 · MP4 · WAV · OGG · M4A · FLAC · WEBM</small>
        <div class="fetch-overlay" id="fetchOverlay">
          <i class="ti ti-cloud-download spin" style="font-size:28px;color:var(--accent2)"></i>
          <div class="fetch-title" id="fetchTitle">Mengambil audio...</div>
          <div class="fetch-sub" id="fetchSub">Mohon tunggu sebentar</div>
        </div>
      </div>
      <input type="file" id="fileIn" accept="audio/*,video/mp4,video/webm" style="display:none">
      <div class="selected-file" id="selectedFile">
        <div class="sf-icon"><i class="ti ti-file-music"></i></div>
        <div class="sf-info">
          <div class="sf-name" id="sfName">—</div>
          <div class="sf-meta" id="sfMeta">—</div>
        </div>
        <button class="btn-clear-file" onclick="clearFile()"><i class="ti ti-x"></i></button>
      </div>
      <div class="wave-wrap"><canvas id="waveCanvas"></canvas></div>
      <div class="chips" id="infoChips">
        <div class="chip"><div class="chip-lbl">Durasi Asli</div><div class="chip-val" id="chipDur">—</div></div>
        <div class="chip"><div class="chip-lbl">Output A</div><div class="chip-val" id="chipOut">—</div></div>
        <div class="chip"><div class="chip-lbl">Playback ×</div><div class="chip-val" id="chipInv">—</div></div>
      </div>
      <div class="section-label">Controls</div>
      <div class="controls-grid">
        <div class="ctrl-card">
          <div class="ctrl-lbl"><span>Kecepatan</span><i class="ti ti-player-fast-forward" style="color:var(--accent2)"></i></div>
          <div class="ctrl-val" id="speedVal">2.30×</div>
          <input type="range" id="speedRange" min="0.2" max="3" step="0.01" value="2.3">
          <div class="range-labels"><span>0.2×</span><span>3×</span></div>
          <input type="number" id="speedNum" min="0.1" max="10" step="0.01" value="2.3">
        </div>
        <div class="ctrl-card">
          <div class="ctrl-lbl"><span>Amplifikasi</span><i class="ti ti-wave-square" style="color:#a78bfa"></i></div>
          <div class="ctrl-val" id="dbVal">0.0 dB</div>
          <input type="range" id="dbRange" min="-20" max="20" step="0.5" value="0">
          <div class="range-labels"><span>-20dB</span><span>+20dB</span></div>
          <input type="number" id="dbNum" min="-40" max="40" step="0.5" value="0">
        </div>
        <div class="ctrl-card">
          <div class="ctrl-lbl"><span>Durasi Maks</span><i class="ti ti-clock" style="color:#f59e0b"></i></div>
          <div class="ctrl-val" id="durVal">400s</div>
          <input type="range" id="durRange" min="10" max="600" step="5" value="400">
          <div class="range-labels"><span>10s</span><span>600s</span></div>
          <input type="number" id="durNum" min="1" max="3600" step="1" value="400">
        </div>
        <div class="ctrl-card">
          <div class="ctrl-lbl"><span>Format Output</span><i class="ti ti-file-music" style="color:#f97316"></i></div>
          <div class="fmt-pills">
            <button class="fmt-pill active" id="fmtMp3" onclick="setFmt('mp3')">MP3</button>
            <button class="fmt-pill" id="fmtWav" onclick="setFmt('wav')">WAV</button>
          </div>
          <div id="mp3Opts">
            <select id="bitrateSelect">
              <option value="64">64 kbps</option>
              <option value="128" selected>128 kbps</option>
              <option value="192">192 kbps</option>
              <option value="320">320 kbps — Best</option>
            </select>
          </div>
        </div>
      </div>
      <div class="prog-wrap" id="progWrap"><div class="prog-bar" id="progBar"></div></div>
      <p class="status-txt" id="statusTxt">Upload file untuk mulai</p>
      <button class="btn-main" id="processBtn" disabled><i class="ti ti-sparkles"></i> Proses Kedua Output</button>
      <div class="out-section" id="outSection">
        <div class="section-label">Hasil</div>
        <div class="out-grid">
          <div class="out-card out-a">
            <div class="out-badge"><i class="ti ti-player-fast-forward" style="font-size:9px"></i> OUTPUT A</div>
            <div class="out-title">Speed + EQ + Compressor</div>
            <div class="out-sub">Speed <span id="labelSpeedA">2.30×</span> · Normalized</div>
            <audio id="previewA" controls></audio>
            <p class="out-info" id="infoA"></p>
            <a id="dlA"><button class="btn-dl btn-dl-a" type="button"><i class="ti ti-download"></i> Download A</button></a>
          </div>
          <div class="out-card out-b">
            <div class="out-badge"><i class="ti ti-music" style="font-size:9px"></i> OUTPUT B</div>
            <div class="out-title">Durasi Asli + EQ</div>
            <div class="out-sub">Original · Normalized</div>
            <audio id="previewB" controls></audio>
            <p class="out-info" id="infoB"></p>
            <a id="dlB"><button class="btn-dl btn-dl-b" type="button"><i class="ti ti-download"></i> Download B</button></a>
          </div>
        </div>
      </div>
    </div>

    <!-- INFO PANEL -->
    <div class="panel footer-panel" id="panel-info">
      <div class="footer-hero"><h1>Info & Kontak</h1><p>Jasa pembuatan aset Roblox Studio & kontak person</p></div>
      <div class="jasa-card">
        <div class="jasa-title"><i class="ti ti-briefcase"></i> Menyediakan Jasa</div>
        <div class="jasa-list">
          <div class="jasa-item">Pembuatan Map</div><div class="jasa-item">Pembuatan Script</div>
          <div class="jasa-item">Perbaikan Map</div><div class="jasa-item">Perbaikan Bug</div>
          <div class="jasa-item">Pembuatan Server Discord</div><div class="jasa-item">Dan lain-lain</div>
        </div>
      </div>
      <div class="divider-line"></div>
      <div class="kontak-title"><i class="ti ti-address-book"></i> Kontak Person</div>
      <div class="kontak-grid">
        <a class="kontak-card k-discord" href="https://discord.com/users/gav1nskie" target="_blank"><div class="kontak-icon"><i class="ti ti-brand-discord"></i></div><div class="kontak-info"><div class="kontak-platform">Discord</div><div class="kontak-handle">@gav1nskie</div></div></a>
        <a class="kontak-card k-tiktok" href="https://tiktok.com/@namelesserr0r" target="_blank"><div class="kontak-icon"><i class="ti ti-brand-tiktok"></i></div><div class="kontak-info"><div class="kontak-platform">TikTok</div><div class="kontak-handle">@namelesserr0r</div></div></a>
        <a class="kontak-card k-wa" href="https://wa.me/6281282664158" target="_blank"><div class="kontak-icon"><i class="ti ti-brand-whatsapp"></i></div><div class="kontak-info"><div class="kontak-platform">WhatsApp</div><div class="kontak-handle">+62 812-8266-4158</div></div></a>
        <a class="kontak-card k-yt" href="https://youtube.com/@namelesserr0r" target="_blank"><div class="kontak-icon"><i class="ti ti-brand-youtube"></i></div><div class="kontak-info"><div class="kontak-platform">YouTube</div><div class="kontak-handle">@namelesserr0r</div></div></a>
      </div>
      <a class="server-card" href="https://discord.gg/7jSsJv7Haj" target="_blank">
        <div class="server-card-icon"><i class="ti ti-brand-discord"></i></div>
        <div class="server-card-info"><div class="server-card-label">Discord Server</div><div class="server-card-name">Ever Dream Studio</div></div>
        <i class="ti ti-arrow-right server-card-arrow"></i>
      </a>
    </div>
  </main>

  <div class="player">
    <div class="player-track">
      <div class="player-thumb" id="playerThumb"><i class="ti ti-music"></i></div>
      <div class="player-info">
        <div class="player-title" id="playerTitle">Tidak ada yang diputar</div>
        <div class="player-artist" id="playerArtist">—</div>
      </div>
      <div class="player-eq" id="playerEq" style="display:none">
        <div class="player-eq-b" id="pe1" style="height:5px"></div>
        <div class="player-eq-b" id="pe2" style="height:11px"></div>
        <div class="player-eq-b" id="pe3" style="height:7px"></div>
        <div class="player-eq-b" id="pe4" style="height:13px"></div>
        <div class="player-eq-b" id="pe5" style="height:6px"></div>
        <div class="player-eq-b" id="pe6" style="height:9px"></div>
        <div class="player-eq-b" id="pe7" style="height:4px"></div>
      </div>
    </div>
    <div class="player-controls">
      <div class="player-btns">
        <button class="player-btn" onclick="playPrev()"><i class="ti ti-player-skip-back"></i></button>
        <button class="player-btn play" id="btnPlay" onclick="togglePlay()"><i class="ti ti-player-play" id="playIcon"></i></button>
        <button class="player-btn" onclick="playNext()"><i class="ti ti-player-skip-forward"></i></button>
      </div>
      <div class="player-progress">
        <span class="player-time" id="timeCur">0:00</span>
        <div class="player-bar" id="playerBarEl" onclick="seekTo(event)"><div class="player-bar-fill" id="playerFill"></div></div>
        <span class="player-time" id="timeDur">0:00</span>
      </div>
    </div>
    <div class="player-right">
      <div class="vol-wrap">
        <i class="ti ti-volume vol-icon"></i>
        <input type="range" class="vol-slider" id="volSlider" min="0" max="1" step="0.01" value="1" oninput="setVol(this.value)">
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const API = 'https://web-production-3ff2c.up.railway.app';
const $ = id => document.getElementById(id);

// ── STATE ──────────────────────────────────────────────────────────────────
let audioEl = new Audio();
audioEl.crossOrigin = 'anonymous';
let hlsInstance = null;
let currentTrack = null;
let trackList = [];
let currentIdx = -1;
let audioBuffer = null;
let fmt = 'mp3';
// Flag: sedang dalam proses ganti source, jangan proses error event
let isChangingSrc = false;

// ── EQ BARS ANIMATION ─────────────────────────────────────────────────────
const eqIds = ['pe1','pe2','pe3','pe4','pe5','pe6','pe7'];
const eqTgt = {}, eqCur = {};
eqIds.forEach(id => { eqTgt[id] = 2 + Math.random()*13; eqCur[id] = 2 + Math.random()*13; });
setInterval(() => eqIds.forEach(id => { eqTgt[id] = 2 + Math.random()*13; }), 280);
(function eqAnim() {
  eqIds.forEach(id => {
    const el = $(id); if (!el) return;
    eqCur[id] += (eqTgt[id] - eqCur[id]) * 0.18;
    el.style.height = Math.round(eqCur[id]) + 'px';
  });
  requestAnimationFrame(eqAnim);
})();

// ── TABS ──────────────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.nav-item').forEach((el, i) => {
    el.classList.toggle('active', ['search','upload','info'][i] === name);
  });
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  $('panel-' + name).classList.add('active');
  $('searchWrap').style.display = name === 'search' ? 'block' : 'none';
}
$('searchWrap').style.display = 'block';

// ── TOAST ─────────────────────────────────────────────────────────────────
let toastTimer;
function toast(msg, dur = 3000) {
  const el = $('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), dur);
}

// ── SEARCH ────────────────────────────────────────────────────────────────
function toggleClear() {
  $('searchClear').classList.toggle('visible', $('searchInput').value.length > 0);
}
function clearSearch() {
  $('searchInput').value = '';
  $('searchClear').classList.remove('visible');
  $('searchInput').focus();
}

async function doSearch() {
  const q = $('searchInput').value.trim();
  if (!q) return;
  $('searchHeading').textContent = `"${q}"`;
  $('searchSub').textContent = 'Mencari di SoundCloud...';
  $('resultsArea').innerHTML = [1,2,3,4,5].map(() => `
    <div style="display:grid;grid-template-columns:32px 48px 1fr auto;align-items:center;gap:12px;padding:7px 10px;border-radius:10px;margin-bottom:2px">
      <div class="skel" style="height:12px;width:18px;margin:auto"></div>
      <div class="skel" style="width:42px;height:42px;border-radius:8px"></div>
      <div><div class="skel" style="height:12px;width:75%;margin-bottom:5px"></div><div class="skel" style="height:10px;width:45%"></div></div>
      <div class="skel" style="height:24px;width:70px;border-radius:100px"></div>
    </div>`).join('');
  try {
    const res = await fetch(`${API}/search?q=${encodeURIComponent(q)}&limit=20`);
    if (!res.ok) throw new Error(`Error ${res.status}`);
    const data = await res.json();
    trackList = data.results || [];
    if (!trackList.length) {
      $('resultsArea').innerHTML = `<div class="empty-state"><div class="empty-icon"><i class="ti ti-search-off"></i></div><h3>Tidak Ada Hasil</h3><p>Coba kata kunci lain</p></div>`;
      return;
    }
    $('searchHeading').textContent = `"${q}"`;
    $('searchSub').textContent = `${trackList.length} hasil ditemukan dari SoundCloud`;
    renderTrackList();
  } catch(e) {
    $('resultsArea').innerHTML = `<div class="empty-state"><div class="empty-icon"><i class="ti ti-wifi-off"></i></div><h3>Gagal Terhubung</h3><p>${e.message}</p></div>`;
  }
}

function renderTrackList() {
  $('resultsArea').innerHTML = `
    <div class="list-hd"><span>${trackList.length} hasil</span><span style="color:var(--accent2)">SoundCloud</span></div>
    ${trackList.map((r, i) => {
      const isP = i === currentIdx;
      return `<div class="track-row ${isP ? 'playing' : ''} fade-up" id="tr-${i}" style="animation-delay:${i*0.03}s" onclick="playTrack(${i})">
        <div class="track-num">${i+1}</div>
        <i class="track-play-icon ti ${isP ? 'ti-player-pause' : 'ti-player-play'}"></i>
        <div class="track-thumb">
          ${r.thumbnail ? `<img src="${escHtml(r.thumbnail)}" alt="" onerror="this.remove()">` : ''}<i class="ti ti-music"></i>
        </div>
        <div class="track-info">
          <div class="track-title">${escHtml(r.title)}</div>
          <div class="track-artist">${escHtml(r.channel || '—')}${r.view_count ? ` · ${fmtCount(r.view_count)} plays` : ''}</div>
        </div>
        <div class="track-right">
          <span class="track-dur">${fmtDur(r.duration)}</span>
          <button class="btn-process" id="proc-${i}" onclick="event.stopPropagation();processFromSearch(${i},this)">
            <i class="ti ti-sparkles"></i> Process
          </button>
        </div>
      </div>`;
    }).join('')}`;
}

// ── HLS HELPER ────────────────────────────────────────────────────────────
function destroyHls() {
  if (hlsInstance) {
    hlsInstance.destroy();
    hlsInstance = null;
  }
}

function attachHls(streamUrl) {
  destroyHls();
  if (Hls.isSupported()) {
    hlsInstance = new Hls({ enableWorker: false });
    hlsInstance.loadSource(streamUrl);
    hlsInstance.attachMedia(audioEl);
    hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
      audioEl.play().catch(e => {
        if (e.name !== 'AbortError') toast('❌ Gagal play HLS: ' + e.message, 3000);
      });
    });
    hlsInstance.on(Hls.Events.ERROR, (ev, data) => {
      if (data.fatal) toast('❌ HLS error: ' + data.type, 3000);
    });
  } else if (audioEl.canPlayType('application/vnd.apple.mpegurl')) {
    // Safari native HLS
    audioEl.src = streamUrl;
    audioEl.play().catch(e => {
      if (e.name !== 'AbortError') toast('❌ ' + e.message, 3000);
    });
  } else {
    toast('❌ Browser tidak support HLS', 3000);
  }
}

// ── AUDIO EVENTS ──────────────────────────────────────────────────────────
audioEl.addEventListener('timeupdate', updateProgress);
audioEl.addEventListener('ended', playNext);
audioEl.addEventListener('play', () => {
  $('playIcon').className = 'ti ti-player-pause';
  $('playerEq').style.display = 'flex';
});
audioEl.addEventListener('pause', () => {
  $('playIcon').className = 'ti ti-player-play';
  $('playerEq').style.display = 'none';
});
audioEl.addEventListener('error', () => {
  // Abaikan error saat kita sengaja reset source
  if (isChangingSrc) return;
  const err = audioEl.error;
  if (!err || err.code === MediaError.MEDIA_ERR_ABORTED) return;
  toast('❌ Gagal memutar audio (kode ' + err.code + ')', 3000);
  $('playIcon').className = 'ti ti-player-play';
  $('playerEq').style.display = 'none';
});

// ── PLAY TRACK ────────────────────────────────────────────────────────────
async function playTrack(idx) {
  currentIdx = idx;
  const r = trackList[idx];
  currentTrack = r;

  // Update UI metadata
  $('playerTitle').textContent = r.title;
  $('playerArtist').textContent = r.channel || '—';
  $('npSideTitle').textContent = r.title;
  $('npSideArtist').textContent = r.channel || '—';

  const npArt = $('npArt');
  npArt.innerHTML = r.thumbnail
    ? `<img src="${escHtml(r.thumbnail)}" alt="" onerror="this.remove();this.parentElement.innerHTML='<i class=ti ti-music></i>'">`
    : `<i class="ti ti-music"></i>`;

  const thumb = $('playerThumb');
  thumb.innerHTML = r.thumbnail
    ? `<img src="${escHtml(r.thumbnail)}" alt="" onerror="this.parentElement.innerHTML='<i class=ti ti-music></i>'">`
    : `<i class="ti ti-music"></i>`;

  $('npSide').classList.add('visible');
  renderTrackList();

  // ── Reset audio sebelum load source baru ──
  // Set flag SEBELUM pause/load agar error event diabaikan
  isChangingSrc = true;
  destroyHls();
  audioEl.pause();
  audioEl.removeAttribute('src');
  audioEl.load();

  try {
    const res = await fetch(`${API}/stream-url?url=${encodeURIComponent(r.url)}`);
    if (!res.ok) throw new Error(`stream-url ${res.status}`);
    const data = await res.json();

    // Aman untuk proses error sekarang
    isChangingSrc = false;

    if (data.is_hls) {
      attachHls(data.stream_url);
    } else {
      audioEl.src = data.stream_url;
      audioEl.play().catch(e => {
        if (e.name === 'AbortError') return;
        toast('⚠️ Direct gagal, coba proxy...', 2000);
        tryProxyFallback(r.url);
      });
    }
  } catch(e) {
    isChangingSrc = false;
    toast('⚠️ stream-url gagal, coba proxy...', 2000);
    tryProxyFallback(r.url);
  }
}

function tryProxyFallback(url) {
  isChangingSrc = true;
  destroyHls();
  audioEl.pause();
  audioEl.removeAttribute('src');
  audioEl.load();
  isChangingSrc = false;
  audioEl.src = `${API}/proxy-audio?url=${encodeURIComponent(url)}`;
  audioEl.play().catch(e => {
    if (e.name !== 'AbortError') toast('❌ Semua metode gagal: ' + e.message, 4000);
  });
}

function togglePlay() {
  if (!currentTrack) return;
  if (audioEl.paused) {
    audioEl.play().catch(e => { if (e.name !== 'AbortError') toast('❌ ' + e.message); });
  } else {
    audioEl.pause();
  }
}
function playNext() { if (currentIdx < trackList.length - 1) playTrack(currentIdx + 1); }
function playPrev() {
  if (audioEl.currentTime > 3) { audioEl.currentTime = 0; return; }
  if (currentIdx > 0) playTrack(currentIdx - 1);
}
function updateProgress() {
  if (!audioEl.duration) return;
  const pct = (audioEl.currentTime / audioEl.duration) * 100;
  $('playerFill').style.width = pct + '%';
  $('timeCur').textContent = fmtDur(audioEl.currentTime);
  $('timeDur').textContent = fmtDur(audioEl.duration);
}
function seekTo(e) {
  if (!audioEl.duration) return;
  const bar = $('playerBarEl'), rect = bar.getBoundingClientRect();
  const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  audioEl.currentTime = pct * audioEl.duration;
}
function setVol(v) { audioEl.volume = parseFloat(v); }

// ── PROCESS FROM SEARCH ───────────────────────────────────────────────────
async function processFromSearch(idx, btn) {
  const r = trackList[idx];
  if (!r) return;

  btn.classList.add('loading');
  btn.innerHTML = '<i class="ti ti-loader spin"></i> Mengambil...';
  toast('⏳ Mengambil audio dari SoundCloud...', 20000);

  switchTab('upload');

  const overlay = $('fetchOverlay');
  overlay.classList.add('show');
  $('fetchTitle').textContent = 'Mengambil: ' + (r.title.length > 38 ? r.title.slice(0, 36) + '…' : r.title);
  $('fetchSub').textContent = 'Menghubungi server...';
  $('uploadHeroTitle').textContent = 'Convert Audio';
  $('uploadHeroSub').textContent = r.title;
  $('fromSearchLabel').textContent = `${escHtml(r.channel || 'SoundCloud')} · ${fmtDur(r.duration)}`;
  $('fromSearchBadge').style.display = 'inline-flex';

  clearFile();

  try {
    $('fetchSub').textContent = 'Download via proxy-audio...';

    const resp = await fetch(`${API}/proxy-audio?url=${encodeURIComponent(r.url)}`);
    if (!resp.ok) throw new Error(`Server error HTTP ${resp.status}`);

    $('fetchSub').textContent = 'Membaca data...';
    const arrayBuf = await resp.arrayBuffer();

    if (arrayBuf.byteLength < 4096) throw new Error('Data terlalu kecil, coba lagi');

    $('fetchSub').textContent = 'Decode audio...';
    const actx = new (window.AudioContext || window.webkitAudioContext)();
    audioBuffer = await actx.decodeAudioData(arrayBuf);

    const sizeMB = (arrayBuf.byteLength / 1048576).toFixed(2);
    const name = r.title.replace(/[/\\?%*:|"<>]/g, '_') + '.mp3';
    $('sfName').textContent = name.length > 45 ? name.slice(0, 42) + '…' : name;
    $('sfMeta').textContent = fmtDur(audioBuffer.duration) + ' · ' + sizeMB + ' MB · SoundCloud';
    $('selectedFile').classList.add('show');
    $('dropLabel').textContent = '✓ Audio siap';

    updateChips();
    drawWaveform(audioBuffer);
    setStatus('Siap — ' + audioBuffer.duration.toFixed(1) + 's');
    $('processBtn').disabled = false;
    $('outSection').style.display = 'none';
    overlay.classList.remove('show');
    toast('✅ Audio siap diproses!');

    btn.classList.remove('loading');
    btn.innerHTML = '<i class="ti ti-sparkles"></i> Process';
  } catch(e) {
    overlay.classList.remove('show');
    toast('❌ Gagal: ' + e.message, 5000);
    setStatus('❌ Gagal: ' + e.message);
    $('uploadHeroTitle').textContent = 'Upload & Convert';
    $('uploadHeroSub').textContent = 'Upload file audio atau video, convert ke MP3 dengan efek profesional';
    $('fromSearchBadge').style.display = 'none';
    btn.classList.remove('loading');
    btn.innerHTML = '<i class="ti ti-sparkles"></i> Process';
    switchTab('search');
  }
}

// ── FILE UPLOAD ───────────────────────────────────────────────────────────
$('dropZone').addEventListener('dragover', e => { e.preventDefault(); $('dropZone').classList.add('drag'); });
$('dropZone').addEventListener('dragleave', () => $('dropZone').classList.remove('drag'));
$('dropZone').addEventListener('drop', e => {
  e.preventDefault();
  $('dropZone').classList.remove('drag');
  if (e.dataTransfer.files[0]) loadFile(e.dataTransfer.files[0]);
});
$('fileIn').addEventListener('change', e => { if (e.target.files[0]) loadFile(e.target.files[0]); });

async function loadFile(file) {
  setStatus('Memuat file...');
  $('fromSearchBadge').style.display = 'none';
  $('uploadHeroTitle').textContent = 'Upload & Convert';
  $('uploadHeroSub').textContent = 'Upload file audio atau video, convert ke MP3 dengan efek profesional';
  const actx = new (window.AudioContext || window.webkitAudioContext)();
  try {
    audioBuffer = await actx.decodeAudioData(await file.arrayBuffer());
    $('sfName').textContent = file.name.length > 45 ? file.name.slice(0, 42) + '…' : file.name;
    $('sfMeta').textContent = fmtDur(audioBuffer.duration) + ' · ' + fmtSize(file.size);
    $('selectedFile').classList.add('show');
    $('dropLabel').textContent = '✓ File dimuat';
    updateChips();
    drawWaveform(audioBuffer);
    setStatus('Siap — ' + audioBuffer.duration.toFixed(1) + 's');
    $('processBtn').disabled = false;
    $('outSection').style.display = 'none';
  } catch(e) {
    setStatus('❌ Gagal membaca file');
    toast('Gagal membaca file: ' + e.message, 4000);
  }
}

function clearFile() {
  audioBuffer = null;
  $('selectedFile').classList.remove('show');
  $('processBtn').disabled = true;
  $('outSection').style.display = 'none';
  $('infoChips').classList.remove('show');
  $('dropLabel').textContent = 'Seret atau klik untuk upload';
  setStatus('Upload file untuk mulai');
  $('fileIn').value = '';
  const cv = $('waveCanvas'), ctx = cv.getContext('2d');
  ctx.clearRect(0, 0, cv.width, cv.height);
}

// ── CONTROLS SYNC ─────────────────────────────────────────────────────────
function syncPair(rId, nId, dId, fn) {
  const r = $(rId), n = $(nId), d = $(dId);
  const upd = v => { d.textContent = fn(parseFloat(v)); updateChips(); };
  r.addEventListener('input', () => { n.value = r.value; upd(r.value); });
  n.addEventListener('input', () => { r.value = n.value; upd(n.value); });
  upd(r.value);
}
syncPair('speedRange', 'speedNum', 'speedVal', v => v.toFixed(2) + '×');
syncPair('dbRange', 'dbNum', 'dbVal', v => (v >= 0 ? '+' : '') + v.toFixed(1) + ' dB');
syncPair('durRange', 'durNum', 'durVal', v => Math.round(v) + 's');

function updateChips() {
  if (!audioBuffer) return;
  const speed = parseFloat($('speedNum').value);
  const maxDur = parseFloat($('durNum').value);
  const outSec = Math.min(audioBuffer.duration / speed, maxDur);
  $('chipDur').textContent = audioBuffer.duration.toFixed(1) + 's';
  $('chipOut').textContent = outSec.toFixed(1) + 's';
  $('chipInv').textContent = (1 / speed).toFixed(4) + '×';
  $('infoChips').classList.add('show');
}

function setFmt(f) {
  fmt = f;
  $('fmtMp3').classList.toggle('active', f === 'mp3');
  $('fmtWav').classList.toggle('active', f === 'wav');
  $('mp3Opts').style.display = f === 'mp3' ? 'block' : 'none';
}
setFmt('mp3');

function drawWaveform(buf) {
  const cv = $('waveCanvas'), ctx = cv.getContext('2d');
  cv.width = cv.offsetWidth * devicePixelRatio;
  cv.height = 112;
  const data = buf.getChannelData(0);
  const step = Math.ceil(data.length / cv.width);
  const h = cv.height / 2;
  ctx.clearRect(0, 0, cv.width, cv.height);
  for (let x = 0; x < cv.width; x++) {
    let mx = 0;
    for (let j = 0; j < step; j++) {
      const v = Math.abs(data[x * step + j] || 0);
      if (v > mx) mx = v;
    }
    const grad = ctx.createLinearGradient(0, h - mx*h*0.9, 0, h + mx*h*0.9);
    grad.addColorStop(0, `rgba(120,100,255,${0.4 + mx*0.6})`);
    grad.addColorStop(1, `rgba(167,139,250,${0.4 + mx*0.6})`);
    ctx.strokeStyle = grad;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x, h - mx*h*0.9);
    ctx.lineTo(x, h + mx*h*0.9);
    ctx.stroke();
  }
}

// ── PROCESS BUTTON ────────────────────────────────────────────────────────
$('processBtn').addEventListener('click', async () => {
  if (!audioBuffer) return;
  $('processBtn').disabled = true;
  $('outSection').style.display = 'none';
  $('progWrap').style.display = 'block';

  setP(5, 'Menyiapkan...');
  await tick(40);

  const speed = parseFloat($('speedNum').value);
  const db = parseFloat($('dbNum').value);
  const maxDur = parseFloat($('durNum').value);
  const gain = Math.pow(10, db / 20);
  const sr = audioBuffer.sampleRate;
  const nc = audioBuffer.numberOfChannels;
  const outSecA = Math.min(audioBuffer.duration / speed, maxDur);
  const outLenA = Math.ceil(outSecA * sr);

  setP(10, 'Output A: time-stretching...');
  await tick(40);

  let stretchedA;
  try {
    stretchedA = await stStretch(audioBuffer, speed, outLenA, sr, nc);
  } catch(e) {
    stretchedA = await fallbackStretch(audioBuffer, speed, outLenA, sr, nc);
  }

  setP(40, 'Output A: efek...');
  await tick(40);
  const renderedA = await applyFx(stretchedA, gain, sr, nc, outLenA);

  const outLenB = Math.min(audioBuffer.length, Math.ceil(maxDur * sr));
  setP(60, 'Output B: efek...');
  await tick(40);
  const renderedB = await applyFx(audioBuffer, gain, sr, nc, outLenB);

  setP(85, 'Encoding...');
  await tick(40);

  const kbps = parseInt($('bitrateSelect').value);
  const blobA = fmt === 'mp3' ? encodeMp3(renderedA, kbps) : encodeWAV(renderedA);
  const blobB = fmt === 'mp3' ? encodeMp3(renderedB, kbps) : encodeWAV(renderedB);
  const ext = fmt === 'mp3' ? 'mp3' : 'wav';

  const urlA = URL.createObjectURL(blobA);
  const urlB = URL.createObjectURL(blobB);

  $('previewA').src = urlA;
  $('dlA').href = urlA;
  $('dlA').download = 'output_A_speed.' + ext;
  $('previewB').src = urlB;
  $('dlB').href = urlB;
  $('dlB').download = 'output_B_original.' + ext;
  $('labelSpeedA').textContent = speed.toFixed(2) + '×';
  $('infoA').textContent = outSecA.toFixed(2) + 's · ' + fmtSize(blobA.size);
  $('infoB').textContent = audioBuffer.duration.toFixed(2) + 's · ' + fmtSize(blobB.size);

  setP(100, '✓ Selesai!');
  $('outSection').style.display = 'block';
  $('processBtn').disabled = false;
  toast('✅ Kedua output siap!');
});

function setP(p, m) { $('progBar').style.width = p + '%'; $('statusTxt').textContent = m; }
function setStatus(m) { $('statusTxt').textContent = m; }
function tick(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── AUDIO FX ──────────────────────────────────────────────────────────────
async function applyFx(srcBuf, gain, sr, nc, outLen) {
  const offCtx = new OfflineAudioContext(nc, outLen, sr);
  const src = offCtx.createBufferSource();
  src.buffer = srcBuf;

  const eqS = [
    {f:80,  g:-2, t:'lowshelf'},
    {f:200, g:1,  t:'peaking'},
    {f:1000,g:2,  t:'peaking'},
    {f:3000,g:3,  t:'peaking'},
    {f:8000,g:2,  t:'peaking'},
    {f:16000,g:1, t:'highshelf'},
  ];
  let chain = src;
  eqS.forEach(s => {
    const n = offCtx.createBiquadFilter();
    n.type = s.t; n.frequency.value = s.f; n.gain.value = s.g; n.Q.value = 0.8;
    chain.connect(n); chain = n;
  });

  const comp = offCtx.createDynamicsCompressor();
  comp.threshold.value = -24; comp.ratio.value = 4; comp.knee.value = 6;
  comp.attack.value = 0.003; comp.release.value = 0.25;
  chain.connect(comp); chain = comp;

  const mk = offCtx.createGain(); mk.gain.value = Math.pow(10, 6/20);
  chain.connect(mk); chain = mk;

  const gn = offCtx.createGain(); gn.gain.value = gain;
  chain.connect(gn); chain = gn;

  chain.connect(offCtx.destination);
  src.start(0);

  let rendered = await offCtx.startRendering();

  // Normalize
  let peak = 0;
  for (let c = 0; c < rendered.numberOfChannels; c++) {
    const d = rendered.getChannelData(c);
    for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > peak) peak = v; }
  }
  if (peak > 0.001 && peak < 0.97) {
    const ng = 0.95 / peak;
    const nCtx = new OfflineAudioContext(rendered.numberOfChannels, outLen, sr);
    const s2 = nCtx.createBufferSource(); s2.buffer = rendered;
    const g2 = nCtx.createGain(); g2.gain.value = ng;
    s2.connect(g2); g2.connect(nCtx.destination); s2.start(0);
    rendered = await nCtx.startRendering();
  }
  return rendered;
}

async function stStretch(srcBuf, speed, outLen, sr, nc) {
  const L = srcBuf.getChannelData(0);
  const R = nc > 1 ? srcBuf.getChannelData(1) : L;
  const st = new soundtouch.SoundTouch(sr);
  st.tempo = speed; st.pitch = 1.0;
  let pos = 0;
  const source = new soundtouch.SimpleFilter({
    extract: (t, n) => {
      const a = Math.min(n, L.length - pos);
      if (a <= 0) return 0;
      for (let i = 0; i < a; i++) { t[i*2] = L[pos+i]; t[i*2+1] = R[pos+i]; }
      pos += a; return a;
    }
  }, st);
  const out = new Float32Array(outLen * 2);
  const chunk = 8192; let written = 0;
  while (written < outLen) {
    const tr = Math.min(chunk, outLen - written);
    const buf = new Float32Array(tr * 2);
    const got = source.extract(buf, tr);
    if (got === 0) break;
    out.set(buf.subarray(0, got * 2), written * 2);
    written += got;
    await tick(0);
  }
  const ob = new AudioBuffer({ numberOfChannels: nc, length: outLen, sampleRate: sr });
  const oL = new Float32Array(outLen), oR = new Float32Array(outLen);
  for (let i = 0; i < outLen; i++) { oL[i] = out[i*2]; oR[i] = out[i*2+1]; }
  ob.copyToChannel(oL, 0);
  if (nc > 1) ob.copyToChannel(oR, 1);
  return ob;
}

async function fallbackStretch(srcBuf, speed, outLen, sr, nc) {
  const offCtx = new OfflineAudioContext(nc, outLen, sr);
  const src = offCtx.createBufferSource();
  src.buffer = srcBuf; src.playbackRate.value = speed;
  src.connect(offCtx.destination); src.start(0);
  return await offCtx.startRendering();
}

// ── ENCODING ──────────────────────────────────────────────────────────────
function encodeMp3(buf, kbps) {
  const nc = buf.numberOfChannels, sr = buf.sampleRate;
  const enc = new lamejs.Mp3Encoder(nc, sr, kbps);
  const bs = 1152;
  const L = buf.getChannelData(0);
  const R = nc > 1 ? buf.getChannelData(1) : null;
  const chunks = [];
  for (let i = 0; i < L.length; i += bs) {
    const lc = f2i(L.subarray(i, i + bs));
    const e = R ? enc.encodeBuffer(lc, f2i(R.subarray(i, i + bs))) : enc.encodeBuffer(lc);
    if (e.length > 0) chunks.push(new Int8Array(e));
  }
  const end = enc.flush();
  if (end.length > 0) chunks.push(new Int8Array(end));
  return new Blob(chunks, { type: 'audio/mpeg' });
}

function f2i(f) {
  const o = new Int16Array(f.length);
  for (let i = 0; i < f.length; i++) {
    const s = Math.max(-1, Math.min(1, f[i]));
    o[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  return o;
}

function encodeWAV(buf) {
  const nc = buf.numberOfChannels, sr = buf.sampleRate;
  const ns = buf.length, ba = nc * 2, ds = ns * ba;
  const ab = new ArrayBuffer(44 + ds), v = new DataView(ab);
  const ws = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
  ws(0, 'RIFF'); v.setUint32(4, 36 + ds, true); ws(8, 'WAVE'); ws(12, 'fmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, nc, true);
  v.setUint32(24, sr, true); v.setUint32(28, sr * ba, true); v.setUint16(32, ba, true);
  v.setUint16(34, 16, true); ws(36, 'data'); v.setUint32(40, ds, true);
  let off = 44;
  const ch = [];
  for (let c = 0; c < nc; c++) ch.push(buf.getChannelData(c));
  for (let i = 0; i < ns; i++) for (let c = 0; c < nc; c++) {
    const s = Math.max(-1, Math.min(1, ch[c][i]));
    v.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    off += 2;
  }
  return new Blob([ab], { type: 'audio/wav' });
}

// ── HELPERS ───────────────────────────────────────────────────────────────
function fmtCount(n) {
  if (!n) return '0';
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toString();
}
function escHtml(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function fmtDur(sec) {
  if (!sec) return '0:00';
  sec = Math.floor(sec);
  const m = Math.floor(sec / 60), s = sec % 60;
  return m + ':' + String(s).padStart(2, '0');
}
function fmtSize(b) {
  return b > 1048576 ? (b / 1048576).toFixed(2) + ' MB' : (b / 1024).toFixed(0) + ' KB';
}
</script>
</body>
</html>
