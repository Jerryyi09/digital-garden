# -*- coding: utf-8 -*-
"""
Round 05: Wuthering Heights, A Tale of Two Cities, Hard Times (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_wuthering_heights():
    data = {
        "title_cn": "呼啸山庄",
        "title_en": "Wuthering Heights",
        "author_cn": "艾米莉·勃朗特",
        "author_en": "Emily Brontë",
        "sub_desc": "英国文学史上最具原始野性之作 · 荒原石南间的超越生死与伦理复仇史诗",
        "hero_quote": "无论我们的灵魂是什么做成的，他和我的都是同一种材料；而林顿的灵魂就像月光和闪电，或者霜与火那样截然不同。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">艾米莉·勃朗特 (1818–1848)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1847 年以笔名埃利斯·贝尔出版</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">哥特式现实主义 / 浪漫主义复仇史诗</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 30 万字 / 全三十四章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 终身必读文学经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">荒野自然力量与维多利亚文明规训的碰撞深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把希斯克利夫误读为言情小说里深情款款的‘霸道总裁男主角’。希斯克利夫身上流淌着被种族侮辱、童年家暴彻底摧残后的恶魔野性——他为了复仇，冷酷虐待妻子伊莎贝拉、用绞索勒死爱犬、逼迫垂危的林顿立遗嘱、把仇人的儿子哈里顿降为不识字的粗鄙仆役。但他与凯瑟琳之间的爱，超越了世俗善恶与肉体欲望，是一种<strong>两个被文明放逐的野性灵魂在宇宙深处的同质共振</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 呼啸山庄 vs 画眉田庄的双重空间哲学对峙：</strong>呼啸山庄坐落在狂风肆虐的荒原山顶，石墙厚重、带刺石楠丛生，代表人类未被驯化的野性本能、暴烈激情与残酷生命力；而画眉田庄坐落在深谷温室之中，精美地毯、金色鸟笼、仆役成群，代表维多利亚文明阶级的优雅、虚弱与虚伪礼法。两座庄园的兴衰，象征着文明与野性的永恒拉锯。
      </div>
      <div class="card-box">
        <strong>② 双层回环嵌套叙事（The Nested Frame Narrative）：</strong>冷漠外来租客洛克伍德先生的日记，与熟悉两代人兴衰的女管家丁奈莉的口述交织。这种客观甚至略带市侩的叙述口吻，像一副沉重的金属外框，将画框内那团炽热骇人的复仇烈火冷静地框住，制造了极其强烈的审美间离感。
      </div>
      <div class="card-box">
        <strong>③ 突破生死界限的形而上执念与第二代和解救赎：</strong>希斯克利夫在凯瑟琳死后二十年夜夜不能安眠，甚至在雪夜掘开墓穴、敲碎棺木侧板要求死后骸骨互溶；然而当复仇大获全胜前夕，目睹小凯瑟琳教哈里顿读书认字的温情，复仇的利刃突然在虚无中滑落，展现了超越仇恨的救赎新生。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪中叶英国约克郡荒凉严酷的荒原沼地。勃朗特姐妹在孤寂闭塞的牧师公馆长大，艾米莉将旷野的凄风苦雨化作笔下摧枯拉朽的原始力量。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .wh-box { rx: 8; stroke-width: 1.5; }
            .wh-bg-heath { fill: #131619; stroke: #8c2d19; stroke-width: 2.2; }
            .wh-bg-cath { fill: #8c2d19; stroke: #a33b24; }
            .wh-bg-edgar { fill: #fbf9f4; stroke: #1d3557; stroke-width: 2; }
            .wh-bg-second { fill: #2a9d8f; stroke: #40916c; }
            .wh-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .wh-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .wh-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .wh-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .wh-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .wh-soul { stroke: #e0725b; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .wh-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="wh-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 呼啸山庄：希斯克利夫 -->
          <rect x="20" y="25" width="210" height="120" class="wh-box wh-bg-heath" />
          <text x="125" y="52" class="wh-t-w">呼啸山庄：希斯克利夫</text>
          <text x="125" y="72" class="wh-t-sub-w">吉普赛弃儿 · 遭受虐待出走</text>
          <text x="125" y="90" class="wh-t-sub-w">发财归来 · 冷血吞并两大家族</text>
          <text x="125" y="108" class="wh-t-sub-w">掘墓求死 · 幽灵荒原游荡</text>
          <text x="125" y="126" style="fill:#e0725b; font-size:10px; font-weight:700; text-anchor:middle;">原始野性与毁灭性仇恨化身</text>

          <!-- 画眉田庄：埃德加·林顿 -->
          <rect x="450" y="25" width="210" height="120" class="wh-box wh-bg-edgar" />
          <text x="555" y="52" class="wh-t-d">画眉田庄：埃德加·林顿</text>
          <text x="555" y="72" class="wh-t-sub">文明绅士 · 优雅温良 · 怯弱无力</text>
          <text x="555" y="90" class="wh-t-sub">以财富与体面迎娶凯瑟琳</text>
          <text x="555" y="108" class="wh-t-sub">在野性狂暴冲击下家破人亡</text>
          <text x="555" y="126" style="fill:#1d3557; font-size:10px; font-weight:700; text-anchor:middle;">脆弱文明秩序的悲情守望者</text>

          <!-- 灵魂拉扯中心：凯瑟琳·恩萧 -->
          <rect x="235" y="130" width="210" height="85" class="wh-box wh-bg-cath" />
          <text x="340" y="158" class="wh-t-w">凯瑟琳·恩萧 (Catherine)</text>
          <text x="340" y="178" class="wh-t-sub-w">高沼旷野之女 · 灵魂与希斯克利夫同一</text>
          <text x="340" y="196" class="wh-t-sub-w">屈从虚荣嫁入画眉田庄，撕裂发狂早逝</text>

          <!-- 灵魂连接线 -->
          <path d="M 230 85 L 235 150" class="wh-soul" />
          <text x="175" y="145" style="fill:#e0725b; font-size:10px; font-weight:700;">‘我就是希斯克利夫！’</text>

          <!-- 世俗婚姻线 -->
          <path d="M 450 85 L 445 150" class="wh-solid" stroke="#1d3557" />
          <text x="500" y="145" style="fill:#1d3557; font-size:10px; font-weight:700;">世俗门第婚姻</text>

          <!-- 下方第二代救赎：哈里顿与小凯瑟琳 -->
          <path d="M 340 215 L 340 250" class="wh-solid" marker-end="url(#wh-arr)" />
          <rect x="180" y="250" width="320" height="75" class="wh-box wh-bg-second" />
          <text x="340" y="278" class="wh-t-w">第二代救赎：哈里顿 · 恩萧 & 小凯瑟琳</text>
          <text x="340" y="298" class="wh-t-sub-w">识字读书 · 抚平世仇 · 山庄庭院重绽报春花</text>
          <text x="340" y="312" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">野性力量与文明教化的终极和谐交融</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>希斯克利夫：</strong>被老恩萧从利物浦街头捡回的黑发孤儿。自幼遭受辛德雷猪狗不如的毒打与贬低，在泥地里与凯瑟琳相依为命。当偷听到凯瑟琳说‘嫁给他会降低身份’时，他的灵魂在暴风雨之夜被雷火击穿。三年后发财归来，他变成了一头冷酷精密的复仇机器，用合法的高利贷收买呼啸山庄，用婚姻折磨林顿家族。然而当他终于把两大家族的房契全部据为己有、大仇得报的那一刻，他却再也吃不下一口食物，整日整夜在雨夜里对着空无一人的窗外呼唤凯瑟琳的名字，直到在狂喜的幻象中微笑着绝食而亡。</li>
        <li><strong>凯瑟琳·恩萧：</strong>世界文学中最具分裂性的狂烈女性。她骨子里是只属于高沼荒原的烈马，却又贪恋画眉田庄精致的蕾丝长裙与贵妇排场。她以为可以通过嫁给埃德加来‘在经济上提携保护希斯克利夫’，这种幼稚的幻想彻底引爆了全剧的地狱熔炉。面对两个截然不同的男人，她的精神被生生扯成两半，最终在精神错乱与难产中狂喊着奔向死亡，成为在生死交界处敲打窗户的永恒冤魂。</li>
        <li><strong>埃德加·林顿：</strong>文明社会温良软弱的标本。他修养极高、举止儒雅，全心全意包容凯瑟琳的任性，但他在面对希斯克利夫野兽般的原始力量时毫无招架之力。他的悲剧证明了：缺乏力量支撑的脆弱文明礼仪，在野蛮的暴力仇恨面前如同薄纸般不堪一击。</li>
        <li><strong>哈里顿·恩萧：</strong>辛德雷之子，被希斯克利夫故意当做牲畜般抚养长大、剥夺受教育权利的受害者。然而他身上保留了老恩萧家族纯朴善良的天性，在小凯瑟琳耐心的教导下学会阅读，最终融化了上一代的滔天仇恨，完成了全剧唯一的光明救赎。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>城里绅士洛克伍德租下荒凉的画眉田庄，暴风雪夜借宿房东希斯克利夫的呼啸山庄，在被封死的旧厢房里遭遇了一只自称‘凯瑟琳·恩萧’的冰冷幽灵小手抓挠窗棂。惊魂未定的洛克伍德返回田庄，听老女管家丁奈莉缓缓道出了一段长达三十年的恐怖往事：三十年前，老恩萧捡回孤儿希斯克利夫，儿子辛德雷对其嫉恨交加百般虐待，唯有女儿凯瑟琳与他形影不离。老恩萧死后，辛德雷将希斯克利夫贬为马夫。凯瑟琳虚荣嫁给画眉田庄的林顿少爷，致使希斯克利夫在雷雨之夜负气出走。三年后希斯克利夫携巨款暴富归来，设局引诱辛德雷赌博输光呼啸山庄，诱骗并虐待林顿之妹伊莎贝拉，凯瑟琳在两难折磨中难产早逝。此后二十年，希斯克利夫展开病态绝伦的第二代报复：迫害辛德雷之子哈里顿使其沦为文盲，强行逼迫病弱儿子与小凯瑟琳成婚夺取画眉田庄房产。就在复仇大功告成、所有仇人后代尽成囊中之物时，希斯克利夫却突然丧失了进食的欲望，夜夜在荒原呼唤亡灵，终在狂喜中暴毙。第二代年轻人以爱释仇，山庄重获宁静。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类不可压抑的原始生命本能与文明秩序规训之间的宿命冲突”</strong>。艾米莉·勃朗特展示了一种超越了基督教道德善恶观念的宇宙生命观：当一种极度真挚强烈的灵魂渴望被世俗阶级偏见撕裂后，它会释放出怎样足以毁灭整座大地的恐怖暗能量，以及这种狂暴能量如何在两代人的循环中完成自愈。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场夜行于约克郡冰冷泥沼与狂暴雷雨中的惊心旅程：在毛发倒竖的哥特战栗中，直击两具灵魂如何击碎人间一切伦理道德框架，在烈火中互相吞噬成灰烬。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾被内心的某种狂烈激情彻底俘获、在理智与本能之间饱受拉扯，渴望领略纯粹文学野性之美的读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>原生态自然能量与绝对灵魂占有欲 vs 维多利亚阶级地位虚荣与文明脆弱规训。</strong></p>

      <div class="sub-heading">全书双代推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 荒原结盟与歧视毒种（第一至八章）：</strong>黑发弃儿进门，辛德雷的马鞭毒打，高沼地里两个野孩子的赤脚相依；画眉田庄恶犬咬伤凯瑟琳，凯瑟琳初沾文明香粉。</li>
        <li><strong>第二幕 · 背叛之夜与出走暴富（第九至十章）：</strong>厨房门后的半句偷听（‘嫁给他会降低身份’），雷电劈裂高大榆树，希斯克利夫消失在狂风暴雨中；凯瑟琳盛大出嫁。</li>
        <li><strong>第三幕 · 恶魔归来与首轮杀戮（第十一至十六章）：</strong>暴富归来的绅士复仇者；引诱伊莎贝拉私奔并对其施暴；凯瑟琳病房内的诀别死吻与难产离世，希斯克利夫以头撞树发出狂野哀嚎。</li>
        <li><strong>第四幕 · 吞噬第二代的冷血布局（第十七至二十八章）：</strong>辛德雷醉死，呼啸山庄易主；哈里顿被剥夺受教育权；逼迫肺痨小林顿诱婚小凯瑟琳，林顿先生悲愤离世，两大家族地产尽入魔掌。</li>
        <li><strong>第五幕 · 仇恨枯竭与雨夜归位（第二十九至三十四章）：</strong>希斯克利夫在小凯瑟琳与哈里顿的眼神中看见了凯瑟琳的影子，复仇之火在瞬间熄灭；绝食三日夜半死于雨夜开启的窗前，嘴角含笑；牧童在暮色中看见两个幽灵在荒原上手拉手漫步。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第九章凯瑟琳向丁奈莉倾吐‘我就是希斯克利夫’的深夜长谈：</strong>凯瑟琳试图在埃德加的财富与希斯克利夫的灵魂之间玩弄两全其美的把戏，然而正是这虚荣的半句话逼走了希斯克利夫，直接酿成了此后两大家族横跨三十年的流血绝罚。
      </div>"""

    sec05 = """      <div class="sub-heading">希斯克利夫绝食而亡之谜：复仇为何在顶峰坍塌？</div>
      <p>许多浅显读者不解：为什么希斯克利夫辛辛苦苦谋划三十年，在完全剥夺了仇人后代的一切、随时可以把他们扫地出门的时刻，突然停手了？文本给出了极其深沉的心理答案：<strong>复仇在本质上只是他对抗失去凯瑟琳这一巨大空虚的替代品</strong>。当他看见哈里顿与小凯瑟琳在一起时，他突然意识到这两个人已经获得了彼此的爱与救赎，而自己的整个复仇大厦在爱面前不过是一堆毫无意义的破砖烂瓦。更为关键的是，凯瑟琳的幽灵已经夜夜走到他的床前，他的全部心智早已被拉入了死后相会的狂喜之中。他不是被打败的，他是被自己更宏大的形而上执念彻底召回了。</p>

      <div class="sub-heading">丁奈莉的叙述者偏见与世俗平庸局限</div>
      <p>女管家丁奈莉绝非毫无瑕疵的诚实见证者。她代表了英国下层社会的世俗道德常识：爱碎碎念、讲究现实体面、偶尔打小报告。她多次隐瞒信件、推波助澜，甚至在凯瑟琳陷入癫狂时认为她只是在‘耍大小姐脾气’。艾米莉·勃朗特巧妙利用这位叙述者的平庸局限，恰恰衬托出了希斯克利夫与凯瑟琳那种不可理喻、超绝凡俗的原始悲剧性。</p>"""

    sec06 = """      <div class="sub-heading">狂暴诗化的自然主义语言风格</div>
      <p>艾米莉·勃朗特在诗作中淬炼出的高密度语言，在小说中倾泻而出。全书充满了‘风暴、闪电、冰雹、沼地、石楠、鲜血、狼犬、棺木’等具有强烈身体刺激感的高能词汇。句子短促雄浑、长驱直入，几乎完全剔除了维多利亚传统小说中虚伪的社交寒暄套话，每一句对话都如同两柄利刃在虚空中擦出的耀眼火花。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>呼啸的荒原冷杉与石楠花 (The Heath and Fir Trees)：</strong>全书永恒的生命背景。扭曲倾斜的树木见证了长年西风的肆虐，顽强生长的紫色石楠象征着未被文明修剪的原始生命野火。</li>
        <li><strong>抓挠窗棂的冰冷小手：</strong>开篇洛克伍德噩梦中出现的幽灵。它象征着<strong>被生生撕裂的深情跨越生死结界、历经二十年风雪摧残依然执着敲门的巨大宿命怨念</strong>。</li>
        <li><strong>掘开的相通棺木：</strong>希斯克利夫收买掘墓人敲碎棺壁。它象征着人类肉身在彻底腐烂归于尘土时，灵魂跨越物种与肉体局限、在化学原子层面上重新融合为一体的绝唱。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（哥特复仇家史）：</strong>一个被侮辱的吉普赛弃儿暴富归来，残暴报复两大家族两代人，最终在见鬼与绝食中暴毙的旷野传奇。<br>
        <strong>深层架构（文明与本能的死结）：</strong>维多利亚时代僵化的人造阶级文明秩序，对人类原生态自然生命能量的压制与必然反噬。优雅如果以阉割真情为代价，必然招致野蛮的血腥屠戮。<br>
        <strong>根本架构（形而上生死一如）：</strong>灵魂超越肉体存在、超越善恶世俗道德的绝对同一性追求。爱不是世俗的搭伙过日子，而是两个被世界流放的灵魂在宇宙废墟中的终极同质相拥。
      </div>"""

    sec08 = """      <div class="sub-heading">解释边界与警惕过度浪漫化</div>
      <p>现代读者切忌将希斯克利夫的狂暴行为美化为‘浪漫真爱’。他对无辜女性伊莎贝拉的身体与精神虐待、对患病儿子小林顿的冷血漠视，都是确凿无疑的恶魔行径。勃朗特展现的是深渊本身，而不是为了赞美深渊；她让我们目睹仇恨是如何将一个曾经受苦的孩子异化成一头嗜血的野兽，警示人类绝不可轻易用残酷摧毁一颗童真的心灵。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《呼啸山庄》指出了现代都市人在精致、安全但窒息的温室生活中，内心对某种‘未被驯化的纯粹生命力’的深刻渴望。我们今天生活在全空调覆盖、算法管理、注重情商礼貌的‘画眉田庄’里，但每个人心底都藏着一座狂风呼啸的荒原，潜伏着对绝对真实、绝不妥协的深情的隐秘渴望。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的情感选择中，你是否曾为了获得外界认可的‘体面、稳定与门第条件’，而违心放弃了那个让你灵魂产生剧烈震颤的人？</li>
        <li>当你遭遇严重的背叛或屈辱时，你心中的复仇之火是否也曾变成一把将无辜旁人一同烧焦的双刃剑？</li>
        <li>如果仇恨无法靠更大的暴力化解，你靠什么在这个充满伤害的世界上守住自己的善良？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《呼啸山庄》是英国文学史上最野性、最吓人也最深情的一本书。一个被虐待长大的孤儿，用三十年时间把迫害他的两大家族全逼入绝境。但他真正想要的不是钱，而是那个刻进他骨血里的女人。最后他在复仇顶峰绝食而死，和亡灵在荒原重聚。它告诉你：爱到了极致，连地狱也关不住它。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊聊英国文学界最不可思议的奇迹——艾米莉·勃朗特的《呼啸山庄》。很多人第一次看这本书会被吓到：男主角希斯克利夫像个疯子，女主角凯瑟琳像个女巫，全书充满叫骂、殴打、诅咒和幽灵。但这正是艾米莉·勃朗特的伟大之处——她彻底抛弃了维多利亚小说那种温情脉脉的下午茶调调，直接带你走进人性的荒原深处。故事里有两座房子：一座是呼啸山庄，代表狂风与原始野性；一座是画眉田庄，代表优雅与文明秩序。女主角凯瑟琳本是荒原上的野丫头，和吉普赛孤儿希斯克利夫灵魂相通，她说出了一句传世名言：‘无论灵魂是什么做的，他和我的都是同一种材料，而林顿就像霜与火那样截然不同！’但为了虚荣，她偏偏嫁给了林顿。希斯克利夫负气出走，三年后带巨资归来，开启了长达两代人的复仇绞杀。他把所有仇人的房产、儿女全玩弄于股掌之间。但就在大获全胜的前夕，他突然绝食死去了。为什么？因为凯瑟琳的鬼魂在荒原里敲了他二十年的窗户，他的灵魂早已跟着她走了。全书最后，仇人的后代在阳光下读书相爱，两大家族的仇恨在温情中彻底和解。这部小说告诉你：人活着不能光靠文明的面具，我们心底都有一片不容侵犯的野性旷野；而战胜这股毁灭能量的，最终依然是爱与包容。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “我的爱就像荒原下的岩石：它虽然不能给你带来浮华的欢悦，但它是坚不可摧的、是永恒存在的，它是支撑整座大地的基石。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界哥特文学巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第三章（幽灵敲窗）：</strong>精读洛克伍德在暴风雪夜遭遇冰冷小手抓挠窗棂、希斯克利夫失声痛哭的恐怖开场。</li>
        <li><strong>必读第二场 · 第九章（我就是希斯克利夫）：</strong>精读凯瑟琳在厨房炉火旁向丁奈莉倾吐‘岩石之爱与落叶之爱’的灵魂长白。</li>
        <li><strong>必读第三场 · 第十五章（病房诀别死吻）：</strong>精读凯瑟琳临死前两人互相撕扯、拥抱、控诉对方杀死了自己的震撼高潮。</li>
        <li><strong>必读第四场 · 第三十四章（雨夜绝食微笑暴毙）：</strong>精读希斯克利夫在荒原亡灵召唤下拒绝进食、在敞开的窗前含笑咽气的终局。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 善恶之外的灵魂契合：</strong>凯瑟琳深知希斯克利夫残暴野蛮，却依然宣称‘我就是希斯克利夫’，这种超越世俗道德评价的精神认同，在现实人类心理中究竟是否存在？
      </div>
      <div class="card-box">
        <strong>Q2 · 谁制造了恶魔？</strong>希斯克利夫的残暴，究竟是他骨子里的天性，还是辛德雷与维多利亚阶级社会数十年的精神虐待亲手打造出来的怪物？
      </div>
      <div class="card-box">
        <strong>Q3 · 复仇的终极荒谬：</strong>希斯克利夫在剥夺了仇人全部财产后感到前所未有的空虚，这给人类追求‘快意恩仇报复’的执念带来了怎样透骨的冰冷反思？
      </div>
      <div class="card-box">
        <strong>Q4 · 第二代的和解之美：</strong>为什么必须由小凯瑟琳教哈里顿‘读书认字’来完成两大家族的救赎？文明教化与原生善良在这里达成了怎样的崇高平衡？
      </div>
      <div class="card-box">
        <strong>Q5 · 荒原游荡的幽灵：</strong>故事结尾乡民看见两个手拉手的鬼魂在暮色中漫步，这究竟是迷信愚昧，还是大自然对一对受难灵魂终获安宁的深情诗意庇护？
      </div>"""

    sec13 = """      <div class="sub-heading">① 情绪断舍离工具：“希斯克利夫复仇止损模型” (The Heathcliff Void Audit)</div>
      <p><strong>适用场景：</strong>当你被某种长期的委屈、被轻蔑或被伤害的情绪所困，发誓要‘出人头地狠狠打他们的脸’、甚至产生报复冲动时。<br>
      <strong>第一步（查空虚）：</strong>问自己：如果三年后我真的彻底‘打脸’了对方，把对方踩在脚下，我内心的那个深渊大洞就会被填满吗？<br>
      <strong>第二步（识代偿）：</strong>看清真相：用仇敌的眼光作为自己前进的动力，本质上是把生命的遥控器永远交给了仇敌；<br>
      <strong>第三步（向阳转身）：</strong>像第二代哈里顿一样，把精力从‘向过去的伤害复仇’，转移到‘学习新知识、建设眼前真实的美好关系’上，这才是对恶魔宿命最彻底的击溃。</p>

      <div class="sub-heading">② 现实观察实验：“狂风下的生命力觉察”</div>
      <p>在一次刮大风或大雨的天气里，站在窗前静静观察窗外狂风中剧烈摇曳的树木。体会艾米莉·勃朗特笔下那种未经人类文明修剪的自然原力，反思自己在日常体面生活中有多少生命能量被自我过度压抑了。</p>

      <div class="sub-heading">③ 心理独白创作仿写任务</div>
      <p>模仿第九章凯瑟琳倾吐心声那种运用‘岩石、泉水、闪电与泥土’等自然意象的雄浑长句风格，写一段关于‘某段刻骨铭心、但注定无法在世俗中平稳相守的深沉执念’的散文诗段落（350字以内，意象鲜明、不用俗套流行语）。</p>"""

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

