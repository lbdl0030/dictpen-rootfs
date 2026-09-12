#!/usr/bin/env python3
"""下载页 / 镜像链接自动生成工具。

读取 GitHub Releases,生成静态 index.html 下载页:
  - 按 Release 时间倒序列出所有版本和资产
  - 每个资产附带 GitHub 直链 + 镜像加速链接(ghproxy 等,可在 mirrors.json 配置)
  - 纯静态单文件,部署到 gh-pages / GitHub Pages 即可

配置(可选,环境变量或 mirrors.json):
  - GH_REPO     仓库,默认从 GITHUB_REPOSITORY 环境变量取
  - mirrors.json: ["https://ghproxy.net/", "https://gh-proxy.com/"]

用法:
  python gen_download_page.py -o index.html
"""

import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

API = "https://api.github.com/repos/{repo}/releases?per_page=100"
UA = {"User-Agent": "dictpen-rootfs-page-gen/1.0",
      "Accept": "application/vnd.github+json"}


def load_mirrors() -> list[str]:
    p = Path("mirrors.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return ["https://ghproxy.net/", "https://gh-proxy.com/"]


def fetch_releases(repo: str) -> list[dict]:
    url = API.format(repo=repo)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def asset_row(a: dict, mirrors: list[str]) -> str:
    size_mb = a["size"] / 1048576
    mirror_links = " ".join(
        f'<a class="mirror" href="{m.rstrip("/")}/{a["browser_download_url"]}" '
        f'target="_blank">镜像{i + 1}</a>'
        for i, m in enumerate(mirrors))
    return (f'<tr><td>{a["name"]}</td><td>{size_mb:.1f} MB</td>'
            f'<td><a href="{a["browser_download_url"]}" target="_blank">下载</a> '
            f'{mirror_links}</td></tr>')


def render(repo: str, releases: list[dict], mirrors: list[str]) -> str:
    sections = []
    for rel in releases:
        if rel.get("draft"):
            continue
        assets = rel.get("assets", [])
        rows = "\n".join(asset_row(a, mirrors) for a in assets)
        body = (rel.get("body") or "").replace("<", "&lt;")
        tag_badge = " 🏷️ 最新" if rel == releases[0] else ""
        sections.append(f"""
<section class="release">
  <h2><a href="{rel["html_url"]}" target="_blank">{rel["name"] or rel["tag_name"]}</a>{tag_badge}</h2>
  <p class="date">发布时间: {rel["published_at"][:10]}</p>
  <pre class="notes">{body}</pre>
  {"<table><tr><th>文件</th><th>大小</th><th>链接</th></tr>" + rows + "</table>" if rows else "<p>此版本无附件</p>"}
</section>""")

    count = sum(len(r.get("assets", [])) for r in releases)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{repo} 固件下载</title>
<style>
body {{ font-family: system-ui, "Microsoft YaHei", sans-serif; max-width: 960px;
       margin: 0 auto; padding: 1rem; color: #222; }}
h1 {{ border-bottom: 2px solid #4a7; padding-bottom: .4rem; }}
table {{ width: 100%; border-collapse: collapse; margin: .5rem 0; }}
th, td {{ border: 1px solid #ddd; padding: .45rem .6rem; text-align: left;
          word-break: break-all; }}
th {{ background: #f4f6f8; }}
.release {{ margin: 2rem 0; }}
.date {{ color: #777; font-size: .9em; }}
.notes {{ background: #fafafa; border-left: 3px solid #ccc; padding: .5rem .8rem;
          white-space: pre-wrap; font-size: .85em; }}
a.mirror {{ margin-left: .4rem; color: #067; }}
footer {{ margin-top: 3rem; color: #888; font-size: .85em; }}
</style>
</head>
<body>
<h1>词典笔固件下载页</h1>
<p>共 {len(releases)} 个版本 / {count} 个文件。下载前请先在
<a href="https://github.com/{repo}#readme" target="_blank">README</a>
中根据设备树模型确认你的内部代号。</p>
{''.join(sections)}
<footer>
数据自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M UTC+8")} ·
镜像链接由第三方 ghproxy 提供,仅加速用途。
</footer>
</body>
</html>"""


def main():
    repo = os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise SystemExit("请设置 GH_REPO 环境变量,如 lbdl0030/dictpen-rootfs")
    mirrors = load_mirrors()
    print(f"[*] 拉取 {repo} 的 Releases ...")
    releases = fetch_releases(repo)
    html = render(repo, releases, mirrors)
    out = Path(os.environ.get("OUT", "index.html"))
    out.write_text(html, encoding="utf-8")
    print(f"[+] 已生成 {out} ({len(releases)} 个版本)")


if __name__ == "__main__":
    main()
