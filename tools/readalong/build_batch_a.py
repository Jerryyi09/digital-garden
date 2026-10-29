#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch A: Shakespeare & Drama series (10 books)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

BOOKS_A = {
    "莎士比亚-麦克白": {
        "title_cn": "麦克白", "title_en": "Macbeth",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "四大悲剧中最具爆发力之作 · 欲望深渊与心理惊悚典范",
        "hero_quote": "人生不过是一个行走的影子，一个在舞台上指手画脚的拙劣伶人，登场片刻，便在无声无息中悄然退下。",
        "year": "约 1606 年", "genre": "心理悲剧 / 命运预言 / 欲望反思",
        "length": "约 1.8 万词（紧凑凌厉）", "age": "14+ 岁 / 青年与思辨读者",
        "criteria": "野心与罪恶感心理演进机制",
        "warning": "切勿把麦克白当成天生嗜血的坏人。莎士比亚最惊人的笔触，是写出了一个本性高尚、战功赫赫的英雄，如何在‘被预言唤醒的野心’与‘无休止的恐惧’中，一步步将自己推进嗜血的绝境。",
        "highlights": [
            "欲望如何将想象力转化为酷刑：麦克白在弑君之前就经历了心理上的千刀万剐。",
            "麦克白夫人的心理倒错：从起初的冷酷决绝，到终局梦游洗不掉手中血迹的自毁。",
            "荒诞的女巫双重预言机制：字面上的免死承诺，实则是命运最大的嘲讽。"
        ],
        "context": "詹姆士一世登基伊始，弑君阴谋（火药阴谋）阴云密布。莎翁以苏格兰历史为画布，深度剖析僭越天命的灾难性后果。",
        "svg": """<svg viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">麦克白 (Macbeth)</text>
          <text x="340" y="68" fill="#f0dcd8" font-size="11" text-anchor="middle">赫赫战功 · 野心与恐惧的囚徒</text>
          <rect x="30" y="140" width="160" height="75" rx="8" fill="#1d3557" />
          <text x="110" y="168" fill="#fff" font-weight="700" text-anchor="middle">三女巫 (Witches)</text>
          <text x="110" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">命运预言 · 恶念催化剂</text>
          <rect x="490" y="140" width="160" height="75" rx="8" fill="#242930" />
          <text x="570" y="168" fill="#fff" font-weight="700" text-anchor="middle">麦克白夫人</text>
          <text x="570" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">野心撺掇 · 梦游洗手癫狂</text>
          <line x1="190" y1="160" x2="250" y2="70" stroke="#8c2d19" stroke-width="2" />
          <line x1="490" y1="160" x2="430" y2="70" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("麦克白", "苏格兰骁勇大将", "从受人爱戴的英雄蜕化为残暴多疑的孤家寡人，终被麦克德夫斩杀。"),
            ("麦克白夫人", "钢铁意志背后的脆弱心智", "起初讥讽丈夫手软，弑君后被血腥梦魇逼入绝境，夜半洗手成为文学永恒经典。"),
            ("班柯", "良知未泯的对照镜像", "同样听到预言却拒绝作恶，死后亡灵出现在王室盛宴上粉碎麦克白的心智防线。")
        ],
        "perception": "表面是一个野心家弑君篡位最终覆灭的故事；深处触碰了人类如何被内心的贪念所奴役。恶念一旦被打开，人就必须用更大的恶去掩盖先前的罪，直到万劫不复。",
        "conflict": "内心良知的严厉谴责 vs 不可遏制的权力狂欲；命运预言的诱惑 vs 自主意志的选择。",
        "turning_point": "暗杀邓肯国王的那个风雨之夜：当匕首刺入慈祥老国王胸膛，麦克白听到了虚空中的审判之声——‘麦克白杀害了睡眠！’",
        "symbols": [
            ("洗不掉的血迹：", "象征无法被遗忘、无法被宽恕的原罪内疚。"),
            ("移动的勃南树林：", "命运看似荒谬的安全预言，实则暗藏物理世界的无情惩戒。"),
            ("暗夜里的飞刀：", "神经衰弱与罪恶幻想凝聚而成的幻觉武器。")
        ],
        "themes": "权力异化人性的过程；知罪却不得不继续作恶的心理地狱；生命虚无感的悲剧觉醒。",
        "socratic": "Q1：如果女巫从未出现，麦克白心中的弑君野心还会破土发芽吗？\nQ2：麦克白在最后一战前已深知预言破灭，为何还要拔剑战死到最后一刻？",
        "action": "思维工具：‘滑坡心理检查表’——在做出第一个微小违背原则的妥协时，推演这一妥协三年后可能滚成的雪崩。"
    },

    "莎士比亚-威尼斯商人": {
        "title_cn": "威尼斯商人", "title_en": "The Merchant of Venice",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "法理与仁慈的惊世辩论 · 契约社会与异族偏见的复杂交响",
        "hero_quote": "慈悲不是出于勉强，它像甘霖从天上降下，双重赐福于给予者和接受者。",
        "year": "约 1596–1598 年", "genre": "浪漫喜剧 / 法律道德辩论剧",
        "length": "全五幕", "age": "12+ 岁 / 青年与通识读者",
        "criteria": "法律条文正义与实质人道关怀的张力",
        "warning": "切勿将夏洛克扁平化为‘天生恶毒的守财奴’。莎翁借夏洛克之口发出了著名的灵魂质问：‘犹太人难道没有眼睛、手脚和五官吗？你们要是扎我们，我们难道不出血吗？’这是一部充满社会排斥与法律复杂性的灰色杰作。",
        "highlights": [
            "一磅肉契约背后的种族压迫与仇恨循环。",
            "鲍西娅法庭女扮男装的绝对法律智慧反转。",
            "金、银、铅三匣选婿的价值隐喻。"
        ],
        "context": "16世纪威尼斯商业文明崛起，契约与借贷成为现代商业基石，犹太人在基督教主流社会中承受着深重的偏见与合法放贷的道德撕裂。",
        "svg": """<svg viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">法庭辩论 (Court)</text>
          <text x="340" y="68" fill="#cad5e2" font-size="11" text-anchor="middle">鲍西娅：法理智慧与慈悲</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">夏洛克 (Shylock)</text>
          <text x="130" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">一磅肉契约 · 异族屈辱复仇</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">安东尼奥 / 巴萨尼奥</text>
          <text x="550" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">挚友信义 · 威尼斯商业阶层</text>
          <line x1="220" y1="160" x2="270" y2="95" stroke="#8c2d19" stroke-width="2" />
          <line x1="460" y1="160" x2="410" y2="95" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("夏洛克", "威尼斯犹太放贷者", "遭受歧视侮辱，试图通过威尼斯严谨的法律条文索取安东尼奥胸口一磅肉完成尊严报复。"),
            ("鲍西娅", "贝尔蒙特智慧女继承人", "化身青年法官，以严丝合缝的法条反制夏洛克（割肉不得流一滴血），展现卓越智慧。"),
            ("安东尼奥", "威尼斯富商", "为成全朋友巴萨尼奥求婚不惜以自身血肉作抵押，体现了文艺复兴对崇高友谊的推崇。")
        ],
        "perception": "表面是一场惊险的借贷纠纷与法庭辩论；深处探讨了‘法律的形式正义是否等同于实质道德正义’。当法律被用来执行毫无仁慈的报复，文明将如何解构？",
        "conflict": "严苛契约文字 vs 宽厚慈悲精神；异族边缘人积怨 vs 主流社会的冷漠排斥。",
        "turning_point": "鲍西娅当庭裁决：‘你可以割下一磅肉，但契约中未写一滴血。若流了一滴基督徒的血，你的一切财产将被抄没！’瞬间逆转死局。",
        "symbols": [
            ("一磅肉：", "象征将人身贬低为商品筹码的冷酷契约，亦是长期受屈辱者极端的尊严诉求。"),
            ("铅匣子：", "‘谁选择了我，必须准备交出并牺牲他所拥有的一切’，象征真正的爱需要放下虚荣与算计。"),
            ("订婚戒指：", "忠诚与信任的象征，在喜剧外壳下对婚姻信任进行微小试炼。")
        ],
        "themes": "法律的字面解释与精神实质；种族歧视导致的仇恨螺旋；慈悲作为最高正义的价值。",
        "socratic": "Q1：鲍西娅剥夺夏洛克全部财产并强迫其改宗，这符合她宣扬的‘慈悲’吗？\nQ2：夏洛克的仇恨，有多少是由威尼斯基督徒平日的傲慢与欺凌亲手浇灌出来的？",
        "action": "沟通工具：‘同理心辩护演练’——站在利益冲突中最反对你的那一方立场，写一段能让全场沉默的真实自白。"
    },

    "莎士比亚-仲夏夜之梦": {
        "title_cn": "仲夏夜之梦", "title_en": "A Midsummer Night's Dream",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "浪漫喜剧的无上巅峰 · 爱情狂喜与林间奇幻之夜",
        "hero_quote": "疯子、情人与诗人，都拥有狂热的想象力；他们看见的世界，远比冰冷的理智所能理解的辽阔。",
        "year": "约 1595–1596 年", "genre": "浪漫轻喜剧 / 诗化神话剧",
        "length": "全五幕", "age": "10+ 岁 / 全年龄文学通识",
        "criteria": "狂欢节狂乱与现实秩序和解的诗学建构",
        "warning": "切勿以为这只是一出无厘头的神仙打闹喜剧。雅典城邦代表着严苛的理智与父权法统，而林地代表着被压抑的潜意识与本能狂欢。莎翁借魔药揭示了爱情中非理性的盲目与神圣。",
        "highlights": [
            "四位青年情侣在魔法森林中的错乱追踪。",
            "仙王仙后的争执与恶作剧精灵迫克（Puck）。",
            "织工波顿变成驴头却得仙后倾慕的荒诞狂欢。"
        ],
        "context": "伊丽莎白时代的宫廷庆典与民间狂欢节传统交织，赞美青春与爱欲冲破封建门第羁绊的生命力。",
        "svg": """<svg viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="90" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">雅典城邦 (Athens)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">公爵泰修斯 · 严苛父权法律</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">理智 · 秩序 · 婚姻专横</text>
          <rect x="450" y="30" width="180" height="90" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">魔法林地 (Woods)</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">仙王奥布朗 · 仙后提泰妮娅</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">花汁迷魂 · 潜意识与狂乱</text>
          <rect x="250" y="160" width="180" height="80" rx="8" fill="#8c2d19" />
          <text x="340" y="190" fill="#fff" font-weight="700" text-anchor="middle">精灵迫克 (Puck)</text>
          <text x="340" y="210" fill="#f0dcd8" font-size="11" text-anchor="middle">滴眼魔汁 · 乱点鸳鸯 · 梦境谢幕</text>
          <line x1="230" y1="80" x2="450" y2="80" stroke="#8c2d19" stroke-width="2" stroke-dasharray="4,4" />
        </svg>""",
        "characters": [
            ("迫克 (Puck)", "顽皮伶俐的小精灵", "仙王侍从，挥洒情水制造错乱，结尾向观众鞠躬道破全剧宛如一梦。"),
            ("赫米娅与拉山德", "坚贞叛逃的情侣", "宁愿死也不愿顺从包办婚姻，私奔至林中引发戏剧连锁反应。"),
            ("织工波顿", "自大而可爱的底层手艺人", "头颅被化作毛驴却坦然享受仙后求爱，成为全剧最有喜感的凡俗象征。")
        ],
        "perception": "表面是一场夜色中的奇幻闹剧；深处展示了人类理智在爱欲面前的彻底缴械。唯有经历过森林中无序的试炼，年轻人的爱意才由盲目的占有走向真诚的托付。",
        "conflict": "城邦法统压制 vs 自由爱欲释放；白昼冷酷理智 vs 黑夜狂乱想象。",
        "turning_point": "迫克误把魔汁滴入拉山德眼中，导致两位青年同时倒戈追求海伦娜，引发四角关系的大乱斗。",
        "symbols": [
            ("爱懒花汁：", "丘比特之箭射中的紫色野花汁液，象征爱情猝不及防、不可理喻的非理性魔力。"),
            ("驴头：", "将最粗俗的驴头套在凡俗男子头上，象征人在热恋盲目中‘把朽木视作天仙’的自我催眠。")
        ],
        "themes": "爱情的盲目与神圣；虚幻梦境对现实僵化秩序的治愈力量；戏剧艺术本身的造梦本质。",
        "socratic": "Q1：如果爱完全受理性计算支配，人类还会拥有诗歌、艺术和狂喜吗？\nQ2：醒来之后，情侣们真能分清哪一段是真实、哪一段是仲夏夜的梦吗？",
        "action": "观察任务：记录身边一个陷入热恋的人与平时截然相反的非理性举动，感受人类心灵在‘魔药’下的奇妙重塑。"
    },

    "莎士比亚-暴风雨": {
        "title_cn": "暴风雨", "title_en": "The Tempest",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "莎翁晚年绝笔传奇剧 · 宽恕、自省与艺术魔杖的封存",
        "hero_quote": "我们都是梦中的材料；我们微渺的一生，在沉睡中前后缠绕。",
        "year": "约 1610–1611 年", "genre": "传奇剧 / 宽恕与和解 / 文明寓言",
        "length": "全五幕", "age": "12+ 岁 / 青年与思辨读者",
        "criteria": "权力的复仇与主动放弃的崇高感",
        "warning": "不要把普洛斯彼罗当作毫无争议的完美智者。他在孤岛上虽然掌控魔法，但对土著卡利班的奴役和对精灵爱丽儿的控制，构成了西方殖民主义与启蒙专制最早的原型隐喻。",
        "highlights": [
            "海上暴风雨的神奇掀起与无伤海难。",
            "复仇权柄在握时的决绝宽恕。",
            "莎翁借主角折断魔杖、将魔法书沉入深海向舞台告别。"
        ],
        "context": "大航海时代开启，新大陆殖民探险故事流传伦敦。晚年的莎士比亚历尽人间沧桑，从悲剧的血雨腥风走向和解与超越。",
        "svg": """<svg viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="80" rx="8" fill="#1d3557" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">普洛斯彼罗 (Prospero)</text>
          <text x="340" y="68" fill="#cad5e2" font-size="11" text-anchor="middle">被逐米兰公爵 · 魔法全知掌控者</text>
          <text x="340" y="88" fill="#cad5e2" font-size="11" text-anchor="middle">折断魔杖 · 宽恕仇敌</text>
          <rect x="40" y="150" width="160" height="75" rx="8" fill="#2a9d8f" />
          <text x="120" y="178" fill="#fff" font-weight="700" text-anchor="middle">精灵爱丽儿 (Ariel)</text>
          <text x="120" y="198" fill="#e5e8eb" font-size="11" text-anchor="middle">风之精灵 · 渴望绝对自由</text>
          <rect x="480" y="150" width="160" height="75" rx="8" fill="#8c2d19" />
          <text x="560" y="178" fill="#fff" font-weight="700" text-anchor="middle">卡利班 (Caliban)</text>
          <text x="560" y="198" fill="#f0dcd8" font-size="11" text-anchor="middle">岛屿原住民 · 被奴役反抗者</text>
          <line x1="250" y1="60" x2="160" y2="150" stroke="#2a9d8f" stroke-width="2" />
          <line x1="430" y1="60" x2="520" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("普洛斯彼罗", "流亡公爵与魔法宗师", "最终领悟‘美德的稀罕在于宽恕，而非复仇’，主动弃绝超凡力量重返平凡人间。"),
            ("米兰达与斐迪南", "新生代的纯洁象征", "仇敌后代的真挚相爱融化了上一代的政治宿怨。"),
            ("卡利班", "粗野的岛屿遗孤", "学会了文明的语言，却用它来诅咒文明施加的锁链，体现了殖民启蒙的创伤。")
        ],
        "perception": "表面是一部带魔法色彩的孤岛历险传奇；深处探讨了‘拥有绝对惩罚力量的人，如何战胜复仇冲动选择宽恕’。",
        "conflict": "快意复仇的诱惑 vs 宽恕救赎的理性；文明的启蒙教化 vs 原生态自尊的被掠夺。",
        "turning_point": "爱丽儿对普洛斯彼罗说：‘如果我是人类，我都会同情他们。’公爵大悟：‘如果连你这非肉体之躯都懂怜悯，我一个凡人怎能不行宽恕？’",
        "symbols": [
            ("折断的魔杖与沉入深海的书：", "象征艺术家放下掌控生杀予夺的创作神力，接受凡人有常的生命归宿。"),
            ("暴风雨：", "人造的虚幻磨难，清洗罪人的骄慢，使迷失者在恐惧中重获良知。")
        ],
        "themes": "宽恕超越复仇的道德崇高；文明与野蛮的辩证反思；艺术创作与现实生活的告别曲。",
        "socratic": "Q1：拥有伤害仇敌的力量却主动放弃，这是一种软弱，还是人类能达到的最稀缺的勇敢？\nQ2：卡利班身上体现了欧洲航海时代对异域文明怎样的偏见与愧疚？",
        "action": "心理演练：找出一位曾经冒犯过你的人，在脑海中完成‘将复仇魔杖沉入深海’的释怀仪式，感受情绪重负的脱落。"
    },

    "莎士比亚-第十二夜": {
        "title_cn": "第十二夜", "title_en": "Twelfth Night",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "狂欢节时期的性别错位喜剧 · 虚荣、痴情与音乐的盛宴",
        "hero_quote": "倘若音乐是爱的食粮，那么奏下去吧；给我过量的音乐，让欲望因为过饱而致疾，终于厌倦！",
        "year": "约 1601–1602 年", "genre": "浪漫抒情喜剧 / 狂欢节狂喜",
        "length": "全五幕", "age": "12+ 岁 / 青年经典",
        "criteria": "身份错位下的情感真实性试炼",
        "warning": "不要只关注薇奥拉女扮男装的搞笑桥段。清教徒管家马伏里奥被捉弄并被关进小黑屋的冷酷遭遇，暗含了莎翁对自命不凡、毫无生活情趣的伪道德家的辛辣讽刺，但也透露出一抹阴郁的现实余响。",
        "highlights": [
            "双胞胎兄妹海难失散引发的阴差阳错。",
            "公爵爱伯爵夫人、夫人爱男装薇奥拉的奇妙三角恋。",
            "马伏里奥黄色长袜与十字绑带的荒唐求爱信受骗记。"
        ],
        "context": "伊丽莎白时期圣诞节后第十二天的‘主显节夜’狂欢，在这一天世俗秩序被暂时颠倒，仆人做主人，女人扮男人。",
        "svg": """<svg viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">薇奥拉 (Viola / 塞萨里奥)</text>
          <text x="340" y="68" fill="#e5e8eb" font-size="11" text-anchor="middle">女扮男装 · 传递情书却身陷相思</text>
          <rect x="40" y="140" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">奥西诺公爵 (Orsino)</text>
          <text x="130" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">沉溺于爱情想象的贵族情人</text>
          <rect x="460" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">奥利维娅伯爵小姐</text>
          <text x="550" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">哀悼兄长誓言禁欲 · 狂热爱上侍童</text>
          <line x1="250" y1="70" x2="160" y2="140" stroke="#1d3557" stroke-width="2" />
          <line x1="430" y1="70" x2="520" y2="140" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("薇奥拉", "机敏深情的女主角", "承受巨大的情感折磨，在为主子向情敌求爱的同时隐藏深情，展现了高贵的人格魅力。"),
            ("小丑费斯特 (Feste)", "游走宫廷的清醒歌者", "看似疯癫实则看透一切虚荣，他的歌声给全剧蒙上一层淡淡的时光流逝忧伤。"),
            ("马伏里奥", "道貌岸然的清教徒总管", "自我感动、缺乏幽默感，最终沦为全剧唯一未能和解的被排斥者。")
        ],
        "perception": "表面是一场令人捧腹的错位求爱喜剧；深处探讨了‘人们爱上的究竟是真实的对方，还是自己脑海中虚构的爱情幻影’。",
        "conflict": "性别外表伪装 vs 内心真挚情感；虚伪的自我沉醉 vs 真实的生活乐趣。",
        "turning_point": "孪生哥哥塞巴斯蒂安的平安登岸并被误认为薇奥拉，使错乱的死结瞬间自然解开，人人各得其所。",
        "symbols": [
            ("男装戏服：", "庇护女性穿行于男权社会的盾牌，也是真情流露的一道透明屏障。"),
            ("黄色袜子与十字交叉绑带：", "虚荣心与被操纵愚昧的鲜明外化标记。")
        ],
        "themes": "爱情具有超越性别与身份的盲目力量；狂欢之后对世俗秩序的回归与沉思。",
        "socratic": "Q1：公爵最初爱的究竟是奥利维娅，还是‘沉浸在失恋痛苦中的自己’？\nQ2：为什么一个没有幽默感、自命高人一等的人，在群体中往往最容易沦为残酷笑柄？",
        "action": "自我反思：检查自己是否在某种人际关系中戴着某种‘假装坚强’的面具，尝试在信任的朋友面前卸下一角防备。"
    },

    "莎士比亚-尤利乌斯·恺撒": {
        "title_cn": "尤利乌斯·恺撒", "title_en": "Julius Caesar",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "政治心理与修辞煽动的巅峰教科书 · 共和挽歌与弑君漩涡",
        "hero_quote": "不是我不爱恺撒，而是我更爱罗马！",
        "year": "约 1599 年", "genre": "罗马历史悲剧 / 政治辩论剧",
        "length": "全五幕", "age": "14+ 岁 / 青年与政治通识",
        "criteria": "高尚道德动机与灾难政治后果的背离机制",
        "warning": "切勿简单站在布鲁图斯或恺撒任何一方。莎翁无情揭示了：<strong>最可怕的政治灾难，往往是由那些动机最崇高、道德最无可挑剔的理想主义者一手造成的。</strong>布鲁图斯爱罗马共和，却因轻信演说和对政治现实的幼稚，引发了席卷帝国的血腥内战。",
        "highlights": [
            "元老院议事堂二十三刀刺杀恺撒的惊心动魄。",
            "安东尼在恺撒葬礼上颠倒乾坤的传世演说大反转。",
            "布鲁图斯与卡西乌斯在军营大帐中的激烈争吵与英雄绝命。"
        ],
        "context": "伊丽莎白女王年老未立储君，英国面临王权更迭还是内战动荡的焦虑。莎翁借古罗马史反思独裁与共和之争。",
        "svg": """<svg viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">尤利乌斯·恺撒 (Caesar)</text>
          <text x="340" y="68" fill="#f0dcd8" font-size="11" text-anchor="middle">罗马独裁官 · 战无不胜 · 倒在元老院</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">布鲁图斯 (Brutus)</text>
          <text x="130" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">高尚共和派 · 理想主义弑君者</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#242930" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">马克·安东尼 (Antony)</text>
          <text x="550" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">忠臣复仇 · 广场修辞煽动大师</text>
          <line x1="170" y1="140" x2="270" y2="95" stroke="#1d3557" stroke-width="2" />
          <line x1="490" y1="140" x2="410" y2="95" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("布鲁图斯", "最受尊敬的罗马贵族", "将刺杀挚友视作奉献给国家的祭品，因不许伤害安东尼并允许其公开演说犯下致命战略错误。"),
            ("马克·安东尼", "智勇双全的演说大师", "在葬礼上以‘布鲁图斯是一个正派人’的反讽辞令点燃暴民狂怒，瞬间改写历史进程。"),
            ("卡西乌斯", "敏锐现实的政治密谋者", "早早看穿安东尼的危险，却在布鲁图斯崇高名望的固执下节节退让，最终自刎沙场。")
        ],
        "perception": "表面是一部暗杀独裁者引发的历史悲剧；深处揭示了‘群体心理极易被语言修辞操纵’的残酷政治真相。",
        "conflict": "维持共和自由的原则 vs 建立强力统治的现实；高尚的个人道德 vs 冷酷的政治算计。",
        "turning_point": "第三幕第二场安东尼的葬礼演说：从‘我来是埋葬恺撒，不是来赞扬他’起步，层层递进点燃群众怒火，将刺杀者逼入流亡绝境。",
        "symbols": [
            ("恺撒带血的长袍：", "安东尼展示给暴民看的直观伤口，成为唤起群体非理性复仇最致命的情感利刃。"),
            ("三月十五日凶兆 (Ides of March)：", "盲人预言家的警告，象征政治狂人对命运规律的傲慢蔑视。")
        ],
        "themes": "理想主义在现实政治中的惨败；修辞话术对民主民意的操纵陷阱；英雄主义与历史大势的错位。",
        "socratic": "Q1：一个为了国家公义而背叛谋杀知己好友的人，他建立的新政权真的可能带来正义吗？\nQ2：安东尼的演讲手法，与今天社交网络上的情绪煽动与流量操控有何惊人相似之处？",
        "action": "沟通分析：重读安东尼演讲词，拆解他如何通过‘先肯定对方、再展示细节证据、最后煽动情绪’三步完成听众心理操控。"
    },

    "莎士比亚十四行诗": {
        "title_cn": "莎士比亚十四行诗", "title_en": "Shakespeare's Sonnets",
        "author_cn": "威廉·莎士比亚", "author_en": "William Shakespeare",
        "sub_desc": "英语抒情诗的珠穆朗玛 · 爱、时间、欲望与不朽诗篇",
        "hero_quote": "我怎能把你比作炎炎夏日？你比夏天更可爱，也更温婉温良。",
        "year": "1609 年出版", "genre": "古典抒情十四行诗集",
        "length": "共 154 首", "age": "14+ 岁 / 青年与诗歌精读",
        "criteria": "格律形式对称性与时间哲学抗争深度",
        "warning": "切勿以为这只是一部甜腻的情诗集。莎翁打破了彼特拉克传统的苍白赞歌，直面黑肤黑发的黑女士、情欲的肮脏自责、时间的冷酷镰刀，乃至自我的老去与丑陋，具有极高的精神解剖诚实度。",
        "highlights": [
            "第18首‘我怎能把你比作夏日’对诗歌赋予生命不朽的崇高宣告。",
            "前126首对‘美貌青年’的劝婚、赞美与友情拉扯。",
            "后28首对神秘‘黑女士’撕扯难熬的情欲肉体纠葛。"
        ],
        "context": "1590年代伦敦瘟疫导致剧院频繁关闭，莎翁在沉潜中倾注毕生诗艺，探索抑扬五步格十四行诗的极限表现力。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="70" rx="8" fill="#1d3557" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">诗人自我 (The Poet)</text>
          <text x="340" y="68" fill="#cad5e2" font-size="11" text-anchor="middle">衰老焦虑 · 抵抗时间吞噬</text>
          <rect x="40" y="140" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="130" y="168" fill="#fff" font-weight="700" text-anchor="middle">美貌青年 (Fair Youth)</text>
          <text x="130" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">第1–126首 · 理想之美与劝婚</text>
          <text x="130" y="208" fill="#e5e8eb" font-size="11" text-anchor="middle">通过诗歌战胜死亡</text>
          <rect x="460" y="140" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="550" y="168" fill="#fff" font-weight="700" text-anchor="middle">黑女士 (Dark Lady)</text>
          <text x="550" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">第127–154首 · 肉体诱惑与背叛</text>
          <text x="550" y="208" fill="#f0dcd8" font-size="11" text-anchor="middle">反传统审美的真实情欲</text>
          <line x1="260" y1="90" x2="160" y2="140" stroke="#2a9d8f" stroke-width="2" />
          <line x1="420" y1="90" x2="520" y2="140" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("诗人叙述者", "直面衰老与激情的灵魂", "深知时间的镰刀终将扫荡一切，唯有将爱铭刻在诗行中抵御虚无。"),
            ("贵族美貌青年", "希腊古典式的完美偶像", "承载了诗人对青春不逝、精神繁衍的至高寄托。"),
            ("黑肤女士", "撕碎虚伪道德审美的叛逆情人", "不符合当时白皙金发的流行审美，却以强烈的生命力令诗人深陷其中。")
        ],
        "perception": "表面是一部关于爱与欲望的私密诗篇；深处是一场‘人类艺术与无情时间摧残的壮烈决斗’。",
        "conflict": "生命的易逝衰亡 vs 诗歌的永恒不朽；理性的崇高纯洁 vs 肉体的放荡沉溺。",
        "turning_point": "第18首的最后两行对联句：‘只要有人活着，只要眼睛看得见，这诗便永存，并赐给你生命！’建立了艺术对时间的胜利。",
        "symbols": [
            ("时间的镰刀与沙漏：", "冷酷无情的自然法则，收割一切人间荣华美貌。"),
            ("夏日：", "短暂、热烈却转瞬即逝的生命青春代名词。")
        ],
        "themes": "艺术赋能生命以永恒；情感世界的道德灰色与真实自省；衰老与时间的哲学沉思。",
        "socratic": "Q1：如果诗歌确实让那个美貌青年活到了四百年后的今天，读者记住的究竟是青年本人，还是莎士比亚的诗才？\nQ2：当莎士比亚在第130首描写‘我情妇的眼睛一点都不像太阳’时，他为何能创造出远比空洞溢美更动人的真爱？",
        "action": "仿写练习：挑选一件正在老去的日常物品（如旧笔记本或一件旧外套），模仿十四行诗的对比节奏，写一段关于‘磨损与深情’的短诗。"
    },

    "莎士比亚故事集": {
        "title_cn": "莎士比亚故事集", "title_en": "Tales from Shakespeare",
        "author_cn": "查尔斯·兰姆 & 玛丽·兰姆", "author_en": "Charles and Mary Lamb",
        "sub_desc": "通往文学万神殿的黄金桥梁 · 戏剧向叙事散文的典范化身",
        "hero_quote": "这些故事是为年轻心灵准备的一杯芬芳佳酿，愿你们从中汲取仁爱、高贵与勇气的滋养。",
        "year": "1807 年出版", "genre": "经典改编散文故事集",
        "length": "收录 20 部名剧", "age": "9+ 岁 / 青少年与入门必读",
        "criteria": "剧本冲突向叙事散文转化的通畅度与精神忠实度",
        "warning": "切勿认为这只是‘小儿科简写本’。兰姆姐弟在极为艰辛的生活中，将莎翁复杂的舞台台词巧妙化解为行云流水的散文叙事，同时近乎完整保留了原著的经典金句与道德内核，是世界文学史上最伟大的普及典范。",
        "highlights": [
            "玛丽·兰姆负责改编温婉优雅的喜剧部（如李尔王、威尼斯商人）。",
            "查尔斯·兰姆执笔凝重深邃的悲剧部（如哈姆雷特、奥赛罗）。",
            "搭建起无阅读门槛直通英国文学黄金顶峰的梯子。"
        ],
        "context": "19世纪初英国浪漫主义兴起，兰姆姐弟旨在让年轻读者摆脱枯燥的说教读物，通过莎士比亚的文学天才滋养丰富的人文心灵。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="250" y="20" width="180" height="70" rx="8" fill="#1d3557" />
          <text x="340" y="48" fill="#fff" font-weight="700" text-anchor="middle">莎士比亚原作剧本</text>
          <text x="340" y="68" fill="#cad5e2" font-size="11" text-anchor="middle">繁复古英语 · 舞台隐喻</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">兰姆故事集 (Tales)</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">生动叙事 · 道德启蒙 · 保留诗意</text>
          <line x1="340" y1="90" x2="340" y2="140" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("兰姆姐弟（编者）", "深情平实的引路人", "以惊人的文学品味剔除粗俗杂质，保留莎翁崇高心智。")
        ],
        "perception": "表面是一部通俗好看的故事书；深处是一场跨越两百年的文学接力，让世界上每一个孩子都能在最柔韧的心灵时期邂逅人类最伟大的故事。",
        "conflict": "原作高耸的语言壁垒 vs 初学读者渴望探索的好奇心。",
        "turning_point": "通过情节散文化，使原本必须依托舞台演员表现的内心冲突，变成平易近人、发人深省的心灵对话。",
        "symbols": [
            ("故事的壁炉角：", "象征文学名著从贵族宫廷剧场走向千家万户的温暖转变。")
        ],
        "themes": "经典普及的创造性转化；青少年人文同理心的早期培育。",
        "socratic": "Q1：把剧本改成散文，失去了演员的直观表演，但读者获得了什么新的想象自由？",
        "action": "转述挑战：选一个你最喜欢的戏剧冲突段落，尝试用口语讲给一位完全没读过原著的家人听，测试能否让他听入迷。"
    },

    "戏剧故事": {
        "title_cn": "西方古典戏剧故事选", "title_en": "Stories from Classical Drama",
        "author_cn": "古典戏剧编委会", "author_en": "Classical Drama Collection",
        "sub_desc": "从古希腊悲剧到近现代名剧 · 人类戏剧精神的源头活水",
        "hero_quote": "戏剧是把人生的困境放在放大镜下，让我们在流泪中清洗灵魂，重获清明。",
        "year": "经典综合卷", "genre": "戏剧鉴赏故事汇编",
        "length": "经典名著多剧荟萃", "age": "12+ 岁 / 中学与通识通览",
        "criteria": "戏剧核心行动线与悲喜冲突机制解析",
        "warning": "读戏剧故事不要仅仅看‘最后谁死了谁活着’。戏剧的灵魂在于<strong>‘情境逼仄下的两难抉择’</strong>——每个人都有自己的正义，当两种正义撞击在一起，悲剧便如雷霆般诞生。",
        "highlights": [
            "涵盖命运悲剧、性格悲剧与社会问题剧的演进模型。",
            "剖析亚里士多德‘卡塔西斯（Catharsis 净化）’的审美心理。",
            "提炼古典戏剧不可缺少的‘三一律’与高潮转折技巧。"
        ],
        "context": "从雅典卫城酒神剧场的万民共鸣，到近代市民社会的镜框舞台，戏剧始终是文明反思自我道德的最强公器。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="80" width="160" height="80" rx="8" fill="#1d3557" />
          <text x="130" y="115" fill="#fff" font-weight="700" text-anchor="middle">命运悲剧 (希腊)</text>
          <text x="130" y="135" fill="#cad5e2" font-size="11" text-anchor="middle">人与神意抗争 · 俄狄浦斯</text>
          <rect x="260" y="80" width="160" height="80" rx="8" fill="#8c2d19" />
          <text x="340" y="115" fill="#fff" font-weight="700" text-anchor="middle">性格悲剧 (文艺复兴)</text>
          <text x="340" y="135" fill="#f0dcd8" font-size="11" text-anchor="middle">欲望自毁 · 莎士比亚</text>
          <rect x="470" y="80" width="160" height="80" rx="8" fill="#2a9d8f" />
          <text x="550" y="115" fill="#fff" font-weight="700" text-anchor="middle">社会戏剧 (近代)</text>
          <text x="550" y="135" fill="#e5e8eb" font-size="11" text-anchor="middle">制度压迫 · 易卜生/契诃夫</text>
          <line x1="210" y1="120" x2="260" y2="120" stroke="#84908a" stroke-width="2" />
          <line x1="420" y1="120" x2="470" y2="120" stroke="#84908a" stroke-width="2" />
        </svg>""",
        "characters": [
            ("悲剧主人公群像", "在命运悬崖边行走的凡人", "具备超凡的热情与坚持，却因微小的‘悲剧过失（Hamartia）’坠入深渊。")
        ],
        "perception": "戏剧把人类逼进没有退路的死角，逼迫灵魂在刀锋上作出选择。",
        "conflict": "个体微弱自由意志 vs 庞大宿命或社会结构冰冷法则。",
        "turning_point": "戏剧核心的‘发现（Anagnorisis）’与‘突转（Peripeteia）’：人物在瞬间认清残酷真相，命运发生断崖式跌落。",
        "symbols": [
            ("面具与聚光灯：", "揭去日常伪装，暴露出最赤裸裸的欲望与良知。")
        ],
        "themes": "在痛苦中磨砺出来的尊严；对世间苦难的深沉悲悯与精神净化。",
        "socratic": "Q1：如果好人得到好报、坏人立刻受罚，戏剧还会像今天这样令人心碎神驰吗？",
        "action": "舞台构思：选取生活中一次难忘的争吵，尝试把它改写为只有两把椅子、两个演员的五分钟独幕话剧对白。"
    }
}

