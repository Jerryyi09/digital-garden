# -*- coding: utf-8 -*-
"""
Round 14: Shakespeare's Sonnets, Tales from Shakespeare, Stories from Classical Drama (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_sonnets():
    data = {
        "title_cn": "莎士比亚十四行诗",
        "title_en": "Shakespeare's Sonnets",
        "author_cn": "威廉·莎士比亚",
        "author_en": "William Shakespeare",
        "sub_desc": "英语抒情诗歌的珠穆朗玛峰 · 爱、欲望、时间的镰刀与艺术永恒的十四行交响",
        "hero_quote": "我怎能把你比作炎炎夏日？你比夏天更可爱，也更温婉温良；只要有人活着，只要眼睛看得见，这诗便永存，并赐给你永恒的生命！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">诗仙与剧作家</div><div class="spec-val">威廉·莎士比亚 (1564–1616)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1609 年索普盗印版出版 / 抒情诗巅峰</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">商籁体格律抒情诗集 / 哲学心理诗篇</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">共 154 首经典十四行诗</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 终身必读诗歌圣殿</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">抑扬五步格诗律张力与时间哲学对抗深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把莎士比亚十四行诗轻浮地误解为普通的情侣表白‘浪漫甜言蜜语集’。莎翁在此彻底打碎了彼特拉克时代将女性神圣化、把爱情空洞化为‘金发碧眼完美雕像’的虚伪传统。全书后半部分（127–154首）以极其坦诚甚至自我鞭笞的现代心理学笔触，描写了一个皮肤黝黑、琴艺粗糙、甚至道德不贞的‘黑女士（Dark Lady）’，并写尽了肉体欲望带来的恶心、自责与内耗。这是一部<strong>赤裸裸解剖人类情欲深渊、以诗歌之刃与冷酷时间展开生死搏斗的形而上学哲学巨著</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 第18首《我怎能把你比作夏日》对时间法则的神圣宣战：</strong>全人类文学史上最著名的诗篇。夏天的灿烂往往过于炎热短暂，狂风会吹落五月娇嫩的蓓蕾，天地间一切美好终将被无情时间的镰刀所收割。然而，莎翁在最后两行对联句中完成了至高的反转：‘只要这首诗存在一天，你的青春与美丽就将超越死亡，在我的文字中永生！’艺术在此刻被赋予了战胜宇宙物理大限的真正神性。
      </div>
      <div class="card-box">
        <strong>② 前126首对‘美貌青年（Fair Youth）’的劝婚与精神繁衍哲学：</strong>前17首著名的‘繁衍十四行诗（Procreation Sonnets）’。诗人不是在宣泄荷尔蒙，而是在苦苦劝诫那位美貌贵族青年成婚生子：‘唯有通过生育后代，你的美丽才不至于随白骨入土，才能在儿女的眼睛里复制出永恒的青春！’这种将肉体繁衍升华为对抗衰老神器的沉思，深具古典希腊哲人的博大智慧。
      </div>
      <div class="card-box">
        <strong>③ 第129首对‘欲望之罪’的法医级精神解剖：</strong>英语诗歌史上对‘事后圣徒、事前魔鬼’的性心理最冷酷的剖析：‘在享受之前，欲望是背叛、凶残、贪婪、绝不顾惜名誉的狂怒；在享受的那一刹那，它是诱饵与陷阱；而一旦享受完毕，它立刻化作深入骨髓的鄙视与悔恨！’莎翁用短短十四行，撕碎了全人类在生理本能面前的一切虚伪遮羞布。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        1590年代伦敦鼠疫大爆发，剧场多次被迫封闭。莎翁在沉潜深思中，将无韵戏剧台词的戏剧张力融入严格的伊丽莎白十四行诗格律，创造了英语诗歌史上的奇迹。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .sn-box { rx: 8; stroke-width: 1.5; }
            .sn-bg-poet { fill: #1d3557; stroke: #2a4d7a; }
            .sn-bg-youth { fill: #2a9d8f; stroke: #40916c; }
            .sn-bg-dark { fill: #8c2d19; stroke: #a33b24; }
            .sn-bg-time { fill: #131619; stroke: #59645f; }
            .sn-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .sn-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .sn-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sn-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sn-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .sn-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .sn-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="sn-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 诗人自我 (中心) -->
          <rect x="230" y="25" width="220" height="120" class="sn-box sn-bg-poet" />
          <text x="340" y="52" class="sn-t-w">诗人自我 (The Speaker)</text>
          <text x="340" y="72" class="sn-t-sub-w">饱经沧桑中年学者 · 面临衰老焦虑</text>
          <text x="340" y="90" class="sn-t-sub-w">深谙时间的残暴与艺术的永恒</text>
          <text x="340" y="108" class="sn-t-sub-w">在崇高友情与狂乱肉欲间反复撕扯</text>
          <text x="340" y="126" style="fill:#a8dadc; font-size:10.5px; font-weight:700; text-anchor:middle;">以诗笔为剑对抗死神的终极斗士</text>

          <!-- 左翼：美貌贵族青年 (第1–126首) -->
          <path d="M 230 85 L 160 85" class="sn-blue" marker-end="url(#sn-arr)" />
          <text x="195" y="75" class="sn-lbl" style="fill:#2a9d8f;">理想之美</text>

          <rect x="15" y="30" width="145" height="110" class="sn-box sn-bg-youth" />
          <text x="87" y="58" class="sn-t-w">美貌青年 (Fair Youth)</text>
          <text x="87" y="78" class="sn-t-sub-w">希腊式古典纯洁化身</text>
          <text x="87" y="96" class="sn-t-sub-w">劝婚生子 · 繁衍诗篇</text>
          <text x="87" y="114" class="sn-t-sub-w">遭遇情敌诗人挑拨背叛</text>
          <text x="87" y="128" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">精神不朽的终极投射</text>

          <!-- 右翼：黑肤女士 (第127–154首) -->
          <path d="M 450 85 L 520 85" class="sn-solid" marker-end="url(#sn-arr)" />
          <text x="485" y="75" class="sn-lbl">肉欲深渊</text>

          <rect x="520" y="30" width="145" height="110" class="sn-box sn-bg-dark" />
          <text x="592" y="58" class="sn-t-w">黑女士 (Dark Lady)</text>
          <text x="592" y="78" class="sn-t-sub-w">黑发黑眸 · 离经叛道</text>
          <text x="592" y="96" class="sn-t-sub-w">反彼得拉克白皙神话</text>
          <text x="592" y="114" class="sn-t-sub-w">肉体狂喜与自责痛楚</text>
          <text x="592" y="128" style="fill:#f0dcd8; font-size:9.5px; text-anchor:middle;">“明知有害却深陷其中”</text>

          <!-- 下方：终极大敌 —— 吞噬一切的时间 -->
          <path d="M 340 145 L 340 200" class="sn-solid" marker-end="url(#sn-arr)" />
          <text x="385" y="175" class="sn-lbl">时间之战</text>

          <rect x="160" y="200" width="360" height="115" class="sn-box sn-bg-time" />
          <text x="340" y="228" class="sn-t-w">暴虐统治者：冷酷无情的时间 (Devouring Time)</text>
          <text x="340" y="248" class="sn-t-sub-w">时间的镰刀收割红颜 · 岁月在额头刻下战壕沟壑 · 衰老的无情降临</text>
          <text x="340" y="266" class="sn-t-sub-w">唯有十四行诗的严密金字塔，让爱跨越四百年依然在每一个读者的嘴唇上复活</text>
          <text x="340" y="284" class="sn-t-sub-w">“这诗便永存，并赐给你永恒的生命！”</text>
          <text x="340" y="300" style="fill:#a8dadc; font-size:10.5px; font-weight:700; text-anchor:middle;">诗歌确立了人类精神战胜物理死亡的最高凯旋</text>
        </svg>
      </div>

      <div class="sub-heading">核心抒情对象与意象谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>诗人叙述者（William Shakespeare 抒情主体）：</strong>站在人生的秋天，头发斑白，深感精力不济。他在诗行中极度坦白自己的自卑：出身贫寒、靠写戏为生被贵族轻视、腿部跛足残损。然而当他手握羽毛笔面对大理石墓碑与暴虐时间时，他展现出比任何国王更不可一世的骄傲：‘暴君的铜像会倒塌，战争会摧毁宏伟的庙宇，唯有我的诗行，将跨越死神冷漠的阻隔，永远呼吸在后人的唇齿之间！’</li>
        <li><strong>美貌青年（Fair Youth，通常考证为南安普敦伯爵或彭布罗克伯爵）：</strong>西方古典男性美学神圣理想的化身。他集中了古希腊雕像般的纯洁与黄金般的光华。诗人待他超越了普通朋友，视其为自己在人间‘对抗衰老的唯一替身’。当青年背叛诗人、甚至与黑女士私通时，诗人经历了剧烈的心碎，但最终在第116首中升华出全人类关于爱最著名的定义：‘爱不是爱，如果在它发现改变时便跟着改变；爱是一座坚固的灯塔，任凭暴风雨摇撼，永远不可动摇！’</li>
        <li><strong>黑肤女士（The Dark Lady）：</strong>打破文艺复兴一切虚伪美学的反叛女郎。在当时的伦敦，金发、雪肤、红唇是唯一的审美标准。莎翁在第130首开篇就写：‘我情妇的眼睛一点都不像太阳；红珊瑚比她的嘴唇还要红得多；如果雪是白的，那她的胸口就是灰暗的；如果头发是金丝，那她的头上长出的就是黑色的铁丝！’然而接着诗人写道：‘但我发誓，我的爱人世间罕见，比任何被虚假比喻夸大的仙女都要珍贵万倍！’这种对真实、粗粝、有瑕疵生命的狂热接纳，开创了现代写实爱情诗的先河。</li>
        <li><strong>时间的镰刀（Time's Scythe）：</strong>全诗集最大的冷血反派。时间从不疲倦，它给青年镀上荣光，随即又在美人的额头上深深刻下如战壕般的皱纹，将世间所有珍宝送入泥土。整本诗集就是一部诗人用十四行诗的格律方阵，向这柄宇宙大镰刀发起冲锋的壮烈战史。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书由整整一百五十四首工整严密的十四行诗组成一个隐秘的情感大史诗。前一百二十六首呈献给一位身份显赫、年轻俊美的贵族美貌青年。开篇前十七首是热切的‘劝婚诗’，诗人苦口婆心劝诫青年尽快娶妻生子，将举世无双的美丽通过血脉代代相传，战胜无情时间的剥夺。随后诗篇展开了更为宏大深邃的哲学漫游：从第十八首宣告通过诗歌赋予青年永恒不朽，到思念、离别、受冷落的痛苦，再到青年被竞争对手诗人诱走、甚至染指了诗人的情妇所带来的背叛创伤，诗人历经嫉妒、自卑、原谅与痛苦的自省，最终在第一百一十六首中达成了对‘爱是永恒灯塔’的至高领悟。后二十八首（第一百二十七至一百五十四首）笔锋剧烈陡转，转向了一位违背传统金发雪肤审美、黑发黑眸、性情放荡的‘黑女士’。诗人陷入了肉体强烈的欲望折磨与内疚深渊，他在第129首痛斥情欲的虚幻与自责，在第130首用最幽默写实的笔触描绘黑女士粗糙的嗓音与呼吸，在狂热的肉体沉溺与精神痛苦中展开搏斗。全集最后以两首关于丘比特沉睡、爱火煮热温泉的希腊神话寓言诗从容谢幕，留下了一部跨越肉体与灵魂、时间与永恒的全景人类精神抒情丰碑。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃叩问的是<strong>“在时间的不可逆单向流逝、肉体必然走向衰老与死亡的冰冷物理铁律面前，人类究竟依靠何种精神力量才能赢得永恒的尊严”</strong>。莎士比亚证明：生物学上的血脉繁衍是第一道防线，但唯有艺术的创造力与无私包容的真诚大爱，才是穿透几百年时空封锁、让生命在死神面前赢得最终胜利的神圣奇迹。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一组用最坚固的黄金与大理石雕刻出的十四行音律琴键：在一次次关于白发、皱纹、欲望与背叛的午夜叹息中，见证人类诗笔如何击碎死神的镰刀，在虚无深处点亮一盏永恒不灭的爱情灯塔。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾对容颜老去感到隐隐恐慌、经历过欲望诱惑与自责撕扯，渴望在诗歌最严格的音律美感中获得灵魂升华与宁静的文学深读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以不可抗力摧毁一切美好容颜与生命的‘时间暴政’ vs 诗人依靠十四行诗格律金字塔与纯粹大爱建立的‘永恒抗争’。</strong></p>

      <div class="sub-heading">全书四大结构抒情推进链条</div>
      <ol class="num-list">
        <li><strong>第一组 · 劝婚与镜像繁衍（第1–17首）：</strong>从‘为了美的不灭而祈求繁衍’起步，劝诫青年不可自私独享美貌，必须通过婚配生子向时间索回利息。</li>
        <li><strong>第二组 · 诗歌战胜死亡与永恒加冕（第18–126首）：</strong>以第18首为分水岭，诗人宣布诗歌本身即是不朽的方舟；历经分别、流言、情敌诗人的竞争、青年冷遇的自卑，最终在第116首确立爱超越时间镰刀的神圣定义。</li>
        <li><strong>第三组 · 黑女士与欲望的深渊试炼（第127–152首）：</strong>颠覆传统彼得拉克诗学；反讽与写实并重；第129首解剖肉欲之罪，第130首赞美真实肉体，在情欲痛苦中展现现代人性的复杂撕扯。</li>
        <li><strong>第四组 · 希腊爱神之火的哲理尾声（第153–154首）：</strong>丘比特火炬点燃冷泉化为温汤，寓言化终局：‘爱能温暖一切，唯有爱本身无法被任何泉水降温。’</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第十八首《我怎能把你比作炎炎夏日》（Shall I compare thee to a summer's day?）：</strong>在此诗之前，诗人的底气是脆弱的，只能哀求青年结婚生子靠后代对抗死亡；从这一首开始，莎士比亚找到了属于艺术家自己的至高武器——他挺直脊梁宣告：无需指望未知的子孙，‘我写下的每一行诗，就是你永不凋零的夏天！’这一刻确立了整部诗集作为艺术征服死神的崇高转折。
      </div>"""

    sec05 = """      <div class="sub-heading">莎士比亚十四行诗格律（The Shakespearean Sonnet）的形式哲学</div>
      <p>莎翁彻底改造了意大利彼得拉克的十四行诗结构，确立了经典的‘三段四行诗 + 一对对联句（ABAB CDCD EFEF GG）’结构。这种结构具有极强的<strong>逻辑辩论与思维递进功能</strong>：<br>
      前四个小节提出核心两难困境（如美貌必衰）；中间四个小节将困境进一步推向绝望极限（如死神张开大口）；第三个小节出现戏剧性转折词‘But（但是）’，从绝望中开掘出一丝微弱生机；最后两行对联句（GG）如同大钟敲响，以石破天惊的双行警句完成全诗的终极反转与哲学收网。形式的严格对称，赋予了思想无与伦比的穿透力。</p>

      <div class="sub-heading">第一百一十六首：人类历史上关于真爱的最高宪章</div>
      <p>第116首被誉为世界诗歌史上最完美的篇章：‘爱绝不是爱，如果在它发现改变时便跟着改变，或者在对方转身时便跟着转身。不！爱是一座永恒的灯塔，它凝视着暴风雨，却永远不可动摇；它是每一艘迷航船只的北极星，虽然它的高度可以测量，但它的价值无人可知。爱不是时间的弄臣，哪怕红唇玉颊终将难逃时间弯弯的镰刀；爱绝不随着短暂的岁月而改变，它坚持到底，直到大限的尽头！如果这是错误的、并且在我身上得到了证实，那我就从未写过一个字，世上也从未有任何人真正爱过！’莎翁用逻辑归谬法，为爱立下了不可动摇的法典。</p>"""

    sec06 = """      <div class="sub-heading">高密度双关语、隐喻与音乐性通感的诗学肌理</div>
      <p>莎士比亚在十四行诗中展现了其语言炼金术的最纯熟功力。每一行诗都暗藏着极其精妙的英国文艺复兴双关语（如‘Will’既是诗人威廉的名字，又代表欲望、遗嘱、意志三重涵义）。五步抑扬格的音步如同人类心跳的节律，在长短音的轻重交替中，完美传达出思念时的急促、绝望时的窒息与释怀时的从容。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>时间的弯弯镰刀 (Time's Sickle)：</strong>全书冷酷的时间收割者符号。无论帝王的宫殿还是绝代佳人的容颜，都在镰刀下如同秋麦般纷纷倒伏，象征<strong>一切肉身存在的不可挽回易逝性</strong>。</li>
        <li><strong>黑夜中的北极星 (The Northern Star)：</strong>第116首中照耀迷途船只的永恒光斑。它象征<strong>超越人世变迁、超越外表衰老的绝对忠诚与纯粹大爱</strong>。</li>
        <li><strong>带刺的红玫瑰与枯萎花瓣：</strong>反复出现的生命象征。玫瑰哪怕在冬日凋零，但将其蒸馏制成香水，其芬芳便能在玻璃瓶中长存，象征<strong>艺术创造力将脆弱生命蒸馏为永恒香气的神圣转化</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（古典抒情诗篇长卷）：</strong>诗人对美貌贵族青年的劝婚崇拜赞歌，与对神秘黑女士充满情欲折磨的十四行诗集。<br>
        <strong>深层架构（心理现实主义解剖）：</strong>对人类真实欲望、嫉妒、自卑、衰老恐惧与背叛痛苦的毫无掩饰的自我剖白。彻底打碎浪漫主义的虚假粉饰，展示爱欲在肉体与精神之间的撕裂全景。<br>
        <strong>根本架构（艺术对抗时间的存在主义胜利）：</strong>文学创作赋予生命以不朽。证明文字不是虚无的玩物，它是人类抵抗宇宙物理熵增与死亡遗忘的终极诺亚方舟。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>十九世纪英国浪漫主义诗仙济慈曾指出：“在读莎士比亚十四行诗时，你感受到的是一种‘消极感受力（Negative Capability）’的最高境界——诗人完全隐匿了世俗的虚荣，甘愿将自己彻底融化在对美、对时间、对痛苦的深邃体察之中。”这部诗集是全人类感知力达到极限时的最高结晶。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天的现代人生活在一个空前惧怕衰老、狂热追求医美滤镜与快餐式速食爱情的时代：<br>
      人们为了抹平脸上一条细小的皱纹耗费巨资，为了追求瞬间的荷尔蒙刺激在社交软件上不断‘左滑右滑’，却在每一次短暂的激情后陷入更深的孤独与自责（正如第129首所言）。莎士比亚在四百年前就戳穿了这一切：靠肉身皮囊维系的吸引脆弱得像夏日的浮云；唯有在灵魂深处建立起像第116首那样‘跨越风暴而不动摇’的深度联结，人才能战胜被时间抛弃的终极恐慌。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>当你看着镜子中自己渐渐增长的白发或细纹时，你内心升起的是对衰老的恐惧焦虑，还是对岁月沉淀出智慧的从容接纳？</li>
        <li>在你的亲密关系中，如果对方的容貌、健康或财富发生了重大改变，你的爱意是否也能经受住时间的磨砺而不变质？</li>
        <li>你是否曾尝试过把生活中的某次深刻痛苦或感动，不发成随手即删的朋友圈，而是用极其克制考究的文字写进日记，让它成为滋养你一生的精神香水？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“莎士比亚十四行诗绝不是什么甜腻的情书。它是诗仙写给全人类的一战封神之作：一边感叹时间的镰刀多么狠毒，把所有美貌全变成白骨；一边挥舞笔杆子向死神宣战：‘只要有人活着，我的诗就会一直呼吸，把你的青春变成永恒！’它告诉你：皮囊终会老去，唯有艺术和真爱能穿越生死。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来仰望世界抒情诗歌的珠穆朗玛峰——莎士比亚的一百五十四首十四行诗。很多人在婚礼上听过其中的名句，但很少有人知道莎翁在里面藏了多么惊心动魄的思想较量。整本诗集的大反派不是某个人，而是那个冷酷无情的时间老头。莎士比亚写道：时间手里拿着一把大弯刀，天天在大地上收割，任凭你长得多俊美、地位多崇高，时间一过，全要在额头上被刻上深深的皱纹。一开始，莎翁很自卑，劝那个年轻美貌的贵族小伙赶紧结婚生娃，把美貌靠后代传下去。但写到第十八首，莎翁突然大彻大悟了，他写出了文学史上最狂妄也最崇高的宣战词：‘我怎么能把你比作夏天呢？夏天太短了，狂风会吹碎鲜花；但你永远的夏天绝不会凋落！因为只要全人类还有眼睛看得见、只要还有人在呼吸，我写下的这些诗句就会永远活着，并且赐给你永恒的生命！’从这一刻起，莎翁找到了艺术战胜死亡的终极密码。更绝的是后半部分，他彻底打破了以前诗歌里虚伪夸赞女人的套路。他描写的‘黑女士’头发像黑铁丝、嘴唇不红、嗓子粗粝，甚至脾气恶劣，但莎翁却说：‘我爱死她了，因为她是一个活生生的真实女人，比那些虚假的天使高贵一万倍！’读完这部诗集你会明白：真正的文学不是虚张声势的华丽辞藻，而是在看透了人生的衰老、欲望与痛苦之后，敢于用最精美的语言，在虚无的大地上筑起一座让后人热泪盈眶的爱的神庙。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “爱不是时间的玩偶，哪怕红唇玉颊终将难逃它弯弯的镰刀；爱跨越人世沧桑，坚守到底，直抵末日大限的边缘。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界十四行诗巅峰必读五大篇章</div>
      <ul class="bullet-list">
        <li><strong>必读第一首 · 第18首《我怎能把你比作夏日》：</strong>文学史上宣告艺术战胜死亡的至高宣言，字字珠玑，终身背诵。</li>
        <li><strong>必读第二首 · 第29首《当我受尽命运与世人白眼》：</strong>精读从极度自卑绝望中，仅凭思念所爱之人便如‘云雀破晓冲向九重天’的惊天心理大反转。</li>
        <li><strong>必读第三首 · 第73首《你在我身上看见晚秋季节》：</strong>世界诗歌史描写衰老最绝美的意象并置（落叶枯枝、暮色余晖、炭火灰烬）。</li>
        <li><strong>必读第四首 · 第116首《不要让我承认真实的结合有何阻碍》：</strong>全人类关于真爱永恒不可动摇之灯塔的最高哲学定义。</li>
        <li><strong>必读第五首 · 第130首《我情妇的眼睛一点不像太阳》：</strong>彻底解构浪漫主义虚伪修辞、回归真实肉身魅力的现代写实诗学里程碑。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 诗歌是否真能赐予永恒？</strong>四百年后的今天，我们依然在朗诵莎士比亚写给那个无名青年的第18首诗。在这个意义上，诗歌是否真的在物理事实上战胜了时间的遗忘法则？
      </div>
      <div class="card-box">
        <strong>Q2 · 第73首的衰老美学：</strong>‘因为你知道我即将离去，所以你的爱才更加深沉狂烈。’为什么直面死亡与衰老的有限性，反而能极大地激发出人类之间最深沉的相爱能力？
      </div>
      <div class="card-box">
        <strong>Q3 · 黑女士诗篇的现代性：</strong>莎翁在400年前就敢于将情妇描写为‘黑发铁丝、口气难闻’，这种彻底打破传统滤镜的真实白描，在今天这个充满人设滤镜的时代具有怎样的颠覆意义？
      </div>
      <div class="card-box">
        <strong>Q4 · 第129首对欲念的反思：</strong>为什么人类在被欲望驱动时会如此丧失理智，而在满足后又会陷入如此深沉的虚无与自责？我们该如何与这种生物性本能达成和解？
      </div>
      <div class="card-box">
        <strong>Q5 · 形式即力量：</strong>为什么十四行诗严苛的四四四二格律，不仅没有束缚莎士比亚的情感，反而像大坝约束激流一样，喷薄出了无与伦比的思想爆发力？
      </div>"""

    sec13 = """      <div class="sub-heading">① 审美沉淀实践工具：“第18首永恒夏天保鲜法” (The Sonnet 18 Distillation)</div>
      <p><strong>适用场景：</strong>当你经历了一次极度美好动人的瞬间（如一次深情相拥、一次完美的黄昏旅行、一次难得的家庭欢聚），害怕这美好的感觉很快被琐碎平庸的日常生活磨灭时。<br>
      <strong>第一步（捕捉三个感官锚点）：</strong>在那一刻闭上眼三秒钟，记录下当时的‘一种气味、一处光线角度、一声独特的音调’；<br>
      <strong>第二步（用十四行诗结构封存）：</strong>尝试用最克制浓缩的八句短诗，将这个瞬间写进你的实体日记本里，最后两行必须给出一个坚定的承诺；<br>
      <strong>第三步（时间的蒸馏瓶）：</strong>一年或五年后再翻开这一页，感受文字如何像香水瓶一样，瞬间释放出当年那一抹未曾凋谢的永恒夏天。</p>

      <div class="sub-heading">② 现实观察实验：“虚假赞美与真实魅力觉察”</div>
      <p>观察社交网络中人们互相吹捧的套话（如‘神仙颜值、绝美天仙’），对比你在现实中真正喜欢的一位朋友。写下这位朋友身上两处‘在世俗标准看来不完美、但让你觉得极其生动可爱真实’的微小瑕疵，体会第130首诗的人性温度。</p>

      <div class="sub-heading">③ 莎式十四行诗结构仿写任务</div>
      <p>模仿‘三段递进起承转合 + 结尾两行反转对联句’的严格结构，写一首十四行的现代短诗：主题关于‘面对手机屏幕的虚妄时，突然想起远方某位挚友的微笑’（严格恪守前四行提问、中间转折、末尾双行收网的戏剧节律）。</p>"""

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

