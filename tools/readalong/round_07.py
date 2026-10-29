# -*- coding: utf-8 -*-
"""
Round 07: Pride and Prejudice, Sense and Sensibility, The Scarlet Letter (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_pride_and_prejudice():
    data = {
        "title_cn": "傲慢与偏见",
        "title_en": "Pride and Prejudice",
        "author_cn": "简·奥斯汀",
        "author_en": "Jane Austen",
        "sub_desc": "英国世态小说的绝美明珠 · 第一印象的虚妄与成熟心智的双向救赎",
        "hero_quote": "凡是有钱的单身汉，总想娶位太太，这已经成了一条举世公认的真理；然而，傲慢让人无法去爱别人，偏见则让人无法被别人所爱。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">简·奥斯汀 (1775–1817)</div></div>
        <div class="spec-item"><div class="spec-label">出版年代</div><div class="spec-val">1796年始作 / 1813年正式出版</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">世态讽刺小说 / 经典心理罗曼史</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 20 万字 / 全三卷六十一章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身必读文学经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">破除第一印象虚妄与两性心智平衡成熟度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《傲慢与偏见》当成一出‘寒门灰姑娘钓金龟婿’的肤浅言情爽文。奥斯汀以‘两寸象牙上的精细雕刻’，极其严肃地解剖了英国摄政时期的残酷现实法律——<strong>‘限嗣继承制（Entailment）’</strong>：由于班内特家没有儿子，老父亲一旦去世，整座朗伯恩庄园必须由远房侄子柯林斯牧师全权继承，五个女儿若不能及时嫁人，将面临被赶出家门流落街头的悲惨命运。奥斯汀探讨的是女性如何在不向金钱妥协卖身的前提下，凭借智慧与尊严争取平等的生存权利。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 达西第一次求婚的‘傲慢反差’与经典被拒：</strong>全书最激烈的语言交锋。达西家产万贯、出身高贵，在求婚时却忍不住强调自己是‘违背了理智、违背了门第观念、违背了家庭期望’在屈尊爱她；而伊丽莎白当头棒喝反击：‘就算世界上只剩下你一个男人，我也绝不会答应嫁给你！’两个骄傲灵魂在极度被刺伤中的碰撞，开创了现代心理小说的对峙范本。
      </div>
      <div class="card-box">
        <strong>② 彭伯利庄园（Pemberley）景致对人格的完美外化：</strong>第三卷伊丽莎白参观达西家宅。庄园没有巴洛克式的矫饰与暴发户的炫耀，溪流依山顺势、林木保留天然野趣。女管家对达西‘从小到大从未对仆人说过一句重话’的真诚赞美，如同一股清泉，彻底洗去了伊丽莎白心中受韦翰谎言蛊惑结下的厚厚偏见冰层。
      </div>
      <div class="card-box">
        <strong>③ 四种截然不同的婚姻样本社会学全景：</strong>柯林斯与夏洛特（纯粹为了生存安稳而交易的功利婚姻）、莉迪亚与韦翰（纯粹出于盲目肉欲与冲动的轻率婚姻）、班内特夫妇（年轻时被容貌吸引后半生陷入互相嘲讽的失败婚姻）、达西与伊丽莎白（历经反省建立在精神平等与人格尊重之上的理想婚姻）。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        18世纪末英国乡村乡绅社会（Landed Gentry）。法国大革命与拿破仑战争远在海峡对岸，英国乡间在舞会、拜访、马车与年金收入的平静水面下，潜伏着严酷的财产阶级博弈。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .pp-box { rx: 8; stroke-width: 1.5; }
            .pp-bg-darcy { fill: #1d3557; stroke: #2a4d7a; }
            .pp-bg-eliza { fill: #8c2d19; stroke: #a33b24; }
            .pp-bg-wick { fill: #242930; stroke: #59645f; }
            .pp-bg-charl { fill: #2a9d8f; stroke: #40916c; }
            .pp-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .pp-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .pp-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .pp-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .pp-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .pp-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .pp-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="pp-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 达西先生 (傲慢) -->
          <rect x="20" y="25" width="210" height="115" class="pp-box pp-bg-darcy" />
          <text x="125" y="52" class="pp-t-w">达西先生 (Mr. Darcy)</text>
          <text x="125" y="72" class="pp-t-sub-w">年金万磅 · 彭伯利领主</text>
          <text x="125" y="90" class="pp-t-sub-w">阶级优越感 · 寡言冷峻被误读</text>
          <text x="125" y="108" class="pp-t-sub-w">受拒后深刻反省，暗中出资救班家</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">放下傲慢，学会平等尊重</text>

          <!-- 伊丽莎白 (偏见) -->
          <rect x="450" y="25" width="210" height="115" class="pp-box pp-bg-eliza" />
          <text x="555" y="52" class="pp-t-w">伊丽莎白·班内特 (Elizabeth)</text>
          <text x="555" y="72" class="pp-t-sub-w">班家二小姐 · 灵动聪慧双眼</text>
          <text x="555" y="90" class="pp-t-sub-w">自尊敏感 · 受轻慢结下顽固偏见</text>
          <text x="555" y="108" class="pp-t-sub-w">读达西长信惊醒自愧盲目</text>
          <text x="555" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">破除偏见，实现心智成熟</text>

          <!-- 傲慢与偏见对决连线 -->
          <path d="M 230 82 L 450 82" class="pp-solid" />
          <text x="340" y="74" class="pp-lbl">初次求婚遭拒 → 达西长信解惑</text>

          <!-- 伪善反面镜像：韦翰 -->
          <rect x="20" y="180" width="210" height="135" class="pp-box pp-bg-wick" />
          <text x="125" y="208" class="pp-t-w">乔治·韦翰 (Wickham)</text>
          <text x="125" y="228" class="pp-t-sub-w">迷人民兵军官 · 满嘴谎言逢迎</text>
          <text x="125" y="246" class="pp-t-sub-w">挥霍达西资助，企图诱拐达西胞妹</text>
          <text x="125" y="264" class="pp-t-sub-w">带莉迪亚私奔险毁班家全门名誉</text>
          <text x="125" y="280" style="fill:#e0725b; font-size:10px; text-anchor:middle;">第一印象陷阱的最典型化身</text>

          <!-- 现实妥协对照：夏洛特 & 柯林斯 -->
          <path d="M 450 140 L 450 180" class="pp-solid" stroke="#2a9d8f" />
          <rect x="450" y="180" width="210" height="135" class="pp-box pp-bg-charl" />
          <text x="555" y="208" class="pp-t-w">夏洛特·卢卡斯 & 柯林斯</text>
          <text x="555" y="228" class="pp-t-sub-w">二十七岁平貌长女 · 嫁给滑稽牧师</text>
          <text x="555" y="246" class="pp-t-sub-w">‘我不浪漫，我只要一个安稳的家’</text>
          <text x="555" y="264" class="pp-t-sub-w">巧妙安排起居室避开愚蠢丈夫</text>
          <text x="555" y="280" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">无爱但极其实用的理性现实主义</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>伊丽莎白·班内特（Lizzy）：</strong>简·奥斯汀笔下最受全球读者喜爱的文学女儿。她有一双充满灵气的明亮黑眼睛，谈吐风趣幽默，敢于嘲弄一切虚伪自大。在麦里屯舞会上，达西一句‘她长得还可以，但还没漂亮到能打动我的心’被她听到，深深刺伤了她的自尊心，使她在很长一段时间内失去了客观判断力。当她在客栈读完达西冷静克制的长信时，她发出了著名的忏悔：‘直到这一刻，我才真正认识了自己！’这种勇于打碎自我虚荣的坦荡，正是她超越普通乡村闺秀的高贵之处。</li>
        <li><strong>费茨威廉·达西（Mr. Darcy）：</strong>外冷内热的英国绅士典范。他身兼彭伯利庞大家业与保护家族名誉的重担，在不熟悉的乡野社交圈中以冷漠傲慢作为自我保护屏障。被伊丽莎白无情拒绝求婚后，他没有恼羞成怒动用特权报复，而是一字一句写下长信澄清事实；当得知伊丽莎白妹妹私奔蒙羞时，他不惜暗中自掏数千英镑替无赖韦翰还清赌债并买下军职，促成二人成婚以保全班家名誉，且严令知情者保守秘密。这种‘只做不说、不求回报’的担当，彻底赢得了伊丽莎白的心。</li>
        <li><strong>柯林斯牧师（Mr. Collins）：</strong>滑稽可怜的势利小丑化身。他满嘴神学与道德，骨子里却对赞助人凯瑟琳·德·包尔夫人谄媚至极。他的求婚演说完全是一份‘向领导汇报思想’的官样文章，遭到伊丽莎白拒绝后三天内就转头向夏洛特求婚，把婚姻完全当成完成社会指标的冷血工具。</li>
        <li><strong>班内特先生与班内特太太：</strong>一对充满黑色幽默的父母标本。班内特太太神经衰弱、整日满脑子只有‘哪家少爷有四千英镑年金’的功利计算；班内特先生博学机智却消极遁世，躲在书房里把愚蠢的妻子和女儿当做笑话看，逃避家庭教育责任，险些酿成小女儿私奔家破人亡的大祸。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>英国赫特福德郡的朗伯恩小镇，富裕青年宾利先生租下尼日斐庄园，引来急于把五个女儿嫁出去的班内特太太狂喜。在小镇舞会上，宾利与美丽温柔的长女简一见钟情；而同行的彭伯利领主达西先生因冷傲不合群，当众拒绝与二女儿伊丽莎白跳舞，使伊丽莎白对其结下深深偏见。不久，仪表堂堂的青年军官韦翰来到小镇，向伊丽莎白编造了‘达西违背先父遗嘱夺走属于自己的牧师教职’的凄惨谎言，使伊丽莎白对达西的厌恶达到顶点。随后，班家财产法定继承人、愚蠢谄媚的柯林斯牧师登门向伊丽莎白求婚遭拒，闪电迎娶了伊丽莎白的务实闺蜜夏洛特。冬季到来，达西因嫌弃班内特太太与小女儿们的粗俗无礼，劝阻宾利离开小镇返回伦敦，拆散了简与宾利的良缘。春日里，伊丽莎白赴肯特郡探望夏洛特，在凯瑟琳夫人庄园偶遇前来度假的达西。达西再也无法压抑对伊丽莎白的炽热深情，突兀求婚；伊丽莎白严词拒绝，痛斥他傲慢拆散姐姐良缘并残害韦翰。备受震惊的达西次日留下一封长信，平静澄清了全部真相（揭露韦翰是个企图诱拐达西十五岁胞妹私奔侵吞财产的恶棍）。伊丽莎白在长信面前羞愧万分，深感自己的盲目自负。夏季，伊丽莎白随舅父母游览德比郡，意外参观达西的彭伯利庄园，在管家赞扬与达西温文尔雅的款待下，心结彻底冰释。就在此时，十六岁的小妹莉迪亚与韦翰私奔蒙羞的惊天丑闻爆发；达西暗中在伦敦找到二人，自掏巨资替韦翰还清赌债买下军衔，平息丑闻。宾利重返小镇向简求婚成功；达西在顶住专横姨母凯瑟琳夫人的门第阻挠后，再次向伊丽莎白吐露心扉，两对璧人在爱与尊严的彻底和解中步入殿堂。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类在认知他人与自我反省的过程中，如何穿透社会阶层制造的‘傲慢’遮蔽，与内心虚荣制造的‘偏见’迷雾，建立起真正基于理性自律与灵魂平等的长久亲密关系”</strong>。奥斯汀证明：没有物质的婚姻是愚蠢的，但没有爱情与尊重的结合是卑鄙的。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在维多利亚乡间沙龙明媚阳光下进行的智商与心智高难度击剑：在机智讽刺的欢笑声中，见证两个同样骄傲的成熟灵魂，如何敢于直面自己的愚昧偏狭，完成双向奔赴的自我救赎。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个自恃聪明敏感、容易凭借第一印象给人下定论，在世俗物质攀比与精神纯粹追求之间渴望寻找成熟平衡点的读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>贵族阶层世袭优势带来的居高临下之‘傲慢’ vs 边缘乡绅自尊心受挫后结下的盲目固执之‘偏见’。</strong></p>

      <div class="sub-heading">全书三卷经典波澜推进链条</div>
      <ol class="num-list">
        <li><strong>第一卷 · 第一印象与偏见筑墙（第一至二十三章）：</strong>麦里屯舞会初遇；达西轻慢言辞结怨；简在风雨中做客尼日斐染病，伊丽莎白赤脚穿越泥泞探视（达西被其灵动双眼俘获）；韦翰散播谎言火上浇油；柯林斯求婚遭拒。</li>
        <li><strong>第二卷 · 碰撞对抗与长信破障（第二十四至四十二章）：</strong>简在伦敦失魂落魄；伊丽莎白赴肯特郡罗斯林斯庄园；达西冲动求婚遭遇伊丽莎白疾风骤雨般的痛斥；达西林间递长信，伊丽莎白经历了人生最深刻的‘自我认知大地震’。</li>
        <li><strong>第三卷 · 彭伯利见悟与救赎终局（第四十三至六十一章）：</strong>彭伯利庄园重逢，达西的谦逊温良彻底融化成见；莉迪亚私奔丑闻爆发，达西暗中力挽狂澜救全族；凯瑟琳夫人大闹朗伯恩逼婚弄巧成拙，林间小径二次求婚终成正果。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第二卷第十三章伊丽莎白独自在小径拆读达西的长信：</strong>这封信是整部小说的精神分水岭。奥斯汀极其细腻地刻画了伊丽莎白的阅读过程——从最初的愤怒、狐疑，到反复对照韦翰平日言行后的背脊发凉，最终不得不承认是自己自诩聪明的虚荣遮蔽了眼睛。正是在这一刻，伊丽莎白战胜了自己的‘偏见’，达西也在被拒的痛苦中打碎了自己的‘傲慢’。
      </div>"""

    sec05 = """      <div class="sub-heading">为什么达西的第一次求婚注定惨败？</div>
      <p>达西的第一次求婚，是典型的‘以施恩者自居的傲慢灾难现场’。他满脑子想的是自己放下了多么高贵的血统、容忍了班内特家多么粗鄙丢人的姻亲，他以为伊丽莎白一定会因为得到一万英镑年金的豪门垂青而感激涕零。他完全没有意识到：<strong>在真正的爱情面前，尊严是绝对平等的</strong>。伊丽莎白的愤怒拒绝，如同一记响亮的耳光打醒了他，让他平生第一次意识到自己的金钱和门第，在真正的品格面前一文不值。正是这场惨败，重塑了达西的人格。</p>

      <div class="sub-heading">夏洛特·卢卡斯的现实主义婚恋观：生存的理性妥协</div>
      <p>许多读者批评夏洛特嫁给猥琐愚蠢的柯林斯是‘自甘堕落’。但奥斯汀以极具同情心的笔触写道：夏洛特二十七岁，相貌平平，没有嫁妆，弟妹众多，她面临的是即将成为家庭沉重负担的真实残酷生存危机。她嫁给柯林斯，不是因为爱他，而是因为柯林斯能给她提供一个合法的独立女主人地位、体面的养老金与安稳的客厅。她把丈夫打发去后花园种菜，自己安居在背阴的舒适起居室里操持生活。奥斯汀借她展示了在残酷法律制度下，普通女性没有爱情时所能做出的最高水平的理性自我保全。</p>"""

    sec06 = """      <div class="sub-heading">奥斯汀独步天下的‘反讽（Irony）与自由间接引语’语言艺术</div>
      <p>奥斯汀是世界文学史上最伟大的幽默讽刺大师之一。她极少直接出面辱骂任何角色，而是大量使用<strong>自由间接引语（Free Indirect Speech）</strong>——让叙述者的语调悄无声息地滑入人物自以为是的内心独白中，让人物在滔滔不绝的自我表白中暴露出内心的愚蠢、虚荣与算计（如柯林斯每一次一本正经的书信）。这种不动声色的反讽，赋予了全书极其高贵、优雅且经得起千百次研读的智性光芒。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>彭伯利庄园的水流与林木 (Pemberley Estate)：</strong>全书最具象征意味的空间。达西的祖业未经暴发户式的人工矫饰，溪流清澈、山势起伏自然，象征达西高尚、厚重、未经世俗虚浮污染的内在人格品质。</li>
        <li><strong>那一双灵动的眼睛 (Fine Eyes)：</strong>达西开篇嘲弄伊丽莎白容貌平平，却在第二卷反复向朋友承认自己被伊丽莎白‘那一双聪慧深邃的黑眼睛’彻底迷住。它象征着<strong>超越皮囊肉体的智识之光与独立灵魂对男权审美的征服</strong>。</li>
        <li><strong>两里泥泞的红裙角：</strong>第一卷伊丽莎白得知姐姐生病，不顾世俗闺秀礼仪，独自在泥泞中步行两里路、裙角溅满泥点赶赴尼日斐。它象征着<strong>姐妹真情对繁文缛节的超越，以及她身上那种未经世俗规训的野性活力</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（乡绅婚恋世态喜剧）：</strong>英国乡村五个待嫁女儿的家庭中，二女儿与傲慢豪门领主历经误会与反省，最终喜结连理的浪漫大团圆故事。<br>
        <strong>深层架构（女性生存社会学）：</strong>对十九世纪限嗣继承法与无财产女性生存危机的深刻解剖。探讨女性在金钱依赖的世俗社会中，如何既避免向纯粹财富妥协沦为商品，又避免陷入盲目激情的陷阱，实现尊严与幸福的统一。<br>
        <strong>根本架构（心智反思与认知正义）：</strong>认知局限性的自我破除史。证明人类心智最大的危险在于自负于自身的第一直觉与聪明；唯有通过痛苦的自省，放下偏执，人才能真正看见他人与世界的真实全貌。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>著名文学批评家F·R·利维斯在《伟大的传统》中将简·奥斯汀列为英国小说伟大传统的开篇第一人。奥斯汀借世态婚恋所探讨的‘诚实、负责、克制与理性自律’，是英国文明最核心的道德哲学基石。她的小说绝不是消遣言情，而是关乎严肃心智成熟的人文主义经典。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《傲慢与偏见》在今天的相亲角、相亲节目与婚恋市场中天天在重演：<br>
      人们拿着房产、年薪、户口、家庭背景等‘指标’在天平上冷酷称重；而在社交软件上，人们往往凭借一张照片、一句不太合拍的言辞，在最初的三秒钟内就给对方打上‘傲慢、普信、油腻或物质’的死刑标签。奥斯汀在两百年前就告诫我们：不要迷信你的第一印象，那个外表看起来有些笨拙冷淡的人，可能深藏着最可靠的高贵担当；而那个一上来就嘴甜幽默如沐春风的人，可能正是掏空你信任的韦翰。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在人际交往中，你是否曾因为对方某个优越的家庭背景或冷淡的举止，而本能地产生一种防御性的反感与刻板偏见？</li>
        <li>当你自以为极其客观敏锐地识破了某个人的‘本质’时，你是否有勇气在得到相反事实证据时，坦然承认自己的浅薄并真诚道歉？</li>
        <li>在择偶或交友时，你更看重对方能带给你的‘外在面子与情绪价值’，还是他在关键危机时刻展现的‘底线担当与无声付出’？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《傲慢与偏见》是所有言情戏的祖宗，但比言情深刻一千倍。一个聪明的穷小姐嫌大富豪太狂妄，富豪嫌小姐家世太低俗。两个人互相看不顺眼，最后小姐发现自己被小白脸骗了，富豪才是暗中救了她全家的大恩人。它告诉你：看人千万别信第一印象，傲慢让人盲目，偏见让人看不见真爱。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊聊两百年经久不衰的文学顶峰之作《傲慢与偏见》。很多人以为这只是一部轻松欢快的小甜文，但简·奥斯汀其实在讲一个关于人类心智如何破除偏见的严肃哲学故事。故事发生在英国乡下一个没儿子的家庭，老父亲一旦去世，房子田产全要被远房亲戚收走，五个女儿面临被扫地出门的危机。这时候，年入一万英镑的大领主达西先生来了。达西有钱有地位，但他有个大毛病——傲慢。在舞会上，他冷冷地说二女儿伊丽莎白‘长得还可以，但打动不了我’，恰好被伊丽莎白听个正着。伊丽莎白也有个大毛病——自负于自己的聪明，她发誓一辈子恨死这个傲慢男。这时，一个长相英俊的军官韦翰跳出来，声泪俱下控诉达西当年夺走自己的财产。伊丽莎白想都不想就全信了，把达西打入了十八层地狱。到了第二卷，达西再也压抑不住对伊丽莎白的深情跑来求婚，但他态度依然居高临下，口口声声说自己是‘放下高贵的门第来屈尊爱她’。伊丽莎白当场爆发，狠狠拒绝了他：‘就算天下男人全死绝了，我也绝不嫁给你！’达西备受震动，连夜写了一封长信，澄清了全部真相：原来韦翰是个挥霍无度、甚至企图拐骗达西十五岁亲妹妹夺家产的超级大恶棍！伊丽莎白一页页读着信，如梦初醒，流着泪承认：‘直到这一刻，我才真正认识了自己！’后来，伊丽莎白去参观达西的彭伯利庄园，在管家口中得知达西从小到大是多么仁慈宽厚。就在这时，小妹妹跟那个混混韦翰私奔了，整个家族名誉眼看全毁。达西没有落井下石，而是自己默默掏了几千英镑替恶棍还清赌债，逼恶棍结婚保全了伊丽莎白全家的脸面，而且一个字都不准别人向伊丽莎白透露。直到真相大白，两个原本傲慢与偏见的灵魂，终于在精神平等的至高圣殿里握手重逢。简·奥斯汀借这部小说向全世界宣布：在爱情与人生里，门第和财富可以衡量身价，但唯有真诚的自省与互相尊重，才能赢得真正的幸福。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “直到这一刻，我才真正认识了自己：我曾经为自己的聪明见识而骄傲，如今我才明白，盲目自大曾让我离真理有多么遥远。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界世态讽刺小说巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一卷第三章（麦里屯舞会初结怨）：</strong>精读达西轻慢评语‘打动不了我’与伊丽莎白傲骨结怨的历史原点。</li>
        <li><strong>必读第二场 · 第二卷第十一章（罗斯林斯庄园初次求婚遭拒）：</strong>世界文学史最精彩的舌战交锋，感受男女主角在自尊被刺伤中的电光石火对决。</li>
        <li><strong>必读第三场 · 第二卷第十三章（漫步小径读达西长信）：</strong>精读伊丽莎白从愤怒自辨到无地自容的心智大地震全过程。</li>
        <li><strong>必读第四场 · 第三卷第一章（彭伯利庄园漫游）：</strong>精读自然风光与达西人格美学的绝妙融合，以及管家口中的真实领主肖像。</li>
        <li><strong>必读第五场 · 第三卷第十六章（凯瑟琳夫人逼门大对决）：</strong>精读伊丽莎白面对贵族老妇盛气凌人逼问时，毫不退让捍卫个人尊严的硬核辩白。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 金钱在婚姻中的分量：</strong>伊丽莎白曾开玩笑说自己是在参观了彭伯利庄园后才爱上达西的。抛开玩笑，达西庞大的财产在伊丽莎白由恨转爱的过程中，究竟起到了怎样的催化作用？没有财富支撑的崇高品格在那个时代能维系尊严吗？
      </div>
      <div class="card-box">
        <strong>Q2 · 谁的傲慢？谁的偏见？</strong>达西有傲慢，但他有没有偏见？伊丽莎白有偏见，但她身上是否同样充满了平民知性女性的自负傲慢？
      </div>
      <div class="card-box">
        <strong>Q3 · 夏洛特的选择值得同情吗？</strong>夏洛特为了生存嫁给滑稽可怜的柯林斯，现代读者往往感到窒息，但奥斯汀为何在字里行间对夏洛特的务实智慧给予了不动声色的敬意？
      </div>
      <div class="card-box">
        <strong>Q4 · 班内特先生的父职失误：</strong>班内特先生平日里极其聪明、把愚蠢的妻子当笑料，但他为何对小女儿莉迪亚的放荡不加管束，最终险些断送全家前程？消极的清高算不算一种严重的失职？
      </div>
      <div class="card-box">
        <strong>Q5 · 真正的自省需要多大勇气：</strong>为什么在现实生活中绝大多数人在被证明判断错误后会本能地诡辩抵赖，而伊丽莎白却能在读完信的几分钟内彻底否定自己以往的全部定见？
      </div>"""

    sec13 = """      <div class="sub-heading">① 认知纠偏思维工具：“达西长信自省模型” (The Darcy Letter Audit)</div>
      <p><strong>适用场景：</strong>当你对身边的某个合作者、上司或伴侣产生强烈反感，笃定认为对方‘自私冷酷、故意针对自己’时。<br>
      <strong>第一步（列证据源头）：</strong>写下你得出这个负面结论的最初三个事实证据。问自己：这些信息究竟是你亲眼所见的核心原件，还是从第三方（如韦翰式的流言传话者）口中间接听来的？<br>
      <strong>第二步（做反向归因假设）：</strong>强制假设对方的行为背后存在一个‘完全出于保护大局、遵守纪律或替他人隐忍’的正当理由，尝试重新解释他的冷淡与严苛；<br>
      <strong>第三步（像伊丽莎白一样勇敢认错）：</strong>如果事实证明是你误解了对方，放下虚荣，当面向对方表达坦诚的敬意与和解。</p>

      <div class="sub-heading">② 现实观察实验：“第一印象标签拆解”</div>
      <p>挑选一个你最近刚认识、且‘第一印象非常不好’的人。在一周内主动寻找一次与他单独就某个具体事务深入沟通的机会，记录他在这项事务中表现出的、与你之前给他贴上的标签完全相反的一个优良品质。</p>

      <div class="sub-heading">③ 反讽修辞仿写任务</div>
      <p>模仿奥斯汀自由间接引语那种‘不动声色地借用人物口吻让其自我暴露愚蠢’的幽默风格，写一段三百字‘一个虚荣的自媒体博主在向朋友吹嘘自己如何通过摆拍获取十万点赞’的小品白描（不用骂词，全凭自大言辞让人发笑）。</p>"""

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

