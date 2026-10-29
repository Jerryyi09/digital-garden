# -*- coding: utf-8 -*-
"""
Round 16: Mrs. Dalloway, Leaves of Grass, The Colour of Magic (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_mrs_dalloway():
    data = {
        "title_cn": "达洛维夫人",
        "title_en": "Mrs. Dalloway",
        "author_cn": "弗吉尼亚·伍尔夫",
        "author_en": "Virginia Woolf",
        "sub_desc": "单日单城的意识流交响巅峰 · 盛夏伦敦一日的灵魂解剖与生死共振史诗",
        "hero_quote": "她觉得自己非常年轻，然而同时又不可思议地衰老；她像一把小刀穿透所有事物，同时又站在外面旁观；大本钟沉重地敲响了，波浪般的一圈圈铅色圆晕在空气中散开。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">弗吉尼亚·伍尔夫 (1882–1941)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1925 年出版 / 现代主义意识流顶峰</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">单日意识流长篇 / 心理双重视角小说</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 17 万字 / 单日时间结构</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">15+ 岁 / 终身必读文学经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">双重视角共振度与主客观时间交融深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿以为全书只是一个英国上流贵妇去花店买花、准备今晚晚宴的琐碎流水账。伍尔夫巧妙设计了‘达洛维夫人’与一战弹震症退伍老兵‘塞普蒂默斯’作为彼此互为镜像的灵魂双生子——一个在鲜花派对中妥协维持体面，另一个在精神分裂中跳楼自尽捍卫灵魂纯洁。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 大本钟沉重报时声（Big Ben）在全书每一个转折处的回荡：</strong>大本钟敲响时‘一圈圈铅色的圆晕在空气中散开’，象征客观物理时间冷酷无情地切割着每个人的生命，与脑海中翻江倒海的主观心理时间构成剧烈反差。
      </div>
      <div class="card-box">
        <strong>② 塞普蒂默斯跳楼自尽与精神医学权威的冷酷压迫：</strong>一战战场目睹战友被炸成肉泥的年轻老兵，回国后患上弹震症无法感知悲伤。名医布拉德肖爵士以‘比例与秩序’为名企图将其强行关入疯人院，逼得青年在阳光下纵身跳出窗户刺死在铁栅栏上。
      </div>
      <div class="card-box">
        <strong>③ 晚宴高潮处与自杀陌生青年的神圣灵魂共振：</strong>达洛维夫人在盛宴正酣时得知疯子跳楼的死讯，独自走进僻静小房间独处，在一扇窗前看着老人熄灯安歇，突然完全理解了青年的死——‘死是一种抗争，死是一种交流的企图！’
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">一战刚结束不久的1923年6月中旬伦敦盛夏。大英帝国在战后余波中粉饰太平，贵族社交晚宴与退伍老兵的无声创伤在同一片天空下激烈对撞。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">克拉丽莎·达洛维</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">五十岁上流贵妇 · 晚宴女主人</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">买花 · 妥协 · 维持世俗体面</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">在派对与社交中抵抗虚无</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">塞普蒂默斯 (Septimus)</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">一战弹震症老兵 · 精神分裂</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">无法悲伤 · 遭遇名医冷酷规训</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">跳窗自尽，誓死捍卫灵魂纯洁</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#242930;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">大本钟报时声 (Big Ben)</text>
          <text x="340" y="198" fill="#e5e8eb" font-size="11" text-anchor="middle">单日单城 · 双重灵魂隔空相认</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色与双重视角谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>克拉丽莎·达洛维（Mrs. Dalloway）：</strong>五十岁的保守党议员夫人。她优雅、通晓世故，三十年前曾深爱狂热浪漫的彼得·沃尔什，也曾对同性挚友萨莉·西顿怀抱纯洁情愫，但最终选择了嫁给平稳可靠的理查·达洛维。她通过举办一场场完美的晚宴来驱散内心的孤独，在听到陌生疯子自杀后，灵魂迎来了神圣升华。</li>
        <li><strong>塞普蒂默斯·沃伦·史密斯：</strong>一战堑壕战生还的平民文学青年。战友埃文斯在眼前被炸飞，摧毁了他全部的神经系统。意大利妻子卢克蕾齐亚对他满怀深情却无能为力。他听见麻雀用古希腊语在阳光下唱歌，看透了文明的伪善。他的自杀是对强权医学规训的最决绝抗争。</li>
        <li><strong>彼得·沃尔什（Peter Walsh）：</strong>三十年浪荡未成的旧情人。手里永远神经质地握着一把折簧小刀，在客厅重见克拉丽莎时泪流满面，展示了深情在岁月磨损下的执着与荒诞。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>1923年6月一个晴朗明媚的早晨，五十岁的克拉丽莎·达洛维出门为今晚的盛大晚宴亲自买花。漫步在伦敦皮卡迪利街头，大本钟敲响了，记忆的闸门轰然打开。三十年前在伯顿乡庄向她求婚遭拒的旧情人彼得·沃尔什突然从印度归来拜访，引得两人内心波澜万丈。与此同时，年轻的退伍老兵塞普蒂默斯在摄政公园长椅上饱受弹震症幻觉折磨，名医布拉德肖爵士下令将其强行关进精神病院；在医生上门抓捕的前一秒，塞普蒂默斯高呼‘我绝不投降’纵身跃出窗户刺死在铁栏上。当晚，达洛维夫人的晚宴高朋满座，首相与名流云集。名医迟到并带来了塞普蒂默斯自杀的噩耗。克拉丽莎离开喧闹大厅走进僻静小房间，在一扇窗前凝视着对楼熄灯安睡的老太太，忽然与这个死去的陌生青年达成了至圣的精神共鸣——她战胜了死亡的虚无，容光焕发地重新走回大厅，在彼得·沃尔什充满敬畏的目光中，完成了这一天的盛大谢幕。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“现代大都市中个体灵魂的绝对孤立与隐秘连接”</strong>。伍尔夫证明：每个人都是一座孤岛，但在某些神圣的瞬间，通过艺术、死亡与同理心，孤岛与孤岛之间可以在无形的大海深处紧紧相拥。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">在伦敦六月晴空下大本钟铅色钟声的层层荡漾中，体验一把手术刀般锐利的意识流长风，穿透世俗社交的全部浮华，直达人类存在最深处的清明与狂喜。</div>"""

    sec04 = """      <div class="sub-heading">叙事建模与时间交响架构</div>
      <div class="card-box">
        <strong>单日单城结构（June, 1923 in London）：</strong>从清晨买花步入阳光，到深夜两点晚宴散场，严格在十八个小时内，凭借无数人物意识流的自由穿梭、联想与回忆，编织出了一部整整涵盖三十年沧桑历史的心理史诗巨著。
      </div>"""

    sec05 = """      <div class="sub-heading">克拉丽莎的顿悟：死是抗争与交流</div>
      <p>克拉丽莎在小房间里的独白被誉为世界意识流小说的至尊巅峰：‘死是一种抗争，死是一种交流的企图；人们绝望地感到难以触及那个中心，于是在拥抱中失去了它，或者在自欺中放弃了它。而这个青年保全了它，他跳向了死亡，把他的生命完好无损地珍藏了起来！’她从青年的死里汲取了继续活下去的勇气，重新走回阳光之下。</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>大本钟的钟声 (Big Ben)：</strong>不可抗拒的客观物理时间法则，将生命无情推向黄昏。</li>
        <li><strong>彼得的小折刀：</strong>脆弱男性掩饰自卑与焦虑的防御性道具。</li>
        <li><strong>花朵 (Flowers)：</strong>克拉丽莎用来点缀生活、对抗虚无的世俗生机图腾。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>伦敦上流社会贵妇筹办一场盛大晚宴的一日见闻与心理独白。<br>
        <strong>深层架构：</strong>一战战后创伤与大英帝国虚伪体制对异端精神个体的冷酷规训与绞杀。<br>
        <strong>根本架构：</strong>生与死的一体两面。通过他人的死亡确证自身存在的尊严与活着的纯粹狂喜。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>伍尔夫在日记中写道：‘我想在《达洛维夫人》中同时揭示生命与死亡、理智与疯狂；我想批评整个社会体制，并在最平凡的生活中展现其最深处的运作机制。’她以这部杰作彻底确立了世界现代主义小说的至尊席位。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>在今天这个充斥着社交人设、朋友圈打卡与隐秘抑郁焦虑的现代都市里，《达洛维夫人》教我们学会在热闹喧嚣的宴席之余，保留一扇属于自己的‘小暗室窗户’，直面内心的真实与脆弱。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《达洛维夫人》是写现代都市人心理写得最神的一本书。一个五十岁贵妇买花办派对，一个一战老兵精神崩溃跳楼自杀。两人一辈子没见过面，贵妇在派对上听到死讯，却在小黑屋里听懂了青年的痛苦。它告诉你：生活再浮华，唯有内心的真实共鸣能救赎灵魂。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读第一章清晨漫步皮卡迪利街头、彼得登门折刀对白、塞普蒂默斯跳楼、终局小暗室顿悟与重回大厅。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 达洛维夫人的婚姻妥协：</strong>克拉丽莎当年拒绝了激烈的彼得，选择平稳的理查，这种妥协究竟是懦弱还是理智的自我保全？
      </div>
      <div class="card-box">
        <strong>Q2 · 塞普蒂默斯自杀的必然性：</strong>名医布拉德肖代表的所谓‘理性与比例’，为什么反而成为了杀害敏感灵魂的最残暴凶器？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“达洛维夫人单日漫步觉察法” (The Mrs. Dalloway Urban Walk)</div>
      <p>在阳光晴好的日子里，独自在城市核心街道漫步四十分钟，不听耳机，用全部感官记录街头掠过的三道截然不同的陌生人面孔，体会生命在同一时空下奇妙交织的复调共振。</p>"""

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

