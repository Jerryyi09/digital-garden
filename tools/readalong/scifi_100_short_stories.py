# -*- coding: utf-8 -*-
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_100_short_stories_guide():
    data = {
        "title_cn": "百部经典微型科幻精选",
        "title_en": "100 Great Science Fiction Short Short Stories",
        "author_cn": "艾萨克·阿西莫夫 等编选",
        "author_en": "Isaac Asimov et al.",
        "sub_desc": "黄金时代大师的思维闪电 · 千字之内的宇宙惊奇哲学",
        "hero_quote": "每一篇极短篇科幻，都是投向人类既定常识的一枚高能思想炸弹。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item">
          <div class="spec-label">主编与阵容</div>
          <div class="spec-val">艾萨克·阿西莫夫 / 弗雷德里克·波尔 等</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">收录跨度</div>
          <div class="spec-val">科幻黄金时代至新浪潮经典篇目</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">体裁坐标</div>
          <div class="spec-val">极短篇科幻 / 概念思想实验 / 欧亨利式反转</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">全书体量</div>
          <div class="spec-val">100 篇独立微构（单篇 500~1500 字）</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">建议阅读年龄</div>
          <div class="spec-val">12+ 岁 / 适合碎片与深度研讨阅读</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">核心判断标准</div>
          <div class="spec-val">设定颠覆度与终局认知转折冲击力</div>
        </div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把微型科幻当作“没写完的小说大纲”或“抖机灵段子”。极短篇是科幻文学中对<strong>形式逻辑、叙事经济学与认知惊奇（Sense of Wonder）</strong>要求最高的形式——它必须在三页纸内建立世界、颠覆常识并完成哲学收网。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 极致压缩的思想实验原型：</strong>从时空悖论（祖父悖论）、硅基智能觉醒，到外星物种的奇特伦理，每一篇都是一个完整自洽的未来世界切片。
      </div>
      <div class="card-box">
        <strong>② 叙事假定前提的瞬间逆转：</strong>微型科幻最精妙的技术在于“潜伏的偏见”。读者自以为在读人类探险，最后一行才揭晓那是机器人在考古，瞬间颠覆读者既有认知。
      </div>
      <div class="card-box">
        <strong>③ 哲学思辨与现代科技反思微型课堂：</strong>篇幅极短，却每每直击道德边界、文明命运与意识本质，是启发青年批判性思维的绝佳思维磨刀石。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        20世纪中叶是科幻文学的黄金爆发期。阿西莫夫等大师从海量杂志中精挑细选出100部短小精悍之作，展现了科幻小说在思维密度与叙事留白上的极限之美。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <style>
            .sf-box { rx: 8; stroke-width: 1.5; }
            .sf-bg-core { fill: #1d3557; stroke: #2a4d7a; }
            .sf-bg-theme { fill: #fbf9f4; stroke: #8c2d19; stroke-width: 1.8; }
            .sf-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 600; text-anchor: middle; }
            .sf-t-d { fill: #8c2d19; font-family: sans-serif; font-size: 12.5px; font-weight: 700; text-anchor: middle; }
            .sf-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sf-line { stroke: #8c2d19; stroke-width: 1.6; fill: none; }
          </style>

          <defs>
            <marker id="sf-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 核心：微型科幻思想发动机 -->
          <rect x="250" y="20" width="180" height="70" class="sf-box sf-bg-core" />
          <text x="340" y="48" class="sf-t-w">微型科幻思想发动机</text>
          <text x="340" y="68" style="fill:#e0e4e8; font-size:11px; text-anchor:middle;">设定假设 · 逻辑推演 · 认知惊奇</text>

          <!-- 辐射到四大母题 -->
          <path d="M 250 55 L 140 130" class="sf-line" marker-end="url(#sf-arr)" />
          <path d="M 310 90 L 250 160" class="sf-line" marker-end="url(#sf-arr)" />
          <path d="M 370 90 L 430 160" class="sf-line" marker-end="url(#sf-arr)" />
          <path d="M 430 55 L 540 130" class="sf-line" marker-end="url(#sf-arr)" />

          <!-- 四大母题卡片 -->
          <rect x="20" y="140" width="145" height="110" class="sf-box sf-bg-theme" />
          <text x="92" y="170" class="sf-t-d">① 人工智能与机器</text>
          <text x="92" y="195" class="sf-t-sub">意识边界 · 终极计算</text>
          <text x="92" y="215" class="sf-t-sub">人机反转 · 机器伦理</text>
          <text x="92" y="235" class="sf-t-sub">如《最后的问题》</text>

          <rect x="180" y="170" width="145" height="110" class="sf-box sf-bg-theme" />
          <text x="252" y="200" class="sf-t-d">② 时间旅行与因果</text>
          <text x="252" y="225" class="sf-t-sub">祖父悖论 · 历史闭环</text>
          <text x="252" y="245" class="sf-t-sub">蝴蝶效应 · 悔恨挽歌</text>
          <text x="252" y="265" class="sf-t-sub">如时空杀手的荒诞锁</text>

          <rect x="355" y="170" width="145" height="110" class="sf-box sf-bg-theme" />
          <text x="427" y="200" class="sf-t-d">③ 地外文明与接触</text>
          <text x="427" y="225" class="sf-t-sub">相对论沟通 · 傲慢打破</text>
          <text x="427" y="245" class="sf-t-sub">动物园假说 · 沉默宇宙</text>
          <text x="427" y="265" class="sf-t-sub">如他们是由肉做成的</text>

          <rect x="515" y="140" width="145" height="110" class="sf-box sf-bg-theme" />
          <text x="587" y="170" class="sf-t-d">④ 末日余晖与社会</text>
          <text x="587" y="195" class="sf-t-sub">核冬废墟 · 极简冷眼</text>
          <text x="587" y="215" class="sf-t-sub">极权缩影 · 荒谬法条</text>
          <text x="587" y="235" class="sf-t-sub">人类终局幽默备忘录</text>
        </svg>
      </div>

      <div class="sub-heading">选集四重思想母题</div>
      <ul class="bullet-list">
        <li><strong>意识与智能的起源：</strong>机器人在什么时刻产生灵魂？当超级计算机回答“要有光”时，技术与神性如何交汇。</li>
        <li><strong>宇宙相对论与人类傲慢：</strong>外星观察者将人类视为“只会蠕动说话的肉块”，颠覆以自我为宇宙中心的盲目膨胀。</li>
        <li><strong>时空因果链条的荒诞：</strong>为了纠正一个微小的历史差错，人类在未来制造了整片毁灭性雪崩。</li>
        <li><strong>文明演化的终极荒唐：</strong>在严谨科学外壳下，暴露出人类官僚、争斗与虚荣的滑稽本质。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事</div>
      <p>100个极短故事，涵盖星际探险、仿生机器人、末日庇护所、超光速实验、记忆买卖等千姿百态的舞台。每一个故事往往在前两段设定正常场景，在最后一段乃至最后一句以令人瞠目结舌的反转彻底掀翻读者的预设。</p>

      <div class="sub-heading">深处真正关心什么</div>
      <p>作品关心<strong>“人类思维模型的局限性”</strong>。我们所有的常识，都建立在特定的地球物理环境、有限的生物感知与短暂的寿命经验之上。微型科幻通过设定极端参数，迫使我们看清常识的边界。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>常规认知定式 vs 陌生化宇宙真相</strong>；人类狭隘自我意识 vs 浩瀚时空物理冷漠。</p>

      <div class="sub-heading">微型科幻经典结构链条</div>
      <ol class="num-list">
        <li><strong>钩子与假定（The Hook）：</strong>第一句话抛出一个不同寻常的技术或现实前提，瞬间抓住眼球。</li>
        <li><strong>压缩推进（The Compression）：</strong>省去所有繁琐的修饰与环境交代，让两个人物在强烈的戏剧冲突下直击核心矛盾。</li>
        <li><strong>认知引诱（The Misdirection）：</strong>引导读者顺着日常思维惯性做出预判。</li>
        <li><strong>尾声爆破（The Stinger / The Twist）：</strong>最后一句话撕破假象，留下回味无穷的深沉哲思。</li>
      </ol>"""

    sec05 = """      <div class="sub-heading">人物谱系的类型学特征</div>
      <p>微型科幻中的人物很少有长篇小说式的冗长心理纠葛，他们往往是<strong>“某一种观念的极致化身”</strong>：执着的物理学家、傲慢的星际外交官、困惑的图灵测试检验员、天真却致命的儿童。正因其精炼，人物的选择往往更具戏剧张力与寓言深度。</p>"""

    sec06 = """      <div class="sub-heading">语言气质与精炼美学</div>
      <p>语言极度崇尚“减法”。每一个动词都经过精密称重，绝无废话。它是文学界的“微积分”，以最微小的文字面积，容纳最辽阔的宇宙想象空间。</p>"""

    sec07 = """      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        <strong>表层：</strong>百花齐放、脑洞大开的超短篇未来奇思妙想博览。<br>
        <strong>深层：</strong>对人类理性边界、技术盲目崇拜与伦理死角的逻辑推演。<br>
        <strong>根本：</strong>在浩瀚宇宙中对智慧生命存在意义的终极谦逊审视。
      </div>"""

    sec08 = """      <div class="sub-heading">警惕过度阐释与轻慢阅读</div>
      <p>不要走马观花地把100篇当作“睡前消遣段子”一次性刷完。最好的读法是每次精读1~2篇，合上书本，把最后那个反转在脑海里细细咀嚼，推敲作者在前面哪些看似不起眼的句子里埋下了伏笔。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>许多几十年前千字微型科幻预言的荒诞场景（如算法接管情绪、虚拟现实成瘾、智能管家喧宾夺主），今天已成为我们触手可及的现实日常。它展现了科幻对未来社会走向惊人的前瞻洞察力。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版</div>
      <p>“这是科幻大师写给忙碌现代人的思维浓缩胶囊。100个千字小故事，每一篇都在最后一句让你头皮发麻。它证明了伟大的思想不需要洋洋洒洒几十万字，一颗子弹大小的篇幅就能击中灵魂。”</p>"""

    sec11 = """      <div class="sub-heading">最小通达路径</div>
      <ul class="bullet-list">
        <li>建议优先挑选阿西莫夫、阿瑟·克拉克、罗伯特·谢克里（Robert Sheckley）收录的篇目精读。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 创意的黄金分割：</strong>为什么一个极度精妙的科幻创意，写成千字短篇往往比扩写成几十万字长篇更加震撼动人？
      </div>
      <div class="card-box">
        <strong>Q2 · 颠覆常识的价值：</strong>阅读科幻最大的快乐，究竟是确认我们已有的道德信念，还是体验信念被无情击穿时的眩晕与重建？
      </div>"""

    sec13 = """      <div class="sub-heading">① 创意写作工具：“反转微型科幻三步法”</div>
      <p><strong>步骤一：</strong>挑选一条你认为天经地义的社会准则（如“人必须睡觉”“诚实是美德”）；<br>
      <strong>步骤二：</strong>设定一个技术条件打破它（如“发明了免睡眠药片”“脑机接口强制广播思想”）；<br>
      <strong>步骤三：</strong>设计一个看似受害、实则是幕后得利者的戏剧性最后一句话（500字以内完成）。</p>"""

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
