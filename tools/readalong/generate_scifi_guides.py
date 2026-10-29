#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate guide.html for Sci-Fi audiobooks based on authoritative literature guidelines.
"""
import os
import sys
from bs4 import BeautifulSoup

BASE_DIR = "/Volumes/750/Music/有声书/科幻"

TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>《{title_cn}》深度导读手札 · {author_cn}</title>
  <style>
    :root {{
      --bg-page: #fbf9f4;
      --bg-card: #ffffff;
      --bg-subtle: #f4efe4;
      --border: rgba(30, 36, 32, 0.08);
      --border-accent: rgba(140, 45, 25, 0.25);
      --text-main: #1c221e;
      --text-muted: #59645f;
      --text-soft: #84908a;
      --accent: #8c2d19;
      --accent-subtle: rgba(140, 45, 25, 0.08);
      --accent-blue: #1d3557;
      --accent-blue-subtle: rgba(29, 53, 87, 0.08);
      --font-serif: "Songti SC", "Source Han Serif CN", Georgia, "Noto Serif CJK SC", serif;
      --font-sans: system-ui, -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
      --shadow-md: 0 6px 20px rgba(0, 0, 0, 0.06);
      --radius: 12px;
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg-page: #131619;
        --bg-card: #1c2025;
        --bg-subtle: #242930;
        --border: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(224, 114, 91, 0.35);
        --text-main: #e5e8eb;
        --text-muted: #9aa3ab;
        --text-soft: #6d767f;
        --accent: #e0725b;
        --accent-subtle: rgba(224, 114, 91, 0.14);
        --accent-blue: #5b9bd5;
        --accent-blue-subtle: rgba(91, 155, 213, 0.14);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 6px 20px rgba(0, 0, 0, 0.4);
      }}
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
    body {{
      background-color: var(--bg-page);
      color: var(--text-main);
      font-family: var(--font-sans);
      font-size: 15.5px;
      line-height: 1.8;
      padding: 24px 16px 88px;
    }}

    .container {{
      max-width: 760px;
      margin: 0 auto;
    }}

    /* 顶部 Hero 总览 */
    .hero {{
      text-align: center;
      padding: 32px 20px 26px;
      margin-bottom: 24px;
      background: var(--bg-card);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 4px;
      background: linear-gradient(90deg, var(--accent), var(--accent-blue));
    }}
    .hero-badge {{
      display: inline-block;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      padding: 3px 12px;
      border-radius: 20px;
      background: var(--accent-subtle);
      color: var(--accent);
      margin-bottom: 12px;
    }}
    .hero h1 {{
      font-family: var(--font-serif);
      font-size: 29px;
      font-weight: 700;
      line-height: 1.3;
      margin-bottom: 6px;
      color: var(--text-main);
    }}
    .hero-sub {{
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 16px;
    }}
    .hero-quote {{
      font-family: var(--font-serif);
      font-style: italic;
      font-size: 15px;
      color: var(--accent);
      background: var(--bg-subtle);
      padding: 10px 18px;
      border-radius: 8px;
      display: inline-block;
      max-width: 90%;
    }}

    /* 全局展开/收起控制栏 */
    .toggle-toolbar {{
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-bottom: 14px;
    }}
    .toggle-btn {{
      font-size: 12.5px;
      color: var(--text-muted);
      background: var(--bg-card);
      border: 1px solid var(--border);
      padding: 4px 12px;
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .toggle-btn:hover {{
      color: var(--accent);
      border-color: var(--border-accent);
      background: var(--bg-subtle);
    }}

    /* 手风琴栏目样式 */
    .guide-section {{
      background: var(--bg-card);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      margin-bottom: 14px;
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .guide-section[open] {{
      box-shadow: var(--shadow-md);
      border-color: var(--border-accent);
    }}

    .section-summary {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      cursor: pointer;
      user-select: none;
      outline: none;
      list-style: none;
      background: var(--bg-card);
      transition: background-color 0.2s ease;
    }}
    .section-summary::-webkit-details-marker {{ display: none; }}
    .section-summary:hover {{
      background-color: var(--bg-subtle);
    }}

    .summary-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .section-idx {{
      font-family: var(--font-serif);
      font-size: 12.5px;
      font-weight: 700;
      color: var(--accent);
      background: var(--accent-subtle);
      padding: 2px 8px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}
    .section-title {{
      font-family: var(--font-serif);
      font-size: 17.5px;
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.2px;
    }}
    .summary-toggle-icon {{
      font-size: 15px;
      font-weight: 300;
      color: var(--text-soft);
      transition: transform 0.25s ease;
      width: 20px;
      text-align: center;
    }}
    .guide-section[open] .summary-toggle-icon {{
      transform: rotate(45deg);
      color: var(--accent);
    }}

    .section-content {{
      padding: 6px 20px 22px;
      border-top: 1px solid var(--border);
      font-size: 15px;
      line-height: 1.8;
      color: var(--text-main);
    }}

    /* 模块内排版与小组件 */
    .specs-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 14px 0;
    }}
    .spec-item {{
      background: var(--bg-subtle);
      padding: 10px 12px;
      border-radius: 8px;
    }}
    .spec-label {{
      font-size: 11.5px;
      color: var(--text-soft);
      margin-bottom: 2px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .spec-val {{
      font-weight: 600;
      font-size: 13.5px;
      color: var(--text-main);
    }}

    .card-box {{
      background: var(--bg-subtle);
      border-radius: 8px;
      padding: 12px 16px;
      margin: 12px 0;
      font-size: 14.5px;
    }}
    .card-box-accent {{
      background: var(--accent-subtle);
      border-left: 3px solid var(--accent);
      border-radius: 0 8px 8px 0;
      padding: 12px 16px;
      margin: 12px 0;
      font-size: 14.5px;
    }}

    .sub-heading {{
      font-family: var(--font-serif);
      font-size: 15.5px;
      font-weight: 700;
      color: var(--accent-blue);
      margin: 18px 0 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .sub-heading::before {{
      content: "▪";
      color: var(--accent);
      font-size: 13px;
    }}

    /* SVG 矢量图容器 */
    .svg-wrap {{
      width: 100%;
      margin: 16px 0;
      padding: 16px 8px;
      background: var(--bg-subtle);
      border-radius: 10px;
      text-align: center;
      overflow-x: auto;
    }}
    .svg-wrap svg {{
      max-width: 100%;
      height: auto;
      display: inline-block;
    }}

    /* 列表与引用 */
    ul.bullet-list, ol.num-list {{
      padding-left: 20px;
      margin: 8px 0 12px;
    }}
    ul.bullet-list li, ol.num-list li {{
      font-size: 14.5px;
      color: var(--text-muted);
      margin-bottom: 6px;
      line-height: 1.7;
    }}
    ul.bullet-list li strong, ol.num-list li strong {{
      color: var(--text-main);
    }}

    .quote-block {{
      font-family: var(--font-serif);
      font-size: 14.5px;
      line-height: 1.7;
      padding: 12px 16px;
      background: var(--accent-blue-subtle);
      border-left: 3px solid var(--accent-blue);
      border-radius: 0 8px 8px 0;
      color: var(--text-main);
      margin: 12px 0;
    }}

    /* 页脚 */
    footer {{
      text-align: center;
      padding: 32px 0 12px;
      font-size: 13px;
      color: var(--text-soft);
      border-top: 1px dashed var(--border);
      margin-top: 36px;
    }}
  </style>
</head>
<body>

<div class="container">

  <!-- 顶部总览 Hero -->
  <header class="hero">
    <div class="hero-badge">深度文学导读 · 思维显微镜</div>
    <h1>{title_cn} ({title_en})</h1>
    <p class="hero-sub">{author_cn}（{author_en}）· {sub_desc}</p>
    <div class="hero-quote">
      “{hero_quote}”
    </div>
  </header>

  <!-- 全局展开/收起控制栏 -->
  <div class="toggle-toolbar">
    <button class="toggle-btn" onclick="toggleAllSections(true)">展开全部</button>
    <button class="toggle-btn" onclick="toggleAllSections(false)">收起全部</button>
  </div>
"""

TEMPLATE_FOOT = """
  <footer>
    <p>Rosemary Garden（花园读书）· 文学与科幻深度导读体系</p>
    <p style="margin-top:4px; font-size:12px;">© 基于规范提示词与自包含 HTML 标准交付 · 专为移动端与深度阅读优化</p>
  </footer>

</div>

<!-- 原生交互控制脚本：支持一键展开/收起全部栏目 -->
<script>
  function toggleAllSections(openState) {
    const sections = document.querySelectorAll(".guide-section");
    sections.forEach(sec => {
      sec.open = openState;
    });
  }
</script>

</body>
</html>
"""

def render_section(idx, title, content_html, is_open=False):
    open_attr = " open" if is_open else ""
    return f"""  <!-- 栏目 {idx:02d} · {title} -->
  <details class="guide-section"{open_attr}>
    <summary class="section-summary">
      <div class="summary-left">
        <span class="section-idx">{idx:02d}</span>
        <h2 class="section-title">{title}</h2>
      </div>
      <span class="summary-toggle-icon">+</span>
    </summary>
    <div class="section-content">
{content_html}
    </div>
  </details>
"""