print("Round 16 deep Mrs. Dalloway ready.")

def get_deep_leaves_of_grass():
    data = {
        "title_cn": "草叶集",
        "title_en": "Leaves of Grass",
        "author_cn": "沃尔特·惠特曼",
        "author_en": "Walt Whitman",
        "sub_desc": "世界自由体诗歌的开天辟地之作 · 肉体神圣、民主大同与宇宙生命力的野性赞歌",
        "hero_quote": "我赞美我自己，我歌唱我自己；我承担的一切，你也必须承担，因为属于我的每一个原子，同样属于你！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">诗圣与游荡者</div><div class="spec-val">沃尔特·惠特曼 (1819–1892)</div></div>
        <div class="spec-item"><div class="spec-label">创作与版本</div><div class="spec-val">1855年自费首版 / 终身重写至临终版</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">现代自由体诗歌集 / 民主泛神论史诗</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">四百余首诗篇长卷巨制</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">14+ 岁 / 终身必读自由之书</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">打破古典格律枷锁与肉体与灵魂绝对平等性</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿带着欧洲宫廷诗歌那种‘押韵、字数整齐、词藻典雅’的陈腐尺子去衡量《草叶集》。惠特曼开创的自由体（Free Verse），把粗野的伐木工、浑身煤灰的机械师、码头脚夫、黑奴、甚至妓女的肉体呼吸感，毫不掩饰地请进了诗歌万神殿。他打破了灵肉二元对立的传统偏见，宣告肉体的每一个毛孔与灵魂同样神圣。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 长诗《自我之歌》（Song of Myself）五十二节的宇宙级放声大唱：</strong>‘我庞大无边，我包容万类！’惠特曼将自我化作一根天线，传导整个新大陆山河大地的磅礴生机。</div>
      <div class="card-box"><strong>② 第六节关于‘什么是草’的传世哲学回答：</strong>草是未曾剪裁的绿旗，是上帝留下的芳香手帕，是泥土的头发；草随处生长，不择贵贱，是最彻底的民主平等象征。</div>
      <div class="card-box"><strong>③ 悼念林肯总统遇刺的绝美抒情挽歌群：</strong>《啊，船长！我的船长！》与《当紫丁香在庭院前绽放》，将政治哀伤升华为春日花开与夜莺啼鸣的宇宙大爱。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">19世纪中叶美国领土西进狂飙突进，南北战争的大流血阵痛中，惠特曼在野草与战地医院的绷带间为新世界唱响自由之歌。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#2a9d8f;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">一叶草 (Grass · 平等)</text>
          <text x="120" y="72" fill="#e5e8eb" font-size="11" text-anchor="middle">卑微坚韧 · 随处生长</text>
          <text x="120" y="90" fill="#e5e8eb" font-size="11" text-anchor="middle">不分阶级、肤色、贫富一视同仁</text>
          <text x="120" y="108" fill="#e5e8eb" font-size="11" text-anchor="middle">大自然至高无上的民主勋章</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">宇宙神性 (Cosmos · 永恒)</text>
          <text x="560" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">肉体与灵魂完全同一</text>
          <text x="560" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">‘凡活着的永远不死，死亡是新生’</text>
          <text x="560" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">群星与原子在血脉中流淌</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#8c2d19" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#8c2d19;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">惠特曼：开放的道路</text>
          <text x="340" y="198" fill="#f0dcd8" font-size="11" text-anchor="middle">敞开怀抱 · 永远向前方进发</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色与意象谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>沃尔特·惠特曼（抒情主体）：</strong>粗犷豪放的游荡诗人。他不穿燕尾服，敞开粗布衬衫领口，赤脚踩在泥土地上。他站在大洋与森林之间，用粗粝响亮的嗓音向全世界大声宣告：每一个人都是平等的宇宙神明！</li>
        <li><strong>普通劳动者群像：</strong>石匠、木匠、铁匠、划船手、母亲、黑奴。在惠特曼笔下，劳动的汗水就是圣水，粗糙的老茧就是功勋章，开创了世界文学中对工农劳动者最真诚热烈的神圣崇拜。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>《草叶集》是一部宏伟庞大的无韵自由诗长卷。从《自我之歌》对肉体、性爱、星辰与平民生命的全面狂欢放歌开始，穿过《桤木小径》中对男性同袍之爱的深情呼唤；走入《桴鼓集》中南北战争战地医院包扎流血断肢的深沉悲悯；再到《当紫丁香在庭院前绽放》对林肯总统的崇高哀思；最终在《告别之歌》中安详面向死亡与大海。惠特曼用一生的笔触，为全人类绘制了一幅包容万类的现代民主生命全景图。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“个体如何在打破阶级与宗教束缚后，完全确立自身肉体与灵魂的绝对尊严，并与整座宇宙的大自然法则融为一体”</strong>。惠特曼证明：生命的本质是自由、流动与无限包容，任何试图用教条矮化人性的企图，终将被野草般奔腾的生命野力彻底冲垮。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一场赤脚奔跑在辽阔无垠北美大草原上的狂风暴雨：彻底撕碎一切礼数与自卑，感受血液在血管里像大河般奔腾咆哮的纯粹野性与崇高自由。</div>"""

    sec04 = """      <div class="sub-heading">自由诗体（Free Verse）的革命性突破</div>
      <p>惠特曼彻底废除了传统诗歌的音步限制与韵尾囚笼，借用《旧约·圣经》诗篇的排比、气势如虹的长排句与呼吸节律，创造了现代诗歌的全新母体。诗句的长度完全由思想的肺活量决定，大开大合，气象万千。</p>"""

    sec05 = """      <div class="sub-heading">‘我包容万类’的宇宙胸襟</div>
      <p>第52节著名的自白：‘如果我自相矛盾吗？好吧，那我就自相矛盾吧！我庞大无边，我包容万类！’惠特曼拒绝用狭隘的逻辑条框束缚生命。人性的丰盈，正在于它包含着光明与阴影、理性与狂乱、崇高与凡俗。敢于全然接纳自己的一切，才是精神成长的最高境界。</p>"""

    sec06 = """      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>草叶 (Leaves of Grass)：</strong>民主与生生不息的最高图腾。</li>
        <li><strong>开放的道路 (The Open Road)：</strong>不设门槛、向所有人敞开的自我探索之旅。</li>
        <li><strong>紫丁香与西方落星：</strong>对林肯总统最深沉壮丽的春日挽歌象征。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>新大陆自然风光、平民劳作与战火创伤的自由体诗歌巨著。<br>
        <strong>深层架构：</strong>肉体与灵魂、民主与平等的系统哲学立宪。<br>
        <strong>根本架构：</strong>宇宙泛神论与生命不朽的永恒赞歌。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>爱默生在读完首版后激动致信惠特曼：‘我向你在伟大事业开端致敬！’《草叶集》被公认为现代美国文学的独立宣言与世界现代诗歌的源头活水。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>在今天被焦虑、自卑与内耗困锁的时代，重读惠特曼能给灵魂注入一股洪荒般的野性定力：去赞美你的身体，去热爱你的劳动，在大地上昂首挺胸从容前行。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《草叶集》是全世界最提气、最自由的诗歌神作。惠特曼不搞风花雪月，他把工人、大洋、汗水甚至肉体的每一个毛孔全写成了诗。他大喊：‘我赞美我自己，我庞大无边包容万物！’它告诉你：你身上的每一个原子都无比神圣，别自卑，站直了活下去！”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读《自我之歌》第1、6、52节 · 《啊，船长！我的船长！》 · 《向曼哈顿致敬》。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 为什么草叶是民主的象征？</strong>草叶随处生长、不择贵贱，这种大自然特质给人类社会平等提供了怎样的神圣隐喻？
      </div>
      <div class="card-box">
        <strong>Q2 · 肉体与灵魂的关系：</strong>惠特曼为什么坚决拒绝贬低肉体？为什么说赞美健康的肉体是现代精神解放的第一步？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“自我之歌能量充电朗诵法”</div>
      <p>在清晨或感到极度疲惫气馁时，站在开阔处，用最大肺活量大声朗诵《自我之歌》第一节：‘我赞美我自己，我歌唱我自己！’体会声音震颤胸膛带来的生命原力苏醒。</p>"""

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

def get_deep_colour_of_magic():
    data = {
        "title_cn": "魔法的颜色",
        "title_en": "The Colour of Magic",
        "author_cn": "特里·普拉切特",
        "author_en": "Terry Pratchett",
        "sub_desc": "碟形世界开天辟地第一卷 · 奇幻文学界最伟大的后现代解构神话与黑色幽默狂欢",
        "hero_quote": "这个世界之所以荒唐，是因为统治宇宙的法则根本不是严肃的逻辑，而是一群神明在闲极无聊时掷下的骰子；逃跑不仅是一种生存技能，更是一门高尚的艺术。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家与爵士</div><div class="spec-val">特里·普拉切特 (1948–2015)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1983 年出版 / 碟形世界传奇开端</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">幽默讽刺奇幻 / 概念解构小说</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 16 万字 / 四大章节连贯大冒险</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">12+ 岁 / 终身必读奇幻解压神作</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">严肃奇幻套路颠覆度与世态政治讽刺锐度</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《魔法的颜色》当成轻浮廉价的‘恶搞打怪流水账’。普拉切特爵士以极其惊人的智识储备，对托尔金式的严肃史诗奇幻、洛夫克拉夫特克苏鲁神话、现代跨国旅游业、火灾保险欺诈、冷血官僚主义以及量子物理学进行了入木三分的狂欢式解构。被誉为‘奇幻界的马克·吐温与伏尔泰’。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 恢弘瑰丽至极的‘碟形世界’宇宙模型：</strong>一只身长一万英里的星际巨龟大阿图因在虚空中缓缓游弋，龟壳上驮着四头巨象，象背上顶着扁平如碟的旋转大陆；海水在边缘倾泻为无尽瀑布，折射出超越人类肉眼光谱的第八种颜色——八元色（Octarine）。</div>
      <div class="card-box"><strong>② 全宇宙最糟糕却最懂生存的巫师灵思风：</strong>魔法学校垫底学徒，全身上下只会一门技艺——拼死逃跑！脑子里寄居着一个八级创世大禁咒，导致他连最基础的点火法术都学不会。然而正是他的自知之明与不逞能，一次次在神仙巨怪神仙打架中奇迹生还。</div>
      <div class="card-box"><strong>③ 百足智梨木行李箱（The Luggage）的呆萌与凶残：</strong>长着无数条密密麻麻小短腿的储物箱，刀枪不入水火不侵，能吞噬一切敌人并自动吐出洗得干净折叠整齐的衬衫，成为奇幻文学史上最深入人心的标志性萌宠神武。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">20世纪80年代欧美严肃奇幻泛滥陈腐，普拉切特以解构主义笑声为整个类型文学注入了颠覆性的新活力。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">碟形世界 (Discworld)</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">巨龟阿图因 · 四大巨象</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">扁平大陆 · 边缘瀑布落空</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">第八种颜色：魔法八元色</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">双花 (Twoflower · 游客)</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">阿盖森帝国小职员 · 戴大眼镜</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">天真烂漫 · 笃信世界充满美</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">百足智梨木行李箱忠诚护主</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#2a9d8f;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">灵思风 (Rincewind · 巫师)</text>
          <text x="340" y="198" fill="#d8f3dc" font-size="11" text-anchor="middle">逃跑宗师 · 擅长在荒谬中活命</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色与奇幻反讽谱系</div>
      <ul class="bullet-list">
        <li><strong>灵思风：</strong>身穿褪色红袍、上面歪歪扭扭用亮片绣着‘Wizzard’（甚至把法师单词都拼错了）的丧气巫师。他厌恶一切冒险，毕生梦想是安安静静当个图书管理员；然而命运却一次次逼他跨过悬崖、掉入太空，展现了小人物在荒诞宇宙中顽强求生的伟大狡黠。</li>
        <li><strong>双花：</strong>全宇宙第一个自费观光游客。他拥有坚不可摧的‘天真防线’——当巨龙喷火、劫匪拔刀时，他欢快地拿出画妖照相机要求合影并给小费；当全城陷入火海时，他赞叹这是一场‘盛大的免费焰火晚会’。这种纯真在残酷世界里产生了不可思议的因果奇迹庇护力。</li>
        <li><strong>百足行李箱：</strong>由极具灵性的智梨木打造。无论主人掉进深渊还是外星维度，它总能用数百条小短腿飞速小跑穿透时空追赶上来，是全书最让人捧腹大笑的忠犬型凶悍杀器。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>在遨游星空的巨龟阿图因背上，坐落着扁平的碟形世界。全宇宙第一个自费游客双花带着装满纯金币的百足智梨木行李箱降落在双城安克-莫波克港口。胆小怯懦的半吊子巫师灵思风受雇担任导游保镖。双花向当地酒馆老板无意灌输了‘火灾保险’的概念，贪婪的老板误以为‘只要投保后烧掉客栈就能大发横财’，引爆了席卷全城的连环纵火案，全城化为焦土。两人由此展开了一场横跨碟形世界的亡命大逃亡：先后坠入克苏鲁怪物盘踞的神庙神魔棋盘、被倒转重力的飞龙城堡囚禁、在世界边缘的瀑布悬崖前被渔网捞起，最终乘坐一艘原本企图探索大龟性别的宇宙飞船滑出世界边缘，跌入深邃太空。全书在脑洞大开、笑料百出的惊险狂欢中，为整个庞大的碟形世界宇宙拉开了辉煌序幕。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“用幽默与笑声解构人类一切自高自大的权威、教条与偏执”</strong>。普拉切特证明：人类建立的严肃系统（经济学、官僚制、宗教神话）本质上充满了荒唐漏洞；唯有保持一份不逞能的自知之明与对未知的乐天好奇，人类才能在荒谬的宇宙中平安幸存。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一场骑在星际巨龟背上飞驰的后现代脱口秀大狂欢：在令人喷饭的英式反讽与奇绝设定中，笑看人类的一切狂妄在浩瀚星辰间化作快乐的泡沫。</div>"""

    sec04 = """      <div class="sub-heading">后现代奇幻解构四大法则</div>
      <div class="card-box"><strong>① 崇高英雄神话的降维解构：</strong>英雄柯南式的野蛮人战士在书中被写成装假牙、患风湿、整天担心养老金的老汉。</div>
      <div class="card-box"><strong>② 现代商业概念在魔法世界的乱入：</strong>当保险精算师的概率论掉进一个充满魔法的城市，直接引发了全城纵火骗保的经济危机。</div>
      <div class="card-box"><strong>③ 神明的荒谬棋局：</strong>诸神在云端并非严肃的道德裁判，而是围坐在一起摇骰子打桌游，凡人的命运不过是骰盅里的点数。</div>"""

    sec05 = """      <div class="sub-heading">灵思风的生存哲学：逃跑作为一门至高艺术</div>
      <p>灵思风是世界文学中最反套路的英雄。他从不拔剑，遇到危险第一秒拔腿就跑。他有一句名言：‘只要你能跑得足够快，你就永远不会死在敌人的剑下。’普拉切特借他撕碎了中世纪骑士文学虚伪的自杀式荣誉感：在荒谬的暴力面前，保全生命去体验人间的清晨与奶酪，比无谓地变成一具英雄烈士尸骨要高贵得多。</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>星际大龟阿图因 (Great A'Tuin)：</strong>在虚空中孤独游弋的巨龟，象征荒谬宇宙背后深不可测的自然承载体。</li>
        <li><strong>八元色 (Octarine)：</strong>只有巫师才能看见的带有绿色荧光的魔法颜色，象征超越世俗肉眼可见经验之外的灵性想象力。</li>
        <li><strong>边缘瀑布 (The Rimfall)：</strong>海水倾泻进太空的万丈绝壁，象征探险家直面虚空、打破认知边界的终极悬崖。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>一个倒霉巫师护送天真游客横穿扁平世界的爆笑奇幻冒险奇谭。<br>
        <strong>深层架构：</strong>对西方传统史诗奇幻陈腔滥调与现代文明制度荒谬性的系统后现代解构。<br>
        <strong>根本架构：</strong>在荒诞无序的宇宙大骰子面前，以幽默笑声与求生韧性确立凡人存在的无上从容。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>英国《卫报》盛赞普拉切特：‘他是整个英语文学史上最伟大的讽刺大师之一，他的碟形世界不仅仅是奇幻，它是二十世纪末对全人类文明运作机制最敏锐的显微镜。’</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>面对现代社会的各种假大空口号与浮夸表演，学会像普拉切特那样哈哈大笑；保持灵思风式的清醒生存韧性，保有一份双花式的纯真好奇心，生活便处处都是奇迹。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《魔法的颜色》是全人类最搞笑的奇幻神作。世界是一只大乌龟驮着四头大象背上的扁平大碟子。全宇宙最怂的逃跑巫师，带着一个长着一百条腿的实木行李箱和天真游客大逃亡。它告诉你：别把生活过得太严肃，在荒唐的人间，笑声才是最强的魔法。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读开篇巨龟宇宙模型描写、火灾保险骗保纵火案、边缘瀑布悬崖飞船跌落终局。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 为什么灵思风比肌肉猛男更受读者喜爱？</strong>这种反英雄小人物的走红，反映了现代读者对传统救世主叙事怎样的厌倦？
      </div>
      <div class="card-box">
        <strong>Q2 · 幽默的解构力量：</strong>为什么极权与偏狭最害怕的就是大众的笑声？幽默在捍卫思想自由中具有怎样独特的杀伤力？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“碟形世界荒谬降维解压法”</div>
      <p>在职场中遭遇极其繁琐的形式主义流程或官僚作风时，在脑海中把这套流程置于碟形世界的大陆上，脑补如果双花和他的百足行李箱闯进来会引发怎样的混乱笑料，用幽默的滤镜瞬间化解内心的焦虑毒素。</p>"""

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
    print("=== 开始批量写入第 16 轮（达洛维夫人、草叶集、魔法的颜色） ===")
    plan = [
        ("达洛维夫人", get_deep_mrs_dalloway),
        ("草叶集", get_deep_leaves_of_grass),
        ("魔法的颜色", get_deep_colour_of_magic),
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
