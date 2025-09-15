import feedparser, re, hashlib
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
# Fungsi slugify
# ==============================
def slugify(title: str, link: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9 ]+", "", title).strip().lower().replace(" ", "-")
    short = hashlib.sha1(link.encode()).hexdigest()[:8]
    return f"{base}-{short}"

# ==============================
# Fungsi membuat file artikel (dengan thumbnail)
# ==============================
def write_post(title, summary, link, published, thumbnail=None):
    slug = slugify(title, link)
    fname = POSTS_DIR / f"{slug}.html"
    if fname.exists():
        return False

    if not thumbnail:
        thumbnail = "https://via.placeholder.com/800x400.png?text=No+Image"

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f9f9f9; color: #333; }}
    header {{ background: #1e1e1e; padding: 15px; }}
    header a {{ color: white; text-decoration: none; font-weight: bold; }}
    .container {{ max-width: 800px; margin: 40px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
    h1 {{ color: #222; margin-bottom: 10px; }}
    .meta {{ color: gray; font-size: 14px; margin-bottom: 20px; }}
    img.thumb {{ width: 100%; border-radius: 8px; margin-bottom: 20px; }}
    .content p {{ line-height: 1.6; margin-bottom: 15px; }}
    .source {{ margin-top: 20px; font-size: 14px; }}
    .source a {{ color: #007bff; text-decoration: none; }}
    .source a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <a href="../index.html">⬅ Kembali ke Home</a> | <a href="index.html">📂 Artikel</a>
  </header>
  <div class="container">
    <img src="{thumbnail}" alt="thumbnail" class="thumb"/>
    <h1>{title}</h1>
    <div class="meta">{published}</div>
    <div class="content">{summary}</div>
    <div class="source">Sumber: <a href="{link}" target="_blank">{link}</a></div>
  </div>
</body>
</html>"""
    fname.write_text(html, encoding="utf-8")
    return True

# ==============================
# Ambil artikel dari feed
# ==============================
for feed_url in FEEDS:
    d = feedparser.parse(feed_url)
    for e in d.entries[:3]:
        title = getattr(e, "title", "Tanpa Judul")
        summary = getattr(e, "summary", "")
        link = getattr(e, "link", "#")
        published = getattr(e, "published", "")
        thumb = None
        if "media_content" in e and e.media_content:
            thumb = e.media_content[0].get("url")
        elif "image" in e:
            thumb = e.image
        write_post(title, summary, link, published, thumb)

# ==============================
# Buat index artikel
# ==============================
def build_index():
    cards = []
    for p in POSTS_DIR.glob("*.html"):
        if p.name == "index.html":
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title>(.*?)</title>", txt, re.I|re.S)
        title = m.group(1).strip() if m else p.stem
        m2 = re.search(r'<img src="(.*?)".*?class="thumb"', txt, re.I|re.S)
        thumb = m2.group(1) if m2 else "https://via.placeholder.com/400x200.png?text=No+Image"
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
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }}
    header {{ background: #1e1e1e; color: white; padding: 15px; text-align: center; }}
    header a {{ color: #fff; text-decoration: none; font-weight: bold; }}
    .container {{ max-width: 1100px; margin: 20px auto; padding: 20px; }}
    h1 {{ color: #333; margin-bottom: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
    .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); overflow: hidden; transition: transform .2s; }}
    .card:hover {{ transform: translateY(-5px); }}
    .card img {{ width: 100%; height: 180px; object-fit: cover; }}
    .card h2 {{ font-size: 16px; padding: 10px; color: #007bff; }}
    .card a {{ text-decoration: none; }}
    .card a:hover h2 {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <a href="../index.html">⬅ Kembali ke Home</a>
  </header>

  <div class="container">
    <h1>Artikel Film Terbaru</h1>
    <div class="grid">
      {''.join(cards)}
    </div>
  </div>
</body>
</html>"""
    (POSTS_DIR / "index.html").write_text(html, encoding="utf-8")

# ==============================
# Update homepage
# ==============================
def update_homepage():
    posts = sorted([p for p in POSTS_DIR.glob("*.html") if p.name != "index.html"],
                   key=lambda x: x.stat().st_mtime, reverse=True)[:3]
    cards = []
    for p in posts:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title>(.*?)</title>", txt, re.I|re.S)
        title = m.group(1).strip() if m else p.stem
        m2 = re.search(r'<img src="(.*?)".*?class="thumb"', txt, re.I|re.S)
        thumb = m2.group(1) if m2 else "https://via.placeholder.com/400x200.png?text=No+Image"
        cards.append(f"""
          <div class="card">
            <a href="posts/{p.name}">
              <img src="{thumb}" alt="{title}">
              <h2>{title}</h2>
            </a>
          </div>
        """)

    homepage = Path("index.html").read_text(encoding="utf-8")
    homepage = homepage.replace("{{LATEST_POSTS}}", "".join(cards))
    Path("index.html").write_text(homepage, encoding="utf-8")

# ==============================
# Jalankan
# ==============================
build_index()
update_homepage()