print("Round 05 deep Wuthering Heights ready.")

def get_deep_tale_of_two_cities():
    data = {
        "title_cn": "双城记",
        "title_en": "A Tale of Two Cities",
        "author_cn": "查尔斯·狄更斯",
        "author_en": "Charles Dickens",
        "sub_desc": "大革命风暴中的绝美复活挽歌 · 牺牲、博爱与人性涅槃的至高丰碑",
        "hero_quote": "这是最好的时代，这是最坏的时代；这是智慧的时代，这是愚蠢的时代；这是笃信的时代，这是疑虑的时代；这是光明的季节，这是黑暗的季节；这是希望之春，这是绝望之冬。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">查尔斯·狄更斯 (1812–1870)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1859 年连载出版 / 狄更斯巅峰杰作</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">历史小说 / 人道主义史诗 / 政治寓言</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 22 万字 / 全三卷四十五章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">13+ 岁 / 终身必读人文经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">历史暴力因果链条剖析与自我牺牲神圣超越性</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《双城记》简单看作一部反对法国大革命的保守主义反动宣教，更不要把断头台描绘当成廉价的恐怖噱头。狄更斯极其深刻地写出了大革命血腥恐怖的<strong>历史必然因果链条</strong>——如果旧制度贵族用马车随意轧死农家幼童、残忍奸杀农妇、将说真话的马内特医生无辜关入巴士底狱十八年，那么当历史的压迫达到极点，圣安东尼区滴淌的红酒终将化作断头台前不可遏制的滚滚人头血潮。狄更斯反对暴民嗜血，但更深刻谴责了亲手播下暴政恶种的统治阶级。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 双城时空全景对照与文学史上最著名的卷首语：</strong>伦敦的保守沉闷、法治微光与法庭偏见，与巴黎的群情激愤、贵族奢靡与革命血浪，构成了两面彼此映照的历史铜镜。卷首排比句不仅是修辞奇观，更是对人类文明在任何大动荡时代精神撕裂的精准诊断。
      </div>
      <div class="card-box">
        <strong>② 悉尼·卡顿从‘行尸走肉’到‘以身殉道’的惊天精神复活：</strong>卡顿是一个在生活中自甘堕落、酗酒沉沦的失意英格兰律师。然而出于对露西·马内特纯洁圣洁之爱的崇高信仰，他在死牢中利用容貌相似调包替死，微笑着登上断头台，用生命写下了全人类文学史上最催人泪下的告白：‘我现在所做的，远比我做过的一切都要好；我即将前去安歇的地方，远比我所知道的一切都要宁静。’
      </div>
      <div class="card-box">
        <strong>③ 德伐日太太在编织针下编织复仇名单的冷酷象征：</strong>这位巴黎酒馆老板娘不仅是革命者，更是被贵族残害至家破人亡的复仇女神。她在织针起落间，将一个个贵族家族的姓名编入生死簿，展现了暴力如何将受害者彻底塑造成毫无怜悯之心的杀戮机器。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        以1789年法国大革命前夕至1793年雅各宾派‘恐怖统治’时期为历史舞台。狄更斯穿梭于伦敦老贝利法庭与巴黎巴士底狱之间，叩问在革命洪流中良知与博爱的存亡。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tc-box { rx: 8; stroke-width: 1.5; }
            .tc-bg-london { fill: #1d3557; stroke: #2a4d7a; }
            .tc-bg-paris { fill: #8c2d19; stroke: #a33b24; }
            .tc-bg-hero { fill: #2a9d8f; stroke: #40916c; }
            .tc-bg-guillo { fill: #131619; stroke: #59645f; }
            .tc-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tc-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tc-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tc-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tc-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .tc-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .tc-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="tc-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 空间一：伦敦 (相对和平与法治) -->
          <rect x="20" y="25" width="200" height="115" class="tc-box tc-bg-london" />
          <text x="120" y="52" class="tc-t-w">伦敦 (London · 庇护所)</text>
          <text x="120" y="72" class="tc-t-sub-w">特尔森银行 · 恪守商业规矩</text>
          <text x="120" y="90" class="tc-t-sub-w">马内特医生：十八年地牢做鞋幸存</text>
          <text x="120" y="108" class="tc-t-sub-w">露西·马内特：金发爱意治愈父亲</text>
          <text x="120" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">复活与博爱的发源地</text>

          <!-- 空间二：巴黎 (暴政与革命血海) -->
          <rect x="460" y="25" width="200" height="115" class="tc-box tc-bg-paris" />
          <text x="560" y="52" class="tc-t-w">巴黎 (Paris · 熔炉)</text>
          <text x="560" y="72" class="tc-t-sub-w">圣安东尼酒馆 · 洒碎红酒化作血</text>
          <text x="560" y="90" class="tc-t-sub-w">德伐日夫妇：编织死亡黑名单</text>
          <text x="560" y="108" class="tc-t-sub-w">九月大屠杀 · 革命法庭狂欢</text>
          <text x="560" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">旧罪催生的复仇地狱</text>

          <!-- 核心行动者：悉尼·卡顿 (调包与复活) -->
          <rect x="240" y="145" width="200" height="85" class="tc-box tc-bg-hero" />
          <text x="340" y="172" class="tc-t-w">悉尼·卡顿 (Sydney Carton)</text>
          <text x="340" y="192" class="tc-t-sub-w">颓废天才律师 · 酷似查尔斯·达奈</text>
          <text x="340" y="210" class="tc-t-sub-w">死囚牢调包替死 · 灵魂大复活</text>

          <!-- 奔赴断头台连线 -->
          <path d="M 220 85 L 240 160" class="tc-blue" />
          <path d="M 460 85 L 440 160" class="tc-solid" />
          <path d="M 340 230 L 340 260" class="tc-solid" marker-end="url(#tc-arr)" />

          <!-- 下方：断头台与终极救赎 -->
          <rect x="180" y="260" width="320" height="65" class="tc-box tc-bg-guillo" />
          <text x="340" y="285" class="tc-t-w">断头台‘小红帽姑娘’ (La Guillotine)</text>
          <text x="340" y="305" class="tc-t-sub-w">牵着无辜缝纫女工的手从容就义 · 仇恨终结于大爱</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度剖析</div>
      <ul class="bullet-list">
        <li><strong>悉尼·卡顿：</strong>世界文学画廊中最具神圣魅力的浪子形象。他才华横溢却看破红尘，自嘲为‘一只给别人做嫁衣裳的豺狼’。他深爱露西，却深知自己配不上她，只留下一句‘为了你和你所爱的人，我愿意献出一切’。当达奈因贵族血统被判死刑时，卡顿潜入死牢，用氯仿麻醉达奈完成调包。在奔赴刑场的囚车上，他握着同样无辜被株连的十八岁小女工颤抖的手，在诵读‘复活在我，生命也在我’中安详受刑，完成了整个人格的神圣涅槃。</li>
        <li><strong>查尔斯·达奈（Charles Darnay）：</strong>法国厄弗里蒙地侯爵家族的继承人。他深恶痛绝家族的残暴统治，自愿放弃世袭领地与头衔，流亡英国靠教法语自食其力。然而在血腥的革命狂澜中，‘个人良善无法洗刷家族原罪’，他因解救老仆人冒险返法被捕，沦为历史宿怨的牺牲品。</li>
        <li><strong>德伐日太太（Madame Defarge）：</strong>文学史上最冷酷恐怖的复仇女神。她的亲姐姐被达奈的叔父与父亲强暴致死，哥哥被刺杀，父亲心碎暴毙。这场惨绝人寰的灭门惨案将她的全部同情心冻结成铁。她在法庭上拿出马内特医生当年的血泪控诉书将达奈送上绝路，誓言要将婴儿在内的一切贵族余孽连根铲除，最终在与普洛斯小姐的肉搏中死于走火的枪下。</li>
        <li><strong>马内特医生（Dr. Manette）：</strong>被苦难折磨的老人。因试图揭发贵族罪行被秘密囚禁巴士底狱北塔一百零五号长达十八年，靠在暗室里做皮鞋保持微弱心智。在女儿露西的爱意抚慰下，他的心智奇迹般‘复活’，在巴黎法庭上以受害者身份拯救女婿，展现了博爱对抗创伤的坚韧力量。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>1775年，流亡英国的露西·马内特得知自己以为早已去世的父亲马内特医生，竟在巴黎巴士底狱被秘密囚禁十八年后获释。露西奔赴巴黎，在老仆德伐日的酒馆里将精神失常、只会做鞋的白发父亲接回伦敦悉心照料，使老人的心智重新‘复活’。五年后，在伦敦老贝利法庭上，法国青年查尔斯·达奈被诬告叛国，凭借才华横溢却颓废不羁的辩护律师悉尼·卡顿因长相酷似达奈当庭制造疑点，达奈被判无罪。达奈与卡顿同时倾慕温柔圣洁的露西，达奈最终赢得美人芳心结为夫妇，卡顿则暗暗发誓愿为露西一家献出生命。1789年法国大革命爆发，攻克巴士底狱的群众在废墟中找到了马内特医生当年的绝笔控诉书。达奈为了营救被扣押的家族老管家冒险潜回巴黎，立刻被列为逃亡贵族逮捕入狱。马内特医生利用自己作为‘巴士底狱烈士’的崇高声望奔走呼号，一度使达奈无罪释放；然而德伐日太太当庭出示了医生当年的绝笔书，控诉厄弗里蒙地家族全家满门，陪审团勒令达奈二十四小时内推上断头台。绝境之中，深爱着露西一家的卡顿潜入巴黎，凭借手腕威逼看守，在死囚牢里用迷药麻醉达奈换上其衣物，命人将达奈全家火速送往英国。在全城搜捕的黄昏，卡顿手挽着同样无辜待决的弱小裁缝女工，在安详与圣洁的默念中微笑着走上断头台，用自己的死亡换取了所爱之人的全部幸福。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃拷问的是<strong>“仇恨能否靠更大的仇恨消灭？正义的事业一旦被极端盲目的暴力复仇绑架，文明将何去何从”</strong>。狄更斯以无与伦比的人道主义情怀宣告：政治暴力只会制造无休止的杀戮螺旋，唯有基督教式的舍己大爱与自我牺牲，才是彻底阻断仇恨链条、让文明获得新生的唯一希望。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        在血雨腥风的历史风暴深处，见证一个原本虚无自毁的失意灵魂，如何在一场毫无杂质的自我献祭中，绽放出比太阳还要眩目的道德神圣光芒。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个身处历史剧烈转折动荡之中、目睹极端仇恨与对立撕裂社会，渴望守住内心最底层善良底线的读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>暴政与暴民之间的仇恨反噬闭环 vs 以博爱与自我牺牲终结宿怨的崇高救赎。</strong></p>

      <div class="sub-heading">全书三卷史诗推进链条</div>
      <ol class="num-list">
        <li><strong>第一卷 · 复活归来（Recalled to Life）：</strong>泰尔森银行送信、巴黎圣安东尼区打碎酒桶如血流成河；阁楼上认父，露西的金发成为老医生穿透十八年黑暗的唯一光明锁链。</li>
        <li><strong>第二卷 · 金色的锁链（The Golden Thread）：</strong>老贝利法庭审判；达奈与卡顿长相酷似伏笔；侯爵马车在巴黎街头轧死男童丢下一块金币；侯爵在城堡遇刺咽气；达奈大婚，卡顿的深夜誓言。</li>
        <li><strong>第三卷上 · 狂澜入狱（The Track of a Storm）：</strong>攻陷巴士底狱，烧毁贵族城堡；达奈奔赴巴黎自投罗网，深陷死囚；恐怖法庭九月屠杀，马内特医生的声望成为保护伞。</li>
        <li><strong>第三卷中 · 控诉重开与死刑判定：</strong>德伐日太太亮出北塔105号墙洞秘藏手稿，揭露达奈父辈滔天罪行，法庭集体狂呼‘血债血偿’，达奈被判死刑。</li>
        <li><strong>第三卷下 · 调包替死与断头台涅槃：</strong>卡顿购买药水潜入死牢；调包送走达奈一家；普洛斯小姐在枪声中震聋双耳击毙德伐日太太；断头台前女工与卡顿相伴受死，全书在神圣的预言中升华。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第三卷第十章法庭当众宣读马内特医生十八年前的藏壁手稿：</strong>这封手稿是整部小说的因果核心。它证明了即使马内特医生此刻愿意原谅女婿，但他当年亲笔写下的‘以全人类公义诅咒厄弗里蒙地全家满门’的历史字据，依然无情地成了将女婿送上断头台的致命铁证。历史的因果律在此展现出绝对无情的冷酷闭环。
      </div>"""

    sec05 = """      <div class="sub-heading">悉尼·卡顿：颓废外表下的现代基督圣徒</div>
      <p>卡顿是狄更斯笔下最令人动容的灵魂。他聪明绝顶，但极度缺乏生活目标与被爱体验。他称自己‘注定一事无成’，整日借酒消愁。正是露西·马内特身上散发出的那种不带功利的温柔，第一次唤醒了他内心沉睡的高贵本质。他深知自己已经无法重过一生，但能‘为了那个点亮过自己灵魂的女人去死’，成了他枯竭生命中最绚烂的救赎。在走向刑场的路上，他不仅毫无恐惧，甚至还在安慰身旁素不相识的弱小女裁缝，完成了从颓废醉汉向圣徒的伟大跃迁。</p>

      <div class="sub-heading">德伐日太太：被仇恨彻底吞噬的机械复仇狂</div>
      <p>德伐日太太是世界文学中对极端暴力政治最深刻的警示。她的仇恨完全具有正当的起源——亲人被虐杀的惨剧任谁也无法承受。然而，当她被仇恨彻底占据后，她丧失了人类最基本的同情心。她不仅要杀达奈，甚至要将完全无辜的露西和小女孩一同送上断头台。狄更斯借此敲响警钟：<strong>当受害者用施暴者的残酷手段去复仇时，受害者就已经变成了新的恶魔</strong>。</p>"""

    sec06 = """      <div class="sub-heading">大河奔流般的史诗宏大象征与复调隐喻</div>
      <p>狄更斯在本作中展现了其语言生涯中最精纯的象征体系。全书的意象如同巨大的交响乐主导动机（Leitmotif），在双城之间反复共振，将历史的宏大与个人的命运紧紧锁死。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>打碎的红酒与流淌的鲜血 (Spilt Wine and Blood)：</strong>全书第一卷开篇圣安东尼区街头打碎的廉价红酒。饥渴的贫民趴在泥水里舔舐红酒，有人用沾满酒糟的手指在墙上写下‘BLOOD（血）’。这个绝妙的隐喻预言了日后大革命断头台下鲜血如红酒般四溢的人间惨象。</li>
        <li><strong>德伐日太太的编织针 (The Knitting Needles)：</strong>看似温良的妇女日常针线活，在全书中化作了死神的账簿。每一次下针、每一次编织，都是一条生命的终结。它象征着仇恨在漫长的沉默岁月中如何被精密地编织成不可逃脱的巨网。</li>
        <li><strong>金色的发丝 (The Golden Thread)：</strong>露西·马内特的金色秀发。它是全书唯一能对抗血腥风暴的崇高纽带，不仅把饱经摧残的老父亲从疯狂的泥潭拉回人间，更如同一根金线，将达奈的爱情与卡顿的牺牲神圣地缝合在一起。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（历史冒险大戏）：</strong>法国大革命恐怖统治期间，英国贵族青年因血统入狱，挚友挺身而出调包替死挽救家庭的大惨烈传奇。<br>
        <strong>深层架构（革命暴力因果学）：</strong>对专制压迫与暴力革命深层因果机制的无情解剖。暴政必然催生暴民，但以血洗血的革命狂欢无法建立真正的正义。<br>
        <strong>根本架构（基督式博爱牺牲）：</strong>‘复活’的核心题旨。肉体的消亡并不意味着毁灭，出于无私之爱的自我牺牲，是阻断世间滔天仇恨、使人类灵魂与文明真正重获新生的唯一坦途。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>托马斯·卡莱尔在《法国革命史》中对狄更斯产生了决定性影响。狄更斯在此书中深刻融合了卡莱尔的历史宿命感与自身坚守的人道主义温情。全书以‘复活在我，生命也在我’（《约翰福音》）贯穿始终，确立了西方文学中最为坚固的牺牲救赎神话。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>当一个社会内部的贫富差距与阶层隔阂被拉大到极点、弱势群体长期遭遇冷漠与侮辱时，群体内心积攒的怨毒终有一天会以某种盲目狂暴的形式爆发出来。而在网络舆论狂欢中动辄对某个个体或群体进行‘道德肉刑、赶尽杀绝’的狂热网暴，正是现代数字空间里德伐日太太式的断头台狂欢。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的生命中，是否有一个人或一种信念，值得你像悉尼·卡顿那样，为了成全其美好而愿意克制甚至牺牲自己的利益？</li>
        <li>当你在网络上参与某种针对犯错者的集体批判时，你是在追求真正的正义，还是在享受站在道德高地上‘挥舞编织针’的狂热快感？</li>
        <li>面对历史上的重大伤害，我们该如何像马内特医生那样走向宽恕，而不是像德伐日太太那样让仇恨吞噬自己全部的良知？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《双城记》是狄更斯最震撼人心的神作。法国大革命爆发，一个无辜的贵族青年被狂热暴民判处死刑；情敌卡顿利用长相一样，在死牢里用迷药把他调包救走，自己替他微笑着走上断头台。它告诉你：仇恨只会制造更多的血腥，唯有爱与牺牲才能让灵魂真正复活。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来重温世界文学史上的终极绝唱——狄更斯的《双城记》。那句传世开场白我们每个人都听过：‘这是最好的时代，这是最坏的时代！’小说讲了两个城市：伦敦和巴黎。法国旧制度下的贵族残暴无比，马车在街上撞死小婴儿，贵族甩下一枚金币扬长而去；无辜的马内特医生因为替被贵族糟蹋的贫民申冤，被秘密关进巴士底狱整整十八年，精神失常只会做鞋。女儿露西用如海的爱把父亲接回伦敦救活。后来，一个厌恶家族残暴自愿放弃贵族头衔的青年达奈爱上了露西，两人结婚。同时，一个整日借酒消愁、觉得自己一事无成的天才律师卡顿也深爱着露西，卡顿对露西说：‘我配不上你，但我发誓，为了你和你所爱的人，我愿献出生命。’大革命爆发了，达奈冒险回巴黎救人，立刻被疯狂的群众抓捕。当年被贵族灭门的酒馆老板娘德伐日太太，拿出马内特医生当年在牢房墙洞里写的血书，要求把达奈推上断头台血债血偿。就在二十四小时内即将问斩的绝境时刻，深爱着露西一家的卡顿潜入死牢，用迷药把达奈麻醉，换上达奈的衣服，让朋友将达奈一家火速送往英国。在全巴黎狂热的断头台前，卡顿拉着同样无辜被株连的十八岁小女工颤抖的手，在阳光下安详赴死。卡顿在临死前留下了一句名垂青史的遗言：‘我现在所做的，远比我做过的一切都要好；我即将前去安歇的地方，远比我所知道的一切都要宁静。’狄更斯用这本书告诉所有人：暴政可恨，暴民可怖，但仇恨永远救不了世界；唯有人与人之间舍己的博爱，才能穿透所有的黑暗，迎来真正的黎明。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “复活在我，生命也在我；信我的人，虽然死了，也必复活；凡活着信我的人，必永远不死。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界历史小说巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一卷第一章（时代开篇）：</strong>精读卷首排比名言，感受狄更斯宏大而精准的历史哲学纵深。</li>
        <li><strong>必读第二场 · 第一卷第五章（圣安东尼区酒桶打碎）：</strong>精读贫民舔舐红酒、在墙上写下‘血’的预言性白描。</li>
        <li><strong>必读第三场 · 第二卷第九章（老侯爵城堡遇刺）：</strong>精读贵族奢华冷酷与石雕人面凝固的惊悚夜晚。</li>
        <li><strong>必读第四场 · 第三卷第十章（巴士底狱墙洞血书宣读）：</strong>法庭上宣读医生绝笔，感受因果报应不可逆转的戏剧高潮。</li>
        <li><strong>必读第五场 · 第三卷第十五章（断头台与小女工相伴受死）：</strong>精读卡顿从容赴死的全过程，体验文学史上最崇高的神圣受难。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 达奈的赎罪限度：</strong>达奈自愿放弃贵族头衔、隐姓埋名自食其力，为什么革命法庭依然执意要将他处死？这揭示了个体在面对宏大集体历史罪恶时的何种无力感？
      </div>
      <div class="card-box">
        <strong>Q2 · 德伐日太太的悲剧根源：</strong>德伐日太太的残暴全是由仇恨塑造的，如果她最终没有在走火的枪下毙命，她能在一个和平的新社会中安度晚年吗？
      </div>
      <div class="card-box">
        <strong>Q3 · 卡顿的替死动机：</strong>卡顿之所以愿意替死，究竟是因为他对自身人生的极度绝望，还是出于对露西一家神圣深沉的爱？抑或是两者的崇高融合？
      </div>
      <div class="card-box">
        <strong>Q4 · 暴力与自由的悖论：</strong>大革命的口号是‘自由、平等、博爱或死亡’，但当‘博爱’必须以无休止的‘死亡’为强制手段时，它是否已经异化为了另一种更残暴的专制？
      </div>
      <div class="card-box">
        <strong>Q5 · 终局预言的意义：</strong>全书最后卡顿在断头台上预见到了一个繁荣、和平、自由的新巴黎，狄更斯通过这种预见寄托了对人类未来怎样的历史乐观主义信念？
      </div>"""

    sec13 = """      <div class="sub-heading">① 冲突化解思维工具：“卡顿阻断仇恨模型” (The Carton Reconciliation Shift)</div>
      <p><strong>适用场景：</strong>在团队、家庭或两代人之间陷入‘以牙还牙、互相伤害’的长期内耗冷战时。<br>
      <strong>第一步（找死结）：</strong>看清当前的互掐循环：双方都认为自己是正义受害者，都在用对方犯过的错作为自己继续伤害对方的借口；<br>
      <strong>第二步（主动承担微小牺牲）：</strong>必须有一方主动站出来，像卡顿一样，主动放弃一次‘讨回公道、让对方认错’的虚荣权利，甚至自愿承受一次微小的利益损失；<br>
      <strong>第三步（终结恶性闭环）：</strong>用实质性的无私奉献让对方的报复逻辑瞬间失效，将战场从‘算旧账’转移到‘共赴未来’。</p>

      <div class="sub-heading">② 现实观察实验：“群体狂热与情绪传染观察”</div>
      <p>观察社交网络上一场正在发酵的‘全网讨伐某人’的舆论风暴。记录其中使用最频繁的侮辱性词汇，分析围观群众是如何在一瞬间完成从‘围观者’到‘狂热行刑者’的心理转变的，体会狄更斯笔下断头台狂乱在数字时代的还魂。</p>

      <div class="sub-heading">③ 宏大对比仿写任务</div>
      <p>模仿《双城记》第一章‘这是最好的时代，这是最坏的时代’那种正反并置、宏大从容的史诗排比修辞，写一段三百字评价我们当下数字化人工智能时代的哲理短章（语言庄严、层层推进）。</p>"""

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

print("Round 05 deep A Tale of Two Cities ready.")

def get_deep_hard_times():
    data = {
        "title_cn": "艰难时世",
        "title_en": "Hard Times",
        "author_cn": "查尔斯·狄更斯",
        "author_en": "Charles Dickens",
        "sub_desc": "功利主义时代的冷酷解剖刀 · 当数据与事实扼杀了人类的情感与童真",
        "hero_quote": "先生，在这个世界上，我们唯一需要的唯有‘事实’！除了事实，什么都不要播种，什么都不要培育；唯有事实才能塑造出具有实际用途的理性头脑！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">查尔斯·狄更斯 (1812–1870)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1854 年在《世界之窗》连载出版</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">批判现实主义 / 工业社会政治讽刺长篇</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 18 万字 / 全三卷三十七章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">13+ 岁 / 青年与社会通识必读</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">工具理性与功利主义教育对人性的戕害机制</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿以为《艰难时世》只是一部批判工业革命煤烟污染环境的小说。狄更斯的核心利刃直刺整个现代文明的根基——<strong>以边沁功利主义（Utilitarianism）为哲学支撑的‘数字崇拜与事实至上主义’</strong>。当教育将孩子当做量杯强行灌注冰冷数据，当工厂将工人当做毫无情感的‘机械人手（Hands）’，整个社会不仅没有变得理性繁荣，反而直接制造了精神虚脱的女儿与偷窃逃亡的罪犯儿子。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 极具荒谬感的‘事实学校’经典开场：</strong>葛擂硬先生在教室里厉声斥责女孩西丝不懂定义一匹马（‘马是有四十颗牙齿、蹄有硬角、食草的哺乳动物’），而女孩对马的温度、奔跑与情感的真实感知，被当成毫无价值的愚蠢废料。这是世界文学史上对死记硬背与应试功利教育最辛辣的解剖。
      </div>
      <div class="card-box">
        <strong>② 焦煤镇（Coketown）如巨大黑蛇般的工业巨兽白描：</strong>狄更斯将工业城镇描绘成一座千篇一律、单调乏味的地狱——红砖墙被煤烟熏黑得如同一具印第安人的红黑脸谱，巨大的蒸汽机活塞日夜单调地上下起伏，宛如一头患了忧郁症的狂躁大象在不停点头。人人在机器中沦为丧失灵魂的面具。
      </div>
      <div class="card-box">
        <strong>③ 马戏团流浪艺人对冷酷资本社会的诗意拯救：</strong>斯莱瑞马戏团虽然身处社会最底层，演员口齿不清、生活漂泊，但他们身上保留了最纯真的人性温存、想象力与互助美德。正是马戏团的小女孩西丝·朱佩，以朴素的爱治愈了葛擂硬全家，宣告了被功利主义蔑视的‘无用童心与情感’才是维系人类社会不致崩溃的真正基石。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪中叶英国兰开夏郡棉纺织业中心。曼彻斯特资本家鼓吹自由放任与唯利是图的功利哲学，劳资矛盾激化，儿童教育沦为流水线预备役。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .ht-box { rx: 8; stroke-width: 1.5; }
            .ht-bg-coke { fill: #131619; stroke: #59645f; }
            .ht-bg-grad { fill: #1d3557; stroke: #2a4d7a; }
            .ht-bg-circus { fill: #2a9d8f; stroke: #40916c; }
            .ht-bg-worker { fill: #8c2d19; stroke: #a33b24; }
            .ht-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ht-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ht-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ht-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ht-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .ht-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .ht-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="ht-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 焦煤镇资本统治者：庞得贝 -->
          <rect x="20" y="25" width="200" height="115" class="ht-box ht-bg-coke" />
          <text x="120" y="52" class="ht-t-w">银行家/厂主：庞得贝</text>
          <text x="120" y="72" class="ht-t-sub-w">狂妄自大 · 吹嘘白手起家</text>
          <text x="120" y="90" class="ht-t-sub-w">视工人为‘唯利是图的贪婪齿轮’</text>
          <text x="120" y="108" class="ht-t-sub-w">老母现身戳穿其自小受宠谎言</text>
          <text x="120" y="124" style="fill:#e0e4e8; font-size:10px; text-anchor:middle;">资本家虚伪暴发的终极小丑</text>

          <!-- 功利主义理论家：葛擂硬先生 -->
          <rect x="460" y="25" width="200" height="115" class="ht-box ht-bg-grad" />
          <text x="560" y="52" class="ht-t-w">事实议员：葛擂硬先生</text>
          <text x="560" y="72" class="ht-t-sub-w">抹杀童真想象 · 唯数字论</text>
          <text x="560" y="90" class="ht-t-sub-w">女儿婚姻毁灭 · 儿子堕为盗贼</text>
          <text x="560" y="108" class="ht-t-sub-w">在大雨之夜面对女儿控诉心碎</text>
          <text x="560" y="124" style="fill:#cad5e2; font-size:10.5px; font-weight:700; text-anchor:middle;">晚年幡然悔悟，投向人道慈悲</text>

          <!-- 牺牲与控诉中心：路易莎 (女儿) -->
          <rect x="240" y="145" width="200" height="85" class="ht-box ht-bg-worker" />
          <text x="340" y="172" class="ht-t-w">路易莎 (Louisa Gradgrind)</text>
          <text x="340" y="192" class="ht-t-sub-w">被剥夺情感知觉的优秀女儿</text>
          <text x="340" y="210" class="ht-t-sub-w">被迫嫁给丑陋老头庞得贝，精神窒息</text>

          <!-- 暴风雨夜逃回父母家连线 -->
          <path d="M 460 85 L 430 150" class="ht-blue" />
          <path d="M 220 85 L 250 150" class="ht-solid" />

          <!-- 下方解药与对比：斯莱瑞马戏团 & 矿工 -->
          <rect x="160" y="250" width="360" height="75" class="ht-box ht-bg-circus" />
          <text x="340" y="275" class="ht-t-w">救赎与温情：西丝·朱佩 & 矿工布莱克浦</text>
          <text x="340" y="295" class="ht-t-sub-w">西丝以爱心陪伴拯救家庭 · 矿工坠入枯井留下宽恕遗言</text>
          <text x="340" y="310" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">“人不能仅靠算盘活着，人活着需要彼此相爱”</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度剖析</div>
      <ul class="bullet-list">
        <li><strong>葛擂硬先生（Thomas Gradgrind）：</strong>全书最典型的悲剧父亲。他不是恶棍，他真诚地以为把孩子培养成‘冷酷计算的实用机器人’是对孩子最好的保护。他建起严格的‘石室公馆’，不准孩子们读童话、不准看马戏、不准仰望星空发呆。直到大女儿路易莎浑身湿透跪在地上哭诉自己生不如死，大儿子汤姆为了还赌债自甘堕落抢劫银行，葛擂硬的世界观轰然倒塌。他最终用自己曾经鄙视的马戏团小丑技巧掩护儿子逃亡，完成了理智向爱的深沉屈服。</li>
        <li><strong>路易莎·葛擂硬：</strong>教育异化的最高受难者。她拥有极高的智识潜力，却被父亲从小阉割了感受爱、表达爱的机能。当老丑自大的庞得贝向她求婚时，她冷漠地问父亲：‘在这个世界上，除了数字和利益，还有别的事情需要考虑吗？既然没有，那我就嫁吧。’直到纨绔子弟哈特豪斯用虚假的温情挑动她未曾苏醒的情感时，她险些失足，在最后一刻逃回父亲身边发出泣血长号，成为现代被工具化教育摧残者的千古绝响。</li>
        <li><strong>斯蒂芬·布莱克浦（Stephen Blackpool）：</strong>焦煤镇四万棉纺织工人的圣洁化身。他一生老实巴交，妻子酗酒堕落但由于法律只为富人服务他无钱离婚；他拒绝加入激进工会的盲目罢工，被全镇工人孤立；他又坚决不肯向资方出卖工友名单，被庞得贝无情开除。他被汤姆陷害背上抢劫银行的黑锅，在回城申冤的荒原雪夜坠入废弃的‘老地狱深井’。在临终弥留之际，他仰望着头顶夜空中唯一的一颗璀璨星辰，留下了一句震撼全人类的祈愿：‘求主宽恕所有在这艰难时世中互相伤害的人们。’</li>
        <li><strong>西丝·朱佩（Sissy Jupe）：</strong>马戏团丑角的遗孤。在‘事实学校’里，她因无法算出‘一百万人口的城市里死于饥荒的比例’而被判定为智力低下的劣等生——因为她关心的不是比例数字，而是‘那每一个饿死的人在这个世界上留下的空缺和痛苦’。正是这个被理性主义判定为‘毫无前途’的弱女子，用她最朴素的同情心陪伴病弱的母亲、守护心碎的路易莎、最终协助挽救了全家人。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>焦煤镇是一座被黑烟笼罩的北方工业纺织重镇。国会议员葛擂硬先生在镇上创办了声名显赫的‘事实模范学校’，严禁任何想象力、诗意与娱乐。马戏团跳骑小丑朱佩抛弃女儿逃跑，葛擂硬出于道德体面收养了小女孩西丝。葛擂硬的一对儿女路易莎与汤姆在极度压抑的理性戒律下长大。成年后，为了给不成器的弟弟汤姆在银行铺路，路易莎违心嫁给了比自己年长三十岁、虚荣粗俗的暴发户银行家庞得贝。老实淳朴的棉纺工人斯蒂芬·布莱克浦生活在不幸婚姻的泥潭中，因为坚守良知既不加入盲目罢工也不肯充当资方密探，被工友与老板双重唾弃开除。与此同时，伦敦浪荡政客哈特豪斯来到焦煤镇竞选，敏锐察觉到路易莎内心的巨大荒芜，展开猛烈的情感诱惑。就在私奔前夕，精神崩溃的路易莎在大雨倾盆的黑夜逃回父亲身边，昏倒在地发出对功利主义教育的痛悔控诉。葛擂硬大受震动，决意庇护女儿与庞得贝彻底决裂。此时，庞得贝的银行发生重大现金失窃案，真正的窃贼——浪子汤姆故意散布谣言嫁祸给外逃求职的工人斯蒂芬。斯蒂芬闻讯赶回证明清白，不幸在暴风雨夜坠入深不见底的废弃矿坑。在西丝与众人的搜救下，垂危的斯蒂芬被绞盘拉出地表，临终前指认了真相并在星光下安详咽气。在马戏团故交斯莱瑞的掩护下，悔悟的葛擂硬协助儿子汤姆化装成小丑逃往美洲，彻底抛弃了唯事实论，在晚年致力于保护工人和儿童权益的人道事业。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃叩问的是<strong>“现代工业文明如果将‘投入产出比’当成衡量人性的唯一准绳，人类社会将滑向何种非人化的地狱”</strong>。狄更斯向全人类敲响警钟：数字、统计学与经济指标固然能带来庞大的财富，但唯有情感、欢笑、童真与无私的博爱，才是区分人与机器的最后一道神圣防线。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        不是一部枯燥的工业报告，而是一把滚烫的人道主义烙铁，狠狠烫在现代社会‘唯KPI、唯分数、唯效率论’的冰冷脑门上，逼迫每个人重新打量内心的荒芜。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个正在用数字、分数、排名折磨孩子的心焦父母，以及每一个在现代KPI考核体系中感到自己被当成无名工具人、日渐丧失生活温度的都市职场人。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以事实和数字为代表的功利资本主义冷酷秩序 vs 以马戏团和童真为代表的人类自然天性与真情渴望。</strong></p>

      <div class="sub-heading">全书三卷‘播种与收获’推进链条</div>
      <ol class="num-list">
        <li><strong>第一卷 · 播种（Sowing）：</strong>事实学校残酷体罚想象力，西丝入驻石室公馆；路易莎凝视壁炉火星自问人生意义；庞得贝虚荣吹嘘白手起家神话；包办婚约达成。</li>
        <li><strong>第二卷 · 收获（Reaping）：</strong>毫无温存的枯竭婚姻；伦敦政客哈特豪斯的无聊猎艳与心理操纵；银行失窃案发生，汤姆构陷诚实矿工斯蒂芬；大雨之夜路易莎狂奔回家彻底摊牌，老葛擂硬世界观首度坍塌。</li>
        <li><strong>第三卷 · 储藏（Garnering）：</strong>庞得贝母亲现身戳穿其自小受尽宠爱、毫无苦难的弥天大谎，傲慢资本家颜面扫地；荒原老地狱深井救赎，斯蒂芬星光下离世；马戏团花脸小丑掩护汤姆逃离国境，全剧在大爱与重生的洗礼中定格。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第二卷第十二章大雨之夜路易莎倒在父亲脚下：</strong>这位从小受尽‘事实教育’的最优等生，抓着胸口向父亲发出世界文学中最震撼的哀鸣：‘你把我的智慧塞得满满的，却把我的心变成了一座死寂的荒原！如果当年你允许我拥有哪怕一点点女孩的眼泪和软弱，我今天就不会落到这步田地！’这一瞬间，葛擂硬数十年构筑的功利主义哲学大厦彻底坍塌成灰。
      </div>"""

    sec05 = """      <div class="sub-heading">庞得贝：白手起家神话背后的虚荣恶霸</div>
      <p>庞得贝是狄更斯笔下最具讽刺力度的资产阶级暴发户典型。他整日挂在嘴边的一句话是：‘我小时候是个被母亲遗弃在臭水沟里的野孩子，全靠自己一把烂泥啃成今天的银行家！’他以此为道德借口，残酷克扣工人工资，声称‘任何工人只要抱怨，就是妄想吃金汤匙装的乌龟汤’。第三卷中，他那位乡下老母亲为了看望风光的儿子偶然现身，当场道破真相：庞得贝自小受到母亲倾尽所有的呵护、送进好学校读书，他所谓的‘悲惨弃儿神话’完全是他为了拔高自己个人奋斗威名而编造的欺世谎言！这一耳光打穿了近代资本主义所有神化剥削的遮羞布。</p>

      <div class="sub-heading">斯蒂芬·布莱克浦：深渊中的无辜受难者</div>
      <p>斯蒂芬是英国劳工阶级最让人心碎的写照。他勤劳、善良、守诺。面对激进罢工煽动者斯莱克斯桥的群情激愤，他固执地认为‘罢工打架解决不了问题，只会带来更多的仇恨和饥饿’；然而面对冷酷的庞得贝，他又坚决不肯背叛工友充当告密内奸。他的结局是被丢入废弃煤井‘老地狱（Old Hell Shaft）’。在黑暗深坑里躺了三天三夜后被救起时，他没有咒骂任何人，只是指着夜空说：‘看那颗星星，它照亮了我的坑底，也照亮了天国之路。’他是工业革命祭坛上最圣洁的一只知更鸟。</p>"""

    sec06 = """      <div class="sub-heading">焦煤镇如黑色毒蟒般的工业批判语言</div>
      <p>狄更斯在本书中开创了一种<strong>极具表现主义色彩的工业环境描摹文风</strong>。他把黑烟比作‘永不散去的巨大黑蟒’，把蒸汽机的轰鸣比作‘疯狂象群的机械点头’，把街道比作‘无数一模一样的红黑火柴盒’。语言冷酷、压抑、带有强烈的金属摩擦感，与斯莱瑞马戏团跳骑演员们充满浓重大舌头口音、俚语和欢笑的民间狂欢口语形成强烈对比，展现了语言的政治学力量。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>焦煤镇的黑烟巨蟒 (The Smoke Serpents of Coketown)：</strong>笼罩在全城烟囱上空终年不散的黑色毒雾。它象征着<strong>毫无节制的物质利益追求对人类自然生机与精神呼吸的永久窒息</strong>。</li>
        <li><strong>壁炉深处的火星 (The Sparks in the Fireplace)：</strong>路易莎少女时期整日整夜凝视的壁炉火炭。它象征着<strong>被理性教条强行封锁在深闺中的少女，内心深处那团微弱却从未真正熄灭的情感渴望与生命之火</strong>。</li>
        <li><strong>老地狱深井 (The Old Hell Shaft)：</strong>荒原上废弃未加盖板的致命深煤坑。它不仅夺去了斯蒂芬的生命，更象征着<strong>工业资本在疯狂开采大自然财富之后，遗留在大地与人类良知深处的险恶深渊与历史陷阱</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（工业社会伦理小说）：</strong>十九世纪英国北方纺织重镇中，议员的功利主义家规破灭、资本家虚伪神话破产、无辜工人蒙冤受难的家庭与社会批判大戏。<br>
        <strong>深层架构（现代工具理性反思）：</strong>对将人降维为生产要素、将教育异化为流水线考试机器的现代功利哲学的系统性清算。证明没有情感与审美作为缓冲，高度发展的理性只会孕育出冷酷自私的罪犯与行尸走肉。<br>
        <strong>根本架构（爱与童真的本体救赎）：</strong>唯有人类未经功利污染的朴素善意、同理心与马戏团式的童真欢笑，才是维系人类社会不致在冰冷竞争中解体瓦解的真正胶水。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>英国著名思想史家约翰·拉斯金曾断言：《艰难时世》是狄更斯生平所写过‘最严肃、最伟大、最具有先知般预言力的一部作品’。他在工业革命极盛期就以惊人的敏锐，看穿了现代管理学、数据统计学背后冷血物化人性的巨大危险，开创了西方现代人道主义对‘唯效率论’的长达一个半世纪的批判传统。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天的应试教育内卷与现代企业管理，几乎是焦煤镇‘事实学校’的超级增强版：<br>
      孩子们从小被灌输各种加分竞赛与升学指标，任何被视为‘无用’的画画、发呆、捉迷藏、看闲书都被视作犯罪；成年人被捆死在精密的OKR与KPI考勤打卡系统里，个人的喜怒哀乐在冰冷报表前毫无意义。《艰难时世》撕开了这一切精致伪装：如果教育出来的孩子既不懂得爱别人也不懂得快乐，这种所谓的‘成功’到底是在创造繁荣，还是在批量生产心理残疾？</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你接受的家庭或学校教育中，是否有哪一项你真心热爱的事情，曾因为‘对考试或赚钱毫无用处’而被长辈无情掐灭？</li>
        <li>当你在工作中把客户或下属仅仅当做完成业绩的‘数字指标’时，你是否意识到自己正在变成另一个微小冷酷的葛擂硬？</li>
        <li>在高度功利的社会竞争中，你靠什么守护内心那片属于‘马戏团西丝·朱佩’式的纯真与善良？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《艰难时世》是专治现代‘唯分数论和唯KPI论’的一剂猛药。一个父亲不准孩子有任何想象力，只准学冰冷的数据事实。结果女儿被逼嫁给自大老头精神崩溃，儿子沦为银行窃贼。最后救了全家的，反而是从小被嘲笑成绩不好的马戏团穷女孩。它告诉你：只认事实的人，最后会被事实狠狠抽耳光。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊聊狄更斯最具现代警世力量的杰作《艰难时世》。如果你也常常感到被工作报表、KPI考核或者孩子的考试名次压得喘不过气，这本书会像惊雷一样震醒你。故事发生在工业重镇焦煤镇，到处是黑烟和轰鸣的机器。国会议员葛擂硬先生办了一所模范学校，第一堂课就怒吼：‘世界上需要的唯有事实，除了事实，其他一切都是废话！’他不仅这么教学生，也这么虐待自己的亲生儿女——不准看童话、不准有幻想。他的女儿路易莎考了一百分，但内心一片荒原；为了利益，父亲逼她嫁给大她三十岁、满嘴跑火车的银行家庞得贝。然而，没有感情的婚姻就是一座活地狱，路易莎在无聊中被纨绔子弟诱惑，差点私奔，最后在狂风大雨的夜晚逃回父亲身边，跪在地上发出绝望控诉：‘你给了我一脑子的知识，却把我的心变成了一片死坟地！’与此同时，严格按照唯利是图教育出来的儿子汤姆，因为贪婪和赌博，居然自编自导抢劫了父亲朋友的银行，还狠心嫁祸给一个老实巴交的穷工人斯蒂芬。这位工人为了证明清白，在大雨夜赶回焦煤镇，失足掉进了废弃的‘老地狱深井’，临死前望着夜空里的星星原谅了所有人。就在葛擂硬全家身败名裂的绝境关头，谁救了他们？不是银行家，不是大学学者，而是当年学校里成绩最差、从小在马戏团长大的小女孩西丝。马戏团的粗人们用杂耍和小丑技巧，巧妙掩护那个犯了法的儿子逃往国外。葛擂硬老头彻底大哭醒悟，晚年再也不谈冰冷的数据，而是把全部精力投入到了关爱工人和儿童的人道事业中。狄更斯在这本书里留下了一句至理名言：‘算盘算得出天下的利益，但算不出人心的温暖；如果一个文明只认事实不认爱，这个文明迟早会在自己的黑烟中窒息而亡！’”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “永远不要用冰冷的数字去衡量人性的分量；在生命的账簿上，最宝贵的东西从来都是不可估价的爱与眼泪。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界工业社会讽刺巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一卷第一至二章（事实学校的马匹定义）：</strong>精读葛擂硬与督学在教室里剥夺儿童想象力、西丝被当众羞辱的荒诞名场面。</li>
        <li><strong>必读第二场 · 第一卷第五章（焦煤镇的黑烟巨蟒）：</strong>世界文学史上最经典的工业化城市表现主义环境白描。</li>
        <li><strong>必读第三场 · 第二卷第十二章（大雨之夜路易莎的血泪控诉）：</strong>精读全剧最高潮，感受被工具化教育摧残者的千古悲鸣。</li>
        <li><strong>必读第四场 · 第三卷第六章（老地狱深坑与星光）：</strong>精读工人斯蒂芬被绞盘拉出深井、仰望星辰留下宽恕遗言的神圣时刻。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 知识与智慧的鸿沟：</strong>西丝·朱佩在学校里连最简单的平均数都算不明白，为什么当灾难降临时，她却表现出了全书所有人都不具备的定力、良知与爱心？
      </div>
      <div class="card-box">
        <strong>Q2 · 功利主义教育的必然产物：</strong>为什么完全遵循葛擂硬‘自私功利逻辑’长大的儿子汤姆，最终会变成一个自私自利、毫无感恩之心、甚至陷害无辜工人的盗贼？
      </div>
      <div class="card-box">
        <strong>Q3 · 庞得贝白手起家神话的崩塌：</strong>当老母亲当众拆穿庞得贝当年受尽家庭呵护、根本不是什么‘臭水沟里长大的弃儿’时，周围小市民的反应为什么极其尴尬？这给现代社会的‘成功学包装’提供了怎样的讽刺？
      </div>
      <div class="card-box">
        <strong>Q4 · 斯蒂芬的拒绝两头讨好：</strong>斯蒂芬既不肯加入偏激工会的罢工，又不肯向资方出卖同胞名单，这种‘两头不讨好的良知坚守’在现实社会中为什么往往最容易被碾碎？
      </div>
      <div class="card-box">
        <strong>Q5 · 马戏团的终极隐喻：</strong>在全书结尾，为什么拯救知识分子家庭的偏偏是这群不识几个大字、身上散发着汗臭与马粪味的马戏团流浪汉？这体现了狄更斯怎样的人性信念？
      </div>"""

    sec13 = """      <div class="sub-heading">① 教育与生活排毒工具：“事实学校盲区测试” (The Gradgrind Filter)</div>
      <p><strong>适用场景：</strong>在面对孩子教育规划、或者自己在制定个人学习计划陷入‘考证内卷、唯分数论’的枯竭焦虑时。<br>
      <strong>第一步（找数据陷阱）：</strong>检查你的日程表：有多少时间被‘纯粹为了打卡、考试、排名’的数据任务所霸占？<br>
      <strong>第二步（查心灵荒原）：</strong>在过去的一个月里，你或你的孩子是否有过一次纯粹为了快乐的大笑、一次对着夕阳或花草的驻足发呆、或者一次为了正义帮助他人的真诚行动？<br>
      <strong>第三步（引入马戏团要素）：</strong>在坚硬的事实日程中，强制插入一项‘毫无实际用途、但能让眼睛发亮’的纯真活动（如看杂技、学陶艺、去林间听鸟鸣）。</p>

      <div class="sub-heading">② 现实观察实验：“办公楼里的黑烟巨蟒”</div>
      <p>观察现代CBD写字楼里员工的日常面孔：从早上挤地铁刷卡进闸，到格子间里面对双屏电脑机械敲击八小时，记录三个人身上表现出的‘如同焦煤镇大象点头般’的机械麻木举止，反思现代企业制度对人性的磨损。</p>

      <div class="sub-heading">③ 讽刺演说仿写任务</div>
      <p>模仿第一章葛擂硬先生那种盛气凌人、满口都是‘数据、事实、指标’的官僚口吻，写一段三百字‘一个现代人工智能算法主管在向实习生强调为什么员工的情感毫无价值’的讽刺对白（反讽力度拉满）。</p>"""

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
    print("=== 开始批量写入第 5 轮（呼啸山庄、双城记、艰难时世） ===")
    plan = [
        ("呼啸山庄", get_deep_wuthering_heights),
        ("双城记", get_deep_tale_of_two_cities),
        ("艰难时世", get_deep_hard_times),
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
