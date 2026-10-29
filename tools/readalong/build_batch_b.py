#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch B: Realism & European Masterpieces (13 books)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT
from build_batch_a import render_book_guide

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

BOOKS_B = {
    "红与黑": {
        "title_cn": "红与黑", "title_en": "Le Rouge et le Noir",
        "author_cn": "司汤达", "author_en": "Stendhal",
        "sub_desc": "批判现实主义文学的奠基丰碑 · 阶级藩篱下的野心与狂澜",
        "hero_quote": "我的罪行是残暴的，但我并不请求宽恕；我的真正罪名，是作为一个贫贱平民，竟敢反抗自己的低下地位！",
        "year": "1830 年出版", "genre": "心理分析小说 / 政治讽刺长篇",
        "length": "约 35 万字", "age": "15+ 岁 / 青年与思辨必读",
        "criteria": "平民青年野心受挫与阶级固化悲剧",
        "warning": "切勿把于连简单定义为‘卑鄙的于连式个人奋斗者’。司汤达写出了法国复辟王朝时期平民青年的普遍窒息感。于连的虚伪，是整个充满虚伪的上流社会逼迫一个天才青年穿上的生存防护铠甲。",
        "highlights": [
            "红（拿破仑军旅热血）与黑（天主教黑袍教职）的时代双重道路抉择。",
            "于连在法庭上掷地有声的阶级自辩绝响。",
            "德·瑞纳夫人的纯洁牺牲与玛蒂尔德的浪漫主义决绝。"
        ],
        "context": "1830年波旁王朝复辟时期，贵族与教会重新垄断权力与阶层通道，平民青年无论多有才华都无法突破阶级天花板。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">于连·索雷尔 (Julien)</text>
          <text x="340" y="68" fill="#cad5e2" font-size="11" text-anchor="middle">平民天才木匠之子 · 崇拜拿破仑</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">德·瑞纳夫人 (Vergy)</text>
          <text x="130" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">母性式的崇高纯爱 · 精神绿洲</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">玛蒂尔德小姐 (Paris)</text>
          <text x="550" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">侯爵千金 · 贵族虚荣与狂热反叛</text>
          <line x1="250" y1="70" x2="160" y2="140" stroke="#2a9d8f" stroke-width="2" />
          <line x1="430" y1="70" x2="520" y2="140" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("于连", "敏感骄傲的平民智者", "精通拉丁文与拿破仑战史，在贵族门第前饱受自尊折磨，终在断头台上找回内心的真实。"),
            ("德·瑞纳夫人", "古典优雅的虔诚贵妇", "在家庭冷漠中被于连的真性情唤醒，死前在于连狱中倾注了无条件的挚爱。"),
            ("玛蒂尔德", "渴望历史英雄主义的贵族小姐", "爱上于连是出于对平庸贵族男子的蔑视，抱着于连的断头展现了惊心动魄的古典决绝。")
        ],
        "perception": "表面是一个底层青年靠才华与情网向社会上层攀爬的个人奋斗悲剧；深处解剖了制度固化如何将最优秀的平民才俊扼杀在萌芽之中。",
        "conflict": "平民对平等与尊严的渴望 vs 贵族阶层对血统特权的垄断；真挚的情感投入 vs 冷酷的功利计算。",
        "turning_point": "德·瑞纳夫人在教会忏悔神父逼迫下写给拉莫尔侯爵的告发信：那一纸信笺斩断了于连即将获封军衔步入顶层的阶级跳跃，激怒他拔枪冲向维里埃教堂。",
        "symbols": [
            ("红与黑：", "红代表拿破仑军旅的平等建功梦，黑代表波旁复辟教权社会的压抑晋升通道。"),
            ("断头台：", "阶级绞杀的终点，亦是于连摆脱一切世俗伪装、获得纯粹精神平静的涅槃台。")
        ],
        "themes": "阶级壁垒与青年发展的不可调和矛盾；虚伪文明对真实灵魂的异化；爱与野心的生死纠缠。",
        "socratic": "Q1：如果于连完全不伪装，他在那个复辟时代的法国有可能活过三十岁吗？\nQ2：于连在法庭上放弃求生机会主动激怒贵族陪审团，这种‘自杀式演说’体现了他怎样的傲骨？",
        "action": "社会观察：反思现代社会的‘学历内卷’与‘出身门第’，分析青年在面对上升通道变窄时，如何避免陷入于连式的极端自毁。"
    },

    "包法利夫人": {
        "title_cn": "包法利夫人", "title_en": "Madame Bovary",
        "author_cn": "居斯塔夫·福楼拜", "author_en": "Gustave Flaubert",
        "sub_desc": "客观现实主义的至高杰作 · 浪漫主义幻想与庸俗现实的绝命撕裂",
        "hero_quote": "语言就像一架破裂的锣，我们敲着它想感动天上的星辰，却只配拿来给熊跳舞。",
        "year": "1856 年出版", "genre": "批判现实主义 / 女性心理悲剧",
        "length": "约 24 万字", "age": "15+ 岁 / 青年与成人经典",
        "criteria": "审美幻想脱离生活基础导致的财务与肉体双重破产",
        "warning": "不要把爱玛简单斥为‘不守妇道的虚荣女子’。福楼拜痛心疾首揭示的，是一种深刻的现代精神疾病——‘包法利主义’（Bovarysme）：一个人总是无力认同自己的真实生活，执迷于大众流行文化制造的虚假幻觉，最终被庸俗的商业世界彻底吸干吃净。",
        "highlights": [
            "福楼拜‘客观而冷漠’、精雕细琢每个字词的纯金文风。",
            "农展会上官僚演讲与情夫偷情絮语交错并置的蒙太奇神笔。",
            "高利贷商人勒合一步步布下财务陷阱将爱玛逼上绝路。"
        ],
        "context": "19世纪中叶法国小资产阶级平庸平淡的乡村生活，浪漫主义流行读物向青年女性兜售不切实际的奢华爱情幻想。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">爱玛·包法利 (Emma)</text>
          <text x="340" y="68" fill="#f0dcd8" font-size="11" text-anchor="middle">追求巴黎罗曼蒂克 · 债务与绝望</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">查理·包法利 (Charles)</text>
          <text x="130" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">平庸笨拙的乡镇医生 · 盲目深爱</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#242930" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">罗多尔夫 / 莱昂 / 勒合</text>
          <text x="550" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">浪荡地主 · 软弱律师 · 嗜血高利贷</text>
          <line x1="250" y1="70" x2="160" y2="140" stroke="#1d3557" stroke-width="2" />
          <line x1="430" y1="70" x2="520" y2="140" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("爱玛", "修道院读通俗小说长大的农家女", "渴望天鹅绒、狂热激吻与异国远航，却被困在阴郁的永维镇，最终服砒霜惨死。"),
            ("查理", "老实木讷的平庸伴侣", "毫无情趣与过人才华，但对爱玛怀有文学史上最深沉、最毫无防备的宽厚之爱。"),
            ("药剂师郝麦 (Homais)", "小市民市侩哲学的终极胜利者", "投机钻营、空谈科学与进步，最后荣获十字勋章，象征庸俗社会的至高加冕。")
        ],
        "perception": "表面是一桩外省医官太太的偷情破产丑闻；深处揭示了现代消费主义与虚假流行文化如何精神毒害普通人的真实生活。",
        "conflict": "浪漫激越的诗意幻景 vs 寡淡窒息的平庸现实；肆意挥霍的欲望 vs 铁板一块的债务契约。",
        "turning_point": "爱玛请求罗多尔夫施舍三千法郎还债遭拒：情夫的冷酷推托彻底粉碎了所谓‘至死不渝真爱’的最后遮羞布。",
        "symbols": [
            ("查理怪异的帽子：", "开篇由各种皮革、布料拼凑的滑稽大帽，象征其平庸笨拙的人格胎记。"),
            ("盲人乞丐的沙哑歌声：", "爱玛临终弥留之际窗外传来的刺耳歌声，象征命运对虚假诗意最粗暴的嘲讽。")
        ],
        "themes": "理想化幻想与严酷现实的毁灭性错位；小资产阶级平庸哲学的普遍泛滥；消费与债务对生命的绞杀。",
        "socratic": "Q1：福楼拜为何说‘包法利夫人就是我自己’？我们每个人身上藏着多少爱玛式的‘消费幻想’？\nQ2：查理发现了所有情书后，为何依然选择原谅并抱着爱玛的画像郁郁而终？",
        "action": "消费心理排查：列出过去半年你购买的某件物品，问自己：你买它是因为它真实有用，还是被它宣传的‘某种优雅生活方式’催眠了？"
    },

    "呼啸山庄": {
        "title_cn": "呼啸山庄", "title_en": "Wuthering Heights",
        "author_cn": "艾米莉·勃朗特", "author_en": "Emily Brontë",
        "sub_desc": "英国文学中最具原始野性之作 · 旷野石南间的超越生死之恋",
        "hero_quote": "无论我们的灵魂是什么做成的，他和我的都是同一种材料；而林顿的灵魂就像月光和闪电，或者霜与火那样截然不同。",
        "year": "1847 年出版", "genre": "哥特浪漫小说 / 复仇史诗",
        "length": "约 30 万字", "age": "14+ 岁 / 青年与成人必读",
        "criteria": "原初狂野激情与文明规训的终极冲突",
        "warning": "切勿把希斯克利夫当作霸道总裁或深情男主。他是一个遭受种族侮辱、童年虐待后，用毕生精力对两个家族展开残酷经济吞并与精神折磨的冷血恶魔。但他对凯瑟琳超越肉体与生死的精神同一性，具有撼动天地的悲剧崇高力量。",
        "highlights": [
            "双层叙事框架：洛克伍德先生与女管家丁奈莉的口述回忆视角。",
            "呼啸山庄（狂风呼啸的原始旷野）与画眉田庄（文明优雅温室）的鲜明空间对立。",
            "希斯克利夫掘开凯瑟琳墓穴要求死后棺木相通的震颤绝唱。"
        ],
        "context": "约克郡荒凉严酷的高沼地，维多利亚文明中阶级规训与人类原始野兽天性的激烈交锋。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="40" y="30" width="200" height="95" rx="8" fill="#131619" stroke="#8c2d19" stroke-width="2" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">呼啸山庄 (Wuthering Heights)</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">狂野高沼 · 原始野性 · 复仇绝地</text>
          <text x="140" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">希斯克利夫 (Heathcliff)</text>
          <rect x="440" y="30" width="200" height="95" rx="8" fill="#fbf9f4" stroke="#1d3557" stroke-width="2" />
          <text x="540" y="60" fill="#1c221e" font-weight="700" text-anchor="middle">画眉田庄 (Thrushcross Grange)</text>
          <text x="540" y="80" fill="#59645f" font-size="11" text-anchor="middle">优雅温室 · 文明秩序 · 脆弱精致</text>
          <text x="540" y="100" fill="#1d3557" font-size="11" text-anchor="middle">埃德加·林顿 (Edgar Linton)</text>
          <rect x="250" y="150" width="180" height="80" rx="8" fill="#8c2d19" />
          <text x="340" y="180" fill="#fff" font-weight="700" text-anchor="middle">凯瑟琳 (Catherine)</text>
          <text x="340" y="200" fill="#f0dcd8" font-size="11" text-anchor="middle">灵魂分裂在野性与文明之间</text>
          <line x1="140" y1="125" x2="270" y2="160" stroke="#8c2d19" stroke-width="2" />
          <line x1="540" y1="125" x2="410" y2="160" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("希斯克利夫", "捡回来的吉普赛孤儿", "遭受辛德雷虐待后出走发财归来，用残暴手段吞并两个家族产业，终在与凯瑟琳幽灵的相会中绝食自尽。"),
            ("凯瑟琳", "性格狂烈的高沼之女", "为了世俗地位选择嫁给优雅的埃德加，却在心底视希斯克利夫为自身灵魂的唯一骨血，精神撕裂难产而亡。"),
            ("小凯瑟琳与哈里顿", "第二代的新生代救赎", "通过识字与相爱化解了两代人的世仇，使荒芜的山庄重开春花。")
        ],
        "perception": "表面是一部跨越两代人的残酷家族复仇家史；深处展现了人类一种近乎神圣而恐怖的原初生命冲动。",
        "conflict": "原生态自然能量 vs 维多利亚文明阶级约束；毁灭性的绝对忠诚 vs 世俗虚荣的选择。",
        "turning_point": "凯瑟琳在厨房向女仆倾诉：‘嫁给希斯克利夫会降低我的身份’，门外的希斯克利夫只听到了半句便在雷雨之夜负气出走。",
        "symbols": [
            ("荒原石南与风暴：", "象征不可驯服的生命烈火，与画眉田庄精美的地毯与金丝鸟笼形成鲜明对照。"),
            ("窗外拍打的冰冷小手：", "鬼魂的敲窗，象征未被安葬的深情永恒徘徊在生死门槛之外。")
        ],
        "themes": "超越伦理与生死的精神互融；仇恨对复仇者自身的毁灭；第二代包容与和解的新生力量。",
        "socratic": "Q1：凯瑟琳如果当年选择嫁给一贫如洗的希斯克利夫，他们真的会幸福吗？\nQ2：希斯克利夫在复仇即将完全大获全胜时，为何突然放下了屠刀，任由自己衰竭而死？",
        "action": "文学地理感知：找一段描绘北方寒冬狂风呼啸的视频，感受自然恶劣气候如何塑造成书中人物坚硬野性的骨骼。"
    },

    "双城记": {
        "title_cn": "双城记", "title_en": "A Tale of Two Cities",
        "author_cn": "查尔斯·狄更斯", "author_en": "Charles Dickens",
        "sub_desc": "大革命风暴中的绝美复活挽歌 · 牺牲与博爱的至高丰碑",
        "hero_quote": "这是最好的时代，这是最坏的时代；这是光明的季节，这是黑暗的季节；这是希望之春，这是绝望之冬。",
        "year": "1859 年出版", "genre": "历史小说 / 人道主义杰作",
        "length": "约 22 万字", "age": "13+ 岁 / 青年与通识必读",
        "criteria": "历史暴力狂澜中个人自我牺牲的超越性",
        "warning": "不要偏颇地把作品当作反革命或颂扬贵族的保守宣教。狄更斯极其深刻地写出了贵族残暴压迫的因果必然性——正是圣安东尼区滴淌的红酒与被马车轧死的农家婴儿，酿成了断头台前德伐日太太无情的血腥复仇针织网。",
        "highlights": [
            "文学史上最经典的卷首名言与时代双城全景对照。",
            "悉尼·卡顿为了心中所爱之人的幸福，自愿替代死刑的终极牺牲。",
            "德伐日太太在编织毛线中记录贵族死亡名单的恐怖冷酷。"
        ],
        "context": "1789年法国大革命前夕至恐怖统治时期，伦敦的保守法治与巴黎的革命血潮形成剧烈对照。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="40" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="130" y="60" fill="#fff" font-weight="700" text-anchor="middle">伦敦 (London)</text>
          <text x="130" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">平和庇护所 · 法律秩序</text>
          <text x="130" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">马内特医生 / 露西</text>
          <rect x="460" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="550" y="60" fill="#fff" font-weight="700" text-anchor="middle">巴黎 (Paris)</text>
          <text x="550" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">大革命风暴 · 断头台血祭</text>
          <text x="550" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">德伐日夫妇 / 革命法庭</text>
          <rect x="250" y="140" width="180" height="90" rx="8" fill="#2a9d8f" />
          <text x="340" y="170" fill="#fff" font-weight="700" text-anchor="middle">悉尼·卡顿 (Sydney Carton)</text>
          <text x="340" y="190" fill="#e5e8eb" font-size="11" text-anchor="middle">颓废律师 · 代替达奈受死</text>
          <text x="340" y="210" fill="#e5e8eb" font-size="11" text-anchor="middle">‘我现在所做的，远比我做过的一切都要好’</text>
          <line x1="130" y1="115" x2="270" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="550" y1="115" x2="410" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("悉尼·卡顿", "才华横溢却自甘堕落的英国律师", "外表浪荡愤世嫉俗，内心怀抱最纯洁圣洁的牺牲之爱，走上断头台完成了灵魂的大复活。"),
            ("查尔斯·达奈", "背弃特权的法国流亡贵族", "厌恶家族残暴血腥统治自愿放弃封号，却因出身险遭革命法庭处死。"),
            ("德伐日太太", "残酷复仇的化身", "一家亲人全被厄弗里蒙地家族害死，仇恨让她在织针中冰冷注视每一个生命的消逝。")
        ],
        "perception": "表面是一部扣人心弦的历史劫难爱情传奇；深处写透了暴政如何催生暴民，以及唯有人道主义的自我牺牲才能阻断仇恨循环。",
        "conflict": "旧制度贵族的横征暴敛 vs 暴民政治的盲目嗜血；暴力的狂欢 vs 爱的献祭。",
        "turning_point": "卡顿利用长相酷似达奈的特征，调包潜入巴士底狱死牢，用氯仿麻醉达奈送其出城，自己安详登台受刑。",
        "symbols": [
            ("断头台‘小红帽姑娘’：", "机械化杀人的恐怖象征，旧暴政的恶种结出的嗜血恶果。"),
            ("编织针：", "平民妇女看似温和的日常手工，化作记录死刑黑名单的冷酷生死簿。")
        ],
        "themes": "仇恨无法战胜仇恨，唯有牺牲能带来真正复活；暴力的因果报应律；博爱对极权狂潮的超脱。",
        "socratic": "Q1：如果面对无休止的压迫，民众不用暴力革命，还有什么途径能够打碎吃人的特权锁链？\nQ2：卡顿一生碌碌无为，他最后的换头替死，究竟是对爱情的升华，还是对虚无人生的解脱？",
        "action": "历史辩析：回顾重大历史转折时刻，分析为什么一旦民众情绪被极端仇恨接管，最初追求正义的运动往往会滑向失控的疯狂。"
    },

    "艰难时世": {
        "title_cn": "艰难时世", "title_en": "Hard Times",
        "author_cn": "查尔斯·狄更斯", "author_en": "Charles Dickens",
        "sub_desc": "功利主义时代的犀利剖析 · 当事实与数字扼杀了童真与情感",
        "hero_quote": "先生，在这个世界上，我们需要的唯有‘事实’！除了事实，什么都不要播种，什么都不要培育！",
        "year": "1854 年出版", "genre": "工业社会讽刺小说 / 批判现实主义",
        "length": "约 18 万字", "age": "13+ 岁 / 青年与社会通识",
        "criteria": "极端功利主义教育对心灵的戕害机制",
        "warning": "切勿以为这部作品只是一部抨击黑烟滚滚煤烟城市的环保小说。狄更斯的核心利箭，正中西方现代文明的命门——<strong>把人当成冷冰冰的数据指标、用投入产出比衡量一切的功利主义哲学（Utilitarianism）</strong>。",
        "highlights": [
            "葛擂硬先生‘事实学校’扼杀孩子想象力的经典荒诞开场。",
            "焦煤镇（Coketown）如巨大黑蛇般盘踞的工业怪兽刻画。",
            "马戏团女孩西丝·朱佩用温情与常识守护心智人性的微光。"
        ],
        "context": "19世纪50年代英国工业革命鼎盛，功利主义与边沁功利哲学垄断教育与劳资关系，工人和儿童被降维为无名机械齿轮。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="200" height="90" rx="8" fill="#131619" />
          <text x="150" y="60" fill="#fff" font-weight="700" text-anchor="middle">焦煤镇 (Coketown)</text>
          <text x="150" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">黑烟巨蛇 · 资本家庞得贝</text>
          <text x="150" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">只认事实 · 人命如数字统计</text>
          <rect x="430" y="30" width="200" height="90" rx="8" fill="#2a9d8f" />
          <text x="530" y="60" fill="#fff" font-weight="700" text-anchor="middle">斯莱瑞马戏团 (Circus)</text>
          <text x="530" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">流浪艺人 · 欢笑与善意</text>
          <text x="530" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">西丝·朱佩 · 朴素人道常识</text>
          <line x1="250" y1="75" x2="430" y2="75" stroke="#8c2d19" stroke-width="2" stroke-dasharray="4,4" />
        </svg>""",
        "characters": [
            ("葛擂硬先生", "信奉事实的国会议员与父亲", "强行用数字教育子女，在女儿婚姻破裂、儿子成为银行小偷的残酷现实面前大彻大悟。"),
            ("路易莎", "被扼杀了情感感受力的女儿", "被迫嫁给比自己大三十岁的狂妄资本家庞得贝，终在精神虚脱中向父亲泣血控诉。"),
            ("黑面矿工布莱克浦", "坚忍纯良的底层劳工标本", "拒绝工会偏激罢工又拒绝向资本家告密，两头不讨好，在深井废坑中展现圣徒般的宽容。")
        ],
        "perception": "表面是一部维多利亚工业小镇家庭悲剧；深处批判了将人类情感、诗意与善意视作‘无用废料’的工具理性泛滥。",
        "conflict": "冷酷的数据理性 vs 温暖的人性同理心；无情的资本剥削 vs 工人基本的尊严诉求。",
        "turning_point": "路易莎在大雨之夜逃回娘家，倒在父亲脚下发出绝望控诉：‘你给了我一脑子的知识，却把我的心变成了一座死寂的荒原！’",
        "symbols": [
            ("永远不会散去的煤烟：", "象征盲目追求工业产值所付出的沉重环境与心理代价。"),
            ("马戏团的花马与杂耍：", "象征未经规训的快乐、想象力与人类纯洁天性。")
        ],
        "themes": "情感与想象力对人性的不可或缺；批判以唯KPI论摧残教育；人不是冷冰冰的生产力工具。",
        "socratic": "Q1：今天用分数、排名与KPI衡量一切的现代社会，与焦煤镇的‘事实学校’有本质区别吗？\nQ2：为什么完全依靠理性算计长大的儿子汤姆，最终会变成一个自私自利的罪犯？",
        "action": "教育反思：写下你受教育经历中最让你感到‘被当成数字或考试机器对待’的一个瞬间，反思它对你人格造成的微小折损。"
    },

    "复活": {
        "title_cn": "复活", "title_en": "Resurrection",
        "author_cn": "列夫·托尔斯泰", "author_en": "Leo Tolstoy",
        "sub_desc": "托翁晚年集大成之作 · 贵族灵魂的彻底忏悔与神圣新生",
        "hero_quote": "人就像河流，河水都是水，但有的地方狭窄，有的地方湍急，有的地方清澈，有的地方浑浊；每个人身上都包含着一切人性的胚胎。",
        "year": "1899 年出版", "genre": "全景现实主义长篇 / 精神自省史诗",
        "length": "约 45 万字", "age": "15+ 岁 / 青年与成人深读",
        "criteria": "社会阶级良知反省与个体道德完全复活",
        "warning": "切勿把《复活》误读为庸俗的‘少爷勾引女仆后良心发现的爱情补救’。聂赫留朵夫陪同喀秋莎流放西伯利亚，是一场全景式拆解沙俄法庭、监狱、官僚体制与教会伪善的<strong>深刻社会审判</strong>，是他对自己整个寄生阶级特权罪恶的彻底清算。",
        "highlights": [
            "法庭陪审席上四目相视的惊天心理电击。",
            "托尔斯泰对沙俄刑事司法制度与东正教虚伪仪式的冷峻剥茧。",
            "西伯利亚万里流放途中的人间地狱全景与底层革命党人交锋。"
        ],
        "context": "19世纪末沙皇专制与农奴制残余下的俄罗斯社会，托翁直面土地兼并、司法腐朽，将福音书精神化作批判社会的利刃。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">聂赫留朵夫公爵</text>
          <text x="340" y="68" fill="#cad5e2" font-size="11" text-anchor="middle">从荒淫贵族到真诚赎罪者</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">玛丝洛娃 (喀秋莎)</text>
          <text x="130" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">被诱奸沦为妓女 · 冤判流放</text>
          <text x="130" y="208" fill="#f0dcd8" font-size="11" text-anchor="middle">在苦难中拒绝施舍，重获自尊</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#242930" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">沙俄腐朽制度网</text>
          <text x="550" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">草菅人命的法官 · 贪婪典狱长</text>
          <text x="550" y="208" fill="#e5e8eb" font-size="11" text-anchor="middle">西伯利亚万里酷寒与苦役</text>
          <line x1="250" y1="70" x2="160" y2="140" stroke="#8c2d19" stroke-width="2" />
          <line x1="430" y1="70" x2="520" y2="140" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("聂赫留朵夫", "贵族精神复活的先行者", "散尽祖传土地分给农民，用一生的诚恳救赎年轻时的罪孽，完成了对自私肉体的超越。"),
            ("玛丝洛娃", "苦难深重的底层女性", "虽然饱受凌辱沉沦烟花，但骨子里傲骨未泯；为了不毁掉聂赫留朵夫的名誉，断然拒绝与他成婚，选择嫁给政治犯西蒙松。"),
            ("政治犯群像", "点亮西伯利亚的微光", "托翁以深切同情刻画了一批甘愿为了平民自由献身流放的先驱。")
        ],
        "perception": "表面是一个富贵公爵对被弃女子的漫长救赎；深处是俄罗斯知识分子直视社会巨大深渊后的精神革命。",
        "conflict": "安逸享有特权的阶级自私 vs 灵魂深处神圣道德的觉醒；官僚司法的冰冷形式 vs 底层鲜活生命的被碾压。",
        "turning_point": "法庭陪审席上的意外相遇：聂赫留朵夫一眼认出受审的毒杀嫌疑犯，正是十年前被自己抛弃的纯洁少女喀秋莎，灵魂在雷击中觉醒。",
        "symbols": [
            ("福音书：", "全书结尾聂赫留朵夫翻开圣经，标志着他在真理的指引下彻底开启全新的精神生命。"),
            ("沉重脚镣：", "流放者脚下清脆的金属撞击声，是对沙皇专制机器最刺耳的控诉。")
        ],
        "themes": "道德复活高于一切世俗地位；土地与劳动的神圣性；制度性罪恶面前个体的不可推卸之责。",
        "socratic": "Q1：玛丝洛娃最后为什么选择不和聂赫留朵夫结婚？这个决定为何标志着她真正的精神独立？\nQ2：托尔斯泰为什么坚决反对‘用暴力消灭暴政’，而坚持‘不以暴力抗恶’的心灵革命？",
        "action": "道德自省手札：回想一件你曾经因为年轻、虚荣或自私而伤害过某个人的往事，写下一封永不寄出的坦诚道歉信，感受自省带来的灵魂清洗。"
    },

    "安娜卡列妮娜": {
        "title_cn": "安娜·卡列尼娜", "title_en": "Anna Karenina",
        "author_cn": "列夫·托尔斯泰", "author_en": "Leo Tolstoy",
        "sub_desc": "世界长篇小说的最高峰 · 婚姻、激情、道德与文明焦虑的双线巨著",
        "hero_quote": "幸福的家庭都是相似的，不幸的家庭各有各的不幸。",
        "year": "1877 年出版", "genre": "全景现实主义长篇 / 心理长卷",
        "length": "约 80 万字", "age": "15+ 岁 / 终身必读文学经典",
        "criteria": "真挚激情与社会伪善礼法的尖锐冲突",
        "warning": "切勿把《安娜》降维成‘出轨贵妇被渣男抛弃卧轨自杀’的狗血八卦。安娜追求的是全心全意、绝不掺假的真实生命之爱，而彼得堡贵族社交界容忍暗中偷情却绝不容忍公开诚实。托翁借安娜与列文双线交织，宏观拷问了整个人类文明在现代化转型期的精神出路。",
        "highlights": [
            "经典双线交织结构：安娜与沃伦斯基的毁灭之火 vs 列文与吉娣的田园耕读新生之光。",
            "赛马场上沃伦斯基折断爱马脊梁的惊心动魄隐喻。",
            "火车站雨雪纷飞中的初遇与终局铁轨下的绝望一跃。"
        ],
        "context": "农奴制改革后的俄国社会，资本主义商品经济与西方思潮涌入，传统贵族家庭与道德伦理面临剧烈解体震荡。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="40" y="30" width="200" height="95" rx="8" fill="#8c2d19" />
          <text x="140" y="58" fill="#fff" font-weight="700" text-anchor="middle">安娜线：毁灭之火</text>
          <text x="140" y="78" fill="#f0dcd8" font-size="11" text-anchor="middle">安娜 · 沃伦斯基 · 卡列宁</text>
          <text x="140" y="98" fill="#f0dcd8" font-size="11" text-anchor="middle">激情 · 猜忌 · 社交圈逐斥 · 铁轨自绝</text>
          <rect x="440" y="30" width="200" height="95" rx="8" fill="#2a9d8f" />
          <text x="540" y="58" fill="#fff" font-weight="700" text-anchor="middle">列文线：新生之光</text>
          <text x="540" y="78" fill="#e5e8eb" font-size="11" text-anchor="middle">列文 · 吉娣 · 庄园农耕</text>
          <text x="540" y="98" fill="#e5e8eb" font-size="11" text-anchor="middle">劳作 · 割草顿悟 · 婚姻笃实 · 信仰回归</text>
          <line x1="240" y1="78" x2="440" y2="78" stroke="#1d3557" stroke-width="2" stroke-dasharray="4,4" />
          <text x="340" y="70" fill="#1d3557" font-size="11" font-weight="600" text-anchor="middle">对照互映</text>
        </svg>""",
        "characters": [
            ("安娜", "光彩照人的彼得堡贵妇", "拥有充沛的生命能量与对真实的执着，不愿在名存实亡的虚伪婚姻中苟活，终被排挤与猜忌逼上绝路。"),
            ("卡列宁", "位高权重的官僚机械", "冷漠刻板，视名声与体面甚于生命，用律法与教条折磨安娜，剥夺其探视亲生儿子的权利。"),
            ("列文", "托尔斯泰的自画像化身", "笨拙纯朴的地主知识分子，在草地上与农民共同挥汗挥镰割草，最终领悟生活的真谛在于为善和利他。")
        ],
        "perception": "表面是一部贵族家庭婚姻纠纷长卷；深处展现了人类在追求绝对真实激情的过程中，如何被社会的虚伪与人性深处的自私无情碾碎。",
        "conflict": "绝对诚实的爱欲本能 vs 虚伪社交秩序的残酷孤立；理性的哲学思辨 vs 大地劳作的朴素顿悟。",
        "turning_point": "赛马场事故：沃伦斯基骑马摔断马脊，看台上的安娜在众目睽睽下失控尖叫失态，向丈夫卡列宁彻底招认私情。",
        "symbols": [
            ("呼啸的火车：", "近代工业文明的钢铁怪兽，既是带来私情的相遇温床，也是碾碎肉身与激情的冰冷工具。"),
            ("割草场景：", "列文与农夫在烈日下节奏一致的劳作，象征回归大地自然对虚无心智的至高治愈。")
        ],
        "themes": "道德审判的归属（‘伸冤在我，我必报应’）；婚姻制度的本质反思；在现代虚妄中追寻朴素的生命意义。",
        "socratic": "Q1：如果卡列宁当年同意平稳离婚，安娜和沃伦斯基真的能长相厮守、白头偕老吗？\nQ2：列文在乡野大地中找到的信仰，为什么能够救赎他摆脱现代知识分子的自杀焦虑？",
        "action": "关系体检：审视身边的一段亲密关系，问自己：在这段关系中，你们彼此展示的是精心装扮的‘人设体面’，还是完全不设防的‘真实自我’？"
    },

    "傲慢与偏见": {
        "title_cn": "傲慢与偏见", "title_en": "Pride and Prejudice",
        "author_cn": "简·奥斯汀", "author_en": "Jane Austen",
        "sub_desc": "英国世态小说的绝美明珠 · 误解消除与成熟心智的胜利",
        "hero_quote": "凡是有钱的单身汉，总想娶位太太，这已经成了一条举世公认的真理。",
        "year": "1813 年出版", "genre": "世态世情讽刺小说 / 经典罗曼史",
        "length": "约 20 万字", "age": "12+ 岁 / 青年与成人必读",
        "criteria": "偏见对心智的遮蔽与通过理性反省实现的自我成长",
        "warning": "切勿以为这只是一部‘贫家女钓金龟婿’的言情爽文。奥斯汀以‘两寸象牙上的精细雕刻’，极度严肃地探讨了<strong>在没有继承权的严苛法律下，女性如何既不向金钱妥协，又不在贫困中沉沦</strong>的生存智慧与独立尊严。",
        "highlights": [
            "伊丽莎白在彭伯利庄园目睹达西真实品格的心理反转。",
            "达西先生第一次高傲求婚遭拒的电光石火经典对决。",
            "柯林斯牧师与班内特太太的世俗小市民精明讽刺画卷。"
        ],
        "context": "18世纪末英国摄政时期，限嗣继承制导致没有儿子的乡绅家庭女儿面临被驱逐流落街头的生存危机。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="40" y="30" width="200" height="90" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">达西先生 (Mr. Darcy)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">阶级傲慢 · 深沉寡言 · 真正高尚</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">放下门第偏执，学会尊重</text>
          <rect x="440" y="30" width="200" height="90" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">伊丽莎白 (Elizabeth)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">聪慧机敏 · 敏锐自尊 · 先入为主</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">破除偏见盲目，正视真实</text>
          <line x1="240" y1="75" x2="440" y2="75" stroke="#2a9d8f" stroke-width="2.5" />
          <text x="340" y="65" fill="#2a9d8f" font-size="11" font-weight="600" text-anchor="middle">从对立到双向成长</text>
        </svg>""",
        "characters": [
            ("伊丽莎白", "富有见识与反思力的二女儿", "机智幽默，勇于拒绝豪门求婚，在读懂达西的辩解信后敢于承认自己的盲目与过失。"),
            ("达西先生", "家产万贯的彭伯利领主", "起初被阶级优越感遮蔽，被伊丽莎白当头棒喝后深刻反省，暗中出资拯救班内特家族名誉。"),
            ("韦翰", "伪善逢迎的军官混混", "用花言巧语编造谎言欺骗小镇，暴露了‘迷人外表’对世俗判断的天然诱导。")
        ],
        "perception": "表面是一出充满诙谐笑料的乡绅婚姻择偶剧；深处展示了两个同样聪明骄傲的人，如何经历痛苦的反省，学会穿透第一印象的虚妄。",
        "conflict": "阶级优越感带来的傲慢冷漠 vs 受到伤害的自尊心结下的顽固偏见。",
        "turning_point": "达西先生的长信：达西在求婚被拒后没有报复，而是平静而克制地澄清了韦翰的恶行，使伊丽莎白第一次直面自己的浅薄盲目。",
        "symbols": [
            ("彭伯利庄园 (Pemberley)：", "自然风景与人工修剪的完美调和，象征达西高尚、开明、未经矫饰的内在精神风貌。")
        ],
        "themes": "成熟心智必须经历自省与破除偏见的痛苦；婚姻中物质基础与精神独立的平衡艺术。",
        "socratic": "Q1：如果达西没有那一万英镑年金和彭伯利庄园，伊丽莎白还会对他产生敬佩与倾慕吗？\nQ2：我们在日常生活中对某个人的‘第一印象’，有多少成分是在投射自己内心的自卑或偏见？",
        "action": "反思练习：列出一位你目前‘非常讨厌或看不惯’的人，尝试找出一件能够反驳你对他的刻板标签的真实事实。"
    },

    "理智与情感": {
        "title_cn": "理智与情感", "title_en": "Sense and Sensibility",
        "author_cn": "简·奥斯汀", "author_en": "Jane Austen",
        "sub_desc": "奥斯汀成名奠基之作 · 两种女性性格与处世哲学的精微交响",
        "hero_quote": "理智与情感并非死敌，失去情感的生活是荒凉的，而失去理智的激情则是毁灭性的狂暴。",
        "year": "1811 年出版", "genre": "世情小说 / 道德伦理小说",
        "length": "约 18 万字", "age": "12+ 岁 / 青年必读经典",
        "criteria": "自我节制克己与激情宣泄的黄金分割点",
        "warning": "不要把埃莉诺简单等同于‘冷酷教条’，也不要把玛丽安当作‘活泼率真’。奥斯汀极其犀利地指出：玛丽安肆无忌惮地沉溺于悲伤，是对身边亲人感受的自私忽视；而埃莉诺强忍心碎替妹妹操持家务，才是最高贵的深情。",
        "highlights": [
            "达什伍德姐妹面对失恋与变故的完全不同心理应对模式。",
            "花花公子威洛比在大雨中现身坦白苦衷的经典忏悔戏。",
            "布兰登上校隐忍克制、如磐石般深沉的成年人守护之爱。"
        ],
        "context": "18世纪末英国乡村社会，浪漫主义狂潮鼓励青年放飞情感，奥斯汀以古典理智主义审视狂热带来的生活破裂。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="200" height="85" rx="8" fill="#1d3557" />
          <text x="150" y="60" fill="#fff" font-weight="700" text-anchor="middle">埃莉诺 (Elinor · 理智)</text>
          <text x="150" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">自我克制 · 关照他人 · 忍耐痛苦</text>
          <text x="150" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">爱德华的信义守诺</text>
          <rect x="430" y="30" width="200" height="85" rx="8" fill="#8c2d19" />
          <text x="530" y="60" fill="#fff" font-weight="700" text-anchor="middle">玛丽安 (Marianne · 情感)</text>
          <text x="530" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">狂热率真 · 忽视社交 · 沉溺痛苦</text>
          <text x="530" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">遭威洛比抛弃重病醒悟</text>
          <line x1="250" y1="72" x2="430" y2="72" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("埃莉诺", "达什伍德家长女", "为了不让母亲与妹妹担忧，深锁内心的悲伤，用理智维护家庭的尊严与体面。"),
            ("玛丽安", "次女，浪漫主义拥趸", "将一切理智节制定性为虚伪，在遭遇情变后几乎送命，最终在姐姐的爱中学会成熟与自律。"),
            ("布兰登上校", "历经风霜的中年退伍军官", "默默承担一切琐事，不求回报地守护玛丽安，代表成熟稳重的深邃担当。")
        ],
        "perception": "表面是两姐妹寻找归宿的婚恋故事；深处探讨了‘人如何平衡内心汹涌的本能情绪与维系文明运转的社会责任’。",
        "conflict": "毫无节制的情感宣泄 vs 恪守自尊克制的社会责任。",
        "turning_point": "玛丽安在风雨中狂奔受凉身染重病命悬一线：肉体的濒死体验彻底惊醒了她的任性，教会了她对生命的敬畏。",
        "symbols": [
            ("钢琴与乐谱：", "既是青年人表达才情与激情的信物，也是过度脱离现实生活的浪漫温室载体。")
        ],
        "themes": "情感必须受到理智的驯化才能持久；成熟是学会为了爱你的人克制不负责任的放纵。",
        "socratic": "Q1：埃莉诺把悲伤藏在心底，这种自控是健康的忍耐，还是一种对自我感受的压抑损害？\nQ2：现代网络文化鼓励‘随性而行做自己’，与玛丽安当年的任性冲动有何异同？",
        "action": "情绪自律演练：在经历一次情绪爆发冲动时，尝试静默等待五分钟，把控诉的本能转化为建设性的解决方案。"
    },

    "德伯家的苔丝": {
        "title_cn": "德伯家的苔丝", "title_en": "Tess of the d'Urbervilles",
        "author_cn": "托马斯·哈代", "author_en": "Thomas Hardy",
        "sub_desc": "英国自然主义悲剧之巅 · 纯洁女性在虚伪双重道德下的绝命长歌",
        "hero_quote": "一个纯洁的女人，严正地呈现于世人面前。",
        "year": "1891 年出版", "genre": "自然主义小说 / 维多利亚伦理批判",
        "length": "约 35 万字", "age": "15+ 岁 / 青年与成人深读",
        "criteria": "维多利亚男女双重性道德对无辜女性的绞杀",
        "warning": "哈代在扉页题写‘一个纯洁的女人’，激怒了当时全英的卫道士。切勿以世俗偏见谴责苔丝的失贞与谋杀。苔丝是一个在肉体上遭遇强暴掠夺、在灵魂上却至纯至善的乡村圣洁造物，逼死她的是整个社会的道德伪善。",
        "highlights": [
            "新婚之夜安吉尔·克莱尔自述放荡被宽恕，却在听闻苔丝悲惨遭遇后冷酷遗弃的双重道德暴击。",
            "巨石阵（Stonehenge）祭坛上黎明破晓时的静穆被捕绝唱。",
            "牛奶场青翠田园中生命力的勃发与荒寒燧石农场劳役的鲜明对照。"
        ],
        "context": "19世纪末工业机器与现代农场碾碎了古老的英国农业田园，基督教严苛的性禁忌将一切受害女性判定为堕落荡妇。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">苔丝 (Tess)</text>
          <text x="340" y="68" fill="#f0dcd8" font-size="11" text-anchor="middle">纯洁圣女 · 命运玩物 · 悲剧献祭</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#131619" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">亚雷 (Alec)</text>
          <text x="130" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">肉体掠夺者 · 伪装善人</text>
          <text x="130" y="208" fill="#e5e8eb" font-size="11" text-anchor="middle">金钱缠绞逼迫</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">安吉尔 (Angel)</text>
          <text x="550" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">唯美知识分子 · 道德教条囚徒</text>
          <text x="550" y="208" fill="#cad5e2" font-size="11" text-anchor="middle">新婚夜遗弃，终悟时已晚</text>
          <line x1="250" y1="70" x2="160" y2="140" stroke="#8c2d19" stroke-width="2" />
          <line x1="430" y1="70" x2="520" y2="140" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("苔丝", "纯朴高贵的高贵弃儿后裔", "集自然生命的美好于一身，饱受贫穷、强暴与背叛撕扯，为了拯救家庭终将利刃刺向折磨者。"),
            ("安吉尔·克莱尔", "自诩摆脱传统的牧师之子", "嘴上高谈阔论精神解放，骨子里依然是狭隘性道德的教条产物，犯下不可原谅的遗弃罪。"),
            ("亚雷·德伯", "买来贵族头衔的新贵浪子", "利用苔丝家庭的破产饥谨，持续追逐纠缠，最终在血色床榻上迎来了苔丝的绝地复仇。")
        ],
        "perception": "表面是一个贫穷村姑的失贞被弃悲剧；深处控诉了父权社会、虚伪宗教与阶级不公三合一绞肉机对弱势者的无情屠杀。",
        "conflict": "大自然赋予的纯洁生命本色 vs 维多利亚社会制定的虚伪人造道德标准。",
        "turning_point": "新婚夜的坦白：苔丝在完全坦白过去后，安吉尔冰冷宣布：‘你不是我所爱的那个人，你只是披着她外表的另一个人！’",
        "symbols": [
            ("巨石阵 (Stonehenge)：", "古代异教的祭祀祭坛。苔丝最后安详躺在其上被捕，象征她作为人类原初纯洁牺牲品的悲剧神圣性。"),
            ("滴血的天花板：", "亚雷旅店客房天花板上渗下的鲜血，宣告了长期沉默者最惊世骇俗的反抗。")
        ],
        "themes": "道德纯洁的本质不在于肉体是否受辱，而在于灵魂的良善；自然法则与人造教条的永恒冲突；悲剧命运的不可逆性。",
        "socratic": "Q1：安吉尔在坦白自己私生活不检点时得到了苔丝的宽恕，为什么他却无法给苔丝同样的宽恕？\nQ2：哈代为何认为工业时代的技术理性加剧了乡村田园人性的毁灭？",
        "action": "道德双标检视：思考在当今网络热点中，是否存在对男性与女性在同等道德失误上极其不公的双重严苛审判？"
    },

    "茶花女": {
        "title_cn": "茶花女", "title_en": "La Dame aux Camélias",
        "author_cn": "小仲马", "author_en": "Alexandre Dumas fils",
        "sub_desc": "世界凄艳爱情的传世挽歌 · 泥沼中开出的圣洁爱情之花",
        "hero_quote": "唯有真正爱过并痛苦过的人，才懂得宽恕的可贵。",
        "year": "1848 年出版", "genre": "浪漫哀婉悲剧 / 世态言情小说",
        "length": "约 15 万字", "age": "13+ 岁 / 青年必读经典",
        "criteria": "社会偏见壁垒与真挚牺牲之爱的冲突",
        "warning": "不要把玛格丽特当作普通的巴黎交际花。在纸醉金迷、买卖肉体的巴黎上流社会，只有她保留了对纯粹精神之爱的向往，并为了爱人的前途和家族体面，自愿承受全世界的唾骂与误解，默默咳血而死。",
        "highlights": [
            "白茶花与红茶花的经典月度暗号。",
            "阿芒之父阿芒先生登门请求玛格丽特断绝关系的心碎交锋。",
            "玛格丽特绝笔日记中记录阿芒用钞票扔在自己脸上时的彻骨绝望。"
        ],
        "context": "19世纪七月王朝时期的巴黎，资产阶级狂热追求财富与交际虚荣，高级名妓成为贵族富豪挥霍与炫耀的玩物。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">玛格丽特 (茶花女)</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">绝色名妓 · 肺病残躯</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">为爱人家庭主动牺牲自我</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">阿芒·杜瓦尔 (Armand)</text>
          <text x="540" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">年轻税务官之子 · 狂热痴爱</text>
          <text x="540" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">误信背叛，以金钱羞辱挚爱</text>
          <line x1="230" y1="72" x2="450" y2="72" stroke="#2a9d8f" stroke-width="2" />
          <text x="340" y="62" fill="#2a9d8f" font-size="11" font-weight="600" text-anchor="middle">牺牲与误解的悲歌</text>
        </svg>""",
        "characters": [
            ("玛格丽特", "饱受肺结核摧残的交际花", "在世俗污泥中渴望真情，为了阿芒妹妹的婚事毅然忍痛佯装重归旧欢，独自在债务与病榻中孤独咽气。"),
            ("阿芒", "冲动狂热的青年男子", "深爱玛格丽特却无法理解她的苦心，因嫉妒与误会多次公开羞辱她，终身陷于终生的悔恨之中。"),
            ("杜瓦尔先生", "老成持重的资产阶级父亲", "代表家庭体制与社会体面，虽然同情玛格丽特的高尚，但依然残忍地要求她退出。")
        ],
        "perception": "表面是一个风尘女子的凄美爱情悲剧；深处揭露了金钱至上的资产阶级社会对真挚人性的无情绞杀。",
        "conflict": "纯洁忠贞的灵魂相托 vs 世俗社会对出身身份的不可跨越偏见。",
        "turning_point": "杜瓦尔老先生暗访乡间小屋：他以‘一个清白家庭的荣誉和女儿的未来’为重托，迫使玛格丽特立下永不复合的重誓。",
        "symbols": [
            ("白茶花：", "清冷、无香却高贵脱俗，象征玛格丽特深处未被金钱污染的纯洁灵魂。"),
            ("拍卖行的遗物拍卖清单：", "全书开篇对遗物的公开叫卖，象征资本社会把一个人一生的深情与眼泪全部兑现为铜臭的冷漠。")
        ],
        "themes": "爱能净化一切苦难与偏见；自我牺牲的至高神圣性；社会名誉与个人幸福的残酷对立。",
        "socratic": "Q1：玛格丽特答应老杜瓦尔离开阿芒，这种牺牲究竟是一种高贵，还是向世俗偏见的一种软弱妥协？\nQ2：为什么人类文学史上‘风尘女子的真情’总能激起最深沉的悲悯与眼泪？",
        "action": "情感自省：思考在人际交往中，你是否曾因为对方的‘某种过去经历或标签’，而轻率地否定了他此刻付出的全部真诚？"
    },

    "红字": {
        "title_cn": "红字", "title_en": "The Scarlet Letter",
        "author_cn": "纳撒尼尔·霍桑", "author_en": "Nathaniel Hawthorne",
        "sub_desc": "美国文学奠基之作 · 清教主义严酷铁律下的罪与罚",
        "hero_quote": "胸前红字的烙印可以洗刷，但灵魂深处的自欺却会将生命化为灰烬。",
        "year": "1850 年出版", "genre": "心理浪漫小说 / 象征主义杰作",
        "length": "约 16 万字", "age": "14+ 岁 / 青年必读经典",
        "criteria": "公开认罪与隐秘负罪的心理对比机制",
        "warning": "不要把故事仅仅看作惩罚通奸的宗教戒律。霍桑最震撼人心的构思，是展示了<strong>公开佩戴耻辱红字的白兰，在苦难中反而赢得了灵魂的独立与坚毅；而道貌岸然、隐瞒私情的年轻牧师狄梅斯代尔，却在万民膜拜中被内心的罪恶感活活折磨成行尸走肉</strong>。",
        "highlights": [
            "波士顿集市断头台开场的全城审判与胸前刺绣的红字‘A’。",
            "狄梅斯代尔牧师夜半私自登上绞刑台的自我鞭笞绝望。",
            "森林中白兰解开发辫与牧师重温自由激情的动人瞬间。"
        ],
        "context": "17世纪中叶北美新英格兰清教殖民地，严苛的加尔文主义将任何越轨行为视为魔鬼附体，社会毫无私人隐私空间。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">海丝特·白兰 (Hester)</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">胸佩红字 A · 公开受辱</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">以刺绣济贫，化耻辱为高贵</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">狄梅斯代尔牧师</text>
          <text x="540" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">暗中通奸者 · 万人敬仰</text>
          <text x="540" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">内疚如烙铁焚烧五脏六腑</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#131619" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">齐灵窝斯 (原配丈夫)</text>
          <text x="340" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">化身私人医生 · 灵魂复仇吸血魔</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#8c2d19" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("海丝特·白兰", "坚忍博爱的女性先驱", "拒不供认情人姓名，用双手的劳作救济病弱，胸前的‘通奸（Adultery）’红字最终被民众尊称为‘能干（Able）’与‘天使（Angel）’。"),
            ("狄梅斯代尔", "备受煎熬的才华圣徒", "缺乏直面羞辱的勇气，终在布道会高潮时走上绞刑台撕开胸膛承认罪恶，死在白兰怀中完成救赎。"),
            ("齐灵窝斯", "被复仇异化的老学者", "以医者身份潜入牧师身旁暗中施加精神凌迟，最终随着复仇对象的死亡而彻底枯竭。")
        ],
        "perception": "表面是一桩清教社会的通奸道德审判案；深处探讨了‘罪与罚’如何塑造人类的心灵结构。",
        "conflict": "清教律法的冷酷教条 vs 人类本能情感的不可遏制；公开承担的坦荡 vs 隐秘伪善的精神地狱。",
        "turning_point": "最后就职大典后的露天认罪：狄梅斯代尔在全体教民面前登上绞刑台，公开揭示自己与白兰的私情并坦陈红字印记，粉碎了齐灵窝斯的终生暗中折磨。",
        "symbols": [
            ("红字‘A’ (The Scarlet Letter)：", "从最初象征耻辱与罪愆的记号，演变为博爱、坚韧与神圣受难的勋章。"),
            ("森林与集市：", "集市代表清教律法严酷监视的冷酷空间，森林代表卸下社会伪装、自然律动复活的自由母体。"),
            ("私生女珠儿 (Pearl)：", "野生野长、未受教条驯化的精灵，是破坏旧律法、象征大自然生命力的活生生红字化身。")
        ],
        "themes": "面对过错的诚实坦荡是治愈灵魂的唯一解药；宗教教条与人道同理心的根本对立；复仇对施暴者灵魂的反噬。",
        "socratic": "Q1：如果狄梅斯代尔一直隐瞒到底并在崇敬中安然离世，他的人生算成功还是彻底的失败？\nQ2：清教徒社会为何对别人的道德过错表现出如此狂热的公开审判欲？这暴露了群体怎样的心理阴暗面？",
        "action": "道德自省测试：“红字日记”——写下一件你曾经极力在他人面前隐瞒掩盖的失误，分析隐瞒它给你带来的心理能耗，感受坦诚面对可能获得的释怀。"
    },

    "The Good Earth 大地": {
        "title_cn": "大地", "title_en": "The Good Earth",
        "author_cn": "赛珍珠", "author_en": "Pearl S. Buck",
        "sub_desc": "诺贝尔文学奖传世巨作 · 华夏农耕文明与土地之魂的雄浑史诗",
        "hero_quote": "只要我们还守着土地，我们就永远不会灭亡；如果失去土地，一切繁华都不过是过眼云烟。",
        "year": "1931 年出版", "genre": "史诗巨著 / 乡土史诗 / 跨文化经典",
        "length": "约 26 万字", "age": "12+ 岁 / 全年龄必读经典",
        "criteria": "人与土地农耕伦理的共生与背离命运",
        "warning": "不要带着‘西方人猎奇中国’的刻板眼光阅读。赛珍珠在中国江南大地上生活了数十年，她以极其深沉的敬畏与同情，写透了中国传统农民面对天灾饥荒时像野草般的坚韧生命力，以及富贵之后脱离土地必然走向败亡的家族历史周期律。",
        "highlights": [
            "王龙与阿兰在春风中并肩躬耕泥土的质朴圣洁图景。",
            "大旱之年全家吞咽观音土、绝不卖地的惊心动魄坚守。",
            "全书结尾王龙抚摸泥土，而儿子们却在暗中筹划变卖田产的时代宿命回响。"
        ],
        "context": "清末民初中国华北与江南乡土社会，古老的宗族血缘与农耕文明在饥荒、战乱与现代商业洪流下的剧烈转型。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">王龙 (Wang Lung)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">勤劳坚韧农民 · 土地崇拜者</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">从一文不名到地主大户</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">阿兰 (O-lan)</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">沉默如大地的黄脸结发妻子</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">吃苦耐劳 · 家族基业真正奠基人</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">泥土与大地 (The Earth)</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">财富与生存的唯一神圣源头</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("王龙", "中国农民的史诗化身", "敬畏土地与祖先，凭一把锄头硬生生在饥馑中积攒出豪门家业，晚年面对骄奢儿孙满怀宿命焦虑。"),
            ("阿兰", "黄土地上最伟大的母亲形象", "曾为黄府丫鬟，嫁给王龙后默默承担全部最沉重的劳作，甚至在战乱废墟中抢回宝石奠定家业，临终前赢得全家无上敬畏。"),
            ("黄家豪门与王龙儿孙", "脱离土地必然腐化的宿命标本", "昔日黄家因吸鸦片挥霍败落，王龙的儿孙们读书当官做生意后，同样看不起泥土，谋划卖田离乡。")
        ],
        "perception": "表面是一部中国北方农民家庭三代人的发家荣辱史；深处谱写了人类生命与孕育一切的泥土之间不可分割的血脉共生诗篇。",
        "conflict": "坚守泥土的勤劳克俭 vs 财富积累后滋生的享乐腐化；父辈的农耕传统信仰 vs 子辈脱离土地的现代诱惑。",
        "turning_point": "南方战乱中抢夺富豪藏宝：阿兰敏锐地在暗墙中摸出一把珠宝，王龙用这笔横财在荒年中买下了黄府全部良田，完成了阶层跃迁。",
        "symbols": [
            ("黄土地：", "不仅是生产粮食的生产资料，更是安身立命、灵魂归宿的无上母亲神性象征。"),
            ("两颗珍珠：", "阿兰从珠宝中唯一留下的私藏，后被王龙夺走送给新妾梨花，成为传统女性最深沉无言的心碎隐痛。")
        ],
        "themes": "土地是人类一切繁荣与尊严的根基；勤俭治家与奢侈败亡的永恒历史周期律；传统劳动女性的崇高牺牲美。",
        "socratic": "Q1：王龙在发财后纳妾并冷落阿兰，这反映了人性在摆脱匮乏后怎样的贪婪与健忘？\nQ2：今天的人们生活在钢筋水泥高楼中，彻底脱离了土地，我们失去了哪种最底层的心理安全感？",
        "action": "自然连接：在阳台或花盆中亲手播种一株绿植，每天观察泥土干湿与萌芽生长，感受大地母亲赋予生命的最初节奏。"
    }
}

def main():
    print("=== 开始批量构建【批次 B：欧洲现实主义长篇巨著】 ===")
    success = 0
    total = len(BOOKS_B)

    for book_name, info in BOOKS_B.items():
        target_dir = os.path.join(BASE_DIR, book_name)
        if not os.path.exists(target_dir):
            print(f"[WARN] 目录不存在: {target_dir}")
            continue

        html = render_book_guide(info)

        # 结构检验
        soup = BeautifulSoup(html, "html.parser")
        assert len(soup.find_all("details", class_="guide-section")) == 13, f"{book_name} 栏目数不为 13"
        assert len(soup.find_all("svg")) >= 1, f"{book_name} 缺少 SVG"

        with open(os.path.join(target_dir, "guide.html"), "w", encoding="utf-8") as f:
            f.write(html)
        with open(os.path.join(target_dir, "guide.index"), "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[OK] {book_name} -> guide.html & guide.index 写入完成 ({len(html)} 字节)")
        success += 1

    print(f"=== 批次 B 顺利完工: {success}/{total} 部作品通过校验并落盘 ===")

if __name__ == "__main__":
    main()
