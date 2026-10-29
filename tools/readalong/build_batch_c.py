#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch C: American Classics, Growth & Mind Quest (14 books)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT
from build_batch_a import render_book_guide

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

BOOKS_C = {
    "了不起的盖茨比": {
        "title_cn": "了不起的盖茨比", "title_en": "The Great Gatsby",
        "author_cn": "F·S·菲茨杰拉德", "author_en": "F. Scott Fitzgerald",
        "sub_desc": "爵士乐时代的绚烂挽歌 · 绿色微光下的美国梦破碎史诗",
        "hero_quote": "于是我们奋力前行，逆水行舟，浪潮却一刻不停地将我们推回过去。",
        "year": "1925 年出版", "genre": "现代抒情小说 / 爵士时代史诗",
        "length": "约 18 万字", "age": "14+ 岁 / 青年与成人必读",
        "criteria": "物质丰裕下的精神荒芜与理想幻灭",
        "warning": "不要把盖茨比看作俗气的暴发户。盖茨比之所以‘了不起’，是因为在一群冷酷自私、‘撞碎了别人的生活就躲回金钱城堡里’的老钱贵胄中，唯有他保留了献祭毕生所有、追求纯洁理想与美好幻觉的神圣能力。",
        "highlights": [
            "码头尽头对岸黛西家那一抹闪烁的绿色微光（The Green Light）。",
            "灰烬谷上空埃克尔堡大夫那一双冷漠注视的巨大眼镜（天意隐喻）。",
            "门庭若市的奢华夏夜派对与死后无人出席的孤寂葬礼对比。"
        ],
        "context": "一战后美国二十世纪二十年代‘爵士时代（Jazz Age）’，禁酒令、黑帮洗钱与华尔街投机狂潮并起，传统道德信仰全面崩溃。",
        "svg": """<svg viewBox="0 0 680 260" xmlns="http://www.w3.org/2000/svg">
          <rect x="40" y="30" width="180" height="90" rx="8" fill="#1d3557" />
          <text x="130" y="60" fill="#fff" font-weight="700" text-anchor="middle">西卵 (West Egg)</text>
          <text x="130" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">暴发新钱 · 盖茨比奢靡庄园</text>
          <text x="130" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">痴情坚守 · 纯洁理想主义</text>
          <rect x="460" y="30" width="180" height="90" rx="8" fill="#242930" />
          <text x="550" y="60" fill="#fff" font-weight="700" text-anchor="middle">东卵 (East Egg)</text>
          <text x="550" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">世代老钱 · 汤姆与黛西</text>
          <text x="550" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">冷酷特权 · 玩弄他人后隐身</text>
          <rect x="250" y="150" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">绿色微光 (The Green Light)</text>
          <text x="340" y="198" fill="#e5e8eb" font-size="11" text-anchor="middle">隔海遥望 · 永不熄灭的未来希望</text>
          <line x1="220" y1="75" x2="460" y2="75" stroke="#2a9d8f" stroke-width="2.5" />
        </svg>""",
        "characters": [
            ("杰·盖茨比", "被爱情梦幻神圣化的孤胆英雄", "从贫苦农家子弟蜕变为挥金如土的神秘大亨，死于为心爱女人顶包撞车罪责，至死不悟。"),
            ("黛西·布坎南", "声音里‘装满金钱’的虚荣名媛", "美丽而苍白，缺乏承担道德责任的勇气，在撞死情妇后平静地跟着丈夫出走逃避。"),
            ("尼克·卡拉威", "冷静克制的道德见证人与叙述者", "看穿了东部上流社会的虚荣残忍，在埋葬盖茨比后决绝地离开纽约返回淳朴中西部。")
        ],
        "perception": "表面是一部爵士时代的奢华情杀案；深处宣告了‘美国梦（通过个人奋斗获取财富与真爱）’在残酷阶级固化面前的彻底破产。",
        "conflict": "不顾一切重塑过去的执着理想 vs 现实阶级血统的不可逾越与冷漠背叛。",
        "turning_point": "纽约广场饭店套房摊牌：汤姆当众撕开盖茨比靠私酒和假债券发财的底细，黛西眼神中流露出的惊恐与后退彻底宣告了梦想破灭。",
        "symbols": [
            ("绿光 (The Green Light)：", "码头尽头的幽微光斑，象征人类对未竟梦想与美好未来的永恒渴求。"),
            ("灰烬谷 (Valley of Ashes)：", "纽约与富人区之间的垃圾荒漠，象征狂热财富繁荣背后被牺牲的底层生灵与精神废墟。")
        ],
        "themes": "金钱无法赎买过去；纯真理想在世俗自私面前的悲壮牺牲；历史洪流中人类逆水行舟的宿命姿态。",
        "socratic": "Q1：盖茨比爱的究竟是黛西这个人，还是当年那个穷小子脑海中‘拥有黛西就拥有了一切美好’的自我神话？\nQ2：为什么尼克最终对盖茨比喊出：‘他们那帮人加起来，都比不上你一个！’？",
        "action": "人生执念检查：思考你心中是否有某个‘一定要实现的证明自我梦想’，评估这个梦想是在滋养你，还是已经把你变成了它的人质？"
    },

    "麦田里的守望者": {
        "title_cn": "麦田里的守望者", "title_en": "The Catcher in the Rye",
        "author_cn": "J·D·塞林格", "author_en": "J. D. Salinger",
        "sub_desc": "全球青少年的精神成年礼 · 痛击虚伪成人世界的纯真保卫战",
        "hero_quote": "我只想做个麦田里的守望者，守在悬崖边，抓住每一个快要掉下悬崖的孩子。",
        "year": "1951 年出版", "genre": "成长小说 / 现代主义意识流",
        "length": "约 15 万字", "age": "13+ 岁 / 青少年终身必读",
        "criteria": "青少年面对成人社会虚伪假模的创伤自愈",
        "warning": "切勿以为霍尔顿只是一个满口粗话、抽烟逃学的‘叛逆坏学生’。他的满腹牢骚，是一个内心极其纯洁敏锐的孩子，在目睹了名校社会的势利、功利、性欺诈与冷漠虚伪后，发出的一声声痛苦的灵魂干呕。",
        "highlights": [
            "霍尔顿在纽约街头游荡三天三夜的内心独白流淌。",
            "对‘麦田守望者’这一崇高纯真使命的心灵自白。",
            "雨中注视妹妹菲比在中央公园旋转木马上抓金环的灵魂释怀与自愈。"
        ],
        "context": "二战后美国中产阶级消费主义与郊区体面生活泛滥，虚伪的礼仪与功利主义扼杀年轻一代的真诚本真。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#131619" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">虚伪的成人世界 (Phonies)</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">潘西名校 · 伪善社交</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">功利算计 · 假模假样</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">纯真守望之地 (Rye)</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">妹妹菲比 · 亡弟阿利</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">旋转木马 · 悬崖守护者</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">霍尔顿 (Holden)</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">反戴红色猎人帽 · 游荡与顿悟</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#131619" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("霍尔顿·考尔菲德", "十六岁的精神流浪儿", "满眼皆是‘假模假样（Phony）’，表面厌世愤懑，内心深怀对弱小者与纯真最温柔的关切。"),
            ("菲比 (Phoebe)", "十岁聪慧灵动的妹妹", "全书唯一真正倾听、理解并无条件信任霍尔顿的人，她的拥抱阻止了哥哥逃往西部荒原。"),
            ("阿利 (Allie)", "患白血病早逝的弟弟", "棒球手套上写满绿墨水诗篇，象征永不褪色、未曾受世俗沾染的纯洁之灵。")
        ],
        "perception": "表面是一个被第四所私立中学开除的纨绔少年游荡记；深处是一部现代人在精神青春期直面社会虚伪时的创伤自愈长卷。",
        "conflict": "未经雕琢的纯洁同理心 vs 功利冷漠的成人游戏规则；渴望守护他人 vs 自身的无力自拔。",
        "turning_point": "中央公园旋转木马场景：大雨倾盆而下，霍尔顿淋得透湿，看着坐在木马上伸手去抓金环的菲比，内心涌出无边平静与幸福。",
        "symbols": [
            ("红色猎人帽：", "霍尔顿自我保护与独特的精神战袍，反戴时象征拒绝顺从平庸的大众审美。"),
            ("中央公园池塘里的鸭子：", "‘冬天湖面结冰，鸭子都飞到哪里去了？’象征无助边缘个体在冷酷严冬中寻找庇护的脆弱发问。")
        ],
        "themes": "成长的阵痛不是妥协，而是认清虚伪后依然保有善良；守护儿童免受成人世俗毒害的纯洁意志；与自我和解的必要性。",
        "socratic": "Q1：为什么霍尔顿讨厌所有人，却在故事结尾说‘我甚至有点想念他们了’？\nQ2：当孩子伸手去抓旋转木马上的金环可能会摔倒时，我们究竟该拉住他们，还是让他们冒着摔倒的风险去探索？",
        "action": "观察记录：寻找今天你遇到的某件让你感到‘虚伪应付’的小事，尝试不用刻薄嘲讽，而是用慈悲理解背后的凡俗无奈。"
    },

    "To Kill A Mockingbird": {
        "title_cn": "杀死一只知更鸟", "title_en": "To Kill a Mockingbird",
        "author_cn": "哈珀·李", "author_en": "Harper Lee",
        "sub_desc": "普利策传世丰碑 · 良知、正义与偏见深渊中的温柔力量",
        "hero_quote": "知更鸟除了唱歌给我们听，什么坏事也不做；它们不吃人们园子里的花果，只是用尽全力为我们歌唱。所以，杀死一只知更鸟就是一桩罪过。",
        "year": "1960 年出版", "genre": "成长文学 / 法庭辩论小说 / 人权史诗",
        "length": "约 22 万字", "age": "11+ 岁 / 终身必读道德经典",
        "criteria": "种族与阶级偏见面前守护良知的勇气",
        "warning": "不要把这本书仅仅当成一部黑人平权题材的法庭胜诉爽文。在三十年代的美国南部小镇梅科姆，汤姆·鲁宾逊即便有铁一般的无罪证据，依然被清一色的白人陪审团判处有罪。阿蒂克斯明知不可为而为之的辩护，展示了人类道德勇气的至高边界。",
        "highlights": [
            "阿蒂克斯坐在看守所门前独自面对持枪动私刑暴民的平静从容。",
            "法庭审理结束阿蒂克斯离开时，二楼黑人旁听席全体起立致敬。",
            "神秘邻居‘怪人’拉德利暗中守护孩子并在万圣节雨夜殊死相救。"
        ],
        "context": "大萧条时期的美国南方小镇，种族隔离与白人贫困群体（红脖子）对有色人种的根深蒂固仇恨。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">阿蒂克斯·芬奇</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">模范父亲 · 法律良知守卫者</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">明知必败仍全力以赴辩护</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">梅科姆小镇偏见深渊</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">尤厄尔家族诬告 · 白人陪审团</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">无辜知更鸟汤姆被射杀</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">斯考特 / 杰姆 / 怪人布</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">儿童视角 · 穿透偏见看清仁慈</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("阿蒂克斯", "全美最受尊敬的平民父亲与律师", "教会孩子‘穿上别人的鞋子走一走才能理解对方’，用平静理性击退仇恨暴力的典范。"),
            ("斯考特 (Scout)", "六岁假小子第一人称叙述者", "用未经偏见污染的清澈童眼，记录下成人的虚伪、正义的代价与人性的幽暗。"),
            ("怪人布 (Boo Radley)", "从未踏出门槛的隐世邻居", "被小镇流言塑造成可怕食人魔，却在暗中在树洞给孩子们留小礼物，最后舍身刺死恶霸救下孩子。")
        ],
        "perception": "表面是一桩大萧条时期的黑人强奸冤案审理纪实；深处展现了一个文明社会中，良知如何在世代偏见的坚冰中顽强扎根生长。",
        "conflict": "法律的程序公正与普遍平等人道原则 vs 根深蒂固的种族仇恨与阶级傲慢。",
        "turning_point": "法庭宣判‘有罪’的那一刻：杰姆泪流满面无法接受现实，而阿蒂克斯平静收拾公文包，黑人群体默默肃立注视他走过通道。",
        "symbols": [
            ("知更鸟 (Mockingbird)：", "象征世界上那些善良、无辜、从不伤害他人、只为世界带来歌声与温暖的弱小生命（汤姆与怪人布皆是）。"),
            ("疯狗事件：", "阿蒂克斯一枪击毙街头狂犬，证明‘真正的勇敢不是手里拿着枪，而是当你还没开始就知道自己会输，却依然去做’。")
        ],
        "themes": "同理心是战胜偏见的唯一钥匙；勇敢的真正定义；在黑暗现实中为孩子树立人格灯塔的父爱典范。",
        "socratic": "Q1：警长最后为何决定隐瞒怪人布刺死尤厄尔的真相，对外宣称恶霸是‘自己摔在刀上’？这违背法治吗？\nQ2：当大多数人都站在狂热的不义一边时，一个孤独清醒的人该如何面对群体的孤立？",
        "action": "共情换位训练：“穿上他的鞋子”——针对你身边某个常常表现怪僻、不合群的人，试着从他的童年家庭背景推导他为何会筑起坚硬防线。"
    },

    "飘": {
        "title_cn": "飘", "title_en": "Gone with the Wind",
        "author_cn": "玛格丽特·米切尔", "author_en": "Margaret Mitchell",
        "sub_desc": "南北战争烽火下的乱世情仇 · 顽强生命力的绝美赞歌",
        "hero_quote": "明天又是新的一天了！(Tomorrow is another day!)",
        "year": "1936 年出版", "genre": "历史巨著 / 浪漫主义传奇",
        "length": "约 100 万字", "age": "13+ 岁 / 终身必读经典",
        "criteria": "极端生存危机中女性意志的野蛮绽放",
        "warning": "不要将斯嘉丽仅仅当作任性虚荣的南国佳人。当战火将佐治亚庄园烧成瓦砾、绅士名媛在废墟中自怜等死时，只有斯嘉丽抓起一把红土，在黄昏中发下重誓：‘就算去偷、去抢、去杀人，我也绝不再挨饿！’她代表着不可战胜的原生生命韧性。",
        "highlights": [
            "亚特兰大沦陷前夕的大撤退与十二橡树庄园的化为灰烬。",
            "瑞德·巴特勒冷峻世俗外表下的无限深情与终局心碎离去。",
            "梅兰妮圣洁宽厚的包容之爱对斯嘉丽狂烈性格的精神平衡。"
        ],
        "context": "美国南北战争与战后重建时期，南方种植园奴隶制封建贵族文明在北方工业大军的烈火中彻底‘随风而逝’。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">斯嘉丽 (Scarlett)</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">塔拉红土之女 · 坚韧野蛮</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">誓死守卫土地与生存</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">瑞德·巴特勒 (Rhett)</text>
          <text x="540" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">反传统走私商 · 洞悉一切</text>
          <text x="540" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">至深挚爱终在耗竭中离去</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">梅兰妮 / 艾希礼</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">博爱圣洁妻子 · 沉湎旧梦弱者</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#8c2d19" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("斯嘉丽·奥哈拉", "具有野草般生机的大女主", "自私、爱慕虚荣，却拥有在废墟中徒手开荒、枪毙劫匪、开办木材厂守护家园的无畏勇气。"),
            ("瑞德·巴特勒", "深情而叛逆的硬汉绅士", "看穿了南方假装体面的战争狂热，最懂斯嘉丽的灵魂伴侣，在付出一切后留下了‘我根本不在乎’的决绝转身。"),
            ("梅兰妮", "具有无上美德的圣洁母亲", "柔弱病躯中怀抱纯真信仰，始终全心全意保护信任斯嘉丽，是斯嘉丽一生最重要的精神铠甲。")
        ],
        "perception": "表面是一场乱世豪门的三角四角婚恋传奇；深处写透了一个旧时代的彻底破灭，以及新生命如何在苦难中野蛮新生。",
        "conflict": "旧贵族虚幻的诗意荣誉 vs 新现实严酷的生存斗争；得不到的情感执念 vs 守在身边的真爱被挥霍。",
        "turning_point": "梅兰妮难产去世与艾希礼的崩溃：那一刻斯嘉丽如梦初醒，发现艾希礼不过是个沉湎在过去画卷里的无能文弱书生，而自己一生真正深爱的是瑞德。",
        "symbols": [
            ("塔拉庄园的红土 (Tara)：", "生命最深沉厚重的滋养源泉，每当斯嘉丽陷入绝境，抚摸红土总能赋予她战胜一切苦难的野蛮力气。"),
            ("绿天鹅绒窗帘礼服：", "在大撤退废墟中，斯嘉丽拆下母亲留下的旧窗帘缝制华服奔赴亚特兰大周旋，象征绝境中尊严与野心的高傲抬头。")
        ],
        "themes": "面对苦难的顽强生命意志；旧时代随风而逝的不可逆转性；学会珍惜近在眼前的真情。",
        "socratic": "Q1：斯嘉丽身上既有自私刻薄又有英勇牺牲，为什么这种充满道德瑕疵的复杂人性反而让全球读者疯狂热爱？\nQ2：‘明天又是新的一天’究竟是一种积极的自愈韧性，还是一种拒绝反思的鸵鸟拖延？",
        "action": "抗挫力心法：在面对看似不可收拾的生活困局时，对自己说出斯嘉丽的名言，将焦虑推迟到明天，先睡一个好觉恢复物理精力。"
    },

    "月亮与六便士": {
        "title_cn": "月亮与六便士", "title_en": "The Moon and Sixpence",
        "author_cn": "W·萨默塞特·毛姆", "author_en": "W. Somerset Maugham",
        "sub_desc": "高更生平为蓝本的传世杰作 · 满地都是六便士，他却抬头看见了月亮",
        "hero_quote": "我必须画画，我身不由己；一个人掉进水里，他游泳游得好不好并不重要，要紧的是他必须挣扎出来，否则就会被淹死。",
        "year": "1919 年出版", "genre": "传记体哲理小说 / 艺术反思小说",
        "length": "约 16 万字", "age": "14+ 岁 / 青年必读精神经典",
        "criteria": "世俗功利规训与纯粹艺术召唤的绝对决裂",
        "warning": "不要把斯特里克兰德洗白为‘温馨温情的艺术大师’。毛姆极其冷酷地记录了他的残忍：抛妻弃子毫无歉意、夺走恩人施特洛夫的妻子逼得对方自杀、对世俗道德充满赤裸裸的鄙视。但他身上展现了一种被‘创作魔鬼附体’的纯粹神圣，令人在道德批判之余不得不战栗肃穆。",
        "highlights": [
            "四十岁证券经纪人一夜蒸发，只留下一封毫无感情的绝交弃家信。",
            "巴黎阁楼病榻上对平庸画家的残酷嘲讽与夺妻悲剧。",
            "塔希提岛大溪地原始丛林中的涅槃狂热，临终前命妻子烧毁毕生绝世壁画神作。"
        ],
        "context": "二十世纪初伦敦资产阶级中产阶层平庸窒息的生活规训，现代人被体面生活套牢丧失了狂热的精神追求。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">伦敦六便士 (Sixpence)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">证券经纪人 · 舒适中产家庭</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">虚伪体面 · 毫无生气的牢笼</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">塔希提月亮 (The Moon)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">原始雨林 · 纯粹灵魂狂喜</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">麻风眼瞎 · 绝笔烧毁自决</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#242930" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">斯特里克兰德 (Strickland)</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">艺术恶魔附体 · 决绝奔赴</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("查尔斯·斯特里克兰德", "着魔的现代高更化身", "弃绝一切世俗虚名与温存，在极度匮乏、疾病与狂热中用油彩与上帝直接对话，临终前彻底粉碎作品完成与世界的告别。"),
            ("德克·施特洛夫", "善良至极却画艺平庸的丑角画家", "能够一眼看破斯特里克兰德的天才价值，在妻子被夺、家破人亡后依然为天才买单，体现了世俗善良的崇高与无奈。"),
            ("毛姆（叙述者）", "洞察世情的冷眼观察者", "既震惊于主角的冷血，又深深被这种超越凡俗的精神狂热所震撼，以嘲讽幽默的笔调记录下整场人生实验。")
        ],
        "perception": "表面是一个中年男人离家出走学画画的离奇八卦；深处叩问了‘人类灵魂究竟该为世俗责任安稳买单，还是为内心的神圣召唤彻底燃烧’。",
        "conflict": "平庸舒适的中产家庭责任 vs 势不可挡的艺术天命召唤；世俗的善良体面 vs 天才的野蛮自私。",
        "turning_point": "斯特里克兰德身患麻风病失明：在生命最后的黑暗中，他在大溪地木屋墙壁上画出了惊天地泣鬼神的原始创世纪壁画，随后命爱塔在他死后一把火烧尽。",
        "symbols": [
            ("月亮与六便士：", "月亮象征悬在夜空、无用却照亮灵魂的至高理想；六便士象征低头弯腰即可捡起、却把人锁在泥土里的世俗物质财富。"),
            ("焚烧的木屋壁画：", "宣告艺术创造的终极目的在于创造者自身的狂喜与解脱，而非迎合世俗后人的掌声与买卖拍卖。")
        ],
        "themes": "追求天命所必须承受的残酷代价；真正的艺术超越世俗道德标准；平庸生活的自欺与解围。",
        "socratic": "Q1：如果世界上人人都是斯特里克兰德，人类社会将陷入崩溃；但如果没有一个斯特里克兰德，人类文明还有探索未知的狂喜吗？\nQ2：他在临死前让妻子将耗尽毕生心血的壁画全部烧掉，这是一种狂妄，还是真正的彻底放下？",
        "action": "人生价值盘点：拿出你的日记本，写下你目前生活中属于‘六便士’的琐事与属于‘月亮’的纯粹热爱，评估两者的平衡状态。"
    },

    "大白鲸": {
        "title_cn": "大白鲸", "title_en": "Moby-Dick",
        "author_cn": "赫尔曼·麦尔维尔", "author_en": "Herman Melville",
        "sub_desc": "美国文学最伟大的史诗丰碑 · 人类意志与冷酷宇宙力量的壮烈决斗",
        "hero_quote": "为了向你发泄我的仇恨，我不惜一切；从地狱深处我刺向你，为了毁灭，我吐出我最后的呼吸！",
        "year": "1851 年出版", "genre": "海洋史诗 / 形而上学象征杰作",
        "length": "约 45 万字", "age": "14+ 岁 / 青年与成人深读",
        "criteria": "人类疯狂意志向大自然冷漠神秘力量的绝命挑战",
        "warning": "不要把《大白鲸》当作普通的捕鲸惊险小说，也不要被书中详尽的鲸鱼生物学、炼油工业技术章节吓退。麦尔维尔是在借一艘名为‘裴廓德号’的捕鲸船，载着全人类的缩影，在大洋深处向不可名状、冷酷威严的宇宙神秘意志（莫比·迪克）发起绝望的形而上决斗。",
        "highlights": [
            "亚哈船长在甲板上用西班牙金币煽动全体船员狂热复仇誓师。",
            "追猎巨鲸莫比·迪克连续三天的惊天地泣鬼神生死搏杀。",
            "裴廓德号被大白鲸撞沉卷入巨大漩涡，唯有以实玛利借棺木浮出海面幸存。"
        ],
        "context": "19世纪中叶美国捕鲸黄金时代，现代商业资本与狂热意志乘风破浪，向未知大自然与深海展开征服掠夺。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#131619" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">亚哈船长 (Ahab)</text>
          <text x="140" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">鲸骨义肢 · 意志偏执狂魔</text>
          <text x="140" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">向冷酷天命发起至死决斗</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#fbf9f4" stroke="#1d3557" stroke-width="2" />
          <text x="540" y="60" fill="#1c221e" font-weight="700" text-anchor="middle">大白鲸莫比·迪克</text>
          <text x="540" y="80" fill="#59645f" font-size="11" text-anchor="middle">雪白巨兽 · 自然神秘意志</text>
          <text x="540" y="100" fill="#59645f" font-size="11" text-anchor="middle">不可被驯服的形而上深渊</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#1d3557" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">裴廓德号 (Pequod)</text>
          <text x="340" y="188" fill="#cad5e2" font-size="11" text-anchor="middle">多民族人类微观缩影 · 沉入深渊</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#131619" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("亚哈船长", "普罗米修斯式的悲剧狂人", "断腿之仇化作形而上的宇宙宿怨，将整艘船引向万劫不复的深渊，最后一刻被捕鲸绳缠颈拖入大海。"),
            ("以实玛利 (Ishmael)", "幸存的漫游哲思叙述者", "‘唤我以实玛利’开篇，代表对浩瀚海洋怀有敬畏之心的谦卑观察者，靠好友魁魁格的空棺木漂流脱险。"),
            ("大副斯塔巴克", "常识与理性的悲情守护者", "虔诚笃实，多次劝阻亚哈放弃复仇，在疯狂意志的裹挟下无力挽回全船覆灭的宿命。")
        ],
        "perception": "表面是一场惊心动魄的深海捕鲸灾难史诗；深处探讨了‘渺小人类面对无情、宏大、不可捉摸的宇宙自然力量时的狂妄与敬畏’。",
        "conflict": "人类傲慢狂热的征服意志 vs 大自然冷酷超越善恶的客观物理威严。",
        "turning_point": "第三天追捕：莫比·迪克调转庞大身躯，如同巨大撞锤正面对准裴廓德号船头迎头一撞，木板碎裂海水灌入，宣告自然终极胜利。",
        "symbols": [
            ("白鲸莫比·迪克：", "纯洁无瑕又恐怖致命的雪白，象征超越人类善恶道德之上的宇宙神秘法则。"),
            ("魁魁格的雕花棺木：", "死者预备的寿材，最终化作以实玛利漂浮生还的救生筏，象征生与死奇妙的辩证循环。")
        ],
        "themes": "狂热偏执对集体命运的毁灭性绑架；在大自然面前人类必须学会谦逊敬畏；生命在虚无大海中的存在主义漂流。",
        "socratic": "Q1：亚哈船长的大战，究竟是一场可歌可泣的人类英雄抗争，还是一场自大无耻拉所有人陪葬的犯罪？\nQ2：大白鲸有意识地在‘仇恨人类’吗？还是人类一厢情愿把大自然的冷漠解读成了敌意？",
        "action": "敬畏练习：在空旷夜晚仰望星空或面对大海，体会自身在几百亿光年宇宙中的沧海一粟，感受自省带来的心智宁静。"
    },

    "小王子": {
        "title_cn": "小王子", "title_en": "Le Petit Prince",
        "author_cn": "安托万·德·圣-埃克苏佩里", "author_en": "Antoine de Saint-Exupéry",
        "sub_desc": "献给所有曾是孩子的成人的至高童话 · 驯服、责任与爱的真谛",
        "hero_quote": "看东西只有用心才能看得清楚；真正重要的东西，用肉眼是看不见的。",
        "year": "1943 年出版", "genre": "哲理寓言童话 / 诗意哲学小说",
        "length": "约 5 万字", "age": "全年龄读者必读经典",
        "criteria": "纯真赤子之心对成人功利世界的诗意解构",
        "warning": "切勿以为这只是一本供幼儿阅读的插图睡前故事。圣-埃克苏佩里在二战流亡的至暗时刻，借一个来自B612小行星的小小访客，严峻剖析了现代成人世界的数字崇拜、官僚自大、孤独成瘾与意义虚无。它是一本含着眼泪写给成人的救赎之书。",
        "highlights": [
            "第一章‘蛇吞象’被大人当作普普通通帽子的经典认知寓言。",
            "狐狸传授给小王子‘关于驯服（建立羁绊）’的永恒哲学课。",
            "在五千朵盛开的玫瑰花丛中，小王子领悟到‘我的玫瑰是独一无二的’深情真谛。"
        ],
        "context": "二战沦陷的法国与流亡纽约的飞行员，现代科技与战争机器把人类推入空前野蛮，呼唤爱与温柔的回归。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">B612 小行星</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">骄傲带刺的玫瑰花</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">清理猴面包树嫩芽 · 纯洁初心</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">大人的荒诞星球</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">无民之王 · 数星商人 · 点灯人</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">只认数字与权力的枯竭心智</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">狐狸的驯服法则</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">建立羁绊 · 为你的玫瑰永远负责</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("小王子", "来自微小星球的纯净赤子", "拥有不被世俗污染的眼睛，认真对待日落、花朵与绵羊，为了重返所爱的玫瑰坦然接受蛇吻脱去沉重肉身。"),
            ("狐狸", "传授爱与生命智慧的哲人", "教会小王子：‘正因为你在玫瑰身上花费了时间，你的玫瑰才变得如此重要。’"),
            ("玫瑰花", "骄傲纤弱的初恋投射", "用四根刺假装坚强，掩饰内心的自卑与深情，是促使小王子远行探索又终生挂怀的源头。")
        ],
        "perception": "表面是一部唯美忧伤的星际童话；深处指引着在物欲与数字中迷失的现代人，如何找回爱他人与建立深层精神联结的能力。",
        "conflict": "儿童纯洁透彻的心灵感知 vs 成人世界盲目功利的数字算计；建立羁绊的可能受伤风险 vs 孤独自闭的安全牢笼。",
        "turning_point": "狐狸的临别赠言：在小王子因发现地球有五千朵一模一样的玫瑰而伤心落泪时，狐狸道破了真爱的秘密——不是因为它罕见，而是因为你曾为它浇灌、为它遮风挡雨。",
        "symbols": [
            ("麦田的颜色：", "狐狸不吃面包，但从此只要看到金黄的麦田，就会想起小王子金色的头发。象征羁绊留给世界的神圣痕迹。"),
            ("猴面包树：", "如果不及时拔除就会撑破星球的恶性植物，象征人性中懒惰、贪婪与偏执的微小萌芽。")
        ],
        "themes": "驯服即建立不可替代的情感联结；为所爱之人承担无休止的责任；唯有用心灵才能触碰真实的智慧。",
        "socratic": "Q1：如果建立羁绊意味着‘承担流泪的风险’，为什么狐狸依然渴望被小王子驯服？\nQ2：小王子最后倒在沙漠里被毒蛇咬伤，他是真正回到了他的B612星球，还是永远死去了？这为什么并不重要？",
        "action": "羁绊仪式：为你生活中某个重要的人（父母、伴侣或挚友），写一张卡片列出三件‘只有你们彼此经历过、因而独一无二的小细节’。"
    },

    "弗兰肯斯坦": {
        "title_cn": "弗兰肯斯坦", "title_en": "Frankenstein",
        "author_cn": "玛丽·雪莱", "author_en": "Mary Shelley",
        "sub_desc": "世界科幻小说的真正鼻祖 · 现代普罗米修斯的人性试炼",
        "hero_quote": "我是你的创造物，我原本该是你的亚当，但我却因为你的厌弃，变成了堕落的恶魔撒旦！",
        "year": "1818 年出版", "genre": "哥特科幻小说 / 伦理悲剧",
        "length": "约 18 万字", "age": "13+ 岁 / 青年与思辨必读",
        "criteria": "造物主责任的背弃与科技力量的伦理反噬",
        "warning": "切勿以为‘弗兰肯斯坦’是那个大怪物的名字。弗兰肯斯坦是那位创造了生命的年轻科学家；那个没有名字的生物，原本渴望阳光、友谊与善意，是在遭到生身之父无情遗弃、遭遇世人以貌取人的石块殴打后，才在绝望中黑化为复仇的杀戮者。",
        "highlights": [
            "十九岁少女玛丽·雪莱在日内瓦湖畔暴雨之夜惊世骇俗的噩梦构想。",
            "怪物在森林木屋悄悄为盲人老农劈柴、自学语言的纯真温存岁月。",
            "北极冰原上造物者与被造物在冰山裂隙间的至死追逐绝响。"
        ],
        "context": "工业革命黎明期，电生理学与生物解剖兴起，人类第一次试图扮演上帝的角色创造生命，技术伦理警钟初鸣。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">维克多·弗兰肯斯坦</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">傲慢年轻学者 · 扮演上帝</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">诞生之日惊骇弃逃，背弃责任</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">被造物 (The Creature)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">拼凑肉体 · 渴望爱与接纳</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">遭全人类厌弃，堕落复仇</text>
          <line x1="230" y1="72" x2="450" y2="72" stroke="#8c2d19" stroke-width="2.5" />
          <text x="340" y="62" fill="#8c2d19" font-size="11" font-weight="600" text-anchor="middle">爱而不得的弑亲复仇循环</text>
        </svg>""",
        "characters": [
            ("维克多", "着魔的青年科学家", "被探索生命源头的狂热驱使，在尸块拼装成功的一刻被丑陋外表吓退，因逃避责任引来满门杀身之祸。"),
            ("怪物 (The Monster)", "心智敏锐的悲剧异类", "读过《失乐园》与《浮士德》，渴望拥有一个同类伴侣不再孤独，求告无门后走向彻底绝望毁灭。"),
            ("沃顿船长", "北极探险船长与叙述者", "在弗兰肯斯坦与怪物的临终对峙中汲取教训，果断放弃不顾船员死活征服北极点的狂热执念，选择返航。")
        ],
        "perception": "表面是一个死尸复活的恐怖科幻传说；深处提出了现代科技最严峻的伦理追问：‘创造了力量却不承担教育与关照责任的人，才是真正的怪物’。",
        "conflict": "人类对超凡科技力量的狂妄掌控欲 vs 承担后果的懦弱逃避；外在皮囊丑陋 vs 内在温存渴望被偏见剥夺。",
        "turning_point": "维克多撕毁即将完成的女性怪物身躯：在答应给怪物制造一个伴侣后，维克多出于对物种繁衍失控的恐惧撕毁承诺，彻底逼怪物在婚礼之夜杀害其新娘伊丽莎白。",
        "symbols": [
            ("普罗米修斯的火种：", "赋予生命的神奇电火，既是启蒙理性的至高荣耀，也是焚毁一切的灾难之源。"),
            ("冰原与绝境：", "北极万劫不复的冰峰，象征人类理智失去温暖同情后走向的冰冷极境。")
        ],
        "themes": "科技伦理必须先行于技术狂热；以貌取人的社会偏见如何亲手制造出凶手；对被创造者神圣不可推卸的生命抚养之责。",
        "socratic": "Q1：如果怪物长得像天使一样俊美，维克多还会仓皇逃跑吗？世人还会用棍棒石头驱逐他吗？\nQ2：今天的人工智能和基因编辑技术，正在把我们每个人变成‘弗兰肯斯坦’吗？我们准备好承担后果了吗？",
        "action": "AI伦理辩论：假如未来强人工智能诞生了自我意识，我们该赋予它们公民权利并以爱相待，还是仅仅把它们当作随用随关的奴仆代码？"
    },

    "彼得潘": {
        "title_cn": "彼得·潘", "title_en": "Peter Pan",
        "author_cn": "J·M·巴里", "author_en": "J. M. Barrie",
        "sub_desc": "永不长大的飞翔神话 · 纯真乐园与残酷成年的永恒拔河",
        "hero_quote": "所有的孩子都会长大，除了一个人。",
        "year": "1911 年出版", "genre": "奇幻冒险童话 / 成长寓言",
        "length": "约 12 万字", "age": "全年龄经典",
        "criteria": "拒绝长大背后对世俗规则的抗拒与遗忘代价",
        "warning": "不要把彼得·潘看作无忧无虑的快乐天使。巴里在字里行间流露出一丝冰冷的残酷——彼得·潘之所以永远不长大，是因为他拥有令人心碎的‘健忘’；他忘记了每一个爱过他的人，甚至忘记了曾经的冒险。拒绝长大，意味着拒绝了深情与记忆。",
        "highlights": [
            "达林先生一家育婴室窗前飞翔而入的那个夜晚。",
            "梦幻岛（Neverland）上失落的孩子、人鱼礁湖与凶残的虎克船长。",
            "温迪选择告别无忧仙境，回到父母身旁迎接终将老去的凡人一生。"
        ],
        "context": "爱德华时代英国中产阶级严苛的绅士淑女教养体制，压抑儿童本真想象，催生了对飞翔仙境的深情呼唤。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">梦幻岛 (Neverland)</text>
          <text x="140" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">彼得·潘 · 永不长大 · 飞翔狂欢</text>
          <text x="140" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">代价：遗忘一切深情记忆</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">达林家育婴室 (London)</text>
          <text x="540" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">温迪与弟弟 · 凡俗人间</text>
          <text x="540" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">必须长大 · 承担责任与变老</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">虎克船长 (Captain Hook)</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">成年人的恐惧化身 · 滴答鳄鱼</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#2a9d8f" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#1d3557" stroke-width="2" />
        </svg>""",
        "characters": [
            ("彼得·潘", "拒绝成熟的永恒少年", "骄傲、勇敢、充满魅力，却被困在自己创造的无龄仙境里，每次回到窗前只能看着温迪逐渐老去。"),
            ("温迪 (Wendy)", "理智温婉的世俗女孩", "在梦幻岛扮演孩子们的‘母亲’，但她清醒地明白飞翔只是一个梦，最终选择回到现实面对成长与结婚生子。"),
            ("虎克船长", "被时间追杀的成年人隐喻", "铁钩代替了手臂，最恐惧的是吞下闹钟的鳄鱼——那一刻不停的‘滴答’声，正是成年人对衰老与死亡的终极惊骇。")
        ],
        "perception": "表面是一部带仙子魔粉与海盗火枪的儿童童话；深处是一曲关于‘告别童年与接纳变老’的心碎哲学诗。",
        "conflict": "无拘无束拒绝承担责任的永恒童稚 vs 充满牵绊、痛苦却有温度的成年现实。",
        "turning_point": "达林太太虚掩的窗户：彼得·潘当年离家出走再回来时，发现母亲已经把窗户锁死生了新宝宝，这个创伤使他坚信‘母亲都是虚伪的’；而温迪坚信母亲会永远留着窗户，这份信任最终带全家孩子重返人间。",
        "symbols": [
            ("吞了闹钟的鳄鱼：", "时间无情流逝的鲜活具象，任何人都无法逃脱衰老与死亡的追捕。"),
            ("影子：", "被达林太太卷起来锁进抽屉的彼得潘的影子，象征文明规训试图捕捉儿童野性本真的微小角力。")
        ],
        "themes": "长大不可避免，但可以葆有一颗不老的童心；成年的代价是失去飞翔的能力，但换来了爱的深度与记忆的厚重。",
        "socratic": "Q1：如果给你一颗药丸可以永远活在十二岁不用长大，但代价是每隔一个月你就会忘记所有爱过你的人，你会吃下它吗？\nQ2：温迪选择长大，彼得潘选择留下，究竟哪一种选择需要更大的勇气？",
        "action": "时光对话：翻出一张你十年前的童年照片，写下几句话告诉当年的自己：虽然成年世界有诸多辛苦，但你现在拥有的哪一份深刻经验是当年童年所不具备的。"
    },

    "小妇人": {
        "title_cn": "小妇人", "title_en": "Little Women",
        "author_cn": "路易莎·梅·奥尔科特", "author_en": "Louisa May Alcott",
        "sub_desc": "温暖几代女性心智的成长史诗 · 独立、亲情与自我价值的寻觅",
        "hero_quote": "我不相信女人活着只是为了结婚生子；我们有思想，有灵魂，有雄心，也有才华！",
        "year": "1868 年出版", "genre": "家庭成长小说 / 女性主义启蒙经典",
        "length": "约 30 万字", "age": "10+ 岁 / 全年龄必读经典",
        "criteria": "女性在传统社会期待与个人独立志向间的平衡探索",
        "warning": "不要把《小妇人》看作四姐妹家长里短的甜美鸡汤。乔（Jo）在那个时代毅然剪掉引以为傲的秀发换钱补贴家用、独自前往纽约从事独立写作、断然拒绝富二代劳里的求婚，展示了卓越的女性自主意识与现代职业精神。",
        "highlights": [
            "战乱清贫的圣诞节早晨，姐妹们把早餐送给更穷苦邻居的高尚分享。",
            "乔面对挚友劳里的深情告白，克制而诚实地拒绝‘不适合的结合’。",
            "柔弱善良的贝丝染上猩红热离世，亲情在生死离别中的深沉凝聚。"
        ],
        "context": "美国南北战争后方清贫家庭，超验主义思想与基督教博爱道德滋润着平凡人的日常生活。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="30" y="30" width="135" height="90" rx="8" fill="#1d3557" />
          <text x="97" y="60" fill="#fff" font-weight="700" text-anchor="middle">梅格 (Meg)</text>
          <text x="97" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">美丽典雅长姐</text>
          <text x="97" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">拥抱清贫却真挚的婚姻</text>
          <rect x="185" y="30" width="135" height="90" rx="8" fill="#8c2d19" />
          <text x="252" y="60" fill="#fff" font-weight="700" text-anchor="middle">乔 (Jo)</text>
          <text x="252" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">灵魂主角 · 独立写作</text>
          <text x="252" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">抗拒传统束缚追寻自我</text>
          <rect x="340" y="30" width="135" height="90" rx="8" fill="#2a9d8f" />
          <text x="407" y="60" fill="#fff" font-weight="700" text-anchor="middle">贝丝 (Beth)</text>
          <text x="407" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">羞怯钢琴天使</text>
          <text x="407" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">安静博爱 · 灵魂凝聚核心</text>
          <rect x="495" y="30" width="135" height="90" rx="8" fill="#242930" />
          <text x="562" y="60" fill="#fff" font-weight="700" text-anchor="middle">艾米 (Amy)</text>
          <text x="562" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">世俗野心画家</text>
          <text x="562" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">追求艺术与上流优雅</text>
        </svg>""",
        "characters": [
            ("乔·马奇", "作者自身的投影化身", "个性率直、热爱文学，敢于打破闺秀刻板印象，凭笔杆子自食其力撑起家庭。"),
            ("劳里 (Laurie)", "英俊多金的邻家大男孩", "从孤独冷漠的深宅少年被四姐妹的欢声笑语治愈，在求婚乔被拒后历经淬炼与艾米结合。"),
            ("马奇太太（妈咪）", "全家最坚韧温柔的精神灯塔", "不求女儿攀附豪门，只愿她们葆有高尚的德行与内心的平和独立。")
        ],
        "perception": "表面是一部记录四个女孩生活细碎琐事的家庭小说；深处展示了女性在经济依赖时代，如何通过不同的人格选择实现自尊、尊严与幸福。",
        "conflict": "物质贫困对体面的剥夺 vs 道德高尚带来的心灵丰裕；传统社会对女性的结婚规训 vs 追求个人事业的自我实现。",
        "turning_point": "乔在阁楼上焚稿与重写：在巴尔教授的直率批评下，乔放弃了粗制滥造的廉价通俗惊悚小说，开始挖掘自己内心深处最真诚的家庭记忆写作，终成大器。",
        "symbols": [
            ("那顶插着羽毛的旧天鹅绒写作帽：", "乔在阁楼埋头写作时的战袍，象征女性纯粹创造力觉醒的圣地。"),
            ("剪掉的秀发：", "女性为了拯救病重父亲自愿放弃世俗美貌标志，象征家庭爱意超越虚荣的牺牲之美。")
        ],
        "themes": "真正的贫穷是心灵的匮乏，而非兜里没有钞票；女性拥有选择自己生活方式的崇高权利；亲情是抵御世界严酷风霜最牢固的城堡。",
        "socratic": "Q1：乔当年拒绝嫁给英俊富有的劳里，很多人感到遗憾，但如果乔答应了，她还会成为那个伟大的独立作家乔吗？\nQ2：四姐妹性格迥异、选择各异，这给今天的女性如何面对多样化的人生选择提供了怎样的启示？",
        "action": "家庭连线：给家里的母亲或姐妹发一条信息，感谢她曾经在某个不起眼的小事上给予你的温暖支持与包容。"
    },

    "手斧男孩": {
        "title_cn": "手斧男孩", "title_en": "Hatchet",
        "author_cn": "盖瑞·伯森", "author_en": "Gary Paulsen",
        "sub_desc": "纽伯瑞银奖荒野求生圣经 · 一把手斧铸就的坚毅男子汉",
        "hero_quote": "自怜是毫无用处的；哭泣救不了命，唯有思考、行动和耐心才能让你活下去。",
        "year": "1987 年出版", "genre": "荒野求生小说 / 少年成长励志经典",
        "length": "约 10 万字", "age": "10+ 岁 / 青少年坚毅品格必读",
        "criteria": "极端生存逆境中独立问题解决心智的淬炼",
        "warning": "切勿以为这是一部开挂猎奇的探险爽文。十三岁男孩布莱恩独自困在加拿大原始针叶林54天，经历了饥饿、黑熊、野猪、龙卷风、机油刺鼻以及自杀绝望的彻底洗礼。他最大的敌人不是野兽，而是脑海中父母离婚的痛苦秘密与放弃生存的怠惰。",
        "highlights": [
            "小飞机飞行员心脏病突发猝死，十三岁少年被迫自行迫降湖泊。",
            "用母亲赠送的手斧在黑夜玄武岩上砸出火花、成功生出救命篝火。",
            "龙卷风掀翻营地后潜入沉没机舱打捞应急包的惊心动魄生死潜水。"
        ],
        "context": "现代都市青少年被温室过度保护、丧失野外生存与独立解决问题本能的时代反思之作。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">都市文明的软弱少年</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">沉溺父母离异秘密痛苦</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">依赖现成外卖与电子产品</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">荒野重塑的坚毅战士</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">观察自然规律 · 制作鱼叉弓箭</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">学会忍耐、专注与尊重自然</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">唯一工具：手斧 (Hatchet)</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">砍柴 · 生火 · 削箭 · 重建自信</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("布莱恩·罗伯森", "十三岁的普通都市男孩", "经历了从绝望痛哭到冷静制火、捕鱼狩猎的蜕变，成长为一个沉稳、敏锐、深具大将之风的真正男子汉。"),
            ("大自然森林生态", "冷酷却公平的严格导师", "不讲人情，却遵守严格的物理与生态法则；只要你尊重它、读懂它，它就赐予你浆果、鸟蛋与活路。")
        ],
        "perception": "表面是一部惊险跌宕的荒岛/野外求生小说；深处展示了一个人在被彻底剥夺了一切外部依赖后，如何从内心深处挖出尊严与力量之井。",
        "conflict": "脆弱自怜的消极退缩心态 vs 面对残酷现实必须行动求生的刚毅意志。",
        "turning_point": "手斧敲击岩石冒出火星：在豪猪刺伤小腿的黑夜，布莱恩偶然发现手斧钢刃砸中黑燧石产生的火花，历经数百次尝试终于用桦树皮吹出了第一缕神圣的火苗。",
        "symbols": [
            ("手斧：", "母亲赠送的皮带上的微小礼物，象征文明赋予个体的最初工具，也是重启生存的钥匙。"),
            ("篝火：", "黑夜中的朋友与守卫，驱散野兽与蚊虫，给荒野孤独的灵魂带来安全感与文明体温。")
        ],
        "themes": "绝境中最大的敌人是自己的恐慌自怜；行动与专注是治愈一切焦虑的良药；大自然教给人类的谦逊与生存智慧。",
        "socratic": "Q1：如果现代都市突然断电断网三天，你自己的生存技能能支撑你独立解决生活问题吗？\nQ2：布莱恩在获救后，为什么对曾经折磨得他痛不欲生的‘父母离婚秘密’选择了永远守口如瓶？",
        "action": "抗挫心法练习：“归零测试”——遇到任何考试失利或工作挫折时，对自己说三句话：1. 哭泣毫无用处；2. 事实已经发生；3. 我目前手上最好的‘下一把手斧’是什么？"
    },

    "欧亨利短篇小说": {
        "title_cn": "欧·亨利短篇小说精选", "title_en": "Selected Stories of O. Henry",
        "author_cn": "欧·亨利", "author_en": "O. Henry",
        "sub_desc": "世界短篇小说三巨匠之一 · 曼哈顿街头的含泪微笑与至情神反转",
        "hero_quote": "人生是由啜泣、抽噎与微笑交织而成的，而抽噎占据了其中绝大部分。",
        "year": "20 世纪初经典", "genre": "市民世态小说 / 经典欧亨利式反转",
        "length": "精选数十部传世名篇", "age": "11+ 岁 / 全年龄必读名著",
        "criteria": "精巧绝伦的情节反转与底层小人物的人道温情",
        "warning": "不要只满足于最后一句‘欧·亨利式惊奇反转（O. Henry Twist）’带来的戏剧快感。欧·亨利最动人的底色，是他在纽约地下廉价公寓、流浪汉长椅、典当行里，写出了最平凡底层人身上所闪耀的舍身之爱与高贵善良。",
        "highlights": [
            "《麦琪的礼物》：卖掉金表买发梳、剪掉长发买表链的千古至情错位献祭。",
            "《最后一片叶子》：老画家贝尔曼在风雨长夜用画笔在砖墙上留下的生命绝笔。",
            "《警察与赞美诗》：流浪汉苏比一心想进监狱蹭暖冬屡屡碰壁、被教堂赞美诗感召决心自新的一瞬却被逮捕的命运讽刺。"
        ],
        "context": "20世纪初镀金时代的纽约曼哈顿，四百万小职员、穷艺术家、售货女郎在金钱丛林中艰辛求生。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">冷酷都市现实 (NYC)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">廉价公寓 · 八美元房租</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">寒风刺骨 · 贫穷与窘迫</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#2a9d8f" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">小人物的人道微光</text>
          <text x="540" y="80" fill="#e5e8eb" font-size="11" text-anchor="middle">舍己之爱 · 舍命壁画</text>
          <text x="540" y="100" fill="#e5e8eb" font-size="11" text-anchor="middle">苦难中的含泪微笑</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#8c2d19" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">欧·亨利式反转 (Twist)</text>
          <text x="340" y="188" fill="#f0dcd8" font-size="11" text-anchor="middle">意料之外 · 情理之中 · 命运的温情嘲弄</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#2a9d8f" stroke-width="2" />
        </svg>""",
        "characters": [
            ("德拉与吉姆 (《麦琪的礼物》)", "贫寒相守的小夫妻", "双双卖掉自己最珍视的传家宝为对方买圣诞礼物，虽失去实用价值，却赢得了世界上最无价的精神富有。"),
            ("贝尔曼 (《最后一片叶子》)", "暴躁酗酒的底层老画家", "一辈子吹嘘要画杰作，在狂风暴雨的冰冷雨夜爬上梯子在墙上画出永不凋零的藤叶，用生命救活了年轻姑娘。"),
            ("苏比 (《警察与赞美诗》)", "幽默自嘲的流浪汉", "精心策划犯罪想进黑岛监狱过冬失败，在重燃生活希望的一刹那被抓，展现了宿命无情的黑色幽默。")
        ],
        "perception": "表面是一篇篇充满戏剧幽默反转的都市传奇；深处流淌着对在钢筋水泥丛林中被生活碾压的小人物深切的同情与敬意。",
        "conflict": "贫穷匮乏对尊严的压迫 vs 精神深处不可剥夺的慷慨爱意；荒谬命运的捉弄 vs 人性微光的暖意。",
        "turning_point": "每篇故事终局的揭秘瞬间：吉姆掏出发梳、德拉摊开没有金表的表链；清晨窗外暴风雨过后依然挺立的最后一片常春藤叶。",
        "symbols": [
            ("最后一片常春藤叶：", "真正的艺术杰作不在于挂进卢浮宫，而在于它是否拥有能够挽救一条生命的慈悲力量。"),
            ("发梳与表链：", "被错位的礼物，象征超越一切实用功利计算的真挚献祭。")
        ],
        "themes": "含泪微笑的人生哲学；底层平民深藏的牺牲精神；命运的戏剧性与偶然性中对善意的守候。",
        "socratic": "Q1：吉姆和德拉的礼物在实用层面上都成了废品，为什么欧·亨利却称他们为‘最聪明的东方三博士（麦琪）’？\nQ2：贝尔曼画了一辈子的庸作，最后画在潮湿砖墙上的那片叶子，为什么能成为不朽的杰作？",
        "action": "微型故事练习：模仿‘意料之外、情理之中’的构思，写一个200字的‘两个互相替对方着想的人最后闹出温情误会’的小故事。"
    },

    "密西西比河上的生活": {
        "title_cn": "密西西比河上的生活", "title_en": "Life on the Mississippi",
        "author_cn": "马克·吐温", "author_en": "Mark Twain",
        "sub_desc": "大河奔流的美国史诗回忆录 · 汽船黄金时代的壮美画卷与逝去挽歌",
        "hero_quote": "把这条大河的每一处浅滩、暗礁与回流刻进脑海；大河就像一本永无止境的大书，每一天都在翻开全新的篇章。",
        "year": "1883 年出版", "genre": "自传体散文长卷 / 地域文化史诗",
        "length": "约 30 万字", "age": "12+ 岁 / 青年与通识必读",
        "criteria": "大河地理人文知识与幽默讽刺叙事的完美融合",
        "warning": "不要以为这只是一部写给游客看的大河风光游记。马克·吐温以极其幽默诙谐却又苍凉深情的笔触，记录了自己青年时代做领港员（水手引航长）的硬核受训生涯，以及随后的铁路与工业化如何无情碾碎了整个汽船时代的浪漫传奇。",
        "highlights": [
            "拜师老领航员比克斯比时，在黑夜狂流中强记一千两百英里暗礁水流的严苛训练。",
            "领航员在甲板上受人尊崇若神明的极盛荣光。",
            "二十年后重访大河时，目睹古老城镇衰落、大河被铁路桥梁束缚的怅惘沉思。"
        ],
        "context": "美国内战前夕密西西比河汽船航运鼎盛，随后铁路时代全面降临，传统内河航运文明急速谢幕。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">汽船领港员时代</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">桀骜不驯的航道之王</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">凭肉眼记忆夜航千重暗礁</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">铁路与机械时代</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">铁桥横跨 · 汽船消亡</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">大河浪漫传奇被速度终结</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">密西西比大河 (The River)</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">变幻莫测的自然母体 · 孕育美国精神</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("年轻的吐温", "懵懂求学的学徒小水手", "从自负傲慢被师傅骂得狗血喷头，到能闭着眼睛辨别水底浅滩沙沙声的顶尖引航员，经历了心智与技能的千锤百炼。"),
            ("比克斯比船长", "威严神武的技术宗师", "外冷内热，严厉近乎残酷，代表了老一代匠人对专业技能炉火纯青的至高信仰。"),
            ("大河两岸各色赌徒、棉农与浪客", "19世纪生机勃勃的美国边疆群像", "展现了未经欧洲老朽文明规训的粗粝、豪爽与狡黠。")
        ],
        "perception": "表面是一部引人入胜的美国航海水手见闻录；深处记录了美国人如何在一场伟大的河流实践中，塑造出坚毅、幽默、崇尚实证的民族性格原型。",
        "conflict": "人类对危险狂野大自然规律的苦心钻研与驯服 vs 现代化流水线技术对传统手艺浪漫的无情替代。",
        "turning_point": "吐温领悟‘大河水色之美背后的危险’：当他把大河当成普通风景看时，看到的是瑰丽的晚霞；当他成为领航员后，晚霞意味着暗礁、微澜意味着死水浅滩——诗意丧失了，但责任与专业诞生了。",
        "symbols": [
            ("水深两拃（Mark Twain）：", "探水水手报告安全水深的行话口令，后成为这位伟大文学家终生的笔名与生命印记。"),
            ("深夜无灯的盲航：", "在浓雾黑夜中凭水流微声航行，象征人类依靠经验与勇气在未知命运中的坚定前行。")
        ],
        "themes": "专业技能的严苛淬炼之路；对工业化碾碎传统手艺浪漫的挽歌；大自然不可预测的雄浑威严。",
        "socratic": "Q1：当吐温掌握了全部引航知识后，感叹自己再也无法单纯欣赏大河风景的美丽，这揭示了知识的获得与审美感性之间怎样的得失？\nQ2：现代自动化航运取代了当年领航员的神技，我们收获了效率，但人类灵魂失去了哪种与自然直接交锋的野性尊严？",
        "action": "专注力训练：回想一项你花费了大量精力熟练掌握的技能（如编程、骑车、弹琴），写下从‘手忙脚乱’到‘肌肉记忆本能’的心路历程。"
    },

    "时间旅行者的妻子": {
        "title_cn": "时间旅行者的妻子", "title_en": "The Time Traveler's Wife",
        "author_cn": "奥黛丽·尼芬格", "author_en": "Audrey Niffenegger",
        "sub_desc": "打破时空维度的深情现代寓言 · 离散、等待与永恒的爱意坚守",
        "hero_quote": "我爱你，在时间的任何一个角落；即便我不在你身边，我的爱也从未离开过你一秒钟。",
        "year": "2003 年出版", "genre": "科幻罗曼史 / 现代存在主义爱情长篇",
        "length": "约 35 万字", "age": "14+ 岁 / 青年与成人深读",
        "criteria": "非线性时空下的深情坚守与接纳命运的勇气",
        "warning": "不要把这本书当成普通言情穿越小说。尼芬格极其残忍地剥离了一切浪漫金手指——亨利患有‘慢性时间错位症’，他的穿越是不可控的基因缺陷，往往在毫无防备的瞬间赤身裸体被抛掷在寒风暴雪与陌生枪口下。克莱尔用一生漫长而孤独的等待，诠释了人类在无常命运面前最神圣的接纳与包容。",
        "highlights": [
            "非线性叙事的精巧拼图：亨利在六岁、二十岁、四十岁与克莱尔在不同年龄段的时空交叠互渗。",
            "亨利赤身裸体穿越时为了生存必须学会开锁、偷衣服与奔跑的窘迫真实刻画。",
            "全书结尾克莱尔白发苍苍坐在窗前，等待八十二岁的自己与生命最后一次跨越时空的亨利重逢。"
        ],
        "context": "现代都市快节奏生活中人际关系的易碎与漂泊，人们面对疾病、离别与不可控命运时对恒常忠诚的深情呼唤。",
        "svg": """<svg viewBox="0 0 680 240" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="30" width="180" height="85" rx="8" fill="#1d3557" />
          <text x="140" y="60" fill="#fff" font-weight="700" text-anchor="middle">亨利 (Henry · 流浪者)</text>
          <text x="140" y="80" fill="#cad5e2" font-size="11" text-anchor="middle">基因缺陷 · 不自主时空穿梭</text>
          <text x="140" y="100" fill="#cad5e2" font-size="11" text-anchor="middle">赤身裸体 · 颠沛流离与宿命预知</text>
          <rect x="450" y="30" width="180" height="85" rx="8" fill="#8c2d19" />
          <text x="540" y="60" fill="#fff" font-weight="700" text-anchor="middle">克莱尔 (Clare · 守望者)</text>
          <text x="540" y="80" fill="#f0dcd8" font-size="11" text-anchor="middle">造纸艺术家 · 线性等待一生</text>
          <text x="540" y="100" fill="#f0dcd8" font-size="11" text-anchor="middle">从六岁初遇守候至白发苍苍</text>
          <rect x="250" y="140" width="180" height="75" rx="8" fill="#2a9d8f" />
          <text x="340" y="168" fill="#fff" font-weight="700" text-anchor="middle">时间的重叠与锚定</text>
          <text x="340" y="188" fill="#e5e8eb" font-size="11" text-anchor="middle">在碎片时空中确认彼此唯一的爱</text>
          <line x1="140" y1="115" x2="260" y2="150" stroke="#1d3557" stroke-width="2" />
          <line x1="540" y1="115" x2="420" y2="150" stroke="#8c2d19" stroke-width="2" />
        </svg>""",
        "characters": [
            ("亨利", "被时间驱逐的悲情旅人", "无法掌控自己去往何方，目睹母亲车祸惨剧却无力改变历史，用尽全部意志在每次穿越中竭力爬回克莱尔身旁。"),
            ("克莱尔", "具有惊人耐受力的雕塑与造纸艺术家", "六岁在草地上遇见三十六岁的亨利，从此一生被这个不断消失又突然重现的男人锁定，在等待中开出绚烂的生命花朵。"),
            ("阿尔巴 (Alba)", "继承了时间穿梭基因的小女儿", "却拥有在时空中自主选择停留的控制力，象征新一代对命运残酷锁链的奇迹超越。")
        ],
        "perception": "表面是一部带时空穿梭科幻设定的现代虐恋奇幻小说；深处借物理学的无情错位，深刻探讨了‘爱一个人究竟意味着愿意为他承受多少不可预知的离别与等待’。",
        "conflict": "破碎非线性的无情时空引力 vs 坚守如一的单向情感锚定；预知死期的无力感 vs 享受当下每一秒的决绝。",
        "turning_point": "亨利提前知晓自己的死因与死期：在未来目睹自己因穿越至冰天雪地被误当作猎物开枪射杀，依然选择隐忍不告诉克莱尔，从容安排好剩余的每一天温存。",
        "symbols": [
            ("留在地上的空衣物：", "亨利突然消失留下的干瘪衣裤，象征生命中毫无征兆的不辞而别与无常空缺。"),
            ("克莱尔自制的手工宣纸：", "一层层纤维在水中缓慢沉淀交织，象征漫长岁月中的等待如何化作坚韧不可摧毁的生命骨骼。")
        ],
        "themes": "等待本身就是一种至高深沉的爱；接纳命运的无常与不可更改性；有限生命在当下相聚时的无价珍贵。",
        "socratic": "Q1：如果一段感情注定充满长期的分离、焦虑与过早的死别，像克莱尔那样全盘接受是理智的选择吗？\nQ2：预先知道自己的生命结局，究竟会让一个人更加绝望，还是让他活得更加清醒坦荡？",
        "action": "当下珍视练习：想象你与身边最亲爱的人下一次见面可能是不可预期的，用这种心态对待今晚的晚餐，放下手机，给予对方三十分钟全神贯注的倾听。"
    }
}

def main():
    print("=== 开始批量构建【批次 C：美国经典、心灵探究与成长名著】 ===")
    success = 0
    total = len(BOOKS_C)

    for book_name, info in BOOKS_C.items():
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

    print(f"=== 批次 C 顺利完工: {success}/{total} 部作品通过校验并落盘 ===")

if __name__ == "__main__":
    main()
