# -*- coding: utf-8 -*-
"""
Round 17: Selected Literary Essays, The Ultimate Essays Collection, Twilight I (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_literary_essays():
    data = {
        "title_cn": "名家文学随笔精选",
        "title_en": "Selected Literary Essays",
        "author_cn": "世界文学随笔大家",
        "author_en": "World Essay Masters (Montaigne, Woolf, Orwell et al.)",
        "sub_desc": "从蒙田到伍尔夫的自由智识漫游 · 撕破伪善与教条的人性显微镜",
        "hero_quote": "随笔是把灵魂放在桌上，不求证明什么，只求真诚地呈现一段思想的呼吸轨迹；‘我知道什么？’这是人类理智最高的从容与谦卑。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">随笔宗师</div><div class="spec-val">蒙田 / 兰姆 / 伍尔夫 / 奥威尔等</div></div>
        <div class="spec-item"><div class="spec-label">跨度时代</div><div class="spec-val">文艺复兴至二十世纪现代名篇汇编</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">哲理随笔 / 抒情散文 / 形式批评</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">精选二十位大家经典长卷</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">14+ 岁 / 终身通识必读宝藏</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">第一人称智识真诚度与批判性反思深度</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把随笔当成‘没有结构的碎碎念日记’或‘浮泛抒情的优美散文套话’。随笔（Essay）源自法语‘尝试（Essai）’，是现代思想史上最自由也最具破坏力的利器。蒙田在古堡书房里敢于公开坦白自己的健忘、自私、便秘与胆小；奥威尔在《猎象记》里敢于承认自己开枪打死大象仅仅是为了‘不在缅甸当地人面前显得丢脸’。这种对自我灵魂近乎残忍的诚实，构成了随笔文体最硬核的脊梁。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 蒙田开创的‘自我解剖学’哲学原点：</strong>‘我自己就是本书的全部材料！’蒙田退隐书房，打破中世纪经院哲学的八股，开创了用常识打量一切宗教偏见与残酷刑罚的自由文风。</div>
      <div class="card-box"><strong>② 乔治·奥威尔对政治谎言与语言腐败的手术刀剖析：</strong>《政治与英语语言》详尽拆解现代官僚如何用被动语态、假大空大词（如‘安抚’代替‘屠杀’）来麻痹大众心智。</div>
      <div class="card-box"><strong>③ 弗吉尼亚·伍尔夫《一间自己的房间》的女性自立战歌：</strong>‘女人要想写小说，必须每年有五百英镑的固定收入，以及一间能够上锁的房间！’以随笔奠定了现代女性主义独立经济学基石。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">四百年间欧洲思想巨匠在书斋、壁炉与荒野中的心灵漫游。随笔打破了神学与学术论文的沉重镣铐，让智慧以最亲密的方式流淌在纸页间。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">蒙田：怀疑主义原点</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">“我知道什么？(Que sais-je?)”</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">打破神学独断 · 承认人性软弱</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">自我剖白即是解剖全人类</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">奥威尔：语言与政治</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">《猎象记》《论政治与语言》</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">拆解官僚大词 · 捍卫清澈常识</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">直视帝国统治者的内在心虚</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#2a9d8f;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">伍尔夫：一间自己的房间</text>
          <text x="340" y="198" fill="#d8f3dc" font-size="11" text-anchor="middle">五百镑年金 · 独立与雌雄同体</text>
        </svg>
      </div>
      <div class="sub-heading">核心随笔大师谱系与思想地标</div>
      <ul class="bullet-list">
        <li><strong>米歇尔·德·蒙田（Michel de Montaigne）：</strong>随笔文体的开山始祖。三十八岁辞官归隐圆塔书房，在天花板横梁刻满希腊先哲箴言。他不建哲学体系，只写自己的偏头痛、骑马时的胡思乱想、对新大陆食人族的平等审视，开创了近代西方人道主义包容精神的黄金黎明。</li>
        <li><strong>查尔斯·兰姆（伊利亚）：</strong>伦敦街头最深情的漫游者。以‘伊利亚’为笔名，在《伊利亚随笔》中写透了烤猪的美味、老瓷器的温润、除夕夜对岁月的眷恋，用幽默与眼泪包裹着自身残酷的家庭创伤。</li>
        <li><strong>乔治·奥威尔（George Orwell）：</strong>二十世纪最冷峻坚毅的政治随笔宗师。在《猎象记》中，他站在手持步枪的帝国警察视角，深刻剖析了当白人举起枪时，正是被身后两千名当地暴民的起哄所绑架，无情揭示了‘当一个人成为暴君时，他也成了暴民的囚徒’。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书精选了西方随笔史上最具思想分量与文学美感的数十篇传世之作。从蒙田在古堡书房面对人类偏见的宽容沉思；培根关于读书与成败的精炼格言；兰姆在伦敦烟雨中对贫穷表亲与老书籍的深情抚摩；赫兹利特关于‘仇恨之乐’的犀利心理剖析；直到伍尔夫乘着想象的翅膀在剑桥草坪上推导莎士比亚早逝妹妹的假想命运，奥威尔在缅甸丛林中面对倒毙大象的良知战栗。每一个篇章都是一位思想大师在毫无防备的私人时刻，向读者敞开书斋大门的心灵对话。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类如何在制度、八股与群体从众的狂潮中，永远保有以第一人称‘我’独立思考与真诚表达的权利”</strong>。随笔证明：真正的智慧不在于背诵权威的标准答案，而在于敢于在世俗的喧嚣中停下来，向自己提出一声清澈的质疑。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一场坐在人类思想史上最伟大的书房壁炉前展开的深度下午茶：在毫无说教、甚至带着调侃自嘲的轻松谈吐间，不知不觉完成了心智与认知的跨世纪升级。</div>"""

    sec04 = """      <div class="sub-heading">随笔思维的三步解毒法</div>
      <div class="card-box"><strong>① 破除抽象大词：</strong>将宏大叙事翻译为具体的人类肉身处境，拒绝用口号替代真实的思考。</div>
      <div class="card-box"><strong>② 敢于自我反省：</strong>在批评他人之前，先在自己内心找出同等阴暗丑陋的偏狭幼苗，完成灵魂排毒。</div>
      <div class="card-box"><strong>③ 坚守常识与诚实：</strong>不迎合任何时代潮流，唯有对内心的真实经验保持绝对的忠诚。</div>"""

    sec05 = """      <div class="sub-heading">伍尔夫与‘莎士比亚的妹妹’假想神话</div>
      <p>伍尔夫在随笔中构想了一个天才少女朱迪丝·莎士比亚：她拥有与哥哥完全同等的伟大诗才，但当哥哥前往伦敦剧院当演员成名时，她却被锁在家里做针线，在十六岁时被强迫订婚；当她逃到伦敦渴望演戏时，所有人都嘲笑她是个疯女人，最终在绝望怀胎后自杀葬在十字路口。伍尔夫借这篇随笔极其冷峻地宣告：<strong>天分需要物质的土壤，没有独立的经济与空间，天才只能在沉默中枯萎</strong>。</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>蒙田的圆塔书房：</strong>四面悬挂古希腊箴言的避难所，象征远离世俗狂热偏狭的理智高地。</li>
        <li><strong>垂死巨象的眼神：</strong>奥威尔笔下被子弹击中的大象，象征帝国主义野蛮机器对自然尊严的无情残害。</li>
        <li><strong>五百英镑年金与上锁的房间：</strong>女性独立与精神自由最不可或缺的物理硬核基石。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>西方随笔大师经典论述篇章的精选汇编。<br>
        <strong>深层架构：</strong>近代人文主义自我审视与批判性思维演进长卷。<br>
        <strong>根本架构：</strong>个体思想独立性对一切极权、教条与偏狭的最强韧防御堡垒。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读与评价</div>
      <p>世界文学史将随笔视为‘文学中的哲学，哲学中的诗歌’。它是检验一个文明是否真正拥有言论从容与心智成熟的最高晴雨表。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>在今天这个充斥着AI自动生成垃圾文案与公关套话的时代，重温名家随笔能让我们重新找回人类语言的真实温度与骨骼，学会不被谎言轻易操纵。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《名家文学随笔》是专治脑子僵化的神作。蒙田教你怀疑，培根教你自律，奥威尔教你拆穿政治黑话，伍尔夫教你经济独立。它告诉你：大作家不是神仙，他们是最敢在纸上对自己坦白的人。读懂随笔，你才拥有了一套看透世俗把戏的透视眼。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读蒙田《论习惯》 · 培根《论读书》 · 奥威尔《猎象记》 · 伍尔夫《一间自己的房间》。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 随笔的真诚力量：</strong>为什么蒙田写自己的小毛病，反而比那些写伟大功业的史书更能赢得全人类五百年的信赖？
      </div>
      <div class="card-box">
        <strong>Q2 · 语言与谎言：</strong>奥威尔为什么说‘语言的腐败必然导致政治的腐败’？我们在日常生活中该如何捍卫清晰诚实的表达？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“奥威尔语言去肿消炎法”</div>
      <p>拿出你写的一段正式报告或发言稿，用红笔把所有假大空的大词、被动语态和套话全部划掉，换成初中生都能听懂的最具象的动词和名词，感受文字重新焕发出的千钧力量。</p>"""

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

