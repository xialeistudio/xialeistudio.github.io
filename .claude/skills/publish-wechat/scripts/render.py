# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown>=3.5", "pygments>=2.17"]
# ///
"""Render WeChat-ready Markdown (from prepare.py) to inline-styled HTML for the 公众号 editor.

Usage:
  uv run --script render.py <wechat.md> <out.html> [--credit "Author"] [--copy]

  --credit  append "封面图：<Author> / Unsplash" at the end
  --copy    put the HTML on the macOS clipboard as rich text (paste with Cmd+V)

The 公众号 editor drops <style>, classes and tabs, so every style is inline,
code indentation becomes &nbsp;, and newlines in code become <br>.
"""
import argparse
import html as htmllib
import re
import subprocess

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

BASE_URL = "https://www.ddhigh.com"
FONT = "-apple-system,'PingFang SC','Microsoft YaHei',sans-serif"
MONO = "Menlo,Consolas,'Courier New',monospace"

STYLES = {
    "p": "margin:14px 0;line-height:1.8;font-size:15px;color:#333;letter-spacing:0.5px;",
    "h2": "margin:32px 0 16px;padding-left:10px;border-left:4px solid #2f6feb;"
    "font-size:18px;font-weight:bold;color:#1f2328;line-height:1.5;",
    "h3": "margin:24px 0 12px;font-size:16px;font-weight:bold;color:#1f2328;",
    "h4": "margin:20px 0 10px;font-size:15px;font-weight:bold;color:#1f2328;",
    "ul": "margin:12px 0;padding-left:22px;",
    "ol": "margin:12px 0;padding-left:22px;",
    "li": "margin:6px 0;line-height:1.8;font-size:15px;color:#333;",
    "strong": "color:#1f2328;font-weight:bold;",
    "blockquote": "margin:16px 0;padding:8px 14px;border-left:3px solid #d0d7de;"
    "background:#f6f8fa;color:#57606a;",
    "table": "border-collapse:collapse;width:100%;margin:16px 0;font-size:13px;",
    "th": "border:1px solid #d0d7de;padding:6px 8px;background:#f6f8fa;text-align:left;",
    "td": "border:1px solid #d0d7de;padding:6px 8px;line-height:1.6;",
    "hr": "margin:28px 0;border:none;border-top:1px solid #e5e7eb;",
    "img": "max-width:100%;display:block;margin:16px auto;border-radius:4px;",
}
INLINE_CODE = (
    "padding:2px 4px;margin:0 2px;background:#f0f2f4;border-radius:3px;"
    f"font-size:13px;color:#c7254e;font-family:{MONO};"
)
FORMATTER = HtmlFormatter(noclasses=True, nowrap=True, style="friendly")


def code_block(lang: str, code: str) -> str:
    code = code.expandtabs(4).rstrip("\n")
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except Exception:
        lexer = TextLexer()
    out = highlight(code, lexer, FORMATTER).rstrip("\n")
    # protect whitespace outside tags, then turn newlines into <br>
    parts = re.split(r"(<[^>]+>)", out)
    out = "".join(p if p.startswith("<") else p.replace(" ", "&nbsp;") for p in parts)
    out = out.replace("\n", "<br>")
    return (
        '<section style="margin:16px 0;padding:12px 14px;background:#f6f8fa;'
        'border-radius:6px;overflow-x:auto;">'
        '<code style="display:block;white-space:nowrap;font-size:12.5px;line-height:1.7;'
        f'font-family:{MONO};color:#24292f;background:none;">{out}</code></section>'
    )


def render(md_text: str, credit: str | None) -> str:
    blocks: list[str] = []

    def stash(m):
        blocks.append(code_block(m.group(1) or "", m.group(2)))
        return f"\n\nCODEBLOCK{len(blocks) - 1}END\n\n"

    md_text = re.sub(r"```(\w*)\n(.*?)```", stash, md_text, flags=re.S)
    if credit:
        md_text = md_text.rstrip() + f"\n\n封面图：{credit} / Unsplash\n"

    out = markdown.markdown(md_text, extensions=["tables"])
    for i, b in enumerate(blocks):
        out = out.replace(f"<p>CODEBLOCK{i}END</p>", b)

    # site-relative images -> absolute, so the editor can fetch them
    out = re.sub(r'<img([^>]*?) src="/', rf'<img\1 src="{BASE_URL}/', out)
    # external links are not clickable in 公众号 articles: keep the URL as text
    def unlink(m):
        href, text = m.group(1), m.group(2)
        plain = re.sub(r"<[^>]+>", "", text)
        return text if plain == href else f"{text}（{htmllib.escape(href)}）"

    out = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', unlink, out, flags=re.S)

    for tag, style in STYLES.items():
        out = re.sub(rf"<{tag}(\s[^>]*)?>", lambda m, t=tag, s=style: f'<{t} style="{s}"{m.group(1) or ""}>', out)
    out = out.replace("<code>", f'<code style="{INLINE_CODE}">')
    return f'<section style="font-family:{FONT};">{out}</section>'


def copy_to_clipboard(fragment: str) -> None:
    data = ('<meta charset="utf-8">' + fragment).encode("utf-8").hex()
    script = f"set the clipboard to «data HTML{data}»"
    subprocess.run(["osascript", "-"], input=script.encode(), check=True)
    info = subprocess.run(["osascript", "-e", "clipboard info"], capture_output=True, text=True).stdout
    if "HTML" not in info:
        raise SystemExit(f"clipboard does not hold HTML: {info}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("out")
    ap.add_argument("--credit")
    ap.add_argument("--copy", action="store_true")
    a = ap.parse_args()

    fragment = render(open(a.markdown, encoding="utf-8").read(), a.credit)
    page = (
        '<!doctype html><html><head><meta charset="utf-8"><title>WeChat preview</title></head>'
        f'<body style="max-width:680px;margin:24px auto;padding:0 16px;background:#fff;">{fragment}</body></html>'
    )
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    if a.copy:
        copy_to_clipboard(fragment)
    print(f"html={a.out} bytes={len(fragment.encode())} code_blocks={fragment.count('overflow-x:auto')}"
          f" tables={fragment.count('<table')} copied={a.copy}")


if __name__ == "__main__":
    main()
