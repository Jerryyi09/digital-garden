#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch D: Philosophy, Stream of Consciousness & Fantasy Saga (12 books)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT
from build_batch_a import render_book_guide

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

BOOKS_D = {
    "Walden": {
        "title_cn": "瓦尔登湖", "title_en": "Walden",
        "author_cn": "亨利·戴维·梭罗", "author_en": "Henry David Thoreau",
        "sub_desc": "自然主义与简约生活的至高圣经 · 湖畔林间的孤独静思长卷",
        "hero_quote": "我步入丛林，因为我希望生活得从容自得；我只想面对生活最根本的要素，看看我是否能学到它要教给我的东西，以免在临死时，才发现自己从未真正活过。",
        "year": "1854 年出版", "genre": "哲理散文 / 自然主义经典 / 超验主义传世作",
        "length": "约 22 万字", "age": "14+ 岁 / 终身必读精神经典",
        "criteria": "极简物质生活与精神丰盈自由的实践典范",
        "warning": "不要把梭罗在瓦尔登湖畔的两年两个月误解为‘完全与世隔绝的隐居野人’。湖畔离康科德小镇只有两英里，梭罗经常步行去镇上借书、访友。他做的是一场极其精确的‘现代经济学反向实验’——向世人证明，维持体面生活所需的必需品何其稀少，人们不必为了虚荣将毕生卖给无休止的劳役。",
        "highlights": [
            "第一章《经济篇》以会计般的严密账目算清‘生存必需品’的真实成本。",
            "描绘瓦尔登湖在四季更迭中如天神之眼般澄澈深邃的湖水色泽变化。",
            "在豆田里独自锄地、倾听林中松雀鸣唱与自然完全交融的物我两忘时刻。"
        ],
        "context": "19世纪中叶美国工业化起步，铁路向西贯通，商业物欲膨胀。爱默生、梭罗倡导超验主义，呼唤重返自然。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">喧嚣城镇文明 (Concord)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">日夜奔忙 · 房贷账单</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">‘绝大多数人生活在平静的绝望中’</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">瓦尔登湖 (Walden Pond)</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">自建木屋 · 躬耕两亩豆田</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">极简清醒 · 精神的至高自由</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">梭罗的生活实验</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">减法生活 · 证明生命本身无需借贷</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("梭罗", "超验主义的孤独践行者", "借了一把斧头走进深林，以二十八美元自建木屋，证明一个人只要把欲望降到最低，每年只需工作六周即可获得彻底的思想自由。"),
            ("瓦尔登湖", "大自然纯洁清明的神圣眼睛", "无论人间发生多少战乱喧嚣，湖水始终碧绿如洗，映照着天光云影，成为治愈疲惫心智的天然神庙。")
        ],
        "perception": "表面是一部荒野木屋隐居实录与自然观察手记；深处是一份人类从物质拜物教中自我解放的独立宣言。",
        "conflict": "社会习俗强加的繁重物质消费枷锁 vs 灵魂渴求从容、清醒呼吸的内在呼唤。",
        "turning_point": "春天的破冰归来：全书在漫长严冬后迎来湖面冰层在巨响中崩解融化，大地复苏，象征经历过极简沉思后人类灵魂的彻底重生日出。",
        "symbols": [
            ("一把借来的斧头：", "‘物归原主时比借来时磨得更锋利’，象征人向自然索取的克制与对工具的敬意。"),
            ("深不见底的湖水：", "村民流传湖没有底，梭罗用铅垂线精确测出水深一百零二英尺，证明‘神圣的真理同样经得起实证理性的测量’。")
        ],
        "themes": "简化，简化，再简化；只有在清醒的孤独中才能听见生命深处的呼吸；与大自然和谐共处的恒常平静。",
        "socratic": "Q1：我们拼命加班赚钱购买的那些昂贵物品，究竟是在给我们的生活带来快乐，还是把我们变成了它们的守门奴仆？\nQ2：梭罗生活实验的最大价值，在于让每个人都去森林住木屋，还是让生活在都市的人保持一份随时可以脱卸身外之物的清醒？",
        "action": "断舍离练习：“二十四小时无电子设备静默日”——挑选一个周末完全关闭手机与电脑，只带一本书和一个笔记本散步半日，体会心神从数字焦虑中脱离的松弛感。"
    },

    "The Elegance of the Hedgehog": {
        "title_cn": "刺猬的优雅", "title_en": "The Elegance of the Hedgehog",
        "author_cn": "妙莉叶·芭贝里", "author_en": "Muriel Barbery",
        "sub_desc": "法国当代畅销哲理奇迹 · 伪装平庸深处的惊世孤独与美学顿悟",
        "hero_quote": "勒妮拥有刺猬的优雅：外表布满尖刺，坚固得令人望而生畏；但内里却极为细腻，怀抱一种孤独的优雅与无与伦比的高贵。",
        "year": "2006 年出版", "genre": "当代哲理小说 / 法国文学畅销名篇",
        "length": "约 18 万字", "age": "14+ 岁 / 青年与成人思辨",
        "criteria": "社会阶层傲慢眼光下平民女性的隐秘精神贵族气质",
        "warning": "不要把这本书当成温馨治愈的小资消遣。芭贝里运用康德、胡塞尔现象学、托尔斯泰与日本禅宗美学，深刻解剖了巴黎上流社会的虚荣、冷漠与无知。女门房勒妮之所以伪装成肥胖粗俗的看门人，是为了在隐秘的暗室里守护对真理与美至死不渝的朝圣。",
        "highlights": [
            "五十四岁寡居门房勒妮暗室里藏满康德哲学书与顶级日本红茶的秘密世界。",
            "十二岁天才富家少女芭洛玛决心在十三岁生日那天自杀的深刻日记。",
            "日本新住客小津格郎先生凭借一句安娜卡列尼娜的暗语识破勒妮的优雅灵魂。"
        ],
        "context": "当代巴黎左岸第七区富人公寓，阶级固化与刻板印象将底层劳动者彻底无形化，知识分子家庭充满空洞的修辞表演。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#131619" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">外在伪装：刺猬外壳</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">肥胖门房 · 电视杂音 · 猫食气味</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">满足上流社会对看门人的刻板偏见</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">内在密室：刺猬的优雅</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">托尔斯泰 · 现象学 · 小津安二郎</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">日本红茶 · 绝美茶花 · 灵魂相惜</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">小津格郎与芭洛玛的相认</text>
          <text x="340" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">‘幸福的家庭都是相似的’密码开启</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#131619" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("勒妮·米歇尔", "巴黎高级公寓的五十四岁女门房", "外表粗笨寡言，内心却是一个精通哲学与日本艺术的隐秘大师，用伪装保护自己不受世俗庸人惊扰。"),
            ("芭洛玛", "智商极高的十二岁富家女孩", "冷眼看穿全家人的虚伪自欺，因不想长大沦为‘鱼缸里的金鱼’策划自杀，却在勒妮身上重新看见了活下去的可能。"),
            ("小津格郎", "温文尔雅的日本退休绅士", "拥有一双能透过社会阶层标签洞察人类高贵灵魂的眼睛，用理解与尊重唤醒了勒妮走出刺猬防线的勇气。")
        ],
        "perception": "表面是一段巴黎高级公寓里不同阶层住户的相遇小品；深处探讨了‘真正的美与高贵究竟来自外在阶级出身，还是内在灵魂对真善美的自觉敬畏’。",
        "conflict": "社会阶层傲慢偏见的刻板囚笼 vs 真正高尚灵魂在孤独中的隐秘坚守。",
        "turning_point": "勒妮为了救助一名神志不清的流浪汉遭洗衣店卡车意外撞击：在生命的弥留之际，她不再恐惧死亡，而是平静地反思‘重要的不是死亡，而是我们在死的那一刻正在做什么——我们正在准备去爱’。",
        "symbols": [
            ("刺猬 (The Hedgehog)：", "浑身是刺却内里极度柔和的生物，象征用冷漠防线守护纯洁敏锐心灵的孤独智者。"),
            ("茶花掉落 (Camellia)：", "‘在时间暂停的刹那，一朵茶花落在青苔之上’，象征日本禅宗美学中在虚无现实中捕捉永恒刹那神圣微光的顿悟。")
        ],
        "themes": "以貌取人的人性盲区；艺术与美是对抗平庸虚无的最终救赎；跨越阶级与年龄的灵魂相惜。",
        "socratic": "Q1：为什么勒妮必须花费巨大精力假装自己‘粗俗无知’才能在社会中安全存活？这控诉了现代社会怎样的隐形暴力？\nQ2：芭洛玛在勒妮死后为什么放弃了自杀？她从勒妮身上学到了什么关于生命的全新答案？",
        "action": "审美暂停练习：在日常匆忙赶路的某个瞬间，停下脚步三十秒，寻找视野里一处微小的‘美’（一片落叶、一抹光斑），体会心灵暂时从功利世界跳脱的平静。"
    },

    "To the Lighthouse": {
        "title_cn": "到灯塔去", "title_en": "To the Lighthouse",
        "author_cn": "弗吉尼亚·伍尔夫", "author_en": "Virginia Woolf",
        "sub_desc": "意识流文学的巅峰高峰 · 时间流逝、家庭记忆与艺术追寻的永恒挽歌",
        "hero_quote": "生命并没有什么宏大的意义；有的只是无数微小的奇迹，在一瞬间被照亮，如同黑暗大海中的一圈涟漪。",
        "year": "1927 年出版", "genre": "现代主义意识流长篇 / 自传体抒情杰作",
        "length": "约 16 万字", "age": "15+ 岁 / 现代文学深读必读",
        "criteria": "主观时间体验与两性心智模式的交融建构",
        "warning": "不要试图用传统小说‘起承转合查案情’的眼光去寻找跌宕起伏的激烈剧情。整部作品的真正事件发生在人物脑海里的每一个心念电转之中。第二部《时光流逝》中，十年的战乱与拉姆齐太太的离世仅仅被放在几个冰冷的括号里一笔带过，展示了时间无情抹去一切人间体面的苍茫震撼。",
        "highlights": [
            "第一部《窗》中，拉姆齐太太张罗 Boeuf en Daube（法式炖牛肉）盛宴的温馨神圣瞬间。",
            "第二部《时光流逝》以空寂废弃的夏日海边度假屋为视角，描绘自然吞噬文明记忆的苍凉。",
            "第三部《灯塔》中，画家莉丽·布里斯科在画布正中画下一笔垂直线条的终极艺术顿悟——‘我已经有了我的幻象’。"
        ],
        "context": "一战后的英国 Bloomsbury 文化圈，传统维多利亚男权秩序与父权家庭在现代主义女性意识觉醒下的深刻重组。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">拉姆齐先生 (Mr. Ramsay)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">哲学学者 · 逻辑与事实狂徒</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">‘明天天气不好，去不成灯塔’</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">拉姆齐太太 (Mrs. Ramsay)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">母性光辉 · 情感粘合剂</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">守护孩子的愿望，融化冷酷</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">莉丽·布里斯科与灯塔</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">女性艺术创作 · 画布中央那一划</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("拉姆齐太太", "维多利亚家庭的完美女主人", "拥有整合人际断裂、赋予瞬间以永恒意义的奇迹能力，但内心深处同样体会着孤寂与空无。"),
            ("拉姆齐先生", "渴望在学术史留名的哲学家", "深陷自怜与才华停滞的焦虑，时刻需要女性的崇拜与心理抚慰，代表冷酷硬性的理性法则。"),
            ("莉丽·布里斯科", "独立不婚的先锋女画家", "拒绝传统贤妻良母角色，用十年的心灵沉淀，终于在拉姆齐太太去世后完成了对两性心智的艺术超拔。")
        ],
        "perception": "表面是一个家庭能否乘船前往海中灯塔的琐碎心愿；深处记录了时间如何在无声无息中侵蚀亲情与生命，以及唯有艺术创造才能为易逝的刹那铸造永恒的墓碑。",
        "conflict": "冷酷的男性逻辑事实 vs 温暖的女性情感直觉；无情流逝的物理时间 vs 凝结在艺术中的主观永恒瞬间。",
        "turning_point": "十年后终于乘船抵达灯塔：老去的拉姆齐先生在船头赞扬了当年被他冷酷对待的儿子詹姆斯，两代人在此刻达成历史性沉默和解，岸上的莉丽同步在画布上落下了最后一笔。",
        "symbols": [
            ("海中的灯塔 (The Lighthouse)：", "既是远方可望不可即的理想彼岸，也是在黑夜冰海中定期扫过海面的清冷指引。"),
            ("莉丽画布正中央的竖线：", "将色彩、明暗与两性撕扯重新归位的形式支点，象征女性自我意识的确立与艺术升华。")
        ],
        "themes": "艺术对时间摧毁力量的抵抗；男女两性精神模式的冲突与互补；家庭记忆中爱意与伤痛的共生。",
        "socratic": "Q1：拉姆齐先生坚持说‘明天去不成灯塔’是因为讲究求真，但为什么拉姆齐太太认为这种‘残忍的事实’毫无必要？\nQ2：十年后他们终于登上了灯塔，这趟迟到的行程还拥有当年的意义吗？",
        "action": "意识流写作练习：选择今天发生的一个微小动作（如喝一杯热咖啡），写下这一瞬间脑海中同时闪过的三个童年回忆或杂乱念头（200字，不加标点过渡）。"
    },

    "达洛维夫人": {
        "title_cn": "达洛维夫人", "title_en": "Mrs. Dalloway",
        "author_cn": "弗吉尼亚·伍尔夫", "author_en": "Virginia Woolf",
        "sub_desc": "单日单城的意识流交响巅峰 · 伦敦盛夏一日的灵魂显微镜",
        "hero_quote": "她觉得自己非常年轻，然而同时又不可思议地衰老。她像一把小刀穿透所有事物，同时又站在外面旁观。",
        "year": "1925 年出版", "genre": "现代主义意识流小说 / 心理双重视角杰作",
        "length": "约 17 万字", "age": "15+ 岁 / 现代经典必读",
        "criteria": "同一时空坐标下正常世俗体面与战争创伤绝望的精神共振",
        "warning": "不要以为全书只是一个英国上流社会贵妇去花店买花、准备今晚晚宴的琐碎流水账。伍尔夫巧妙设计了‘达洛维夫人’与一战弹震症退伍老兵‘塞普蒂默斯’作为彼此互为镜像的灵魂双生子——一个在鲜花派对中妥协维持体面，另一个在精神分裂中跳楼自尽捍卫灵魂纯洁。",
        "highlights": [
            "大本钟沉重报时声（Big Ben）在全书每一个转折处的回荡（客观物理时间与主观心理时间的对抗）。",
            "克拉丽莎与旧情人彼得·沃尔什在客厅久别重逢时内心的惊涛骇浪。",
            "派对高潮处听到陌生疯子自杀消息时，达洛维夫人走进小暗室独处时的神圣共鸣。"
        ],
        "context": "一战结束后的伦敦盛夏，大英帝国在战后余波中强行维持传统贵族社交荣光，然而战争给年轻人留下的精神残疾无处不在。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">克拉丽莎·达洛维</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">上流贵妇 · 晚宴女主人</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">买花 · 妥协 · 维持世俗体面</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">塞普蒂默斯 (Septimus)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">一战弹震症老兵 · 精神分裂</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">跳窗自尽 · 绝不向庸医妥协</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">大本钟报时声 (Big Ben)</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">同一天同一城 · 灵魂的双向镜鉴</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("克拉丽莎", "五十岁优雅的上流社会主妇", "年轻时曾有惊世骇俗的浪漫梦想，最终选择嫁给体面平稳的理查·达洛维，在社交仪式中寻找微小的存在感。"),
            ("塞普蒂默斯", "目睹战友惨死而无法悲伤的年轻老兵", "被冷酷自负的庸医判定为自私装病，为了不被强行关进精神病院毅然纵身跃向铁栅栏。"),
            ("彼得·沃尔什", "一生漂泊无成的旧情人", "神经质地玩弄小折刀，三十年后依然被克拉丽莎的一颦一笑彻底击溃，体现了深情的荒诞与执着。")
        ],
        "perception": "表面是记录一位伦敦贵妇筹备晚宴的一天；深处展示了现代社会中，繁华体面的社交面具与濒临崩溃的个体绝望如何并存于同一片天空之下。",
        "conflict": "维系日常运转的世俗社交义务 vs 窥视虚无深渊时对绝对自由的渴望；冷漠医学权威的规训 vs 创伤心灵的真实呼救。",
        "turning_point": "晚宴上名医布拉德肖带来青年自杀的消息：达洛维夫人离开喧闹的宾客，走进僻静小房间，在一扇窗前看着老人熄灯安歇，忽然完全理解了青年的死——‘死是一种抗争，死是一种交流的企图’。",
        "symbols": [
            ("大本钟的一记记钟声：", "象征不可逆转的客观文明时间，无情地将每一个人的一天切成无法挽回的薄片。"),
            ("彼得手中的小折刀：", "防御性的脆弱男性武器，既是掩饰自卑的道具，也是挑开往事伤疤的工具。")
        ],
        "themes": "生命的脆弱与连接的不可替代；精神创伤在冷漠文明面前的绝望呼喊；在琐碎日常中确认活着的纯粹狂喜。",
        "socratic": "Q1：达洛维夫人从未见过塞普蒂默斯，为什么她在得知他的死讯后，反而感到‘自己的生命得到了救赎’？\nQ2：现代人的社交聚会与朋友圈点赞，有多少成分是为了掩饰内心的空虚与死亡焦虑？",
        "action": "城市漫步练习：独自在熟悉的城市街道漫步三十分钟，不听音乐、不看手机，用全部感官记录身旁擦肩而过的陌生人的神态、衣着与步伐节奏。"
    },

    "草叶集": {
        "title_cn": "草叶集", "title_en": "Leaves of Grass",
        "author_cn": "沃尔特·惠特曼", "author_en": "Walt Whitman",
        "sub_desc": "美国诗歌史上的创世纪独立宣言 · 肉体与灵魂、民主与宇宙的自由放歌",
        "hero_quote": "我赞美我自己，我歌唱我自己；我承担的一切，你也必须承担，因为属于我的每一个原子，同样属于你。",
        "year": "1855 年首版（终生修订）", "genre": "自由体抒情诗集 / 现代诗歌奠基作",
        "length": "四百余首诗篇长卷", "age": "14+ 岁 / 终身必读经典",
        "criteria": "突破古典诗律的自由长句与民主肉体平等赞歌",
        "warning": "切勿带着传统宫廷格律诗的眼光要求《草叶集》押韵对仗。惠特曼开创了咆哮式的自由体（Free Verse），把粗野的伐木工、码头脚夫、黑人奴隶、妓女、机器引擎以及最原始的肉体呼吸感全部迎入诗歌殿堂，给新大陆锻造了第一个自由野性的灵魂嗓音。",
        "highlights": [
            "长诗《自我之歌》（Song of Myself）五十二节气势恢宏的宇宙肉体放声大唱。",
            "哀悼林肯总统遇刺的传世挽歌《啊，船长！我的船长！》与《当紫丁香在庭院前绽放》。",
            "对普通劳动者双手、尘土与野草生命的无上神圣赞美。"
        ],
        "context": "19世纪中叶美国领土西进与工业狂飙，南北分裂与内战创伤中，惠特曼试图用诗歌构建包容万物的民主大同宇宙。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">一叶平民野草 (Grass)</text>
          <text x="140" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">随处生长 · 不择阶级</text>
          <text x="140" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">平等 · 民主 · 大地生机</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">宏大宇宙神性 (Cosmos)</text>
          <text x="540" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">星辰运转 · 肉体与灵魂同一</text>
          <text x="540" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">死亡是更丰盈的生长</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">惠特曼的‘自我之歌’</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">‘我庞大无边，我包容万类’</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#2a9d8f" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("惠特曼自我", "新大陆的游荡吟游诗人", "赤脚踩在泥土上，敞开衬衫，把自己的肉身作为传导天地生机的避雷针，向全人类发出博爱狂喜的呼喊。"),
            ("普通美国民众群像", "木匠、石匠、划船手、母亲与士兵", "每一个在日常岗位上流汗劳作的人，在诗行中都获得了堪比希腊神明的光辉尊严。")
        ],
        "perception": "表面是一部不拘一格的长句诗篇大杂烩；深处是人类对自我肉体存在、对自然万物平等神性最毫无畏惧的自尊礼赞。",
        "conflict": "欧洲旧大陆阶级礼数与萎靡诗律的枷锁 vs 新大陆野性、粗犷、万类霜天竞自由的民主天性。",
        "turning_point": "《自我之歌》第六节孩子问‘什么是草？’：诗人答曰‘草是未曾剪裁的绿旗、上帝的芳香手帕、泥土的头发，是未曾真正死亡的坟墓生机’，确立了全书最高诗学象征。",
        "symbols": [
            ("一叶草 (Grass)：", "随处可见、卑微坚韧、在大地上无差别覆盖一切阶级的民主最高象征。"),
            ("开放的道路 (The Open Road)：", "不断前行、永不停步、向一切流浪者与探索者敞开怀抱的生命旅程。")
        ],
        "themes": "肉体与灵魂的平等神圣性；人人皆享有的民主与博爱；死亡非但不是终结，而是回归大地的更伟大新生。",
        "socratic": "Q1：为什么在惠特曼的笔下，一个劳动者满身大汗的肉体，比贵族喷洒香水的心智更加圣洁？\nQ2：在今天精致利己主义盛行的时代，惠特曼那种‘我包容一切、我拥抱万物’的宏大胸襟，能给我们提供怎样的心智解药？",
        "action": "朗诵练习：挑选《自我之歌》中的任意五个小节，在晨光中站在阳台或窗前，用胸腔最洪亮的声音大声朗诵出来，感受声音震颤身体带来的自由力量。"
    },

    "魔法的颜色": {
        "title_cn": "魔法的颜色", "title_en": "The Colour of Magic",
        "author_cn": "特里·普拉切特", "author_en": "Terry Pratchett",
        "sub_desc": "碟形世界开山之作 · 奇幻文学界最伟大的后现代讽刺神话",
        "hero_quote": "这个世界之所以荒唐，是因为统治世界的法则根本不是严肃的逻辑，而是一群神明在闲极无聊时掷下的骰子。",
        "year": "1983 年出版", "genre": "幽默讽刺奇幻 / 碟形世界开篇长卷",
        "length": "约 16 万字", "age": "12+ 岁 / 全年龄奇幻盛宴",
        "criteria": "解构传统严肃奇幻套路的黑色幽默与后现代讽刺",
        "warning": "不要把《魔法的颜色》当成轻浮的小品笑话书。普拉切特爵士以惊人的智识储备，对托尔金式的严肃史诗奇幻、洛夫克拉夫特克苏鲁神话、现代旅游业、保险金融欺诈与官僚主义进行了入木三分的狂欢式解构，被誉为‘奇幻界的马克·吐温’。",
        "highlights": [
            "碟形世界恢弘壮丽的世界观：一只在星空中游弋的巨龟阿图因，背上驮着四头巨象，象背上顶着扁平世界。",
            "全宇宙最糟糕的怯懦巫师灵思风（只会逃跑且脑子里霸占着一个八级禁咒）。",
            "用具有无数小细腿的多足智梨木箱子（Luggage）守护天真烂漫的第一位游客‘双花’。"
        ],
        "context": "20世纪80年代欧美严肃奇幻泛滥陈腐，普拉切特以解构主义笑声为整个类型文学注入了颠覆性的新活力。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">碟形世界 (Discworld)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">大龟阿图因 · 四大巨象</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">第八种颜色：八元色 (Octarine)</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">双花 (Twoflower · 游客)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">天真富豪 · 随身带照相机</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">多足智梨木行李箱凶悍护主</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">灵思风 (Rincewind · 巫师)</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">逃跑宗师 · 擅长在危机中幸存</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("灵思风", "不学无术的半吊子巫师", "全心全意热爱‘无聊与安全’，却总被命运当成网球拍来回抽打，凭着登峰造极的逃跑本领屡创奇迹。"),
            ("双花", "纯真到近乎智障的阿盖森帝国小职员", "碟形世界上第一个游客，坚信世界充满善意与风景，把火灾当做‘免费焰火表演’，凭纯真逢凶化吉。"),
            ("智梨木行李箱", "长着数百条小短腿的忠犬型储物箱", "刀枪不入、水火不侵，能吞噬一切敌人，成为奇幻文学史上最深入人心的标志性萌宠杀器。")
        ],
        "perception": "表面是一场荒诞不经的公路追逐奇幻冒险闹剧；深处以嬉笑怒骂的英式幽默解构了人类在政治、经济、宗教与传统神话上的全部虚妄。",
        "conflict": "巫师极力求生的逃跑本能 vs 天真游客对‘异国情调冒险’的执着作死求证。",
        "turning_point": "双花在双城港口介绍‘火灾保险’概念：当地酒馆老板误以为‘投保后只要烧掉房子就能发财’，引发了席卷整座城市的疯狂纵火狂潮，全城化为火海，两人开启亡命大逃亡。",
        "symbols": [
            ("八元色 (Octarine)：", "只有巫师和猫才能看见的魔法专属颜色，象征超越世俗肉眼可见光谱之外的灵性想象力。"),
            ("跌落边缘的瀑布：", "碟形世界扁平大地的边缘瀑布，象征探险家直面虚空、探索世界真相的终极悬崖。")
        ],
        "themes": "用笑声解构权威与教条；真正的生存智慧往往隐藏在‘不逞能的自知之明’之中；天真好奇心所拥有的奇迹庇护力。",
        "socratic": "Q1：灵思风明明是个逃跑懦夫，为什么比起那些勇猛好斗的野蛮人英雄，读者更愿意认同他并视他为主角？\nQ2：幽默与讽刺为什么常常是人类在面对荒谬现实时最强大、最具有破坏力的武器？",
        "action": "反转幽默练习：选取你今天遇到的一件倒霉尴尬事，尝试把它改写为一个‘仿佛世界运转法则在故意幽默恶作剧’的段子，感受幽默带来的释怀释然。"
    },

    "文学随笔": {
        "title_cn": "名家文学随笔精选", "title_en": "Selected Literary Essays",
        "author_cn": "世界文学随笔大家", "author_en": "World Essay Masters",
        "sub_desc": "从蒙田到伍尔夫的智识漫游 · 自由心灵在书页间的喃喃私语",
        "hero_quote": "随笔是把灵魂放在桌上，不求证明什么，只求真诚地呈现一段思想的呼吸轨迹。",
        "year": "经典跨世纪集", "genre": "哲理散文 / 文学随笔长卷",
        "length": "精选名篇荟萃", "age": "13+ 岁 / 终身通识必读",
        "criteria": "思想随性漫游中的洞察敏锐度与智识真诚",
        "warning": "不要把随笔误解为‘没有条理的杂碎流水账’。随笔（Essay）源自法语‘尝试（Essai）’，是人类文学中最不装腔作势、最考验作者真实见识与人格坦率的文体。它不提供教科书式的唯一标准答案，而是邀请读者参与一场平等亲密的智识下午茶。",
        "highlights": [
            "蒙田随笔中‘我知道什么？’的伟大怀疑主义自省原点。",
            "弗朗西斯·培根简练如精钢铭文般的世情格言智慧。",
            "查尔斯·兰姆、乔治·奥威尔随笔中底层平民温情与政治虚伪照妖镜。"
        ],
        "context": "从文艺复兴人文主义诞生，到现代主义对内心碎片的审视，随笔始终是思想家安顿自我心灵的自由自留地。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">蒙田哲学原点</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">城堡书房圆塔 · 自我审视</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">‘我自己就是本书的材料’</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">现代批判先声</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">奥威尔 · 伍尔夫 · 兰姆</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">政治话术拆解 · 炉边谈心</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">随笔的心智魅力</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">摆脱八股框架 · 自由思想探险</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("随笔作者群像", "坦荡解剖自我的智者", "不装神弄鬼，敢于公开承认自己的偏见、软弱、健忘与怪癖，在真诚的自剖中赢得读者的深层信任。")
        ],
        "perception": "表面是就生活随处可见之物（睡眠、书籍、书房、散步、习惯）的自由杂谈；深处是人类理智在摆脱了宗教教条和学术条框后的独立自由飞翔。",
        "conflict": "僵化八股教条的思维束缚 vs 自由散漫却直击本质的真知灼见。",
        "turning_point": "随笔从学术论文的严肃中脱胎，开创了‘以第一人称我直接与读者面对面谈话’的全新亲切维度。",
        "symbols": [
            ("书房与书桌：", "隔绝外界权力争斗与世俗喧嚣的思考圣殿，思想在此静静发酵生根。")
        ],
        "themes": "认识你自己；对一切权威教条保持清醒的怀疑；在平凡生活中提炼出哲理甘露。",
        "socratic": "Q1：为什么一篇优秀的随笔，即使作者表达的观点与你完全相左，你依然能读得津津有味心怀敬意？",
        "action": "微型随笔练习：挑选一件你今天经手的不起眼小物件（如一支用尽的圆珠笔），写一段三百字的‘小品沉思’，由物及人，探究它见证的微小心意。"
    },

    "The Ultimate Essays Collection": {
        "title_cn": "欧美名家散文名篇终极典藏", "title_en": "The Ultimate Essays Collection",
        "author_cn": "欧美经典文萃编委会", "author_en": "Ultimate Essay Edition",
        "sub_desc": "英语散文黄金岁月的精神回响 · 语言、理性与修辞的终极盛宴",
        "hero_quote": "读书足以怡情，足以傅彩，足以长才；凡有所学，皆成性格。",
        "year": "经典文库编纂", "genre": "名家散文典藏 / 经典英语修辞范本",
        "length": "跨时代名篇精粹", "age": "13+ 岁 / 终身必读经典",
        "criteria": "语言修辞典范性与思想通识博雅度",
        "warning": "不要只把名篇散文当成背诵好词好句的‘应试素材库’。散文是思想家的肌肉记忆，每一个并列句、转折词、隐喻，都是作者为了精确捕获自己飞扬的思绪而锻造的银箭。学会读散文，就是学会如何严密而优雅地组织自己的心智。",
        "highlights": [
            "培根论读书、论友谊、论逆境的箴言式论说文典范。",
            "爱默生《论自立》（Self-Reliance）点燃一代美国青年独立精神之火的激荡呼喊。",
            "奥威尔《政治与英语语言》对现代谎言话术的解剖手术刀。"
        ],
        "context": "文艺复兴至二十世纪，散文作为通识启蒙公器，塑造了现代西方的言论自由、理性辩论与个人主义精神土壤。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">培根 / 逻辑箴言</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">冷峻精辟 · 实用哲学</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">思维骨架与修辞法则</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">爱默生 / 精神自立</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">超验自立 · 破除从众</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">‘信任你自己’的独立之声</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">现代批判与良知</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">奥威尔对语言假大空的精准击杀</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("西方散文巨擘序列", "培根、爱默生、哈兹利特、兰姆、奥威尔", "各擅胜场，或如冷峻法官，或如旷野先知，或如炉边挚友，共同构筑起英语散文的万神殿。")
        ],
        "perception": "表面是一部跨越数百年的散文经典荟萃；深处是文明如何通过凝练的语言，将人类最宝贵的智识体验一代代淬炼传承。",
        "conflict": "从众平庸随波逐流的惰性 vs 坚持独立自主思考的高贵意志。",
        "turning_point": "爱默生大声宣告：‘盲目模仿即是自杀，盲目顺从即是出卖灵魂’，确立了现代独立人格的尊严宣言。",
        "symbols": [
            ("语言的金字塔：", "散文中精确的论证结构，象征人类理性摆脱野蛮混沌建立秩序的智识之光。")
        ],
        "themes": "精神自立是最高品格；语言的澄澈即思想的澄澈；经典的永恒滋养力量。",
        "socratic": "Q1：爱默生说‘一个人如果想成为真正的人，就绝不能做一个顺民’，如何在社会规则与个人独立自立之间保持健康的平衡？",
        "action": "论说练习：针对当下网络上的某个争议话题，不使用任何脏话、情绪感叹号与人身攻击标签，写一篇三百字逻辑严密、论点鲜明的议论小短文。"
    },

    "暮光之城I- 暮色": {
        "title_cn": "暮光之城Ⅰ · 暮色", "title_en": "Twilight",
        "author_cn": "斯蒂芬妮·梅尔", "author_en": "Stephenie Meyer",
        "sub_desc": "全球青少年的现象级奇幻纯爱神话 · 致命危险与深情自抑的冰冷诱惑",
        "hero_quote": "狮子无可救药地爱上了羔羊；一只愚蠢的羔羊，一只变态自虐的狮子。",
        "year": "2005 年出版", "genre": "奇幻浪漫小说 / 吸血鬼新神话",
        "length": "约 25 万字", "age": "12+ 岁 / 青少年风靡经典",
        "criteria": "极端本能压抑与青春情感投射的心理张力",
        "warning": "不要把《暮光之城》当成毫无思想的爆米花偶像书。梅尔之所以能掀起全球青春狂潮，是因为她极其精准地抓住了青春期少男少女对‘被彻底接纳、被唯一珍视’的极致心理渴望。爱德华忍受嗜血本能对贝拉的自我克制，构成了禁忌之恋最强烈的心理悬念。",
        "highlights": [
            "福克斯阴雨连绵、终年不见阳光的冷杉森林氛围营造。",
            "生物学实验室里风吹动发丝引发的嗜血杀机与瞬间克制。",
            "卡伦家族在雷电风暴中打棒球的超自然惊艳场景。"
        ],
        "context": "21世纪初互联网与智能手机尚未完全绑架青少年的时代，传统哥特吸血鬼传说向青春成长罗曼史的现代化转型。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">爱德华·卡伦 (Edward)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">百年吸血鬼 · 冰冷大理石</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">克制嗜血本能 · 守护真爱</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">贝拉·斯旺 (Bella)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">平凡转校生 · 敏感自卑</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">无畏走向危险 · 渴望永恒相守</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">福克斯阴雨小镇 (Forks)</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">茂密森林 · 禁忌与深情的试炼场</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("贝拉", "看似笨拙平凡实则坚韧决绝的少女", "抗拒虚荣的社交圈，敏锐察觉爱德华的异类身份，敢于直视最致命的危险。"),
            ("爱德华", "兼具优雅绅士风度与危险食肉野性的异类", "把自己的嗜血欲望视作地狱诅咒，宁愿承受万千痛苦也绝不伤害贝拉分毫。"),
            ("卡伦素食家族", "恪守道德戒律的异类文明标本", "拒绝吸食人血，选择以兽血维生融入人类社会，展现了理智战胜残酷天性的力量。")
        ],
        "perception": "表面是一部跨越物种的浪漫魔幻校园恋情；深处展示了青年时期个体如何战胜自我怀疑，在充满危险与不确定的世界中寻觅唯一的灵魂归属。",
        "conflict": "吸血鬼对鲜血不可抗拒的生理杀戮本能 vs 出于真爱的崇高自控意志。",
        "turning_point": "森林草地上爱德华在阳光下展露真身：皮肤在光线中如同无数细碎钻石般闪耀，贝拉没有被怪物的恐怖吓退，而是轻抚大理石般冰冷的脸庞，完成了生死信任绑定。",
        "symbols": [
            ("封面双手捧着的红苹果：", "象征伊甸园禁忌的果实，充满诱惑却暗藏危险，也是做出命运抉择的自主隐喻。"),
            ("钻石般的冷光皮肤：", "美丽与危险并存的至高象征，致命之物却拥有世界上最眩目的光泽。")
        ],
        "themes": "自控是爱最深沉的表现；接纳彼此的异类与不完美；面对危险时超乎寻常的信任与勇气。",
        "socratic": "Q1：为什么爱德华对贝拉鲜血的极度渴望，反而让他的每一次拥抱显得如此动人神圣？\nQ2：青春期读者在贝拉身上找到了哪些属于自己‘敏感、自卑却渴望被看见’的心理共鸣？",
        "action": "情感自律反思：在面对某种极其强烈的诱惑或冲动时，体会爱德华式的‘为了所爱之人的长久福祉而主动选择克制’，感受自控带来的尊严力量。"
    },

    "暮光之城II-新月": {
        "title_cn": "暮光之城Ⅱ · 新月", "title_en": "New Moon",
        "author_cn": "斯蒂芬妮·梅尔", "author_en": "Stephenie Meyer",
        "sub_desc": "失去、心碎与治愈的暗夜长歌 · 狼人守护与意大利古老王座",
        "hero_quote": "没有你的日子，不仅是黑暗；我的天空不仅失去了太阳，还失去了所有闪耀的星辰。",
        "year": "2006 年出版", "genre": "奇幻成长小说 / 失恋与创伤疗愈",
        "length": "约 26 万字", "age": "12+ 岁 / 青少年必读",
        "criteria": "失恋绝望下的自我毁灭倾向与友情救赎",
        "warning": "不要把《新月》仅仅看作爱德华离开后贝拉与雅各布的三角备胎戏。全书极其精准地还原了<strong>遭遇初恋毁灭性断崖弃离后，年轻人的重度抑郁症体验</strong>——胸口开着无法愈合的大洞、四个月毫无知觉的空白日记，展现了极高的心理真实度。",
        "highlights": [
            "全书最具形式感的一幕：十月、十一月、十二月、一月连续四张完全空白的日记页码。",
            "雅各布与拉普什保留地狼人族群的兄弟情与温暖阳光守护。",
            "意大利沃尔图拉古城钟楼前，贝拉在万人狂欢红袍中奋力飞奔拥抱即将赴死的爱德华。"
        ],
        "context": "年轻人在成长过程中第一次遭遇毁灭性情感失落时的自我重构与生命成长。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#131619" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">爱德华的离去</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">以为离开是对贝拉最好的保护</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">陷入误会赴意大利沃尔泰拉求死</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">雅各布·奎鲁特 (Jacob)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">狼人血脉觉醒 · 滚烫阳光体温</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">修摩托车 · 陪伴拯救抑郁深渊</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">贝拉的心碎空洞</text>
          <text x="340" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">自虐式寻求幻觉 · 悬崖跳水顿悟</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#131619" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("贝拉", "经历灵魂碎裂的坚忍少女", "在胸口的大洞中苦撑，通过悬崖跳水寻找求生的意志，最终飞赴意大利挽救爱德华生命。"),
            ("雅各布", "如阳光般热烈的狼人少年", "体温高达42度，陪伴贝拉修理摩托车，充当无私的精神创可贴，虽遭拒绝依然默默护航。"),
            ("爱德华", "因傲慢自以为是而酿成大祸的痛苦情人", "自以为离开可以让贝拉重获平凡幸福，却不知遗弃给对方带来了怎样的灭顶之灾。")
        ],
        "perception": "表面是一部曲折跌宕的魔幻离合传奇；深处写透了‘以爱的名义单方面做出的遗弃，如何给所爱之人造成最致命的伤害’。",
        "conflict": "单向的家长式保护意志 vs 渴望共同承担风雨的平等爱意；温暖阳光的疗愈陪伴 vs 铭刻骨血的致命执念。",
        "turning_point": "沃尔泰拉钟楼正午十二点钟声响起：爱德华正欲脱去外衣走入阳光自曝引死，贝拉冲破广场拥挤的人潮扑进他怀中，死亡危机瞬间化作劫后重生的狂喜。",
        "symbols": [
            ("新月 (New Moon)：", "没有月光的暗夜，象征生命中最深沉的绝望与虚无期。"),
            ("胸口的巨大空洞：", "失恋与离别带来的生理般钝痛，形象揭示了心碎对人体的真实摧残。")
        ],
        "themes": "面对分离的疗愈与自我重建；真正的爱需要坦诚沟通而非自以为是的放手；友情的崇高修复力量。",
        "socratic": "Q1：爱德华以为离开贝拉是对她好，这种‘为了你好而擅自替你做决定’的做法在生活中有多少人还在犯？\nQ2：雅各布的温暖与爱德华的冷酷，究竟哪一种感情更适合支撑漫长的一生？",
        "action": "心理创伤自我疏导：写下一个你曾经遭遇过的‘被忽视或被抛弃’的难过瞬间，告诉自己：对方的离开是他自身的局限，绝不意味着你丧失了被爱的价值。"
    },

    "暮光之城III-月食": {
        "title_cn": "暮光之城Ⅲ · 月食", "title_en": "Eclipse",
        "author_cn": "斯蒂芬妮·梅尔", "author_en": "Stephenie Meyer",
        "sub_desc": "宿敌联盟与决断时刻 · 暴风雨前夕的阵营抉择与新生军死战",
        "hero_quote": "云彩遮住了太阳，但太阳依然在那里；然而对我而言，你才是我的太阳。",
        "year": "2007 年出版", "genre": "奇幻战争 / 爱情抉择与阵营同盟",
        "length": "约 27 万字", "age": "12+ 岁 / 青年经典",
        "criteria": "历史世仇面前为了共同正义的理性妥协与阵营和解",
        "warning": "不要只看成贝拉在吸血鬼与狼人之间的纠结摇摆。在维多利亚复仇者率领暴虐的西雅图‘新生吸血鬼大军’压境的生死关头，数百年来势同水火的吸血鬼卡伦家族与印第安狼人奎鲁特部落，放下了刻入骨髓的种族世仇并肩作战，展示了极具格局的政治妥协智慧。",
        "highlights": [
            "卡伦家族在林间空地指导狼人如何合力猎杀新生吸血鬼的绝妙战术演练。",
            "雪山帐篷里爱德华与雅各布在冰雪严寒中坦诚心迹的情敌和解。",
            "西雅图新生军登陆与森林血战歼灭战的高燃终局。"
        ],
        "context": "青年即将高中毕业踏入成年门槛，必须在自身的人性身份与非人永生之间做出不可逆的终极决定。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">卡伦吸血鬼家族</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">防守阵营 · 优雅战术</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">爱德华的成熟包容</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">奎鲁特狼人族群</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">荒野守护者 · 狂暴力量</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">雅各布的英勇出征</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">宿怨冰释 · 共同御敌</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">合力粉碎西雅图新生军侵略</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("贝拉", "面临终极成人选择的守望者", "明晰自己的心意，即便对雅各布怀有温暖的友情与感动，依然诚实坚决地选择爱德华。"),
            ("爱德华", "学会放手与信任的情人", "克服了狭隘的嫉妒心，允许雅各布在雪山用体温拯救冻僵的贝拉，展现出真正的成年人胸襟。"),
            ("维多利亚", "冷酷狡诈的复仇女首领", "为替詹姆斯报仇建立嗜血的新生儿军团，最终在雪峰决战中被爱德华彻底击毁。")
        ],
        "perception": "表面是一场惊险激烈的阵营联合抗敌魔幻战争；深处探讨了‘人如何为自己的不可逆人生抉择承担全部代价’。",
        "conflict": "放下历史宿仇实现合作 vs 顽固仇恨导致的全盘覆灭；保留凡人人性 vs 选择永生蜕变的身份认同撕扯。",
        "turning_point": "雪山营地风暴夜：贝拉因高山严寒濒临冻死，爱德华冰冷的体温无能为力，主动唤来滚烫的雅各布进入睡袋抱住贝拉取暖，完成了情敌之间最震撼人心的信任和解。",
        "symbols": [
            ("月食 (Eclipse)：", "象征月亮遮蔽了太阳的光辉，但太阳的炽热从未泯灭。"),
            ("折断的红色缎带：", "封面上被撕裂的红丝带，象征贝拉与平静凡人生活的彻底割舍。")
        ],
        "themes": "成熟意味着敢于做不可兼得的取舍；面对共同危机时的跨阵营协作；真正的爱包含对对方选择的敬意。",
        "socratic": "Q1：雅各布明知贝拉最终会选择爱德华，为什么依然选择为保护她拼死与新生军血战？\nQ2：爱德华允许雅各布给贝拉取暖，这需要克服多大的本能抗拒？这体现了怎样成熟的爱情观？",
        "action": "沟通妥协训练：在与某个有立场偏见的同事或同学合作时，尝试聚焦双方‘共同的目标’，将历史恩怨暂时归零封存。"
    },

    "暮光之城IV-破晓": {
        "title_cn": "暮光之城Ⅳ · 破晓", "title_en": "Breaking Dawn",
        "author_cn": "斯蒂芬妮·梅尔", "author_en": "Stephenie Meyer",
        "sub_desc": "全系列宏大终章 · 母亲的坚忍抗争、蜕变新生与沃尔图里终局对峙",
        "hero_quote": "唯有在成为母亲的那一刻，我才真正懂得了什么叫无坚不摧。",
        "year": "2008 年出版", "genre": "史诗魔幻奇幻 / 家族抗争终局",
        "length": "约 35 万字", "age": "13+ 岁 / 终身必读完结卷",
        "criteria": "母性牺牲本能对死亡恐惧的彻底战胜",
        "warning": "不要把《破晓》只看作一场生化危机式的‘吸血鬼婴儿争夺战’。梅尔在后半卷构建了一场世界奇幻文学罕见的<strong>‘不战而屈人之兵’的宏大外交对抗</strong>——卡伦家族没有动用屠杀，而是遍访全球吸血鬼盟友作为‘证人’，在雪原上凭借道德证言与冷静克制，迫使不可一世的意大利教廷独裁者退兵。",
        "highlights": [
            "贝拉冒着脊椎折断与肉体枯竭的生命危险，坚决捍卫胎儿降生的惊心动魄产房奇迹。",
            "贝拉死而复生蜕变为新生吸血鬼，觉醒出能守护全体族人的‘精神意念盾牌’天赋。",
            "全球各异种族吸血鬼盟友汇聚福克斯雪原，与沃尔图里皇室近百名黑袍卫队的世纪大对峙。"
        ],
        "context": "从少女到母亲、从依赖他人保护到成为庇护全族的至强盾牌，女性生命意志的全面觉醒与升华。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">贝拉与蕾妮斯梅</text>
          <text x="140" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">母性奇迹 · 意念护盾觉醒</text>
          <text x="140" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">从弱小受护者到家族保护神</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#131619" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">沃尔图里皇室 (Volturi)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">阿罗 · 绝对权力裁决者</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">企图以借口铲除异己巩固统治</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">雪原全球盟友大集结</text>
          <text x="340" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">以真理为证 · 和平破局消除浩劫</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#2a9d8f" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#131619" stroke-width="2" />
        </svg>""",
        "characters": [
            ("贝拉", "全系核心保护者", "成为新生吸血鬼后展现出不可思议的超强自控力，其护盾能力抵挡了阿罗与简的所有精神攻击。"),
            ("爱德华", "终于放下百年焦虑的丈夫与父亲", "在贝拉的护盾下第一次听见女儿纯洁的心声，获得了前所未有的安详与平静。"),
            ("阿罗 (Aro)", "醉心于收集异能天才的罗马教皇式霸主", "在目睹了贝拉不可撼动的护盾防御与亚马逊证人证据后，衡量利害从容撤兵，展现了老牌政客的精明。")
        ],
        "perception": "表面是一部带超自然激战色彩的奇幻大团圆终章；深处展现了一个女性在历经爱、生育与死亡淬炼后，所迸发出的庇护整个社群的神圣母性光辉。",
        "conflict": "教廷霸权对自身统治权威的绝对维护 vs 自由家族追求生存真相的正义抵抗；屠杀冲动 vs 维护和平的智慧克制。",
        "turning_point": "爱丽丝带回亚马逊丛林的另一位半人半吸血鬼纳乌尔作为活证人：直接戳穿了阿罗宣称‘半吸血鬼是不死害虫’的莫须有罪名，在全世界证人面前彻底剥夺了教廷开战的合法性。",
        "symbols": [
            ("白雪与晨曦（破晓）：", "象征穿越漫长血腥暗夜后，生命终于迎来属于自己的黎明与永恒安宁。"),
            ("国际象棋白王后：", "封面上进击的白棋王后，象征贝拉从最初任人摆布的兵卒，最终蜕变为横扫棋盘的至强庇护核心。")
        ],
        "themes": "母爱具有超越死亡的至高神性；真正的强大源自内心守护所爱之人的愿望；智慧与真相能够战胜强权武力。",
        "socratic": "Q1：如果贝拉没有觉醒出足以抵挡教廷攻击的无敌护盾，沃尔图里还会平静地选择撤兵吗？这揭示了和平与实力之间怎样的关系？\nQ2：四部曲走完，贝拉从一个事事需要被保护的自卑女孩，到成为保护所有人的英雄母亲，这种女性成长轨迹具有怎样的普遍启示？",
        "action": "内心护盾冥想：闭上眼睛三分钟，想象你的心智被一层金色的‘意念护盾’温柔包裹，外界一切尖酸苛责与负面情绪击打在护盾上皆如细雨散落，感受内心坚不可摧的安宁。"
    }
}

def main():
    print("=== 开始批量构建【批次 D：哲学、意识流与现当代奇幻名著】 ===")
    success = 0
    total = len(BOOKS_D)

    for book_name, info in BOOKS_D.items():
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

    print(f"=== 批次 D 顺利完工: {success}/{total} 部作品通过校验并落盘 ===")

if __name__ == "__main__":
    main()
