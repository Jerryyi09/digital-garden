# -*- coding: utf-8 -*-
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_time_machine_guide():
    data = {
        "title_cn": "时间机器",
        "title_en": "The Time Machine",
        "author_cn": "赫伯特·乔治·威尔斯",
        "author_en": "H. G. Wells",
        "sub_desc": "世界科幻小说奠基之作 · 阶级演化与热力学终局预言",
        "hero_quote": "在时间的洪流中，人类不过是微小的浮游生物；文明的自满，终将在熵增的冷酷法则下化为虚无。"
    }

    # Section 01
    sec01 = """      <div class="specs-grid">
        <div class="spec-item">
          <div class="spec-label">作者与生卒</div>
          <div class="spec-val">H·G·威尔斯 (1866–1946)</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">出版年份</div>
          <div class="spec-val">1895 年发表 / 奠定时间旅行范式</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">体裁坐标</div>
          <div class="spec-val">硬核社会学科幻 / 哲学反乌托邦</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">全书体量</div>
          <div class="spec-val">约 3.5 万字（短篇哲理长构）</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">建议阅读年龄</div>
          <div class="spec-val">12+ 岁 / 青年与思辨读者</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">核心判断标准</div>
          <div class="spec-val">演化生物学推演度与阶级批判深度</div>
        </div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《时间机器》当作轻松猎奇的时空冒险爆米花。它本质上是威尔斯运用达尔文进化论与十九世纪末热力学第二定律，对英国维多利亚工业阶级撕裂展开的一场<strong>极度冷酷的末日社会学思想实验</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 颠覆“进步神话”的演化退化论：</strong>维多利亚时期笃信人类将无限繁荣，威尔斯却展示了极度舒适带来的生理与智力全面退化——无痛的乐园就是行尸走肉的屠宰场。
      </div>
      <div class="card-box">
        <strong>② 阶级对立的生物学生理化裂变：</strong>资本家与工人的社会分工，在八十万年后异化为两种完全隔离的物种——地上娇嫩无知的“埃洛伊人”沦为牲畜，地下凶残劳作的“莫洛克人”成为捕食者。
      </div>
      <div class="card-box">
        <strong>③ 宇宙尺度下的终极虚无感：</strong>时间旅行者并未止步于公元八十万年，而是驶向三千万年后的死寂地球——渐冻的残阳、巨蟹与苔藓，展现了早期科幻罕见的崇高与苍凉。
      </div>"""

    # Section 02 (with SVG)
    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪末正值大英帝国工业文明极盛期。达尔文进化论席卷知识界，热力学“宇宙热寂说”引发深刻哲学焦虑。威尔斯结合生物学训练与社会主义思潮，将时间视为第四个维度，推演了人类文明的演化盲区。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tm-box { rx: 8; stroke-width: 1.5; }
            .tm-bg-hero { fill: #1d3557; stroke: #2a4d7a; }
            .tm-bg-eloi { fill: #fbf9f4; stroke: #e0725b; stroke-width: 2; }
            .tm-bg-morlock { fill: #131619; stroke: #59645f; }
            .tm-bg-apoc { fill: #8c2d19; stroke: #a33b24; }
            .tm-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 600; text-anchor: middle; }
            .tm-t-d { fill: #1c221e; font-family: sans-serif; font-size: 12.5px; font-weight: 600; text-anchor: middle; }
            .tm-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tm-t-sub-w { fill: #d5d8dc; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tm-line { stroke: #84908a; stroke-width: 1.4; stroke-dasharray: 4,3; fill: none; }
            .tm-solid { stroke: #8c2d19; stroke-width: 1.8; fill: none; }
            .tm-lbl { font-family: sans-serif; font-size: 10.5px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="tm-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 时间旅行者 (起点) -->
          <rect x="20" y="125" width="140" height="65" class="tm-box tm-bg-hero" />
          <text x="90" y="152" class="tm-t-w">时间旅行者</text>
          <text x="90" y="170" class="tm-t-sub-w">维多利亚理性科学家</text>

          <!-- 穿越箭头 -->
          <path d="M 160 157 L 240 157" class="tm-solid" marker-end="url(#tm-arr)" />
          <text x="200" y="148" class="tm-lbl">穿跃80万年</text>

          <!-- 公元 802,701 年 -->
          <rect x="250" y="25" width="220" height="110" class="tm-box tm-bg-eloi" />
          <text x="360" y="55" class="tm-t-d">地上：埃洛伊人 (Eloi)</text>
          <text x="360" y="75" class="tm-t-sub">柔美稚弱 / 无智无产 / 昔日贵族</text>
          <text x="360" y="95" class="tm-t-sub">白昼狂欢，黑夜陷入原始恐惧</text>
          <text x="360" y="115" class="tm-t-sub">被捕食的“放牧牲畜”</text>

          <!-- 共生捕食连线 -->
          <path d="M 360 135 L 360 175" class="tm-solid" stroke="#8c2d19" />
          <text x="415" y="160" class="tm-lbl">供养与暗夜猎食</text>

          <!-- 地下莫洛克人 -->
          <rect x="250" y="185" width="220" height="110" class="tm-box tm-bg-morlock" />
          <text x="360" y="215" class="tm-t-w">地下：莫洛克人 (Morlocks)</text>
          <text x="360" y="235" class="tm-t-sub-w">白毛如猴 / 畏光工匠 / 昔日工人</text>
          <text x="360" y="255" class="tm-t-sub-w">掌控地下机器与工业维生系统</text>
          <text x="360" y="275" class="tm-t-sub-w">夜出捕食埃洛伊人作为肉食</text>

          <!-- 终极退化箭头 -->
          <path d="M 470 157 L 525 157" class="tm-solid" marker-end="url(#tm-arr)" />
          <text x="500" y="148" class="tm-lbl">3000万年</text>

          <!-- 终极死寂 -->
          <rect x="535" y="125" width="130" height="65" class="tm-box tm-bg-apoc" />
          <text x="600" y="152" class="tm-t-w">宇宙热寂末日</text>
          <text x="600" y="170" class="tm-t-sub-w">血色残阳 / 巨蟹冰封</text>
        </svg>
      </div>

      <div class="sub-heading">核心人物与物种谱系</div>
      <ul class="bullet-list">
        <li><strong>时间旅行者（The Time Traveller）：</strong>维多利亚时代经验主义与启蒙理性的集大成者。他不仅制造了机器，更保持着冷酷客观的实证精神。他由最初对“乌托邦”的赞叹，逐渐走向识破地底真相后的震惊与幻灭。</li>
        <li><strong>维娜（Weena）：</strong>埃洛伊人小女孩，落水时被旅行者救起。她像孩童般依恋旅行者，采摘奇异花朵相赠。她的脆弱象征着人情与温存最后的微弱火花，其在森林大火中的失踪宣告了温情无法挽救退化的宿命。</li>
        <li><strong>莫洛克人群体：</strong>地底机器轰鸣中的幽灵。他们眼球惨白、动作敏捷，保留了操作机械与劳作的本能，但道德知觉彻底泯灭，将地上的同胞退化降解为盘中餐食。</li>
      </ul>"""

    # Section 03
    sec03 = """      <div class="sub-heading">表面上讲了什么故事</div>
      <p>一位天才物理学者研制出能自由穿梭第四维度的时间机器。他孤身一人来到公元802701年，先是以为来到了无忧无虑的田园黄金时代，随后机器在白色狮身人面像底座中神秘失窃。在找寻机器的过程中，他潜入黑暗的地下通风井，发现了人类分裂为地下食人怪兽与地上待宰羔羊的恐怖真相，在浴血脱险后进一步驶向三千万年后的地球残局。</p>

      <div class="sub-heading">深处真正关心什么</div>
      <p>作品探讨了<strong>“安全、富足与过度安逸对物种生存意志的毁灭性腐蚀”</strong>。当一切自然风险被科技铲除，当社会阶级通过空间隔离彻底固化，人类的智性、审美、勇气与体力都将失去演化动力，最终沦为自然的弃儿。</p>

      <div class="sub-heading">核心体验一句话</div>
      <p>穿透“科技必将带来光明彼岸”的盲目乐观，直面宇宙终极熵增与人性异化的森冷深渊。</p>"""

    # Section 04
    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>知性探索者 vs 演化残酷法则</strong>；维多利亚工业文明的自负 vs 八十万年后不可逆转的生物异化终局。</p>

      <div class="sub-heading">情节推进链条</div>
      <ol class="num-list">
        <li><strong>启程与时空飞跃：</strong>实验室里的哲学论辩，随后拉下控制杆，昼夜如日光灯般闪烁交替，建筑与森林如潮水消长。</li>
        <li><strong>初抵假相乐园：</strong>置身金碧辉煌的宏伟废墟，邂逅素食娇小的埃洛伊人，误以为人类已实现永久和平。</li>
        <li><strong>机器失窃与幽暗低语：</strong>时间机器被拖入青铜巨门，黑夜降临，深井中传来令人毛骨悚然的吸吮声。</li>
        <li><strong>地下深渊探秘：</strong>划亮安全火柴潜入地底，目睹莫洛克人餐盘上的新鲜肉尸，解开双物种共生捕食的残酷谜题。</li>
        <li><strong>森林火海与逃亡：</strong>点燃樟脑与干柴在黑夜中与莫洛克人激战，维娜失踪，旅行者夺回机器绝地反击。</li>
        <li><strong>终点远眺与归来：</strong>跳跃至远未来直视地球衰竭，返回维多利亚壁炉前讲述经历，随后再次出发永不复返。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>时间旅行者在黑暗深井中点燃第一根火柴：</strong>那一瞬间跳跃的微光，照亮了莫洛克人苍白的皮肤和正在被切割的肉块。这一刻粉碎了所有“进步假想”，确立了全书不可逆转的冷酷基调。
      </div>"""

    # Section 05
    sec05 = """      <div class="sub-heading">时间旅行者的精神弧线：从启蒙探险家到末日见证者</div>
      <p>他并非传统打怪通关的冒险英雄，而是带着笔记本和观察眼光的科学家。面对死亡威胁，他的第一反应依然是推导生物演化因果链条。他的伟大不在于武力战胜莫洛克人，而在于能够承受文明崩塌的真相，并坦然将其公之于世。</p>

      <div class="sub-heading">埃洛伊人：无痛社会的心理标本</div>
      <p>他们拥有孩童般纯真秀美的面庞，却毫无好奇心与悲悯心。同伴溺水时，他们像群鸟掠过般冷漠旁观。威尔斯深刻洞察到：<strong>当痛苦、匮乏与劳动被彻底消除，人类深沉的情感与道德感知也一并蒸发了。</strong></p>

      <div class="sub-heading">莫洛克人：被驱逐阶级的野蛮复仇</div>
      <p>他们畏惧光芒，长年生活在地底黑暗与重油机械的轰鸣中。他们保留了行动力与分工协作，却演化出了食人恶习。这是马克思阶级论在达尔文主义框架下的极端演绎——历史的压迫者最终变成了被剥削阶级的食粮。</p>"""

    # Section 06
    sec06 = """      <div class="sub-heading">语言气质与呼吸方式</div>
      <p>采用优雅考究的<strong>框形叙事（Frame Narrative）</strong>。外层是维多利亚绅士沙龙的雪茄香气与理性辩论，内层是时间旅行者沙哑、疲惫却严丝合缝的第一人称追忆。语言沉着、精确，充满维多利亚科学报告的冷静质感，与远古末日的苍茫形成巨大张力。</p>

      <div class="sub-heading">三大核心象征网络</div>
      <ul class="bullet-list">
        <li><strong>白色狮身人面像 (The White Sphinx)：</strong>屹立在废墟之上的巨大青铜大理石雕像。它象征着不可知的时间谜题，昔日的智慧如今沉默地注视着人性的降解。</li>
        <li><strong>安全火柴与樟脑：</strong>时间旅行者口袋里的微小文明遗物。在莫洛克人出没的夜里，火柴是保护生命的唯一步骤，象征着“火”作为人类文明黎明与自卫的最初也是最后工具。</li>
        <li><strong>两朵枯萎的异界干花：</strong>维娜塞在旅行者口袋里的不知名花朵。即使在三千万年后的无尽冰雪与文明废墟中，它依然证实着“互助与爱慕的记忆曾真实存在”。</li>
      </ul>"""

    # Section 07
    sec07 = """      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        <strong>表层：</strong>一台跨越时空的精密机械引发的未来冒险奇谭。<br>
        <strong>深层：</strong>资本主义工业阶级分化导致人种生物学断裂的社会学警示。<br>
        <strong>根本：</strong>宇宙物理法则（熵增与热力学极限）面前人类自我中心主义的彻底粉碎。
      </div>

      <div class="sub-heading">不可调和的价值冲突</div>
      <p><strong>安逸无知的生活 vs 痛苦清醒的意志</strong>。埃洛伊人没有战争、贫困与劳役，但丧失了人之所以为人的全部尊严；莫洛克人保有力量与机器，却沦为残忍嗜血的异形。人类何去何从？</p>"""

    # Section 08
    sec08 = """      <div class="sub-heading">最有文本依据的解读</div>
      <p>对19世纪末放任自流资本主义制度与社会达尔文主义的严正预警。科技的发展绝不自动带来精神的解放，阶级鸿沟若不弥合，最终将走向互相吞噬的生物学生态系统。</p>

      <div class="sub-heading">警惕过度阐释</div>
      <p>不要简单将莫洛克人等同于“天生邪恶的反派”。在威尔斯的笔下，莫洛克人所展现出的食人习性，正是历代统治阶级将其驱逐到暗无天日的地下环境后，环境反哺催生出的生存适应结果。</p>"""

    # Section 09
    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>算法推荐与信息茧房正在将现代人圈养为精神上的“埃洛伊人”——只需轻触屏幕即可获得廉价的多巴胺，深度思考能力迅速退化；而庞大的算力中心与数据机房隐藏在城市看不见的地底，无声地操控着现实运转。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>当智能技术代劳了一切体力与智力劳动，你靠什么保持自己心智的敏锐与肌肉的活力？</li>
        <li>你是否在某些时刻为了追求当下的舒适感，自愿放弃了对复杂现实的探索与追问？</li>
        <li>如果生命的结局注定被时间遗忘，人类个体创造的爱与美还有什么不可替代的意义？</li>
      </ol>"""

    # Section 10
    sec10 = """      <div class="sub-heading">30 秒日常交流版</div>
      <p>“如果你以为科技发展等于人类繁荣，《时间机器》会给你一记重击。它借一场八十万年后的旅行证明：如果只追求毫无挑战的舒适，人类最终会退化为地上被圈养的玩偶和地下食人的怪兽。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “智慧是身处危险与变故中的力量；如果一切都完美而安定，思考便成了多余的器官。”
      </div>"""

    # Section 11
    sec11 = """      <div class="sub-heading">最小通达路径</div>
      <ul class="bullet-list">
        <li><strong>必读核心章节：</strong>第四章（初遇埃洛伊人）、第五章（发现莫洛克人）、第十一章（三千万年后的死寂地球）。</li>
        <li><strong>最值得精读的高密度段落：</strong>时间旅行者在第十一章中描写冰冷海岸、血色夕阳与最后一只巨大甲壳类生物的段落。</li>
      </ul>
      <div class="sub-heading">互文阅读推荐</div>
      <p>阿道司·赫胥黎《美丽新世界》（技术圈养下的无痛奴役） · 乔治·奥威尔《一九八四》（意识形态剥夺下的精神窒息）。</p>"""

    # Section 12
    sec12 = """      <div class="card-box">
        <strong>Q1 · 舒适与退化的悖论：</strong>如果完全消除了疾病、痛苦与贫困，人类文明是否真的必然丧失前进的雄心与创造力？
      </div>
      <div class="card-box">
        <strong>Q2 · 谁才是真正的受害者？</strong>在埃洛伊人与莫洛克人的关系中，道德天平究竟该倾向无辜羸弱的埃洛伊人，还是长年不见天日的苦力莫洛克人？
      </div>
      <div class="card-box">
        <strong>Q3 · 技术的双刃剑：</strong>时间机器赋予了旅行者洞察未来的全知视角，但这除了带给他更深沉的绝望与虚无之外，还能改变既定的历史因果吗？
      </div>
      <div class="card-box">
        <strong>Q4 · 记忆的尊严：</strong>两朵干瘪的花朵究竟证明了什么？为什么弱小的善意比宏伟的青铜机器更能抵抗时间的磨灭？
      </div>
      <div class="card-box">
        <strong>Q5 · 终极宇宙观：</strong>面对太阳熄灭、宇宙热寂的宏大宿命，人类当下的一切奋斗与苦难具有怎样的崇高性？
      </div>"""

    # Section 13
    sec13 = """      <div class="sub-heading">① 思维工具：“反向演化压力测试”</div>
      <p><strong>适用场景：</strong>评估某项新技术、新制度是否在暗中削弱团队或个人的基本生存本领。<br>
      <strong>核心问法：</strong>这项工具省去了哪种“不舒服”的磨砺？失去了这种磨砺，一年后我的哪种核心机能会萎缩？</p>

      <div class="sub-heading">② 写作练习任务</div>
      <p>模仿第十一章《时间的尽头》那种寂寥、宏大的语言质感，写一段描述“城市电力彻底中断后第五十年，人类在摩天大楼废墟顶端仰望星空”的静谧场景（300字以内，不出现惊叹号与激动修辞）。</p>"""

    # Assemble HTML
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