print("Round 07 deep Pride and Prejudice ready.")

def get_deep_sense_and_sensibility():
    data = {
        "title_cn": "理智与情感",
        "title_en": "Sense and Sensibility",
        "author_cn": "简·奥斯汀",
        "author_en": "Jane Austen",
        "sub_desc": "奥斯汀成名奠基之作 · 两种女性性格与处世哲学的精微交响与成人礼",
        "hero_quote": "理智与情感并非不可调和的死敌；失去情感的生活是一片荒凉的荒漠，而失去理智的情感则是毁灭性的狂暴风暴。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">简·奥斯汀 (1775–1817)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1811 年匿名出版 / 奥斯汀处女作长卷</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">世态小说 / 道德伦理心理剧</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 18 万字 / 全三卷五十章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 青年婚恋必读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">自我克制节制与激情表达的黄金分割点</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把埃莉诺简单贬为‘冷酷压抑的古板老姑娘’，也不要把玛丽安抬高为‘真性情活泼可爱的浪漫天使’。奥斯汀极其犀利地指出：玛丽安任由自己的悲伤肆虐、在公共场合对人不理不睬，本质上是一种<strong>自私自利的任性</strong>——她沉浸在失恋的自我感动中，却把全家老小的心情当成空气；而埃莉诺在得知爱人早已暗中订婚时强咽下心碎的眼泪，微笑着安慰母亲和妹妹，这才是最高贵、最具利他精神的深沉担当。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 姐妹二人面对情感背叛时截然相反的心理承受机制：</strong>当埃莉诺发现爱德华五年前就已与俗气的露西私订终身时，她选择默默独自承担秘密，不让任何人因她而难堪；当玛丽安遭遇风流少爷威洛比的绝情退信时，她绝食哭嚎、在暴雨中狂奔受寒险些丧命。两种应对方式构成了古典克己哲学与浪漫放纵主义的激烈交锋。
      </div>
      <div class="card-box">
        <strong>② 威洛比在大雨之夜的深夜忏悔戏：</strong>第三卷第八章的传世名场面：在得知玛丽安生命垂危之际，已经为了巨额嫁妆迎娶富婆的威洛比，满身泥浆策马狂奔赶来见埃莉诺。他吐露了自己对金钱奢华生活的贪恋，承认自己为了还清挥霍债务出卖了毕生唯一的真爱。这出充满痛苦的独白，让读者看见了虚荣生活对一个英俊青年的无情侵蚀。
      </div>
      <div class="card-box">
        <strong>③ 布兰登上校如大山般沉默的成年人守护之爱：</strong>中年军官布兰登历经风霜，早年挚爱惨死异乡。他从不夸耀财富，在玛丽安沉溺于威洛比的甜言蜜语时默默隐忍；在玛丽安病重时快马加鞭接来母亲；在爱德华被剥夺继承权时无私赠予教职。这种隐忍、深沉、不求即时回报的爱，构成了全书最坚实的道德基石。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        18世纪末英国德文郡与伦敦。浪漫主义思潮席卷欧洲，青年一代狂热崇拜情感宣泄；奥斯汀坚守十八世纪启蒙理智传统，用手术刀般的幽默剖析任性的代价。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .ss-box { rx: 8; stroke-width: 1.5; }
            .ss-bg-elinor { fill: #1d3557; stroke: #2a4d7a; }
            .ss-bg-marianne { fill: #8c2d19; stroke: #a33b24; }
            .ss-bg-brandon { fill: #2a9d8f; stroke: #40916c; }
            .ss-bg-willoughby { fill: #242930; stroke: #59645f; }
            .ss-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ss-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ss-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ss-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ss-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .ss-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .ss-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="ss-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 姐姐：埃莉诺 (理智 Sense) -->
          <rect x="20" y="25" width="210" height="115" class="ss-box ss-bg-elinor" />
          <text x="125" y="52" class="ss-t-w">埃莉诺 (Elinor · 理智)</text>
          <text x="125" y="72" class="ss-t-sub-w">十九岁长女 · 自律克己 · 顾全大局</text>
          <text x="125" y="90" class="ss-t-sub-w">深知爱德华有密约，强忍心碎维系家庭</text>
          <text x="125" y="108" class="ss-t-sub-w">信守诺言不向任何人泄密</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">终获真爱与体面宁静生活</text>

          <!-- 妹妹：玛丽安 (情感 Sensibility) -->
          <rect x="450" y="25" width="210" height="115" class="ss-box ss-bg-marianne" />
          <text x="555" y="52" class="ss-t-w">玛丽安 (Marianne · 情感)</text>
          <text x="555" y="72" class="ss-t-sub-w">十七岁次女 · 狂热率真 · 鄙视平庸</text>
          <text x="555" y="90" class="ss-t-sub-w">遭威洛比抛弃绝食狂奔身染重病</text>
          <text x="555" y="108" class="ss-t-sub-w">在濒死边缘终于领悟姐姐的高贵</text>
          <text x="555" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">嫁给布兰登上校走向成熟完满</text>

          <!-- 姐妹性格镜像对照 -->
          <path d="M 230 82 L 450 82" class="ss-solid" stroke="#2a9d8f" stroke-dasharray="4,4" />
          <text x="340" y="74" style="fill:#2a9d8f; font-size:11px; font-weight:700; text-anchor:middle;">性格互补与双向教育</text>

          <!-- 负心者：威洛比 -->
          <rect x="20" y="180" width="210" height="135" class="ss-box ss-bg-willoughby" />
          <text x="125" y="208" class="ss-t-w">约翰·威洛比 (Willoughby)</text>
          <text x="125" y="228" class="ss-t-sub-w">英俊风流 · 狂热投契 · 挥霍无度</text>
          <text x="125" y="246" class="ss-t-sub-w">为五万英镑嫁妆抛弃真爱迎娶富婆</text>
          <text x="125" y="264" class="ss-t-sub-w">雨夜忏悔，终生困于无爱金钱婚姻</text>
          <text x="125" y="280" style="fill:#e0725b; font-size:10px; text-anchor:middle;">虚荣软弱男性的真实自毁</text>

          <!-- 真正担当者：布兰登上校 -->
          <rect x="450" y="180" width="210" height="135" class="ss-box ss-bg-brandon" />
          <text x="555" y="208" class="ss-t-w">布兰登上校 (Colonel Brandon)</text>
          <text x="555" y="228" class="ss-t-sub-w">三十五岁退伍老兵 · 身负沧桑深情</text>
          <text x="555" y="246" class="ss-t-sub-w">不言不语默默守护，赠教职救爱德华</text>
          <text x="555" y="264" class="ss-t-sub-w">以如山般坚毅宽厚终得玛丽安敬重</text>
          <text x="555" y="280" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">成熟成年人深沉之爱的最高范本</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>埃莉诺·达什伍德：</strong>全书理智与品格的最高支柱。面对丧父后长兄贪婪扣留遗产、全家沦落海边巴顿小屋的困顿，她精打细算操持生活。当深爱的爱德华因被强势母亲剥夺继承权而陷入绝境、且身负与粗鄙表妹露西的不成熟婚约时，埃莉诺没有哭闹逼迫，而是默默承受长达四个月的心碎隐忍。当得知爱德华重获自由来求婚时，这位平日最克制的姑娘终于失控失声痛哭，展现了深情深锁背后的巨大震撼。</li>
        <li><strong>玛丽安·达什伍德：</strong>浪漫主义时代的狂热牺牲品。她弹得一手好琴，要求心上人必须和自己喜欢同一首诗、热爱同一种落叶风景。遇到威洛比时，她不顾任何世俗礼节，在尚未订婚前就私自接受赠马、甚至擅自去参观未婚夫的私宅。在遭遇背叛后，她任由绝望摧毁身体，在暴雨中狂走导致高烧感染。濒死体验使她彻底醒悟：<strong>把无节制的情感宣泄当做美德，本质上是对身边至亲最自私的折磨</strong>。</li>
        <li><strong>约翰·威洛比：</strong>典型的两面派浪荡子。他并非完全没有真情，在暴雨中抱起摔伤脚踝的玛丽安的一刻他是动心的。但他身上有英国纨绔子弟最致命的弱点——贪图享乐却害怕过苦日子。他不愿放弃猎犬、赛马与伦敦开销，为了五万英镑迎娶了毫不相干的格雷小姐。他是一个为了物质彻底杀死自己良知的可怜懦夫。</li>
        <li><strong>爱德华·费华斯：</strong>腼腆内向、深具责任感的绅士。在十九岁年轻无知时被势利的露西诱骗订立密约，当得知自己如果违约就能娶埃莉诺、守约就会被母亲剥夺封地遗产时，他毅然选择信守诺言宁肯过苦日子。这种‘哪怕自己受苦也绝不践踏诺言’的呆板老实，在奥斯汀笔下赢得了最高的道德赞赏。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>达什伍德老庄园主病逝，家产依照继承法全部归同父异母的长兄约翰所有。在贪婪吝啬的嫂子挑唆下，达什伍德太太与三个女儿被剥夺了原本应得的几千镑年金，只得分文未取地迁居至德文郡偏僻简陋的巴顿小屋。长女埃莉诺在旧宅与嫂子的弟弟爱德华互生深情，但爱德华因家庭门第压力言辞闪烁。迁至新居后，次女玛丽安在山坡雨天滑倒扭伤脚踝，被风度翩翩的年轻地主威洛比英雄救美抱回小屋。威洛比与玛丽安迅速陷入形影不离的狂热恋情，然而正当全家人期盼订婚时，威洛比突然面色苍白借故匆忙离去伦敦，音讯全无。不久，一位俗气势利的外省姑娘露西·斯梯尔向埃莉诺私下炫耀了一个保守四年的惊天秘密——她早已与爱德华秘密订婚，并展示了爱德华赠送的发丝戒指。埃莉诺如遭五雷轰顶，但为了信守对露西不外传的承诺，强忍剧痛对母亲和妹妹守口如瓶。冬日，姐妹二人随詹宁斯太太赴伦敦，在盛大舞会上玛丽安撞见冷淡如冰的威洛比，随后收到威洛比退还情书与发丝的绝情退婚信，并得知威洛比已为了五万英镑聘礼迎娶富家女。玛丽安在极度悲伤中绝食消瘦；爱德华秘密订婚曝光遭母亲剥夺全部财产，其弟继承家业，爱德华却坚决信守婚约不肯抛弃露西。敬佩其操守的布兰登上校无私赠予其德拉福德教职以供糊口。在返乡途中，玛丽安在暴风雨中狂走染上重度热病濒临死亡，威洛比在深悔中雪夜赶来向埃莉诺忏悔。玛丽安大难不死终于醒悟，彻底告别了任性浪漫。此时传来消息：势利的露西见爱德华被剥夺继承权，立刻悔婚改嫁给了拿到财产的爱德华弟弟！重获自由的爱德华飞马赶到巴顿小屋向埃莉诺深情求婚，埃莉诺喜极而泣；玛丽安也在历经岁月沉淀后，真诚地爱上了默默守候在侧的布兰登上校，两姐妹在理智与情感的平衡融合中迎来了各自的幸福归宿。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人在面对剧烈的情感风暴与世俗逆境时，究竟应当放纵本能情绪大肆宣泄，还是应当借助理智的自控守护尊严与他人的安宁”</strong>。奥斯汀证明：没有情感的生活是一片枯井，但没有理智驾驭的情感则是一座吞噬一切的火山；真正的成熟，是让理智去守护深情，让深情在理智中持久发光。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在微雨与壁炉旁展开的双声部古典弦乐重奏：在隐忍克制的剧痛与狂放不羁的任性对照中，感受人类心灵如何学会驯服自私的情绪猛兽，蜕变出最动人的成年担当。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个年轻气盛、容易被情绪牵着鼻子走，把‘随心所欲宣泄’当做真性情，在经历过人际和情感挫伤后渴望学会真正成熟自律的青年读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以埃莉诺为代表的古典自律、利他担当与理性克制 vs 以玛丽安为代表的浪漫放纵、极端自我中心与情绪沉溺。</strong></p>

      <div class="sub-heading">全书戏剧波澜推进链条</div>
      <ol class="num-list">
        <li><strong>第一卷 · 诺兰庄园驱逐与巴顿移居（第一至二十二章）：</strong>诺兰庄园客厅里嫂子步步蚕食将三千镑年金剥削至零；巴顿小屋生活；威洛比骑马救美与骤然不辞而别；露西在灌木林向埃莉诺投下秘密订婚炸弹。</li>
        <li><strong>第二卷 · 伦敦狂澜与残酷退婚（第二十三至三十六章）：</strong>伦敦社交界相逢；舞会上威洛比冷漠闪躲；绝情信送达引发玛丽安崩溃；爱德华秘密订婚曝光被母亲剥夺长子继承权，布兰登上校赠予教职。</li>
        <li><strong>第三卷 · 濒死觉醒与双重圆满（第三十七至五十章）：</strong>克利夫兰庄园大雨成疾，玛丽安命悬一线；威洛比大雨夜狂奔忏悔；露西改嫁胞弟奇案反转；爱德华策马求婚，埃莉诺失声痛哭；两对眷侣在德拉福德携手相守。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第三卷第十一章玛丽安在重病痊愈后坐在巴顿花园小径上的自省长谈：</strong>玛丽安大难不死后，拉着埃莉诺的手悔恨地承认：‘我终于看清了自己过去的行径——我的狂热不仅没有证明我的高贵，反而差点让母亲心碎、差点杀了我自己！从今以后，我要学习你的自律，把精力用来陪伴家人和读书！’这一刻标志着全书‘情感向理智靠拢’的主题终极确立。
      </div>"""

    sec05 = """      <div class="sub-heading">埃莉诺的眼泪：隐忍不是麻木，而是最深的爱</div>
      <p>许多读者误以为埃莉诺不爱爱德华，因为她从未像玛丽安那样在房间里嚎啕大哭。然而奥斯汀在第三卷第三十五章写下了全书最令人心碎也最动人的一幕：当仆人托马斯误传‘爱德华先生已经和露西小姐结婚了’时，埃莉诺面色苍白强撑微笑；然而当爱德华本人突然骑马登门、结结巴巴地解释‘结婚的是我弟弟罗伯特，我依然是自由的，我爱你！’的那一刹那，埃莉诺再也无法支撑那具钢铁般的理智外壳，她冲出客厅扑进房里，爆发出了整部小说中最剧烈、最放纵的号啕痛哭！这串眼泪证明了：<strong>真正的自律从来不是感情的枯竭，而是一座为了保护所爱之人宁愿把自己压出内伤的坚固大坝</strong>。</p>

      <div class="sub-heading">威洛比深夜忏悔的悲剧深度</div>
      <p>第三卷第八章威洛比的深夜自白是奥斯汀罕见的阴郁笔触。这位平日里风光无限的浪荡子，在大雨之夜狼狈不堪地闯入客栈。他承认自己爱玛丽安，但贫困的恐惧使他出卖了灵魂。他得到了豪宅和五万英镑，但妻子专横跋扈、心胸狭隘，他的余生只能在对玛丽安永无休止的悔恨追忆中度过。奥斯汀借他证明：<strong>贪图捷径出卖真情的人，金钱最终会变成锁死其终生幸福的黄金枷锁</strong>。</p>"""

    sec06 = """      <div class="sub-heading">双重修辞对比与精妙的对称文风</div>
      <p>奥斯汀在全书中建立了极其工整的二元对称修辞体系：埃莉诺的台词大量使用动词‘思考、判断、克制、希望’，语调平稳、逻辑严密、多用长复合句；而玛丽安的台词充斥着‘狂喜、痛苦、绝望、狂热’等感叹词与短促反问句。这种形式上的对称性，完美构成了两性心理学的双向镜鉴。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>钢琴与琴谱 (The Pianoforte)：</strong>玛丽安沉溺感性世界的象征媒介。她在琴键上倾注全部的狂喜与哀怨，借音乐构建与现实隔离的脆弱温室，最终也是在钢琴旁完成了精神的成熟转变。</li>
        <li><strong>一绺发丝的戒指 (A Ring of Hair)：</strong>爱德华手中那枚原本属于露西、却被埃莉诺误以为是自己的发丝戒指。它象征着<strong>年轻时欠考虑的轻率誓言如何化作一具沉重的锁链，死死锁住人生的自由选择</strong>。</li>
        <li><strong>巴顿农舍的微小壁炉 (The Hearth at Barton Cottage)：</strong>清贫却温馨的母女避难所。它与诺兰庄园冷酷华丽的石雕大厅形成对照，象征着<strong>物质的匮乏无法剥夺内心的温暖与亲情的凝聚</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（世态婚恋小说）：</strong>达什伍德两姐妹在遭遇财产剥夺与感情双重背叛后，历经波折最终各自寻得理想归宿的家庭世情故事。<br>
        <strong>深层架构（心理学与性格哲学）：</strong>理智（Sense）与情感（Sensibility）的动态平衡。批判无节制情绪宣泄带来的自毁与对至亲的绑架，赞美以利他担当为底色的自制之美。<br>
        <strong>根本架构（文明社会的道德契约）：</strong>人作为社会共同体的一员，必须学会在个人情感自由与承担家庭信义责任之间达成和谐共生。
      </div>"""

    sec08 = """      <div class="sub-heading">解释边界与过度阐释警惕</div>
      <p>切忌将本书生硬地概括为‘理智战胜了情感’。奥斯汀从来没有主张消灭情感——在故事结尾，埃莉诺因真情而收获了爱德华，玛丽安因理智而获得了布兰登的深情。全书的主题不是‘理智消灭情感’，而是‘理智驯化情感、情感丰润理智’。两者缺一不可，偏废任何一方都会走向人生的歧途。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>现代网络文化盛行‘发疯文学’与‘拒绝情绪内耗、谁让我不爽我就让谁难堪’的极端利己主义宣泄，许多人把任性撒泼当做‘独立率真’。玛丽安的悲剧在今天敲响了警钟：毫无克制的情绪发泄并不是勇敢，反而往往是对身边真正爱你的人最残忍的消耗；学会在狂风暴雨中像埃莉诺一样守住心智的定力，才是一个现代人最过硬的心理素质。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在遭遇重大的学业或人际挫折时，你习惯于像玛丽安一样大发脾气、让所有关心你的人为你担惊受怕，还是能像埃莉诺一样先冷静处理实际问题？</li>
        <li>当你为了信守对朋友的一句承诺时，你是否曾哪怕自己承受重大误解也坚决不出卖对方的隐私？</li>
        <li>在选择终生伴侣时，你更倾向于像威洛比那样能给你带来瞬间电击感但缺乏底线的人，还是像布兰登上校那样不善言辞但始终如磐石般可靠的人？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《理智与情感》是教你如何在失恋中活下去的最好教科书。两姐妹同时失恋：姐姐心里流血但咬牙撑住全家，妹妹哭天喊地在大雨里发烧差点丧命。最后姐姐赢得了真爱，妹妹明白了成熟的道理。它告诉你：任性宣泄不是真性情，能扛住事、能体谅别人的自律，才是最高级的深情。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊简·奥斯汀的处女作长卷《理智与情感》。很多人以为这本书是在讲两个女人找对象，其实奥斯汀在探讨一个人成长的终极核心问题：我们该如何对待自己的情绪？达什伍德家有两个女儿：大女儿埃莉诺代表‘理智’，二女儿玛丽安代表‘情感’。老父亲一死，贪婪的嫂子把她们赶到海边一间破旧小屋。姐姐埃莉诺深爱着爱德华，但突然得知爱德华早在四年前就跟别人私定终身了。换作一般人早就闹翻天了，但埃莉诺为了不让母亲和妹妹操心，咬着牙把这口血咽进肚子里，一个人扛下了四个月的心碎。而妹妹玛丽安呢？她爱上了英俊少爷威洛比，整天高谈阔论，把姐姐的自律嘲笑成虚伪。结果威洛比为了五万英镑转头娶了富婆，给玛丽安寄来一封冷血退婚信。玛丽安瞬间崩溃，绝食、哭嚎、大半夜在暴风雨里狂奔，烧成了重度肺炎命悬一线。在快死的那一刻，那个平日里被她嫌弃年纪大、不够浪漫的中年军官布兰登上校，骑着快马在泥水里狂奔去接来她的母亲，而那个风流的威洛比却只能在远方抱着金币痛苦后悔。最后，玛丽安大难不死，彻底看清了自己以前是多么自私任性；而爱德华也因祸得福解除了旧婚约，飞奔赶来向埃莉诺求婚。奥斯汀通过这个故事告诉我们：冲动放纵不是酷，能管住自己的嘴、收住自己的脾气、用肩膀替家人遮风挡雨，才是一个人真正的魅力所在。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “把悲伤当成炫耀的特权，是对他人的冒犯；唯有在沉静中消化苦难的灵魂，才能在岁月深处结出坚固的硕果。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界世态小说奠基之作核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一卷第二章（诺兰庄园客厅削减年金）：</strong>精读贪婪嫂子如何用一套‘巧舌如簧的逻辑’把三千镑年金剥削得一文不剩，体验奥斯汀讽刺艺术的巅峰。</li>
        <li><strong>必读第二场 · 第二卷第四至五章（伦敦舞会退婚信惨剧）：</strong>精读玛丽安目睹威洛比冷漠闪躲与随后收到退还发丝信件的崩溃全景。</li>
        <li><strong>必读第三场 · 第三卷第八章（威洛比雪夜客栈忏悔）：</strong>精读风流少爷在暴风雨中向埃莉诺吐露心声的唯一深情闪光时刻。</li>
        <li><strong>必读第四场 · 第三卷第十一章（玛丽安大难不死自省）：</strong>精读玛丽安向姐姐承认自身自私、宣告心智走向成熟的哲学转折。</li>
        <li><strong>必读第五场 · 第三卷第十五章（爱德华求婚与埃莉诺失声痛哭）：</strong>精读全剧最动人泪崩时刻，领悟克制背后的浩瀚深情。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 情绪宣泄的伦理边界：</strong>玛丽安失恋后沉湎悲伤，甚至拒绝向好心探望的邻居打招呼，这种表现算不算一种以‘真性情’为名的自私道德绑架？
      </div>
      <div class="card-box">
        <strong>Q2 · 埃莉诺的守信代价：</strong>埃莉诺为了信守对情敌露西不泄密的承诺，连亲生母亲和妹妹都瞒着，一个人承受巨大的内耗，这种死守诺言在今天看来究竟是迂腐还是高贵？
      </div>
      <div class="card-box">
        <strong>Q3 · 布兰登上校的爱：</strong>为什么年轻女孩最初往往被威洛比式的轻浮英俊所吸引，却很难看懂布兰登上校那种如磐石般沉稳厚重的爱？
      </div>
      <div class="card-box">
        <strong>Q4 · 威洛比的忏悔：</strong>威洛比冒着大雪狂奔来看望垂危的玛丽安，这证明了他本质上还不算个坏人吗？为什么这种‘迟到的真情’换不来任何实际的救赎？
      </div>
      <div class="card-box">
        <strong>Q5 · 婚姻与金钱的真实关系：</strong>全书不论是埃莉诺还是玛丽安，最终结婚时都仔细算清了彼此的年金收入。奥斯汀为什么如此执着地在小说里写清每一个家庭的具体账目？
      </div>"""

    sec13 = """      <div class="sub-heading">① 情绪管理实操工具：“埃莉诺深呼吸缓冲带” (The Elinor Pause Protocol)</div>
      <p><strong>适用场景：</strong>遭遇职场恶评、突发背叛或极度委屈，第一反应想要拍桌子大骂、发朋友圈宣泄或掀翻局面时。<br>
      <strong>第一步（设二十四小时观察期）：</strong>严格对自己下令：在此刻剧烈充血的脑神经状态下，不做任何公开回复，不发任何文字；<br>
      <strong>第二步（分清事实与感受）：</strong>拿出一张纸，左边写‘客观事实是什么’，右边写‘我此刻的主观受害妄想是什么’，将两者物理剥离；<br>
      <strong>第三步（像长姐一样行动）：</strong>问自己：为了守护大局和长远利益，我现在最具建设性的下一步动作是什么？用建设性行动代替破坏性宣泄。</p>

      <div class="sub-heading">② 现实观察实验：“生活中的威洛比与布兰登辨识”</div>
      <p>在你的日常人际网络中，观察哪一类人属于‘平日里满口高调誓言、但关键利益时刻立刻退缩自保’，哪一类人属于‘平日不善言辞甚至有点木讷、但关键时刻默默替你解决实际麻烦’。建立你自己的识人坐标系。</p>

      <div class="sub-heading">③ 心理对白创作仿写任务</div>
      <p>模仿第三卷第十一章玛丽安病愈自省那种既有真情流露又有冷峻自制的长句节奏，写一段关于‘某人在经历一次重大失败后，坦然向父母或挚友承认自己以往任性与盲目’的真挚独白（350字以内，不用俗套鸡汤词）。</p>"""

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

print("Round 07 deep Sense and Sensibility ready.")

def get_deep_scarlet_letter():
    data = {
        "title_cn": "红字",
        "title_en": "The Scarlet Letter",
        "author_cn": "纳撒尼尔·霍桑",
        "author_en": "Nathaniel Hawthorne",
        "sub_desc": "美国浪漫主义文学开山巨构 · 清教严酷铁律下的罪愆、伪善与灵魂涅槃史诗",
        "hero_quote": "胸前红字的烙印固然沉重，但灵魂深处的自欺却会将生命化为灰烬；做真诚的人吧，向世人坦白你最丑陋的罪恶，哪怕只是展示其中的一角！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">纳撒尼尔·霍桑 (1804–1864)</div></div>
        <div class="spec-item"><div class="spec-label">出版年代</div><div class="spec-val">1850 年出版 / 奠定美国严肃文学地位</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">心理浪漫主义小说 / 道德象征主义杰作</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 16 万字 / 全二十四章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 终身必读道德与思想经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">公开认罪与隐秘负罪的心理对比深刻度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《红字》简单看成一部抨击中世纪通奸罪恶的宗教宣教故事。霍桑在祖上曾是塞勒姆审巫案的铁血法官，他带着深沉的家族原罪感，在这部作品中做出了世界文学史上最惊世骇俗的反向道德实验：<strong>公开佩戴耻辱红字‘A’的海丝特·白兰，在世俗的排斥与苦难中洗尽铅华，最终赢得了灵魂的完全独立、博爱与高贵；而道貌岸然、受万人膜拜敬仰的年轻圣洁牧师狄梅斯代尔，却在隐秘掩盖罪恶中，被内心的懦弱与自责活活折磨成了行尸走肉</strong>。这是一记刺向整个清教道德社会虚伪心窝的致命之剑。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 波士顿集市绞刑台的三次核心出场叙事回环：</strong>开篇第一幕：正午阳光下，白兰怀抱私生女珠儿独立于绞刑台上接受全城万人唾骂；中场第十二章：午夜黑云压顶，身负重疾的狄梅斯代尔独自在黑夜中登上绞刑台自我鞭笞祈求救赎；终场第二十三章：就职大典盛况空前，牧师在万人颂赞中突然撕开胸前衣襟走向绞刑台当众坦白，倒毙在白兰怀里。三次绞刑台构成了全书最严丝合缝的灵魂攀登阶梯。
      </div>
      <div class="card-box">
        <strong>② 齐灵窝斯‘灵魂吸血鬼’式的复仇异化机制：</strong>原配老学者齐灵窝斯并不诉诸世俗法庭，而是化身私人医生潜伏在病弱的狄梅斯代尔身旁。他如同一名恶魔解剖师，每日用言辞刺探牧师的伤口，在对方的心如刀绞中吸食复仇快感。霍桑借他残酷揭示：<strong>当一个人将毕生精力完全投入到对仇敌的折磨中时，施暴者最终会将自己的灵魂也彻底降解为地狱恶魔</strong>。
      </div>
      <div class="card-box">
        <strong>③ 原始森林与严苛集市的二元空间哲学对抗：</strong>集市是清教徒严酷律法、监视耳目与道德审判的冷酷石雕场域；而城外的原始森林，则是大自然未受文明规训、包容一切生机与真情的庇护母体。在森林中，白兰解开被压抑多年的发辫、抛下红字，金发如瀑布般倾泻而下，展现了自然律法对人造教条的崇高超越。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        17世纪中叶北美马萨诸塞清教殖民地（波士顿）。加尔文主义神权政治笼罩全境，教会即政府，律法严酷如铁，凡人的每一个私密举止都被置于神权法庭的严苛审视之下。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .sl-box { rx: 8; stroke-width: 1.5; }
            .sl-bg-hester { fill: #8c2d19; stroke: #a33b24; }
            .sl-bg-arthur { fill: #1d3557; stroke: #2a4d7a; }
            .sl-bg-roger { fill: #131619; stroke: #59645f; }
            .sl-bg-pearl { fill: #2a9d8f; stroke: #40916c; }
            .sl-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .sl-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .sl-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sl-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .sl-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .sl-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .sl-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="sl-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 海丝特·白兰 (公开佩戴红字者) -->
          <rect x="20" y="25" width="210" height="115" class="sl-box sl-bg-hester" />
          <text x="125" y="52" class="sl-t-w">海丝特·白兰 (Hester Prynne)</text>
          <text x="125" y="72" class="sl-t-sub-w">胸前刺绣红字 A · 公开受辱</text>
          <text x="125" y="90" class="sl-t-sub-w">拒不指认情人 · 靠刺绣济贫行善</text>
          <text x="125" y="108" class="sl-t-sub-w">化耻辱为高贵：从‘通奸’到‘天使’</text>
          <text x="125" y="124" style="fill:#f0dcd8; font-size:10px; font-weight:700; text-anchor:middle;">在苦难磨砺中实现彻底精神独立</text>

          <!-- 阿瑟·狄梅斯代尔 (隐秘负罪牧师) -->
          <rect x="450" y="25" width="210" height="115" class="sl-box sl-bg-arthur" />
          <text x="555" y="52" class="sl-t-w">狄梅斯代尔牧师 (Dimmesdale)</text>
          <text x="555" y="72" class="sl-t-sub-w">信众爱戴圣徒 · 私下通奸同谋</text>
          <text x="555" y="90" class="sl-t-sub-w">懦弱隐瞒 · 内疚如烙铁焚烧骨髓</text>
          <text x="555" y="108" class="sl-t-sub-w">深夜绞刑台自我鞭笞 · 终获坦白勇气</text>
          <text x="555" y="124" style="fill:#cad5e2; font-size:10px; font-weight:700; text-anchor:middle;">死前撕开胸膛认罪，完成绝地救赎</text>

          <!-- 隐秘同谋与深爱连线 -->
          <path d="M 230 82 L 450 82" class="sl-solid" stroke="#2a9d8f" stroke-dasharray="4,4" />
          <text x="340" y="74" style="fill:#2a9d8f; font-size:11px; font-weight:700; text-anchor:middle;">隐秘挚爱与罪愆同谋</text>

          <!-- 恶魔复仇者：齐灵窝斯 -->
          <rect x="20" y="180" width="210" height="135" class="sl-box sl-bg-roger" />
          <text x="125" y="208" class="sl-t-w">罗杰·齐灵窝斯 (Chillingworth)</text>
          <text x="125" y="228" class="sl-t-sub-w">原配畸形老学者 · 伪装驻地医生</text>
          <text x="125" y="246" class="sl-t-sub-w">窥伺牧师内心伤口 · 精神凌迟</text>
          <text x="125" y="264" class="sl-t-sub-w">仇敌死后失去寄生宿主，迅速枯萎</text>
          <text x="125" y="280" style="fill:#e0725b; font-size:10px; text-anchor:middle;">被仇恨异化为地狱魔鬼的标本</text>

          <!-- 活生生的红字化身：珠儿 -->
          <path d="M 450 140 L 450 180" class="sl-solid" stroke="#2a9d8f" />
          <rect x="450" y="180" width="210" height="135" class="sl-box sl-bg-pearl" />
          <text x="555" y="208" class="sl-t-w">珠儿 (Pearl · 私生女)</text>
          <text x="555" y="228" class="sl-t-sub-w">野生野长精灵 · 未受清教规训</text>
          <text x="555" y="246" class="sl-t-sub-w">纯真而敏锐 · 活生生的红字图腾</text>
          <text x="555" y="264" class="sl-t-sub-w">父女绞刑台相认，终于流下人类的眼泪</text>
          <text x="555" y="280" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">象征大自然不可屈服的自由生命力</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>海丝特·白兰（Hester Prynne）：</strong>全人类文学画廊中最具神圣傲骨的女性先驱。她怀抱非婚所生的小女婴，平静地站在全镇市民的口诛笔伐之中。她不仅没有被耻辱压垮，反而用一手精美绝伦的金线刺绣，把代表通奸的红色大写字母‘A’装点得如同贵族勋章般华丽耀眼。在随后的七年里，她独居在海边荒凉的孤舍，为全镇的穷人缝补衣物、守护每一个临终的病人。随着岁月流逝，人们惊奇地发现，胸前那个红字‘A’，不再代表‘通奸（Adultery）’，而被全镇民众由衷尊称为‘能干与坚韧（Able）’、甚至‘仁慈的天使（Angel）’。她展现了女性依靠自我劳动与纯洁博爱实现自我救赎的至高力量。</li>
        <li><strong>阿瑟·狄梅斯代尔（Arthur Dimmesdale）：</strong>世界文学中最令人同情又令人叹息的懦弱圣徒。他是牛津大学毕业的高材生，面容英俊、声音充满磁性，布道时能让全场教民泪如雨下。然而，他正是珠儿的亲生父亲。由于缺乏直面世俗惩罚的勇气，他选择了隐瞒。但这种隐瞒给他带来了灭顶的精神酷刑——每当信徒跪在他脚下赞美他是‘纯洁的圣人’时，他内心深处就如同吞下一块滚烫的木炭。他在暗室里用皮鞭抽打自己、在寒冬绝食，在狂乱中于胸口肉体上自残刻下带血的‘A’字。最终，他在宣讲完毕生最辉煌的就职布道后，挣脱齐灵窝斯的毒手走向绞刑台坦白自绝，完成了灵魂的伟大解放。</li>
        <li><strong>罗杰·齐灵窝斯：</strong>深不可测的复仇恶魔。他自幼驼背畸形，早年专注于书斋，娶了年轻的白兰却未能给予其温存。当他在波士顿集市上目睹妻子佩戴红字站桩时，他发誓要查出奸夫。他化名齐灵窝斯作为名医潜伏在狄梅斯代尔身边，以治疗牧师心脏病为名，日夜如同手术刀般挑拨牧师的负罪神经。霍桑深刻指出：<strong>仇恨不仅毁灭受害者，更会彻底把施害者变成一头寄生虫</strong>——当狄梅斯代尔当众认罪死在台上的那一刻，齐灵窝斯发出了绝望的惨叫：‘你从我的手里逃掉了！’失去了复仇寄宿体的他，在一年内像脱水的杂草般迅速干瘪死去。</li>
        <li><strong>珠儿（Pearl）：</strong>全剧最灵动的超现实意象。她是白兰付出了全部名誉与尊严换来的‘无价珍珠’。她未曾受过清教教条的摧残，在大自然与海浪边跳跃成长，眼神敏锐如鹰。她时刻逼问母亲‘胸前的红字是什么意思’、逼问牧师‘是否敢在白天拉着我们的手站在集市中央’，扮演了拷问成人伪善良知的小小上帝使者。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>十七世纪中叶北美波士顿清教小镇，年轻少妇海丝特·白兰因丈夫长年滞留海外失联、却在婚外怀胎生下私生女珠儿，被宗教法庭判处在全镇市民围观下站在绞刑台上示众三小时，并终生在胸前长袍上佩戴象征通奸耻辱的红色大写字母‘A’。在绞刑台前，白兰坚决拒绝向总督和年轻英俊的狄梅斯代尔牧师供出同谋情夫的姓名。此时，被印第安人扣押多年、终于脱险赶到小镇的原配畸形老丈夫罗杰·齐灵窝斯目睹了这一切，他化名驻地医生潜入小镇，私下逼迫白兰发誓隐瞒其真实身份，誓言要揪出奸夫展开残酷报复。白兰获释后，带着珠儿隐居在城郊海边一间破旧木屋，靠一手出神入化的刺绣手艺自食其力抚养女儿，并默默济贫抚恤孤苦，逐渐赢得了全镇的尊重。与此同时，神学声望日隆的狄梅斯代尔牧师身体急速恶化，齐灵窝斯以私人医生身份与其同吃同住，终于在牧师熟睡时扯开其衣襟，窥见了其胸膛肉体上隐秘自残溃烂的红字烙印，开始在暗中对牧师施加长达数年的精神凌迟。在黑夜中备受折磨的牧师登上绞刑台私自忏悔，与归途中的白兰母女在暴雨夜相遇，天空中划过一道巨大的‘A’字流星血光。七年后，白兰在森林中拦住日渐虚弱的牧师，劝其抛弃沉重过去一同乘船逃往欧洲重获自由，牧师在激情的重燃中获得了片刻活力。然而，在全镇最隆重的新总督就职布道大典结束后，回光返照的狄梅斯代尔拒绝了齐灵窝斯的毒爪，在全体教民的惊骇注视下，挽着白兰和珠儿的手毅然登上了白天的绞刑台，当众扯开教袍展示胸膛上带血的红字认罪，在亲吻了女儿珠儿后安详咽气。齐灵窝斯因失去复仇目标在一年内枯竭暴毙，遗嘱将全部巨额财产留给了珠儿；白兰远赴欧洲安置女儿完婚后，晚年自愿重返波士顿小木屋，依然佩戴着那枚红字‘A’安详为求助的女性排忧解难，死后葬在狄梅斯代尔身旁，黑色墓碑上只刻着一行铭文：‘黑底长眠，红字长存’。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃拷问的是<strong>“公开认罪所带来的苦难与救赎，与隐秘伪善所招致的灵魂凌迟之间的巨大反差”</strong>。霍桑证明了：人性的本质是包含瑕疵的，压抑情感的极权宗教律法无法消灭爱欲；在这个世界上，最无可救药的罪恶不是肉体的犯规，而是为了维护体面人设而将同伴推入火坑的伪善自私。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在清教严霜与深林烈火间进行的灵魂审判：在胸前鲜红刺绣的灼烧下，见证一个公开受辱的弱女子如何站成一座独立的道德灯塔，而一个道貌岸然的圣徒如何在伪善的泥潭中艰难爬向光明的绞刑台。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾因犯错而深陷负罪感、在公众目光与隐秘自责中备受煎熬，渴望学会坦诚直面自我过错、重获精神宁静的读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>大自然生机勃勃的原初爱欲与真诚人性 vs 清教极权神权社会的冷酷道德私刑与伪善规训。</strong></p>

      <div class="sub-heading">全书戏剧推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 监狱门与绞刑台（第一至三章）：</strong>橡木铁钉狱门开，黑衣信徒环伺，野玫瑰在门旁盛开；白兰怀抱珠儿登上集市绞刑台，胸前红字A耀眼夺目，原配齐灵窝斯在人群外阴鸷注视。</li>
        <li><strong>第二幕 · 狱中盟约与孤舍针线（第四至八章）：</strong>齐灵窝斯牢房递药，逼立保密毒誓；海边孤木屋的坚韧劳作；总督官邸力争珠儿抚养权，狄梅斯代尔暗中进言保全母女。</li>
        <li><strong>第三幕 · 恶魔与圣徒的同室操戈（第九至十二章）：</strong>齐灵窝斯作为名医贴身窥探；夜探熟睡牧师胸前秘密；狄梅斯代尔深夜独自登上绞刑台，流星在天幕划过猩红‘A’字。</li>
        <li><strong>第四幕 · 森林重逢与金发倾泻（第十三至十九章）：</strong>红字涵义转变为‘能干’与‘天使’；白兰在森林中拦住牧师劝其私奔，摘下红字解开发辫，阳光穿透树林洒满草地，珠儿隔溪逼母重新戴上红字。</li>
        <li><strong>第五幕 · 就职大典与绞刑台绝唱（第二十至二十四章）：</strong>牧师发表毕生最高峰布道，随后在全城惊骇中拒绝逃亡、走向绞刑台当众认罪受死；齐灵窝斯枯竭暴毙；白兰晚年重归小木屋，黑底墓碑红字长存。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第十八章森林深处白兰毅然摘下胸前的红字：</strong>在阳光穿透林木的瞬间，白兰拔掉别针把红字扔进枯叶堆中，解开禁锢多年的发网，金发如瀑布般披散在肩头。这一刻，大自然的原初生命力彻底击碎了清教律法的万千枷锁，证明了‘人类对自由与爱的渴望，永远高于一切人造的教条戒律’。
      </div>"""

    sec05 = """      <div class="sub-heading">红字‘A’的三重涵义演变：从耻辱到圣洁的飞跃</div>
      <p>霍桑在小说中构建了世界文学史上最伟大的象征演变链条：<br>
      <strong>第一阶段：通奸 (Adultery)。</strong>全镇教会与法官将红字烙在白兰胸口，旨在让她成为一具活生生的反面教材，剥夺她的一切社交尊严；<br>
      <strong>第二阶段：能干 (Able)。</strong>白兰没有逃跑，她用精湛的刺绣手艺养活自己，为全镇百姓缝制婴儿襁褓、官员长袍与死者裹尸布。哪里有瘟疫、饥荒与苦难，白兰就带着针线包出现在哪里。人们开始低语：‘这个红字代表了坚强与能干’；<br>
      <strong>第三阶段：天使 (Angel)。</strong>到了第七年，红字已经完全失去了惩戒的毒性，反而散发出神圣的保护光环，哪怕狂徒暴民也不敢侵犯。甚至在外来流浪汉眼中，这个大写红字成了她贵族身份般的圣洁勋章。白兰用自己七年如一日的博爱，彻底重塑了一个词汇的社会定义。</p>

      <div class="sub-heading">狄梅斯代尔的自我救赎：为什么临死前的认罪是唯一的解药？</div>
      <p>狄梅斯代尔原本可以答应白兰的建议，乘船逃往英国或德国重获新生。但霍桑极其深刻地指出：<strong>逃避惩罚并不等于获得自由</strong>。如果他带着隐秘的罪恶逃到欧洲，他依然是一个在内心深处鄙视自己的逃兵。唯有在当年白兰受辱的同一个集市、同一个绞刑台、在全城所有教民的面前撕开胸膛承认自己的软弱，他才真正战胜了齐灵窝斯的恶魔诅咒，找回了作为神圣个体的灵魂完整性。</p>"""

    sec06 = """      <div class="sub-heading">暗影与微光交织的哥特象征主义语言质感</div>
      <p>霍桑开创了独特的<strong>‘暮色浪漫主义（Twilight Romance）’文风</strong>。他自称‘喜欢坐在壁炉炭火即将熄灭、月光从窗外照进地板的交界处写作’。在《红字》中，现实的坚硬物体与幽微的潜意识幻象在半明半暗的光线中奇妙交融：流星划过夜空的血色A光、黑衣服人群边缘盛开的一株带刺野生红玫瑰、镜子中扭曲拉长的红字倒影。这种充满神秘沉郁哲理的诗意语言，给全书镀上了一层永不褪色的古典青铜光泽。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>监狱门旁的野生红玫瑰 (The Wild Rose-Bush)：</strong>全书第一章的第一件物象。在坚硬冰冷、长满铁锈的橡木狱门旁，一株野玫瑰在石缝中绽放芬芳。霍桑写道：‘愿它给走入死牢的囚徒、走出刑场的受难者，带来大自然深沉的怜悯与慰藉。’它象征着<strong>超越一切冷酷律法之上、永远宽恕生命过失的大自然慈悲神性</strong>。</li>
        <li><strong>夜空中划过的猩红流星‘A’：</strong>第十二章牧师深夜站在绞刑台上时天幕划过的巨大流星。自负的清教总管以为那是上帝在赞扬刚刚病逝的总督是‘天使（Angel）’；而牧师却在其中看见了审判自己通奸的火印。它象征着<strong>客观自然物理现象在不同内疚心智中引发的截然不同的投射</strong>。</li>
        <li><strong>黑色墓碑上的红字铭文：</strong>全书最后一句的终极象征：‘在黑色的绝壁大地上，唯有一枚红字闪烁着阴郁的光芒。’它象征着在残酷压抑的历史长河中，真挚的爱与受难的尊严将永世长存。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（清教传奇故事）：</strong>十七世纪北美殖民地中，一个年轻女子因通奸被判佩戴红字示众，原配复仇，同谋牧师隐瞒多年最终在绞刑台认罪死去的悲剧。<br>
        <strong>深层架构（神权社会的极权批判）：</strong>对加尔文清教主义‘严刑峻法、抹杀人性、窥探隐私’的系统性历史解剖。揭示将道德信仰强制升级为国家法律对人类心灵造成的普遍残疾与伪善扭曲。<br>
        <strong>根本架构（罪与罚的形而上救赎）：</strong>人如何面对自身的有限性与道德过失。公开承担痛苦的人在磨难中获得圣洁，掩盖自欺的人在虚荣中走向自毁；唯有真诚直面自我，才能赢得生命最后的平安。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>美国文学宗师亨利·詹姆斯在《霍桑传》中指出：《红字》是美国文学史上第一部真正拥有欧洲古典大师级厚度的杰作。霍桑没有停留在浅薄的反宗教口号上，他深深理解清教先祖对道德纯洁性的执着追求，但他以无比的悲悯证明了：没有仁慈与同情作为支撑的道德纯洁，本身就是世间最残暴的罪恶。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《红字》在当今互联网数字时代拥有了惊人的全新生命力：<br>
      今天网络上动辄由‘道德纠察队’发起的对某位公众人物或普通人的‘全网人肉、公开处刑、在社交账号下打上耻辱标签’的赛博狂欢，正是波士顿集市绞刑台在数字空间的精准还魂。人们迫不及待地想要给别人胸前挂上一枚‘失德、出轨、辱华或不端’的现代红字，借以掩盖自己内心隐秘的自私与平庸。霍桑的警告响彻耳畔：每一个急于向别人扔石块的人，都应当先照照自己的镜子。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的生命中，是否也曾因为害怕受到身边群体或长辈的指责，而选择像狄梅斯代尔那样掩盖某个秘密，并在漫长的日子里承受无休止的内疚煎熬？</li>
        <li>当你在网络上目睹某个被集体声讨、贴上道德耻辱标签的公众事件时，你是否能像霍桑那样，保持一份对个体复杂困境的悲悯与慎思？</li>
        <li>如果命运强加给你某种不可抹去的负面评价或标签，你是否有勇气像海丝特·白兰一样，不怨不尤，用时间与无可挑剔的善行将它重新定义？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《红字》是美国文学的开山王冠。一个女人被当众逼着在胸前戴上耻辱的红字A，但她靠一针一线的善行，硬是把‘耻辱’活成了‘天使’；而那个没被发现的当官情人，却在万人膜拜中被内疚活活逼死。它告诉你：公开面对错误会让人强大，道貌岸然的自欺才是真正的地狱。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊聊被誉为美国文学奠基之作的《红字》。故事发生在几百年前极端保守的波士顿清教小镇。女主角海丝特·白兰因为丈夫失踪多年、自己婚外生了女儿，被宗教法庭抓起来，勒令她一辈子在胸口佩戴一个大写的红色字母‘A’，代表通奸耻辱，并在全城人面前站桩受审。白兰抱紧孩子，面对唾骂坚决不说出情夫是谁。她搬到海边破屋，靠着巧夺天工的刺绣手艺养活自己和女儿，谁家有难她就去帮忙缝衣服照料病人。年复一年，全镇百姓慢慢发现，她胸前的那个红字A，已经不再代表通奸，而代表了‘了不起的天使’！那么，那个真正的奸夫是谁呢？正是小镇上最年轻英俊、受万人爱戴的明星牧师狄梅斯代尔！牧师懦弱不敢承认，但他内心的良知把他折磨得生不如死。更可怕的是，白兰那个畸形的原配老丈夫化名医生潜伏在牧师身边，每天像恶魔一样在暗中用话语刺痛牧师的伤口。牧师每晚用鞭子抽打自己，胸膛的皮肉甚至被自己用烙铁硬生生烫出了一个流血的红字！到了小说第七年，牧师在一场盛大的新官就职典礼上讲完了全城最辉煌的布道，万人欢呼。然而在这个荣耀的巅峰时刻，回光返照的牧师走向了绞刑台，在全场倒吸冷气的惊骇中，他拉着白兰和女儿的手，当众撕开衣襟露出胸膛带血的红字，坦白了自己的罪孽，安详死在白兰怀里。老恶魔因为失去了折磨对象，一年内枯萎死去。白兰晚年重归波士顿，依然佩戴着那枚红字，死后与牧师合葬，墓碑上刻着‘黑底长眠，红字长存’。霍桑借这个故事告诉我们：人活在这个世界上，最大的惩罚从来不是别人给你的枷锁，而是你对自己的撒谎；敢于在阳光下承认错误的人，苦难会把他淬炼成圣徒；而躲在面具下做戏的人，体面终将变成他自己的绞索。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “做真诚的人吧！在这个世界上，没有任何罪恶比戴着圣洁面具欺骗世人更让灵魂感到窒息与枯竭。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：美国浪漫象征主义巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一至二章（狱门与集市绞刑台）：</strong>精读野玫瑰盛开的狱门描写，以及白兰怀抱女婴在万民注视下傲然挺立的开场。</li>
        <li><strong>必读第二场 · 第十二章（牧师夜半私登绞刑台）：</strong>精读狄梅斯代尔在暴风雨夜独自站桩自我鞭笞，天际划过猩红A字流星的惊悚神作。</li>
        <li><strong>必读第三场 · 第十八章（森林中摘下红字）：</strong>精读白兰解开发辫、金发如瀑、大自然阳光重新洒满林地的诗意超越。</li>
        <li><strong>必读第四场 · 第二十三章（就职大典破晓认罪）：</strong>精读全书最高潮，牧师在万人膜拜中走向绞刑台当众扯开教袍展示红字的史诗受难。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 罪恶与成圣的辩证：</strong>如果没有犯下通奸罪、没有佩戴那枚耻辱的红字，白兰在清教社会里是否只会成长为一个循规蹈矩、精神平庸的普通主妇？苦难与边缘化在多大程度上成全了她独立博爱的伟大心智？
      </div>
      <div class="card-box">
        <strong>Q2 · 伪善与内耗的代价：</strong>狄梅斯代尔享受了七年的万人敬仰，但代价是内心的日夜凌迟。这种‘拥有全世界却在暗室里自我厌弃’的体验，与白兰‘被全世界抛弃却在内心坦荡从容’的处境相比，究竟谁更值得同情？
      </div>
      <div class="card-box">
        <strong>Q3 · 齐灵窝斯的悲剧教训：</strong>齐灵窝斯原本是个有学问的长者，但他为什么会一步步蜕化为吸血恶魔？当一个人将毕生价值寄托在‘让仇敌痛苦’上时，仇敌的死亡为什么会带给他自身的彻底毁灭？
      </div>
      <div class="card-box">
        <strong>Q4 · 珠儿的拒绝与接纳：</strong>在森林里，当母亲摘下红字时，小珠儿为什么隔着小溪愤怒尖叫拒绝靠近，直到母亲把红字重新别在胸前才肯相拥？这个小细节蕴含着怎样深刻的心理隐喻？
      </div>
      <div class="card-box">
        <strong>Q5 · 终局黑底红字的诗学：</strong>墓碑铭文‘黑底长眠，红字长存’（On a field, sable, the letter A, gules）到底在宣告什么？是宣布罪恶的不可磨灭，还是赞美坚韧灵魂在黑暗世界里永恒闪耀的光华？
      </div>"""

    sec13 = """      <div class="sub-heading">① 心理疗愈实践工具：“红字脱敏去毒日记” (The Scarlet Letter Exposure Protocol)</div>
      <p><strong>适用场景：</strong>当你因为过去的某个重大过失、被他人贴上的负面标签、或者内心的某种自卑耻辱感而长年抬不起头时。<br>
      <strong>第一步（物理显形）：</strong>把那个最让你恐惧、害怕被别人知道的负面标签（如‘被辞退’、‘离异’、‘挂科’、‘破产’）大写在一张白纸正中央；<br>
      <strong>第二步（赋予新定义）：</strong>像海丝特·白兰一样，列出这个标签带给你的三个未曾预料的礼物（如：彻底看清了谁是真朋友、逼迫自己学会了某项独立生存技能、对自己和他人的脆弱有了极深沉的同理心）；<br>
      <strong>第三步（坦荡面对）：</strong>在信任的伙伴面前，不再闪烁其词掩盖它，而是把它当做生命中淬炼过自己的一枚高贵勋章坦然谈论，让耻辱的毒性在阳光下彻底蒸发。</p>

      <div class="sub-heading">② 现实观察实验：“网络数字红字狂欢觉察”</div>
      <p>观察社交媒体上一场正在发生的‘围攻某人道德失范’的热点事件。记录三位情绪最激烈的攻击者的留言用词，分析他们是否在借指责他人来满足自身的道德优越感，体会霍桑笔下波士顿清教徒的现代心理投影。</p>

      <div class="sub-heading">③ 象征主义场景仿写任务</div>
      <p>模仿霍桑‘将自然天气（如浓雾、暴雨、月光）与人物隐秘心理剧烈呼应’的笔法，写一段关于‘某人在深夜独自向窗外黑夜吐露一个压抑十年的重大秘密’的微型场景（350字以内，意象深沉、带有神秘哥特美感）。</p>"""

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
    print("=== 开始批量写入第 7 轮（傲慢与偏见、理智与情感、红字） ===")
    plan = [
        ("傲慢与偏见", get_deep_pride_and_prejudice),
        ("理智与情感", get_deep_sense_and_sensibility),
        ("红字", get_deep_scarlet_letter),
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
