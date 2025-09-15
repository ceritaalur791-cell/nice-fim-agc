import feedparser, os, re, hashlib
from pathlib import Path

# RSS feed tentang film (← bisa kamu tambah/kurangi)
FEEDS = [
    "https://www.boxofficemojo.com/rss/",
    "https://editorial.rottentomatoes.com/feed/"
]

POSTS_DIR = Path("posts")
POSTS_DIR.mkdir(parents=True, exist_ok=True)

def slugify(title: str, link: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9- ]+", "", title).strip().lower().replace(" ", "-")
    short = hashlib.sha1(link.encode()).hexdigest()[:8]
    return f"{base}-{short}"

def write_post(title, summary, link, published):
    slug = slugify(title, link)
    fname = POSTS_DIR / f"{slug}.html"
    if fname.exists():
        return False

    html = f"""<!doctype html>
<html>
  <head><meta charset="utf-8"><title>{title}</title></head>
  <body>
    <a href="../index.html">⬅ Kembali ke Home</a>
    <h1>{title}</h1>
    <p><i>{published or ''}</i></p>
    <div>{summary}</div>
    <p><em>Sumber: <a href="{link}" target="_blank">{link}</a></em></p>
  </body>
</html>"""
    fname.write_text(html, encoding="utf-8")
    return True

# proses setiap feed
for feed_url in FEEDS:
    d = feedparser.parse(feed_url)
    for e in d.entries[:3]:  # ambil 3 artikel terbaru
        write_post(
            e.get("title", "Tanpa Judul"),
            e.get("summary", ""),
            e.get("link", "#"),
            e.get("published", "")
        )

# buat daftar index posts
def build_index():
    items = []
    for p in POSTS_DIR.glob("*.html"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title>(.*?)</title>", txt, re.I|re.S)
        title = m.group(1) if m else p.stem
        items.append((p.name, title))
    lis = "\n".join([f'<li><a href="{n}">{t}</a></li>' for n, t in items])
    html = f"""<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Artikel Film</title></head>
  <body>
    <h1>Artikel Film Terbaru</h1>
    <ul>{lis}</ul>
    <p><a href="../index.html">⬅ Kembali ke Home</a></p>
  </body>
</html>"""
    (POSTS_DIR / "index.html").write_text(html, encoding="utf-8")

build_index()
