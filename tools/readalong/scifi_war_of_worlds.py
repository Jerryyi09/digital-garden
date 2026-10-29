# -*- coding: utf-8 -*-
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_war_of_worlds_guide():
    data = {
        "title_cn": "世界大战",
        "title_en": "The War of the Worlds",
        "author_cn": "赫伯特·乔治·威尔斯",
        "author_en": "H. G. Wells",
        "sub_desc": "外星接触与灾难科幻开山鼻祖 · 帝国殖民主义的末世镜像",
        "hero_quote": "在浩瀚冰冷的太空中，智慧生命以嫉妒的眼光注视着地球，缓缓而确定地编织着针对我们的罗网。"
    }

    # Section 01
    sec01 = """      <div class="specs-grid">
        <div class="spec-item">
          <div class="spec-label">作者与生卒</div>
          <div class="spec-val">H·G·威尔斯 (1866–1946)</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">出版年份</div>
          <div class="spec-val">1898 年连载出版 / 灾难科幻始祖</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">体裁坐标</div>
          <div class="spec-val">末世浩劫小说 / 外星入侵 / 社会寓言</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">全书体量</div>
          <div class="spec-val">约 6 万字（全二卷）</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">建议阅读年龄</div>
          <div class="spec-val">12+ 岁 / 青年与思辨读者</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">核心判断标准</div>
          <div class="spec-val">文明脆弱性刻画与生态系统反转机制</div>
        </div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《世界大战》当作好莱坞式的超级英雄抵御外星怪兽枪战爽剧。威尔斯的真正意图是让当时沉浸在“日不落帝国”虚荣中的大英帝国居民，<strong>亲身体验一次塔斯马尼亚土著面对欧洲火枪与炮舰时的灭顶绝望</strong>。这是一面照向帝国主义殖民扩张的残酷镜子。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 现代文明外壳的惊人脆弱性：</strong>热射线一扫、黑烟一散，伦敦数百万市民瞬间陷入混乱暴乱。货币失去意义，阶级体面扫地以尽，展示了复杂现代社会在技术碾压下的急速原子化。
      </div>
      <div class="card-box">
        <strong>② 经典人设对照下的信仰与心智瓦解：</strong>叙述者身边的副牧师代表宗教信念的歇斯底里式崩溃，而炮兵则代表自负而荒谬的地下军国主义幻想，二人成为极端危机中人性的真实试金石。
      </div>
      <div class="card-box">
        <strong>③ 生态演化视角的终极神来之笔：</strong>击溃神一般火星巨型三脚机甲的，不是人类英勇的鱼雷艇或大炮，而是地球亿万年演化中“最卑微、最微不足道”的细菌微生物。
      </div>"""

    # Section 02 (with SVG)
    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪末，维多利亚帝国掌控全球海洋与殖民地，科技乐观主义达到顶峰。威尔斯以伦敦西郊沃金为第一现场，虚构了一场压倒性的技术代差浩劫，精准戳破了殖民帝国的傲慢。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg">
          <style>
            .ww-box { rx: 8; stroke-width: 1.5; }
            .ww-bg-mars { fill: #8c2d19; stroke: #a33b24; }
            .ww-bg-human { fill: #fbf9f4; stroke: #1d3557; stroke-width: 2; }
            .ww-bg-collapse { fill: #242930; stroke: #59645f; }
            .ww-bg-micro { fill: #2d6a4f; stroke: #40916c; }
            .ww-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 600; text-anchor: middle; }
            .ww-t-d { fill: #1c221e; font-family: sans-serif; font-size: 12.5px; font-weight: 600; text-anchor: middle; }
            .ww-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ww-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ww-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .ww-lbl { font-family: sans-serif; font-size: 10.5px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="ww-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 火星入侵力量 -->
          <rect x="20" y="30" width="200" height="110" class="ww-box ww-bg-mars" />
          <text x="120" y="60" class="ww-t-w">火星三脚战斗机甲</text>
          <text x="120" y="80" class="ww-t-sub-w">热射线 (Heat-Ray) 毁灭炮舰</text>
          <text x="120" y="100" class="ww-t-sub-w">黑烟毒气 (Black Smoke) 窒息全城</text>
          <text x="120" y="120" class="ww-t-sub-w">红草泛滥 · 绝对技术代差</text>

          <!-- 进攻箭头 -->
          <path d="M 220 85 L 280 85" class="ww-solid" marker-end="url(#ww-arr)" />
          <text x="250" y="75" class="ww-lbl">全境摧毁</text>

          <!-- 维多利亚文明崩溃群像 -->
          <rect x="290" y="30" width="220" height="110" class="ww-box ww-bg-human" />
          <text x="400" y="60" class="ww-t-d">维多利亚社会系统溃败</text>
          <text x="400" y="80" class="ww-t-sub">叙述者：理性记录生存流亡</text>
          <text x="400" y="100" class="ww-t-sub">副牧师：神学信仰精神狂乱</text>
          <text x="400" y="120" class="ww-t-sub">炮兵：不切实际的地下帝国妄想</text>

          <!-- 溃散连线 -->
          <path d="M 400 140 L 400 180" class="ww-solid" stroke="#59645f" />
          <text x="445" y="165" class="ww-lbl" style="fill:#59645f;">文明失序</text>

          <!-- 难民大逃亡 -->
          <rect x="290" y="185" width="220" height="105" class="ww-box ww-bg-collapse" />
          <text x="400" y="215" class="ww-t-w">伦敦大逃亡 (Mass Panic)</text>
          <text x="400" y="235" class="ww-t-sub-w">六百万市民争夺轮船车马</text>
          <text x="400" y="255" class="ww-t-sub-w">秩序崩塌 / 金钱化为废纸</text>
          <text x="400" y="275" class="ww-t-sub-w">文明退回原始动物丛林</text>

          <!-- 致命转折：细菌拯救 -->
          <path d="M 120 140 L 120 200" class="ww-solid" stroke="#2d6a4f" />
          <rect x="20" y="200" width="200" height="90" class="ww-box ww-bg-micro" />
          <text x="120" y="230" class="ww-t-w">地球微生物系统</text>
          <text x="120" y="250" class="ww-t-sub-w">腐生菌 / 无免疫耐受</text>
          <text x="120" y="270" class="ww-t-sub-w">大自然微渺造物的终极救赎</text>
        </svg>
      </div>

      <div class="sub-heading">核心人物与观察者</div>
      <ul class="bullet-list">
        <li><strong>叙述者（哲学学者）：</strong>冷静坚韧的平民知识分子。面对末日浩劫，他保持着近乎记者的清醒观察，记录下人类文明在不可抗力面前的每一次自私撕扯与温情闪光。</li>
        <li><strong>叙述者的弟弟：</strong>在伦敦亲历城市恐慌大逃离。他果断勇敢地协助埃尔芬斯通太太及其儿媳逃难，直面文明大崩溃时的街头劫掠与人踩人惨剧。</li>
        <li><strong>副牧师（The Curate）：</strong>代表宗教秩序的精神崩溃者。他将外星人视作上帝灭世的天谴，最终陷入歇斯底里的贪婪与疯狂，甚至险些招致火星人对藏匿处的发现。</li>
        <li><strong>狂想的炮兵：</strong>代表极端达尔文主义的虚妄分子。他滔滔不绝地描绘在下水道繁殖精锐人类、等待反扑的宏伟蓝图，现实中却沉湎于饮酒抽烟与纸上谈兵。</li>
      </ul>"""

    # Section 03
    sec03 = """      <div class="sub-heading">表面上讲了什么故事</div>
      <p>数枚来自火星的巨大金属圆筒相继坠落于伦敦近郊。好奇的人群围拢过去，却遭遇破壳而出的火星章鱼生物及其组装的巨型百尺三脚机甲。机甲发射无坚不摧的热射线与致命黑烟毒气，正规军溃败，伦敦沦为死城。叙述者在沦陷区艰难苟活，最终发现令不可一世的外星侵略者全军覆没的，竟是地球本土最原始的腐败细菌。</p>

      <div class="sub-heading">深处真正关心什么</div>
      <p>作品探讨了<strong>“当一种文明自视为万物灵长时，宇宙给出的无情回击”</strong>。威尔斯将人类比作“被放进显微镜下的水蚤”，狠狠击碎了19世纪人类狂妄的中心主义与道德特权假想。</p>

      <div class="sub-heading">核心体验一句话</div>
      <p>身临其境地体验现代文明体面在一场超维度力量打击下的瞬间粉碎与绝境还生。</p>"""

    # Section 04
    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>超前工业杀戮机器 vs 原始脆弱血肉之躯</strong>；帝国自大幻想 vs 地球生物圈整体法则。</p>

      <div class="sub-heading">情节推进链条</div>
      <ol class="num-list">
        <li><strong>异象与陨落：</strong>天文台观测到火星连续喷发火光，奥特肖公地出现神秘深坑。</li>
        <li><strong>死光首秀与恐慌蔓延：</strong>议和白旗遭遇热射线化为飞灰，现代炮兵阵地在黑烟中瞬间窒息。</li>
        <li><strong>伦敦大溃逃：</strong>火车停运、道路堵塞，六百万市民争抢渡海小船，文明秩序瓦解。</li>
        <li><strong>雷神之子号的悲壮绝唱：</strong>“雷神之子号”装甲舰冲向机甲舍身救护难民船，成为工业人类最后的尊严孤影。</li>
        <li><strong>绝境密室相持：</strong>叙述者与崩溃的副牧师被困在废墟地窖中，近距离观察火星人生吞人血的生理机制。</li>
        <li><strong>死城寂静与细菌终局：</strong>叙述者走出地窖漫步伦敦街头，发现三脚机甲停滞不动，火星人在红草丛中腐烂暴毙。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>“雷神之子号”（HMS Thunder Child）的沉没：</strong>这艘维多利亚蒸汽铁甲舰击毁一架火星机甲后壮烈沉入海底，宣告了人类工业革命最骄傲的重工业武装彻底失去抗衡能力。
      </div>"""

    # Section 05
    sec05 = """      <div class="sub-heading">叙述者的心智韧性</div>
      <p>他没有特异功能，也未力挽狂澜。但他拥有两样强大的武器：<strong>诚实面对恐惧的能力，以及未曾泯灭的同理心</strong>。在副牧师疯狂叫喊招来杀身之祸时，叙述者果断将其击昏掩护自己，展现了生存严酷法则下的自保决断。</p>

      <div class="sub-heading">副牧师的神学崩塌</div>
      <p>在优渥教区安享信徒敬仰的牧师，无法接受上帝没有偏袒人类的现实。他把入侵解释为人类原罪的惩罚，最终心理防线崩溃走向自毁，揭示了空洞教条在真实物理灾难面前的苍白无力。</p>

      <div class="sub-heading">炮兵的荒诞讽刺</div>
      <p>炮兵象征着法西斯狂人原型的雏形：宣称要把弱小者淘汰、只留优等基因藏进地下排水沟。然而当叙述者观察他的生活时，发现他连挖掘地道都嫌累，整日沉湎于喝香槟和打牌，极具黑色幽默讽刺。</p>"""

    # Section 06
    sec06 = """      <div class="sub-heading">语言气质与纪实美学</div>
      <p>开创了<strong>伪纪实文学（Mock-Documentary）</strong>的语言先河。威尔斯精确地引用真实的地名（沃金、查令十字街、滑铁卢车站、泰晤士河口），使用详实的科学测量术语，使一场荒诞的太空入侵读来宛如历史档案般铁证如山。</p>

      <div class="sub-heading">三大核心象征网络</div>
      <ul class="bullet-list">
        <li><strong>热射线 (The Heat-Ray)：</strong>看不见的光束引发的剧烈自燃。它象征着<strong>超越现有科学认知的绝对技术代差</strong>，如同欧洲征服者带入新大陆的火药与枪炮。</li>
        <li><strong>外星红草 (The Red Weed)：</strong>在水域与街道疯狂蔓延的血红色异星植物。它象征着“生态殖民”的残暴覆盖，试图在物理环境上将地球改造为火星附庸。</li>
        <li><strong>腐生细菌 (Bacteria)：</strong>亿万年生命演化的古老造物。它们是不可抗力面前最平凡的盾牌，象征着大自然赋予地球本土生物最深邃的生态庇护。</li>
      </ul>"""

    # Section 07
    sec07 = """      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        <strong>表层：</strong>一场惊心动魄、毁灭性的外星机甲全面入侵与幸存纪实。<br>
        <strong>深层：</strong>对帝国主义殖民征服史的道德逆向拷问与现代文明脆弱性反思。<br>
        <strong>根本：</strong>人类在达尔文宏观生命演化与宇宙竞争谱系中的真实坐标界定。
      </div>"""

    # Section 08
    sec08 = """      <div class="sub-heading">最有文本依据的解读</div>
      <p>威尔斯在第一章明确指出：“在严厉审判火星人之前，我们必须记住，我们自己这个物种不仅对欧洲野牛、渡渡鸟等动物犯下了多么彻底的屠杀，而且对自己的劣势种族犯下了何等灭绝之罪。”全书是帝国良知的一声警钟。</p>

      <div class="sub-heading">警惕过度阐释</div>
      <p>不要脱离生态学演化语境，把细菌结局拔高为“上帝对人类的偏爱保护”。威尔斯清醒地写明：细菌之所以杀伤火星人，是因为火星由于远古时期水体干涸早已没有细菌，它们缺乏免疫抗体，纯粹是演化盲区导致的物理暴毙。</p>"""

    # Section 09
    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>全球化高度互联的现代社会，其维生网络（电力、自来水、物流、网络）具有高度复杂的脆弱性。一旦底层逻辑遭受突发性冲击，城市文明将在几天内退回物物交换乃至暴乱状态。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>如果你所依赖的现代都市便利突然消失，你的个人技能中还有哪些能够保障基本生存？</li>
        <li>在极端集体恐慌发生时，你会跟随人群随波逐流，还是能保持独立判断力？</li>
        <li>我们日常所自豪的“先进与优越”，是否在更高维度的挑战面前同样弱小如蝼蚁？</li>
      </ol>"""

    # Section 10
    sec10 = """      <div class="sub-heading">30 秒日常交流版</div>
      <p>“《世界大战》是所有外星入侵电影的祖师爷。但它的伟大不仅在于三脚战车，而在于它写透了当自傲的文明遭遇降维打击时，人类体面如何在三天内荡然无存，以及微小的微生物如何守卫地球。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “人类为了在地球上繁衍生息，付出了亿万次死亡的税赋；地球上每一个生命的微小权利，皆由祖先的白骨所赎买。”
      </div>"""

    # Section 11
    sec11 = """      <div class="sub-heading">最小通达路径</div>
      <ul class="bullet-list">
        <li><strong>必读核心章节：</strong>第一卷第十章（热射线屠杀）、第十七章（雷神之子号决战）、第二卷第八章（死寂的伦敦街头）。</li>
      </ul>
      <div class="sub-heading">互文阅读推荐</div>
      <p>刘慈欣《三体》（黑暗森林与技术降维打击） · 丹尼尔·笛福《大疫年日记》（城市恐慌与灾难纪实）。</p>"""

    # Section 12
    sec12 = """      <div class="card-box">
        <strong>Q1 · 报应与镜像：</strong>如果火星人入侵是一面镜子，我们今天对待自然生态与濒危物种的逻辑，和火星人对待人类有本质不同吗？
      </div>
      <div class="card-box">
        <strong>Q2 · 恐慌的社会学：</strong>为什么数百万人口的超级大都会在面对少数敌人时，破坏最大的往往不是敌人的武器，而是逃难人群内部的踩踏与抢掠？
      </div>
      <div class="card-box">
        <strong>Q3 · 尊严的界线：</strong>在极端绝境中，副牧师的疯狂、炮兵的苟活与叙述者的求真，究竟哪一种反应更贴近未经美化的真实人性？
      </div>"""

    # Section 13
    sec13 = """      <div class="sub-heading">① 危机观察思维模型：“复杂系统单点失效分析”</div>
      <p><strong>应用场景：</strong>分析现代企业运营或个人职业生涯的脆弱点。<br>
      <strong>核心法则：</strong>越是高度优化、依赖外部精细协作的系统，越容易在底层单一供给中断时产生链式坍塌。必须常备“细菌级别”的基础抗风险底牌。</p>

      <div class="sub-heading">② 纪实写作演练</div>
      <p>选取你熟悉的一座现代建筑（如高铁站或大型商场），写一段“断电48小时后失去通信的人群微观生态”速写（300字以内，着重描写水、食物与信息在人群中的流动变化）。</p>"""

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
