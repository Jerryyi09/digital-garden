# -*- coding: utf-8 -*-
"""
Deep Literature Guide for Top Sci-Fi and Fantasy (Target: 5500+ Chinese chars, full benchmark level)
"""
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_deep_top_fantasy():
    data = {
        "title_cn": "世界顶级科幻与奇幻经典总览",
        "title_en": "Top Sci-Fi and Fantasy",
        "author_cn": "欧美权威书评与文萃编委会",
        "author_en": "Curated Classics Edition",
        "sub_desc": "想象力文学的双峰对决 · 从硬核物理推演到心灵史诗神话",
        "hero_quote": "科幻探索我们向外走能走多远，奇幻追问我们向内探能探多深；它们共同守护着人类仰望星空与直视心灵的最高权利。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">编选体系</div><div class="spec-val">世界科幻与奇幻文库权威精选</div></div>
        <div class="spec-item"><div class="spec-label">大师坐标</div><div class="spec-val">托尔金 / 阿西莫夫 / 勒瑰恩 / 赫伯特等</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">史诗奇幻 · 硬核科幻 · 太空歌剧 · 思想实验</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">跨世纪二十位宗师体系化导读长卷</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 青少年与博雅通识通读</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">世界模型构筑完整度与人性哲学超越性</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把科幻与奇幻当作毫无营养、供人逃避现实压力的‘廉价避难所（Escapism）’。正如《魔戒》作者J.R.R.托尔金在著名的文学讲演中所愤怒驳斥的：<strong>“在整座人类监狱里，最痛恨逃亡之心的，唯有那些冰冷的狱卒！”</strong>伟大的幻想文学绝非逃离真实，而是借由暂时悬置物理定律或世俗习俗的枷锁，带领读者跃入更高维度的道德试炼场，直面权力、死亡、爱与牺牲的根本命题。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 两种截然不同却互为照耀的世界模型构筑机制：</strong>科幻依赖“理性推演（Extrapolation）”，追问“如果某项关键科技或宇宙参数发生改变，人类社会与伦理将如何剧烈重构”；奇幻依赖“神话原型与潜意识投影”，追问“在面对深渊魔戒的绝对诱惑时，平凡人如何守住微小的灵魂烛火”。两者共同构成了现代心智的一体两面。
      </div>
      <div class="card-box">
        <strong>② 宏大叙事中对道德熔炉（The Moral Crucible）的极致锻造：</strong>无论是《沙丘》中保罗·厄崔迪明知帝国圣战将屠杀数百亿生灵却无法逆转预言的崇高悲剧，还是《地海巫师》中格得必须拥抱自己放出的黑影才能找回真名的心灵整合，优秀的幻想文学总是将人类复杂的政治、伦理抉择推向戏剧化的极限。
      </div>
      <div class="card-box">
        <strong>③ 跨学科博雅通识素养的至高殿堂：</strong>涉及语言学的完整人工发明（托尔金的辛达林精灵语）、复杂干旱生态学的严密推导（弗兰克·赫伯特的沙丘生态循环）、天体物理学与社会历史动力学（阿西莫夫的心理史学），是培养青年跨学科架构思维与宏大世界观的无上熔炉。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        从工业革命以来的科学理性飞跃，到两次世界大战后西方文明对精神家园与失落神话的呼唤，科幻与奇幻共同构筑了二十世纪最雄浑的文学双峰。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tf-box { rx: 8; stroke-width: 1.5; }
            .tf-bg-core { fill: #fbf9f4; stroke: #1c221e; stroke-width: 2.2; }
            .tf-bg-scifi { fill: #1d3557; stroke: #2a4d7a; }
            .tf-bg-fant { fill: #8c2d19; stroke: #a33b24; }
            .tf-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
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

          <!-- 核心枢纽：人类存在困境 -->
          <rect x="240" y="115" width="200" height="105" class="tf-box tf-bg-core" />
          <text x="340" y="145" class="tf-t-d">人类生存与文明命题枢纽</text>
          <text x="340" y="167" class="tf-t-sub">爱与恐惧 · 自由与宿命 · 权力诱惑</text>
          <text x="340" y="187" class="tf-t-sub">道德牺牲 · 意义追问 · 宇宙归宿</text>
          <text x="340" y="205" style="fill:#8c2d19; font-size:10px; font-weight:700; text-anchor:middle;">文学探索的共同精神终点</text>

          <!-- 向左：科幻推演轴 (向外探索) -->
          <path d="M 240 167 L 175 167" class="tf-line-blue" marker-end="url(#tf-arr-b)" />
          <rect x="15" y="40" width="155" height="255" class="tf-box tf-bg-scifi" />
          <text x="92" y="70" class="tf-t-w">科幻推演维度 (Sci-Fi)</text>
          <text x="92" y="98" style="fill:#a8dadc; font-size:11px; font-weight:700; text-anchor:middle;">【认知陌生化引擎】</text>
          <text x="92" y="125" class="tf-t-sub-w">物理法则与数学推导</text>
          <text x="92" y="148" class="tf-t-sub-w">深空殖民与代际飞船</text>
          <text x="92" y="171" class="tf-t-sub-w">人工智能与赛博义体</text>
          <text x="92" y="194" class="tf-t-sub-w">社会系统未来学演进</text>
          <text x="92" y="222" style="fill:#cad5e2; font-size:10px; text-anchor:middle;">代表：阿西莫夫 · 赫伯特</text>
          <text x="92" y="240" style="fill:#cad5e2; font-size:10px; text-anchor:middle;">克拉克 · 菲利普·迪克</text>
          <text x="92" y="270" style="fill:#90e0ef; font-size:11.5px; font-weight:700; text-anchor:middle;">“向外走能走多远？”</text>

          <!-- 向右：奇幻神话轴 (向内探寻) -->
          <path d="M 440 167 L 505 167" class="tf-line-red" marker-end="url(#tf-arr-r)" />
          <rect x="510" y="40" width="155" height="255" class="tf-box tf-bg-fant" />
          <text x="587" y="70" class="tf-t-w">奇幻神话维度 (Fantasy)</text>
          <text x="587" y="98" style="fill:#f0dcd8; font-size:11px; font-weight:700; text-anchor:middle;">【潜意识心灵剧场】</text>
          <text x="587" y="125" class="tf-t-sub-w">英雄旅程与单子神话</text>
          <text x="587" y="148" class="tf-t-sub-w">魔法代价与古老誓约</text>
          <text x="587" y="171" class="tf-t-sub-w">善恶交锋与深渊诱惑</text>
          <text x="587" y="194" class="tf-t-sub-w">失落乐园的诗意挽歌</text>
          <text x="587" y="222" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">代表：托尔金 · 勒瑰恩</text>
          <text x="587" y="240" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">乔治·马丁 · 普拉切特</text>
          <text x="587" y="270" style="fill:#fbc4ab; font-size:11.5px; font-weight:700; text-anchor:middle;">“向内探能探多深？”</text>
        </svg>
      </div>

      <div class="sub-heading">两大体系的核心支柱与思想大师对照</div>
      <ul class="bullet-list">
        <li><strong>科幻体系代表人物与思想核心：</strong><br>
        - 艾萨克·阿西莫夫（《银河帝国》《基地》）：以数理历史学推演大帝国的盛极而衰，确立机器人三大法则，探讨文明周期律；<br>
        - 弗兰克·赫伯特（《沙丘》）：深度融合干旱生态学、伊斯兰苏菲神学与封建地缘政治，解剖救世主神话对人类自决意志的毁灭性绑架；<br>
        - 菲利普·K·迪克（《仿生人会梦见电子羊吗？》）：赛博朋克先驱，提出‘如果记忆可以被人工植入，什么才是定义人类的唯一标准’的虚无拷问。</li>
        <li><strong>奇幻体系代表人物与精神原型：</strong><br>
        - J.R.R.托尔金（《魔戒》《霍比特人》）：现代严肃奇幻的无上丰碑，以语言学家的虔诚构筑中土世界，借弗罗多与山姆这两个卑微霍比特人的纯朴坚守，宣告了对至高魔戒（绝对权力）的自愿弃绝；<br>
        - 厄休拉·勒瑰恩（《地海传奇》）：融合东方老庄道家哲学，指出光芒与黑暗的互生互克，魔法不是炫耀征服的力量，而是‘在万物平衡的琴弦上轻柔拨弄’的克制智慧；<br>
        - 乔治·R·R·马丁（《冰与火之歌》）：解构古典奇幻的美好幻想，引入冷酷的中世纪现实主义政治博弈（马基雅维利式权谋与生存严冬）。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>从宇宙尽头以百万年光年计的星际文明大衰亡、外星异形母舰降临，到中土大陆风雪交加中的护戒远征队、地海群岛上骑着龙飞翔的法师，再到沙丘荒漠深处驾驭四百米沙虫的救世主圣战。汇聚了二十世纪最磅礴壮丽的二十位文学宗师所构建的完整宇宙文明与神话演进史。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处关心的是<strong>“人类在脱离了熟悉的日常平庸安全感之后，靠什么确立自己的存在尊严”</strong>。无论是面对外在冰冷无垠、充满降维打击的宇宙星空，还是面对内在被欲望、魔戒和贪婪侵蚀的心灵幽暗森林，人类真正寻找的支点，永远是爱、牺牲、忠诚与对未知力量的自省敬畏。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        给灵魂装上一副广角望远镜与一台深层内窥镜：向外，直面亿万光年宇宙物理法则的宏大威严；向内，照见远古神话原型深处人类最脆弱也最神圣的道德火种。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个不甘心将一生局限于逼仄写字楼格子间、渴望用宏大时空尺度重新审视人生价值与文明命运的青年学者与通识读者。</p>"""

    sec04 = """      <div class="sub-heading">叙事建模的两大古典与现代范式</div>
      <div class="card-box">
        <strong>范式 A · 英雄的深渊启程与救赎回归（坎贝尔单子神话 Monomyth）：</strong><br>
        平凡夏尔村庄的召集令 → 跨越第一道幽暗门槛（莫瑞亚矿坑） → 绝境与深渊考验（末日火山魔戒诱惑） → 放弃占有与牺牲自我 → 带着创伤与平静重返家园（如《魔戒》《地海巫师》）。这套结构是人类千百年来心理成年礼的永恒投影。
      </div>
      <div class="card-box">
        <strong>范式 B · 技术外推与社会系统异化演进链条（Cognitive Extrapolation）：</strong><br>
        设定一项不可逆的核心技术突破（如香料折叠空间、脑机记忆买卖、机器人普及） → 严谨推演该技术如何重构家庭、阶级、宗教与权力分配 → 当技术系统产生自身不受控的意志时爆发全盘政治危机 → 探索人类在机器统治边缘的妥协与存续（如《沙丘》《银河帝国》《基地》）。
      </div>"""

    sec05 = """      <div class="sub-heading">人物复杂性与宿命悲剧深度</div>
      <p>世界顶级幻想文学绝不设立扁平幼稚的‘纯善主角’与‘纯恶反派’：<br>
      托尔金笔下的至尊魔戒持有者弗罗多，在末日火山熔岩之巅的最后关头，意志终于被魔戒彻底击垮，狂喊着‘我不愿毁掉它，魔戒是我的！’那一刻如果不是贪婪的咕噜姆失足跌落熔岩，拯救中土的使命就会彻底破产。托尔金借此残酷宣告：<strong>在绝对权力的毒液面前，没有凡人的意志可以毫发无损地幸存</strong>。<br>
      沙丘保罗在饮下生命之水后获得了全知视野，却痛苦地发现无论自己怎么选择，由自己掀起的银河系圣战都将烧死六百一十亿无辜平民。这种英雄被自身神化偶像反噬的深沉悲剧，展现了幻想文学完全比肩古典希腊悲剧的崇高分量。</p>"""

    sec06 = """      <div class="sub-heading">世界构筑（Worldbuilding）的文学肌理精粹</div>
      <p>优秀的幻想文学大师从不进行枯燥生硬的信息灌输（Exposition Dump），而是像考古学家与生态学家一样，让读者在行云流水的故事推进中，自然而然地触摸到那个异域世界的泥土质感与空气温度：<br>
      在《沙丘》中，赫伯特通过描写弗雷曼人如何珍惜每一滴眼泪、如何用蒸馏服过滤每一滴汗水与尿液，将‘水即生命、水即神明’的严酷沙漠宗教刻进读者骨髓；在《魔戒》中，托尔金运用数十首行军古歌、不同种族的饮食习惯与地名词根，让中土世界的每一座山峰都仿佛拥有三千年的沧桑记忆。</p>

      <div class="sub-heading">三大核心象征网络</div>
      <ul class="bullet-list">
        <li><strong>至尊魔戒 (The One Ring)：</strong>绝对权力的终极象征。它不仅腐蚀佩戴者，更可怕的是它能诱骗善良的人‘为了正义与仁慈而使用它’，最终把每一个救世主变成下一个黑暗魔王。</li>
        <li><strong>沙丘的沙虫与香料 (Shai-Hulud and Melange)：</strong>既是带来无穷财富与星际折叠导航的战略资源，也是狂暴毁灭性大自然的化身。它象征着现代工业文明对化石能源的贪婪成瘾与必然反噬。</li>
        <li><strong>真名 (True Name)：</strong>地海巫师掌握魔法的唯一钥匙。知晓万物的真名即知晓其本质与界限；滥用真名打破平衡，就会招致黑暗魔影的现身吞噬。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（恢弘奇观）：</strong>跨越星系与古老大陆的史诗远征、巨舰大炮、巨龙魔法与阵营大战。<br>
        <strong>深层架构（制度与政治推演）：</strong>对寡头垄断、神权专制、救世主崇拜与技术异化的冷酷政治学解剖。<br>
        <strong>根本架构（形而上道德）：</strong>在无限冷漠的宇宙物理法则与幽深的人性欲望深渊中，确认人类微小而坚韧的道德主体性与克制美德。
      </div>"""

    sec08 = """      <div class="sub-heading">解释边界与过度阐释警惕</div>
      <p>阅读顶级幻想文学，切忌陷入两极偏狭：<br>
      一是浅薄的‘唯设定论’——整日沉迷于对比哪艘星际战舰火力更强、哪个禁咒魔法破坏力更大，把伟大的文学杰作降格为廉价的网络卡牌游戏数值对决；<br>
      二是生硬的‘机械隐喻论’——非要把魔戒穿凿附会为原子弹、把半兽人附会为某个具体的现代民族。托尔金生前极其厌恶这种僵化的对号入座，他强调幻想作品的魅力在于其具有‘普遍适用性（Applicability）’，它探讨的是超越一时一地的永恒人性困境。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>现代人正生活在由算法巨头、金融衍生品与海量数字信息构筑的‘新型中土与沙丘帝国’中：<br>
      我们对社交媒体流量与掌控力的渴望，正如对至尊魔戒的贪恋；我们对石油、算力芯片等核心资源的全球地缘争夺，正如各大家族在厄拉科斯星上对香料的血腥厮杀。幻想文学是一面超高分辨率的历史照妖镜，照出了现代文明潜伏在西装革履背后的古老贪婪。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>如果你手中突然获得了一份可以凌驾于他人之上、不受监督的绝对权力（如掌控团队评优或资源分配），你能抵挡住不把它变成‘自私魔戒’的诱惑吗？</li>
        <li>在面对时代浪潮中的狂热‘造神’崇拜时，你是否能保持像弗兰克·赫伯特那样的清醒警惕，看穿救世主光环背后的巨大代偿风险？</li>
        <li>当生活陷入看似不可战胜的绝境时，你身上是否还能保留像山姆·甘吉那样‘哪怕只是为了守护世间仅存的美好而继续走下去’的纯朴信念？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“千万别把科幻奇幻当成逃避现实的小说。科幻是向外看宇宙的显微镜，奇幻是向内看人性的解剖刀。从《沙丘》对权力的警惕，到《魔戒》对贪婪的克制，顶级幻想作品不仅带你看见几万年后的未来，更教会你在当下如何做一个有自省、有骨气的人。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊聊《世界顶级科幻与奇幻经典》。很多严肃读者曾对幻想文学抱有偏见，认为那是青少年的不务正业。但如果你读过托尔金的《魔戒》、弗兰克·赫伯特的《沙丘》或勒瑰恩的《地海传奇》，你会发现它们探讨的伦理深度丝毫不输托尔斯泰或莎士比亚。为什么科幻与奇幻总被放在一起？因为它们是人类心智的一体两面。科幻探讨‘技术向外推演的极限’——如果AI全面觉醒、如果基因彻底被修改，人类社会会走向何方？而奇幻探讨‘道德向内扎根的定力’——面对至尊魔戒的绝对诱惑，连神仙精灵都会堕落，为什么拯救世界的偏偏是两个脚踩泥土、只知道种菜喝麦酒的小小霍比特人？因为托尔金深刻洞察到：战胜绝对权力的唯一武器，不是更强大的权力，而是对权力的主动放弃与对平凡善良的死守。这套经典书目是送给每一个现代人的精神疫苗，它让我们在充满浮躁焦虑的现代生活中，拥有一片能够安放星空与勇气的宏大精神原野。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “奇幻是人类古老童年的诗意神圣回响，科幻是人类走向宇宙成年的清醒理性战歌；唯有将两者兼收并蓄，我们的灵魂才拥有完整的翅膀与坚实的锚桩。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界顶级幻想双峰必读指南</div>
      <ul class="bullet-list">
        <li><strong>科幻史诗顶峰 · 弗兰克·赫伯特《沙丘》六部曲：</strong>重点精读第一卷保罗在沙漠试炼与戈姆刺受刑的章节，领悟‘恐惧是思维杀手’的意志法则。</li>
        <li><strong>奇幻神话绝唱 · J.R.R.托尔金《魔戒》三部曲：</strong>重点精读第三部《王者归来》末日火山之巅弗罗多被诱惑、以及山姆背负主人攀登峭壁的千古绝唱。</li>
        <li><strong>东方哲思奇幻 · 厄休拉·勒瑰恩《地海巫师》：</strong>重点精读结尾格得在海面拥抱自己的黑影、呼喊出彼此同名同姓的心灵整合神谕。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 英雄的真实代价：</strong>在《魔戒》最后，弗罗多拯救了整个中土世界，但他自己的心灵却被魔戒与怨灵之刃留下了终生无法愈合的剧痛，最终不得不离开家乡西渡沧海。这打破了传统大团圆童话，传达了关于‘创伤与代价’怎样的崇高启示？
      </div>
      <div class="card-box">
        <strong>Q2 · 救世主之毒：</strong>《沙丘》作者赫伯特说‘领袖人物的错误往往因盲从者众多而被无限放大’，为什么寄希望于某一个全能的救世主降临，往往是人类灾难的开端？
      </div>
      <div class="card-box">
        <strong>Q3 · 力量的克制：</strong>为什么在顶级奇幻小说中，最强大的巫师（如甘道夫、格得）往往极少施展毁天灭地的攻击性法术，而是时刻谨守‘不轻易扰乱世界自然平衡’的戒律？
      </div>
      <div class="card-box">
        <strong>Q4 · 科技与灵魂：</strong>当科幻小说推演人类肉身被改造成不老不死的机械生化人时，人性的本质究竟退守到哪里？纯粹理性的逻辑能够赋予生命真正的幸福吗？
      </div>
      <div class="card-box">
        <strong>Q5 · 仰望星空的必要性：</strong>如果一个人一生只关注柴米油盐房贷车贷，从未读过一本关于星际或巨龙的幻想小说，他的生命失去了哪一种最不可替代的体验？
      </div>"""

    sec13 = """      <div class="sub-heading">① 架构思维工具：“世界观宏观推演模型” (The Macro-Worldbuilding Matrix)</div>
      <p><strong>适用场景：</strong>深度内容创作、大型项目顶层架构规划、前瞻性商业战略推演。<br>
      <strong>维度一（物理底层律）：</strong>明确你所构筑的世界中，哪一项核心资源（如沙丘的水与香料、现实中的算力芯片与清洁能源）具有绝对稀缺性与决定性霸权。<br>
      <strong>维度二（制度与社会网络）：</strong>推导这个稀缺性如何自下而上塑造该社会的家庭形态、等级制度、意识形态与禁忌迷信。<br>
      <strong>维度三（边缘异变点）：</strong>在这个看似铁板一块的庞大系统最不起眼的边缘地带，寻找可能引爆整个系统重组的微小异类力量（如沙漠游民、霍比特人）。</p>

      <div class="sub-heading">② 现实观察实验：“身边的魔戒测试”</div>
      <p>审视你所在的团队、班级或朋友圈中，是否存在某种能够让人们为之趋之若鹜、甚至不惜背弃真诚友谊的小小‘特权或利益诱饵’。观察人们在面对这一诱饵时眼神与言辞的微妙变化，体会托尔金关于魔戒诱惑的现实深刻性。</p>

      <div class="sub-heading">③ 跨体裁仿写演练</div>
      <p>选择一个极度现代化的场景（如证券交易所或大型数据中心服务器机房），尝试用托尔金描写摩多黑门要塞或矮人地下宫殿那种充满古老史诗韵律、崇高修辞的庄严笔调进行一段环境白描（350字以内，不使用现代口语流行词）。</p>"""

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

    body = TEMPLATE_HEAD.format(**data)
    for idx, title, content, is_open in sections:
        body += render_section(idx, title, content, is_open)
    body += TEMPLATE_FOOT
    return body