print("Round 14 deep Sonnets ready.")

def get_deep_tales_from_shakespeare():
    data = {
        "title_cn": "莎士比亚故事集",
        "title_en": "Tales from Shakespeare",
        "author_cn": "查尔斯·兰姆 & 玛丽·兰姆",
        "author_en": "Charles and Mary Lamb",
        "sub_desc": "通往世界文学万神殿的黄金桥梁 · 戏剧向散文叙事的创造性典范化身",
        "hero_quote": "这些故事是为年轻心灵准备的一杯芬芳甘霖；愿你们在踏入这个复杂的世间之前，先从中汲取仁爱、高贵、宽恕与勇气的最初滋养。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">改编者与散文家</div><div class="spec-val">查尔斯·兰姆 & 玛丽·兰姆</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1807 年出版 / 畅销两百年经典启蒙作</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">经典戏剧散文化改编 / 青少年人文启蒙名著</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">收录二十部莎翁经典名剧改编</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">9+ 岁至全年龄文学普及必读</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">语言流畅度与莎翁原本道德诗学神髓保留度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把兰姆姐弟的《莎士比亚故事集》当成快餐式的‘少儿低幼小人书简写本’。兰姆姐弟（尤其是身患周期性精神疾患却才情横溢的姐姐玛丽·兰姆）在极为清贫艰辛的人生境遇中，以惊人的文学品味，将伊丽莎白时代繁复生涩、充满古英语双关与舞台暗语的四千行诗剧，天衣无缝地重组为<strong>行云流水、典雅纯正的十九世纪纯正散文叙事</strong>。更为珍贵的是，他们几乎完整保留了莎士比亚原著的经典名句与深刻伦理冲突，是世界文学史上最伟大的经典普及丰碑。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 姐弟分工背后的文学互补奇迹：</strong>姐姐玛丽·兰姆执笔了其中十四部浪漫喜剧（如《暴风雨》《仲夏夜之梦》《皆大欢喜》《第十二夜》），文风温婉轻快、洞察女性幽微心理；弟弟查尔斯·兰姆（英国散文泰斗、伊利亚散文作者）则执笔了六大悲剧（如《李尔王》《哈姆雷特》《奥赛罗》《麦克白》），语言凝重苍凉、雄浑壮美。双峰并立，相映成趣。
      </div>
      <div class="card-box">
        <strong>② 从‘舞台剧本台词’向‘小说心理叙事’的范式转换：</strong>传统戏剧全凭演员对白推动，缺乏旁白解释，初学者极难读懂人物动机；兰姆姐弟巧妙地在对白之间穿插了大量极具同情心的叙述者旁白，将舞台上无声的眼神与暗自的挣扎，转化为平实动人的心理剖白，让青少年在毫无阅读门槛中直接触碰莎翁最深邃的人格核心。
      </div>
      <div class="card-box">
        <strong>③ 剔除粗俗杂质、保留崇高道德火种的文明洗礼：</strong>莎士比亚为了迎合当时伦敦环球剧场的底层站坑观众，原剧中夹杂了不少粗俗开车的荤段子与血腥杂质。兰姆姐弟以非凡的人道眼光，剔除了所有腐坏枝叶，悉心呵护并放大了原著中关于‘宽恕、诚实、守信、仁慈与抗争’的道德养分，使之成为塑造一代代人文明心智的无瑕读本。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪初英国浪漫主义启蒙时期。兰姆姐弟在伦敦内殿法学院的狭小公寓里，与诗人华兹华斯、柯勒律治相伴，决意为全天下的年轻心灵搭建一座通向戏剧万神殿的黄金阶梯。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .ts-box { rx: 8; stroke-width: 1.5; }
            .ts-bg-raw { fill: #131619; stroke: #59645f; }
            .ts-bg-mary { fill: #2a9d8f; stroke: #40916c; }
            .ts-bg-charles { fill: #1d3557; stroke: #2a4d7a; }
            .ts-bg-bridge { fill: #8c2d19; stroke: #a33b24; }
            .ts-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ts-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ts-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ts-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ts-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .ts-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="ts2-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 源头：莎翁原版舞台剧本 -->
          <rect x="230" y="25" width="220" height="85" class="ts-box ts-bg-raw" />
          <text x="340" y="52" class="ts-t-w">莎士比亚原作剧本 (Shakespeare)</text>
          <text x="340" y="72" class="ts-t-sub-w">古英语无韵诗 · 繁复双关 · 舞台暗码</text>
          <text x="340" y="90" class="ts-t-sub-w">对非专业初学者构成极高阅读门槛</text>

          <!-- 兰姆姐弟双轨转化 -->
          <path d="M 270 110 L 140 160" class="ts-solid" stroke="#2a9d8f" marker-end="url(#ts2-arr)" />
          <path d="M 410 110 L 540 160" class="ts-solid" stroke="#1d3557" marker-end="url(#ts2-arr)" />

          <!-- 左：玛丽·兰姆执笔喜剧 -->
          <rect x="20" y="160" width="230" height="95" class="ts-box ts-bg-mary" />
          <text x="135" y="188" class="ts-t-w">玛丽·兰姆 (Mary Lamb · 喜剧14部)</text>
          <text x="135" y="208" class="ts-t-sub-w">温婉典雅 · 专攻女性心理与节日狂欢</text>
          <text x="135" y="226" class="ts-t-sub-w">《暴风雨》《仲夏夜之梦》《皆大欢喜》等</text>
          <text x="135" y="242" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">在文字中寄托对人间纯真美满的祈愿</text>

          <!-- 右：查尔斯·兰姆执笔悲剧 -->
          <rect x="430" y="160" width="230" height="95" class="ts-box ts-bg-charles" />
          <text x="545" y="188" class="ts-t-w">查尔斯·兰姆 (Charles · 悲剧6部)</text>
          <text x="545" y="208" class="ts-t-sub-w">散文巨匠 · 雄浑苍凉 · 沉郁深刻</text>
          <text x="545" y="226" class="ts-t-sub-w">《李尔王》《哈姆雷特》《奥赛罗》等</text>
          <text x="545" y="242" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">解剖人性深渊与命运终极受难</text>

          <!-- 下方终极成果：黄金桥梁 -->
          <rect x="180" y="275" width="320" height="55" class="ts-box ts-bg-bridge" />
          <text x="340" y="298" class="ts-t-w">跨越两个世纪的文学普及黄金桥梁</text>
          <text x="340" y="316" class="ts-t-sub-w">保留神圣金句 · 滋养千千万万年轻心灵走向成熟</text>
        </svg>
      </div>

      <div class="sub-heading">经典名篇精选与叙事艺术谱系</div>
      <ul class="bullet-list">
        <li><strong>《李尔王》（King Lear · 查尔斯·兰姆执笔）：</strong>全书最催人泪下的悲剧巅峰。老国王在暴风雨荒原上的呼嚎、考狄利娅被绞死在父亲怀中的绝唱，被兰姆以圣经般的散文句法重塑，写透了世态炎凉与亲情真伪的试金石。</li>
        <li><strong>《暴风雨》（The Tempest · 玛丽·兰姆执笔）：</strong>作为全书的第一篇开门大作。玛丽以母亲般温柔的语调，把魔法、海难、宽恕与年轻人的相爱讲得如同安徒生童话般清澈，让孩子在第一页就种下‘宽恕远比复仇高尚’的良善种子。</li>
        <li><strong>《奥赛罗》（Othello · 查尔斯·兰姆执笔）：</strong>心理惊悚的至高转化。将邪恶伊阿古如何一步步用巧言令色在摩尔人统帅心中种下嫉妒毒瘤、最终掐死纯洁苔丝狄蒙娜的悲剧，剖析得丝丝入扣，成为警惕流言猜忌的永恒教材。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书收录了莎士比亚最负盛名的二十部戏剧散文故事。涵盖了以神仙斗法与真情大团圆为底色的《暴风雨》《仲夏夜之梦》《第十二夜》《皆大欢喜》等经典浪漫喜剧；以法庭辩论与种族恩怨为核心的《威尼斯商人》；以纯洁爱情遭遇家族世仇毁灭的《罗密欧与朱丽叶》；以人性野心与罪恶感噬魂的《麦克白》；以知行脱节哲学延宕为标志的《哈姆雷特》；以及以老父错信虚伪谄媚最终发疯暴毙的《李尔王》。兰姆姐弟将原剧中动辄几十个跑龙套的次要人物精简，把错综复杂的五幕换场梳理为脉络清晰的起承转合，让每一个读者在短短几十分钟内，就能完整经历一场场世界顶级的悲喜精神洗礼。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“伟大的文学经典如何通过创造性的现代转化，打破时间与语言的阻隔，成为每一个普通孩子都触手可及的精神甘霖”</strong>。兰姆姐弟证明：真正的经典不是放在象牙塔里供少数人研磨的死骨董，而是能够化作千家万户壁炉前的睡前故事，在最柔软的心灵土壤里播下同理心与正义感的生命火种。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一座通往浩瀚文学万神殿的汉白玉缓坡长阶：在最平实质朴、温润如玉的散文步道上，不费力气地拾级而上，最终在云端俯瞰到莎士比亚那座金碧辉煌的诗神之城。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个想读莎士比亚却被古英语和剧本格式劝退的初学者，以及渴望给孩子提供最纯正、最具文学营养经典启蒙读物的智慧父母。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>原著剧本深奥晦涩的语言阅读门槛 vs 普通读者尤其是青少年对崇高故事与生动人性的天然精神渴望。</strong></p>

      <div class="sub-heading">经典故事改编的三大炼金术步骤</div>
      <ol class="num-list">
        <li><strong>第一步 · 骨架提纯（Distillation）：</strong>剔除所有与核心矛盾无关的次要副线与粗俗市井段子，将戏剧行动线紧紧锁定在主人公的道德考验上。</li>
        <li><strong>第二步 · 对白散文化（Narrativization）：</strong>将原本属于演员声嘶力竭的独白，巧妙化解为第三人称充满关切的深情叙述，点明人物深层的心理动机。</li>
        <li><strong>第三步 · 诗意金句镀金（Preservation）：</strong>在故事的关键转折处，一字不差地保留莎翁最震撼人心的传世原著诗句（如‘生存还是毁灭’、‘慈悲如甘霖降下’），让读者品尝到最原汁原味的原典神髓。</li>
      </ol>"""

    sec05 = """      <div class="sub-heading">兰姆姐弟的苦难与救赎：文字背后的圣洁亲情</div>
      <p>《莎士比亚故事集》背后藏着英国文学史上最凄美的一段真实亲情：姐姐玛丽·兰姆患有严重的家族遗传性精神疾患，在一次发病狂乱中曾失手刺死亲生母亲；弟弟查尔斯·兰姆当时二十出头，为了保护姐姐免于被终身关进疯人院，毅然在法官面前发下一生不婚的重誓，用毕生精力监护、陪伴姐姐。当玛丽神志清醒时，姐弟俩围坐在一张桌子前，查尔斯写悲剧，玛丽写喜剧。每当玛丽感到自己即将发病时，她会平静地收拾好包裹，与泪流满面的弟弟携手步行走向郊外的疗养院。这本给全世界孩子带来欢笑与泪水的童话集，正是浸泡在这对伟大姐弟最深沉的苦难与无私大爱中写就的。</p>"""

    sec06 = """      <div class="sub-heading">十九世纪英国散文黄金时代的典范笔致</div>
      <p>查尔斯·兰姆是英国浪漫主义散文的无冕之王。在本书中，他的笔触<strong>洗练、雅致、温厚、毫不装腔作势</strong>。他完全继承了莎士比亚对平民大众深切的同情心，用最纯正的伊丽莎白语汇滋养读者的语感，被公认为学习经典现代英语写作的最佳范本。</p>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（经典戏剧故事改编）：</strong>莎士比亚二十部经典名剧由舞台台词向生动优美散文小说转化的故事汇编。<br>
        <strong>深层架构（经典大众化的创造性传承）：</strong>文化遗产如何在不降低思想深度前提下打破阶层壁垒、实现普及启蒙的范式工程。<br>
        <strong>根本架构（人道主义精神启蒙）：</strong>通过二十个关于爱、背叛、宽恕与牺牲的故事，在幼小心灵深处建立起抵御人世一切恶毒与平庸的最高精神免疫力。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>英国文学史家将其赞誉为‘世界上最完美的二手创作’。它不仅没有贬低莎士比亚，反而在两百年间将数以亿计原本可能一生与戏剧无缘的普通读者，稳稳引渡到了原典的宽阔海洋之中。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天我们在文化普及中常常陷入两个极端：要么高高在上故作高深搞得大众望而却步，要么为了所谓‘迎合年轻人口味’大搞低俗化、恶搞化与魔改。《莎士比亚故事集》给现代文化传播树立了不朽的典范：<strong>真正的普及，不是把经典拉下神坛迎合平庸，而是用最深情、最清澈的语言，把大众的手稳稳托举到经典面前</strong>。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《莎士比亚故事集》是读懂莎翁最好的敲门砖。一对伟大的英国散文家姐弟，把莎翁最难懂的二十部大戏，改写成了全世界孩子都能读懂的优美睡前故事，金句全在，情节全通。它告诉你：最伟大的经典不是死在博物馆里，而是活在千家万户读者的枕边。”</p>"""

    sec11 = """      <div class="sub-heading">最小通达路径：故事集中必读三大名篇</div>
      <ul class="bullet-list">
        <li><strong>必读第一篇 · 《暴风雨》：</strong>体会玛丽·兰姆如何用最温柔的神笔开启全剧大门。</li>
        <li><strong>必读第二篇 · 《威尼斯商人》：</strong>精读法庭一磅肉辩论在散文笔触下的紧凑张力。</li>
        <li><strong>必读第三篇 · 《李尔王》：</strong>精读查尔斯·兰姆在暴风雨荒原上的雄浑散文挽歌。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 改编与原作的关系：</strong>读完兰姆的故事集，是否就等于读懂了莎士比亚？它在什么维度上替代不了原著剧本的现场观演体验？
      </div>
      <div class="card-box">
        <strong>Q2 · 悲喜分工背后的隐喻：</strong>姐姐玛丽一生受尽疯癫折磨却写出了全书最明媚的喜剧，弟弟查尔斯一生照顾姐姐却写下了最深沉的悲剧，这种互补给我们的心灵修养带来怎样的震颤？
      </div>"""

    sec13 = """      <div class="sub-heading">① 经典知识转化实践工具：“兰姆故事改写三步法” (The Lamb Story-Bridge Protocol)</div>
      <p><strong>适用场景：</strong>当你需要向外行、孩子或非专业客户讲解某项极其复杂高深的技术理论或经典模型时。<br>
      <strong>第一步（找戏剧核心）：</strong>剔除所有复杂的数学公式或技术术语，找出这项理论背后最核心的‘那个人类冲突矛盾’；<br>
      <strong>第二步（用家常比喻还原）：</strong>用听众最熟悉的日常物品（如壁炉、雨伞、面包）替换抽象概念；<br>
      <strong>第三步（保留一个原典金句）：</strong>在结尾处完整亮出一句原汁原味的权威定义，让听众在听懂故事的同时体会到对知识的敬畏。</p>"""

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

print("Round 14 deep Tales from Shakespeare ready.")

def get_deep_classical_drama():
    data = {
        "title_cn": "西方古典戏剧故事选",
        "title_en": "Stories from Classical Drama",
        "author_cn": "古典戏剧编委会",
        "author_en": "Classical Drama Collection",
        "sub_desc": "从古希腊悲剧到近代名剧 · 人类戏剧精神的源头活水与净化洗礼史诗",
        "hero_quote": "戏剧是把人类最逼仄的道德困境置于命运放大镜下；让我们在剧场的泪水与震撼中清洗灵魂的尘埃，重获清明与崇高。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">编选体系</div><div class="spec-val">西方戏剧正典精粹汇编</div></div>
        <div class="spec-item"><div class="spec-label">坐标跨度</div><div class="spec-val">索福克勒斯 / 欧里庇得斯 / 莫里哀 / 易卜生等</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">古典悲喜剧故事选 / 戏剧形式批评读本</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">跨越两千五百年戏剧演进史</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身通识必读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">命运冲突模型与亚里士多德卡塔西斯（净化）深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把古典戏剧故事当成看‘最后好人胜出还是坏人伏诛’的肥皂剧。戏剧的真正灵魂在于黑格尔所言的<strong>“两种正义的不可调和之撞击”</strong>——在《安提戈涅》中，安提戈涅要遵循神圣的天理人伦埋葬亲生兄长，而国王克瑞翁要捍卫城邦国家的成文法纪维护秩序，双方都在践行内心的正义，撞击在一起便爆发出了撕裂宇宙的万古悲剧。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 古希腊‘命运悲剧’向近代‘性格悲剧’与‘社会问题剧’的演进脉络：</strong>从索福克勒斯《俄狄浦斯王》中人无论多么竭力逃避依然不可抗拒地走向神谕弑父娶母的残酷宿命；到莎士比亚写由于人性自身的性格弱点（哈姆雷特的迟疑、奥赛罗的嫉妒）引发的内耗毁灭；再到近代易卜生《玩偶之家》中娜拉摔门而出向封建夫权社会发起的制度宣战。一部大书看尽人类自我意识觉醒的两千五百年。
      </div>
      <div class="card-box">
        <strong>② 亚里士多德《诗学》‘卡塔西斯（Catharsis 精神净化）’的核心机制：</strong>悲剧之所以能带给人至高的崇高美感，是因为它在两小时内将一个原本伟大善良的英雄推向毁灭（悲剧过失 Hamartia），唤起观众内心深处极度的‘恐惧与怜悯’。观众走出剧场时，灵魂在泪水中完成了对自身狂妄与私欲的彻底清洗。
      </div>
      <div class="card-box">
        <strong>③ 戏剧‘突转（Peripeteia）与发现（Anagnorisis）’的极致结构美学：</strong>分析古典戏剧如何通过一封信、一个胎记、一句真相的揭发，在刹那间将原告变为被告、将胜利者打落深渊。结构之精密，构成了全人类叙事艺术的源头法宝。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        从雅典卫城酒神剧场万民同哭同笑的城邦公民教育，到十七世纪法兰西古典主义三一律殿堂，再到十九世纪欧洲市民剧场，戏剧始终是文明反躬自省的最高公器。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .cd-box { rx: 8; stroke-width: 1.5; }
            .cd-bg-fate { fill: #1d3557; stroke: #2a4d7a; }
            .cd-bg-char { fill: #8c2d19; stroke: #a33b24; }
            .cd-bg-soc { fill: #2a9d8f; stroke: #40916c; }
            .cd-bg-core { fill: #fbf9f4; stroke: #1c221e; stroke-width: 2.2; }
            .cd-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .cd-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .cd-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .cd-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .cd-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .cd-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="cd-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 核心枢纽：戏剧两难境地与卡塔西斯 -->
          <rect x="230" y="25" width="220" height="90" class="cd-box cd-bg-core" />
          <text x="340" y="52" class="cd-t-d">戏剧冲突核心：两难死锁</text>
          <text x="340" y="72" class="cd-t-sub">两种正义的不可调和碰撞</text>
          <text x="340" y="90" class="cd-t-sub">怜悯与恐惧 → 灵魂净化 (Catharsis)</text>
          <text x="340" y="104" style="fill:#8c2d19; font-size:10px; font-weight:700; text-anchor:middle;">“在苦难中照亮人性的尊严”</text>

          <!-- 三大演进维度 -->
          <path d="M 230 70 L 125 150" class="cd-solid" stroke="#1d3557" marker-end="url(#cd-arr)" />
          <path d="M 340 115 L 340 150" class="cd-solid" stroke="#8c2d19" marker-end="url(#cd-arr)" />
          <path d="M 450 70 L 555 150" class="cd-solid" stroke="#2a9d8f" marker-end="url(#cd-arr)" />

          <!-- 阶段一：古希腊命运悲剧 -->
          <rect x="15" y="150" width="200" height="150" class="cd-box cd-bg-fate" />
          <text x="115" y="178" class="cd-t-w">① 古希腊：命运悲剧</text>
          <text x="115" y="200" class="cd-t-sub-w">神谕预言 · 不可抗力</text>
          <text x="115" y="220" class="cd-t-sub-w">《俄狄浦斯王》刺瞎双目</text>
          <text x="115" y="240" class="cd-t-sub-w">《安提戈涅》良心葬兄抗王法</text>
          <text x="115" y="260" class="cd-t-sub-w">虽败犹荣的凡人傲骨</text>
          <text x="115" y="280" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">“向神明证明人性的尊严”</text>

          <!-- 阶段二：文艺复兴性格悲剧 -->
          <rect x="240" y="150" width="200" height="150" class="cd-box cd-bg-char" />
          <text x="340" y="178" class="cd-t-w">② 近代：性格悲剧</text>
          <text x="340" y="200" class="cd-t-sub-w">欲望觉醒 · 自我搏斗</text>
          <text x="340" y="220" class="cd-t-sub-w">莎士比亚四大悲剧巅峰</text>
          <text x="340" y="240" class="cd-t-sub-w">麦克白野心 · 浮士德卖魂</text>
          <text x="340" y="260" class="cd-t-sub-w">性格即命运的深刻解剖</text>
          <text x="340" y="280" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">“内心的魔鬼才是终极对手”</text>

          <!-- 阶段三：近现代社会问题剧 -->
          <rect x="465" y="150" width="200" height="150" class="cd-box cd-bg-soc" />
          <text x="565" y="178" class="cd-t-w">③ 现代：社会与存在剧</text>
          <text x="565" y="200" class="cd-t-sub-w">制度锁链 · 平庸之恶</text>
          <text x="565" y="220" class="cd-t-sub-w">易卜生《玩偶之家》摔门出走</text>
          <text x="565" y="240" class="cd-t-sub-w">契诃夫《樱桃园》时代落幕</text>
          <text x="565" y="260" class="cd-t-sub-w">贝克特《等待戈多》荒诞虚无</text>
          <text x="565" y="280" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">“向整个伪善体制发起宣战”</text>
        </svg>
      </div>

      <div class="sub-heading">经典名篇流派与思想原型谱系</div>
      <ul class="bullet-list">
        <li><strong>《俄狄浦斯王》（索福克勒斯）：</strong>全人类悲剧的‘黄金标杆’。底比斯国王俄狄浦斯为了拯救城邦瘟疫全力追查杀害先王的凶手，在剥茧抽丝的严密推理中惊骇发现自己正是那个在十字路口无意杀父、随后迎娶亲生母亲的弑父娶母凶手！他没有逃避责任，为了履行对城邦的诅咒，当众用黄金别针刺瞎自己的双眼，自我放逐步入荒原。这种面对命运残酷真相时的极端诚实，成就了人类精神的千古绝唱。</li>
        <li><strong>《浮士德》（歌德）：</strong>两百年铸就的欧洲精神史诗。老学者浮士德学富五车却深感人生空虚，与魔鬼靡菲斯特立下赌约——只要魔鬼能让他在人世间体验到真正的满足，令他脱口喊出‘停留一下吧，你多么美丽！’，他的灵魂就归魔鬼所有。浮士德经历了书斋、情欲、政治、古希腊古典美学的万千洗礼，最终在开垦围海造田造福万民的大劳动中顿悟而死，灵魂在天使的歌声中升华。</li>
        <li><strong>《玩偶之家》（易卜生）：</strong>现代女性主义与社会问题剧的开山大炮。贤妻良母娜拉为了挽救丈夫海尔茂的性命伪造签名借款治病，在东窗事发后，她震惊地发现丈夫为了维护行长名誉对自己破口大骂，危机解除后又变回逗弄金丝雀的虚伪面具。娜拉在子夜愤然换上常服，摔门而出，那一记关门的巨响，宣告了现代独立人格对父权傀儡家庭的彻底决裂。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书收录了西方两千五百年来最具有震撼力的十余部经典戏剧故事。从古希腊神话时期为民盗火被锁在高加索悬崖日夜受神鹰啄食内脏的《被缚的普罗米修斯》；为了给战死叛国的亲兄长入土安葬而不惜违抗国王死刑号令的《安提戈涅》；逃避神谕却在命中注定的三岔路口误杀亲父、自刺双目的《俄狄浦斯王》；到法兰西古典主义莫里哀笔下揭穿宗教伪善骗局的《伪君子》、死守钱箱甚至把儿子当做金钱筹码的《悭吝人》；再到德意志狂飙突进时期席勒笔下反抗封建专制的《阴谋与爱情》、歌德耗尽毕生心血追索人生终极价值的《浮士德》；直至近代易卜生让妻子摔碎虚伪鸟笼出走的《玩偶之家》、契诃夫记录老贵族文明在斧砍声中烟消云散的《樱桃园》。每一个故事都是一次高浓度的生命情境逼定，将凡人逼进无路可退的悬崖，直面灵魂最残酷的抉择。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类在肉体有限、命运无常、体制压迫的绝对局限面前，如何凭借崇高的道德自决与精神反抗，确证自由意志的存在”</strong>。全书证明：戏剧从来不是为了逗乐消遣，它是文明最深沉的一面透镜，逼迫我们在流泪与惊骇中反思自身的傲慢与偏狭。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一座横跨两千年的巨型多宝阁：在古希腊岩石剧场的万民号哭与近代客厅关门的巨响交织中，见证人类灵魂如何在一次次撞得粉身碎骨的绝境中，淬炼出不可屈服的文明火种。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个渴望全面把握西方戏剧文学演进史、探究叙事结构动力学与矛盾冲突模型，提升哲学思辨深度的高阶读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>不可抗力的神圣宿命与制度铁律 vs 人类微小肉身深处不可剥夺的良知反抗与自决尊严。</strong></p>

      <div class="sub-heading">全书戏剧美学三大演进阶梯</div>
      <ol class="num-list">
        <li><strong>第一阶梯 · 古希腊神话本体论（神 vs 人）：</strong>人在不可理解的宇宙宿命面前的知情决斗。重点精读《俄狄浦斯王》严丝合缝如现代侦探小说般自查自判的结构奇迹。</li>
        <li><strong>第二阶梯 · 文艺复兴与古典主义道德论（欲望 vs 理性）：</strong>人如何面对自身的虚荣与贪婪。重点精读《伪君子》中骗子达尔丢夫在餐桌下的露馅与《浮士德》的永恒追求。</li>
        <li><strong>第三阶梯 · 近现代社会制度论（体制 vs 个体自由）：</strong>人如何挣脱伪善家庭与资产阶级社会的大网。重点精读《玩偶之家》娜拉认清‘丈夫只把自己当宠物’后的决绝觉醒。</li>
      </ol>"""

    sec05 = """      <div class="sub-heading">俄狄浦斯的伟大：不是悲剧的受害者，而是真理的殉道者</div>
      <p>许多浅显读者认为《俄狄浦斯王》是一个荒唐的巧合故事。然而亚里士多德将其奉为‘无可逾越的第一神作’。俄狄浦斯完全可以在查案中适可而止——当老盲人先知警告他‘凶手就是你自己’、当王后伊俄卡斯忒痛哭哀求他‘别再查下去了，求你为了活命停手吧’，俄狄浦斯只要装聋作哑，他依然能继续当他万人膜拜的底比斯国王！但他发出了全人类历史上最震撼的誓言：‘不管我的身世多么卑微可怖，我也必须追查到底！’正是这种<strong>哪怕粉身碎骨也绝不向自欺妥协的求真意志</strong>，将一个乱伦弑父的罪犯，升华为了全人类勇气的至尊图腾。</p>"""

    sec06 = """      <div class="sub-heading">合唱队（Chorus）与独白（Monologue）的形式美学</div>
      <p>古典戏剧开创了世界文学最成熟的复调形式系统：台上的主角在狂怒中冲锋，台下的合唱队则以庄严的诗句代表城邦老者与旁观大众，唱出对命运的敬畏与对暴虐的警示。它时刻提醒读者：<strong>我们既是舞台上痛苦受难的那个具体人，也是在台下冷眼观照人世的理智神明</strong>。</p>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（经典戏剧故事萃取）：</strong>西方古希腊、文艺复兴、古典主义与近现代十余部传世名剧的核心故事与人物冲突汇编。<br>
        <strong>深层架构（戏剧形式与叙事动力学演进）：</strong>对三一律、卡塔西斯、突转与发现等核心戏剧法则的全面实操解剖。揭示伟大戏剧如何通过极致的逼仄情境挤压出人性的全部真伪。<br>
        <strong>根本架构（人道主义精神自愈）：</strong>在直面人世不可避免的苦难与死亡时，人类通过戏剧艺术完成集体的精神疗愈与道德升华。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>亚里士多德在《诗学》第六章留下了关于悲剧的永恒定义：“悲剧是对一个严肃、完整、有一定长度的行动的摹仿；通过引发怜悯与恐惧，来使这种情感得到净化（Catharsis）。”这本故事集就是这套净化法则在两千五百年世界文学长河中的完美演练场。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>现代社会的人们习惯了在短视频与肥皂剧的‘即时爽感’中麻痹自己，越来越丧失了直面深刻冲突与复杂道德困境的能力。《戏剧故事》带我们重回严肃的精神战场：生活充满了无法两全其美的两难，唯有敢于直面悲剧的深度，一个人才能建立起坚固的人格内核，不至于在生活的第一记耳光面前粉身碎骨。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《戏剧故事》是西方两千五百年好戏的终极精选。从古希腊为了真理自挖双眼的俄狄浦斯王，到跟魔鬼打赌游历人间的浮士德，再到砸碎家庭锁链出走的娜拉。它告诉你：好戏从来不是看热闹，而是把人逼进死角，看灵魂如何在绝境中站成一座英雄的雕像。”</p>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界戏剧正典必读三大里程碑</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 《俄狄浦斯王》终盘真相大白：</strong>精读牧羊人吐露身世、国王自刺双目的惊惊悚崇高顶峰。</li>
        <li><strong>必读第二场 · 《浮士德》盲目掘土顿悟：</strong>精读浮士德在盲目中听闻铲土声喊出‘停留一下吧你多么美丽’的世纪灵魂决斗。</li>
        <li><strong>必读第三场 · 《玩偶之家》深夜摔门出走：</strong>精读娜拉向丈夫清算八年玩偶婚姻、决绝摔上大门的现代女性觉醒时刻。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 悲剧为何比喜剧更具永恒震撼力？</strong>为什么人类文明记忆中流传最久、最震撼灵魂的作品，绝大部分都是让人痛哭沉思的悲剧？
      </div>
      <div class="card-box">
        <strong>Q2 · 安提戈涅的法理困境：</strong>当国家法律与内心的道德良知发生不可调和的冲突时，公民的服从义务应当退守到何处？
      </div>"""

    sec13 = """      <div class="sub-heading">① 决策模拟工具：“戏剧两难压力测试” (The Dramatic Dilemma Matrix)</div>
      <p><strong>适用场景：</strong>在团队管理或个人生活中遭遇‘无论怎么选都有重大代价’的死局时。<br>
      <strong>第一步（列出两端正义）：</strong>像黑格尔解剖悲剧一样，写出对立双方各自依据的‘正当原则’是什么；<br>
      <strong>第二步（剔除自私借口）：</strong>看清矛盾的本质不是善与恶的交锋，而是两种不同维度的善在资源有限下的争夺；<br>
      <strong>第三步（像俄狄浦斯一样承担代价）：</strong>不逃避、不推诿，做出决定并勇敢准备好支付该决定所必须付出的全部真实代价。</p>"""

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

def main():
    print("=== 开始批量写入第 14 轮（莎士比亚十四行诗、莎士比亚故事集、戏剧故事） ===")
    plan = [
        ("莎士比亚十四行诗", get_deep_sonnets),
        ("莎士比亚故事集", get_deep_tales_from_shakespeare),
        ("戏剧故事", get_deep_classical_drama),
    ]
    for bname, getter in plan:
        target_dir = os.path.join(BASE_DIR, bname)
        if not os.path.exists(target_dir):
            print(f"[ERROR] 目录不存在: {target_dir}")
            continue
        html = getter()
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        cn = len([c for c in text if "一" <= c <= "鿿"])
        secs = len(soup.find_all("details", class_="guide-section"))
        svgs = len(soup.find_all("svg"))
        assert secs == 13, f"{bname} 栏目数异常: {secs}"
        assert svgs >= 1, f"{bname} 缺少 SVG"
        with open(os.path.join(target_dir, "guide.html"), "w", encoding="utf-8") as f:
            f.write(html)
        with open(os.path.join(target_dir, "guide.index"), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] {bname} -> guide.html ({len(html)} 字节, 纯中文 {cn} 字, 13 栏目全绿, SVG 成功)")

if __name__ == "__main__":
    main()