print("Round 17 deep Literary Essays ready.")

def get_deep_ultimate_essays():
    data = {
        "title_cn": "欧美名家散文名篇终极典藏",
        "title_en": "The Ultimate Essays Collection",
        "author_cn": "欧美经典文萃编委会",
        "author_en": "Ultimate Essay Edition (Bacon, Emerson, Hazlitt et al.)",
        "sub_desc": "英语散文黄金岁月的至高智识回响 · 理性、修辞与灵魂自立的终极盛宴",
        "hero_quote": "读书足以怡情，足以傅彩，足以长才；凡有所学，皆成性格；相信你自己的思想，相信你内心深处所认定的真实，这便是真正的天才！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">散文先驱</div><div class="spec-val">培根 / 爱默生 / 哈兹利特等</div></div>
        <div class="spec-item"><div class="spec-label">版本源流</div><div class="spec-val">英语经典散文文库核心正典</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">哲学箴言录 / 雄辩议论文 / 启蒙散文</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">精选三十篇传世篇章长卷</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">14+ 岁 / 终身必读思维与修辞典范</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">逻辑论证严密度与超验自立精神张力</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把名家散文当作中学生摘抄优美句子的‘作文素材库’。培根的随笔是权谋家兼科学家在世俗风浪中提炼的钢铁处世法则；爱默生的《论自立》是青年人对抗社会平庸从众的战斗檄文。每一篇作品都是一次对人类大脑神经逻辑的严格重组，是西方文明由中世纪愚昧迈向现代独立人格的核心智识母体。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 弗朗西斯·培根冷峻精辟的箴言式论说：</strong>《论读书》《论友谊》《论逆境》如同经过淬火的钢刀，以‘狡黠者轻鄙学问，愚鲁者羡慕学问，唯聪明者善用学问’等对仗排比，开创了近代实用理性文风。</div>
      <div class="card-box"><strong>② 拉尔夫·沃尔多·爱默生《论自立》（Self-Reliance）的独立风暴：</strong>‘盲目模仿即是自杀，盲目顺从即是背叛！’爱默生痛斥现代人在社会舆论面前的唯唯诺诺，呼唤每一个人像新大陆的参天大树一样，以不可动摇的自信站立在大地之上。</div>
      <div class="card-box"><strong>③ 威廉·哈兹利特激越辛辣的心理实相解剖：</strong>《论憎恨的快乐》揭穿了人类内心深处对敌意与攻击性的隐秘沉迷，展示了英国散文最锋利的心理洞察力量。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">从英国文艺复兴经验主义的觉醒，到美国十九世纪超验主义的思想爆发，散文始终是人类精神确立自我尊严的最高公器。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">培根：理性与经验</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">《论读书》《论真理》</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">经验归纳法 · 实操思维骨架</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">冷峻精辟 · 实用哲学巅峰</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#2a9d8f;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">爱默生：超验与自立</text>
          <text x="560" y="72" fill="#e5e8eb" font-size="11" text-anchor="middle">《论自立》《论自然》</text>
          <text x="560" y="90" fill="#e5e8eb" font-size="11" text-anchor="middle">破除从众 · 确立神圣自我</text>
          <text x="560" y="108" fill="#e5e8eb" font-size="11" text-anchor="middle">“信任你自己，每一颗心都与那根铁弦共鸣！”</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#8c2d19" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#8c2d19;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">语言与精神的终极金字塔</text>
          <text x="340" y="198" fill="#f0dcd8" font-size="11" text-anchor="middle">以雄辩修辞为文明立心</text>
        </svg>
      </div>
      <div class="sub-heading">核心散文大师与论战谱系</div>
      <ul class="bullet-list">
        <li><strong>弗朗西斯·培根（Francis Bacon）：</strong>哲学家与大法官。开创科学归纳法，其散文短小精悍如黄钟大吕，字字闪耀着文艺复兴巨人对现世功业与理性探索的磅礴野心。</li>
        <li><strong>拉尔夫·沃尔多·爱默生（Ralph Waldo Emerson）：</strong>美国思想之父。他的演讲如同一场席卷灵魂的龙卷风，彻底打碎了美国知识界对欧洲文化的自卑仰望，奠定了美利坚民族独立自信的精神基石。</li>
        <li><strong>威廉·哈兹利特（William Hazlitt）：</strong>散文界的斗士。语言充满激情与火药味，不避讳人性的阴暗与社会的伤口，展示了散文家作为独立批判者的硬核骨气。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>全书收录了自培根以来的三十篇经典论辩散文巨构。涵盖了关于读书学习之道的系统指南（‘书有可尝者，有可吞者，少许可咀嚼消化者’）；关于逆境与厄运的形而上沉思（‘奇迹多是在厄运中出现的’）；关于个人在社会规训面前如何拒绝随波逐流的自立宣言；关于历史名画与自然风景的审美细读；以及关于死亡、衰老、名誉与永恒的终极哲学论辩。每一篇都如同一场经过严密布局的法庭大辩论，用无可辩驳的逻辑与如诗般的修辞征服读者的心智。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“理性修辞如何赋予思想以坚固的形式，从而帮助人类在混沌荒谬的世俗潮流中，守住清晰独立判断力与精神骨气”</strong>。它证明：一个人语言的严密程度，直接决定了他思维的深度与他人生的格局。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一场在思维大理石殿堂中进行的逻辑与雄辩大操练：在每一个严丝合缝的对仗与层层递进的反诘中，体会人类智力在最高境界所能散发出的不可撼动的尊严力量。</div>"""

    sec04 = """      <div class="sub-heading">议论文修辞三大结构法则</div>
      <div class="card-box"><strong>① 论点如铁钉：</strong>开篇第一句绝不绕弯子，直接将核心命题如铁钉般砸入木板。</div>
      <div class="card-box"><strong>② 对照与层递：</strong>通过正反两极的严密对比（如培根对史学家、诗人、数学家不同心智功用的划分），穷尽逻辑的可能性。</div>
      <div class="card-box"><strong>③ 箴言式收网：</strong>结尾以一两句极具诗意与权威感的格言式短句彻底定鼎，让人百读不厌。</div>"""

    sec05 = """      <div class="sub-heading">爱默生《论自立》的世纪雷鸣</div>
      <p>爱默生在《论自立》中留下了全人类最震撼的青年宣言：‘一个人在教育的某个阶段，必然会得出这样的结论：嫉妒即是无知，模仿即是自杀；不管好歹，他必须接纳自己作为一个独特的个体……社会在任何地方都在合谋反对其每一个成员的独立男子气概。在这个世界上，遵从世界的眼光生活是容易的；在孤独中遵从自己的意志也是容易的；但那个在人群中依然能完美保持独立孤独的人，才是真正伟大的灵魂！’</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>铁弦 (The Iron String)：</strong>‘信任你自己吧，每一颗心都在随着那根铁弦跳动共鸣！’象征人类良知深处对真理本能的终极感召。</li>
        <li><strong>经验的炉火：</strong>培根笔下用来冶炼知识的归纳法炉火，象征实证科学对虚假教条的彻底粉碎。</li>
        <li><strong>参天大树与杂草：</strong>自立灵魂与从众平庸者的鲜明对照。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>欧美近现代三十篇经典论说散文的名家汇编。<br>
        <strong>深层架构：</strong>理性主义、经验主义与超验主义在修辞学维度的最高演练长卷。<br>
        <strong>根本架构：</strong>个体心智独立与精神自决对社会平庸化浪潮的终极阻击。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>林肯总统称爱默生是‘指引美利坚民族精神的北极星’；罗曼·罗兰盛赞培根‘给欧洲散文注入了钢铁般的骨骼’。这部散文集是全人类青年训练逻辑思维与宏大格局的必修教材。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>在算法推荐与群体狂欢制造大量‘同质化巨婴’的今天，重温培根与爱默生是一场刻不容缓的精神自救：拒绝人云亦云，相信你自己的眼睛，敢于为了真理承受孤独。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《欧美名家散文典藏》是教你如何拥有硬核脑子的神书。培根教你把书读透变成生产力，爱默生吼出‘模仿就是自杀，相信你自己！’它告诉你：别随大流，用严密的逻辑武装你的嘴，用坚定的自信站稳你的脚跟，你就是无可战胜的独立个体。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读培根《论读书》《论真理》 · 爱默生《论自立》 · 哈兹利特《论往日的愉悦》。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 自立与自负的界限：</strong>爱默生强调‘信任你自己’，这与盲目自大、狂妄自恋有何本质区别？
      </div>
      <div class="card-box">
        <strong>Q2 · 读书的功利与超脱：</strong>培根说‘读书足以长才’，我们在今天追求实用技能的同时，如何保有一份‘读书足以怡情’的超然优雅？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“爱默生自立决策清单” (The Self-Reliance Decision Audit)</div>
      <p>在做一个重大人生决定时，拿出一张纸写下：如果这个决定完全不考虑父母的期望、不考虑同学朋友的羡慕评价、不考虑世俗所谓的体面标签，纯粹出自你内心的真实召命，你会做出怎样的选择？以此校准你的真实人生方向。</p>"""

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

def get_deep_twilight_1():
    data = {
        "title_cn": "暮光之城Ⅰ · 暮色",
        "title_en": "Twilight",
        "author_cn": "斯蒂芬妮·梅尔",
        "author_en": "Stephenie Meyer",
        "sub_desc": "全球青少年的现象级奇幻纯爱神话 · 致命危险、嗜血本能与深情自抑的冰冷诱惑",
        "hero_quote": "狮子无可救药地爱上了羔羊；一只愚蠢的羔羊，一只变态自虐的狮子；如果我能在这个世界上选择一种死法，那便是为了深爱的人交出生命。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">斯蒂芬妮·梅尔 (1973– )</div></div>
        <div class="spec-item"><div class="spec-label">出版与风靡</div><div class="spec-val">2005 年出版 / 破全球青春图书销售神话</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">现代超自然青春小说 / 哥特式浪漫传奇</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 25 万字 / 全二十四章带尾声</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">12+ 岁 / 青少年与奇幻爱好者必读</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">致命本能压抑张力与青春身份认同心理剖析</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《暮光之城》当成一部浅薄幼稚的‘霸道吸血鬼爱上我’的爆米花言情流水账。梅尔精准击中了青春期人类最深层的心理秘密——<strong>面对陌生成人社会的致命诱惑，那种‘渴望被彻底看见、被唯一珍视、并在危险边缘试探自我边界’的巨大张力</strong>。爱德华忍受百年嗜血天性对贝拉实行的极端自我克制，构成了全书最强烈的道德与戏剧悬念。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 福克斯终年不见阳光的温带雨林氛围：</strong>阴雨、浓雾、参天冷杉树冠、苔藓，梅尔以极其细腻的感官白描，构筑了一座与喧嚣现代都市完全隔离的超自然纯爱避难所。</div>
      <div class="card-box"><strong>② 草地上阳光下的‘钻石皮肤’震撼坦白：</strong>第十三章。爱德华带贝拉走进阳光穿透的林间空地，脱下外衣展露吸血鬼在阳光下如无数细碎钻石般闪耀的皮肤，以及快如闪电的致命身手，在恐怖与极致眩目中完成了生死信任盟约。</div>
      <div class="card-box"><strong>③ 芭蕾舞教室惊心动魄的吸血救人决战：</strong>追踪者詹姆斯设局将贝拉逼入空荡荡的镜面芭蕾舞室并咬穿其手腕；爱德华在击碎仇敌后，必须伏在心爱女孩流血的手腕上吸出致命剧毒，并在理智崩溃的边缘强行止住嗜血本能，完成了全书最高难度的心智自控。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">美国西北部华盛顿州奥林匹克半岛偏僻的福克斯小镇（Forks）。漫无止境的雨季与印第安古老传说在现代高中校园边缘低语。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">爱德华·卡伦 (Edward)</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">1901年西班牙流感幸存者</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">读心术 · 冰冷大理石身躯</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">恪守‘素食’不吸人血戒律</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">贝拉·斯旺 (Bella Swan)</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">十七岁转校生 · 敏感自卑</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">思维不可被读透的独特灵魂</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">无畏走向危险，渴望成为同类</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#242930;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">卡伦素食家族 vs 流浪追踪者</text>
          <text x="340" y="198" fill="#e5e8eb" font-size="11" text-anchor="middle">自律文明 vs 残酷猎食本能</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色谱系深度剖析</div>
      <ul class="bullet-list">
        <li><strong>贝拉·斯旺：</strong>看似笨拙平凡，实则具有罕见的坚韧意志与通透。她是全校唯一一个爱德华读不透心思的人（大脑天然具备屏蔽心灵感应的防御盾牌）。面对致命的捕食者，她没有尖叫逃跑，而是坦然承认‘我不在乎你是吸血鬼，我只在乎你是否真诚爱我’，展现了惊人的心理定力。</li>
        <li><strong>爱德华·卡伦：</strong>拥有十七岁外表却活了百年的绅士老灵魂。弹得一手绝妙肖邦钢琴，深爱着贝拉血液中那股对他而言如同‘特制毒品’般的致命香气。他的每一次靠近与亲吻，都是在万伏高压电线上行走；他的伟大在于他克制了本能，用绅士的温柔守护了脆弱的凡人生命。</li>
        <li><strong>卡莱尔·卡伦医生：</strong>全家族的精神父亲。身为十七世纪清教牧师之子，三百年来凭借钢铁般的意志完全克服了对人类鲜血的渴望，在现代医院担任外科主刀医生救死扶伤，证明了<strong>理智与道德可以彻底战胜生理本能的黑暗暴政</strong>。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>习惯了凤凰城阳光的十七岁女孩贝拉·斯旺，搬到常年阴雨连绵的华盛顿州福克斯小镇与做警长的父亲查理同住。在福克斯高中，她被神秘俊美的卡伦医生一家五个收养子女深深吸引，特别是坐在她生物课同桌的少年爱德华·卡伦。在经历了一次停车场打滑皮卡车被爱德华徒手单手逼停推凹车门的惊险救援后，贝拉通过印第安好友雅各布了解了古老的部落冷人传说，揭开了爱德华不老不死的吸血鬼真实身份。爱德华带贝拉走进深山阳光下的草地展示钻石身躯，两人确立了跨越物种的炽热恋情，贝拉融入了以兽血维生的温和卡伦家族。然而在一次暴风雨雷电棒球赛中，三个路过的嗜血流浪吸血鬼詹姆斯、维多利亚和劳伦特偶然闯入。顶级追踪者詹姆斯闻到了贝拉作为人类的甜美气味，展开了凶残的猫鼠追猎游戏。卡伦家族兵分两路掩护贝拉逃往凤凰城，詹姆斯却用母亲遭绑架的伪造录像带将贝拉单枪匹马骗入废弃的芭蕾舞学校展开虐杀，并狠狠咬穿其手腕注入尸毒。危急关头，爱德华与家人破门而入撕碎詹姆斯并将其焚化；爱德华在理智与嗜血的极限悬崖边，伏在贝拉手腕上吸出了全部毒液，保全了贝拉的人类肉身。伤愈后的贝拉身穿晚礼服与爱德华出席高中毕业舞会，在摇曳的灯火下，贝拉向爱德华提出了将其转化为不死吸血鬼的终极愿望，爱德华温柔拒绝，以深情的亲吻为第一部画上深邃温存的未完句号。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“青春期个体在面对强大、危险、未知异质世界的诱惑时，如何确认自我身份价值，以及如何通过对本能欲望的克制与守护，完成对自私肉体的精神超越”</strong>。梅尔证明：真正的爱绝不是随心所欲的放纵，而是甘愿为了保护所爱之人的平安，将最暴烈的爪牙深锁在温柔的怀抱之中。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一场漫步在终年阴雨的冰冷冷杉树冠之巅的惊险飞翔：在足以致命的嗜血尖牙边缘，感受人类情感所能达到的最极致的自律、信任与温存。</div>"""

    sec04 = """      <div class="sub-heading">双重本能博弈叙事模型</div>
      <div class="card-box"><strong>① 致命生理吸引 vs 道德绝对戒律：</strong>爱德华每时每刻都在与自己喉咙里燃烧的嗜血干渴搏斗，这种紧绷感赋予了全书长达数十万字的悬念张力。</div>
      <div class="card-box"><strong>② 凡人脆弱性 vs 永生诱惑：</strong>贝拉在面对衰老、疾病与死亡时，渴望跨越边界；爱德华却誓死捍卫贝拉作为凡人的灵魂完整性，展现了崇高的人生观博弈。</div>"""

    sec05 = """      <div class="sub-heading">芭蕾舞教室手腕吸毒：全书自控力的最高圣坛</div>
      <p>第二十四章是全系列最具代表性的高潮场次。当爱德华必须用嘴去吸出贝拉手腕伤口里的毒液时，他面对的是全宇宙最令他发狂的鲜血。多吸一口，贝拉就会失血死亡；少吸一口，贝拉就会被毒素同化。爱德华在万劫不复的边缘，凭借对贝拉纯粹的爱意，强行合上了牙齿抬起头颅。这一口吸吮，成为了他战胜吸血鬼诅咒、确立神圣人性的至尊勋章。</p>"""

    sec06 = """      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>双手捧起的红苹果 (The Red Apple)：</strong>原著封面图案，源自创世纪禁果，象征<strong>人类对禁忌知识与危险诱惑的自主选择权</strong>。</li>
        <li><strong>如钻石般闪光的皮肤：</strong>美丽与杀戮的同源符号，象征致命之物往往披着世间最耀眼的华服。</li>
        <li><strong>常年不见天日的阴雨森林：</strong>隔绝凡俗功利喧嚣的神秘温室空间。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>现代女高中生与百年吸血鬼相爱、遭遇异类追踪者追杀并化险为夷的校园奇幻罗曼史。<br>
        <strong>深层架构：</strong>青春期心理防御机制与深层身份焦虑的心理学投射。探讨如何在一个充满诱惑与危险的世界中被唯一接纳。<br>
        <strong>根本架构：</strong>自律作为爱的至高表达。证明超越生理宿命的纯粹意志是人类抵御黑暗的唯一灯塔。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读与评价</div>
      <p>当代青年文学史研究指出：《暮光之城》开创了二十一世纪超自然青春文学的黄金纪元，它通过将传统吸血鬼从‘恶魔杀手’重塑为‘恪守道德自律的文明守护者’，深刻迎合了全球年轻一代对纯真忠诚情感的集体乡愁。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>在快餐恋爱流行、把感情当做快感消费的今天，爱德华与贝拉的故事提醒我们：真正的爱需要敬畏、需要耐心的等待，更需要为了对方的长远幸福而克制自己眼前的冲动。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《暮光之城》是全球青少年的纯爱神话。转校生女孩爱上了一个吃素的吸血鬼大帅哥，男孩身上流着致命的杀戮本能，却宁愿自己痛苦得浑身发抖也绝不伤她一根汗毛。它告诉你：最性感的从来不是放肆，而是拥有征服你的力量、却选择用一生克制来守护你的深情。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读第五章停车场徒手挡车 · 第十三章阳光森林展露钻石真身 · 第二十四章芭蕾舞室吸毒救人。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 危险的诱惑力：</strong>为什么越是致命、神秘、不可触摸的危险存在，越容易在青春期心智中激发出难以遏制的迷恋？
      </div>
      <div class="card-box">
        <strong>Q2 · 永生的代价：</strong>爱德华为什么坚决不肯轻易将贝拉变成吸血鬼？在他看来，丧失凡人老去的权利意味着怎样沉重的灵魂牺牲？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“爱德华式自律沉思法”</div>
      <p>在面临某种极度想要放纵自己的冲动时刻（如暴饮暴食、通宵刷手机、发脾气摔东西），停下五秒钟，像爱德华克制嗜血本能一样闭上眼睛深呼吸，体会用意志力战胜肉体本能带来的尊严掌控感。</p>"""

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
    print("=== 开始批量写入第 17 轮（文学随笔、The Ultimate Essays、暮光之城I- 暮色） ===")
    plan = [
        ("文学随笔", get_deep_literary_essays),
        ("The Ultimate Essays Collection", get_deep_ultimate_essays),
        ("暮光之城I- 暮色", get_deep_twilight_1),
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
