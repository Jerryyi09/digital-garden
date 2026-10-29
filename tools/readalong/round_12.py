# -*- coding: utf-8 -*-
"""
Round 12: O. Henry Selected Stories, Life on the Mississippi, The Time Traveler's Wife (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_o_henry():
    data = {
        "title_cn": "欧·亨利短篇小说精选",
        "title_en": "Selected Stories of O. Henry",
        "author_cn": "欧·亨利",
        "author_en": "O. Henry (William Sydney Porter)",
        "sub_desc": "世界三大短篇小说巨匠之一 · 曼哈顿四百万小人物的含泪微笑与至情神反转",
        "hero_quote": "人生是由啜泣、抽噎与微笑交织而成的，而抽噎占据了其中绝大部分；但只要在这冰冷的人间还有一丝未曾熄灭的善意，微笑便拥有刺穿一切黑暗的神圣微光。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说巨匠</div><div class="spec-val">欧·亨利 (1862–1910)</div></div>
        <div class="spec-item"><div class="spec-label">创作年代</div><div class="spec-val">20世纪初镀金时代 / 传世名篇精萃</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">世态短篇小说 / 欧·亨利式反转典范</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">精选数十部代表作 / 约 25 万字</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">11+ 岁 / 全年龄终生必读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">意外结局叙事技巧与底层人道同理心浓度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把欧·亨利的作品浅薄地当成‘抖机灵的段子合集’或‘纯凭巧合取胜的快餐小说’。欧·亨利因被冤枉挪用银行公款坐过三年冤狱，他在俄亥俄州联邦监狱的死囚牢房与夜班医务室里，看尽了社会底层最深沉的苦难与泪水。他出狱后混迹于纽约最廉价的啤酒馆、公园长椅与阁楼，他笔下的每一个‘神反转’，不是为了炫耀编剧技巧，而是为了<strong>在冰冷荒谬的资本金钱丛林中，像魔术师一样从破烂口袋里掏出一块热乎乎的糖，给那些在苦海中挣扎的弱小生灵带去活下去的尊严与暖意</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 《麦琪的礼物》（The Gift of the Magi）中的‘错位献祭哲学’：</strong>圣诞节前夕，贫穷小夫妻各自瞒着对方，妻子卖掉自己唯一引以为傲的及膝瀑布般美丽长发，为丈夫的传家金表配了一根纯白金表链；而丈夫当掉了祖传金表，为妻子买回了她渴望已久的带宝石玳瑁发梳。两件礼物在实用层面上瞬间变成了毫无用处的废品，然而在精神层面上，他们却完成了人类文学史上最崇高富有的无私相赠。
      </div>
      <div class="card-box">
        <strong>② 《最后一片叶子》（The Last Leaf）中艺术杰作的真正定义：</strong>暴躁、酗酒、一辈子叫嚣要画传世杰作却连房租都交不起的底层老画家贝尔曼，在寒冬冰雨肆虐的深夜，冒着严寒肺炎爬上梯子，在湿冷冰凉的红砖墙上画下了一片永不凋零的常春藤叶。正是这片绿叶救活了心死等死的年轻女画家琼珊。贝尔曼用生命画下的这幅画，宣告了真正的艺术不在于挂进卢浮宫，而在于能否拯救一个垂死的生命。
      </div>
      <div class="card-box">
        <strong>③ 《警察与赞美诗》（The Cop and the Anthem）中宿命讽刺的最高黑色幽默：</strong>无家可归的流浪汉苏比为了在温暖的布莱克韦尔岛监狱蹭过严冬，使出浑身解数去高档餐厅吃霸王餐、砸碎橱窗玻璃、调戏良家妇女、在街头装醉狂喊，警察却每一次都把他当成狂欢大学生放过；就在他在古老教堂窗外听见童年熟悉的赞美诗管风琴声、流着热泪发誓明天重新做人自食其力的那一秒钟，一只冷冰冰的大手搭在他肩头——警察以‘无端闲荡罪’当场将其逮捕判处三个月苦役。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        20世纪初美国镀金时代与进步主义交界期的纽约曼哈顿。四百万小职员、失意画家、售货女郎、流浪汉在摩天大楼与地下排污口之间求生，金钱拜物教与温情同理心剧烈碰撞。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .oh-box { rx: 8; stroke-width: 1.5; }
            .oh-bg-nyc { fill: #1d3557; stroke: #2a4d7a; }
            .oh-bg-gift { fill: #8c2d19; stroke: #a33b24; }
            .oh-bg-leaf { fill: #2a9d8f; stroke: #40916c; }
            .oh-bg-twist { fill: #242930; stroke: #59645f; }
            .oh-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .oh-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .oh-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .oh-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .oh-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .oh-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .oh-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="oh-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 核心舞台：曼哈顿四百万普通市民 -->
          <rect x="230" y="25" width="220" height="115" class="oh-box oh-bg-nyc" />
          <text x="340" y="52" class="oh-t-w">纽约‘四百万’小人物 (The 4 Million)</text>
          <text x="340" y="72" class="oh-t-sub-w">八美元周租公寓 · 穿风衣的流浪汉</text>
          <text x="340" y="90" class="oh-t-sub-w">售货女郎的微薄薪水 · 寒风中的尊严</text>
          <text x="340" y="108" class="oh-t-sub-w">在冷漠金钱森林中保持纯粹的善良</text>
          <text x="340" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">“人生是由啜泣、抽噎与微笑织成的”</text>

          <!-- 左侧名篇一：《麦琪的礼物》 -->
          <path d="M 230 82 L 160 82" class="oh-solid" stroke="#8c2d19" />
          <rect x="15" y="30" width="145" height="110" class="oh-box oh-bg-gift" />
          <text x="87" y="58" class="oh-t-w">《麦琪的礼物》</text>
          <text x="87" y="78" class="oh-t-sub-w">德拉剪掉及膝秀发</text>
          <text x="87" y="96" class="oh-t-sub-w">吉姆当掉传家金表</text>
          <text x="87" y="114" class="oh-t-sub-w">发梳与表链的错位</text>
          <text x="87" y="128" style="fill:#f0dcd8; font-size:9.5px; text-anchor:middle;">最贫困者的无上神圣富有</text>

          <!-- 右侧名篇二：《最后一片叶子》 -->
          <path d="M 450 82 L 520 82" class="oh-solid" stroke="#2a9d8f" />
          <rect x="520" y="30" width="145" height="110" class="oh-box oh-bg-leaf" />
          <text x="592" y="58" class="oh-t-w">《最后一片叶子》</text>
          <text x="592" y="78" class="oh-t-sub-w">琼珊数树叶等待死亡</text>
          <text x="592" y="96" class="oh-t-sub-w">贝尔曼风雨夜画假叶</text>
          <text x="592" y="114" class="oh-t-sub-w">救活生命，自身患肺炎死</text>
          <text x="592" y="128" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">留在潮湿砖墙上的真正杰作</text>

          <!-- 下方：欧·亨利式反转结构 -->
          <path d="M 340 140 L 340 200" class="oh-solid" marker-end="url(#oh-arr)" />
          <text x="385" y="175" class="oh-lbl">命运的神反转</text>

          <rect x="160" y="200" width="360" height="115" class="oh-box oh-bg-twist" />
          <text x="340" y="228" class="oh-t-w">欧·亨利式反转机制 (O. Henry Twist)</text>
          <text x="340" y="248" class="oh-t-sub-w">严密的误导伏笔 · 意料之外，情理之中</text>
          <text x="340" y="266" class="oh-t-sub-w">《二十年后》：老友重逢，警察挚友亲手逮捕通缉犯兄弟</text>
          <text x="340" y="284" class="oh-t-sub-w">《警察与赞美诗》：决心自新的一瞬，冰冷手铐当场落下</text>
          <text x="340" y="300" style="fill:#f0dcd8; font-size:10.5px; font-weight:700; text-anchor:middle;">在残酷荒谬的宿命弄巧中，守护人类未泯的善意火种</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色群像深度解剖</div>
      <ul class="bullet-list">
        <li><strong>德拉与吉姆（Della and Jim Young）：</strong>《麦琪的礼物》中相濡以沫的贫贱小夫妻。每周收入仅二十美元，除去八美元房租所剩无几。然而在圣洁的爱面前，他们展现了不可思议的慷慨：德拉站在镜子前看着自己像瀑布般倾泻的秀发，只犹豫了一秒钟，便跑到‘索弗罗妮夫人假发店’剪下换了二十块钱；而吉姆卖掉了祖父留给父亲、父亲留给自己的金表。当两人在破旧餐桌上摊开各自的礼物时，他们相对无言。欧·亨利把他们比作‘东方三博士（Magi）’，宣告了在爱面前，所有算盘计算全成废土。</li>
        <li><strong>老贝尔曼（Old Behrman）：</strong>《最后一片叶子》中脾气暴躁的老艺术家。六十多岁，长着摩西般的卷胡子，终日借酒消愁，一事无成。然而当得知年轻的女画家琼珊因肺炎心死、发誓‘当最后一片常春藤叶子掉光我也要死去’时，这位平日粗鲁凶煞的老头在黑夜暴雨中默默扛起梯子、灯笼与画笔，冒着刺骨冰雨在砖墙上勾勒出永远不会掉落的绿色叶脉。他用自己的生命完成了全人类艺术史上最伟大的杰作。</li>
        <li><strong>苏比（Soapy）：</strong>《警察与赞美诗》中幽默优雅的流浪汉哲学家。他有独特的自尊，看不起慈善收容所里那些借着施舍查户口、逼人洗澡的伪善；他只想安安静静在黑岛监狱度过三个月的寒冬。当他经历一系列失败，站在昏暗的古老教堂窗外听见赞美诗时，童年的纯洁回忆如闪电般劈开了他的麻木，他决心明天就去找工作重新当一个堂堂正正的人。然而命运的大手在这一秒无情按下了反转键。这种近乎残酷的黑色幽默，展现了小人物在荒诞社会面前的无力宿命。</li>
        <li><strong>吉米·瓦伦丁（Jimmy Valentine）：</strong>《改邪归正》中的保险箱飞贼之神。出狱后偶遇银行家之女一见钟情，从此隐姓埋名成为诚实鞋匠。然而当小女孩不慎被反锁进防盗绝密金库窒息垂危时，为了拯救生命，他在心爱的未婚妻和一直在暗中追捕他的老警探面前，平静地拿出了自己全套镀镍的窃贼作案工具，在众目睽睽下用高超技术切开了保险箱门，坦然等待手铐。老警探凝视着他，最终假装不认识他转身离去，完成了人性良知的崇高和解。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书收录了数十篇发生在一世纪初纽约曼哈顿街头、得克萨斯荒原与外省小镇的平民传奇。《麦琪的礼物》讲述一对贫穷小夫妻为了在圣诞节给对方赠送礼物，妻子剪发买表链，丈夫当表买发梳，双双以无私牺牲换来了两件无用却无价的深情信物。《最后一片叶子》讲述年轻女画家琼珊患重度肺炎病危，执迷于窗外常春藤叶落尽即是死期；隔壁老画家贝尔曼在风雨严寒之夜用画笔在砖墙上画下一片永不凋零的绿叶，用生命点燃了女孩的求生希望。《二十年后》讲述一对二十年前立誓重逢的挚友，一人如约守在昏暗门廊下，一人成为巡警暗中认出昔日好兄弟已成全美通缉的大盗，最终在职业正义与挚友私情之间，选择派便衣警察前去逮捕，留下一纸心碎字条。《警察与赞美诗》讲述流浪汉苏比为进监狱过冬屡次策划犯罪碰壁，最终在教堂圣乐感召立志自新的一瞬被警察捕入狱。《带家具出租的房间》讲述青年在全纽约廉价旅店疯狂寻找失踪的情人，最终在充满木犀草香气的破房间里开煤气自尽，殊不知一周前心上人正是在这张床上用同样的煤气结束了生命。每一篇故事短小精悍，如同曼哈顿夜空下的繁星，闪耀着世态的炎凉与人性的微澜。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“在资本主义金钱丛林与严酷荒谬的生存竞争中，生活在社会底层最不起眼的平民草根，如何依靠彼此之间微小的善意、牺牲、幽默与信守诺言，对抗命运无情的捉弄并维系人的神圣尊严”</strong>。欧·亨利证明：平凡人也许没有显赫的功名，但在生活的重压之下，他们灵魂深处绽放出的美德，远比上流名利场的珠光宝气纯洁万倍。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一杯在冬夜廉价咖啡馆里递上的苦咖啡中掺入的一勺粗砂糖：在一声声生活的无奈叹息与抽噎之后，猝不及防地被一抹意料之外的反转暖流击中眼眶，绽放出含泪的微笑。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个在大城市打拼挣扎、为了几两碎银奔波劳碌，在生活的残酷真相面前感到疲惫，渴望重新被朴素善意击中内心的普通人。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>底层小人物微薄生存资源的极度匮乏 vs 精神世界不计代价的慷慨牺牲；严酷冷漠的荒谬宿命捉弄 vs 偶发善意对绝望人生的微光救赎。</strong></p>

      <div class="sub-heading">全书四大母题模块推进链条</div>
      <ol class="num-list">
        <li><strong>第一板块 · 爱的错位与至圣牺牲（《麦琪的礼物》《最后一片叶子》）：</strong>匮乏中的倾囊相助，用看似荒唐的代价置换无价真情；死神与希望在艺术笔触下的终极拔河。</li>
        <li><strong>第二板块 · 宿命的反讽与黑色幽默（《警察与赞美诗》《带家具出租的房间》）：</strong>人类理性算计在命运无常面前的彻底失效；渴望犯罪而不得，立志从善遭逮捕；擦肩而过的死亡悲剧。</li>
        <li><strong>第三板块 · 罪恶与良知的救赎反转（《改邪归正》《二十年后》）：</strong>大盗面对纯洁生命时的弃恶从善；法律职责与兄弟私情在街灯下的痛苦割席。</li>
        <li><strong>第四板块 · 市井狡黠与西部狂想（《红毛酋长的赎金》《苹果树下的罗曼史》）：</strong>绑匪反被熊孩子折磨倒赔钱的爆笑狂欢，展现美国本土民间文学的粗粝幽默元气。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>《最后一片叶子》终盘苏艾向病愈琼珊道破真相的瞬间：</strong>‘亲爱的，看着窗外墙上的那片叶子吧。难道你没觉得奇怪吗？为什么风吹雨打它从来不动一下？那是贝尔曼的杰作啊——就在最后一片叶子落下的那个暴风雨之夜，他把它画在了那里！’那一秒钟，所有的伏笔瞬间咬合，严厉暴躁的老酒鬼在读者心中升华为舍命救人的圣徒。
      </div>"""

    sec05 = """      <div class="sub-heading">欧·亨利式反转（The O. Henry Twist）的叙事建筑学秘诀</div>
      <p>欧·亨利的结尾反转绝非胡编乱造的机械降神。他建立了极其精密的<strong>‘双重视角双轨并进法’</strong>：<br>
      作者在故事前半部分故意隐藏某一个关键视角（如《麦琪的礼物》中只写德拉卖头发的痛苦，完全不提吉姆在同一时间干什么；《二十年后》中故意让警察在街角先和通缉犯平静交谈二十分钟），借此引导读者产生单向思维惯性；然而在前文里，他又极其小心地埋下了大量符合逻辑的物理线索。当结尾两轨相撞引爆炸弹时，读者在惊呼‘意料之外’的同时，回头重读立刻发现‘完全在情理之中’。这种绝妙的结构工艺，奠定了世界短篇小说的典范黄金律。</p>

      <div class="sub-heading">‘含泪的微笑’：超越愤怒的慈悲世界观</div>
      <p>欧·亨利一生坎坷：早年丧母丧妻，因账目问题入狱服刑，晚年饱受糖尿病与酗酒折磨。然而在面对如此残忍的生活时，他笔下从不流露刻毒的愤世嫉俗。他把一切委屈化作了一声声温厚的自嘲与微笑。他爱纽约清晨倒垃圾的环卫工、爱柜台后面站了一整天脚踝肿胀的姑娘、爱坐在公园长椅上用旧报纸取暖的老汉。他的伟大在于他<strong>认清了生活的残酷本质之后，依然选择用文字给这些弱小者送去一丝尊严与希望</strong>。</p>"""

    sec06 = """      <div class="sub-heading">市民通俗语言与古典修辞并置的幽默美学</div>
      <p>欧·亨利善于运用一种<strong>奇妙的‘语言不协调反差幽默’</strong>。他经常用希腊神话、莎士比亚戏剧的崇高典故，来形容一个街头小贩或无赖混混的滑稽动作；他在短句与快节奏对话中穿插俚语，随后突然拔高至哲理箴言。这种语言风格既极度接地气，又散发着知识分子的风雅韵味，成为二十世纪美国通俗文学的最佳代言人。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>墙上的最后一片常春藤叶 (The Last Leaf)：</strong>全人类文学中最著名的希望符号。它不是大自然的植物，而是人类用颜料、画笔与生命在冰冷残酷现实中伪造出的‘信仰奇迹’。它证明了<strong>虚构的艺术能够打败物理上的死神</strong>。</li>
        <li><strong>发梳与表链 (The Combs and Watch Chain)：</strong>两件丧失了使用价值的定情信物。它们象征着<strong>超越一切商业等价交换原则之上的纯粹神圣奉献</strong>。</li>
        <li><strong>二十年前约定的街角门廊：</strong>冷风呼啸的五金店门口。它象征着<strong>时间流逝中个体道德选择的分道扬镳</strong>——有人坚守了法律的忠诚，有人滑向了犯罪的深渊，而两者的撞击构成了宿命最沉痛的叹息。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（都市传奇短篇故事汇编）：</strong>二十世纪初美国大都市与西部各色底层平民在困顿生活中的巧遇、误会、犯罪与反转大戏。<br>
        <strong>深层架构（命运无常与人道主义微光）：</strong>对现代商业社会金钱冷漠残酷本质的犀利剖析。揭示底层弱者在面对生活重压时，依靠牺牲、幽默与互助战胜绝望的心智自愈力量。<br>
        <strong>根本架构（生命的尊严与爱的无价性）：</strong>人类生存的真正意义不在于拥有多少物质财富或功名，而在于在逆境中依然能够保有为所爱之人付出一切的至高神圣性。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>美国文学界将每年评选的全美最佳短篇小说奖命名为‘欧·亨利奖（O. Henry Award）’（福克纳、海明威、塞林格皆曾获此殊荣）。它确立了世界短篇文学最核心的评价标准——短小精炼、直指人心、结构绝妙、饱含人道温情。欧·亨利是世界短篇小说长河中一座永远流淌着清冽甘泉的丰碑。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>欧·亨利笔下的曼哈顿小人物，正是今天大都市里每一个外卖骑手、格子间加班青年与合租房打工人的真实写照：<br>
      在大城市昂贵的房租面前，现代人常常感到自己的微不足道与窘迫；而在情人节或纪念日，多少年轻情侣在预算有限的尴尬中，依然想方设法给对方准备一份惊喜。《麦琪的礼物》告诉我们：不要为了物质的匮乏而自卑，两颗真心彼此珍惜的温度，远比任何昂贵的大牌奢侈品更值得骄傲。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的生活经历中，是否曾收到过某件‘外表并不昂贵、甚至不太实用，但里面装满了对方全部心意’的珍贵礼物？你当时是如何对待这份真诚的？</li>
        <li>当你遭遇连续倒霉的事情时，你倾向于像苏比那样怨天尤人自暴自弃，还是能学会用欧·亨利式的幽默自嘲给生活解解压？</li>
        <li>如果你的一个多年挚友走上了违背原则甚至违法的道路，在面对职业底线与私人交情时，你会像《二十年后》里的警察那样痛苦抉择吗？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“欧·亨利是短篇小说之神。一个穷妻子卖了长发给丈夫买表链，丈夫当了金表给妻子买发梳，两件礼物全废了，但他们拥有全世界最无价的爱；一个快病死的女画家看着窗外的树叶等死，老邻居在大雨夜把最后一片假叶画在墙上救了她，自己却冻死了。它告诉你：生活再苦，只要有人默默为你画下一片绿叶，你就值得好好活下去。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读世界短篇小说三巨匠之一欧·亨利的名作。他的故事大家都听过一个词叫‘欧·亨利式反转’，但这个反转背后，流淌的是全人类最温暖的眼泪。欧·亨利是个苦命人，坐过三年冤狱，他在牢房里看尽了人间的悲苦，出狱后混迹在纽约最底层的廉价小酒馆里。他最著名的两篇故事，每个人都该读一遍。第一篇是《麦琪的礼物》：一对穷夫妻，全家最值钱的宝贝只有两样——丈夫祖传的怀表，和妻子那一头瀑布般的绝美长发。圣诞节到了，妻子想给丈夫买一条配得上金表的白金链子，偷偷去理发店把一头长发卖了二十块钱；晚上丈夫回家看见短发的妻子愣住了，掏出了一套妻子渴望已久的带宝石的昂贵发梳——为了买这头发梳，他把金表当掉了！两个人看着对方手里的礼物，抱头痛哭又破涕为笑。在功利的世界看来，他们干了两件蠢事；但在欧·亨利眼里，他们是全天下最富有的圣徒。第二篇是《最后一片叶子》：年轻女画家得重感冒肺炎快死了，她看着窗外掉落的常春藤树叶，说‘等最后一片叶子掉光，我就要死了’。隔壁住着一个六十多岁的潦倒老画家贝尔曼，整天喝大酒骂人，一辈子想画杰作却没画出来。在狂风暴雨下大雪的冰冷黑夜里，老人扛着梯子和灯笼消失在院子里。第二天早晨，狂风过后，窗外墙上居然还孤零零挂着最后一片绿叶！女画家深受震撼，重新燃起了求生的意志，活了过来。但就在同一天，老画家贝尔曼被送进了医院，他在那个暴风雨夜在湿漉漉的砖墙上画下了那片永远不掉的叶子，衣服全湿透了，患急性肺炎去世。欧·亨利在故事最后揭开真相：那片叶子就是老画家一辈子想画的真正杰作！欧·亨利的伟大正在于此：他告诉每一个在苦海里挣扎的平凡人，生活或许充满了荒谬和耳光，但只要有人愿意为你剪下长发、为你画下一片绿叶，人间就依然值得我们含泪微笑。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “在这世间所有的送礼者与受礼者当中，唯有那些为了对方而甘愿牺牲自己最珍视之宝的人，才是最智慧的东方三博士。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界短篇小说巅峰四大必读神作</div>
      <ul class="bullet-list">
        <li><strong>必读第一篇 · 《麦琪的礼物》：</strong>全篇仅四千字，精读结尾夫妻对视摊开礼物的神圣瞬间，体会叙事经济学极限。</li>
        <li><strong>必读第二篇 · 《最后一片叶子》：</strong>精读窗前数叶子到终盘揭露贝尔曼画叶牺牲的催泪反转。</li>
        <li><strong>必读第三篇 · 《警察与赞美诗》：</strong>精读流浪汉苏比六次策划犯罪碰壁、在教堂乐声中立志自新却被逮捕的黑色幽默绝唱。</li>
        <li><strong>必读第四篇 · 《二十年后》：</strong>精读夜风中划亮火柴认出通缉犯兄弟、巡警写下便条转交逮捕的道德两难。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 礼物的价值评判：</strong>吉姆的发梳与德拉的表链在物理层面上全成了摆设，为什么欧·亨利却断言‘他们是全世界最聪明的人’？在现代商业社会的送礼文化中，这一洞见有何颠覆意义？
      </div>
      <div class="card-box">
        <strong>Q2 · 艺术的最高标准：</strong>老贝尔曼画在潮湿砖墙上的常春藤叶，在构图或技巧上未必能比得上卢浮宫的古典名画，为什么它却被称为‘无上杰作’？艺术的终极价值究竟是什么？
      </div>
      <div class="card-box">
        <strong>Q3 · 苏比的被捕宿命：</strong>《警察与赞美诗》中苏比在做坏事时警察全当没看见，一旦想要从善却立刻被捕，这种荒诞的情节安排揭示了法律与底层人之间怎样的荒谬关系？
      </div>
      <div class="card-box">
        <strong>Q4 · 巡警鲍勃的职业道德：</strong>在《二十年后》中，警察巡警如果当场私放了二十年前对自己有恩的通缉犯兄弟，他在道德上是否情有可原？他选择找便衣代为抓捕体现了他怎样的内心折磨？
      </div>
      <div class="card-box">
        <strong>Q5 · 欧·亨利式反转为何百看不厌？</strong>为什么读者在明知欧·亨利必有反转的前提下，每一次读到结尾依然会被深深震撼与感动？</div>"""

    sec13 = """      <div class="sub-heading">① 人际共情实践工具：“麦琪之礼真诚测试” (The Magi Empathy Audit)</div>
      <p><strong>适用场景：</strong>在准备为重要的人赠送生日礼物、纪念日礼物，或者在日常表达感谢时。<br>
      <strong>第一步（剔除面子）：</strong>把‘送这个东西能不能显得我有钱、能不能发朋友圈炫耀’的虚荣念头从脑海中彻底删去；<br>
      <strong>第二步（寻找对方的表链）：</strong>回忆对方在过去半年内，曾无意中流露出的某个真实的痛点、未竟的心愿或深藏的爱好；<br>
      <strong>第三步（倾注时间而非金钱）：</strong>附上一封你手写亲笔写下的感谢卡片，详细记录一个对方曾感动过你的微小细节。记住：在真爱面前，倾注心血的时间远胜过冰冷的支票。</p>

      <div class="sub-heading">② 现实观察实验：“城市门廊下的苏比视角”</div>
      <p>观察繁华商场或地铁口附近的一位拾荒老人或流浪者。观察过往路人投向他的眼神（是嫌弃、视若无睹还是微小的同情），尝试站在他的视角打量这栋充满暖气与奢侈品的玻璃大厦，体会欧·亨利笔下‘四百万纽约人’的阶级断层。</p>

      <div class="sub-heading">③ 极短篇反转仿写任务</div>
      <p>模仿欧·亨利‘前文布满合理误导、最后一句彻底反转’的结构技巧，写一篇五百字以内的微型短篇小说：以‘一个自以为在暗中观察小偷的便衣警察’为视角，结尾反转揭示‘真正的卧底与被保护者其实另有其人’（严密自洽、情理之中）。</p>"""

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

