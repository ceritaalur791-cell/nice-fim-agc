import feedparser, os, re, hashlib
from pathlib import Path

# ==============================
# FEEDS — daftar sumber berita film (RSS)
# ==============================
FEEDS = [
    "https://www.boxofficemojo.com/rss/",
    "https://editorial.rottentomatoes.com/feed/"
]

# Folder untuk menyimpan artikel
POSTS_DIR = Path("posts")
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# Fungsi slugify (fix regex)
# ==============================
def slugify(title: str, link: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9 ]+", "", title) \
             .strip() \
             .lower() \
             .replace(" ", "-")
    short = hashlib.sha1(link.encode()).hexdigest()[:8]
    return f"{base}-{short}"

# ==============================
# Fungsi membuat file artikel
# ==============================
def write_post(title, summary, link, published, thumb):
    slug = slugify(title, link)
    fname = POSTS_DIR / f"{slug}.html"
    if fname.exists():
        return False

    html = f"""<!doctype html>
<html>
  <head><meta charset="utf-8"><title>{title}</title></head>
  <body style="font-family: Arial, sans-serif; background: #f9f9f9; color:#333; padding:20px;">
    <a href="../index.html">⬅ Kembali ke Home</a> | <a href="index.html">📂 Artikel</a>
    <h1>{title}</h1>
    <p><i>{published or ''}</i></p>
    <img src="{thumb}" alt="{title}" style="max-width:600px; border-radius:8px; margin:10px 0;">
    <div>{summary}</div>
    <p><em>Sumber: <a href="{link}" target="_blank">{link}</a></em></p>
  </body>
</html>"""
    fname.write_text(html, encoding="utf-8")
    return True

# ==============================
# Loop: ambil artikel dari setiap feed
# ==============================
for feed_url in FEEDS:
    d = feedparser.parse(feed_url)
    for e in d.entries[:3]:
        title = getattr(e, "title", "Tanpa Judul")
        summary = getattr(e, "summary", "")
        link = getattr(e, "link", "#")
        published = getattr(e, "published", "")
        # Cari thumbnail (kalau ada)
        thumb = ""
        if "media_thumbnail" in e:
            thumb = e.media_thumbnail[0]["url"]
        elif "media_content" in e:
            thumb = e.media_content[0]["url"]
        else:
            thumb = "https://via.placeholder.com/400x200.png?text=No+Image"

        write_post(title, summary, link, published, thumb)

# ==============================
# Buat index artikel (grid card)
# ==============================
def build_index():
    cards = []
    for p in POSTS_DIR.glob("*.html"):
        if p.name == "index.html":
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            m_title = re.search(r"<title>(.*?)</title>", txt, re.I|re.S)
            title = m_title.group(1).strip() if m_title else p.stem
            m_img = re.search(r'<img src="(.*?)"', txt)
            thumb = m_img.group(1) if m_img else "https://via.placeholder.com/400x200.png?text=No+Image"
        except Exception:
            title, thumb = p.stem, "https://via.placeholder.com/400x200.png?text=No+Image"

        cards.append(f"""
        <div class="card">
          <a href="{p.name}">
            <img src="{thumb}" alt="{title}">
            <h2>{title}</h2>
          </a>
        </div>
        """)

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Artikel Film Terbaru</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin:0; padding:0; }}
    header {{ background: #1e1e1e; color:#fff; padding:15px; text-align:center; }}
    header a {{ color:#fff; text-decoration:none; font-weight:bold; }}
    .container {{ max-width:1000px; margin:20px auto; padding:20px; }}
    h1 {{ color:#333; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }}
    .card {{ background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.1); }}
    .card img {{ width:100%; height:160px; object-fit:cover; }}
    .card h2 {{ font-size:16px; padding:10px; color:#007bff; }}
    .card h2:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <header><a href="../index.html">⬅ Kembali ke Home</a></header>
  <div class="container">
    <h1>Artikel Film Terbaru</h1>
    <div class="grid">
      {''.join(cards)}
    </div>
  </div>
</body>
</html>"""
    (POSTS_DIR / "index.html").write_text(html, encoding="utf-8")

build_index()
