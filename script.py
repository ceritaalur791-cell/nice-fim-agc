import feedparser, os, re, hashlib
from pathlib import Path

# ==============================
# FEEDS — daftar sumber berita film (RSS)
# Bisa kamu tambah/kurangi sesuai kebutuhan
# ==============================
FEEDS = [
    "https://www.boxofficemojo.com/rss/",
    "https://editorial.rottentomatoes.com/feed/"
]

# Folder untuk menyimpan artikel
POSTS_DIR = Path("posts")
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# Fungsi slugify (FIX regex)
# ==============================
def slugify(title: str, link: str) -> str:
    # Hapus karakter aneh, hanya izinkan huruf/angka/spasi
    base = re.sub(r"[^a-zA-Z0-9 ]+", "", title) \
             .strip() \
             .lower() \
             .replace(" ", "-")
    # Tambahkan hash pendek dari link supaya unik
    short = hashlib.sha1(link.encode()).hexdigest()[:8]
    return f"{base}-{short}"

# ==============================
# Fungsi membuat file artikel
# ==============================
def write_post(title, summary, link, published):
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
    for e in d.entries[:3]:  # ambil maksimal 3 artikel terbaru
        title = getattr(e, "title", "Tanpa Judul")
        summary = getattr(e, "summary", "")
        link = getattr(e, "link", "#")
        published = getattr(e, "published", "")

        write_post(title, summary, link, published)

# ==============================
# Buat index artikel (posts/index.html) langsung card grid
# ==============================
def build_index():
    cards = []
    for p in POSTS_DIR.glob("*.html"):
        if p.name == "index.html":
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<title>(.*?)</title>", txt, re.I|re.S)
            title = m.group(1).strip() if m else p.stem
        except Exception:
            title = p.stem
        cards.append(f'<div class="card"><a href="{p.name}">{title}</a></div>')

    # Buat file index.html final (langsung berisi cards)
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Artikel Film Terbaru</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f4f4; }}
    header {{ background: #1e1e1e; color: white; padding: 15px; text-align: center; }}
    header a {{ color: #fff; text-decoration: none; font-weight: bold; }}
    .container {{ max-width: 1000px; margin: 20px auto; padding: 20px; }}
    h1 {{ color: #333; margin-bottom: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
    .card {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); transition: transform .2s; }}
    .card:hover {{ transform: translateY(-5px); }}
    .card a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
    .card a:hover {{ text-decoration: underline; }}
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

build_index()
