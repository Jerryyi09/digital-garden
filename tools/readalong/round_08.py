# -*- coding: utf-8 -*-
"""
Round 08: The Good Earth, The Great Gatsby, The Catcher in the Rye (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_the_good_earth():
    data = {
        "title_cn": "大地",
        "title_en": "The Good Earth",
        "author_cn": "赛珍珠",
        "author_en": "Pearl S. Buck",
        "sub_desc": "诺贝尔文学奖传世史诗 · 华夏农耕文明灵魂与土地周期的雄浑长卷",
        "hero_quote": "只要我们还守着土地，我们就永远不会灭亡；从泥土里出来，最终还要回到泥土里去。如果失去土地，一切繁华都不过是风中的败叶！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">赛珍珠 (1892–1973)</div></div>
        <div class="spec-item"><div class="spec-label">出版与荣誉</div><div class="spec-val">1931年出版 / 获普利策奖与诺贝尔奖</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">家族乡土史诗 / 跨文化人类学经典</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 26 万字 / 全三十四章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身必读寻根经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">农耕生存伦理与暴富后脱离土地必然衰亡规律</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿带着‘西方传教士居高临下猎奇旧中国’的刻板眼光阅读。赛珍珠四个月大即随父母来到中国，在江苏镇江与江南农村度过了近四十年岁月，中文被她视为第一母语。她以极其深沉的敬畏、挚爱与同理心，写活了中国传统农民面对水旱蝗灾、兵燹土匪时如野草般的坚韧生命力，更精准提炼出了中国几千年来宗族由‘躬耕起家’到‘脱离土地败亡’的残酷历史周期律。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 王龙与阿兰在春风中并肩耕作的农耕神圣画卷：</strong>新婚清晨，两人各执一把锄头，在沉默中一寸寸翻开苏北平原黝黑肥沃的泥土。他们不说话，只有锄头入土的钝响、泥土散发的甜腥气与粗重的喘息。这种人与土地血脉交融的朴素劳作，构成了全书最神圣的生命基石。
      </div>
      <div class="card-box">
        <strong>② 饥荒绝境中‘宁死绝不卖地’的宗族骨气：</strong>大旱连年，村庄人相食，乡邻为了一升杂粮不得不变卖田产；王龙全家吞咽观音土、煮食老牛，在饿死边缘依然死守地契。王龙抓起一把干土嘶吼：‘卖了地，我们就成了乞丐！只要地还在，雨水一下，我们就还是这块大地的主人！’
      </div>
      <div class="card-box">
        <strong>③ 全书结尾两代人对待泥土的绝妙历史讽刺：</strong>垂死的老王龙坐在田埂上，双手颤抖着抓起一把黑土老泪纵横，喃喃告诫儿子们‘绝不能卖地’；然而站在身后的两个儿子相视一笑，早已在私底下背着父亲盘算好了把田地瓜分变现、迁往上海繁华租界做寓公的账目。家族由兴而衰的循环，在这一抹笑容中拉开序幕。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        清末民初至北伐战争前夕的中国江淮平原。古老的农耕自给自足体系，在军阀混战、近代商业投机与天灾频发的大时代裂隙中，经历着剧烈的文明蜕变阵痛。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .ge-box { rx: 8; stroke-width: 1.5; }
            .ge-bg-wang { fill: #1d3557; stroke: #2a4d7a; }
            .ge-bg-olan { fill: #2a9d8f; stroke: #40916c; }
            .ge-bg-earth { fill: #8c2d19; stroke: #a33b24; }
            .ge-bg-sons { fill: #242930; stroke: #59645f; }
            .ge-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ge-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ge-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ge-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ge-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .ge-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="ge-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 丈夫：王龙 -->
          <rect x="20" y="25" width="210" height="115" class="ge-box ge-bg-wang" />
          <text x="125" y="52" class="ge-t-w">王龙 (Wang Lung)</text>
          <text x="125" y="72" class="ge-t-sub-w">勤俭起家 · 敬畏泥土神明</text>
          <text x="125" y="90" class="ge-t-sub-w">饥荒中死守地契 · 荒年抄底兼并</text>
          <text x="125" y="108" class="ge-t-sub-w">暴富后纳妾娶梨花，晚年困于子孙异化</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">大地之子由朴素到衰老的史诗</text>

          <!-- 妻子：阿兰 (大地的具象化身) -->
          <rect x="450" y="25" width="210" height="115" class="ge-box ge-bg-olan" />
          <text x="555" y="52" class="ge-t-w">阿兰 (O-lan)</text>
          <text x="555" y="72" class="ge-t-sub-w">黄府脱籍粗使丫鬟 · 沉默坚忍</text>
          <text x="555" y="90" class="ge-t-sub-w">产子后立即下地 · 战乱中掏出珠宝</text>
          <text x="555" y="108" class="ge-t-sub-w">被夺走两颗珍珠无声饮泣</text>
          <text x="555" y="124" style="fill:#d8f3dc; font-size:10px; font-weight:700; text-anchor:middle;">华夏土地之母的最圣洁化身</text>

          <!-- 夫妻共耕纽带 -->
          <path d="M 230 82 L 450 82" class="ge-solid" stroke="#2a9d8f" stroke-dasharray="4,4" />
          <text x="340" y="74" style="fill:#2a9d8f; font-size:11px; font-weight:700; text-anchor:middle;">并肩躬耕 · 奠定万代家业</text>

          <!-- 下方核心枢纽：大地黑土 -->
          <rect x="235" y="135" width="210" height="75" class="ge-box ge-bg-earth" />
          <text x="340" y="162" class="ge-t-w">大地母体 (The Earth)</text>
          <text x="340" y="180" class="ge-t-sub-w">生存源泉 · 财富根本 · 祖先归宿</text>
          <text x="340" y="196" style="fill:#f0dcd8; font-size:9.5px; text-anchor:middle;">“谁离开土地，谁就自取灭亡”</text>

          <!-- 第二代腐化危机 -->
          <path d="M 340 210 L 340 245" class="ge-solid" marker-end="url(#ge-arr)" />
          <rect x="160" y="245" width="360" height="80" class="ge-box ge-bg-sons" />
          <text x="340" y="272" class="ge-t-w">第二代与第三代：离开土地的溃败</text>
          <text x="340" y="292" class="ge-t-sub-w">大儿子好大喜功做官 · 二儿子投机经商 · 小儿子当兵造反</text>
          <text x="340" y="308" style="fill:#e0725b; font-size:10px; font-weight:700; text-anchor:middle;">老父未断气，儿子已在暗中计议卖地分钱</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>王龙：</strong>从挑水做饭的贫寒光棍，成长为富甲一方的大地主。他敬畏土地神庙里的两尊泥塑菩萨，每次丰收都要给泥菩萨换上新红袍；他抠门、坚韧、勤劳，能吃下常人无法承受的苦难。然而财富也腐蚀了他——当他在城里看见小脚女人的白皙脚踝时，开始嫌弃陪伴自己白手起家的阿兰‘脚大粗笨’，纳妓女莲花为妾，引发家庭内耗。但他骨子里始终是泥土的儿子，到了晚年，他抛弃了大宅的争斗，搬回当年的土胚老屋安度余生。</li>
        <li><strong>阿兰：</strong>中国文学史上最深沉、最伟大的母亲形象。她长相丑陋，生来就因脚大被父母卖进黄府当奴婢。嫁给王龙后，她几乎不讲废话，在冰天雪地里独自生下孩子，咬断脐带洗干净包裹好，下午就若无其事地下地干活。在全家逃荒南方的暴乱中，凭借当年在豪门当差的见识，敏锐地从富豪空宅暗壁中抠出一大把珠宝，奠定了王龙回乡买地的全部本金。然而当王龙为了讨好小妾莲花，硬生生从她发间抢走她唯一舍不得变卖的两颗白珍珠时，她只是默默流下一行浑浊的眼泪。她的死，抽走了王龙家族真正的主心骨。</li>
        <li><strong>王龙的儿子们：</strong>农耕文明向近代城市堕落的活标本。大儿子读书考功名，满脑子都是摆阔、讲排场，花巨资迎娶大户小姐；二儿子精于算计、斤斤计较，成为唯利是图的粮商；小儿子性情暴烈，厌恶土地，最终离家出走当了军阀大兵。他们没有一人愿意把手插进泥土里，预示着这个庞大家族必将重蹈当年黄府破产败亡的覆辙。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>贫农王龙在结婚当天，从城里黄府领回了粗使大脚丫鬟阿兰。夫妻二人克勤克俭，并肩在黑土地里刨食，迎来一茬茬丰收，生下健康的儿女。不久天降大旱，淮北平原寸草不生，王龙忍痛杀掉耕牛，全家挤上南下的闷罐难民列车逃荒至南方大都市（南京），在城墙根下搭棚栖身。王龙靠拉黄包车度日，阿兰带孩子们沿街乞讨，饱尝大城市的繁华冷漠。南方革命战乱爆发，底层群众抢劫富豪公馆，阿兰凭借在旧豪门服役的经验摸出藏在暗壁里的珍宝。王龙全家携巨款返回故乡，此时故乡百姓死绝、土地荒芜，王龙趁机买下破产黄府的千亩良田，一跃成为全县最大的地主大户。随后黄河发大水，富足闲暇的王龙开始流连茶馆，迷恋上娇小裹足的歌妓莲花并娶为偏房，强行夺走阿兰私藏的两颗珍珠送给小妾，重伤了阿兰的心。阿兰操劳成疾、在病榻上安详离世，王龙愧悔交加为其举行盛大安葬。晚年的王龙搬进黄府旧宅安享尊荣，然而儿孙们骄奢淫逸、内讧不断。年逾古稀的老王龙搬回起家的土屋，在两个儿子的搀扶下抚摸着脚下的黑土，哀求他们千万不要卖地；然而两个儿子相视冷笑，早已在暗地里商量好了把良田换成金条的败家计划。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类生命力与泥土大地的共生法则，以及财富积累后脱离体力劳动必然滋生骄奢败亡的永恒历史宿命”</strong>。赛珍珠向西方乃至全人类证明：中国农民对土地的执着不是落后愚昧，而是古老东方文明赖以繁衍五千年未曾断绝的至高生命哲学。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一尊伫立在风霜雨雪中的黄土雕像：在麦浪翻滚与饥荒蝗灾的交替翻覆中，见证人性的坚韧、贪婪、深情与背叛，最终全部归宿于大地母亲沉静宽容的怀抱。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个在大城市快节奏中丧失了土地根基、精神浮躁飘忽，渴望重新汲取粗粝扎实的生命定力的大众读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>守卫土地、勤劳克俭的农耕自然伦理 vs 城市商品经济诱发的消费享乐与脱离劳动的家族腐化宿命。</strong></p>

      <div class="sub-heading">全书四大阶段推进链条</div>
      <ol class="num-list">
        <li><strong>第一阶段 · 泥土播种与起家（第一至八章）：</strong>从黄府领回新娘；并肩躬耕收获麦浪；银钱藏进泥墙缝隙；黄府首度衰落割地卖田，王龙买下第一块祖业之外的土地。</li>
        <li><strong>第二阶段 · 荒年逃荒与南国淘宝（第九至十四章）：</strong>连年大旱人相食，吞咽观音土；杀死忠诚老牛痛哭；全家南下寄居城墙脚下拉车乞讨；革命战乱爆发，阿兰在富豪空宅暗壁摸得整包珠宝。</li>
        <li><strong>第三阶段 · 兼并黄府与移情纳妾（第十五至二十五章）：</strong>衣锦还乡大举买地；洪水泛滥无事生非；茶馆纳妾莲花，抢夺阿兰发间两颗珍珠；阿兰病重离世盛大下葬，王龙深悔断肠。</li>
        <li><strong>第四阶段 · 家族溃败与终极宿命（第二十六至三十四章）：</strong>迁入黄府故宅成为老爷；大儿子好大喜功、二儿子经商算计、三儿子弃田从戎；老王龙回土屋抚摸黑土哀求，儿子们暗中商量卖地，全书在冰冷的循环警钟中落幕。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第十四章南方战乱中阿兰摸得珠宝：</strong>如果没有这袋意外的财宝，王龙全家充其量只能成为一个靠血汗苦熬自耕的小自耕农；正是这笔天降横财，使王龙瞬间跨越了阶层成为大庄园主，也正是从这一刻起，当年导致黄府败落的寄生、纳妾、儿孙不肖的腐化毒素，正式注入了王龙家族的血液之中。
      </div>"""

    sec05 = """      <div class="sub-heading">阿兰的两颗珍珠：中国传统劳动女性无声的尊严血泪</div>
      <p>全书最具情感穿透力的细节，是阿兰藏在胸口的两颗珍珠。阿兰把摸到的满袋钻石红宝全交给了丈夫去买地，唯独留下两颗小小的白珍珠，缝在贴身棉袄的夹层里。她不识字，也不懂首饰，她只是想在漫长苦难的人生中，拥有一两样‘纯粹属于美丽、属于自己’的东西。然而当王龙被小妾莲花缠得不耐烦时，粗暴地扯开阿兰的衣襟抢走了珍珠。阿兰没有大吵大闹，只是默默闭上双眼，眼泪顺着满是风霜皱纹的脸庞滑落。这一刻，赛珍珠写尽了封建男权宗法制度对底层劳动女性最残酷的感情掠夺。</p>

      <div class="sub-heading">土地神庙的红袍变迁：中国民间信仰的极度务实性</div>
      <p>王龙对田头小小泥菩萨的供奉极具民俗学深度：风调雨顺发了财，他就去镇上买红纸给泥菩萨穿新衣、点香叩头；遇到大旱灾全家快饿死时，他路过土地庙不仅不拜，反而狠狠冲泥菩萨吐唾沫、骂它们‘吃白食不管人间死活’。赛珍珠敏锐地抓住了中国民间信仰的核心特征——<strong>它不是西方超越性的形而上敬畏，而是一种极其务实的‘互惠契约’</strong>。唯有脚下厚实的黑土地，才是农民心中唯一永恒不变的真神。</p>"""

    sec06 = """      <div class="sub-heading">圣经钦定本与中国古典话本相融的雄浑文风</div>
      <p>赛珍珠的英语文风极其独特。她完全模仿《圣经·创世纪》与中国《水浒传》的句式结构：大量使用以连词‘And（并且、于是）’开头的简洁并列长句，剔除一切华而不实的现代俚语，赋予全书一种如同古老羊皮卷般的史诗质感与黄土地的原始呼吸感。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>厚重的黑土 (The Dark Earth)：</strong>全书神圣的母体。它包容一切粪便、死尸与汗水，回馈以金黄的麦浪与高粱。离开它，人就会变成无根的浮萍与寄生虫。</li>
        <li><strong>阿兰的大脚与莲花的三寸金莲：</strong>全书两极对立的女性身体隐喻。阿兰的大脚代表<strong>扎根大地、勤劳健壮的真正生命力量</strong>；而莲花裹得畸形的金莲，则代表<strong>封建男权病态审美与寄生消费主义的腐朽毒疽</strong>。</li>
        <li><strong>黄府旧宅的鸦片榻与枯井：</strong>象征封建世家不可逃脱的历史沉沦周期律。当王龙家族搬进这座宅邸时，命运的轮盘就已经宣告了相同的败亡终局。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（乡土家族史诗）：</strong>清末民初中国北方农民由一贫如洗依靠勤劳土地起家，历经荒年逃荒发财兼并，最终晚年儿孙谋划卖田的家族荣辱大戏。<br>
        <strong>深层架构（农耕伦理与现代化冲击）：</strong>中国农业文明五千年深厚生存智慧的完整提炼。揭示土地是一切繁荣与道德的源头，脱离体力劳动是家族衰落的不可逆开端。<br>
        <strong>根本架构（人与大地的永恒契约）：</strong>人类文明无论发展到何等科技高度，在肉体与本质上依然是泥土的产物；违背自然节律与大地法则，必然招致文明的自我湮灭。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>1938年瑞典文学院授予赛珍珠诺贝尔文学奖时评价：“她对中国农民生活进行了极其丰富、真实而雄浑的史诗性描述，跨越了东西方文化的无形鸿沟，树立了一座沟通全人类心灵的里程碑。”《大地》是西方世界第一部彻底洗刷对华人‘傅满洲式妖魔化偏见’、以崇高人道主义平视中国人民的传世巨作。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天远离土地、居住在水泥森林里的现代都市人，普遍患有‘大自然缺失症’与‘根基焦虑症’：<br>
      我们在虚拟的金融报表、股票代码与社交网络点赞中消耗生命，却对身边一棵麦子的灌浆、一棵树的落叶毫无知觉。当经济周期下行、资产泡沫破裂时，现代人内心的惊恐与虚无，正如当年黄府那些失去了土地的大少爷们一样无助。《大地》提醒我们：无论时代怎么变，守住一份踏实做事的本领与对大地的敬畏，才是抵抗时代风浪最深厚的底牌。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的家庭中，祖辈父辈曾依靠怎样的节俭与血汗为你铺平了今天的台阶？你是否曾因为某种虚荣而嫌弃过他们的朴素与‘不够体面’？</li>
        <li>当你获得了一定的金钱财富之后，你是否也曾像发财后的王龙一样，开始滋生出对物质享受的傲慢，甚至伤害了当年陪你一起吃苦的伙伴？</li>
        <li>如果现代社会的虚拟金融与技术服务在一瞬间失灵，你身上还有哪一项能够直接生产生活必需品的硬核本领？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《大地》是唯一一部写透了中国土地之魂的诺贝尔奖巨作。一个穷光蛋农民娶了丑丫鬟，靠一块块买地发家成了全县首富。但富贵之后儿子们却嫌泥土太脏，暗中商量卖地进城。它告诉你：土地是所有财富的母亲；什么时候你瞧不起脚下的泥土了，什么时候你的败亡就开始了。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊一部写透了中国人骨髓的传世经典——赛珍珠的《大地》。很多人不知道，赛珍珠虽然是美国人，但在中国生活了近四十年，她的第一母语就是中文。她以极其深情的笔触，写活了一个中国农民王龙的一生。王龙一开始穷得连媳妇都娶不起，从城里大户黄府领回了一个粗手大脚的丫鬟阿兰。阿兰不爱说话，但坚韧如铁，生完孩子当天下午就下地干活，两个人硬是在黑土地里刨出了一份家业。大旱之年全家饿得吃观音土，王龙宁死不肯卖地，带着一家老小逃荒去南方城里拉黄包车。后来遇上战乱，阿兰在富豪空宅暗壁里掏出一大袋珠宝，王龙回乡趁低价兼并了当年那个高不可攀的黄府的全部土地，一下子成了大财主。然而，发了财的王龙变了。他开始嫌弃阿兰脚大难看，去茶馆娶了娇小的歌妓莲花，甚至硬生生抢走阿兰贴身藏着的两颗心爱珍珠送给小妾。阿兰积劳成疾去世，王龙悔恨痛哭。到了晚年，王龙搬进黄府旧宅，儿女们不仅不愿种田，反而内讧争产。小说最后一段堪称绝唱：年迈的老王龙搬回当年起家的土屋，颤抖着抓起一把黑土，哀求两个儿子：‘只要守着地，咱们就饿不死，千万别卖地啊！’然而站在他背后的两个儿子相视冷笑，早就把卖地的契约盘算好了。赛珍珠借这本书向全世界揭示了一个真理：土地不仅是粮食的来源，更是一个家族道德与生机的根。勤劳坚韧能让你从泥土里站起来，而骄奢挥霍会让你重新跌入尘埃。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “人世间的一切华贵、荣耀与金钱，都不过是漂浮在风中的尘埃；唯有那无言的大地，以永恒的慈悲，托举着一代代生生不息的人类。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界乡土文学巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第二至三章（新婚躬耕与麦浪）：</strong>精读王龙与阿兰在春风中并肩挥锄翻开黑土的纯朴圣洁图景。</li>
        <li><strong>必读第二场 · 第八至九章（荒年大旱杀牛拒卖地）：</strong>精读全家吞咽观音土、绝不卖掉命根子田产的坚韧骨气白描。</li>
        <li><strong>必读第三场 · 第二十章（强夺阿兰两颗珍珠）：</strong>全书最令人心碎的道德批判场次，体会劳动女性无言的尊严血泪。</li>
        <li><strong>必读第四场 · 第三十四章（老王龙抚土与儿子冷笑）：</strong>精读全书最后一段，领悟中国历史朝代家族由盛转衰的深刻宿命。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 勤劳与发家的辩证法：</strong>王龙一生极其勤劳，但如果没有南方战乱中阿兰摸得的那一袋横财珠宝，他能够突破阶层壁垒成为大地主吗？这揭示了社会流动怎样的残酷规律？
      </div>
      <div class="card-box">
        <strong>Q2 · 阿兰的伟大品格：</strong>阿兰一生几乎没有一句长篇大论，但为什么全球读者公认她是整部小说中道德光芒最璀璨的真正英雄？
      </div>
      <div class="card-box">
        <strong>Q3 · 财富对人性的腐蚀：</strong>王龙在发财后为什么必然会走向纳妾、轻慢结发妻子的道路？这种变化是王龙个人的品德败坏，还是传统宗法社会富农阶层的普遍阶级劣根性？
      </div>
      <div class="card-box">
        <strong>Q4 · 城市与乡村的文明对立：</strong>在赛珍珠笔下，大城市（南京、上海）往往与投机、乞讨、浮华和战乱相伴，而乡村土地则代表着宁静与生机。这种对比在今天是否依然具有启示意义？
      </div>
      <div class="card-box">
        <strong>Q5 · 终局卖地预言的必然性：</strong>王龙的儿子们为什么注定无法守住土地？当一个人接受了近代城市教育之后，他回归土地的可能性究竟有多大？
      </div>"""

    sec13 = """      <div class="sub-heading">① 家族与个人传承自省工具：“根基沉淀审计表” (The Good Earth Grounding Audit)</div>
      <p><strong>适用场景：</strong>在感到生活浮躁漂浮、盲目追求虚幻消费或投机快钱、家庭代际沟通出现严重隔阂时。<br>
      <strong>第一步（找根基）：</strong>追溯你的家族三代前是在哪一片土地、依靠哪一项具体而辛苦的劳动养活了后代；<br>
      <strong>第二步（查浮华）：</strong>审视你目前的开销与追求中，有多少属于当年黄府式的‘虚张声势与消费代偿’；<br>
      <strong>第三步（做一件与大地连接的事）：</strong>去农田、菜园或自然山野中，亲手体验一次挥洒汗水的重体力劳动，让虚浮的心神重新扎入厚实的现实土壤。</p>

      <div class="sub-heading">② 现实观察实验：“老一辈的土地情结访谈”</div>
      <p>采访你家中的爷爷奶奶或外公外婆，让他们讲一件年轻时关于‘挨饿、种地或守护口粮’的真实往事。记录他们在讲述时眼神中流露出的敬畏与珍惜，对比现代年轻人对外卖剩饭的随意浪费，体会两代人精神底色的差异。</p>

      <div class="sub-heading">③ 泥土史诗仿写任务</div>
      <p>模仿赛珍珠那种运用大量圣经并列短句、描写春雨滋润干渴田野的史诗笔调，写一段关于‘久旱之后的村庄迎来第一场透雨、农人走出泥屋仰望天穹’的白描段落（350字以内，不加花哨形容词，全凭质朴动作感动人心）。</p>"""

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

