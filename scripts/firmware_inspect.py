#!/usr/bin/env python3
"""固件解包分析工具。

对 OTA 包 / rootfs / boot 镜像做自动化分析:
  - 识别文件类型 (zip OTA / Rockchip update.img / ext4 sparse / 原始镜像)
  - 从 zip OTA 中提取 build.prop、oem.prop 等
  - 在镜像中扫描设备树 model 字符串 (/proc/device-tree/model 特征)
  - 输出 JSON 报告 + Markdown 摘要,可直接用于补充 README 映射表

用法:
  python firmware_inspect.py <固件文件> [-o 输出目录]
  python firmware_inspect.py <目录>      # 批量分析目录下所有固件
"""

import argparse
import hashlib
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

# 设备树 model 典型特征,用于在二进制中定位 dts_model
MODEL_PATTERNS = [
    re.compile(rb"(Rockchip[ -~]{4,120}Board)"),
    re.compile(rb"(Rockchip[ -~]{4,120}version)"),
    re.compile(rb"(Cvitek[ -~]{4,120}version)"),
]

# 常见属性文件名(在 OTA zip 中查找)
PROP_FILES = ("build.prop", "oem.prop", "vendor/build.prop", "system/build.prop",
              "odm/etc/build.prop", "product/build.prop")


def sha256(path: Path, limit: int = 64 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def detect_format(path: Path) -> str:
    with open(path, "rb") as f:
        head = f.read(16)
    if head[:4] == b"PK\x03\x04":
        return "zip"
    if head[:4] == b"RKAF":
        return "rockchip-update-img"
    if head[:4] == b"\x3a\xff\x26\xed":
        return "android-sparse"
    if head[:2] == b"\x53\xef":  # ext4 superblock @1024
        return "ext4"
    return "raw"


def scan_models(data: bytes) -> list[str]:
    """在二进制数据中寻找设备树 model 字符串。"""
    found = []
    for pat in MODEL_PATTERNS:
        for m in pat.finditer(data):
            s = m.group(1).decode("ascii", "replace").strip("\x00\r\n")
            if s not in found:
                found.append(s)
    return found


def scan_file_models(path: Path, chunk_size: int = 16 * 1024 * 1024) -> list[str]:
    """流式扫描大文件,块间保留重叠避免跨界漏检。"""
    found: list[str] = []
    overlap = 1024
    with open(path, "rb") as f:
        tail = b""
        while chunk := f.read(chunk_size):
            data = tail + chunk
            for m in scan_models(data):
                if m not in found:
                    found.append(m)
            tail = data[-overlap:]
    return found


def parse_props(text: str) -> dict[str, str]:
    props = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            props[k.strip()] = v.strip()
    return props


def inspect_zip(path: Path) -> dict:
    info: dict = {"format": "zip", "props": {}, "inner_files_sample": []}
    interesting = ("rootfs", "boot", "update", "ota", "image", ".img", ".ext4",
                   ".bin", "build.prop", "prop")
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        info["entry_count"] = len(names)
        info["inner_files_sample"] = names[:60]
        for name in names:
            base = name.split("/")[-1]
            if base in ("build.prop", "oem.prop") or name in PROP_FILES:
                try:
                    info["props"].update(parse_props(z.read(name).decode("utf-8", "replace")))
                except Exception:
                    pass
        # 逐个提取 zip 内的镜像文件做 model 扫描(限制大小,防止内存爆掉)
        for name in names:
            data = z.getinfo(name)
            if data.file_size > 800 * 1024 * 1024:
                continue
            base = name.split("/")[-1]
            if any(k in base.lower() for k in ("rootfs", "boot", "image", ".img", ".ext4")):
                with z.open(name) as f:
                    for m in scan_models(f.read(64 * 1024 * 1024)):
                        info.setdefault("models", [])
                        if m not in info["models"]:
                            info["models"].append(m)
    return info


RKAF_HEADER = struct.Struct("<4sQ16sI")


def inspect_rockchip_img(path: Path) -> dict:
    """Rockchip RKAF update.img: 读取头部并列出内嵌分区表。"""
    info: dict = {"format": "rockchip-update-img", "partitions": [], "models": []}
    with open(path, "rb") as f:
        magic, _, _, chip = RKAF_HEADER.unpack(f.read(RKAF_HEADER.size))
        info["chip"] = chip.rstrip(b"\x00").decode("ascii", "replace")
        raw = f.read(70)
        # 头部后半段包含分区数量与分区项(名称@偏移+大小),此处只取分区名
        n_parts = struct.unpack_from("<I", raw, 50 - 32)[0] if len(raw) >= 50 else 0
        for i in range(min(n_parts, 32)):
            ent = f.read(52)
            if len(ent) < 52:
                break
            name = ent[:32].rstrip(b"\x00").decode("ascii", "replace")
            info["partitions"].append(name)
    info["models"] = scan_file_models(path)
    return info


def inspect(path: Path) -> dict:
    fmt = detect_format(path)
    result = {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "format": fmt,
    }
    try:
        if fmt == "zip":
            result.update(inspect_zip(path))
        elif fmt == "rockchip-update-img":
            result.update(inspect_rockchip_img(path))
        else:
            result["models"] = scan_file_models(path)
    except Exception as e:  # 分析失败不应阻断批量流程
        result["error"] = repr(e)
    # 任何路径下都做一次全文件扫描兜底(zip 内嵌套包常见)
    if "models" not in result or not result.get("models"):
        result["models"] = scan_file_models(path)
    return result


def to_markdown(reports: list[dict]) -> str:
    lines = ["| 文件 | 格式 | 发现的设备树模型 |", "|---|---|---|"]
    for r in reports:
        models = "<br>`".join(r.get("models", [])) or "-"
        lines.append(f"| `{r['file']}` | {r['format']} | `{models}` |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", help="固件文件或目录")
    ap.add_argument("-o", "--out", default="inspect_out", help="报告输出目录")
    args = ap.parse_args()

    target = Path(args.target)
    files = sorted(target.glob("*")) if target.is_dir() else [target]
    files = [f for f in files if f.is_file() and not f.name.startswith(".")]

    reports = []
    for f in files:
        print(f"[*] 分析 {f} ...")
        r = inspect(f)
        reports.append(r)
        print(f"    格式={r['format']} 模型={r.get('models', [])}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    (out / "report.md").write_text(to_markdown(reports), encoding="utf-8")
    print(f"[+] 报告已写入 {out}/report.json 和 {out}/report.md")


if __name__ == "__main__":
    sys.exit(main())
