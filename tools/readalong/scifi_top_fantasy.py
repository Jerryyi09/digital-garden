# -*- coding: utf-8 -*-
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_top_fantasy_guide():
    data = {
        "title_cn": "世界顶级科幻与奇幻经典总览",
        "title_en": "Top Sci-Fi and Fantasy",
        "author_cn": "欧美权威书评与经典导读组",
        "author_en": "Curated Classics Edition",
        "sub_desc": "想象力文学的双峰对决 · 从硬核物理推演到心灵史诗神话",
        "hero_quote": "科幻探索我们向外走能走多远，奇幻追问我们向内探能探多深；它们共同守护着人类仰望星空的权利。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item">
          <div class="spec-label">编选体系</div>
          <div class="spec-val">世界科幻与奇幻文库典藏精选</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">坐标跨度</div>
          <div class="spec-val">托尔金 / 阿西莫夫 / 勒瑰恩 / 赫伯特等</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">体裁坐标</div>
          <div class="spec-val">史诗奇幻 · 硬科幻 · 太空歌剧 · 乌托邦文学</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">全书体量</div>
          <div class="spec-val">跨世纪经典多轨系统导读</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">建议阅读年龄</div>
          <div class="spec-val">12+ 岁 / 青少年与通识经典阅读</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">核心判断标准</div>
          <div class="spec-val">世界模型构筑完整度与人性哲学深度</div>
        </div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把科幻和奇幻当成毫无营养的逃避现实消遣（Escapism）。如J.R.R.托尔金所言：<strong>“监狱守卫最痛恨的，正是囚犯渴望越狱的雄心。”</strong>优秀的幻想文学不是逃离真实，而是借由暂时悬置物理或世俗法则，直抵人类生存的深层价值核心。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 两种截然不同却互相照耀的“世界模型”：</strong>科幻依赖“推演（Extrapolation）”，追问“如果这项科技成真，社会将如何变化”；奇幻依赖“神话与潜意识投影”，追问“面对古老的诱惑与黑暗，人类如何守住灵魂”。
      </div>
      <div class="card-box">
        <strong>② 宏大叙事中的道德试炼（The Moral Crucible）：</strong>无论是至尊魔戒对权力的诱惑，还是香料对银河帝国的垄断腐蚀，幻想文学巨作总能将人类复杂的政治与道德抉择推向戏剧化极致。
      </div>
      <div class="card-box">
        <strong>③ 跨学科通识视野的全面启蒙：</strong>涉及语言学创造（如精灵语）、生态学推演（如沙丘生态链）、天体物理学、宗教学、人类学等，是培养青年博雅通识素养的最佳熔炉。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        从工业革命以来的科学理智飞跃，到两次世界大战后人类对精神家园的寻觅，科幻与奇幻共同构成了二十世纪最磅礴的文学奇观。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tf-box { rx: 8; stroke-width: 1.5; }
            .tf-bg-core { fill: #fbf9f4; stroke: #1c221e; stroke-width: 2; }
            .tf-bg-scifi { fill: #1d3557; stroke: #2a4d7a; }
            .tf-bg-fant { fill: #8c2d19; stroke: #a33b24; }
            .tf-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 600; text-anchor: middle; }
            .tf-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tf-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tf-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tf-line-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .tf-line-red { stroke: #8c2d19; stroke-width: 2; fill: none; }
          </style>

          <defs>
            <marker id="tf-arr-b" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#1d3557" />
            </marker>
            <marker id="tf-arr-r" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 核心：人类生存处境 -->
          <rect x="250" y="115" width="180" height="90" class="tf-box tf-bg-core" />
          <text x="340" y="145" class="tf-t-d">人类生存与文明命题</text>
          <text x="340" y="165" class="tf-t-sub">爱与恐惧 · 权力与牺牲</text>
          <text x="340" y="185" class="tf-t-sub">意义追求 · 存在追问</text>

          <!-- 向左：科幻推演轴 -->
          <path d="M 250 160 L 175 160" class="tf-line-blue" marker-end="url(#tf-arr-b)" />
          <rect x="15" y="55" width="155" height="210" class="tf-box tf-bg-scifi" />
          <text x="92" y="85" class="tf-t-w">科幻探索维度 (Sci-Fi)</text>
          <text x="92" y="115" class="tf-t-sub-w">【认知推演引擎】</text>
          <text x="92" y="140" class="tf-t-sub-w">物理法则与技术外推</text>
          <text x="92" y="165" class="tf-t-sub-w">宇宙尺度与异星接触</text>
          <text x="92" y="190" class="tf-t-sub-w">社会系统与未来政治</text>
          <text x="92" y="215" class="tf-t-sub-w">代表：基地 · 沙丘 · 2001</text>
          <text x="92" y="240" style="fill:#90e0ef; font-size:11px; text-anchor:middle;">“向外走的边界”</text>

          <!-- 向右：奇幻神话轴 -->
          <path d="M 430 160 L 505 160" class="tf-line-red" marker-end="url(#tf-arr-r)" />
          <rect x="510" y="55" width="155" height="210" class="tf-box tf-bg-fant" />
          <text x="587" y="85" class="tf-t-w">奇幻神话维度 (Fantasy)</text>
          <text x="587" y="115" class="tf-t-sub-w">【心灵原型剧场】</text>
          <text x="587" y="140" class="tf-t-sub-w">英雄旅程与精神试炼</text>
          <text x="587" y="165" class="tf-t-sub-w">善恶交锋与内在诱惑</text>
          <text x="587" y="190" class="tf-t-sub-w">魔法法则与古老盟约</text>
          <text x="587" y="215" class="tf-t-sub-w">代表：魔戒 · 地海 · 冰与火</text>
          <text x="587" y="240" style="fill:#fbc4ab; font-size:11px; text-anchor:middle;">“向内探的深渊”</text>
        </svg>
      </div>

      <div class="sub-heading">两大体系支柱</div>
      <ul class="bullet-list">
        <li><strong>科幻的理性推演法则：</strong>即使设定再超前，必须遵循逻辑的一致性（Cognitive Estrangement）。它锻炼读者对复杂技术社会后果的前瞻推断力。</li>
        <li><strong>奇幻的道德象征网络：</strong>魔法从来不是万能的逃避，它往往伴随着沉重的代价。它训练读者辨识内心的贪婪、懦弱与英雄主义情怀。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事</div>
      <p>从宇宙尽头的星际联邦、帝国兴衰史，到中土大地的护戒远征、巨龙苏醒与魔法学院试炼。汇聚了全球二十位殿堂级作家的叙事精髓与世界观架构。</p>

      <div class="sub-heading">深处真正关心什么</div>
      <p>作品关心<strong>“人类在已知边界之外如何界定自我”</strong>。不管是飞入冰冷无垠的深空，还是步入幽暗古老的森林，人类真正寻找的永远是同情、正义与心灵救赎的支点。</p>"""

    sec04 = """      <div class="sub-heading">叙事建模的两大范式</div>
      <div class="card-box">
        <strong>范式 A · 英雄的启程与回归（坎贝尔单子神话）：</strong>平凡世界的召唤 → 跨越第一道门槛 → 试炼深渊与绝境置死地 → 获得神符与智慧 → 带着救赎回归（如《魔戒》《地海巫师》）。<br><br>
        <strong>范式 B · 技术文明异化推演链条：</strong>核心技术假设提出 → 社会结构沿逻辑自洽重组 → 阶级或物种利益不可调和冲突爆发 → 寻找文明存续妥协之路（如《沙丘》《银河帝国》）。
      </div>"""

    sec05 = """      <div class="sub-heading">人物宿命与复杂性</div>
      <p>伟大的幻想文学绝不设立非黑即白的扁平角色。魔戒的持有者佛罗多在最后关头险些沦陷；沙丘的保罗深知自己引发的圣战将导致数百亿人死亡却无从逆转。这种崇高的宿命悲剧感赋予了幻想文学不输严肃纯文学的厚重分量。</p>"""

    sec06 = """      <div class="sub-heading">语言肌理与世界构筑（Worldbuilding）</div>
      <p>优秀的作者不依赖陈腔滥调的说明性灌输（Exposition Dump），而是像考古学家一样，通过一句地方俗谚、一柄古剑的纹饰、一套奇怪的礼节，让读者在字里行间呼吸到那个世界的真实尘土与空气。</p>"""

    sec07 = """      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        <strong>表层：</strong>波澜壮阔的史诗冒险与奇绝瑰丽的异星奇观。<br>
        <strong>深层：</strong>对权力意志、技术专制、生态平衡与文明周期的深刻推演。<br>
        <strong>根本：</strong>在无限宇宙中确认人类微小而坚韧的道德主体性。
      </div>"""

    sec08 = """      <div class="sub-heading">警惕空洞的奇观崇拜</div>
      <p>阅读时切忌只记住炫酷的机甲参数或华丽的魔法咒语。那些只是舞台灯光，真正驱动经典的永远是灯光下那个满身尘土、在道德悬崖边痛苦抉择的人类灵魂。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>现代人常常被眼前碎片的世俗琐事困锁，丧失了对远方与历史的宏观视野。幻想文学是一台精神望远镜，拉开时空焦距，让我们跳出内卷与焦虑，用百万年和亿万光年的尺度重新审视当下的生命意义。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版</div>
      <p>“幻想文学不是胡思乱想，而是人类最高级的思想实验室。科幻让我们看清科技发展的隐秘悬崖，奇幻让我们看清内心深处的幽微神魔。读懂它们，你才拥有了一套完整的现代精神宇宙观。”</p>"""

    sec11 = """      <div class="sub-heading">入门进阶经典书单</div>
      <ul class="bullet-list">
        <li><strong>科幻入门：</strong>阿瑟·克拉克《童年的终结》 · 艾萨克·阿西莫夫《神们自己》 · 弗兰克·赫伯特《沙丘》。</li>
        <li><strong>奇幻巅峰：</strong>J.R.R.托尔金《魔戒》 · 厄休拉·勒瑰恩《地海巫师》 · 乔治·马丁《冰与火之歌》。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 真实与虚构的辩证：</strong>为什么有时候一个完全虚构的异星社会，比我们每天生活的现实世界更能暴露人性的真相？
      </div>
      <div class="card-box">
        <strong>Q2 · 力量的代价：</strong>在所有伟大的幻想故事里，为什么至高无上的超强力量最终总是伴随着悲惨的反噬与孤独？
      </div>"""

    sec13 = """      <div class="sub-heading">① 世界观构建演练：“三法则世界建模”</div>
      <p><strong>法则一（物理底线）：</strong>设定一个不同于地球的微小自然法则（如“陆地上没有金属”或“重力是地球的三倍”）；<br>
      <strong>法则二（社会回响）：</strong>推导这个物理法则如何深刻重构该社会的建筑、家庭与权力阶层；<br>
      <strong>法则三（冲突焦点）：</strong>写一个在该世界中生活的小人物，为了追求爱情或尊严所遭遇的制度死结。</p>"""

    sections_data = [
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

    body_html = TEMPLATE_HEAD.format(**data)
    for idx, title, content, is_open in sections_data:
        body_html += render_section(idx, title, content, is_open)
    body_html += TEMPLATE_FOOT

    return body_html