def render_book_guide(info):
    title_cn = info["title_cn"]
    title_en = info["title_en"]
    author_cn = info["author_cn"]
    author_en = info["author_en"]
    sub_desc = info["sub_desc"]
    hero_quote = info["hero_quote"]

    data = {
        "title_cn": title_cn, "title_en": title_en,
        "author_cn": author_cn, "author_en": author_en,
        "sub_desc": sub_desc, "hero_quote": hero_quote
    }

    # Sec 01
    sec01 = f"""      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">作者</div><div class="spec-val">{author_cn}</div></div>
        <div class="spec-item"><div class="spec-label">创作年份</div><div class="spec-val">{info['year']}</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">{info['genre']}</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">{info['length']}</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">{info['age']}</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">{info['criteria']}</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>{info['warning']}
      </div>
      <div class="sub-heading">三大核心看点</div>
"""
    for idx_h, hl in enumerate(info["highlights"], 1):
        sec01 += f"""      <div class="card-box"><strong>看点 {idx_h}：</strong>{hl}</div>\n"""

    # Sec 02
    sec02 = f"""      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">{info['context']}</p>
      <div class="svg-wrap">
        {info['svg']}
      </div>
      <div class="sub-heading">核心角色与功能图谱</div>
      <ul class="bullet-list">
"""
    for c_name, c_role, c_desc in info["characters"]:
        sec02 += f"""        <li><strong>{c_name}（{c_role}）：</strong>{c_desc}</li>\n"""
    sec02 += "      </ul>"

    # Sec 03
    sec03 = f"""      <div class="sub-heading">表面与深处</div>
      <p>{info['perception']}</p>"""

    # Sec 04
    sec04 = f"""      <div class="sub-heading">核心冲突与转折</div>
      <p><strong>核心冲突模型：</strong>{info['conflict']}</p>
      <div class="card-box">
        <strong>决定性转折点：</strong>{info['turning_point']}
      </div>"""

    # Sec 05
    sec05 = f"""      <div class="sub-heading">人性的深度解构</div>
      <p>作品超越了简单的道德标签，人物的行事动机深植于特定的时代处境与欲望拉扯之中。每一个重要角色的沉浮，都映射出社会肌理的幽暗真相。</p>"""

    # Sec 06
    sec06 = f"""      <div class="sub-heading">核心意象与象征网络</div>
      <ul class="bullet-list">
"""
    for sym_name, sym_desc in info.get("symbols", [("戏剧核心意象：", "凝结全剧冲突的象征媒介。")]):
        sec06 += f"""        <li><strong>{sym_name}</strong>{sym_desc}</li>\n"""
    sec06 += "      </ul>"

    # Sec 07
    sec07 = f"""      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        {info['themes']}
      </div>"""

    # Sec 08
    sec08 = """      <div class="sub-heading">解释边界与过度阐释警惕</div>
      <p>始终回归文本具体的台词与时代情境，警惕用现代人的后见之明对古人的困境进行轻佻的道德说教。</p>"""

    # Sec 09
    sec09 = """      <div class="sub-heading">现实关系与思想迁移</div>
      <p>经典之所以历久弥新，正是因为它们提出的生存难题跨越了时代。人性的贪婪、恐惧、深情与软弱，在今天依然以全新的形式在现代社会中重演。</p>"""

    # Sec 10
    sec10 = """      <div class="sub-heading">如何把作品讲给别人听</div>
      <p>跳出枯燥的剧情复述，直击主人公面对的两难死局，用一句话引起听者的共情与好奇。</p>"""

    # Sec 11
    sec11 = """      <div class="sub-heading">最小通达路径</div>
      <p>挑选戏剧中最具戏剧张力的高潮场次精读，感受语言的锋芒与节奏的变化。</p>"""

    # Sec 12
    sec12 = f"""      <div class="sub-heading">苏格拉底式深想追问</div>
      <div class="card-box">
        {info['socratic']}
      </div>"""

    # Sec 13
    sec13 = f"""      <div class="sub-heading">创造行动与思维工具</div>
      <div class="card-box">
        {info['action']}
      </div>"""

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
    print("=== 开始批量构建【批次 A：莎士比亚与戏剧系列】 ===")
    from build_shakespeare_batch import build_hamlet
    
    # 1. Hamlet
    h_html = build_hamlet()
    h_dir = os.path.join(BASE_DIR, "莎士比亚-哈姆雷特")
    if os.path.exists(h_dir):
        with open(os.path.join(h_dir, "guide.html"), "w", encoding="utf-8") as f:
            f.write(h_html)
        with open(os.path.join(h_dir, "guide.index"), "w", encoding="utf-8") as f:
            f.write(h_html)
        print(f"[OK] 莎士比亚-哈姆雷特 -> guide.html & guide.index 写入完成 ({len(h_html)} 字节)")

    # 2-10: 其它 9 本
    for book_name, info in BOOKS_A.items():
        target_dir = os.path.join(BASE_DIR, book_name)
        if not os.path.exists(target_dir):
            print(f"[WARN] 目录不存在: {target_dir}")
            continue
        html = render_book_guide(info)
        # 校验
        soup = BeautifulSoup(html, "html.parser")
        assert len(soup.find_all("details", class_="guide-section")) == 13
        assert len(soup.find_all("svg")) >= 1
        with open(os.path.join(target_dir, "guide.html"), "w", encoding="utf-8") as f:
            f.write(html)
        with open(os.path.join(target_dir, "guide.index"), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[OK] {book_name} -> guide.html & guide.index 写入完成 ({len(html)} 字节)")

    print("=== 批次 A 顺利完工 ===")

if __name__ == "__main__":
    main()
