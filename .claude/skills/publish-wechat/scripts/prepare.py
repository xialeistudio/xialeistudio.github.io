"""Prepare the latest (or given) zh blog post for the WeChat 公众号 editor.

Usage:
  python3 -I prepare.py [post.md] [out_dir]

Without a post path, picks the newest file in content/zh/posts by front-matter date.
Writes <out_dir>/wechat.md (front matter and <!--more--> stripped, blog footer added)
and prints a JSON line with title / slug / date / url / description / tags.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # repo root
POSTS = ROOT / "content" / "zh" / "posts"
BASE_URL = "https://www.ddhigh.com"


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit("no front matter")
    return m.group(1), m.group(2)


def field(fm, key):
    m = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', fm, re.M)
    return m.group(1).strip() if m else ""


def tags(fm):
    m = re.search(r"^tags:\s*\n((?:\s*-\s*.*\n?)+)", fm, re.M)
    return [t.strip() for t in re.findall(r"-\s*(.+)", m.group(1))] if m else []


def latest_post():
    best = None
    for p in POSTS.glob("*.md"):
        fm, _ = front_matter(p.read_text(encoding="utf-8"))
        if re.search(r"^draft:\s*true", fm, re.M):
            continue
        d = field(fm, "date")
        if best is None or d > best[0]:
            best = (d, p)
    return best[1]


post = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else latest_post()
out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
out_dir.mkdir(parents=True, exist_ok=True)

fm, body = front_matter(post.read_text(encoding="utf-8"))
date = field(fm, "date")
slug = field(fm, "slug")
y, mo, d = date[:10].split("-")
url = f"{BASE_URL}/{y}/{mo}/{d}/{slug}/"

body = body.replace("<!--more-->\n", "").replace("<!--more-->", "").strip()
footer = f"\n\n---\n\n本文同步发布于博客：{url} ，完整代码与测试见原文。\n"
(out_dir / "wechat.md").write_text(body + footer, encoding="utf-8")

print(json.dumps({
    "post": str(post),
    "title": field(fm, "title"),
    "slug": slug,
    "date": date,
    "url": url,
    "description": field(fm, "description"),
    "tags": tags(fm),
    "markdown": str(out_dir / "wechat.md"),
}, ensure_ascii=False))
