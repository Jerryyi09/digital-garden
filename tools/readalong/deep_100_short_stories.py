# -*- coding: utf-8 -*-
"""
Deep Literature Guide for 100 Great Science Fiction Short Short Stories (Target: 5500+ Chinese chars, full benchmark level)
"""
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_deep_100_short_stories():
    data = {
        "title_cn": "百部经典微型科幻精选",
        "title_en": "100 Great Science Fiction Short Short Stories",
        "author_cn": "艾萨克·阿西莫夫 等编选",
        "author_en": "Isaac Asimov, Martin H. Greenberg et al.",
        "sub_desc": "黄金时代大师的思维闪电熔炉 · 千字之内的宇宙惊奇与认知颠覆",
        "hero_quote": "每一篇极短篇科幻，都是投向人类既定常识的一枚高能思想炸弹；在三页纸的方寸之间，宇宙的命运被颠覆了千百次。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">主编阵容</div><div class="spec-val">阿西莫夫 / 格林伯格 / 奥利弗</div></div>
        <div class="spec-item"><div class="spec-label">收录时代</div><div class="spec-val">科幻黄金时代至新浪潮盛期精粹</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">极短篇科幻 (Flash Fiction) / 思想实验</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">100 篇独立构筑 (单篇500-1500字)</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身思维研磨读物</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">叙事经济学极限与终局反转认知震荡度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把微型科幻当成“没写完的长篇小说大纲”或“耍小聪明的一分钟段子”。极短篇是科幻文学中对<strong>形式逻辑自洽、词语经济学与认知惊奇（Sense of Wonder）</strong>要求最高的形式。作者必须在五百至一千字的极小文本空间内，完成“建立未来设定、埋藏认知偏见、触发戏剧冲突、最后一行无情引爆反转”的四重跳跃。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 极致压缩的哲学思想实验模型：</strong>收录作品几乎涵盖了现代科幻的所有核心母题——人工智能图灵测试的倒错、时间旅行祖父悖论的自锁循环、费米悖论中外星文明冷酷的“沉默假说”、以及人类基因编辑后的伦理死结。每一篇都是一颗高浓缩的思想胶囊。
      </div>
      <div class="card-box">
        <strong>② 叙事假定前提（Premise）的瞬间连环引爆：</strong>微型科幻最精妙的刀法在于“潜伏偏见的误导（The Misdirection）”。读者自以为在读一场人类宇航员的星际拓荒，直到最后一句才冷不丁揭晓：那些被枪杀的所谓“嗜血怪物”，正是降落异星的地球殖民者自己。既有的人类中心主义在刹那间被撕得粉碎。
      </div>
      <div class="card-box">
        <strong>③ 碎片化时代的深度专注力与思辨磨刀石：</strong>在现代人注意力被算法短视频严重肢解的今天，阅读这100篇千字短篇不是消遣，而是一场高质量的心智体操。它逼迫读者在短短三分钟内动用全部逻辑推演力，跟随大师完成一次次对现实常识的凌空飞跃。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        二十世纪中叶是世界科幻文学的黄金年代。冷战军备竞赛、阿波罗登月计划与早期计算机的诞生，将全人类的想象力推向前所未有的高潮。阿西莫夫等巨匠从数千篇短篇中披沙拣金，整理出这套代表人类短篇想象力巅峰的百宝箱。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .sf-box { rx: 8; stroke-width: 1.5; }
            .sf-bg-core { fill: #1d3557; stroke: #2a4d7a; }
            .sf-bg-node { fill: #fbf9f4; stroke: #8c2d19; stroke-width: 2; }
            .sf-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .sf-t-d { fill: #8c2d19; font-family: sans-serif; font-size: 12.5px; font-weight: 700; text-anchor: middle; }
            .sf-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sf-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sf-line { stroke: #8c2d19; stroke-width: 1.8; fill: none; }
          </style>

          <defs>
            <marker id="sf-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 核心：微型科幻思想发动机 -->
          <rect x="230" y="20" width="220" height="75" class="sf-box sf-bg-core" />
          <text x="340" y="48" class="sf-t-w">微型科幻思想发动机</text>
          <text x="340" y="68" class="sf-t-sub-w">认知陌生化 · 逻辑硬核 · 终局反转</text>
          <text x="340" y="84" style="fill:#a8dadc; font-size:9.5px; text-anchor:middle;">“在方寸之间轰碎世俗思维偏见”</text>

          <!-- 四向辐射箭头 -->
          <path d="M 230 55 L 145 135" class="sf-line" marker-end="url(#sf-arr)" />
          <path d="M 290 95 L 245 160" class="sf-line" marker-end="url(#sf-arr)" />
          <path d="M 390 95 L 435 160" class="sf-line" marker-end="url(#sf-arr)" />
          <path d="M 450 55 L 535 135" class="sf-line" marker-end="url(#sf-arr)" />

          <!-- 四大母题卡片 -->
          <rect x="15" y="140" width="155" height="125" class="sf-box sf-bg-node" />
          <text x="92" y="168" class="sf-t-d">① 人工智能与图灵</text>
          <text x="92" y="190" class="sf-t-sub">终极算力演化 · 意识觉醒</text>
          <text x="92" y="208" class="sf-t-sub">人机身份倒错 · 逻辑自毁</text>
          <text x="92" y="226" class="sf-t-sub">经典：超级电脑与上帝之名</text>
          <text x="92" y="244" style="fill:#1d3557; font-size:10px; font-weight:700; text-anchor:middle;">“神明原是最后的主机”</text>

          <rect x="180" y="165" width="155" height="125" class="sf-box sf-bg-node" />
          <text x="257" y="193" class="sf-t-d">② 时空因果与悖论</text>
          <text x="257" y="215" class="sf-t-sub">祖父悖论闭环 · 蝴蝶风暴</text>
          <text x="257" y="233" class="sf-t-sub">修正历史引发更大坍塌</text>
          <text x="257" y="251" class="sf-t-sub">经典：穿梭客的永恒悔恨</text>
          <text x="257" y="269" style="fill:#1d3557; font-size:10px; font-weight:700; text-anchor:middle;">“因果链条不可戏弄”</text>

          <rect x="345" y="165" width="155" height="125" class="sf-box sf-bg-node" />
          <text x="422" y="193" class="sf-t-d">③ 地外文明与傲慢</text>
          <text x="422" y="215" class="sf-t-sub">相对论沟通 · 费米沉默</text>
          <text x="422" y="233" class="sf-t-sub">异星视角下的恶心人类</text>
          <text x="422" y="251" class="sf-t-sub">经典：《他们是由肉做的》</text>
          <text x="422" y="269" style="fill:#1d3557; font-size:10px; font-weight:700; text-anchor:middle;">“肉块竟然也能思考？”</text>

          <rect x="510" y="140" width="155" height="125" class="sf-box sf-bg-node" />
          <text x="587" y="168" class="sf-t-d">④ 末日余晖与社会</text>
          <text x="587" y="190" class="sf-t-sub">核冬天废墟 · 冰冷遗物</text>
          <text x="587" y="208" class="sf-t-sub">自动化兵器无主运转</text>
          <text x="587" y="226" class="sf-t-sub">经典：地球最后一人敲门声</text>
          <text x="587" y="244" style="fill:#1d3557; font-size:10px; font-weight:700; text-anchor:middle;">“敲门声在死寂中响起”</text>
        </svg>
      </div>

      <div class="sub-heading">全书四大核心思想母题谱系</div>
      <ul class="bullet-list">
        <li><strong>人工智能与意识起源（AI & Consciousness）：</strong>探索硅基心智在何种临界点跨入灵魂领域。计算机是否会因为逻辑运算的穷尽而产生痛苦？人类在将全部记忆托管给云端后，是否自愿完成了退化？</li>
        <li><strong>时空干涉与因果宿命（Time Travel & Causality）：</strong>时间旅行者为了拯救心爱之人一次次跳回过去，却惊恐地发现每一次微小的纠偏，都是导致对方死亡历史得以发生的真正因果动因。宿命如同莫比乌斯环，将自由意志嘲弄得体无完肤。</li>
        <li><strong>外星异质生命与认知绝壁（Alien Otherness）：</strong>彻底抛弃‘好莱坞人形外星人’的幼稚预设。外星文明可能是纯粹的气体意识、硅基晶体、或是跨越光年的引力波扰动。人类引以为傲的语言、爱与艺术，在异类眼中不过是可笑的碳水化合物分泌物。</li>
        <li><strong>末世绝境中的人类微光（Post-Apocalyptic Humanism）：</strong>在核战后荒凉废墟中，在所有生命死绝的地下避难所里，一台老旧的留声机依然在空无一人的房间里自动播放着贝多芬的《月光曲》。文明虽然熄灭，但美的回响证明了人类曾在此存在。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书由整整一百个独立成篇的千字极短篇小说组成。舞台在几十亿光年的星际联邦、拥挤逼仄的未来赛博贫民窟、远古恐龙丛林、核战后被灰烬覆盖的防空洞之间自由跳跃。每一个故事通常在开篇平静交代一个看似合乎日常逻辑的情境，随后两名角色展开简短而刀刀见血的对话或行动；就在读者以为即将滑向预期结局的最后一段乃至最后一句话，作者突然掀翻桌子，用一个不可辩驳的冷酷事实摧毁读者的全盘预设，留下震耳欲聋的思想回响。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处关心的是<strong>“人类认知的局限性与自我中心的荒谬”</strong>。我们所有关于真理、善恶、美丑的判断，都仅仅建立在地球重力加速度9.8、碳水化合物代谢与平均七八十年肉身寿命这几项极其狭隘的物理参数之上。微型科幻通过瞬间改变这一底层参数，逼迫读者看清：我们奉为神圣的一切，在浩瀚宇宙法则面前是多么偶然与脆弱。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        不是漫长马拉松式的温水煮青蛙，而是坐上一百次过山车——在每一个三分钟里，你的心智被迅速提升至万米高空，随后在一句急转直下的尾声中，体验认知失重带来的眩晕与狂喜。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个厌倦了冗长说教、渴望在短时间内激活大脑批判性思维与想象力触角的现代读者，以及每一个试图探究文学叙事精湛结构工艺的写作者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>人类日常世俗认知惯性 vs 宇宙冷酷客观物理现实与异维真理。</strong></p>

      <div class="sub-heading">微型科幻的四步精密手术刀结构</div>
      <ol class="num-list">
        <li><strong>第一步 · 设定抛出（The Hook）：</strong>第一句话绝无废话，直接亮出核心异常参数（例如：“地球上的最后一个人独自坐在房间里。这时，敲门声响了。”）。读者瞬间被拽入异质世界。</li>
        <li><strong>第二步 · 紧缩推进（The Compression）：</strong>彻底剔除一切次要环境描写与家常闲聊。两三句对话交代两极冲突，将悬念如弹簧般压缩至物理极限。</li>
        <li><strong>第三步 · 认知引诱（The Misdirection）：</strong>作者故意利用人类读者固有的地球偏见（如默认‘主角是人类’、默认‘长相丑陋的是侵略者’、默认‘科技高级等于道德高尚’）设下思维陷阱，引诱读者向错误的方向做出推断。</li>
        <li><strong>第四步 · 尾声爆破（The Stinger / The O. Henry Twist）：</strong>在终盘最后一个句点前引爆炸弹。这记反转绝非胡编乱造的机械降神，而是前文所有线索收网后的必然结果，让读者在惊呼之余不得不承认作者逻辑的绝对严密。</li>
      </ol>

      <div class="sub-heading">决定性叙事经典案例拆解</div>
      <div class="card-box">
        <strong>名篇《他们是由肉做成的》（They're Made out of Meat · 特里·比森）：</strong><br>
        两个外星高维观察者在飞船中讨论地球科幻发现。外星人甲满腹狐疑地向长官汇报：他们真的在全宇宙各个频道侦听到了无线电波，但发射信号的生物不可理喻——它们竟然‘完全是由肉做成的’！‘肉怎么可能思考？肉怎么可能制造机器？’外星长官感到无比恶心，最终裁定：把地球从智慧生命星图中彻底抹去，当做不存在。这篇千字对话完全不用动作描写，仅凭语言纯粹的陌生化视角，把人类自鸣得意的‘万物之灵’傲慢解构得体无完肤。
      </div>"""

    sec05 = """      <div class="sub-heading">人物塑造的类型学奇迹：观念的具象化化身</div>
      <p>微型科幻没有篇幅去细致刻画一个人物长达三十年的童年心理创伤。在这里，人物被提炼为<strong>“某一种文明价值取向的纯粹承载体”</strong>：<br>
      那位为了解答‘宇宙熵增能否逆转’而熬白了头发、一代代升级超级计算机的程序员；那位为了给病榻上的女儿买一剂退烧药而不惜以自己二十年记忆为抵押的赛博父亲；那位在废墟中执着地给一具枯骨整理领带的生化保姆机器人……正是因为叙事的高度浓缩，人物在生死决断那一秒所迸发出的光芒，才具有如同钻石般纯粹坚硬的感染力。</p>

      <div class="sub-heading">反派的消失与系统性冷酷</div>
      <p>优秀科幻极少设立脸谱化的单纯恶棍。在《百部微型科幻》中，制造绝境的往往不是残暴的独裁者，而是<strong>无处不在的物理定律（光速不可逾越、热力学熵增不可逆、时间维度的单向流动）</strong>，或者是人类自身制造出的、由于过于精密而失去制动能力的官僚算法系统。这种‘没有敌人的悲剧’，深刻映射出近代人类在自身造物面前的异化困境。</p>"""

    sec06 = """      <div class="sub-heading">极致修辞经济学：文学减法的最高境界</div>
      <p>在千字微型小说中，文字就是黄金。每一个形容词都必须承担双重甚至三重任务——既要刻画环境，又要暗示人物心理，还要在潜意识中为最后的惊天反转埋下伏线。这种文字气质是<strong>冷峻、克制、锋利且高度理性的</strong>。它像是一组精密的手表齿轮，只要抽掉任何一个词，整个故事在结尾的反转爆发力就会大打折扣。</p>

      <div class="sub-heading">三大核心象征网络</div>
      <ul class="bullet-list">
        <li><strong>闪烁的终端屏幕与绿光 (The Terminal Screen)：</strong>在无数短篇中反复出现的意象。冷冰冰的阴极射线管屏幕，既是通往全知全能数字神明的圣殿窗口，也是将人类肉身与自然大地彻底切断的隔离玻璃。</li>
        <li><strong>时钟与单向箭头 (The Arrow of Time)：</strong>滴答作响的秒针与时间机器仪盘。它象征着物理世界不可抗拒的残酷性，无论人类多么深情、多么悔恨，过去永远如同一尊冷酷的大理石雕像，绝不容许凡人擅自涂改。</li>
        <li><strong>空无一人的宇宙摇篮 (The Empty Cradle)：</strong>废弃的飞船客舱、荒凉的殖民地穹顶。它象征着人类走出地球襁褓后，所必须承受的漫长、冰冷且毫无回音的宇宙存在主义孤独。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（百花齐放）：</strong>一百次妙趣横生、智商拉满、让人欲罢不能的脑洞盛宴与奇思妙想博览会。<br>
        <strong>深层架构（理性自省）：</strong>运用严格的形式逻辑，将人类在技术、伦理、政治与家庭生活中的每一个微小自私推导至极端荒谬的境地，充当现代科技社会的警醒哨兵。<br>
        <strong>根本架构（宇宙谦卑）：</strong>重塑人类在星际尺度下的自我认知。打破‘人类是万物尺度’的神话，让读者学会以一种平和、包容且充满敬畏的心态注视未知的星空。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的阅读指导</div>
      <p>阿西莫夫在序言中明确告诫读者：微型科幻的阅读节奏必须是‘慢品’而非‘鲸吞’。一口气连续刷完三十篇只会导致感官麻木与审美疲劳；正确的打开方式是将它放在床头或案前，每次只读一两篇。在合上书本后，花三分钟去复盘作者是如何在短短三段话内完成布局并引爆反转的，把它当做一件精密的瑞士钟表拆解研磨。</p>

      <div class="sub-heading">警惕两种典型的浅层误读</div>
      <ul class="bullet-list">
        <li><strong>误读一：将微型科幻贬为‘不入流的快餐文学’。</strong>纯文学界曾长期轻视科幻短篇。然而历史证明，阿西莫夫的《最后的问题》、阿瑟·克拉克的《九十亿个上帝的名字》所展现的形而上哲学深度与文学美感，足以傲视绝大多数充斥着生活琐碎纠葛的传统庸俗长篇。</li>
        <li><strong>误读二：以为反转就是‘故弄玄虚的胡扯’。</strong>优秀的科幻反转绝非魔术师从帽子里突然掏出一只兔子，它的每一个齿轮在前文都有伏笔。如果反转违背了作者自设的世界观物理铁律，那就是劣质伪劣之作。</li>
      </ul>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>半个世纪前大师们在微型科幻中写下的诸多荒诞推演，今天已经变成耸人听闻的现实新闻：<br>
      生成式人工智能开始以假乱真地模仿人类情感，令无数孤单者深陷数字爱恋；算法评分系统无声地决定着一个人的求职、贷款与出行权限；人们在虚拟现实中流连忘返，视现实生活为毫无意义的苦役……大师们在千字短篇中敲响的警钟，正在我们生活的每一个角落应验。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>如果你的手机算法比你本人更清楚你下一秒想看什么、想买什么、爱上什么人，你还算拥有真正的‘自由意志’吗？</li>
        <li>在高度数字化的今天，如果你的所有社交账号在一夜之间被系统注销，你靠什么证明自己在现实世界中真实存在？</li>
        <li>在面对复杂人生抉择时，你倾向于依赖精密的数据分析给出最优解，还是听从内心哪怕并不完美的道德直觉？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“如果你嫌长篇科幻太厚读不下去，一定要看阿西莫夫选的这本《百部微型科幻》。每一篇只有一千字，每一篇都在最后一行狠狠敲击你的大脑。它证明了最震撼的宇宙神话不需要几十万字铺垫，一颗子弹大小的篇幅就能击穿你的常识。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天向大家隆重推荐《百部经典微型科幻精选》。很多人以为短篇只是长篇的缩写，大错特错！微型科幻是文学界的‘高能粒子对撞机’。在这本书里，阿西莫夫等黄金时代巨匠展示了令人惊叹的叙事经济学。他们是如何在三页纸里颠覆世界的？第一步，抛出一个奇异的极端设定；第二步，剔除所有无关废话，用两三句对话推向高潮；第三步，利用你作为人类的习惯性盲区设下陷阱；最后一步，在全篇最后一个标点符号前引爆反转！比如著名的《他们是由肉做的》，全篇只是两个外星人的对话，它们侦听到了地球的无线电信号，却恶心又困惑地发现：发出信号的竟然不是机器或能量波，而是一群‘由肉做成、用肉块拍打空气发出声波’的碳水化合物怪物！短短几百字，人类所有的自命不凡瞬间化为齑粉。在今天碎片化阅读的时代，与其把时间浪费在毫无营养的短视频上，不如每天花三分钟品读一篇大师的微型科幻，在纯粹的逻辑与惊奇中重新激活自己的大脑。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “伟大的智慧从来不需要庞大身躯的堆叠；当思维的闪电在方寸字行间划破夜空，整座宇宙的星辰都将为之黯然失色。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：如果时间有限必读的五大殿堂神作</div>
      <ul class="bullet-list">
        <li><strong>必读第一篇 · 艾萨克·阿西莫夫《最后的问题》：</strong>人类不断追问超级电脑如何逆转热力学熵增，历经亿万年宇宙死寂后，只剩纯思维的主机在虚空中宣布：‘要有光！’</li>
        <li><strong>必读第二篇 · 特里·比森《他们是由肉做成的》：</strong>在外星高维智慧眼中，人类如同蠕动的牛排般不可理喻。</li>
        <li><strong>必读第三篇 · 阿瑟·克拉克《九十亿个上帝的名字》：</strong>喇嘛雇佣电脑排查神的所有真名，当最后一个名字打印完成，头顶的群星开始一颗颗无声熄灭。</li>
        <li><strong>必读第四篇 · 弗雷德里克·布朗《敲门》：</strong>世界上最后一个人独自坐在房间里，敲门声却响起的终极悬疑开场。</li>
        <li><strong>必读第五篇 · 罗伯特·谢克里《危险的奖赏》：</strong>真人秀追杀与全民围观嗜血，提前半个世纪预言流量时代的荒谬。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 形式与容量的辩证：</strong>为什么一个构思极度绝妙的科幻核心创意，写成一千字的极短篇往往比扩写成几十万字的长篇更加震撼、更具有穿透力？
      </div>
      <div class="card-box">
        <strong>Q2 · 终局反转的审美快感：</strong>我们在读到结尾的反转时，所获得的快乐究竟是‘被作者智商碾压的受虐快感’，还是‘既有世俗认知被打破后豁然开朗的解放感’？
      </div>
      <div class="card-box">
        <strong>Q3 · 技术乌托邦的反思：</strong>在收录的众多故事中，为什么凡是试图用超级计算机建立‘完美无痛社会’的尝试，最终无一例外走向了文明的死绝与荒诞？
      </div>
      <div class="card-box">
        <strong>Q4 · 孤独的普遍性：</strong>为什么跨越了光年、战胜了疾病的未来人类，在星际深空之中依然如同初生婴儿般饱尝孤独？科技能够治愈人类的终极孤独吗？
      </div>
      <div class="card-box">
        <strong>Q5 · 语言的边界：</strong>当故事中的外星文明用气味、电磁波动或纯粹意念交流时，人类基于声带震颤发明的拼音与汉字，是否在根本上限制了我们理解更高维度宇宙真理的能力？
      </div>"""

    sec13 = """      <div class="sub-heading">① 创意构思工具：“设定逆转三棱镜” (The Sci-Fi Inversion Prism)</div>
      <p><strong>应用场景：</strong>日常写作构思、破除思维定式、商业反直觉产品设计。<br>
      <strong>第一步（找公理）：</strong>在日常生活中找出一件所有人都觉得理所应当的铁律（例如：“诚实是最高美德”、“记忆越清晰越好”、“死亡是生命的敌人”）。<br>
      <strong>第二步（改参数）：</strong>设定一项技术或未来环境打破这项铁律（例如：“发明了一种能够彻底清除痛苦记忆的橡皮擦药水”、“脑机接口强制公开所有人的每一个心念”）。<br>
      <strong>第三步（设陷阱与爆破）：</strong>写一个主人公以为这项技术拯救了自己，却在最后一行绝望发现：正是由于消除了这项‘痛苦’，他彻底丧失了作为人类最宝贵的东西（800字内完成微型短篇）。</p>

      <div class="sub-heading">② 现实观察实验：“荒谬常识记录本”</div>
      <p>用一整天的时间，把自己当做一个刚刚降落地球的外星人类学家。观察身边行人的日常行为（如排队买奶茶、低头对着发光的玻璃方块微笑、在格子间里对着塑料键盘敲击一天），用完全客观、不带人类文化偏见的词汇记录三件看似正常、实则荒诞不经的地球人日常仪式。</p>

      <div class="sub-heading">③ 极短篇仿写挑战</div>
      <p>模仿阿西莫夫《最后的问题》的跨时空跳跃结构，写一篇五百字以内的极短篇：以‘人类制造的第一台微型量子计算机’为起点，每隔两段跨越十万年，记录它与最后一位人类的对话，结尾必须包含一句意料之外的终极反转台词。</p>"""

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
