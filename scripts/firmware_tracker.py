#!/usr/bin/env python3
"""新版本固件自动跟踪下载工具。

通过 sources.json 配置固件来源(URL 列表),用 ETag / Last-Modified / Content-Length
检测远端是否有新版本;发现变化则下载到 downloads/ 并把索引写入 firmware_index.json。
index.json 记录历史状态,重复运行时只下载新出现或内容变化的固件。

sources.json 示例:
{
  "sources": [
    {
      "name": "youdao-ota-x3s",
      "url": "https://example.com/ota/x3s/ota.zip",
      "device": "Cherry-3566",
      "os_version_hint": "extract_from_filename"
    }
  ]
}

用法:
  python firmware_tracker.py [--sources sources.json] [--downloads downloads]
                             [--dry-run]
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = {"User-Agent": "dictpen-rootfs-tracker/1.0"}


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def head_info(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return {k.lower(): v for k, v in r.headers.items()}


def fingerprint(info: dict) -> str:
    """用 ETag/Last-Modified/Content-Length 组合成远端内容指纹。"""
    key = "|".join(info.get(k, "") for k in ("etag", "last-modified", "content-length"))
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def os_version_from_name(name: str) -> str | None:
    m = re.search(r"(\d+\.\d+(?:\.\d+)?)", name)
    return m.group(1) if m else None


def track(sources_file: Path, downloads: Path, dry_run: bool) -> list[dict]:
    cfg = load_json(sources_file, {"sources": []})
    index = load_json(Path("firmware_index.json"), {"firmware": []})
    known = {f["fingerprint"] for f in index["firmware"]}
    new_items = []

    for src in cfg.get("sources", []):
        name, url = src.get("name"), src.get("url")
        if not url:
            print(f"[!] 跳过缺少 url 的条目: {name}")
            continue
        print(f"[*] 检查 {name}: {url}")
        try:
            info = head_info(url)
        except Exception as e:
            print(f"[!] HEAD 失败(部分服务器不支持,可改用 GET): {e}")
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=60) as r:
                    info = {k.lower(): v for k, v in r.headers.items()}
                    r.close()
            except Exception as e2:
                print(f"[!] 获取失败: {e2}")
                continue

        fp = fingerprint(info)
        if fp in known:
            print(f"    无更新 ({fp})")
            continue

        size = int(info.get("content-length", 0) or 0)
        fname = url.rstrip("/").split("/")[-1] or name
        item = {
            "name": name,
            "url": url,
            "device": src.get("device"),
            "os_version": src.get("os_version") or os_version_from_name(fname),
            "filename": fname,
            "size_bytes": size,
            "fingerprint": fp,
            "etag": info.get("etag"),
            "last_modified": info.get("last-modified"),
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "downloaded": False,
        }
        print(f"    新固件! {fname} ({size/1048576:.1f} MB, fp={fp})")
        new_items.append(item)

        if not dry_run:
            dest = downloads / fname
            print(f"    下载到 {dest} ...")
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
                    while chunk := r.read(1024 * 1024):
                        f.write(chunk)
                item["downloaded"] = True
                item["sha256"] = hashlib.sha256(dest.read_bytes()).hexdigest()
                # 下载后可接 firmware_inspect 做解包分析
            except Exception as e:
                print(f"[!] 下载失败: {e}")
                if dest.exists():
                    dest.unlink()

    if new_items:
        index["firmware"].extend(new_items)
        if not dry_run:
            Path("firmware_index.json").write_text(
                json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[+] firmware_index.json 已更新,新增 {len(new_items)} 条")
    else:
        print("[+] 没有发现新固件")
    return new_items


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", default="sources.json")
    ap.add_argument("--downloads", default="downloads")
    ap.add_argument("--dry-run", action="store_true", help="只检测不下载")
    args = ap.parse_args()

    downloads = Path(args.downloads)
    if not args.dry_run:
        downloads.mkdir(parents=True, exist_ok=True)
    new = track(Path(args.sources), downloads, args.dry_run)
    # 供 GitHub Actions 判断是否需要发 Release
    (Path("new_firmware.json")).write_text(
        json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
