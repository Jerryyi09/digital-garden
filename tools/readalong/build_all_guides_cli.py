#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rosemary Garden Audiobook Guide Generator CLI
Unified runner for Literature & Sci-Fi book guide production.
"""
import os
import sys
import subprocess

def run_step(cmd, desc):
    print(f"\n>>> 正在执行: {desc}")
    res = subprocess.run(cmd, shell=True, env=dict(os.environ, PYTHONPATH="tools/readalong"))
    if res.returncode != 0:
        print(f"[FAIL] 执行失败: {desc} (退出码: {res.returncode})")
        sys.exit(res.returncode)
    print(f"[SUCCESS] {desc} 完成")

def main():
    print("====================================================")
    print("  Rosemary Garden 有声书深度导读 (guide.html) 生成系统")
    print("====================================================")
    run_step("python3 tools/readalong/build_all_scifi.py", "构建科幻作品深度导读 (5部)")
    run_step("python3 tools/readalong/build_batch_a.py", "构建文学作品批次 A (莎士比亚戏剧系列 10部)")
    run_step("python3 tools/readalong/build_batch_b.py", "构建文学作品批次 B (欧洲现实主义巨著 13部)")
    run_step("python3 tools/readalong/build_batch_c.py", "构建文学作品批次 C (美国经典与心灵成长 14部)")
    run_step("python3 tools/readalong/build_batch_d.py", "构建文学作品批次 D (哲学意识流与现当代 12部)")
    print("\n====================================================")
    print("  全量 57 部作品 guide.html & guide.index 生成完毕！")
    print("====================================================")

if __name__ == "__main__":
    main()
