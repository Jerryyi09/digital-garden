#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from bs4 import BeautifulSoup

from scifi_time_machine import get_time_machine_guide
from scifi_war_of_worlds import get_war_of_worlds_guide
from scifi_invisible_man import get_invisible_man_guide
from scifi_100_short_stories import get_100_short_stories_guide
from scifi_top_fantasy import get_top_fantasy_guide

SCIFI_MAP = {
    "科幻-时间机器": get_time_machine_guide,
    "科幻-世界大战": get_war_of_worlds_guide,
    "科幻-隐形人": get_invisible_man_guide,
    "100 Great Science Fiction Short Short Stories": get_100_short_stories_guide,
    "Top Sci-Fi and Fantasy": get_top_fantasy_guide,
}

BASE_DIR = "/Volumes/750/Music/有声书/科幻"

def main():
    print("=== 开始批量构建【科幻】目录深度导读 guide.html ===")
    total = len(SCIFI_MAP)
    success = 0

    for book_folder, generator in SCIFI_MAP.items():
        target_dir = os.path.join(BASE_DIR, book_folder)
        if not os.path.exists(target_dir):
            print(f"[ERROR] 目录不存在: {target_dir}")
            continue

        html_content = generator()

        # 结构校验
        soup = BeautifulSoup(html_content, "html.parser")
        sections = soup.find_all("details", class_="guide-section")
        if len(sections) != 13:
            print(f"[FAIL] {book_folder} 栏目数不为 13 (当前: {len(sections)})")
            continue

        for i, sec in enumerate(sections, 1):
            if not sec.find("summary", class_="section-summary") or not sec.find("div", class_="section-content"):
                print(f"[FAIL] {book_folder} 栏目 {i} summary/content 结构不完整")
                continue

        svgs = soup.find_all("svg")
        if len(svgs) < 1:
            print(f"[FAIL] {book_folder} 缺少原生 SVG 矢量图")
            continue

        # 写入 guide.html
        guide_html_path = os.path.join(target_dir, "guide.html")
        with open(guide_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 写入 guide.index 兼容
        guide_index_path = os.path.join(target_dir, "guide.index")
        with open(guide_index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_size = os.path.getsize(guide_html_path)
        print(f"[OK] {book_folder} -> guide.html ({file_size} 字节, 13 栏目全绿, SVG 嵌入成功)")
        success += 1

    print(f"\n=== 科幻目录构建完成: {success}/{total} 部作品通过校验并落盘 ===")

if __name__ == "__main__":
    main()
