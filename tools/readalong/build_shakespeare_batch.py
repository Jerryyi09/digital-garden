#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate guide.html for all Shakespeare and Drama audiobooks based on authoritative guidelines.
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def make_guide(data, sections):
    body = TEMPLATE_HEAD.format(**data)
    for idx, title, content, is_open in sections:
        body += render_section(idx, title, content, is_open)
    body += TEMPLATE_FOOT
    return body

def build_hamlet():
    data = {
        "title_cn": "哈姆雷特",
        "title_en": "Hamlet",
        "author_cn": "威廉·莎士比亚",
        "author_en": "William Shakespeare",
        "sub_desc": "世界四大悲剧之冠 · 存在主义的困惑与延宕之谜",
        "hero_quote": "生存还是毁灭，这是一个值得思考的问题：是默然忍受命运暴虐的毒箭，还是挺身反抗人世无涯的苦难？"
    }
    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">作者</div><div class="spec-val">莎士比亚 (1564–1616)</div></div>
        <div class="spec-item"><div class="spec-label">创作年份</div><div class="spec-val">约 1599–1601 年</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">复仇悲剧 / 哲学心理剧</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">全五幕 · 约 3 万词诗剧</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">14+ 岁 / 中学与青年经典</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">心理独白深度与道德困境</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把哈姆雷特的“延宕”简单归结为性格软弱懦弱。他面对的是一个彻底失序的时代（“时代脱臼了，倒霉的我却要把它扶正”）。他在行动前必须先确证正义的绝对依据，这种对道德证据的洁癖与对灵魂后果的深思，正是现代知识分子精神觉醒的最初标志。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 灵魂独白对人类存在的极度拷问：</strong>全剧七次关键独白，展现了理性面对死亡、虚伪与信仰瓦解时的惊人深度。</div>
      <div class="card-box"><strong>② “戏中戏”作为真相试金石的艺术构思：</strong>借《捕鼠机》的戏剧演出刺探叔父克劳狄斯的罪恶灵魂。</div>
      <div class="card-box"><strong>③ 绝望中的诗意升华：</strong>奥菲利亚的落水而亡与掘墓人场景，构成了对虚荣世俗的终极解构。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">文艺复兴晚期人文主义理想在封建宫廷与近代现实碰撞下的深刻危机。丹麦埃尔西诺城堡化为一座幽闭的心理囚笼。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <style>
            .hb-box { rx: 8; stroke-width: 1.5; }
            .hb-bg-prince { fill: #1d3557; stroke: #2a4d7a; }
            .hb-bg-king { fill: #8c2d19; stroke: #a33b24; }
            .hb-bg-ophelia { fill: #fbf9f4; stroke: #2a9d8f; stroke-width:2; }
            .hb-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 600; text-anchor: middle; }
            .hb-t-d { fill: #1c221e; font-family: sans-serif; font-size: 12.5px; font-weight: 600; text-anchor: middle; }
            .hb-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10px; text-anchor: middle; }
            .hb-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10px; text-anchor: middle; }
            .hb-line { stroke: #8c2d19; stroke-width: 1.8; fill: none; }
          </style>
          <!-- 哈姆雷特 -->
          <rect x="240" y="20" width="200" height="85" class="hb-box hb-bg-prince" />
          <text x="340" y="50" class="hb-t-w">哈姆雷特 (Hamlet)</text>
          <text x="340" y="70" class="hb-t-sub-w">丹麦王子 · 人文主义理想之子</text>
          <text x="340" y="90" class="hb-t-sub-w">装疯求证 · 灵魂延宕与深刻绝望</text>

          <!-- 弑兄篡位的叔父与母后 -->
          <rect x="30" y="150" width="180" height="95" class="hb-box hb-bg-king" />
          <text x="120" y="180" class="hb-t-w">克劳狄斯 / 乔特鲁德</text>
          <text x="120" y="200" class="hb-t-sub-w">篡位毒杀 / 伦理失序</text>
          <text x="120" y="220" class="hb-t-sub-w">罪孽深重却无法真诚祈祷</text>

          <!-- 冲突对立连线 -->
          <path d="M 240 65 L 120 150" class="hb-line" />
          <text x="170" y="95" style="fill:#8c2d19; font-size:11px; font-weight:600;">弑父血仇与虚伪揭露</text>

          <!-- 奥菲利亚与波洛涅斯 -->
          <rect x="470" y="150" width="180" height="95" class="hb-box hb-bg-ophelia" />
          <text x="560" y="180" class="hb-t-d">奥菲利亚 / 波洛涅斯</text>
          <text x="560" y="200" class="hb-t-sub">纯真牺牲品 / 谄媚弄权老臣</text>
          <text x="560" y="220" class="hb-t-sub">溺水凋零 · 雷欧提斯的复仇之剑</text>

          <path d="M 440 65 L 560 150" class="hb-line" style="stroke:#2a9d8f;" />
          <text x="510" y="95" style="fill:#2a9d8f; font-size:11px; font-weight:600;">爱意撕裂与牺牲</text>
        </svg>
      </div>
      <div class="sub-heading">核心人物速查</div>
      <ul class="bullet-list">
        <li><strong>哈姆雷特：</strong>具有哲学家气质的悲剧英雄，在腐烂的世道中承担起纠正乾坤的沉重使命。</li>
        <li><strong>克劳狄斯：</strong>残忍狡黠的马基雅维利式政客，其在祷告时的独白揭示了罪恶与灵魂的死锁。</li>
        <li><strong>奥菲利亚：</strong>父权与宫廷政治的无辜牺牲品，纯洁的情感被撕得粉碎后在歌声中溺水而亡。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面与深处</div>
      <p>表面上是一个王子复仇的故事；深处触碰了人类理智对现实罪恶的绝望反抗。当整个世界的道德基石崩塌，个体究竟应该麻木顺从，还是以毁灭自身为代价撞击坚壁？</p>"""

    sec04 = """      <div class="sub-heading">叙事核心与转折</div>
      <p>第三幕第二场“戏中戏”是决定性转折：克劳狄斯的离席尖叫坐实了鬼魂的控诉，哈姆雷特彻底拿到了行动的道义依据，全剧从此走向不可逆的流血杀局。</p>"""

    sec05 = """      <div class="sub-heading">人性的深度解构</div>
      <p>哈姆雷特的伟大不在于没有弱点，而在于他毫无遮掩地审视自己的每一个幽微念头。他不怕死，但害怕“死后的未知梦境”，这种对永恒的敬畏使人类的盲目行动停下了脚步。</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>鬼魂与铠甲：</strong>已故老王的幽灵，象征着未酬的历史正义与沉重的过去召唤。</li>
        <li><strong>约里克的头骨：</strong>掘墓人挖出的弄臣头骨。王子抚摸白骨的独白，是文学史上对死亡与人生虚妄最透彻的解构。</li>
        <li><strong>毒药与毒剑：</strong>从灌入耳中的毒液到决斗抹毒的剑尖，象征着谎言腐蚀机体的致命机制。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        <strong>表层：</strong>埃尔西诺宫廷中的复仇、阴谋与决斗惨剧。<br>
        <strong>深层：</strong>人文主义理智在腐烂政治现实面前的幻灭与延宕之谜。<br>
        <strong>根本：</strong>人类面对死亡、终极正义与存在意义时的永恒彷徨。
      </div>"""

    sec08 = """      <div class="sub-heading">解释边界</div>
      <p>不要滥用现代精神分析将哈姆雷特定性为“俄狄浦斯情结病态狂”。莎士比亚植根于近代黎明，他写的是知行脱节的哲学悲剧，而非精神病院的病理报告。</p>"""

    sec09 = """      <div class="sub-heading">现实关联</div>
      <p>面对职场或社会的潜规则，我们常常如同哈姆雷特：看透了荒谬，却因深思熟虑而迟疑不决。如何在复杂博弈中保持内心的纯洁与果敢？</p>"""

    sec10 = """      <div class="sub-heading">30秒日常版</div>
      <p>“《哈姆雷特》不是简单的王子复仇记，而是一个天才面对虚伪现实时的高难度反抗。他的迟疑不是胆怯，而是当世界脱臼时，清醒者对生命和正义代价的无上敬畏。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>第三幕第一场（“生存还是毁灭”独白） · 第五幕第一场（掘墓人与头骨对话）。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1：</strong>如果不延宕，哈姆雷特第一时间杀死叔父，他会成为一个更好的国王，还是另一个克劳狄斯？
      </div>
      <div class="card-box">
        <strong>Q2：</strong>在不义的体制中，为了求真而伪装发疯，最终是拯救了灵魂还是失去了自我？
      </div>"""

    sec13 = """      <div class="sub-heading">思维工具：“捕鼠机测试”</div>
      <p>当你需要识破某个隐藏极深的谎言时，不要直接正面对峙，而是搭建一个逼真的情境模型，观察对方在微小应激下的本能反应。</p>"""

    sections = [
        (1, "头部速览与阅读看点", sec01, True),
        (2, "时代背景与人物/线索地图", sec02, True),
        (3, "真实感知：作品让我们看见了什么", sec03, False),
        (4, "叙事建模：故事是如何搭起来的", sec04, False),
        (5, "人物细读：复杂人性的深度剖析", sec05, False),
        (6, "语言与象征：文学肌理的精细解读", sec06, False),
        (7, "主题辨析：作品到底在追问什么难题", sec07, False),
        (8, "不确定性判断：开放但有边界的解释", sec08, False),
        (9, "价值辨别：作品与我们的现实关系", sec09, False),
        (10, "表达协作：如何把作品讲给别人听", sec10, False),
        (11, "极简路径：如果只读一章/一段/一幕", sec11, False),
        (12, "五个苏格拉底式深想问题", sec12, False),
        (13, "创造行动：把作品转化为思考与写作工具", sec13, False),
    ]
    return make_guide(data, sections)

print("Hamlet builder ready.")