print("Round 12 deep O. Henry ready.")

def get_deep_life_on_mississippi():
    data = {
        "title_cn": "密西西比河上的生活",
        "title_en": "Life on the Mississippi",
        "author_cn": "马克·吐温",
        "author_en": "Mark Twain (Samuel Langhorne Clemens)",
        "sub_desc": "大河奔流的美国精神自传史诗 · 蒸汽轮船黄金时代的壮美画卷与逝去挽歌",
        "hero_quote": "把这条大河的每一处浅滩、暗礁、倒木与回流刻进脑髓；密西西比河不是一条简单的水道，而是一本永无止境的浩瀚大书，每一天都在翻开全新的篇章。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说巨匠</div><div class="spec-val">马克·吐温 (1835–1910)</div></div>
        <div class="spec-item"><div class="spec-label">出版年代</div><div class="spec-val">1883 年出版 / 自传体非虚构巅峰杰作</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">回忆录 / 历史地理散文长卷 / 讽刺纪实文学</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 30 万字 / 全六十章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身必读文化经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">工匠精神硬核淬炼与工业化抹平浪漫的挽歌反思</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《密西西比河上的生活》当成走马观花的‘大河旅游风光游记’。马克·吐温以其青年时期亲历四年领航员（Steamboat Pilot）的切肤经验，写下了一部极其硬核的<strong>专业技能淬炼史与时代挽歌</strong>。在书中，他深刻揭示了知识的双刃剑——当一个青年完全掌握了河流的每一处暗礁水文规律、成为受人膜拜的航道之王时，他却悲哀地发现，大河在他眼中永远丧失了最初那种纯真浪漫的诗意风光；而随后铁路时代的铁桥横跨，则以不可逆的商业速度将整个浪漫的轮船时代彻底送进了历史博物馆。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 严苛到近乎神经衰弱的‘引航员魔鬼学徒生涯’：</strong>第六至十三章。拜师老领航员比克斯比时，青年吐温必须在几个月内把从新奥尔良到圣路易斯一千两百英里航道上的每一道沙洲、每一个弯道、两岸每一棵大树在白天和黑夜甚至浓雾中的倒影全部背下来。师傅冷酷地逼问：‘如果你在黑夜里连这片回流都看不出，你凭什么把全船五百条人命交在你手里？’这是世界文学史上对‘专业主义精神（Professionalism）’最极致的赞歌。
      </div>
      <div class="card-box">
        <strong>② 航道之王在镀金时代的至高尊荣与绝对权力：</strong>在十九世纪五十年代的美国内陆，领航员不仅是技术工匠，更是拥有君王般待遇的传奇阶层——月薪高达二百五十美元（堪比今天数万美元）、不受船长管辖、手握全船生死大权。他们在甲板上叼着雪茄从容掌舵，两岸市镇万人涌上码头脱帽欢呼，展现了新大陆拓荒时代对真正技术大师的无上崇敬。
      </div>
      <div class="card-box">
        <strong>③ 二十一年后重访大河的沧海桑田与挽歌余响：</strong>全书后半部分。内战结束、年近半百的马克·吐温以著名作家身份重游旧地。然而，昔日桅樯如林的繁华码头已长满荒草，蒸汽轮船被密如蛛网的铁路线彻底挤垮，古老的领航员公会不复存在。吐温在铁桥下仰望呼啸而过的火车，发出了对技术进步与诗意消逝并存的深沉哲学沉思。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        1850至1880年代的美国中西部与南部。南北战争前后，蒸汽机轮船曾垄断密西西比大动脉，随后横贯大陆的联合太平洋铁路与钢铁大桥崛起，将粗粝的拓荒时代推入工业垄断文明。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .lm-box { rx: 8; stroke-width: 1.5; }
            .lm-bg-steamer { fill: #1d3557; stroke: #2a4d7a; }
            .lm-bg-railway { fill: #8c2d19; stroke: #a33b24; }
            .lm-bg-river { fill: #2a9d8f; stroke: #40916c; }
            .lm-bg-twain { fill: #242930; stroke: #59645f; }
            .lm-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .lm-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .lm-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .lm-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .lm-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .lm-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .lm-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="lm-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 时代一：蒸汽轮船黄金岁月 (浪漫与匠人) -->
          <rect x="20" y="25" width="210" height="115" class="lm-box lm-bg-steamer" />
          <text x="125" y="52" class="lm-t-w">蒸汽轮船时代 (1850s)</text>
          <text x="125" y="72" class="lm-t-sub-w">领港员掌控航道 · 绝对崇高权威</text>
          <text x="125" y="90" class="lm-t-sub-w">强记千英里暗礁水流 · 肉眼辨暗流</text>
          <text x="125" y="108" class="lm-t-sub-w">充满粗粝野性、幽默与拓荒浪漫</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">“大河的浪漫与诗意岁月”</text>

          <!-- 时代二：铁路与钢铁工业时代 (效率与消逝) -->
          <rect x="450" y="25" width="210" height="115" class="lm-box lm-bg-railway" />
          <text x="555" y="52" class="lm-t-w">铁路与商业大桥时代 (1880s)</text>
          <text x="555" y="72" class="lm-t-sub-w">铁桥横跨河面 · 火车呼啸飞驰</text>
          <text x="555" y="90" class="lm-t-sub-w">轮船航运破产 · 码头荒草丛生</text>
          <text x="555" y="108" class="lm-t-sub-w">速度消灭距离 · 浪漫让位效率</text>
          <text x="555" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">“随风而逝的大河神话”</text>

          <!-- 时代变迁箭头 -->
          <path d="M 230 82 L 450 82" class="lm-solid" marker-end="url(#lm-arr)" />
          <text x="340" y="74" class="lm-lbl">二十一年变迁 · 工业革命抹平浪漫</text>

          <!-- 核心枢纽：大河母体与马克·吐温 -->
          <rect x="235" y="135" width="210" height="75" class="lm-box lm-bg-river" />
          <text x="340" y="162" class="lm-t-w">密西西比大河 (The River)</text>
          <text x="340" y="180" class="lm-t-sub-w">一千两百英里奔腾水脉 · 美国精神之母</text>
          <text x="340" y="196" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">“水深两拃 (Mark Twain) 永恒名号”</text>

          <!-- 下方：知识的代价与启蒙成熟 -->
          <path d="M 340 210 L 340 245" class="lm-solid" stroke="#59645f" />
          <rect x="160" y="245" width="360" height="80" class="lm-box lm-bg-twain" />
          <text x="340" y="272" class="lm-t-w">知识的代价：诗意丧失与责任诞生</text>
          <text x="340" y="292" class="lm-t-sub-w">从看客的玫瑰色晚霞，到引航员眼中的暗礁警报</text>
          <text x="340" y="308" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">“在看懂大河全部残酷真相后，依然深沉地爱着它”</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色与时代见证谱系</div>
      <ul class="bullet-list">
        <li><strong>青年萨缪尔·克莱门斯（青年马克·吐温）：</strong>全书第一人称主角。从一个满脑子想当水手出风头的懵懂小市民少年，在暴躁严格的师傅比克斯比手下饱受打击折磨。他经历了记忆力被逼到极限、在漆黑暴雨夜独自掌舵吓出冷汗的磨砺，最终成长为能闭着眼睛凭借水流回声判断深浅的王牌领航员，为后来的文学创作积累了毕生最深厚的语汇与观察力。</li>
        <li><strong>霍勒斯·比克斯比船长（Horace Bixby）：</strong>大河上最令人敬畏的技术宗师。他目光如炬、脾气暴烈，但技术炉火纯青。面对青年吐温的盲目自信，他用最苛刻的黑夜盲航教学打碎其幻想；面对大难临头的急流暗礁，他展现出泰山崩于前而色不变的神级定力。他代表了未被官僚流水线破坏的老一代匠人对专业极致水准的神圣崇拜。</li>
        <li><strong>探水水手与大河劳动者群像：</strong>在船头手持铅锤绳、在风浪中声嘶力竭高喊水深口号的水手们——‘深四拃！深三拃！水深两拃（Mark Twain，代表十二英尺安全水深）！’正是这声口号，成为了作家终生荣耀的笔名。他们在烈日与严寒中拉缆绳、加煤块、清理倒木，展现了新大陆劳动阶级最粗粝坚忍的生命力。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书分为两大部分：前半部分是极其精彩生动的自传体回忆。在密苏里州汉尼拔小镇长大的少年萨缪尔，与全镇所有男孩一样，唯一的梦想就是成为一名威风凛凛的密西西比河轮船领航员。十九岁那年，他以五百美元学费拜传奇引航长比克斯比为师，开启了长达数年近乎残酷的学徒生涯。在狂暴复杂的大河上，他必须硬记一千二百英里间每一座城镇、每一个岛屿、每一处沙洲在不同枯水期与洪水期的位置变动，甚至要在伸手不见五指的大雾黑夜里凭两岸树林的微弱剪影分辨航道。在历经无数次被责骂、恐惧与挫败后，他终于拿到了领航员执照，成为月薪数百美元、受全河膜拜的王者。然而随着南北战争爆发，内河航运停摆，吐温被迫告别大河。后半部分发生在二十一年后，成为世界知名文学大师的马克·吐温以普通旅客身份化名重返密西西比河。他乘坐现代轮船从圣路易斯一路向南航行至新奥尔良，又转乘北上至明尼阿波利斯。他目睹了当年神气活现的领航员行会彻底被铁路线挤垮破产，两岸棉花城镇在大火与战争后衰落沉寂，古老的传奇轶事被现代机械效率无情抹平。吐温以充满欢笑、讽刺又夹杂着无尽怅惘的笔调，为这条流淌着全美国灵魂的大河写下了最深沉壮阔的史诗纪念册。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃探究的是<strong>“现代工业文明的发展在带来高效率与物质财富的同时，是如何不可避免地将传统手艺人身上的个性、浪漫、与大自然直接博弈的野性尊严彻底消解抹平”</strong>。吐温证明：技术进步是必然的，但人类必须清醒意识到我们为了这种进步究竟支付了何等巨大的文化与精神代价。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一艘在汽笛长鸣与飞溅浪花中劈波斩浪的巍峨明轮船：在粗犷豪迈的美式幽默欢笑声中，驶过千重险滩暗礁，最终在汽船时代的落日余晖中，为人类逝去的浪漫青春献上一曲深情的挽歌。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个渴望掌握一门硬核专业本领、经历过残酷学徒磨砺，在现代流水线社会的平庸中留恋传统手艺温度与大自然旷野之美的成年人。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>大自然变幻莫测、随时可能吞噬船只的狂野水势 vs 领航员依靠绝对严谨经验与意志建立的专业控制力；传统手艺浪漫时代 vs 工业流水线铁路时代的无情替代。</strong></p>

      <div class="sub-heading">全书双翼历史推进链条</div>
      <ol class="num-list">
        <li><strong>第一部分上 · 少年雄心与拜师学艺（第一至五章）：</strong>汉尼拔小镇的轮船狂热；码头汽笛响起时的全镇狂奔；拜师比克斯比立约，登上下行轮船。</li>
        <li><strong>第一部分中 · 记忆的魔鬼地狱训练（第六至九章）：</strong>强记十二个不同水位的暗礁形状；黑夜盲航险些撞山崖吓得魂飞魄散；比克斯比的当头棒喝。</li>
        <li><strong>第一部分下 · 航道之王与诗意代价（第十至二十章）：</strong>第九章著名的‘大河美感之丧失’哲学顿悟；建立领航员联合公会垄断航运；南北战争爆发大幕落下。</li>
        <li><strong>第二部分上 · 二十年后故地重游（第二十一至三十九章）：</strong>化名登船观察现代轮船；圣路易斯到新奥尔良的港口变迁；探访旧友，昔日风光大师沦为看更老人。</li>
        <li><strong>第二部分下 · 上游北巡与终极沉思（第四十至六十章）：</strong>从新奥尔良北上至双子城；两岸锯木业、铁路网与新市镇崛起；全书在回顾密西西比大河数百年地理沧桑的宏大叙事中落幕。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第九章‘大河美感之丧失（The Loss of a Book's Beauty）’：</strong>当青年吐温终于能准确读懂水面上的每一道波纹意味着水下有暗礁、每一抹红霞意味着起风变天时，他突然悲哀地发现：自己再也不能像普通乘客那样单纯欣赏晚霞倒映在波浪上的瑰丽诗意了。知识与经验赋予了他保全全船性命的专业本领，但也永远杀死了他眼中最初的那份无邪浪漫。
      </div>"""

    sec05 = """      <div class="sub-heading">比克斯比的教育学：把人逼到绝境的匠人传承</div>
      <p>第六章比克斯比故意整蛊吐温的桥段堪称教学经典：船行至一处看似极其险恶、实则水深万丈的安全航道时，比克斯比故意装出惊恐万状的样子走开，安排几个水手在甲板上大喊‘水深只剩一拃、快要触礁搁浅了！’可怜的吐温在舵轮前吓得浑身发抖、语无伦次，在绝望中下令倒车几乎把整艘船折断。比克斯比从容走回舵室，冷冷痛斥：‘你为什么要听别人的瞎嚷嚷？你明知道这里水深三十英尺！记住：哪怕全世界都在对你大喊大叫，只要你的罗盘和记忆是对的，你就必须像块石头一样站死在舵轮前！’这种在极度恐慌中淬炼绝对自信的教育，塑造了真正的大师风骨。</p>

      <div class="sub-heading">领航员公会：工会力量与资本博弈的早期标本</div>
      <p>第十五章详尽记录了美国历史上最早、最成功的行业工会——领航员互助会（Pilots' Benevolent Association）的建立史。领航员们通过互通水文暗号、拒绝为不雇佣工会会员的船主开船，硬生生逼得不可一世的轮船资本大亨们全盘下跪妥协，将工资提高到神话般的数字。吐温以充满自豪的口吻记录了工匠如何依靠对‘不可替代技术壁垒’的绝对垄断，在早期野蛮资本社会中为体力与脑力劳动者争得无上尊严。</p>"""

    sec06 = """      <div class="sub-heading">密苏里幽默吹牛（Tall Tales）与专业实证白描的杂糅文风</div>
      <p>马克·吐温确立了美国本土文学最鲜明的语言品格。他将美国西部边疆那些荒诞不经的吹牛狂欢（如一个人能从新奥尔良一路跳过墨西哥湾）、水手们粗俗响亮的詈骂，与极其严谨、精密的航海水文学记录天衣无缝地焊接在一起。文字充满爆发力、幽默感与大江大河的奔腾之势，彻底洗刷了欧洲老派英国文学的无病呻吟。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>两拃水深 (Mark Twain)：</strong>航海水手的安全水深探测口令。‘Mark’意为标记刻度，‘Twain’意为两拃（十二英尺安全水位）。它不仅是作家的笔名，更象征着<strong>在凶险人世险滩中，始终为生命探寻安全深流的清醒指引</strong>。</li>
        <li><strong>轮船舵楼 (The Pilot-House)：</strong>全船视野最高、四面玻璃环绕的指挥中枢。它象征着<strong>凡人凭借专业经验所能达到的最高掌控境界</strong>，在风雨迷雾中如同翱翔在浪涛之上的鹰巢。</li>
        <li><strong>横跨密西西比河的现代铁路大桥：</strong>全书后半段的核心工业意象。巨大的钢铁桥墩插入江心，桥上火车喷薄黑烟疾驰，给下方曾经神气活现的蒸汽明轮船投下巨大的阴影，象征<strong>工业效率对传统浪漫文明不可抗拒的历史换轨</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <p><strong>表层架构（水手生涯传奇回忆录）：</strong>一个美国青年从零基础学徒成长为一代王牌引航长，并在二十年后重访大河目睹时代变迁的非虚构纪实史诗。<br>
      <strong>深层架构（专业主义精神与成长的代价）：</strong>对炉火纯青技术淬炼史的至高赞歌。揭示一个人从天真走向成熟，必须以丧失部分感性诗意为代价，换取承担沉重生命责任的专业力量。<br>
      <strong>根本架构（文明形态的更迭与自然长存）：</strong>人类人造的机械帝国（轮船、铁路、城市）在历史长河中此起彼伏，而大河本身——这条变幻莫测、随时冲垮堤坝的古老大河，永远在按照自己的意志奔流入海，嘲弄着人类一切短暂的自大。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>海明威曾留下一句传世名言：“所有现代美国文学都来自马克·吐温的一本书，那就是《哈克贝利·费恩历险记》；但如果你不读《密西西比河上的生活》，你就永远无法理解马克·吐温是用何等厚重扎实的人生骨骼，孕育出了那条属于全人类的精神之河。”</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天我们在AI时代所经历的‘职业颠覆焦虑’，与当年蒸汽轮船领航员面对铁路崛起时的绝望一模一样：<br>
      一个耗费十年苦功练就一身屠龙绝技的资深专家，可能在一夜之间被一项全新的技术（如火车大桥、大语言模型）降维淘汰。《密西西比河上的生活》展现了一种最高级的成年人格局：不要像怨妇一样诅咒技术的进步，记录它、理解它、坦然面对它，因为时代的浪潮永远向前，唯有在浪潮中锤炼过的那份工匠尊严，将永载史册。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你目前的专业领域中，你是否拥有像当年领航员那样‘哪怕在黑夜大雾中依然能闭着眼睛辨别航道’的无可替代的硬核本领？</li>
        <li>当你掌握了越来越多的专业技能之后，你是否也像吐温一样，发现自己正在丧失对世界最初那种单纯热烈的好奇与惊叹？</li>
        <li>如果明天一项全新的颠覆性技术彻底淘汰了你赖以谋生的职业技能，你靠什么心态面对这种历史必然？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《密西西比河上的生活》是马克·吐温最硬核的人生自传。他花了几年时间把一千两百英里的暗礁水流全背下来，成了全美工资最高的王牌水手；然而二十年后回去，火车铁路把轮船全干趴下了，老水手全失业了。它告诉你：专业技能是立身之本，但谁也阻挡不了时代的大江大河奔涌向前。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊聊大文豪马克·吐温最硬核、最纯正的一部自传杰作——《密西西比河上的生活》。很多人知道他的笔名‘马克·吐温’，但很少有人知道这四个字到底是什么意思。原来，十九岁那年，他在密西西比河上当轮船水手学徒，船头负责测水深的人每次扔下铅锤，量到水深有十二英尺、轮船可以安全通行时，就会扯着嗓子大喊一声：‘Mark Twain（水深两拃）！’这个安全水深的口号，后来成了这位伟大作家的终生笔名。这本书的前半部分堪称人类历史上最严苛的‘魔鬼学徒受难记’。他的师傅是全河第一领航长比克斯比，脾气极度暴躁。小吐温一开始以为开船很简单，结果师傅逼他把一千两百英里航道上每一个沙洲、每一个弯道、甚至两岸每一棵长相奇怪的大树在白昼、黑夜和大雾里的形状全背下来！有一天半夜，师傅故意走开，水手在甲板上大喊‘要触礁了’，吐温吓得浑身发抖差点翻船。师傅走出来狠狠骂他：‘你明明知道水深三十尺，为什么别人一喊你就慌了？记住，全世界都在鬼叫，只要你的罗盘是对的，你就必须像块石头一样给我站死在舵轮前！’经历这番磨砺，吐温终于成了独当一面的大引航长，每个月拿几百美元巨款，在甲板上叼着雪茄受全河崇拜。但最深刻的在后半部分：南北战争爆发，航运中断，二十年后大作家吐温回乡重游，发现一切全变了——铁路修通了，钢铁大桥横跨江面，当年的王牌引航员们全失业成了看门老人，豪华轮船全成了烂木头。吐温看着呼啸而过的火车，没有哭天喊地，而是写下了这本充满敬畏与幽默的世纪挽歌。他告诉我们：工匠的本事能让你立足，但时代的巨浪不可阻挡；唯有看透了现实的残酷之后依然深爱大河，生命才算真正成熟。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “大河夺走了我的诗意，但赐予了我掌舵的双手；在生活的激流中，唯有那些真正读懂了暗礁险滩的人，才能把生命之舟稳稳驶向彼岸。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界非虚构地理散文巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第四至六章（拜师与夜航初体验）：</strong>精读比克斯比魔鬼教学法，感受一千两百英里航道记忆压力的惊心动魄。</li>
        <li><strong>必读第二场 · 第九章（大河美感之丧失）：</strong>世界散文史最著名的‘专业认知颠覆感性审美’的哲学沉思长卷。</li>
        <li><strong>必读第三场 · 第十五章（领航员公会垄断传奇）：</strong>精读工匠技术壁垒硬抗资本家的经典博弈，充满美式智慧幽默。</li>
        <li><strong>必读第四场 · 第二十一至二十二章（重访大河初遇新轮船）：</strong>精读二十年后重逢旧港口，在铁桥与浮华消逝中领悟时代变迁。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 审美的代价：</strong>吐温感叹掌握了水文知识后‘再也无法欣赏夕阳在水面上的美丽’，我们在现代教育中获得越来越多的科学理性时，是否也在不可避免地丧失对大自然的童真敬畏？
      </div>
      <div class="card-box">
        <strong>Q2 · 比克斯比的抗压训练：</strong>比克斯比故意制造恐慌环境考验学徒的心理素质，在现代企业培训与危机管理中具有怎样的参考价值？
      </div>
      <div class="card-box">
        <strong>Q3 · 技术淘汰的必然性：</strong>铁路彻底淘汰了轮船航运，带来了空前的物流速度与财富，为什么吐温在赞美这种进步的同时依然留下了深沉的伤感？
      </div>
      <div class="card-box">
        <strong>Q4 · 笔名的生命意义：</strong>为什么吐温功成名就后，始终坚持使用当年水手探水深时的口号‘Mark Twain’作为笔名？这个名字时刻在提醒他什么？
      </div>
      <div class="card-box">
        <strong>Q5 · 大河与美国性格：</strong>密西西比河变幻莫测、随时冲垮堤坝的暴烈天性，在多大程度上塑造了美国人冒险、不拘小节、实用主义的民族性格？
      </div>"""

    sec13 = """      <div class="sub-heading">① 技能深度沉淀工具：“比克斯比暗礁记忆模型” (The Pilot Mastery Protocol)</div>
      <p><strong>适用场景：</strong>在攻克一门难度极大、信息量极高、必须形成下意识肌肉反应的专业技能（如编程调试、复杂手术、航空驾驶、辩护质证）时。<br>
      <strong>第一步（找一千两百英里航道）：</strong>不要被庞大的知识体系吓退，把整门技能拆解为‘一百个必须无条件背熟的底层核心坐标’；<br>
      <strong>第二步（做黑夜盲航测试）：</strong>在完全关闭参考资料、甚至在充满外部干扰与噪音的压力环境下，强迫自己独立完成一次全流程实操模拟；<br>
      <strong>第三步（成为舵轮前的石头）：</strong>当遭遇突发意外危机时，坚决不盲从外界的恐慌喊叫，只相信自己经过千百次实操验证的底层逻辑，沉稳掌舵突破死结。</p>

      <div class="sub-heading">② 现实观察实验：“老工匠技能的消逝觉察”</div>
      <p>寻找城市街头一位正在坚持某种濒危传统手工（如修表师傅、手工弹棉花、磨刀木匠）的老人。观察他粗糙布满老茧的双手与全神贯注的眼神，体会大工业时代前人类凭借肉身技能与物理世界建立的深层神圣尊严。</p>

      <div class="sub-heading">③ 职业叙事仿写任务</div>
      <p>模仿第九章吐温描写‘专业视角如何取代外行看客浪漫幻想’的对比笔法，写一段关于‘某位从事特定专业工作的人（如医生、程序员、摄影师）在审视某个原本浪漫的日常场景时所产生的心境转变’（350字以内，既有技术深度又有哲思余响）。</p>"""

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

print("Round 12 deep Life on the Mississippi ready.")

def get_deep_time_travelers_wife():
    data = {
        "title_cn": "时间旅行者的妻子",
        "title_en": "The Time Traveler's Wife",
        "author_cn": "奥黛丽·尼芬格",
        "author_en": "Audrey Niffenegger",
        "sub_desc": "非线性时空下的深情绝唱 · 离散、等待与跨越维度的爱意守候史诗",
        "hero_quote": "我爱你，在时间的任何一个角落；即便我不在你身边，我的爱也从未离开过你哪怕一秒钟；等待，是我能给予你最深沉的陪伴。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家与造纸艺术家</div><div class="spec-val">奥黛丽·尼芬格 (1963– )</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">2003 年出版 / 全球畅销数千万册</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">软科幻爱情小说 / 现代存在主义小说</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 35 万字 / 全三部精密时间错位篇章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 青年与成人深读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">非线性叙事精巧度与接纳无常宿命之勇气</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《时间旅行者的妻子》当成一部‘主角带有时空穿梭特异功能的金手指浪漫言情爽剧’。尼芬格从第一页起就极其残忍地剥夺了全部科幻英雄主义光环——亨利患有的是严重的‘慢性时间错位症（Chrono-Impairment）’，这是一种由罕见基因缺陷导致的<strong>生理残疾与无法自愈的顽疾</strong>。他的穿越完全不可控，往往在压力爆发的瞬间被毫无预兆地抽离现实，赤身裸体被抛掷在风雪交加、充满野狗与陌生枪口的危险过去或未来；而克莱尔用一生漫长而孤独的等待，诠释了人类在冷酷无常的时空重力面前，最神圣的接纳、包容与长情。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 令人叹为观止的非线性双重视角时间拼图：</strong>女主角克莱尔的时间是绝对线性的（从6岁初遇、20岁重逢、30岁结婚到82岁白发苍苍）；而男主角亨利的时间则是支离破碎、前后乱跳的（6岁目睹母亲车祸、36岁穿越回草地给小女孩讲故事、43岁瘸腿断脚）。两人相遇在不同年龄段的交错，构成了世界文学史上最精密、最烧脑也最深情的结构建筑学。
      </div>
      <div class="card-box">
        <strong>② 极度真实的物理窘迫与生存本能白描：</strong>尼芬格绝不把时空穿梭浪漫化。因为不能带走任何物质，亨利每次降落时都是赤身裸体、牙齿打颤、胃里饥肠辘辘。为了生存，这位优雅的纽伯里图书馆图书管理员，在黑夜里不得不自学撬锁、偷衣服、翻垃圾箱、在街头逃避警察追捕。这种狼狈真实的物理负荷，赋予了故事无可比拟的凡人质感。
      </div>
      <div class="card-box">
        <strong>③ 预知死期下的英雄主义从容与白发终局：</strong>亨利提前数年穿越到未来，亲眼看见了自己将在四十三岁那年因穿越到冰天雪地被猎人误当作鹿开枪击中下肢截肢、最终中弹身亡。然而在确知死期的日子里，他没有自暴自弃，而是极其温柔地珍惜与克莱尔、女儿阿尔巴在一起的每一秒钟。全书结尾，八十二岁白发苍苍的克莱尔独坐窗前，终于等来了生命中最后一次穿越而来的年轻亨利，在暮光中完成了跨越一生的神圣重逢。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        1970年代至21世纪初的美国芝加哥与密歇根郊外大草地。现代都市生活节奏的破碎飞旋，与造纸艺术工坊沉静漫长的手工质感交织呼应。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tt-box { rx: 8; stroke-width: 1.5; }
            .tt-bg-henry { fill: #1d3557; stroke: #2a4d7a; }
            .tt-bg-clare { fill: #2a9d8f; stroke: #40916c; }
            .tt-bg-time { fill: #131619; stroke: #59645f; }
            .tt-bg-alba { fill: #8c2d19; stroke: #a33b24; }
            .tt-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tt-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tt-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tt-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tt-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .tt-gold { stroke: #2a9d8f; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .tt-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="tt-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 丈夫：亨利 (非线性流浪者) -->
          <rect x="20" y="25" width="210" height="115" class="tt-box tt-bg-henry" />
          <text x="125" y="52" class="tt-t-w">亨利·德坦伯 (Henry)</text>
          <text x="125" y="72" class="tt-t-sub-w">图书管理员 · 罕见基因缺陷</text>
          <text x="125" y="90" class="tt-t-sub-w">不自主跨越时空 · 赤身裸体求生</text>
          <text x="125" y="108" class="tt-t-sub-w">目睹母亲车祸却无力改变历史</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">在时间的狂乱洋流中全力游向克莱尔</text>

          <!-- 妻子：克莱尔 (线性守望者) -->
          <rect x="450" y="25" width="210" height="115" class="tt-box tt-bg-clare" />
          <text x="555" y="52" class="tt-t-w">克莱尔·阿布夏尔 (Clare)</text>
          <text x="555" y="72" class="tt-t-sub-w">手工造纸雕塑家 · 坚忍博爱</text>
          <text x="555" y="90" class="tt-t-sub-w">6岁草地初见36岁丈夫 · 终身等待</text>
          <text x="555" y="108" class="tt-t-sub-w">经历无数次流产与突然离别</text>
          <text x="555" y="124" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">“等待是我的全部职业” · 守候至白发</text>

          <!-- 时空穿梭纽带 -->
          <path d="M 230 82 L 450 82" class="tt-gold" />
          <text x="340" y="74" style="fill:#2a9d8f; font-size:11px; font-weight:700; text-anchor:middle;">时空错位交叉相遇 · 绝对羁绊</text>

          <!-- 下方：时间牢笼与新生的超越 -->
          <rect x="20" y="180" width="290" height="135" class="tt-box tt-bg-time" />
          <text x="165" y="208" class="tt-t-w">时间暴政：不可更改的过去与未来</text>
          <text x="165" y="228" class="tt-t-sub-w">无论穿越多少次，历史铁律坚不可摧</text>
          <text x="165" y="246" class="tt-t-sub-w">母亲必死在琴弦下 · 亨利必中弹于雪原</text>
          <text x="165" y="264" class="tt-t-sub-w">留在地上的空衣物：生命无常离开的具象</text>
          <text x="165" y="280" style="fill:#e0725b; font-size:10px; text-anchor:middle;">物理时空对凡人宿命的绝对统治</text>

          <!-- 女儿阿尔巴：进化的奇迹 -->
          <path d="M 310 245 L 370 245" class="tt-solid" marker-end="url(#tt-arr)" />
          <rect x="370" y="180" width="290" height="135" class="tt-box tt-bg-alba" />
          <text x="515" y="208" class="tt-t-w">女儿阿尔巴 (Alba) · 新生超越</text>
          <text x="515" y="228" class="tt-t-sub-w">克服基因缺陷，拥有自主穿梭控制力</text>
          <text x="515" y="246" class="tt-t-sub-w">在时空中抚平父亲的创伤</text>
          <text x="515" y="264" class="tt-t-sub-w">八十二岁窗前的白发重逢：爱战胜时间</text>
          <text x="515" y="280" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">生命在代际传承中终获神圣自由</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>亨利·德坦伯：</strong>世界科幻小说中最令人心碎的时空旅人。他并不是一个威风凛凛的穿越超级英雄，而是一个常年饱受时空痉挛折磨的病人。在他六岁那年，一辆货车切断了母亲小提琴家的喉咙，他在车祸前一秒被未来拉走幸存；此后数十年，他反复被迫穿越回那个惨烈的现场，却无论如何阻挡不了母亲的死。直到在草地上遇见年幼的克莱尔，他的漂泊生命才找到了唯一的‘引力锚桩’。他在四十三岁前夕平静接受截肢与死期，用最后一次穿越给克莱尔留下了永恒的拥抱。</li>
        <li><strong>克莱尔·阿布夏尔：</strong>拥有大理石般惊人精神耐受力的女雕塑家。她从小把大自己十几岁的‘林中亨利’当做唯一的守护神，并在日记里记录下他每一次降临的日期与留言。成年后重逢同龄亨利，她必须面对一个极其残酷的现实——此时的年轻亨利根本还不认识她！她甘愿承受漫长无期的等待、数次因时空基因缺陷引发的血腥流产、以及随时可能面临的死别。她用手工造纸一层层纤维在水中的缓慢沉淀，隐喻了自己如何用耐心把痛苦熬成艺术。</li>
        <li><strong>戈梅兹（Charisse & Gomez）：</strong>克莱尔的密友。在亨利频繁失踪的岁月里充当现实生活的依靠，见证了这桩非人婚姻背后的巨大精神消耗，构成了世俗理性对这桩超验爱情的冷峻审视。</li>
        <li><strong>阿尔巴（Alba）：</strong>全书奇迹的化身。亨利与克莱尔历经九死一生诞下的女儿。她同样遗传了时空穿梭基因，但在基因演化中展现出了进化的优越性——她不会突然失控晕厥，她能够清醒自主地选择停留的时空，成为了抚平父母两代人时空创伤的至高希望。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>居住在芝加哥的纽伯里图书馆古籍管理员亨利·德坦伯患有一种极其罕见的常染色体显性遗传病‘慢性时间错位症’。当遭遇情绪紧张或压力时，他的身体会在瞬间消失，不自主地穿越到过去或未来的不同时空节点，每次降落都赤身裸体必须依靠潜伏偷窃求生。在他二十八岁那年，一位二十岁的漂亮艺术系女大学生克莱尔·阿布夏尔走进图书馆，激动得热泪盈眶地喊出他的名字，而亨利此前从未见过她。克莱尔拿出一本厚厚的童年日记，向亨利讲述了一个惊人的秘密：在克莱尔六岁那年，三十六岁的亨利首次出现在她家密歇根大草地的树林旁，此后数年间断断续续穿越归来一百五十二次，陪伴她度过了整个孤独的少女时代，并在克莱尔十八岁时与之定下婚约。两人在现实中迅速相爱成婚，但婚姻生活却充满了常人无法想象的折磨：亨利随时会在晚宴、做爱、甚至婚礼现场瞬间凭空消失，只在地板上留下一堆空空的衣裤；克莱尔因为胎儿同样遗传了时间穿梭基因导致数次在子宫内穿梭流产，险些丧命。在医学专家肯德里克博士的协助下，克莱尔终于成功诞下女儿阿尔巴。然而随着年龄增长，亨利在一次穿越到零下二十度的芝加哥雪夜停车场时遭遇严重冻伤，双腿被迫高位截肢，丧失了在穿梭中逃跑奔跑的能力。亨利提前穿越预见到了自己将在四十三岁那年被克莱尔的兄长在冬猎时误当作雄鹿开枪击中。在那个注定的冬日早晨，亨利平静地穿戴整齐，在最后的倒计时中与全家相拥，随后穿越至雪地中弹，被送回原本时空的克莱尔怀抱中咽气身亡。伤心欲绝的克莱尔在亨利留下的告别信中得知：在遥远的未来，当她长到八十二岁时，年轻的亨利还会最后一次穿越回房间看望她。克莱尔在深爱中度过了余生漫长的四十余年孤独，在老年的炉火前迎来了那个永不磨灭的炽热拥抱。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃探究的是<strong>“人类在冷酷、无常、不可抗拒的时间单向重力法则面前，应当如何理解‘等待’与‘相聚’的真正分量”</strong>。尼芬格向全人类证明：所有的爱情本质上都是一场‘时间错位’——每个人都有自己的时钟，每个人都随时可能面临意外的分离与不可预期的永诀。唯有把当下的每一次相拥都当做此生的最后一次，爱才能战胜虚无，成为永恒的锚桩。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一枚被抛入无边宇宙黑洞的时钟齿轮：在一次次毫无预兆的冰冷离散与粉身碎骨中，见证一颗人类心脏如何用跨越一生的坚守，在时间的每一处缝隙里，紧紧抱住那个属于自己的神圣坐标。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾饱受异地恋分离之苦、经历过至亲突发离世而深陷自责，在时间的洪流中感到漂浮无依、渴望学会坚强守护承诺的成年读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>不可控制、粉碎一切常态生活的残酷非线性时空引力 vs 坚守单向度生命长跑、以爱意为唯一坐标的执着等待。</strong></p>

      <div class="sub-heading">全书非线性拼图推进链条</div>
      <ol class="num-list">
        <li><strong>第一部 · 命运的线头与初见（1977–1991）：</strong>六岁草地上的神秘毛毯怪客；二十八岁图书馆重逢；日记本里的时间坐标对照；两个不同时间轴的人在现实中确立爱情。</li>
        <li><strong>第二部上 · 婚姻的重量与血色空房（1992–1998）：</strong>婚礼前夕亨利穿越消失，四十一岁瘸腿亨利赶来替二十八岁的自己宣誓；多次流产的血色床榻；基因实验的艰难突破；阿尔巴降生。</li>
        <li><strong>第二部下 · 宿命预知与截肢悲歌（1999–2006）：</strong>亨利穿越到未来目睹阿尔巴十岁生活并得知自己死期；冬夜雪地穿越双腿深度冻伤截肢；坐上轮椅倒计时安排后事。</li>
        <li><strong>第三部 · 终局枪响与白发重逢（2006至未来）：</strong>新年之夜枪响身亡，死在克莱尔怀中；告别信启封：‘别在悲伤中挥霍一生，但要在八十二岁等我一次’；漫长四十载岁月；八十二岁老妪在窗前与三十五岁青年最后的永恒相拥。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>亨利在未来目睹自己十岁的女儿阿尔巴并获悉自己活不过四十三岁：</strong>当亨利穿越到十年后的学校，阿尔巴一眼认出了父亲，并平静地对他说出‘你已经去世五年了’的那一刻，全书的科幻悬念彻底转变为崇高的宿命接纳。亨利没有歇斯底里地试图改写历史，而是从此将全部精力用来在生命的最后时光里，给予克莱尔最坚固的爱。
      </div>"""

    sec05 = """      <div class="sub-heading">留在地板上的空衣物：现代离散最直观的视觉隐喻</div>
      <p>全书反复出现的最惊悚也最凄凉的视觉画面，是<strong>‘一堆毫无征兆突然垮塌在走廊、厨房或床上的空衣服’</strong>。亨利可以在上一秒还端着热咖啡跟你说话，下一秒人就凭空消失了，只留下一套还带着体温的衬衫和牛仔裤掉在木地板上。尼芬格运用这个细节，极其精准地外化了现代人类在面对疾病、意外猝死与离别时最真实的心理创伤——在这个充满不确定的世界上，任何深爱的人都可能在下一个转角毫无告别地离开我们，留下的只有空荡荡的房间与无法填满的缺憾。</p>

      <div class="sub-heading">造纸艺术的哲学隐喻：克莱尔的沉淀与自愈</div>
      <p>克莱尔的职业是全书最绝妙的象征隐喻。她是一名手工造纸艺术家。造纸是一项极其繁琐、需要巨大耐心与等待的手艺：把棉麻纤维泡烂、打浆、在水槽中一遍遍捞起、压干、晾晒。克莱尔在造纸工坊里整天挽着袖子浸泡在冷水里，这种把无形的等待转化为有形的纸张雕塑的过程，正是她抵抗内心孤独与疯狂的最强精神铠甲。她用自己的双手，把一生的空虚等待沉淀成了坚固不朽的艺术作品。</p>"""

    sec06 = """      <div class="sub-heading">双第一人称日记交叠与时间戳的现代主义文风</div>
      <p>全书的每一章开篇都严格标注了两个时间戳：【克莱尔（年龄），亨利（年龄），公历日期】。这种如同精密物理日志般的双第一人称交替独白，营造出一种极其真实、亲密且扣人心弦的临场感。语言细腻、多情、充满诗意，同时在描写医学抽血、肌肉冻伤、猎枪近距离射击时又极具法医学的冷静质感，开创了现代科幻爱情小说的至高境界。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>大草地与林间空地 (The Meadow)：</strong>克莱尔童年家园旁的辽阔草地。它象征着<strong>时间洋流中一个永恒不变的物理圣殿</strong>。无论亨利被时间的风暴甩到多么遥远的年代，只要他降落在这片草地上，他就知道自己已经回到了克莱尔身边。</li>
        <li><strong>克莱尔的手工纸张 (Handmade Paper)：</strong>白色的纤维浆料，在水中慢慢捞起、风干。它象征着<strong>克莱尔用一生漫长的等待与坚守，为颠沛流离的亨利筑起的坚固精神之巢</strong>。</li>
        <li><strong>阿尔巴的音乐：</strong>小女儿继承了祖母天才的小提琴基因。音乐跨越了语言与维度的阻隔，在时间的缝隙中奏响，象征<strong>爱与美的遗传力量最终超越了基因缺陷与死亡的冰冷枷锁</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（科幻时空罗曼史）：</strong>一个患有不可控时空穿梭基因缺陷的图书管理员，与一位用一生时间等待他的女雕塑家之间跨越维度的凄美爱情传奇。<br>
        <strong>深层架构（宿命与自由意志的哲学探讨）：</strong>对不可逆转的时间物理铁律的深刻解剖。证明过去无法更改、未来已然注定，人类真正的自由意志不在于妄图扭转历史，而在于在不可避免的苦难面前，选择以何种尊严与深情面对彼此。<br>
        <strong>根本架构（等待与相聚的存在主义本体论）：</strong>全人类亲密关系最本质的真相——一切相聚都是暂时的，一切深情都在走向离别；唯有全然接纳生命的不确定性，在拥抱时倾尽全力，等待才拥有照亮一生的崇高力量。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>美国著名文学评论界指出：《时间旅行者的妻子》虽然借用了科幻的时间旅行设定，但它在本质上是一部探讨‘身患绝症者的家庭生活’的现实主义沉思录。亨利的时间错位，可以被看作阿尔茨海默症、癌症晚期或严重战后创伤综合征的终极隐喻。它以最震撼的形式展现了一个女人在面对至爱之人的重疾与早逝时，所能展现出的最伟大的包容与韧性。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天的现代人生活在高度碎片化、流动性极强的异地奔波中：<br>
      伴侣常常因为出差、加班、异地派遣而陷入‘聚少离多’的常态，人际关系变得极其脆弱易碎。多少人在等待中失去了耐心，在猜忌中走散。《时间旅行者的妻子》给所有现代人注入了一剂深情强心针：如果克莱尔能在面对一百多次毫无音讯的突然失踪中坚守如一，我们在现实中面对微小的距离与等待时，是否也应当收起浮躁的抱怨，学会珍惜每一次来之不易的相聚？</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的亲密关系或友情中，当你面临长期的异地分离时，你是否能像克莱尔那样建立起独立充盈的自我世界，而不是把全部精力用来内耗猜忌？</li>
        <li>如果预先知道你深爱的人将在十年后因病过世，你是否有勇气依然选择与他相爱相守？</li>
        <li>在今天的日常生活中，当你与家人道别出门上班时，你是否能做到认真看着对方的眼睛说一声再见，而不是敷衍地盯着手里的手机屏幕？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《时间旅行者的妻子》是把时空穿越写得最让人心碎的神作。男主患有基因缺陷，随时会突然赤身裸体被甩到过去或未来；女主从六岁起就在草地里等他，等了一辈子，看着他中弹死去，守寡到八十二岁终于在窗前等来最后一次拥抱。它告诉你：生命里每一次拥抱都可能是最后一次，唯有拼尽全力去爱，时间才打不倒你。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读一部哭碎了全球几千万读者的科幻爱情巅峰——奥黛丽·尼芬格的《时间旅行者的妻子》。很多人一听书名，以为这是什么霸道总裁穿越时空的浪漫爽文。大错特错！这是一部极度残忍、也极度深情的存在主义受难史。男主角亨利是个图书管理员，但他有一种不可控制的基因绝症——随时随地，没有任何征兆，他就会从空气中消失，赤身裸体被扔在暴风雪或者危险的街头。为了活命，他必须学会撬锁偷衣服、在垃圾桶里翻吃的。而女主角克莱尔的时间是正常的。六岁那年，三十六岁的亨利突然光着身子出现在她家草地里，告诉她‘我是你未来的丈夫’。小女孩拿大衣给他穿，给他留巧克力，等了他整整十四年！二十岁那年，她在图书馆撞见了同龄的亨利，但这时候的亨利根本还不认识她！两个人终于结婚了，但生活是一场漫长的折磨：亨利随时会在做饭、甚至婚礼宣誓时突然消失，留下一堆还带着体温的衣服在地板上；克莱尔流产了无数次，因为孩子在肚子里也会穿越。好不容易生下女儿，亨利却提前穿越到未来，亲眼看见了自己将在四十三岁那年冬天中弹身亡！他没有逃，而是从容给全家人安排好一切，在截肢后坐着轮椅微笑着陪妻子过完了最后的岁月。在那个注定的冬夜，亨利中弹了，被送回原本的时空，死在克莱尔怀里。但最催人泪下的在最后：亨利在死前留了一封信，告诉克莱尔：‘别荒废一生，但八十二岁那年，请你坐在窗前等我，我会最后一次来看你。’克莱尔守着对他的爱，一个人做雕塑、抚养女儿，孤独地过了四十多年。全书最后一行，满头白发的老太太坐在夕阳下的窗前，房门被轻轻推开，三十多岁的亨利大步走进来，微笑着向她张开双臂。尼芬格用这部书告诉全人类：人生本质上就是一场时间错位，没有人能永远陪着你；但只要在相聚的每一秒钟倾尽全部真心，只要你敢于承担等待的重量，爱就能超越光年，战胜死神。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “我们不会因为死亡而真正分开；在每一个我曾经深深爱过你的时空褶皱里，我都依然在紧紧拥抱你。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：现代时空哲学长篇核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一部第一章（图书馆重逢与日记本）：</strong>精读二十岁克莱尔在古籍阅览室认出二十八岁亨利，两套时间轴首次碰撞的惊艳开场。</li>
        <li><strong>必读第二场 · 第一部第十五章（婚礼现场的替身宣誓）：</strong>精读四十一岁截肢亨利穿越回十年前替失踪的青年自己完成宣誓的神级结构反转。</li>
        <li><strong>必读第三场 · 第二部第二十章（未来与十岁阿尔巴相认）：</strong>精读亨利在音乐教室门前得知自己死期的至高宿命震撼。</li>
        <li><strong>必读第四场 · 第三部第二章（雪夜中弹死于怀中）：</strong>精读最后的冬日倒计时与穿越中弹后抱憾离世的绝美挽歌。</li>
        <li><strong>必读第五场 · 第三部尾声（八十二岁窗前白发重逢）：</strong>精读全书最后三页，体会跨越四十年生死大限的终极神圣相拥。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 宿命与预知的伦理悖论：</strong>亨利明知母亲会在车祸中惨死，穿越了无数次依然阻止不了悲剧发生；他预知了自己的死期，也同样无法逆转。在不可更改的时空铁律面前，‘预知未来’对人类而言究竟是恩赐还是残酷的折磨？
      </div>
      <div class="card-box">
        <strong>Q2 · 克莱尔的选择值得吗？</strong>克莱尔用整整四十年的孤独守候去换取八十二岁窗前那短短几分钟的最后重逢，在世俗的幸福经济学看来是极度不划算的，但为什么全球读者为这份坚守流下眼泪？
      </div>
      <div class="card-box">
        <strong>Q3 · 现代爱情的耐受力测试：</strong>在离婚率飙升、‘即时满足’横行的现代快餐文化中，《时间旅行者的妻子》所展现的这种坚忍不拔的‘等待美学’，给现代人提供了怎样的解毒剂？
      </div>
      <div class="card-box">
        <strong>Q4 · 空衣物的象征力量：</strong>为什么每次亨利穿越离开时，作者都要特意描写留在地板上的那堆空衣服？这个视觉细节在传达人类‘失去至亲’的心理创伤时具有怎样的震撼力？
      </div>
      <div class="card-box">
        <strong>Q5 · 终局重逢的诗学神韵：</strong>全书最后让年轻力壮的亨利与八十二岁满脸皱纹的克莱尔相拥，打破了世俗对‘青年男女完美肉身结合’的肤浅审美，传达了关于爱与灵魂怎样的崇高升华？
      </div>"""

    sec13 = """      <div class="sub-heading">① 亲密关系珍视工具：“时间旅行者告别自省法” (The Time-Travel Farewell Protocol)</div>
      <p><strong>适用场景：</strong>在每天清晨与伴侣/家人告别、或者在出差异地前感到琐事烦躁想要敷衍了事时。<br>
      <strong>第一步（假设空衣物）：</strong>在关门的一瞬间，假设自己就像亨利一样，下一秒可能因为突发的意外或变故被拉入遥远的时空、数个月乃至数年无法再见眼前这个人；<br>
      <strong>第二步（给一个全神贯注的凝视）：</strong>转过身来，认真注视对方的眼睛五秒钟，给一个坚实的拥抱，说一句温暖真挚的话语；<br>
      <strong>第三步（把日常当奇迹）：</strong>在心里确认：能够平安坐在一起吃一顿晚餐、能够晚上躺在同一张床上听见彼此的呼吸，这本身就是宇宙中千载难逢的奇迹，绝不为鸡毛蒜皮的琐事挥霍任何一秒钟。</p>

      <div class="sub-heading">② 现实观察实验：“生活中的碎片时间日志”</div>
      <p>记录你昨天一天中，由于‘等待（等电梯、等红灯、等外卖、等回复）’所消耗的碎片时间总和。观察你在等待时表现出的焦躁与不耐烦，反思自己是否在现代效率至上的压迫下，丧失了克莱尔式‘在等待中沉淀心智’的从容能力。</p>

      <div class="sub-heading">③ 非线性时空书信仿写任务</div>
      <p>模仿亨利在死前留给八十二岁克莱尔的那封遗书风格，写一封‘穿越四十年时空、致四十年前或四十年后的自己/挚爱’的深情短笺（350字以内，包含具体年龄对比与超越生死的坦荡祝福）。</p>"""

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
    print("=== 开始批量写入第 12 轮（欧亨利短篇小说、密西西比河上的生活、时间旅行者的妻子） ===")
    plan = [
        ("欧亨利短篇小说", get_deep_o_henry),
        ("密西西比河上的生活", get_deep_life_on_mississippi),
        ("时间旅行者的妻子", get_deep_time_travelers_wife),
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