print("Round 08 deep The Good Earth ready.")

def get_deep_great_gatsby():
    data = {
        "title_cn": "了不起的盖茨比",
        "title_en": "The Great Gatsby",
        "author_cn": "F·S·菲茨杰拉德",
        "author_en": "F. Scott Fitzgerald",
        "sub_desc": "二十世纪美国文学的绝顶明珠 · 爵士乐时代的绚烂挽歌与美国梦的终极幻灭",
        "hero_quote": "于是我们奋力前行，逆水行舟，浪潮却一刻不停地将我们推回过去。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">F·S·菲茨杰拉德 (1896–1940)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1925 年出版 / 现代美国文学奠基之作</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">抒情现代主义长篇 / 爵士时代悼亡史诗</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 18 万字 / 全九章经典篇幅</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 终身必读文学经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">物质极度丰饶下的精神荒芜与理想幻灭深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把杰·盖茨比当成一个低俗炫富、一心想插足他人婚姻的‘黑帮暴发户小三’。盖茨比之所以在文学史上被冠以‘了不起（Great）’之名，是因为在一群冷酷、自私、‘撞碎了别人的生活就缩回巨额金钱城堡里’的世袭老钱阶层（如汤姆与黛西）中间，唯有他保留了一种<strong>在成年人的世界里绝无仅有的、近乎宗教般纯粹圣洁的理想主义能力</strong>。他把生命全部的筹码押在了一颗绿色的微光之上，这场悲剧是全人类理想主义面对冷酷现实最悲壮的献祭。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 码头尽头对岸那一抹永恒跳动的绿色微光（The Green Light）：</strong>全书最具统摄力的象征图腾。每当夜深人静，盖茨比独自站在长岛幽暗的草坪边缘，伸出双臂颤抖着指向海湾对岸黛西码头的绿灯。它不仅是那个娇柔虚荣的名媛，更是人类对未竟梦想、纯真过去与美好未来最执着、最不可企及的形而上向往。
      </div>
      <div class="card-box">
        <strong>② 灰烬谷（Valley of Ashes）上空巨大盲眼的冷眼俯瞰：</strong>连接奢华长岛与浮华曼哈顿之间的巨大工业垃圾荒原，常年笼罩在灰蒙蒙的煤灰下；在废墟之上，赫然矗立着眼科医生埃克尔堡大夫褪色的巨大广告牌——那双没有脸庞、没有情感、足有数尺高的淡黄色巨大眼睛，在尘土中冷冷注视着人间的谋杀、偷情与贪婪，构成了现代神明缺席的恐怖隐喻。
      </div>
      <div class="card-box">
        <strong>③ 夏夜盛宴的万人狂欢与秋雨葬礼的凄凉死寂对照：</strong>盖茨比生前，每逢周末庄园里灯火通明、流水席开席、数百名甚至连主人名字都不知道的社交名流蜂拥而至喝掉几百箱香槟；然而当他横尸泳池后，整个纽约上流社会作鸟兽散，除了叙述者尼克和老父亲，没有一个当年在他草坪上欢笑的‘贵宾’出席葬礼，将世态炎凉撕扯得淋漓尽致。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        一战结束后1920年代美国‘爵士乐时代（Jazz Age）’。禁酒令反而刺激了全国性的私酒走私与黑帮洗钱，华尔街投机狂飙突进，整个社会沉浸在一种纸醉金迷、道德失语的狂热末日幻觉中。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .gg-box { rx: 8; stroke-width: 1.5; }
            .gg-bg-west { fill: #1d3557; stroke: #2a4d7a; }
            .gg-bg-east { fill: #242930; stroke: #59645f; }
            .gg-bg-light { fill: #2a9d8f; stroke: #40916c; }
            .gg-bg-valley { fill: #8c2d19; stroke: #a33b24; }
            .gg-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .gg-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .gg-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .gg-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .gg-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .gg-green { stroke: #2a9d8f; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .gg-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="gg-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 西卵：杰·盖茨比 (新钱 · 浪漫理想) -->
          <rect x="20" y="25" width="210" height="115" class="gg-box gg-bg-west" />
          <text x="125" y="52" class="gg-t-w">西卵：杰·盖茨比 (Gatsby)</text>
          <text x="125" y="72" class="gg-t-sub-w">詹姆斯·盖茨贫农起家 · 暴发新钱</text>
          <text x="125" y="90" class="gg-t-sub-w">奢华流水席狂欢 · 滴酒不沾的守望者</text>
          <text x="125" y="108" class="gg-t-sub-w">相信过去可以重来 · 为爱顶包死于枪下</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">“他身上有一种惊人的希望天赋”</text>

          <!-- 东卵：汤姆与黛西 (老钱 · 残酷自私) -->
          <rect x="450" y="25" width="210" height="115" class="gg-box gg-bg-east" />
          <text x="555" y="52" class="gg-t-w">东卵：汤姆 & 黛西·布坎南</text>
          <text x="555" y="72" class="gg-t-sub-w">世袭名门老钱 · 声音里装满金钱</text>
          <text x="555" y="90" class="gg-t-sub-w">白人优越狂躁 · 撞死人后远走高飞</text>
          <text x="555" y="108" class="gg-t-sub-w">‘他们打碎了东西，就躲回钱堆里’</text>
          <text x="555" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">残忍冷酷的阶层特权城堡</text>

          <!-- 隔海相望：绿色微光 -->
          <path d="M 230 82 L 450 82" class="gg-green" />
          <text x="340" y="74" style="fill:#2a9d8f; font-size:11px; font-weight:700; text-anchor:middle;">海湾隔绝 · 伸出双臂触摸绿光</text>

          <!-- 中间纽带：尼克·卡拉威 (叙述者) -->
          <rect x="235" y="135" width="210" height="75" class="gg-box gg-bg-light" />
          <text x="340" y="162" class="gg-t-w">见证人：尼克·卡拉威 (Nick)</text>
          <text x="340" y="180" class="gg-t-sub-w">中西部淳朴青年 · 身兼局内与局外</text>
          <text x="340" y="196" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">“他们那帮人加起来，都比不上你一个”</text>

          <!-- 下方死亡深渊：灰烬谷与威尔逊 -->
          <path d="M 340 210 L 340 245" class="gg-solid" marker-end="url(#gg-arr)" />
          <rect x="160" y="245" width="360" height="80" class="gg-box gg-bg-valley" />
          <text x="340" y="272" class="gg-t-w">灰烬谷 (Valley of Ashes) · 阶级废墟</text>
          <text x="340" y="292" class="gg-t-sub-w">埃克尔堡大夫褪色巨眼 · 汽车修理工威尔逊被借刀杀人</text>
          <text x="340" y="308" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">黄色劳斯莱斯撞碎肉体，泳池水波荡漾血色</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>杰·盖茨比（Jay Gatsby）：</strong>世界文学画廊中最具神话悲彩的人物。原名詹姆斯·盖茨，来自北达科他州的贫农家庭。他十六岁离家流浪，靠钢铁般的意志制定严格的时间表与自律守则；在军营初遇黛西后，将自己的一切价值神圣化为‘必须配得上黛西’。为了买下海湾对面的庄园，他不惜涉足私酒走私与伪造债券。但他从不喝酒，在夜夜喧闹的派对上如同清醒的幽灵注视人群。他的全部家产，只为了在某个下午换来黛西的‘顺道造访’。当黛西开车撞死情妇默特尔后，盖茨比毫不犹豫地替她顶包，在树荫下守候至天明以防汤姆家暴。他的纯真与伟大，在于他身陷污泥，灵魂却始终保留了一尘不染的圣徒执念。</li>
        <li><strong>黛西·布坎南（Daisy Buchanan）：</strong>金钱社会的终极洋娃娃化身。她的声音充满魔力，‘听起来像金币在银盘子里叮当作响’。她曾深爱年轻的军官盖茨比，但在盖茨比赴欧参战后，因无法抵挡孤独与对奢华生活的渴求，收下了汤姆价值三十五万英镑的昂贵珍珠项链成婚。她美丽而空虚，撞死人后平静地坐在家中与丈夫吃冷鸡喝红酒密谋对策，随后带上行李远走高飞，连一通慰问电话、一朵白花都没有留给盖茨比。</li>
        <li><strong>汤姆·布坎南（Tom Buchanan）：</strong>耶鲁大学前明星橄榄球卫，世袭庞大庄园的白人贵族暴君。他粗暴蛮横、充满种族偏见，整日研读《有色帝国的崛起》等纳粹式读物。他在外面肆无忌惮地包养修车工妻子默特尔，却无法忍受妻子黛西的任何精神出轨；当撞车惨剧发生后，他残忍地向发狂的威尔逊透露黄色汽车的主人是盖茨比，借刀杀人干掉了情敌与情妇的丈夫，随后若无其事地回到大都市继续享乐。</li>
        <li><strong>尼克·卡拉威（Nick Carraway）：</strong>全书第一人称叙述者与最高道德裁判官。他受过严格的家教，奉行‘不轻易评判他人’的家风。他是盖茨比喧嚣派对里唯一收到正式请柬的客人，也是看穿了整个东卵老钱阶层‘冷酷无情与无度破坏’的唯一清醒者。在埋葬盖茨比后，他厌恶地斩断了与乔丹·贝克的虚伪情丝，毅然告别充满腐尸气息的纽约返回中西部，留下了一部传世的安魂曲。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>年轻的中西部耶鲁毕业生尼克·卡拉威来到纽约长岛西卵从事债券买卖，租住在神秘富豪杰·盖茨比那栋仿造诺曼底古堡风格的宏大庄园隔壁。海湾对岸的东卵，住着尼克的远房表妹黛西与她蛮横富有的丈夫汤姆。盖茨比每周末在庄园里举办极其奢华庞大、全纽约名流不请自来的免费狂欢派对，但主人本身却始终神龙见首不见尾。通过女高尔夫球手乔丹·贝克，尼克终于解开了谜团：原来盖茨比五年前曾是一名一贫如洗的陆军中尉，与贵族少女黛西坠入热恋；盖茨比赴欧参战期间，黛西嫁给了拥有数亿家产的汤姆；五年来，盖茨比通过走私私酒拼死暴富买下这栋庄园，夜夜遥望黛西码头的绿色微光，举办盛大派对只为吸引黛西前来看看。在尼克的秘密安排下，盖茨比与黛西在雨天的小木屋里奇迹重逢，泪流满面，旧情重燃。然而在最炎热的仲夏之日，四人在纽约广场饭店套房摊牌：汤姆当众揭发了盖茨比靠非法私酒和假债券起家的黑底，黛西在恐惧与退缩中放弃了离开汤姆的诺言。返程途中，心神恍惚的黛西驾驶着盖茨比耀眼的黄色大跑车，在灰烬谷路段撞死了汤姆的情妇默特尔后仓皇逃逸。汤姆暗中向发狂的修车工威尔逊告密，谎称车主盖茨比正是肇事者与奸夫。次日午后，在落叶纷飞的深秋泳池中，等待黛西电话的盖茨比被潜入的威尔逊一枪射杀，威尔逊随即在草丛中吞枪自尽。在盖茨比惨淡凄凉的葬礼上，名流四散，黛西毫无踪影，只有尼克与白发老父亲送葬。看透上流社会残忍自私的尼克卖掉租屋，毅然返回纯朴的中西部，在午夜的海滩上凝视着对岸永远熄灭的绿光，发出了逆水行舟的世纪浩叹。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃解剖的是<strong>“美国梦在二十世纪物质狂热时代的彻底破灭”</strong>。小说证明：金钱或许能买来豪华城堡、能把成箱的丝绸衬衫从伦敦空运而来，但在由世袭门第与冷酷阶级特权筑起的高墙面前，一个平民青年妄图通过财富赎买纯洁理想与爱情的企图，注定只能撞得头破血流。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在盛大夏夜爵士乐与冰镇香槟泡沫中徐徐展开的末日挽歌：在极尽绚烂的派对欢笑背后，闻到一具被时代冷酷碾碎的纯真灵魂散发出的凄美与苍凉。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾为某个崇高的梦想孤注一掷、在物质的名利场上跌得粉身碎骨，却在深夜独自一人时依然相信‘那盏绿光曾经真实照亮过自己’的理想主义受难者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以盖茨比为代表的平民个人纯真浪漫英雄主义执念 vs 以布坎南家族为代表的世袭老钱阶层的绝对冷酷自私与阶级壁垒。</strong></p>

      <div class="sub-heading">全书九章精密交响推进链条</div>
      <ol class="num-list">
        <li><strong>第一至二章 · 浮华两极与灰烬深渊：</strong>东卵白色大宅里轻飘飘的白窗帘与声音如金钱的黛西；灰烬谷埃克尔堡大夫的盲眼巨照与汽车修理厂脏乱偷情。</li>
        <li><strong>第三至四章 · 盛大夜宴与神秘真相：</strong>西卵盖茨比庄园数百人的夏夜纵饮；劳斯莱斯轿车与车上闪闪发光的勋章；尼克得知‘五年来每一座派对只为引她前来’的惊天纯情秘密。</li>
        <li><strong>第五章 · 雨中重逢与衬衫之泪：</strong>全书情感巅峰。茶室雨过天晴，盖茨比将成箱各色丝绸衬衫抛向空中，黛西伏在衬衫堆中失声痛哭（‘我从未见过这么美丽的衬衫！’）。</li>
        <li><strong>第六至七章 · 炎热摊牌与黄色车祸：</strong>全剧最高潮。纽约广场饭店密室激辩，汤姆撕碎盖茨比假学历与黑金底细；黛西绝望退缩；归途黄色跑车在灰烬谷撞碎默特尔肉身。</li>
        <li><strong>第八至九章 · 泳池残阳与寂寞葬礼：</strong>盖茨比守候至黎明得知真相；泳池枪响血水泛红；世态炎凉人情如纸；尼克夜巡故园，发出‘逆水行舟推回过去’的千古绝唱。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第七章广场饭店套房里汤姆厉声揭发盖茨比：</strong>当汤姆吼出盖茨比不过是一个在药房里私自贩酒的走私贩子时，盖茨比的脸色变成了‘仿佛杀了人一样的煞白’，他试图向黛西辩白，但黛西眼中的光芒在瞬间熄灭了，她惊恐地缩回沙发，哀求汤姆带她回家。这一刻，那个用五年财富编织的美丽神话彻底宣告流产。
      </div>"""

    sec05 = """      <div class="sub-heading">为什么盖茨比是‘了不起’的？——尼克的终极道德裁决</div>
      <p>全书第八章黎明，尼克在离开盖茨比庄园前回头大喊：<strong>‘他们那帮人加起来，都比不上你一个！’</strong>（They're a rotten crowd. You're worth the whole damn bunch put together.）尼克自始至终厌恶盖茨比的炫耀品味与走私黑金，但为什么给予他全书唯一的至高赞誉？因为在那个充斥着谎言与背叛的时代，汤姆与黛西是‘粗心大意的人——他们打碎了东西、毁灭了生命，然后缩回他们的金钱或巨大的粗心大意里，让别人来替他们收拾残局’；而唯有盖茨比，守着那份对爱的神圣忠诚，甘愿在黑暗的灌木丛中为心爱的女人守候一整夜，甘愿替她顶下全部的凶杀罪名。他的手段是肮脏的，但他的动机是神圣无暇的。</p>

      <div class="sub-heading">黛西的眼泪：对金钱体制的深沉臣服</div>
      <p>第五章黛西把脸埋在盖茨比绚烂的衬衫堆里放声大哭，是文学史上最耐人寻味的眼泪。她哭的不是衣服，而是她在那一瞬间猛然惊醒：<strong>当年如果她稍微多等盖茨比几年，她既可以拥有真挚无上的爱情，又不需要放弃巨额的物质财富！</strong>然而历史无法重来，她的眼泪是对自己当年屈从于三十五万英镑项链的懦弱的微小追悔，但只要危机一旦降临，她依然会毫不犹豫地再次躲回汤姆的巨额金钱城堡之中。</p>"""

    sec06 = """      <div class="sub-heading">二十世纪英语文学最华丽深情的抒情诗化文风</div>
      <p>菲茨杰拉德在本作中展现了令人叹为观止的语言炼金术。全书的文字如同涂抹着微光的水彩画，充满了‘低语声、香槟泡沫、黄昏的萨克斯管哀鸣、夏日草坪上的微风’等极其精致感官的通感描写。文字自带一种沉郁浪漫的管弦乐韵律，每一个句号的收尾都带有淡淡的怅惘与芳香，把一场纽约庸俗的谋杀案提炼为现代人类精神的至尊挽歌。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>码头尽头的绿光 (The Green Light)：</strong>世界文学史上最经典的象征之一。它既是黛西码头物理上的灯火，也是人类对那不可企及之美好未来、对逝去纯真时光的永恒形而上向往。</li>
        <li><strong>埃克尔堡大夫的眼睛 (The Eyes of Dr. T. J. Eckleburg)：</strong>巨幅广告牌上的巨大盲眼。在暴民威尔逊眼中，那双眼睛就是‘洞悉一切罪恶的上帝之眼’；但在客观现实中，它只是一块在风雨中逐渐褪色的商业广告帆布，象征着<strong>现代资本工业社会中神圣信仰的彻底缺席与道德荒原</strong>。</li>
        <li><strong>盖茨比那辆炫目的黄色跑车 (The Yellow Car)：</strong>长岛大道上疾驰的‘死亡马车’。黄色既是财富金子的炫耀颜色，也是走向毁灭的警示色。正是这辆车碾碎了情妇的肉身，也彻底成为了碾碎盖茨比自己生命的断头台。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（爵士时代情杀传奇）：</strong>一个神秘富豪为了挽回初恋情人举办奢华派对，最终因车祸误会被情妇丈夫枪杀于泳池的豪门悲剧。<br>
        <strong>深层架构（美国梦与阶层固化）：</strong>对美国建国神话‘通过诚实个人奋斗即可获得一切幸福’的冷酷解构。揭示老钱阶层对新钱阶层的无情蔑视与制度性排斥，证明阶级壁垒永远无法单凭财富抹平。<br>
        <strong>根本架构（时间与人类生存宿命）：</strong>人类对‘重回过去纯真’的永恒徒劳抵抗。我们的一生就是被时间的巨浪不断推向前，却始终在心底执着地想要重返生命最初那座洒满夕阳与花香的纯洁原野。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>美国著名文学巨匠T·S·艾略特在读完《了不起的盖茨比》后致信菲茨杰拉德赞叹：‘这是自亨利·詹姆斯以来，美国小说迈出的第一步！’小说以极其克制的全景笔触，完成了对第一次世界大战后整个‘迷惘的一代（Lost Generation）’在精神废墟中追寻神圣意义的永恒雕塑。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天的互联网时代与金融狂欢，几乎就是爵士乐时代在元宇宙和短视频里的重演：<br>
      那些在社交网络上晒着豪车、名表、私人飞机、豪华派对的网红博主，正如当年在长岛开派对的盖茨比；而那些在屏幕这端狂热围观、甚至赶去蹭局打卡的粉丝名流，正像当年那些连主人名字都叫不全就喝光几百箱香槟的客人们。当繁华散尽、潮水退去，现代人在算法泡沫破裂后所感受到的无边荒凉，与当年躺在落叶泳池中的盖茨比毫无二致。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的人生追求中，是否有某一个目标（如考上某所学校、年薪达到某个数字、追到某个男神女神），被你赋予了‘一旦实现我就能彻底幸福’的过度神圣想象？</li>
        <li>面对身边那些虽然拥有显赫财富地位、但为人极其自私冷酷的‘汤姆和黛西’们，你是否能保持独立的清醒骨气，不向他们的资源低头？</li>
        <li>在经历了无数社会的欺骗与现实挫折后，你靠什么守护内心那份对美好事物最初的‘希望的天赋’？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《了不起的盖茨比》是全世界写美国梦写得最美、也最狠的一本书。一个穷小子为了追回当年嫌他穷嫁给富二代的初恋，拼死搞走私暴富买下一座大庄园，天天开免费派对等她来看。最后他替初恋顶包车祸罪名，被冤枉一枪打死在泳池里，初恋却连一朵花都没送。它告诉你：最可怕的不是穷，而是你把一身的才华与深情，押在了一个根本不配被爱的虚伪灵魂身上。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读二十世纪世界文学皇冠上的明珠——菲茨杰拉德的《了不起的盖茨比》。很多人只记得小李子电影里那个手举香槟微笑的帅气身影，但这部小说真正要讲的，是一场让人心碎的理想主义自毁史诗。故事发生在1920年代纸醉金迷的纽约长岛。男主角盖茨比是个神秘的大富豪，每到周末他的庄园就亮起漫天灯火，全纽约的名流不用请帖全跑来蹭吃蹭喝。但没有人知道，盖茨比本人滴酒不沾，他夜夜站在海边，死死盯着对岸码头上一盏小小的绿色灯火。为什么？因为五年前他还是个一贫如洗的穷军官，爱上了对岸的豪门千金黛西。黛西等不起，转头收了三十五万英镑的珍珠项链，嫁给了一个冷酷粗暴的豪门世子汤姆。五年来，盖茨比只有一个念头：我要发财，我要把过去的一切全买回来！在邻居尼克的帮助下，两人终于重逢。盖茨比把整整一柜子从伦敦空运来的丝绸衬衫疯狂抛向空中，黛西把脸埋在衬衫堆里放声痛哭。但现实是极其残忍的。在纽约大饭店的套房里，汤姆当众撕开了盖茨比靠走私起家的黑底，黛西瞬间退缩了，她要的是体面，不是冒险。在回程的路上，精神恍惚的黛西开着盖茨比的黄色跑车，撞死了汤姆的情妇，然后仓皇逃逸。盖茨比毫不犹豫地替黛西扛下了全部罪名，在黑暗的树林里默默守候了一整夜，生怕汤姆回家打她。然而第二天，汤姆借刀杀人，向死者的丈夫告密。在秋风萧瑟的泳池里，盖茨比躺在气垫上静静等待着黛西的电话，直到一声枪响打破了寂静。葬礼那一天，全城当年吃他喝他的名流全跑得无影无踪，黛西正收拾行李和丈夫开开心心去欧洲度假。小说的最后一句话，成为了英语文学史上最伟大的墓碑金句：‘于是我们奋力前行，逆水行舟，浪潮却一刻不停地将我们推回过去。’盖茨比是了不起的，因为在这个唯利是图的世界上，唯有他敢于为了那盏看似不可企及的绿色微光，献出自己的全部生命。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “他走过了漫长的道路才来到这片金色的草坪上，他的梦想一定显得近在眼前，仿佛只要伸出手去就绝不会错过；但他不知道，那个梦想早已落在了他的身后，落在了那片在黑暗夜空下无边无际延伸的荒原深处。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界现代主义小说巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一章结尾（海湾绿光初现）：</strong>精读尼克在夜色中初见盖茨比独自向着海湾伸出双臂、注视幽微绿光的诗意剪影。</li>
        <li><strong>必读第二场 · 第五章（雨天茶室重逢与衬衫之泪）：</strong>世界文学史最著名的重逢名场面，感受极致紧绷的尴尬如何化作丝绸衬衫漫天飞舞的心碎。</li>
        <li><strong>必读第三场 · 第七章（广场饭店残酷摊牌与车祸）：</strong>精读汤姆撕碎盖茨比假人设，以及黄色跑车在灰烬谷撞击惨剧的极速对决。</li>
        <li><strong>必读第四场 · 第八章（尼克最后一句赞美）：</strong>精读尼克在栅栏旁回身大喊‘他们那帮人加起来，都比不上你一个’的道德洗礼。</li>
        <li><strong>必读第五场 · 第九章（末尾沙滩夜巡逆水行舟）：</strong>反复诵读最后三段传世文字，体会全人类文学在时间面前最崇高的叹息。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 理想与客体的错位：</strong>盖茨比深爱的那座神像，究竟是真实的黛西，还是他自己在漫长五年苦熬中用全部才华虚构出的‘完美化身’？当虚构的客体与真实的庸俗肉身重叠时，幻灭是否在第一天就已经注定？
      </div>
      <div class="card-box">
        <strong>Q2 · 老钱与新钱的阶级天花板：</strong>为什么盖茨比哪怕拥有了富可敌国的资产、买下了长岛最顶级的城堡，在汤姆这些老钱世家眼里，他依然只配被称作‘粉红色西装的下等小贩’？现代社会靠财富能够抹平阶层鄙视链吗？
      </div>
      <div class="card-box">
        <strong>Q3 · 尼克的‘不评判’底线：</strong>尼克开篇宣称自己‘恪守不轻易评判他人的家训’，但在全书终盘他做出了最决绝的道德审判——痛斥汤姆和黛西‘打碎了一切就躲回钱堆里’。这种从‘冷眼旁观’到‘严厉审判’的转变标志着他怎样的心智蜕变？
      </div>
      <div class="card-box">
        <strong>Q4 · 逆水行舟的物理隐喻：</strong>全书最后一句‘逆水行舟，浪潮却一刻不停将我们推回过去’（So we beat on, boats against the current, borne back ceaselessly into the past），传达了人类在时间与欲望面前怎样一种兼具悲壮与徒劳的崇高尊严？
      </div>
      <div class="card-box">
        <strong>Q5 · 真正的粗心大意：</strong>汤姆和黛西身上展现出的那种‘无坚不摧的巨大粗心大意（Carelessness）’为什么比赤裸裸的犯罪更让人感到骨髓冰冷？这揭示了特权阶级怎样的隐蔽残忍？
      </div>"""

    sec13 = """      <div class="sub-heading">① 执念断舍离实践工具：“绿色微光去魅模型” (The Green Light De-Myth Protocol)</div>
      <p><strong>适用场景：</strong>当你被过去某段未能挽回的遗憾、某个曾经深深伤害过你的‘白月光/前任’、或者某个你投入了数年心血却早已变质的目标所困，无法开启新生活时。<br>
      <strong>第一步（剥离投射）：</strong>拿出一张纸，左边写下你记忆中对方‘多么完美、多么不可替代’的闪光细节；右边用冰冷理智列出在关键危机或利益时刻，对方真实表现出的自私、怯懦与背叛事实；<br>
      <strong>第二步（承认绿光已熄）：</strong>像尼克一样勇敢承认：那盏绿灯早在你跨过海湾、看清对岸真实平庸的那一刻，就已经彻底失去魔力了；你爱的只是当年那个全力以赴追求梦想的纯真自己；<br>
      <strong>第三步（离开西卵）：</strong>果断拉黑清空一切消耗你的旧信件与旧痕迹，离开虚浮的名利场，回到属于你自己的扎实大地上去重新生根。</p>

      <div class="sub-heading">② 现实观察实验：“名利场派对与世态炎凉觉察”</div>
      <p>观察朋友圈或行业聚会中某些正处于‘高光时刻、资源丰富’的人物，看他身边围绕着多少狂热点赞合影的追随者。记录当其中某个人突发危机或失去平台职务后的两周内，这些热络人脉展现出的极速沉默与避嫌，体会菲茨杰拉德笔下‘万人夜宴与冷清葬礼’的当代常态。</p>

      <div class="sub-heading">③ 抒情史诗仿写任务</div>
      <p>模仿《了不起的盖茨比》第九章结尾那种以宏大自然地貌为画卷、将微小个体命运升华至全人类普遍宿命的抒情哲理长句风格，写一段关于‘某座繁华城市在午夜完全熄灭霓虹灯后，流淌在江面上的反思与晨曦预感’（350字以内，带有管弦乐般的诗性节奏）。</p>"""

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

print("Round 08 deep The Great Gatsby ready.")

def get_deep_catcher_in_the_rye():
    data = {
        "title_cn": "麦田里的守望者",
        "title_en": "The Catcher in the Rye",
        "author_cn": "J·D·塞林格",
        "author_en": "J. D. Salinger",
        "sub_desc": "全球青少年的精神成年礼与抵抗圣经 · 痛击虚伪成人世界的纯真保卫战",
        "hero_quote": "我整天就想做这件事：我只想做个麦田里的守望者。守在一大片麦田的悬崖边，抓住每一个在狂奔中快要掉下悬崖的孩子。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">J·D·塞林格 (1919–2010)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1951 年出版 / 战后美国文学里程碑</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">成长小说 (Bildungsroman) / 第一人称意识流</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 15 万字 / 全二十六章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">13+ 岁 / 青少年与迷惘成年人必读</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">青春期反叛背后对纯真人性的执着守护与自愈机制</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把十六岁的霍尔顿·考尔菲德简单贬为满嘴粗话、抽烟喝酒、挂科被退学的‘不良问题少年’。塞林格经历过二战诺曼底登陆与集中营解放的血腥创伤，他将自己深沉的创伤后应激障碍（PTSD）注入了霍尔顿体内。霍尔顿满腹看似刻薄厌世的牢骚，本质上是一个<strong>拥有极其纯洁敏感同理心、道德洁癖至极的未成年灵魂，在直面整个成人社会充斥的虚伪（Phony）、自私、势利与性剥削时，所本能发出的一声声撕心裂肺的灵魂干呕</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 独特的‘口语意识流’第一人称无死角心智袒露：</strong>塞林格开创了现代英语文学最纯熟的青年口语叙事体（大量‘真的、假模假样、把人恶心得要命’等标志性口头禅）。读者不是在读一篇精心装扮的书面作文，而是仿佛坐在疗养院的长椅上，听一个疲惫不堪却极度诚实的十六岁少年，向你掏心掏肺地倾吐他在纽约街头三天三夜的游荡梦魇。
      </div>
      <div class="card-box">
        <strong>② ‘麦田里的守望者’这一伟大意象的诞生时刻：</strong>全书第十六章，霍尔顿借罗伯特·彭斯的诗句，向妹妹菲比吐露自己一生唯一真正渴望成为的角色：‘我不想当什么律师、政客或大款。我只想站在悬崖边，如果有成千上万的孩子在麦田里狂奔玩耍，看不见前面的悬崖，我就飞奔过去抓住他们，不让他们掉下去！’这是世界文学史上对‘守护儿童免受成人世俗毒害’最神圣的宣言。
      </div>
      <div class="card-box">
        <strong>③ 中央公园暴雨中旋转木马上的终极释怀与自愈：</strong>全书第二十五章的高潮与收尾：霍尔顿放弃了逃往西部当装聋作哑隐士的幼稚计划，陪妹妹菲比去动物园坐旋转木马。瓢泼大雨倾盆而下，霍尔顿反戴着猎人帽浑身湿透坐在长椅上，看着菲比和其他孩子冒着跌落的危险伸手去抓木马上的金环，那一瞬间他突然领悟到成长的真谛，内心涌出前所未有的纯净幸福。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        二战刚结束不久的美国五十年代冷战初期。中产阶级郊区体面生活与消费主义狂飙，名牌私立中学兜售虚伪精英教育，战后青年一代在繁荣表象下体验着深沉的精神窒息与虚无。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .cr-box { rx: 8; stroke-width: 1.5; }
            .cr-bg-holden { fill: #8c2d19; stroke: #a33b24; }
            .cr-bg-phony { fill: #131619; stroke: #59645f; }
            .cr-bg-phoebe { fill: #2a9d8f; stroke: #40916c; }
            .cr-bg-allie { fill: #1d3557; stroke: #2a4d7a; }
            .cr-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .cr-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .cr-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .cr-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .cr-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .cr-green { stroke: #2a9d8f; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .cr-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="cr-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 霍尔顿·考尔菲德 (中心) -->
          <rect x="230" y="25" width="220" height="120" class="cr-box cr-bg-holden" />
          <text x="340" y="52" class="cr-t-w">霍尔顿 (Holden Caulfield)</text>
          <text x="340" y="72" class="cr-t-sub-w">十六岁高个少年 · 满头白发一缕</text>
          <text x="340" y="90" class="cr-t-sub-w">反戴红色猎人帽 · 厌恶一切‘假模假样’</text>
          <text x="340" y="108" class="cr-t-sub-w">纽约三天漫游 · 神经衰弱与同情博爱</text>
          <text x="340" y="126" style="fill:#f0dcd8; font-size:10.5px; font-weight:700; text-anchor:middle;">“麦田里的守望者”与纯真捍卫者</text>

          <!-- 恶心对象：虚伪的成人世界 (Phonies) -->
          <path d="M 230 85 L 160 85" class="cr-solid" marker-end="url(#cr-arr)" />
          <text x="195" y="75" class="cr-lbl">对抗厌恶</text>

          <rect x="15" y="30" width="145" height="110" class="cr-box cr-bg-phony" />
          <text x="87" y="58" class="cr-t-w">虚伪成人世界 (Phonies)</text>
          <text x="87" y="78" class="cr-t-sub-w">潘西私立名校校长</text>
          <text x="87" y="96" class="cr-t-sub-w">自私室友斯特拉德莱塔</text>
          <text x="87" y="114" class="cr-t-sub-w">酒店皮条客与妓女桑妮</text>
          <text x="87" y="128" style="fill:#e0e4e8; font-size:9.5px; text-anchor:middle;">功利、伪善与身体剥削</text>

          <!-- 纯真治愈源泉：妹妹菲比 -->
          <path d="M 450 85 L 520 85" class="cr-green" />
          <text x="485" y="75" class="cr-lbl" style="fill:#2a9d8f;">深情救赎</text>

          <rect x="520" y="30" width="145" height="110" class="cr-box cr-bg-phoebe" />
          <text x="592" y="58" class="cr-t-w">妹妹菲比 (Phoebe)</text>
          <text x="592" y="78" class="cr-t-sub-w">十岁红发聪慧少女</text>
          <text x="592" y="96" class="cr-t-sub-w">毫无保留倾听哥哥</text>
          <text x="592" y="114" class="cr-t-sub-w">拿圣诞零花钱相赠</text>
          <text x="592" y="128" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">阻止逃亡 · 旋转木马天使</text>

          <!-- 下方：精神圣殿 —— 亡弟阿利与鸭子迷思 -->
          <path d="M 340 145 L 340 200" class="cr-solid" marker-end="url(#cr-arr)" />
          <text x="385" y="175" class="cr-lbl">精神寄托</text>

          <rect x="160" y="200" width="360" height="115" class="cr-box cr-bg-allie" />
          <text x="340" y="228" class="cr-t-w">未被世俗污染的圣域 (阿利的棒球手套)</text>
          <text x="340" y="248" class="cr-t-sub-w">白血病早逝的十一岁弟弟 · 手套上写满绿墨水诗篇</text>
          <text x="340" y="266" class="cr-t-sub-w">中央公园池塘里的野鸭子：冬天结冰时，鸭子去哪儿了？</text>
          <text x="340" y="284" class="cr-t-sub-w">暴雨中注视木马抓金环：成长的危险不可避免，但必须放手</text>
          <text x="340" y="300" style="fill:#a8dadc; font-size:10.5px; font-weight:700; text-anchor:middle;">“千万别跟任何人说任何事；说了，你就会想念所有人。”</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>霍尔顿·考尔菲德：</strong>十六岁、身高一米八八却极度瘦弱的叛逆少年。一侧头发已长满白发，象征未成年肉身承担着过早老化的精神疲惫。他随身携带着两件护身法宝：反戴的红色鸭舌猎人帽（捍卫自我独特性的战甲），以及写满诗歌的阿利左手棒球手套（纯洁神圣的精神祭坛）。他嘴上尖酸刻薄骂尽全纽约的伪君子，却在火车上热情替同学在母亲面前编造美言，在小饭馆里自掏二十美元捐给两位清贫修女，在自然历史博物馆里为玻璃柜中‘一万年都不会变样’的爱斯基摩人蜡像深深落泪。他是一个在肮脏世界上赤脚行走的道德殉道者。</li>
        <li><strong>菲比·考尔菲德（Phoebe）：</strong>全书最动人的救赎天使。十岁的小姑娘，聪明伶俐，能在日记里写出富有哲理的小说。当霍尔顿半夜偷偷溜回父母家潜入卧室时，菲比一眼看穿哥哥被第四所学校开除的恐慌。她没有责备，而是拿出自己积攒准备买圣诞礼物的全部八块六毛五分钱塞在哥哥手里。在霍尔顿发誓要流浪西部时，菲比拖着沉重的大皮箱坚决要跟着哥哥去流浪，用执着的陪伴粉碎了霍尔顿自暴自弃的逃避幻象。</li>
        <li><strong>阿利（Allie）：</strong>全剧不在场的永恒神明。三年前因白血病去世的十一岁弟弟。在霍尔顿眼中，阿利是全世界最聪明、最可爱、最不会发脾气的天才。阿利死的那晚，十三岁的霍尔顿在车库里用拳头砸碎了全部玻璃，导致右手关节永久残疾。每当霍尔顿在纽约街头感到自己快要跌入深渊消失时，他都在心底疯狂呼唤：‘阿利，别让我掉下去，阿利，求求你！’阿利的死，是霍尔顿对成人世界一切美好彻底产生信任危机的终极创伤原点。</li>
        <li><strong>安托里尼先生（Mr. Antolini）：</strong>霍尔顿唯一信任的前英语老师。他博学开朗，曾在学生自杀时毫不犹豫脱下大衣包裹血淋淋的尸体。他向霍尔顿给出了全书最深刻的成年忠告：‘一个不成熟男子的标志是他愿意为了某种事业英勇地死去，而一个成熟男子的标志是他愿意为了某种事业谦卑地活着。’然而在深夜，当喝醉的老师轻抚熟睡霍尔顿的前额时，霍尔顿惊恐地以为遭遇了性侵骚扰逃出门外。这一幕展现了创伤青少年对成人世界动机不可挽回的病态信任崩溃。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>十六岁少年霍尔顿因五门功课四门不及格，在圣诞节前夕被著名的潘西预备私立学校第四次开除。在与吹嘘玩弄女孩的虚荣室友斯特拉德莱塔大打出手后，厌恶名校虚伪氛围的霍尔顿戴上红色猎人帽，连夜收拾行李离开学校，潜入纽约曼哈顿度过了三天三夜的漫游。在下榻的肮脏埃德蒙酒店里，他目睹了隔壁房间互相吐水的怪异客人；因寂寞接受电梯工推荐叫来年轻妓女桑妮，却只愿付五块钱陪她坐着聊天；拒绝勒索后遭到皮条客电梯工莫里斯的殴打与洗劫。次日，他与虚荣势利的旧女友萨莉约会看戏、滑冰，因提议‘开着旧车去缅因州森林搭木屋隐居’遭嘲弄而大吵分手。在醉酒漫游、把准备送给妹妹的昂贵黑人爵士乐唱片《小雪莉·比恩斯》摔成五十块碎片后，身无分文的霍尔顿深夜偷偷潜回家中探望熟睡的十岁妹妹菲比，倾吐了自己想当‘麦田里的守望者’的心灵志愿。告别妹妹后，他投奔敬重的前英语老师安托里尼先生，却因老师深夜抚摸其前额的举动误以为遭遇同性骚扰而落荒而逃。在中央公园长椅上挨饿受冻、在艺术博物馆墙壁上疯狂擦拭别人涂写的下流脏话后，霍尔顿相约妹妹在博物馆门前告别，准备搭便车逃往西部装聋作哑度过余生。然而菲比拖着大旅行箱坚决要求同行，霍尔顿深受震动决定留下。在动物园大雨滂沱的旋转木马旁，霍尔顿看着抓金环的妹妹泪流满面，内心迎来了彻底的自愈与平静。全书在精神疗养院的病榻回忆中收尾，留下了‘想念所有人’的千古余韵。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“一个未经世俗污染的年轻生命，在被迫迈入充斥着虚伪、妥协与剥削的成人社会门槛时，所必须经历的巨大精神创伤、自我怀疑与心理重建”</strong>。塞林格证明：青少年的叛逆不是道德缺陷，而是人类良知在面对体制化虚伪时最本能的免疫排异反应。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场漫步在寒冬纽约肮脏泥泞与刺眼霓虹灯下的心灵独白：在满口粗话与满腹厌恶的刺猬外壳之下，摸到一颗为了守护这世上残存的一点点纯真而跳动得血肉模糊的赤子之心。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个在青春期曾感到被整个世界孤立遗弃、嫌恶成人社交的油腻逢迎，在跌跌撞撞的长大过程中受尽暗伤却依然渴望被理解的灵魂。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>青少年未经妥协的绝对道德纯洁性与对真实的渴望 vs 成人社会弥漫的虚伪做戏（Phoniness）、功利合谋与精神粗鄙。</strong></p>

      <div class="sub-heading">全书三天三夜流浪推进链条</div>
      <ol class="num-list">
        <li><strong>第一至三章 · 逃离潘西高墙：</strong>橄榄球赛冷眼旁观，老历史老师斯宾塞的教训与破棉袍；宿舍与室友激战，反戴猎人帽深夜跳上通往纽约的列车。</li>
        <li><strong>第四至七章 · 虚伪人间的初体验：</strong>列车上对同学母亲的讽刺性撒谎；埃德蒙酒店的窥视狂；丁香酒吧与三个西雅图女游客的空洞寒暄。</li>
        <li><strong>第八至十三章 · 伤痛、皮条客与暴力：</strong>暗夜思念阿利；电梯工莫里斯与妓女桑妮；五美元的聊天拒绝；胃部挨重拳洗劫后的复仇幻想（‘假装自己腹部中弹扣动扳机’）。</li>
        <li><strong>第十四至十七章 · 麦田守望者的诞生：</strong>街头小男孩唱着‘如果有人抓到有人在麦田里狂奔’；小木屋私奔提议破灭；百老汇剧场的空洞表演；向菲比吐露唯一理想——当麦田守望者。</li>
        <li><strong>第十八至二十二章 · 避难所的幻灭：</strong>夜访安托里尼老师，领受‘为了事业谦卑活着’的诤言；深夜惊醒落荒而逃；中央公园长椅上的濒死寒战。</li>
        <li><strong>第二十三至二十六章 · 旋转木马上的顿悟救赎：</strong>擦除小学墙上的下流脏话；菲比拖着大箱子逼停逃亡；中央公园旋转木马雨中狂喜；疗养院终局：‘千万别跟任何人说任何事，说了你就会想念他们。’</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第二十五章中央公园旋转木马旁看着菲比抓金环：</strong>当看到妹妹坐在木马上身子探得很远去抓悬空的金环时，霍尔顿本能地想冲过去拉住她，但他在那一秒停住了：‘我什么话也没说，什么事也没做。如果孩子们想去抓金环，你就得由着他们去抓，一句话都不能说。就算他们掉下来，也没什么大不了的；你如果硬去拦他们，反而会把事情搞砸。’这一瞬间标志着霍尔顿终于从偏执的‘守望者狂想’中完成蜕变，学会了接纳现实的危险与成长的不可抗拒性。
      </div>"""

    sec05 = """      <div class="sub-heading">霍尔顿的‘擦脏话圣战’：面对不可阻挡世俗化的绝望痛楚</div>
      <p>第二十五章在妹妹的小学走廊里，霍尔顿发现墙上有人用红蜡笔写了一句极其下流的‘操你（Fuck you）’。他像发了疯一样用手去死命擦除它，‘生怕那些天真无邪的小学生看到这句脏话，心里会被埋下肮脏的念头’。然而当他走到大都会博物馆的埃及古墓展厅时，赫然发现连几千年前法老墓穴的防弹玻璃上，都被人用小刀刻上了同样的脏话。霍尔顿绝望地瘫坐在地上领悟到：<strong>你就算擦掉一万面墙上的脏话，在这个肮脏的世界上，下一秒依然会有人在每一个角落涂满污秽</strong>。这种想要替全人类守护纯真却不得不面对现实污染的无力感，展现了现代存在主义悲剧的至高深度。</p>

      <div class="sub-heading">鸭子迷思：边缘弱者的安全感焦虑</div>
      <p>全书中霍尔顿执着地向出租车司机提问：‘中央公园南面池塘里的野鸭子，到了冬天湖面全结成冰的时候，它们都飞到哪里去了？是谁开着卡车把它们运走了，还是它们自己飞走了？’司机们全把他当成白痴。然而这群鸭子正是霍尔顿自身的潜意识投射：在这座冷酷冰封的纽约大都市里，当寒冬降临、没有庇护所的时候，像他这样一个被体制开除、无处容身的脆弱孤儿，究竟该飞向哪里？</p>"""

    sec06 = """      <div class="sub-heading">现代口语叙事体的文学革命</div>
      <p>塞林格在本作中彻底改写了战后美国小说的语言面貌。他把十六岁少年的日常俚语、脏话、口吃、情绪化重复提升到了极具音乐美感的纯文学高度。这种语言看似散漫无序，实则经过了极端精密的修辞推敲：每一次‘我说真的’（I really mean it）都在强化其直视灵魂的诚实；每一次‘恶心得要命’（made me want to vomit）都在划定其与虚伪体制不可妥协的绝罚界限。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>红色鸭舌猎人帽 (The Red Hunting Hat)：</strong>一块钱在体育用品店买来的奇特鸭舌帽。它不仅保暖，更是霍尔顿<strong>抵御外部虚伪世界的心灵战甲</strong>。反戴帽子时，他才感到真正的安全与自由；在最后大雨中，菲比把这顶帽子轻轻扣在哥哥头上，完成了爱意与接纳的至高传递。</li>
        <li><strong>阿利的棒球手套 (Allie's Baseball Glove)：</strong>用绿墨水在手指与虎口处密密麻麻抄写满托马斯·哈代诗歌的旧手套。它象征着<strong>未经世俗沾染的纯洁智慧、艺术与爱在人间的终极圣物</strong>。</li>
        <li><strong>旋转木马与金环 (The Carousel and the Gold Ring)：</strong>生命的轮回与成长的危险隐喻。木马永远放着古老的乐曲旋转，孩子们为了抓住虚幻的金环探出身子。它象征着<strong>人生虽然充满风险与循环，但那种伸手探索世界的热情与快乐，本身就是不可剥夺的神圣体验</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（问题少年游荡记）：</strong>一个被第四所预备中学开除的纨绔少年，在纽约曼哈顿街头漫无目的游荡三天三夜的冒险经历。<br>
        <strong>深层架构（反体制与纯真保卫战）：</strong>对战后西方中产阶级精英教育、成人虚伪社交与消费主义文化的深刻反胃与无情解剖。揭示青少年叛逆背后对真诚与爱的绝望呼唤。<br>
        <strong>根本架构（接纳成长与存在自愈）：</strong>个人如何面对世界的必然不完美。从最初妄图充当‘麦田守望者’阻挡一切孩子长大的偏执救世主幻想，最终在雨中学会放手，接纳孩子必须冒险、世俗必然嘈杂的生命真相，实现与自我的深层和解。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>全书最后一句‘千万别跟任何人说任何事；一旦你说了，你就会开始想念每一个人’（Don't ever tell anybody anything. If you do, you start missing everybody.）是全人类文学史上的绝妙叹息。霍尔顿从最初痛恨全天下的‘假模假样’，到最后在疗养院里发现自己甚至在想念那个粗暴的室友和狠揍过他的皮条客。这种超越愤世嫉俗的普世同理心，宣告了少年真正跨入了成年的门槛。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天的青少年与年轻一代，正面临着比霍尔顿当年严重十倍的‘虚伪与意义虚无困境’：<br>
      名校履历包装、社交媒体精修人设、职场黑话与言不由衷的赞美把年轻人裹挟在巨大的‘假模假样网络’之中；多少青年因此患上抑郁、焦虑，选择‘躺平、隐居甚至自闭’。塞林格的《麦田》告诉每一个感到恶心的年轻人：你的敏感不是病，它是你在麻木世界里尚未死去的良知触角；但不要用逃跑去自毁，要像霍尔顿一样，为了心中的菲比，勇敢在暴雨中留下来。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你感到对身边环境极度厌恶、想要‘抛弃一切逃到远方装聋作哑’时，促使你最终停下脚步留下来面对现实的那一根‘最后的稻草’是什么？</li>
        <li>如果有一个孩子或晚辈向你展现了他看似荒唐脆弱的梦想，你是否能做到像菲比那样不嘲笑、不否定，给予他全神贯注的倾听？</li>
        <li>在不得不学会成人世界生存技能的同时，你靠什么守护自己心底那个坚决不肯说谎的‘红帽子霍尔顿’？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《麦田里的守望者》是全天下被嫌弃少年的精神圣经。一个被开除的高中生在纽约游荡了三天，骂遍了全天下的装腔作势，唯一想干的事就是守在麦田悬崖边，抓住每一个快掉下去的孩子。最后他在大雨里看着妹妹坐旋转木马哭出了声。它告诉你：看透了世界的假模假样之后依然选择留下来去爱，才是真正的成熟。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读全球年轻人的心灵成年礼——塞林格的《麦田里的守望者》。这本书曾被列为禁书，因为主角满口粗话、抽烟逃学。但如果你读懂了十六岁少年霍尔顿，你会发现他是全世界心肠最软、最干净的孩子。故事发生在圣诞节前夕，霍尔顿因为功课不及格被第四所名牌中学开除了。他忍受不了学校里校长谄媚富豪、同学互相攀比做戏的虚伪，半夜收拾行李逃回纽约，在街头游荡了三天三夜。在这三天里，他住廉价酒店，被皮条客勒索挨揍；他想找人聊天，但每个人都在自说自话。他戴着一顶一块钱买来的红色猎人帽，像个刺猬一样向全世界喷洒毒舌。但在这个浑身带刺的外表下，藏着什么？他兜里永远揣着患白血病早逝的弟弟阿利的棒球手套，手套上密密麻麻抄满了诗歌；他走在路上，满脑子想的是中央公园池塘结冰后那群无家可归的野鸭子；他深夜偷偷溜回家看熟睡的十岁妹妹菲比，妹妹问他：‘你这辈子到底想干嘛？’霍尔顿说出了一段让全世界动容的愿望：‘我只想做个麦田里的守望者，守在一大片麦田的悬崖边，抓住每一个快要掉下悬崖的孩子。’他不想长大，因为长大就意味着变成虚伪的骗子。他甚至准备逃去西部深山装聋作哑过一辈子。然而，当十岁的妹妹拖着大箱子一定要跟着他去流浪时，霍尔顿被这股纯洁的爱击碎了。在大雨如注的中央公园，霍尔顿浑身湿透坐在长椅上，看着坐旋转木马的妹妹伸手去抓空中的金环，他忽然顿悟了：成长是有风险的，孩子们总会长大、总可能会摔倒，你不可能把所有人锁在无菌室里；但只要你能放手去爱、去陪伴，生活就依然拥有值得活下去的奇迹。塞林格借这个故事告诉我们：看清世界的肮脏不是为了让你厌世自戕，而是让你在学会成熟的同时，用一生的力气去守住那顶红色的猎人帽。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “一个不成熟男子的标志是他愿意为了某种事业英勇地死去，而一个成熟男子的标志是他愿意为了某种事业谦卑地活着。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界现代主义成长小说巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一至三章（潘西宿舍告别）：</strong>精读霍尔顿反戴红色猎人帽、向深夜沉睡的宿舍大喊‘做个好梦吧混账们’的决绝开场。</li>
        <li><strong>必读第二场 · 第五章（阿利的绿墨水手套）：</strong>精读全书最圣洁深情的段落，感受暴躁少年心底最柔软的隐秘痛点。</li>
        <li><strong>必读第三场 · 第十六章（麦田守望者志愿）：</strong>精读与妹妹菲比在卧室里的深夜对话，领悟全书核心意象的诞生时刻。</li>
        <li><strong>必读第四场 · 第二十五章（旋转木马雨中狂喜）：</strong>世界文学史最动人的自愈高潮，体会大雨倾盆下释怀成长的纯净幸福。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 敏感者的生存悖论：</strong>霍尔顿讨厌一切‘假模假样’，但他在火车上为了让同学的母亲开心，也张口编造了一大堆赞美谎言。这种‘善意的谎言’算不算假模假样？人是否能做到百分之百的绝对真实？
      </div>
      <div class="card-box">
        <strong>Q2 · 守望者的不可能任务：</strong>霍尔顿想守在麦田边抓住每一个孩子，但安托里尼老师指出这是一种‘追求高尚死去的狂热’。为什么说‘学会谦卑地活在不完美的世界里’比‘悲壮赴死’需要更大的勇气？
      </div>
      <div class="card-box">
        <strong>Q3 · 擦不掉的下流脏话：</strong>霍尔顿在学校和博物馆发疯一样擦除墙上的脏话，这个行为象征着他对纯洁童年怎样的执念与最终的幻灭？
      </div>
      <div class="card-box">
        <strong>Q4 · 妹妹菲比的力量：</strong>为什么全纽约的名流、老师和心理医生都治不好霍尔顿，而十岁的妹妹菲比仅仅凭着‘拖着箱子要跟他一起走’的举动，就瞬间化解了他的自毁倾向？
      </div>
      <div class="card-box">
        <strong>Q5 · 想念所有人的终局：</strong>全书最后一句‘千万别跟任何人说任何事，说了你就会想念所有人’，包含了怎样一种在经历了创伤之后向全人类敞开怀抱的博大宽恕？
      </div>"""

    sec13 = """      <div class="sub-heading">① 情绪排毒思维工具：“霍尔顿假模假样过滤网” (The Anti-Phony Self-Audit)</div>
      <p><strong>适用场景：</strong>在感到社交倦怠、网络人设浮夸、对身边的虚伪应酬感到恶心想要掀桌子自暴自弃时。<br>
      <strong>第一步（找恶心源头）：</strong>写下当前最让你感到‘假模假样’的一件具体事情（如某个虚伪的夸赞、某场毫无意义的表演式会议）；<br>
      <strong>第二步（分清界限）：</strong>学会在心底像霍尔顿一样‘戴上红帽子’——冷眼看穿这一切是世俗生存的无聊游戏，允许别人表演，但自己在核心价值观上坚决不跟着配合撒谎；<br>
      <strong>第三步（寻找你的菲比）：</strong>离开嘈杂的派对，找一个能完全理解你、听你讲真话的朋友或家人，哪怕只是一起吃一顿普通的便饭，让灵魂在真诚中迅速回血。</p>

      <div class="sub-heading">② 现实观察实验：“生活中的野鸭子提问”</div>
      <p>寻找一个在世俗忙碌中完全被所有人忽略的‘纯洁小问题’（如冬天树上的麻雀在哪里避寒、深夜路边修车的老人如何过冬）。尝试向你身边的两个成年人提出这个问题，观察他们展现出的是不耐烦的嘲笑，还是同理心的停顿，体会现代心智的硬化程度。</p>

      <div class="sub-heading">③ 第一人称口语意识流仿写任务</div>
      <p>模仿霍尔顿那种大量使用‘说真的’、极度坦率自剖、夹杂自嘲与深沉温柔的口语语调，写一段三百字‘你在某个极其讨厌的正式场合偷偷溜出来、在街角吸一口冷空气时的内心独白’（真实、锋利、带点少年气）。</p>"""

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
    print("=== 开始批量写入第 8 轮（The Good Earth 大地、了不起的盖茨比、麦田里的守望者） ===")
    plan = [
        ("The Good Earth 大地", get_deep_the_good_earth),
        ("了不起的盖茨比", get_deep_great_gatsby),
        ("麦田里的守望者", get_deep_catcher_in_the_rye),
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
