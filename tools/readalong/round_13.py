# -*- coding: utf-8 -*-
"""
Round 13: The Tempest, Twelfth Night, Julius Caesar (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_the_tempest():
    data = {
        "title_cn": "暴风雨",
        "title_en": "The Tempest",
        "author_cn": "威廉·莎士比亚",
        "author_en": "William Shakespeare",
        "sub_desc": "莎士比亚晚年绝笔传奇剧 · 宽恕超越复仇的至圣篇章与艺术魔杖的终极封存",
        "hero_quote": "我们都是梦中的材料；我们微渺的一生，在沉睡中前后缠绕；美德的罕见与高贵在于宽恕，绝不在于复仇。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">剧作家</div><div class="spec-val">威廉·莎士比亚 (1564–1616)</div></div>
        <div class="spec-item"><div class="spec-label">创作年份</div><div class="spec-val">约 1610–1611 年 / 告别剧坛绝唱</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">晚期传奇剧 / 文明寓言剧 / 宽恕史诗</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">全五幕九场 · 约 1.7 万词精粹诗剧</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身必读文学巅峰</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">复仇权柄的主动放下与殖民文明启蒙反思深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《暴风雨》简单看作一出老神仙在荒岛上用魔法耍弄仇人、最后让女儿结婚的大团圆奇幻神话。莎翁在生命的晚秋，通过米兰公爵普洛斯彼罗这一角色，严肃探讨了<strong>人类权力的本质、西方殖民主义对原住民的剥夺（卡利班问题）、以及艺术家在看透了世俗一切喧嚣之后，如何主动折断掌控生杀予夺的魔杖、平静重返凡人生活的至高从容</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 掌控生死权柄时对‘复仇’的主动弃绝：</strong>全书最震撼的道德高潮。十二年前被胞弟安东尼奥与那不勒斯国王勾结夺去王位、被推入漏水破舟九死一生的普洛斯彼罗，凭借魔法将全体仇敌诱入孤岛迷宫并玩弄于股掌之间。当他随时可以将所有人挫骨扬灰时，听到了风之精灵爱丽儿的同情之声，毅然宣布：‘我选择更高贵的理智，放弃狂怒；他们既然悔悟，我唯一的目的就已达到！’
      </div>
      <div class="card-box">
        <strong>② 卡利班（Caliban）身上大航海时代殖民启蒙的尖锐反思：</strong>岛屿原住民、女巫之子卡利班是世界文学史上最早的被殖民者隐喻。普洛斯彼罗占有了他的岛屿，教他学会了人类的语言；卡利班却反唇相讥：‘你们教我语言，我唯一的收获就是学会了如何诅咒！’这种文明征服与原生野性自尊之间的死结，展示了莎翁惊人的历史前瞻力。
      </div>
      <div class="card-box">
        <strong>③ 莎士比亚本人向世界舞台的壮美告别：</strong>第五幕著名的‘折断魔杖’演说与终场致辞（Epilogue）。普洛斯彼罗宣布：‘我要折断我的魔杖，把它埋入深土数尺；我要把我的魔法书沉入大洋，沉到铅锤永远测不到的深渊！’莎翁借主角之口，宣布结束自己三十年的戏剧创造生涯，收起神力，祈求观众用宽恕与掌声释放这位疲惫的凡人。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        17世纪初詹姆士一世时期，英国弗吉尼亚殖民地探险船队在百慕大群岛遭遇飓风神迹生还的消息轰动伦敦。莎翁以此为灵感，构筑了一座超凡脱俗的地中海魔法孤岛。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tp-box { rx: 8; stroke-width: 1.5; }
            .tp-bg-pros { fill: #1d3557; stroke: #2a4d7a; }
            .tp-bg-ariel { fill: #2a9d8f; stroke: #40916c; }
            .tp-bg-caliban { fill: #8c2d19; stroke: #a33b24; }
            .tp-bg-court { fill: #242930; stroke: #59645f; }
            .tp-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tp-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tp-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tp-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tp-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .tp-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .tp-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="tp-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 魔法全知掌控者：普洛斯彼罗 -->
          <rect x="230" y="25" width="220" height="120" class="tp-box tp-bg-pros" />
          <text x="340" y="52" class="tp-t-w">普洛斯彼罗 (Prospero)</text>
          <text x="340" y="72" class="tp-t-sub-w">米兰合法公爵 · 魔法宗师</text>
          <text x="340" y="90" class="tp-t-sub-w">掀起风暴 · 统辖全岛生灵</text>
          <text x="340" y="108" class="tp-t-sub-w">放下权柄 · 折断魔杖 · 宽恕仇敌</text>
          <text x="340" y="126" style="fill:#a8dadc; font-size:10.5px; font-weight:700; text-anchor:middle;">“莎士比亚本人收起羽毛笔的化身”</text>

          <!-- 气之精灵：爱丽儿 -->
          <path d="M 230 85 L 160 85" class="tp-blue" marker-end="url(#tp-arr)" />
          <text x="195" y="75" class="tp-lbl" style="fill:#2a9d8f;">役使与释放</text>

          <rect x="15" y="30" width="145" height="110" class="tp-box tp-bg-ariel" />
          <text x="87" y="58" class="tp-t-w">爱丽儿 (Ariel)</text>
          <text x="87" y="78" class="tp-t-sub-w">气与风之灵 · 歌声清冽</text>
          <text x="87" y="96" class="tp-t-sub-w">执行幻象施法任务</text>
          <text x="87" y="114" class="tp-t-sub-w">以怜悯之心感化公爵</text>
          <text x="87" y="128" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">终获绝对自由翱翔长空</text>

          <!-- 地之怪物：卡利班 -->
          <path d="M 450 85 L 520 85" class="tp-solid" marker-end="url(#tp-arr)" />
          <text x="485" y="75" class="tp-lbl">奴役与叛乱</text>

          <rect x="520" y="30" width="145" height="110" class="tp-box tp-bg-caliban" />
          <text x="592" y="58" class="tp-t-w">卡利班 (Caliban)</text>
          <text x="592" y="78" class="tp-t-sub-w">大地与泥土怪物 · 岛民</text>
          <text x="592" y="96" class="tp-t-sub-w">粗野本能 · 痛恨教化</text>
          <text x="592" y="114" class="tp-t-sub-w">勾结酒鬼水手谋反未遂</text>
          <text x="592" y="128" style="fill:#f0dcd8; font-size:9.5px; text-anchor:middle;">被殖民原住民的永恒隐喻</text>

          <!-- 下方：受洗礼的仇敌与新生代 -->
          <path d="M 340 145 L 340 200" class="tp-solid" stroke="#2a9d8f" />
          <rect x="160" y="200" width="360" height="115" class="tp-box tp-bg-court" />
          <text x="340" y="228" class="tp-t-w">迷途与重生 (那不勒斯国王 / 斐迪南 & 米兰达)</text>
          <text x="340" y="248" class="tp-t-sub-w">那不勒斯阿隆索国王：痛悔夺位罪恶，跪求公爵宽恕</text>
          <text x="340" y="266" class="tp-t-sub-w">米兰达 & 斐迪南：在纯真棋局中相爱，化解两代政治宿怨</text>
          <text x="340" y="284" class="tp-t-sub-w">“人类是多么美丽！啊，奇妙的新世界，有这样的人在其中！”</text>
          <text x="340" y="300" style="fill:#a8dadc; font-size:10.5px; font-weight:700; text-anchor:middle;">风暴平息，扬帆重返凡俗意大利人间</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>普洛斯彼罗（Prospero）：</strong>米兰合法公爵。十二年前因痴迷书斋研究、疏于政务，被野心勃勃的亲弟弟安东尼奥篡夺公位，与三岁幼女米兰达被塞入漏水破舟漂流至孤岛。他在岛上修习魔法，征服了精灵与巨兽。然而他最崇高的人格，不是用魔法呼风唤雨掀起巨浪，而是在将全体仇敌引至洞口、剑锋直指其咽喉的一刻，在爱丽儿的感召下主动宣布放下私仇。他撕开法袍、折断魔杖、将魔法秘籍沉入大洋深处，坦然重回毫无超能力的米兰做一个凡人领袖，准备安享晚年‘每走三步，就有一步要想到坟墓’。</li>
        <li><strong>爱丽儿（Ariel）：</strong>轻盈透明、具有神性灵光的气之精灵。他曾被邪恶女巫西考拉克斯囚禁在裂开的松树干中长达十二年，饱受日夜哀嚎的酷刑，直到被普洛斯彼罗解救。他忠心耿耿执行每一项复杂的舞台魔术任务，但他身上最动人的特质是‘对绝对自由的渴望’。在第四幕，正是这只没有人类肉身的精灵，对仇敌的痛苦流下了怜悯之泪，点醒了普洛斯彼罗心中的神圣宽恕。</li>
        <li><strong>卡利班（Caliban）：</strong>恶女巫与魔鬼结合产下的畸形野人。他身体腥臭如鱼，满脑子原始欲望，甚至企图玷污米兰达‘让岛上充满小卡利班’。然而，当他面对大自然时，却能用最纯粹优美的诗句描绘岛上的清泉、鸟巢与夜半飘来的仙乐（‘这岛上充满了声音，奇异而甜美的音调，带给人欢愉而不伤人’）。他把醉醺醺的酒鬼水手特林枯罗当成神明下跪，生动揭示了原住民被近代殖民者用烈酒轻易征服与玩弄的荒谬悲歌。</li>
        <li><strong>米兰达（Miranda）：</strong>从未见过其他男性的纯真海岛圣女。三岁流落孤岛，在父亲的悉心教导与自然风霜中长大。当风暴掀翻大船时，她哭喊着求父亲‘如果是你的法术掀起了巨浪，请快快平息它，因为我看见无辜的人受难，我的心也碎成了千万片！’当她第一次看见落难的年轻王子斐迪南时，以为对方是天神降临；而斐迪南宁愿为她搬运千万根沉重的圆木苦役也心甘情愿。两人的结合，成为全剧最圣洁的朝阳。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>十二年前，米兰公爵普洛斯彼罗因沉醉学术研究，被亲弟安东尼奥勾结那不勒斯国王阿隆索夺去公位，将他与三岁幼女米兰达塞入一条没有帆缆的破船推入茫茫大海。老忠臣贡萨罗暗中在船上放置了清水、衣物与公爵最珍视的魔法典籍。两人漂流至一座被女巫统治过的前哨孤岛。公爵凭借高超法术解救了被禁锢在树干中的精灵爱丽儿，收服了女巫的畸形儿子卡利班，成为海岛绝对主宰。十二年后，那不勒斯国王载着篡位弟安东尼奥、王弟塞巴斯蒂安及王子斐迪南等人参加完突尼斯公主婚礼乘船返航，恰好经过该岛海域。普洛斯彼罗命爱丽儿掀起遮天蔽日的暴风雨将战舰击碎，但依法保全全船人员毫发无损地分散冲上小岛。年轻王子斐迪南被爱丽儿的迷魂仙乐引至公爵洞穴，与米兰达一见钟情；普洛斯彼罗为考验其真心，故意刁难命其搬运数千根沉重木头苦役，斐迪南心甘情愿任劳任怨。与此同时，昏睡的国王险遭篡位弟安东尼奥与塞巴斯蒂安拔剑暗杀，被爱丽儿暗中唤醒挫败阴谋；粗鄙酒鬼水手斯丹法诺给卡利班灌饮烈酒，被野人奉为天神，密谋刺杀公爵夺岛，被爱丽儿用华服陷阱与灵犬狂吠驱散。当全体仇敌被施法困在结界迷宫中惊魂未定、神志昏乱时，普洛斯彼罗在爱丽儿的怜悯劝说下宣布弃绝复仇。他换上威严的米兰公爵朝服现身，揭穿叛逆罪行，宣布宽恕仇敌，迎出正在洞中甜蜜下棋的斐迪南与米兰达，使以为痛失爱子的阿隆索国王老泪纵横当场退还公位并结为秦晋之好。普洛斯彼罗履行誓言释放爱丽儿重归虚空自由，折断魔杖、将魔法书沉入大洋深处，等待次日清晨借着顺风归航意大利，向全人类舞台做终极深情谢幕。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃叩问的是<strong>“拥有绝对支配力量的人，如何战胜以牙还牙的复仇本能，通过主动放弃力量来达成更高维度的文明和解；以及人类如何走出被仇恨、野心与殖民控制撕裂的黑暗牢笼”</strong>。莎士比亚证明：暴力只能征服肉体，唯有宽恕才能救赎灵魂；人世间的一切功名与魔法皆如梦幻泡影，唯有仁爱与包容才能长存。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在仙乐缭绕的海岛迷雾中经历的风暴洗礼：在狂怒与杀机的巅峰时刻，见证一位白发宗师主动将复仇利刃化作漫天甘霖，在天地之间升华出人类所能达到的最从容宁静之境。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾遭受过重大背叛、手中拥有反击权力却在内心深处受尽仇恨煎熬，渴望学会以高贵姿态放下包袱、轻装前行的成年读者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>普洛斯彼罗手握绝对神罚力量之下的复仇烈火 vs 灵魂深处走向理性宽恕救赎的圣徒抉择；文明教化的傲慢征服 vs 原生态野性自尊的剧烈反抗。</strong></p>

      <div class="sub-heading">全书五幕经典推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 海难风暴与身世揭秘：</strong>雷电击裂桅杆，水手与王公贵族在海浪中哀嚎；米兰达痛惜求情，普洛斯彼罗解下法袍讲述十二年前被亲弟篡位的骨肉之仇；爱丽儿与卡利班分别出场。</li>
        <li><strong>第二幕 · 迷宫阴谋与烈酒降神：</strong>阿隆索国王为‘丧子’悲恸；安东尼奥拔剑欲弑君篡权被爱丽儿惊醒；小丑与酒鬼用朗姆酒收服野人卡利班，密谋刺杀公爵。</li>
        <li><strong>第三幕 · 搬木试炼与神宴幻象：</strong>斐迪南搬木甘之如饴，与米兰达立下婚誓，公爵在暗处含笑注视；爱丽儿化作鹰头怪兽掀翻海难贵族的假宴席，当众痛斥其十二年前弑兄天谴。</li>
        <li><strong>第四幕 · 众神假面舞会与恶搞叛徒：</strong>公爵召来天神为新人举办丰收丰饶面具幻象舞会；爱丽儿用华丽戏服设下诱饵，引恶犬撕咬追逐卡利班与酒鬼谋反三人组。</li>
        <li><strong>第五幕 · 宽恕大释怀与魔杖深沉：</strong>爱丽儿动情劝善，公爵宣布宽恕全体仇敌；折断魔杖、将书沉海；换公爵常服与国王相认；帘幕拉开新人下棋；释放爱丽儿；终场致辞乞求观众掌声解救灵魂。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第五幕第一场爱丽儿对公爵的动情进言：</strong>当爱丽儿汇报全体仇敌已经被魔法困在树林迷宫中动弹不得、老国王痛哭流涕时，这只精灵说：‘如果我是人类，我都会同情他们！’普洛斯彼罗听后深受震动：‘你是一只精灵，尚且懂得同情人类的苦难；我是一个血肉凡人，难道反倒比你更残忍？我选择美德，放下复仇！’这一瞬间，全剧从一场血腥的报复陷阱，彻底升华为了千古和解史诗。
      </div>"""

    sec05 = """      <div class="sub-heading">第四幕‘梦中的材料’：世界文学最恢弘的形而上幻灭</div>
      <p>第四幕第一场在神仙面具舞会突然消散后，普洛斯彼罗对惊恐的斐迪南说出的独白，被公认为莎士比亚一生的文学墓志铭：‘我们的狂欢已经结束了。我们这些演员，正如我曾经向你预告过的，全都是一些幽灵；他们已经化作稀薄的空气消失了。就像这出虚幻的戏剧一样，巍峨的高耸云端的宫殿、庄严的庙宇、甚至我们脚下这整座巨大的地球球体本身，以及地球上所有的一切，都将融化消散，就像刚才那场虚无的幻影一样，连一缕轻烟都不会留下！我们都是梦中的材料；我们微渺的一生，在沉睡中前后缠绕。’在这段传世独白中，莎翁将戏剧、魔法、帝国、战争与凡人的一生，全部消解为浩瀚宇宙中的短暂一梦，展现了最高维度的佛道通透境界。</p>

      <div class="sub-heading">终场致辞（Epilogue）：艺术家走出神坛的深深一躬</div>
      <p>全剧最后的二十行终场诗，是世界戏剧史上最让人潸然泪下的告白。此时舞台上所有演员已退场，大灯熄灭，年迈的莎士比亚（借普洛斯彼罗之身）独自一人留在空荡荡的舞台中央。他扔掉了魔杖，解除了法袍，对台下的观众轻声说道：‘现在，我的全部魔法都已经用尽了；我所剩的只有自己微弱的力量。既然我已经宽恕了所有伤害我的人，并重新夺回了我的公位，那么请不要让我留在这座孤岛上……解开我的咒符吧，唯有用你们仁慈的双手的掌声，才能释放我！’伟大的造梦者收起了神笔，像个孩子一样向人间祈求掌声的宽恕与接纳，将戏剧的仪式感推向了极致。</p>"""

    sec06 = """      <div class="sub-heading">融贯仙乐、歌谣与宫廷诗剧的至高语言熔炉</div>
      <p>《暴风雨》是莎士比亚晚年对英语音韵调度的绝对大师之作。爱丽儿唱出的歌谣（如《在五寻深处你的父亲躺卧》《蜜蜂吮吸的地方我也吮吸》）轻灵得如同一串随风飘荡的水晶风铃；而普洛斯彼罗召唤大自然精灵的独白，则犹如海啸般层层叠叠、雄浑肃穆。全书严格恪守古典戏剧的‘三一律’（事件发生在同一座小岛、时间严格控制在四个小时之内），在极小的时空骨架内爆发出了宇宙般的精神容量。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>折断的魔杖与沉海的魔法书 (The Broken Staff and Drowned Book)：</strong>全书至高哲学图腾。它象征着<strong>知识与超凡力量的持有者，最终敢于放弃对外部世界的强力掌控，回归平凡肉身、接纳生老病死自然规律的至圣定力</strong>。</li>
        <li><strong>五寻深处珍珠化的白骨 (Full Fathom Five)：</strong>爱丽儿向斐迪南唱出的挽歌：‘在五寻的海底，你的父亲白骨正在化作珊瑚，他的双眼正在化作两颗明珠。’它象征着<strong>人世间一切血腥痛苦的苦难，在时间的深海中终将发生‘海洋般的蜕变（A Sea-Change）’，沉淀为晶莹剔透的美德与智慧</strong>。</li>
        <li><strong>洞穴中的一局国际象棋：</strong>全书第五幕拉开帘幕时，斐迪南与米兰达正在对弈下棋。在外面，父辈们为了权力和领土杀得头破血流；在洞里，仇敌的孩子们却在棋盘上互相让子、含情脉脉。它象征着<strong>两代人的政治野心被年轻一代纯洁的爱意彻底消解降维</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（传奇魔法海岛剧）：</strong>被篡位的公爵在孤岛利用魔法掀起风暴诱捕仇敌，最终放下私仇促成儿女联姻、重返家园的大团圆传奇。<br>
        <strong>深层架构（政治与殖民反思寓言）：</strong>对欧洲大航海时代殖民扩张、权力更迭与启蒙专制的深刻反思。剖析文明教化与原生态野性自尊之间的深层断裂与弥合可能。<br>
        <strong>根本架构（宽恕即解脱的形而上救赎）：</strong>全人类面对仇恨的终极解药。证明复仇只是力量的低级炫耀，唯有主动放下执念选择宽恕，才能让受害者从自我禁锢的心灵孤岛中彻底脱困，重获生命的真正自由。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>英国诗人奥登在《长袍与魔杖》中指出：《暴风雨》是莎士比亚对整个西方文艺复兴人文主义理想所做的最终总结。普洛斯彼罗从最初沉迷书斋导致丢位，到后来凭借魔法控制一切，再到最后主动抛弃魔法重返人间负责，完成了一个知识分子从‘逃避现实’到‘迷信技术力量’再到‘以仁慈拥抱平凡现实’的伟大心智循环。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《暴风雨》在今天是一面照向现代科技与地缘政治的至圣明镜：<br>
      今天的人类掌握了核武器、基因工程、人工智能等堪比普洛斯彼罗当年呼风唤雨的‘超级魔杖’。我们面对着各种地缘冲突与历史恩怨。如果我们像当年的安东尼奥一样沉迷于弑兄夺权，或者像最初的普洛斯彼罗一样满脑子只想用超级力量将仇敌挫骨扬灰，文明只能在风暴中覆灭。《暴风雨》用四百年前的微弱声音提醒现代霸权：真正的伟大不在于你拥有多少摧毁敌人的弹药，而在于你是否有勇气折断傲慢的魔杖，给世界留下一片可以下棋的宁静洞穴。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>当你手中掌握了某个可以轻易让仇人或竞争对手当众出丑、甚至身败名裂的致命把柄时，你能否做到像普洛斯彼罗一样，在确认对方已经有所反省后，主动选择优雅放手？</li>
        <li>在你的人生经历中，是否有一项你曾经极度引以为傲、甚至当做自我身份全部依赖的‘特长或标签’？你是否有勇气在某个阶段主动放下它，做一个平和自在的普通人？</li>
        <li>面对社会上那些文化背景、行为举止与你截然不同甚至略显粗野的‘卡利班’们，你是否能收起傲慢的优越感，给予他们一份平等的聆听与尊重？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《暴风雨》是莎士比亚生前封笔的最后神作。一个被篡位的魔法老国王把所有仇人全骗到孤岛上，本来一挥手就能把他们全灭了，结果他听了一只小精灵的劝告，主动宣布原谅所有人，把魔杖折断扔进深海回老家当普通人。它告诉你：报复只是小孩的冲动，敢于拥有力量却主动选择宽恕，才是最高级的王者之风。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读莎士比亚一生艺术生涯的谢幕天鹅绝唱——《暴风雨》。如果说《哈姆雷特》是莎翁在青年时期的痛苦发问，《麦克白》是中年时期的惊悚挣扎，那么《暴风雨》就是这位伟大的老人在晚年看透一切之后的从容大和解。主角普洛斯彼罗原本是米兰公爵，十二年前被亲弟弟勾结外国国王篡位，差点被扔进海里淹死。但他懂魔法，带着三岁的女儿漂流到一座孤岛，成了全岛的岛主。十二年后，那帮仇人坐着大船正好路过小岛。公爵一挥魔杖，掀起漫天风暴把大船撕碎，把仇人们全抓到了岛上。在魔法结界里，仇人吓得浑身发抖，随时可以被他碎尸万段。然而，就在这大仇得报的最高潮时刻，全剧最神圣的一幕发生了：侍奉公爵的小精灵爱丽儿走过来，叹了口气说：‘公爵大人，如果我是个凡人，我都会可怜这帮仇敌。’白发苍苍的老公爵愣住了，他看着天空，突然大彻大悟：‘你一只没有肉身的精灵尚且懂得同情，我一个血肉凡人怎么能沉湎于仇恨？美德的真正崇高，不在于报复，而在于宽恕！’公爵走出山洞，没有杀一个人。他原谅了篡位的亲弟弟，把女儿嫁给了仇人的王子，两代人在棋盘前相视一笑。最震撼的是结局：公爵当着全宇宙的面，宣布折断自己的魔杖，把毕生修习的魔法书沉入最深的海底，他要彻底告别超能力，回老家踏踏实实做一个凡人。在空无一人的舞台上，莎士比亚借主角的嘴向台下深深鞠了一躬说：‘我的魔法全用完了，请用你们善良的掌声解救我吧！’读完这部戏你会热泪盈眶：人这一辈子最难的不是战胜对手，而是战胜自己内心的执念；敢于在拥有绝对力量时选择宽恕，才是人类能达到的最接近神明的时刻。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “去把仇恨的残篇沉入大洋深处吧；在岁月的辽阔航程中，唯有宽恕能为我们扬起平安归航的顺风。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：莎士比亚晚期传奇剧巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一幕第二场（海难风暴与身世诉说）：</strong>精读公爵向女儿讲述十二年前被亲弟篡位浮海奇迹生还的史诗开场。</li>
        <li><strong>必读第二场 · 第三幕第二场（卡利班的美妙音乐赞歌）：</strong>精读粗野怪人在草地上描绘‘岛上充满甜美声音’的绝妙诗篇，感受野性深处的诗意灵魂。</li>
        <li><strong>必读第三场 · 第四幕第一场（梦中的材料）：</strong>世界文学史最恢弘的存在主义幻灭独白，反复研磨‘大殿与地球皆将融化’的通透哲理。</li>
        <li><strong>必读第四场 · 第五幕第一场（折断魔杖与大宽恕）：</strong>精读爱丽儿劝善、公爵宣布将魔杖深埋地下数尺、将魔法书沉入深海的和解高潮。</li>
        <li><strong>必读第五场 · 终场致辞（Epilogue）：</strong>反复朗读莎翁最后二十行致辞，体会艺术家告别舞台时向人间祈求掌声的无上坦荡。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 宽恕与软弱的本质区别：</strong>普洛斯彼罗是在‘对方毫无反抗之力、自己完全手握绝对惩罚权’的压倒性优势下宣布宽恕的，这种宽恕与弱者无可奈何的妥协有何根本不同？
      </div>
      <div class="card-box">
        <strong>Q2 · 卡利班的诅咒之问：</strong>‘你们教我语言，我唯一的收获是学会了诅咒’，这句话为什么被列为后殖民主义文学最著名的反抗宣言？文明在教化未开化群体时常犯哪些傲慢错误？
      </div>
      <div class="card-box">
        <strong>Q3 · 折断魔杖的自愿缴械：</strong>在这个崇拜权力与掌控的世界上，为什么主动折断魔杖、放弃超凡特权需要比追求特权大一千倍的勇气？
      </div>
      <div class="card-box">
        <strong>Q4 · 棋局作为化解世仇的隐喻：</strong>为什么莎翁安排两个年轻人在洞中‘下国际象棋’而不是举行盛大阅兵？棋盘上的争斗与现实战场上的杀戮相比，展现了人类文明怎样的和平跃升？
      </div>
      <div class="card-box">
        <strong>Q5 · 虚妄之梦与当下生活：</strong>如果一切宫殿、庙宇乃至整座地球都不过是一场‘梦中的材料’，那人类当下认真生活、彼此相爱的行动还具有怎样的严肃意义？
      </div>"""

    sec13 = """      <div class="sub-heading">① 宽恕自愈实践工具：“普洛斯彼罗魔杖沉海法则” (The Prospero Staff-Burying Protocol)</div>
      <p><strong>适用场景：</strong>在家庭矛盾、旧日恩怨或团队纠纷中，你已经证明了对方的错误、完全占据了道德与理智的上风，但依然在心底紧咬着怨恨不放时。<br>
      <strong>第一步（确认胜利已了）：</strong>告诉自己：对方已经得到了教训，或者时间已经证明了你的清白，继续穷追猛打只会让自己沦为怨恨的囚徒；<br>
      <strong>第二步（举行物理断舍离仪式）：</strong>把记录那段恩怨的一封旧邮件、一张旧合影或一件让你烦躁的旧物件彻底撕碎或沉入垃圾桶，象征将‘魔杖折断沉海’；<br>
      <strong>第三步（从容回归人间）：</strong>微笑着走出房间，把全部精力投入到今天的下一盘棋、下一顿饭中，用你的平和告诉世界：你已经完成了对那段阴暗历史的彻底超越。</p>

      <div class="sub-heading">② 现实观察实验：“生活中的爱丽儿式提醒”</div>
      <p>观察身边某个常常表现出绝对自律、甚至有些冷酷苛刻的管理型朋友。在他即将对一个犯错下属进行严厉处分时，尝试用温和客观的口吻提醒他一句对方最近面临的家庭困难，观察这一抹同理心的介入是否能够化解一场冷酷的冲突。</p>

      <div class="sub-heading">③ 戏剧谢幕词仿写任务</div>
      <p>模仿第五幕普洛斯彼罗‘我们都是梦中的材料’那种以大自然宏大消解一切世俗名利执念的哲理诗句，写一段关于‘某位行业老兵在退休告别酒会上面对年轻人发表的从容致辞’（350字以内，不用官话套话，充满对岁月的感恩与通透）。</p>"""

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

print("Round 13 deep The Tempest ready.")

def get_deep_twelfth_night():
    data = {
        "title_cn": "第十二夜",
        "title_en": "Twelfth Night",
        "author_cn": "威廉·莎士比亚",
        "author_en": "William Shakespeare",
        "sub_desc": "狂欢节时期的性别错位喜剧巅峰 · 虚荣、痴情、荒诞恶作剧与音乐的狂喜盛宴",
        "hero_quote": "倘若音乐是爱情的食粮，那么奏下去吧！给我过量的音乐，让欲望因为过饱而生病，终于厌倦！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">剧作家</div><div class="spec-val">威廉·莎士比亚 (1564–1616)</div></div>
        <div class="spec-item"><div class="spec-label">创作年份</div><div class="spec-val">约 1601–1602 年 / 浪漫喜剧圆熟之作</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">狂欢节颠倒喜剧 / 性别错位浪漫剧</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">全五幕十八场 · 约 2 万词</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 终身必读经典文学</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">假面狂欢下的真情自律与清教徒虚伪伪善解构</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《第十二夜》仅仅看作一出女扮男装、阴差阳错的爆笑插科打诨闹剧。在伊利里亚王国那个如醉如狂的狂欢节外表下，莎翁极其敏锐地解剖了<strong>人类在爱情中的自恋与盲目——公爵爱的不是奥利维娅，而是沉溺在‘失恋贵族’角色里的自我感动；奥利维娅借口哀悼亡兄七年不见生人，却在见到男装小厮的第一秒就被打得溃不成军</strong>。更为深刻的是对清教徒管家马伏里奥的捉弄与监禁，在笑声深处投下了一抹极其冰冷的社会排他性阴影。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 薇奥拉身陷‘双重绝境’的传世假面独白：</strong>第二幕第二场。当奥利维娅派人送还假意遗落的戒指时，女扮男装的薇奥拉在月色下恍然大悟：‘我的主人疯狂爱着她，而可怜的我深爱着我的主人，她又糊里糊涂地爱上了虚假的我！男装啊，你真是一个害人的恶魔！’她以极高的智慧与忍耐，在克制中守护深情，成为莎翁笔下最聪慧的女性化身。
      </div>
      <div class="card-box">
        <strong>② 马伏里奥（Malvolio）黄色长袜十字绑带的疯狂自恋受骗记：</strong>第二部第五场花园恶作剧。女仆玛利亚伪造女主人笔迹留下情书，指使自命清高的管家‘穿黄色长袜、系十字交叉绑带、整天傻笑’。马伏里奥被虚荣野心彻底冲昏头脑，当真穿着荒唐怪服向女伯爵抛媚眼，被当成精神病人关入暗室，构成了世界戏剧史上对自负无趣的伪善者最残忍的讽刺。
      </div>
      <div class="card-box">
        <strong>③ 宫廷弄臣费斯特（Feste）游走全剧的清醒哲人歌声：</strong>全书真正的精神旁观者。他不疯，他的‘疯话’每一句都在扒光公爵与夫人的虚荣底裤。在第四幕他假扮神父隔门审讯马伏里奥，在终幕他独自留在空无一人的舞台上唱起那首带着雨雪萧瑟之感的古老民谣：‘下雨啊，每天都在下雨……’给整部狂欢喜剧注入了一抹挥之不去的沧桑挽歌韵味。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        圣诞节后第十二天的‘主显节之夜（Twelfth Night）’是欧洲传统的狂欢狂喜高潮。在这一夜，一切世俗尊卑秩序被暂时颠倒，仆人做主人，女子扮男儿。莎翁以此为舞台，展开了一场关于真爱的试炼。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .tn-box { rx: 8; stroke-width: 1.5; }
            .tn-bg-viola { fill: #2a9d8f; stroke: #40916c; }
            .tn-bg-orsino { fill: #1d3557; stroke: #2a4d7a; }
            .tn-bg-olivia { fill: #8c2d19; stroke: #a33b24; }
            .tn-bg-malvolio { fill: #242930; stroke: #59645f; }
            .tn-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tn-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .tn-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tn-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .tn-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .tn-green { stroke: #2a9d8f; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .tn-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="tn-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 核心枢纽：薇奥拉 (男装塞萨里奥) -->
          <rect x="230" y="25" width="220" height="120" class="tn-box tn-bg-viola" />
          <text x="340" y="52" class="tn-t-w">薇奥拉 (Viola · 塞萨里奥)</text>
          <text x="340" y="72" class="tn-t-sub-w">海难落单少女 · 女扮男装作书童</text>
          <text x="340" y="90" class="tn-t-sub-w">替公爵求爱情敌 · 内心深陷暗恋</text>
          <text x="340" y="108" class="tn-t-sub-w">以机敏克己之德守护双向真情</text>
          <text x="340" y="126" style="fill:#d8f3dc; font-size:10.5px; font-weight:700; text-anchor:middle;">“时间啊，唯有你才能解开这死结！”</text>

          <!-- 左侧：奥西诺公爵 (自我沉醉者) -->
          <path d="M 230 85 L 160 85" class="tn-solid" stroke="#1d3557" />
          <text x="195" y="75" class="tn-lbl" style="fill:#1d3557;">暗恋情愫</text>

          <rect x="15" y="30" width="145" height="110" class="tn-box tn-bg-orsino" />
          <text x="87" y="58" class="tn-t-w">奥西诺公爵</text>
          <text x="87" y="78" class="tn-t-sub-w">伊利里亚统治者</text>
          <text x="87" y="96" class="tn-t-sub-w">沉迷于失恋诗意</text>
          <text x="87" y="114" class="tn-t-sub-w">把书童当做知己</text>
          <text x="87" y="128" style="fill:#cad5e2; font-size:9.5px; text-anchor:middle;">终获真爱洞穿幻象</text>

          <!-- 右侧：奥利维娅伯爵小姐 (狂热沦陷者) -->
          <path d="M 450 85 L 520 85" class="tn-solid" marker-end="url(#tn-arr)" />
          <text x="485" y="75" class="tn-lbl">倒追男装</text>

          <rect x="520" y="30" width="145" height="110" class="tn-box tn-bg-olivia" />
          <text x="592" y="58" class="tn-t-w">奥利维娅女伯爵</text>
          <text x="592" y="78" class="tn-t-sub-w">誓言禁欲七年守丧</text>
          <text x="592" y="96" class="tn-t-sub-w">见塞萨里奥瞬间沦陷</text>
          <text x="592" y="114" class="tn-t-sub-w">错嫁孪生哥哥塞巴斯蒂安</text>
          <text x="592" y="128" style="fill:#f0dcd8; font-size:9.5px; text-anchor:middle;">打破虚伪禁欲戒律</text>

          <!-- 下方：小丑恶作剧与马伏里奥被整 -->
          <path d="M 340 145 L 340 200" class="tn-solid" marker-end="url(#tn-arr)" />
          <rect x="160" y="200" width="360" height="115" class="tn-box tn-bg-malvolio" />
          <text x="340" y="228" class="tn-t-w">狂欢节小丑恶作剧：清教徒管家马伏里奥之辱</text>
          <text x="340" y="248" class="tn-t-sub-w">托比爵士、安德鲁爵士、玛利亚伪造求爱信 · 假情书诱入圈套</text>
          <text x="340" y="266" class="tn-t-sub-w">黄色长袜与十字交叉绑带 · 关进暗室指为疯癫 · 费斯特假扮神父戏耍</text>
          <text x="340" y="284" class="tn-t-sub-w">终场愤愤离去：‘我要向你们整帮人报复到底！’ · 狂欢背后的残酷阴影</text>
          <text x="340" y="300" style="fill:#a8dadc; font-size:10.5px; font-weight:700; text-anchor:middle;">小丑独留舞台唱响‘每天都在下雨’的沧桑民谣</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>薇奥拉（Viola）：</strong>莎士比亚喜剧中最兼具智慧与深情的女主角。海难落单、举目无亲，她没有坐在沙滩上哭泣，而是穿上男装保护自己，靠谈吐与音乐才华进入公爵府邸。面对自己深爱的公爵让她去向另一个女人求爱的高难度折磨，她恪尽职守、言辞恳切，不仅没有从中作梗破坏，反而用极高的文学才华打动了女伯爵。当公爵误以为她背叛想要杀她时，她平静地说：‘我甘愿一千次为你赴死，如果这能让你感到一丝安宁！’这种无私坦荡的高贵灵魂，使她成为全剧唯一的道德指南针。</li>
        <li><strong>奥西诺公爵（Orsino）：</strong>典型的‘爱情自恋狂’。他开篇躺在花丛中听音乐，沉浸在‘求而不得’的痛苦幻觉中。他爱的不是奥利维娅的具体灵魂，而是自己作为一个失恋深情诗人的高雅人设。当薇奥拉向他讲述一个‘暗中相爱、像墓碑雕像般默默消瘦憔悴的少女’的故事时，公爵被深深触动却毫无察觉那正是身旁的薇奥拉。直到终局发现薇奥拉的女儿身，他瞬间从虚无的单相思中醒来，迎娶了真正陪伴自己灵魂的知己。</li>
        <li><strong>马伏里奥（Malvolio）：</strong>清教徒伪善势利的最绝妙代表。他作为管家，整日对狂饮作乐的托比爵士指手画脚，自诩道德高尚不近女色；然而在花园捡到假情书时，他内心深处的权力野心与阶层跃迁狂欲瞬间暴露无遗——他立刻幻想自己成为‘奥利维娅伯爵，穿着天鹅绒长袍，把托比召来厉声训斥’。他的悲剧在于他的缺乏幽默感与极端自负，成为狂欢节文化无情嘲弄与驱逐的替罪羊。</li>
        <li><strong>费斯特（小丑 Feste）：</strong>看穿一切人世荒诞的清醒歌者。他靠嘲弄世人维生，公爵称他是‘一个聪明的傻子’。他敢于当面斥责奥利维娅：‘你既然笃信你哥哥的灵魂已经升入天堂，那你为什么还要天天为他披麻戴孝大哭？你才是真正的傻子！’他的歌声凄美动人，每一次出场都将浅薄的打闹升华到了对时光飞逝、青春易老的哲学沉思。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>孪生兄妹塞巴斯蒂安与薇奥拉在伊利里亚海域遭遇特大海难，彼此以为对方已经葬身大海。获救上岸的少女薇奥拉女扮男装化名‘塞萨里奥’，投奔当地统治者奥西诺公爵担任侍从书童。公爵苦苦暗恋为亡兄守丧发誓七年不见男人的奥利维娅女伯爵，派容貌清秀、言辞动人的塞萨里奥前去替自己登门提亲求爱。不料奥利维娅不仅没有接受公爵，反而在面纱揭开的一瞬间被男装的塞萨里奥深深迷住，设计送还戒指展开疯狂倒追；而朝夕相伴中，薇奥拉已不可自拔地深爱上了自己的主人公爵，陷入前所未有的三角错位死结。在伯爵公馆里，傲慢刻薄的清教徒大管家马伏里奥因干涉托比爵士与小丑们的深夜饮酒狂欢激起公愤。机灵女仆玛利亚伪造了一封女伯爵的情书扔在花园小径上，诱骗马伏里奥穿上黄色长袜、系十字绑带、当面向女主人傻笑示爱。马伏里奥中计发狂，被众人当成恶魔附体的疯子关入暗室受尽小丑戏弄。此时，海难生还的孪生哥哥塞巴斯蒂安在海盗船长安东尼奥的护送下抵达成邦，由于容貌与男装妹妹完全一模一样，引发了一连串惊天大误会：托比爵士将其误认为懦弱的塞萨里奥拔剑决斗却被痛揍，奥利维娅将其误认为心上人拉入教堂当场完婚，公爵更误以为是侍童背叛自己夺爱拔剑欲杀。就在危机爆发的最高潮，两兄妹在广场上当场相认，谜团瞬间解开——奥利维娅欢喜接纳了勇敢英俊的哥哥，公爵猛然识破身旁书童正是深爱自己已久的女儿身薇奥拉，当场牵手立下婚约。获释的马伏里奥愤恨发誓‘向整帮人复仇到底’拂袖而去，全场在婚礼的盛大欢歌中闭幕，唯有小丑费斯特留在大雨磅礴的舞台上唱响人世风霜民谣。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类在盲目的激情与自我感动的迷思中，如何凭借时间的沉淀与真诚的自律，穿透性别假面与虚荣幻影，找回对真实心灵的辨识与接纳”</strong>。莎士比亚证明：爱情无法被人工设计，越是严苛的戒律越容易在欲望面前溃败；而唯有抱持无私善意、愿意等待时间自然解开死结的人，才能在狂欢落幕后赢得持久的安稳。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在伊利里亚海风与欢快鲁特琴声中穿行的假面狂欢：在令人捧腹的性别错位与恶作剧大笑背后，体会人类情感超越外表形式的深邃自由与岁月流逝的淡淡怅惘。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾在单相思中自我感动、被虚伪自负困锁心智，渴望在幽默与笑声中卸下面具、勇敢追求真性情的现代青年。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以薇奥拉为代表的真诚自律隐忍之爱 vs 以公爵和奥利维娅为代表的虚妄自我陶醉；狂欢节的自由天性 vs 清教徒马伏里奥代表的僵化道德伪善。</strong></p>

      <div class="sub-heading">全书五幕经典狂欢推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 音乐食粮与男装假面：</strong>公爵长叹‘倘若音乐是爱的食粮’；海难上岸，薇奥拉换上男装；替公爵首次赴伯爵府提亲，奥利维娅揭开面纱一见倾心。</li>
        <li><strong>第二幕 · 戒指暗号与花园伪信：</strong>女伯爵命管家送还戒指设套；薇奥拉对月长叹时间之结；托比与小丑深夜纵酒；玛利亚伪造求爱信扔入花径。</li>
        <li><strong>第三幕 · 黄袜十字绑带与决斗闹剧：</strong>马伏里奥当众着黄袜傻笑被视作疯癫；塞巴斯蒂安进城；安德鲁爵士在挑唆下与塞萨里奥决斗，两人吓得浑身发抖险象环生。</li>
        <li><strong>第四幕 · 疯人暗室与教堂闪婚：</strong>小丑假扮神父隔门戏弄马伏里奥；哥哥塞巴斯蒂安误撞奥利维娅，顺水推舟被拉进礼拜堂闪电订婚。</li>
        <li><strong>第五幕 · 孪生相认与小丑雨歌：</strong>公爵翻脸欲杀‘背叛者’；双生子当庭并立震惊全场；马伏里奥发誓复仇；两桩神圣婚约达成，小丑独留舞台唱响‘每天都在下雨’终曲。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第五幕第一场孪生兄妹塞巴斯蒂安与薇奥拉并肩站在广场上：</strong>全剧最大的死结在瞬间被物理瓦解。公爵惊呼‘一张脸、一副身材、一种声音，却分成了两个人，这是自然界的奇妙幻象！’奥利维娅发现自己错嫁的正是自己心爱之人真正的男儿之身，公爵发现自己最贴心的侍从正是可以终生相托的贤妻。狂欢节的假面在此刻神圣归位。
      </div>"""

    sec05 = """      <div class="sub-heading">薇奥拉的‘墓碑之爱’独白：世界戏剧最动人的暗恋自白</div>
      <p>第二幕第四场，当公爵自吹自擂‘男人的爱比女人更深沉狂烈’时，男装的薇奥拉忍不住反唇相讥，向公爵讲述了自己‘虚拟妹妹’的一段深情往事：‘她从不向人吐露她的爱情，她让相思像一朵被蛀虫侵害的花蕾，悄悄吞噬她桃红色的脸颊。她在痛苦中消沉，整日微笑着坐在石头上注视着悲哀，宛如墓碑上雕刻的耐心忍耐女神。难道这不是真正的爱吗？我们男人发誓发得最响，但真到了行动上，我们的誓言往往只是一阵风，远不如女人的爱来得真诚而持久！’这段话把暗恋写到了无上圣洁的境界——爱不是霸道的占有与索取，而是宁愿自己化作墓碑雕像也要守护对方平安的深沉沉默。</p>

      <div class="sub-heading">马伏里奥之辱：狂欢节对清教徒秩序的报复与悲剧余响</div>
      <p>许多现代评论家敏锐地指出：第四幕众人把马伏里奥关进漆黑小地牢、让小丑装神弄鬼假扮神父逼他承认‘灵魂可以转世成野鸭子’的桥段，已经跨越了善意恶作剧的边界，带有一种令人不安的残酷私刑色彩。马伏里奥固然自私刻薄，但他作为管家恪尽职守。他在最后一幕气得发抖喊出‘我要向你们整帮人报复到底！’的遗言，极具历史预言性——整整四十年后，受到压迫的清教徒军团斩首了查理一世，关闭了全英所有的剧院，以最残酷的形式报复了当年狂欢剧场对他们的嘲弄。</p>"""

    sec06 = """      <div class="sub-heading">抒情诗、双关语与民间醉歌的复调狂欢文风</div>
      <p>《第十二夜》展现了莎士比亚在喜剧语言上极其丰富的光谱层次：既有第一幕公爵那种带有纯正十四行诗格律的高雅抒情独白，又有小丑费斯特充满哲学智慧的悖论双关语，更有托比爵士与马夫们在后半夜拍着酒桶高唱的粗俗祝酒歌。语言充满了节日啤酒泡沫般的欢快弹跳感，与结尾民谣的苍凉形成绝妙张力。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>黄色长袜与十字交叉绑带 (Yellow Stockings and Cross-Gartered)：</strong>荒诞虚荣的最滑稽视觉符号。黄色是奥利维娅最厌恶的颜色，十字绑带是老气横秋的过时穿法。让一个刻板管家穿上它狂笑，象征着<strong>欲望一旦脱离自知之明，必将把人降维为最滑稽的小丑</strong>。</li>
        <li><strong>遗落又送还的戒指 (The Lost Ring)：</strong>女伯爵掩饰主动追求的隐蔽借口。它在主仆、男女之间流转，象征着<strong>爱情的降临往往借由不可名状的偶然误会完成对世俗防线的突破</strong>。</li>
        <li><strong>舞台上无休止的细雨与风 (The Wind and the Rain)：</strong>终幕小丑反复歌唱的意象。‘任凭世界有多荒唐，大雨啊每天都在下。’它象征着<strong>狂欢的酒宴终会散场，凡人终将回归冷酷风雨人间的永恒自然现实</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（浪漫节日错位喜剧）：</strong>海难失散的双胞胎兄妹在异邦由于女扮男装引发三角错恋，众人设计捉弄刻薄管家，最终大团圆成婚的庆典大戏。<br>
        <strong>深层架构（欲望自恋与心智成熟）：</strong>对人类打着爱情幌子行自我迷恋之实的系统解构。证明未经历练的单相思只是一场自私的梦游，唯有在真实互动中完成相互关照与自制，爱才不致沦为荒唐闹剧。<br>
        <strong>根本架构（人生的狂欢与世俗现实归宿）：</strong>狂欢节颠倒机制的哲学隐喻。颠倒世俗秩序能够释放被压抑的生命元气，但狂欢之后必须学会从容回归有秩序、有责任、有担当的平凡日常。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>著名莎学泰斗哈罗德·布鲁姆在《西方正典》中高度评价《第十二夜》：“这是莎士比亚最完美的喜剧高山，其艺术完整度超越了《皆大欢喜》。小丑费斯特是全剧真正的主宰，他的忧郁唱词赋予了整部闹剧一种只有最高级的天才才能调配出的形而上神韵。”</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《第十二夜》在今天的性别流动、网络伪装与恋爱脑现象中依然是一针清醒剂：<br>
      多少年轻人在恋爱中如同当年的奥西诺公爵与奥利维娅，整天发着矫揉造作的朋友圈感叹‘为爱受尽折磨’，其实只是在爱着那个‘沉迷深情人设的自己’；而网络上那些戴着各种假面滤镜、在虚拟人设中寻找快感的人，正如当年沉迷男装的薇奥拉。莎翁提醒我们：面具可以防身，但真情必须以真面目示人；不要做自恋的马伏里奥，学会用幽默与真诚拥抱真实的生活。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你过去的某段暗恋经历中，你所迷恋的究竟是那个真实、有缺点的活人，还是你脑海中自行美化出来的‘完美公爵或伯爵’？</li>
        <li>当你为了保护自己或为了职场需要佩戴某种‘假面’时，你是否有足够的清醒，不让这副面具反过来侵蚀你的真实性格？</li>
        <li>面对身边那些性格严肃、不懂幽默、有时甚至有些讨厌的‘马伏里奥式’同事，我们该如何划定开玩笑与恶意霸凌的清晰界限？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《第十二夜》是莎士比亚最好看的爱情轻喜剧。双胞胎兄妹海难失散，妹妹女扮男装去给大帅哥公爵当书童，替公爵去追富婆，结果富婆爱上了男装的妹妹，妹妹却爱上了公爵！最后双胞胎哥哥一出现，全场原地结拜大团圆。它告诉你：爱情不讲道理，但唯有真诚等待，时间自会解开所有的死结。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读莎士比亚浪漫喜剧的至高王冠《第十二夜》。书名里的‘第十二夜’，指的是西方圣诞节后第十二天的狂欢之夜，在这一天，所有人都要戴上面具颠倒身份，仆人扮国王，女人扮男人。故事发生在一个充满音乐的世外桃源伊利里亚王国。女主角薇奥拉在海难中和孪生哥哥失散，为了在异乡自保，她剪短头发穿上男装，去给大帅哥奥西诺公爵当书童。公爵整天躺在花丛里听歌，说出了一句名垂青史的开场白：‘倘若音乐是爱的食粮，那就奏下去吧！’公爵自以为深爱着高冷的女伯爵奥利维娅，派男装的薇奥拉去当月老替自己表白。结果神转折来了——女伯爵一掀面纱，居然不可救药地倒追爱上了男装的薇奥拉！而薇奥拉呢，在天天陪公爵聊天中，早已在心里爱死了公爵！这时候，整个大宅里还上演了一出极其爆笑的捉弄戏：那个道貌岸然、整天管闲事的保守派大管家马伏里奥，捡到了一封假情书，以为女伯爵暗恋自己，居然真的穿上骚气的黄色长袜、系上十字绑带当众冲女主人抛媚眼，被全场当成疯子关进地牢！最后，那个大难不死、长得跟妹妹一模一样的亲哥哥塞巴斯蒂安进城了。女伯爵迎面撞上英俊的哥哥，一把拉进教堂当场闪婚；公爵看着两个一模一样的兄妹惊呆了，终于看清身旁的书童是个姑娘，当场单膝跪地求婚。两对新人欢欢喜喜办大婚。最后所有演员退场，唯独那个看透一切的白胡子小丑留在舞台上，在漫天大雨里唱起了那首沧桑的歌：‘下雨啊，每天都在下雨……’莎士比亚用这出戏告诉我们：在这个荒唐又美丽的世界上，每个人都在戴着面具演戏；但只要你的心底保留着无私的善良，时间这个最高明的编剧，自会把属于你的真爱送进你的怀抱。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “时间啊，全靠你来解开这团乱麻了，这不是我柔弱的心智所能解决的死结；无论世界的雨雪多么凄迷，真诚的人终将在破晓相逢。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界错位喜剧巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一幕第一章（音乐是爱的食粮）：</strong>精读公爵开篇华彩抒情长篇，体会莎翁关于‘爱情自恋狂想’的精妙白描。</li>
        <li><strong>必读第二场 · 第二幕第二场（戒指与时间之结）：</strong>精读薇奥拉在月色下恍然大悟、对月抒怀的经典假面独白。</li>
        <li><strong>必读第三场 · 第二幕第五场（花园拾假情书）：</strong>世界戏剧史最经典的恶作剧场次，细读马伏里奥在虚荣中一步步咬上诱饵的滑稽心理。</li>
        <li><strong>必读第四场 · 第五幕第一场（双生子大相认与小丑终曲）：</strong>精读全剧大解结高潮，以及小丑在大雨中的传世谢幕歌谣。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 奥西诺公爵的爱是否廉价？</strong>公爵前一秒还在为奥利维娅寻死觅活，后一秒得知薇奥拉是女儿身立刻宣布娶她。这种光速移情是荒唐可笑，还是说明他终于从虚妄的单相思中醒悟、拥抱了真实生活？
      </div>
      <div class="card-box">
        <strong>Q2 · 奥利维娅的闪婚心理：</strong>女伯爵甚至连塞巴斯蒂安的真实名字都不知道，仅仅凭着对方长着一张和薇奥拉一模一样的脸就拉去礼拜堂成婚，这种爱在本质上是一种怎样的盲目？
      </div>
      <div class="card-box">
        <strong>Q3 · 恶作剧的道德边界：</strong>众人把马伏里奥关进暗室、让小丑扮神父折磨他，这种整蛊在多大程度上超越了恶作剧的善意，变成了对一个不合群者的集体霸凌？
      </div>
      <div class="card-box">
        <strong>Q4 · 薇奥拉的隐忍智慧：</strong>面对双重两难死锁，薇奥拉没有去揭穿假面大吵大闹，而是把一切交给‘时间’。这种‘以无为胜有为’的定力在今天具有怎样的现实借鉴价值？
      </div>
      <div class="card-box">
        <strong>Q5 · 小丑雨歌的苍凉底色：</strong>为什么在一场皆大欢喜的浪漫喜剧大团圆之后，莎翁一定要让小丑留在大雨中唱一首沧桑凄凉的歌来收尾？</div>"""

    sec13 = """      <div class="sub-heading">① 情绪脱困实践工具：“薇奥拉时间解结法则” (The Viola Patience Protocol)</div>
      <p><strong>适用场景：</strong>当你身处一个错综复杂、多方利益严重死锁、无论你怎么解释辩白都会越描越黑的被动绝境时。<br>
      <strong>第一步（承认局限）：</strong>像薇奥拉一样坦白：‘这不是我微弱的心智现在能够用嘴皮子强行解开的死结’，停止一切画蛇添足的自辨；<br>
      <strong>第二步（恪守本分）：</strong>在迷局彻底清晰前，只做好你眼前岗位上最核心、最无可挑剔的本职工作，用无懈可击的品格维持信誉底盘；<br>
      <strong>第三步（把舞台交给时间）：</strong>静坐常思，让各方利益在时间的自然发酵中暴露真实面目。记住：生活是一场大戏，最大的翻盘往往来自你意料之外的‘那个孪生哥哥的入场’。</p>

      <div class="sub-heading">② 现实观察实验：“狂欢节效应与职场假面”</div>
      <p>观察一次公司年会或朋友聚会派对。记录人们在饮酒、音乐和游戏放松时，与平日里在正式办公室里展现出的截然相反的肢体语言与笑语，反思‘社会规训面具’对人类本能活力的长期压制。</p>

      <div class="sub-heading">③ 浪漫喜剧对白仿写任务</div>
      <p>模仿第一幕第五场薇奥拉替公爵向女伯爵提亲那种充满机智双关、不卑不亢、在赞美中暗藏锋芒的典雅对白风格，写一段关于‘一个职场实习生在向一位极其挑剔傲慢的高管汇报方案’的三百字交锋对话（优雅从容、寸步不让）。</p>"""

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

print("Round 13 deep Twelfth Night ready.")

def get_deep_julius_caesar():
    data = {
        "title_cn": "尤利乌斯·恺撒",
        "title_en": "Julius Caesar",
        "author_cn": "威廉·莎士比亚",
        "author_en": "William Shakespeare",
        "sub_desc": "政治心理与修辞操纵的无上教科书 · 共和挽歌、刺杀阴谋与民意风暴的史诗巨构",
        "hero_quote": "不是我不爱恺撒，而是我更爱罗马！当崇高的理想主义向现实盲动妥协，刺向独裁者的利刃，往往会撕开更深重的血腥暴政地狱。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">剧作家</div><div class="spec-val">威廉·莎士比亚 (1564–1616)</div></div>
        <div class="spec-item"><div class="spec-label">创作年代</div><div class="spec-val">约 1599 年 / 环球剧场落成大戏</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">罗马历史悲剧 / 政治辩论剧 / 心理史诗</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">全五幕十八场 · 约 1.9 万词精悍诗剧</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 青年与政治哲学通识必读</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">道德动机与政治后果背离机制及群体心理修辞操纵深度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把本剧简单看作‘正义刺客铲除暴君’的好莱坞英雄反抗片，更不要将布鲁图斯或恺撒单方面脸谱化。莎士比亚以极其冷酷的政治现实主义目光，揭示了世界政治史上最深沉的悲剧法则：<strong>最可怕的历史灾难与流血内战，往往不是由十恶不赦的恶棍发动的，而是由布鲁图斯这样道德纯洁、满怀崇高共和理想、但政治上极度幼稚自负的理想主义书生一手促成的</strong>。刺杀恺撒没有拯救罗马共和国，反而直接催生了更加专制血腥的屋大维罗马帝国。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 元老院议事堂二十三刀刺杀恺撒的惊天惊悚瞬间：</strong>第三幕第一场。恺撒在拒绝赦免元老亲属、狂妄自比为‘北极星般恒常不可动摇’的巅峰时刻，密谋者一拥而上拔刀乱刺。当看到自己最信任、待若亲子的布鲁图斯也拔出短剑刺向自己时，这位横扫欧亚的统帅彻底放弃了挣扎，拉紧长袍遮住面庞发出千古悲叹：‘还有你吗，布鲁图斯？（Et tu, Brute?）那么恺撒，倒下吧！’
      </div>
      <div class="card-box">
        <strong>② 安东尼在恺撒葬礼上颠倒乾坤的传世广场演说：</strong>第三幕第二场是世界修辞学与群众心理学无可逾越的高峰。布鲁图斯刚用枯燥理性的哲学逻辑说服了暴民‘为了罗马自由必须杀恺撒’；紧接着安东尼登台，以‘布鲁图斯是一个正派人’这句看似顺从的反讽套话起步，一步步展示恺撒的血衣、指出每一个刀口的刺杀者、宣读恺撒给每个公民分发七十五便士的遗嘱，瞬间将成千上万原本欢呼自由的暴民煽动成狂怒的火海，点燃了内战的燎原烈火。
      </div>
      <div class="card-box">
        <strong>③ 萨第斯军营大帐中的兄弟争吵与恺撒幽灵现身：</strong>第四幕第三场。在腓立比决战前夕，刺杀首领布鲁图斯与卡西乌斯在营帐里为了钱粮军饷和道德纯洁发生极其激烈的拔剑争吵，随后在对波西娅自杀的同哀中和解。深夜烛光跳动，恺撒巨大的幽灵现身大帐，冷冷宣告：‘腓立比，我们将再次相会！’展现了弑君者内心深处挥之不去的宿命鬼影。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        公元前44年罗马共和国晚期。贵族寡头元老院体制在恺撒的军事威望面前名存实亡，面临向帝制独裁转型的历史巨大裂隙。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .jc-box { rx: 8; stroke-width: 1.5; }
            .jc-bg-caesar { fill: #8c2d19; stroke: #a33b24; }
            .jc-bg-brutus { fill: #1d3557; stroke: #2a4d7a; }
            .jc-bg-antony { fill: #242930; stroke: #59645f; }
            .jc-bg-crowd { fill: #fbf9f4; stroke: #1c221e; stroke-width: 2.2; }
            .jc-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .jc-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .jc-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .jc-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .jc-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .jc-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .jc-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="jc-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 独裁君王：尤利乌斯·恺撒 -->
          <rect x="20" y="25" width="210" height="115" class="jc-box jc-bg-caesar" />
          <text x="125" y="52" class="jc-t-w">尤利乌斯·恺撒 (Caesar)</text>
          <text x="125" y="72" class="jc-t-sub-w">终身独裁官 · 战无不胜 · 傲慢自负</text>
          <text x="125" y="90" class="jc-t-sub-w">自比北极星 · 蔑视凶兆预言</text>
          <text x="125" y="108" class="jc-t-sub-w">元老院二十三刀倒毙于庞培雕像下</text>
          <text x="125" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">“还有你吗，布鲁图斯？倒下吧！”</text>

          <!-- 共和刺客首领：布鲁图斯 -->
          <rect x="450" y="25" width="210" height="115" class="jc-box jc-bg-brutus" />
          <text x="555" y="52" class="jc-t-w">马库斯·布鲁图斯 (Brutus)</text>
          <text x="555" y="72" class="jc-t-sub-w">‘最尊贵的罗马人’ · 斯多葛哲人</text>
          <text x="555" y="90" class="jc-t-sub-w">为了抽象共和自由弑杀挚友君王</text>
          <text x="555" y="108" class="jc-t-sub-w">政治幼稚：允安东尼演说犯下致命错</text>
          <text x="555" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">理想主义在现实政治中的惨烈败亡</text>

          <!-- 刺杀行动连线 -->
          <path d="M 450 82 L 230 82" class="jc-solid" marker-end="url(#jc-arr)" />
          <text x="340" y="74" class="jc-lbl">三月十五日 · 元老院刺杀</text>

          <!-- 现实权谋大师：马克·安东尼 -->
          <rect x="235" y="140" width="210" height="80" class="jc-box jc-bg-antony" />
          <text x="340" y="168" class="jc-t-w">马克·安东尼 (Mark Antony)</text>
          <text x="340" y="188" class="jc-t-sub-w">恺撒爱将 · 广场修辞操纵大师</text>
          <text x="340" y="204" style="fill:#e0e4e8; font-size:9.5px; text-anchor:middle;">‘布鲁图斯是一个正派人’绝妙反讽煽动</text>

          <!-- 下方：罗马盲从暴民与内战屠场 -->
          <path d="M 340 220 L 340 250" class="jc-solid" marker-end="url(#jc-arr)" />
          <rect x="160" y="250" width="360" height="75" class="jc-box jc-bg-crowd" />
          <text x="340" y="275" class="jc-t-d">罗马广场暴民与腓立比决战 (Philippi)</text>
          <text x="340" y="295" class="jc-t-sub">被修辞轻易玩弄的乌合之众 · 焚烧刺客房屋 · 错杀无辜诗人辛纳</text>
          <text x="340" y="310" style="fill:#8c2d19; font-size:10px; font-weight:700; text-anchor:middle;">刺客自刎沙场，帝制以更血腥的形式加冕</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>布鲁图斯：</strong>古往今来最受尊敬也最让人扼腕叹息的政治悲剧典型。他恪守斯多葛学派哲学，生活极度清廉自律。安东尼在全剧结尾向他的遗体由衷致敬：‘所有刺客中，只有他一个人不是出于对恺撒的妒忌，而是纯粹出于对公众自由的大公无私！’然而正是这种道德上的‘圣徒自恋’，毁掉了整个罗马——他盲目相信理性演讲能说服暴民，他不准杀掉危险的安东尼，他甚至允许安东尼在葬礼上发表公众演讲。他在现实政治中的每一次‘宽宏大度’，都在为共和国掘下更深的坟墓。</li>
        <li><strong>尤利乌斯·恺撒：</strong>世界帝王气象与凡人生理残缺并存的矛盾体。他征服高卢、踏平庞培，在罗马平民中拥有神一般的威望；但他身上带有明显的癫痫、左耳失聪与对阿谀奉承的隐秘沉迷。他明知三月十五日（Ides of March）有大凶预言，明知妻子昨夜梦见他的塑像涌出鲜血，但为了维护自己‘恺撒比危险本身更危险’的无敌神话，他依然昂首步入元老院，在被刺二十三刀后轰然倒塌在旧敌庞培雕像的基座下。</li>
        <li><strong>马克·安东尼：</strong>冷酷精密的政治实用主义天才。在恺撒死后，他面对满手鲜血的刺客元老，当场与他们握手称兄道弟，麻痹对方；转身面对恺撒的尸体，却流下了真诚复仇的眼泪，发誓要让‘意大利大地充斥血雨腥风’。在葬礼上，他将修辞学技巧运用得如同神迹，把一群支持刺杀的民众在一刻钟内煽动为烧毁刺客住宅的暴民。他是现代大众政治传播学当之无愧的祖师爷。</li>
        <li><strong>卡西乌斯（Cassius）：</strong>敏锐精明的政治密谋核心。他生性阴鸷消瘦，恺撒一眼就看穿他‘想得太多，这样的人是危险的’。他策划了整个刺杀阴谋，多次提出极其精准的战略建议（‘必须把安东尼和恺撒一同杀掉’、‘绝不能让安东尼公开发表葬礼演说’、‘不要贸然出击腓立比平原’）。然而每一次，他的现实智慧都在布鲁图斯崇高名望的固执坚持下一一退让，最终在误报军情的绝望中命仆人将自己刺死。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>公元前44年罗马城，战无不胜的执政官恺撒击溃庞培余党凯旋归来，全城民众如痴如狂涌上街头欢庆。在牧神节狂欢中，一个盲人预言家穿过人群警告恺撒：‘当心三月十五日！’恺撒斥其为疯子置之不理。安东尼三次在广场向恺撒献上王冠，恺撒三次推辞但眼神充满留恋。痛恨独裁的元老卡西乌斯秘密拉拢最受全罗马尊敬的贵族布鲁图斯入伙密谋，伪造大量平民请愿书投进布鲁图斯书房，终于以‘保卫罗马共和自由’的崇高大义说服了布鲁图斯领衔刺杀。三月十五日早晨，恺撒之妻因凶梦劝其留家，密谋者德基乌斯巧言令色将其诱骗至元老院议事堂。在众元老借故陈情围拢之后，卡斯卡率先拔刀，密谋者二十三刀将其刺倒在庞培雕像前，布鲁图斯的最后一刀彻底击碎了恺撒的抵抗意志。刺杀成功后，布鲁图斯不顾卡西乌斯反对，不仅赦免了安东尼，更准许安东尼在广场发表葬礼演说。布鲁图斯在讲台上以‘不是我不爱恺撒，而是我更爱罗马’的理性哲学赢得了平民的掌声；然而紧接着登台的安东尼，手抚恺撒带血的长袍，用绝妙的反讽与公布遗嘱的煽动，将罗马平民煽动成狂怒的火海，暴民四处纵火追杀刺客，无辜诗人辛纳仅仅因为与刺客同名就被当街撕成碎片。布鲁图斯与卡西乌斯仓皇逃出罗马建立军团；安东尼与年轻的屋大维、雷必达组成后三头同盟，在罗马展开残酷的清洗大屠杀。一年后，在希腊腓立比平原决战前夕，恺撒的幽灵在夜半大帐中向布鲁图斯现身预言死期。决战爆发，卡西乌斯误判战局伏剑自刎；布鲁图斯在败局已定时，坦然命侍从握剑、自己迎剑自戕。安东尼与屋大维在遗体前肃立致敬，称其为‘全罗马最尊贵的人’，一场旨在捍卫共和的刺杀，最终在罗马帝国的大一统加冕中彻底收场。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“崇高的道德理想主义在冷酷现实政治面前的必然挫败，以及语言修辞如何操纵乌合之众的狂热盲从”</strong>。莎士比亚向全人类证明：政治是一门依靠力量对比、人性洞察与组织纪律运作的残酷艺术；缺乏现实政治智慧的‘道德圣洁’，不仅拯救不了自由，反而会把文明推向更加嗜血的全面专制深渊。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在罗马元老院血泊与万人广场演说中徐徐展开的政治解剖大戏：在纯粹的刀光剑影与字字千钧的修辞攻防战中，见证高尚的理想主义者如何亲手将自己送上历史的断头台。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个热衷政治辩论、崇尚理想主义情怀，渴望看穿现代大众媒体修辞煽动话术与政治博弈深层残酷规律的深度思考者。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以布鲁图斯为代表的抽象古典共和自由理想与道德洁癖 vs 以恺撒、安东尼为代表的历史集权大势、民众现实利益诉求与修辞政治现实主义。</strong></p>

      <div class="sub-heading">全书五幕史诗政治推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 狂欢节预言与密谋织网：</strong>罗马街头市民为恺撒狂欢；三月十五日预言初现；卡西乌斯在暴风雨之夜引诱布鲁图斯；雷电劈裂神庙异象频生。</li>
        <li><strong>第二幕 · 花园决断与血色祭献：</strong>布鲁图斯在书房整夜难眠，将刺杀定性为‘向罗马献祭’；拒绝斩草除根杀安东尼；波西娅割伤大腿证明女性忠贞；恺撒在凶梦与奉承中执意走向元老院。</li>
        <li><strong>第三幕 · 二十三刀与广场修辞大逆转：</strong>元老院血溅庞培雕像；安东尼与刺客握手隐忍；布鲁图斯的理性演说大胜；安东尼登台颠倒乾坤；暴民暴乱，诗人辛纳因同名遭当街撕碎。</li>
        <li><strong>第四幕 · 后三头大清洗与大帐决裂：</strong>安东尼等三人拿着黑名单冷酷勾决亲族；布鲁图斯与卡西乌斯在萨第斯军营大帐因军纪军饷拔剑对峙；波西娅吞炭自尽；恺撒幽灵夜半现身。</li>
        <li><strong>第五幕 · 腓立比决战与英雄绝命：</strong>两军阵前对骂；卡西乌斯误判战局伏剑自尽；布鲁图斯迎剑殉道；安东尼致敬全剧最尊贵的罗马人，帝国大幕升起。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第三幕第二场安东尼发表著名的葬礼演说（Friends, Romans, countrymen, lend me your ears）：</strong>这是全书乃至世界政治史的绝对分水岭。如果布鲁图斯遵从卡西乌斯的建议禁止安东尼发表演讲，共和派早已巩固政权；正是由于布鲁图斯傲慢地以为‘全天下人都和我一样崇尚理性哲学’，放任安东尼登台，导致局势在十五分钟内彻底逆转，全剧从此直坠内战地狱。
      </div>"""

    sec05 = """      <div class="sub-heading">安东尼葬礼演讲的七步修辞解剖学</div>
      <p>安东尼在罗马广场上的演讲，是世界传播学与心理学必须字字研读的<strong>操纵群体心理的至尊教科书</strong>：<br>
      <strong>第一步（伪装顺从）：</strong>以‘我是来埋葬恺撒，不是来赞扬他’开场，承认‘布鲁图斯是个正派人’，化解台下暴民的敌对情绪；<br>
      <strong>第二步（事实反问）：</strong>列举恺撒带回战俘赎金充实国库、拒绝王冠三次的事实，反问‘这难道是野心吗？’在逻辑上给布鲁图斯钉上一枚问号；<br>
      <strong>第三步（情感共振）：</strong>当众流泪抽泣，为暴民留出心理发酵的沉默期，让暴民互相对视产生‘其实恺撒很冤’的动摇；<br>
      <strong>第四步（展示物证）：</strong>走下讲台走入人群，指着恺撒被刺破的长袍，一一指出‘这是卡西乌斯扎的窟窿，那是布鲁图斯扎的致命伤口’，将抽象政治转化为具体血肉创痛；<br>
      <strong>第五步（欲擒故纵）：</strong>拿出恺撒的遗嘱却声称‘我不能念，念了你们会疯掉去吻他的伤口’，反向激起暴民‘一定要念’的狂怒；<br>
      <strong>第六步（利益绑定）：</strong>公布遗嘱——恺撒给每一个罗马公民留下了七十五便士和全部私人花园！直接将政治正义与民众切身物质利益死死绑定；<br>
      <strong>第七步（释放恶犬）：</strong>看着暴民扛着火把冲向刺客住宅，安东尼冷冷冷笑：‘恶作剧，你已经开场了，随你怎么走吧！’展现了权谋大师对群众心理的绝对玩弄。</p>

      <div class="sub-heading">诗人辛纳之死：乌合之众狂暴的最惊悚隐喻</div>
      <p>第三幕第三场仅仅二十行短对白，却构成了全剧最恐怖的一笔：暴民在街上拦截了无辜诗人辛纳，盘问其姓名。诗人辩解说：‘我不是刺客辛纳，我是个写诗的辛纳！’暴民却狂吼：‘那就因为他的烂诗撕碎他！管他妈的是谁，叫辛纳就得死！’随后将其乱棍打死拖走。莎士比亚以极其清醒的冷眼向全人类揭示：<strong>一旦群众的盲目复仇狂热被煽动起来，它就会脱离一切正义的轨道，演变为反智、反文明、撕碎一切无辜者的嗜血绞肉机</strong>。</p>"""

    sec06 = """      <div class="sub-heading">雄辩、庄严、如同罗马大理石般的古典辩论体语言</div>
      <p>《尤利乌斯·恺撒》展现了莎士比亚所有剧作中最<strong>严整、精炼、几乎没有一句废话的古典崇高文风</strong>。全书没有小丑插科打诨，语言全部由元老、将军与战士在重大历史关头发表的政治辩论诗句构成。长句排比、对偶、层递与反诘如同罗马军团方阵般严丝合缝、步步紧逼，散发出一种花岗岩般的硬朗金属质感。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>恺撒被刺透的带血长袍 (Caesar's Mantle)：</strong>安东尼手中最致命的修辞武器。它将抽象的‘政见分歧’具象化为一具具血淋淋的肉体刀口，成为了瞬间引爆民众感官与狂暴情绪的最强导体。</li>
        <li><strong>庞培的石雕神像 (Pompey's Statue)：</strong>元老院大殿中央的古典石雕。恺撒当年击溃了庞培称霸，最终却倒毙在手下败将的雕像脚下，鲜血染红了冰冷的大理石基座，象征<strong>政治权力的永恒轮回与任何狂妄胜利者的最终覆灭宿命</strong>。</li>
        <li><strong>三月十五日的凶兆与流星：</strong>夜空下的大火、狮子在街头漫步、坟墓开裂露出尸首。它象征着<strong>当合法的政治秩序即将被暴力刺杀打破时，大自然在暗夜中向文明发出的终极警告</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（古罗马历史政治悲剧）：</strong>罗马元老院为了捍卫共和刺杀独裁者恺撒，引发广场民意大反转与血腥内战，刺客集团在腓立比彻底败亡的史诗。<br>
        <strong>深层架构（理想主义的政治自杀）：</strong>对崇高道德动机脱离现实权谋法则必然失败的冷酷解剖。证明自命清高的书生理想主义不仅不能挽救制度，反而会以最快速度为更冷酷的军事独裁开路。<br>
        <strong>根本架构（修辞与大众民主的内在脆弱性）：</strong>乌合之众极易被言辞煽动的政治学宿命。当民众丧失了理性辨析事实的能力，所谓民意就只是一张任由野心家随意挥舞涂抹的空白支票。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>普鲁塔克的《希腊罗马名人传》是莎翁创作此剧的唯一历史母本。莎士比亚精准抓住了普鲁塔克对布鲁图斯‘过于崇尚哲学以致脱离世情’的历史定性，将其升华为西方文学史上探讨‘正义手段与崇高目的不可分割’的至高伦理杰作。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《尤利乌斯·恺撒》是<strong>现代信息战、公关公关、大选演说与网络民粹操控的祖宗神作</strong>：<br>
      今天政客在电视辩论上的字字玄机、商业公司公关在发布会上的情绪调动、以及社交媒体上大V通过剪辑视频、制造悲情带节奏引发全网狂暴围攻的套路，与两千年前安东尼在罗马广场上的七步演讲毫无二致。布鲁图斯的惨败警示每一个现代知识分子：光有道德和事实是远远不够的；如果你不懂得传播学规律、不懂得群众心理的弱点，你的崇高理想只会被野心家当做柴火烧成灰烬。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的团队或组织中，当你出于公心想要推动某项重大改革时，你是否曾犯过像布鲁图斯那样‘以为所有人都讲道理、忽视各方利益算计’的书生幼稚病？</li>
        <li>在网络热点事件中，当你被某篇煽情的小作文挑动得义愤填膺想要去网暴某人时，你是否能停下来问自己：我是不是正在变成那个当街打死诗人的暴民？</li>
        <li>如果为了实现一个看似崇高伟大的集体目标，必须采取下毒、暗杀或背叛挚友的手段，这种手段带来的‘正义’真的能长久吗？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《尤利乌斯·恺撒》是全世界最好的政治演讲与公关教科书。一群道德高尚的书生为了民主刺杀了独裁者恺撒，自以为赢了；结果将军安东尼在葬礼上发表了一场绝妙演讲，二十分钟就把全城百姓煽动成暴民把刺客全灭了。它告诉你：光有道德没有手腕，就是政治自杀；懂修辞的人，一句话就能改写历史。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读莎士比亚最具现代政治深度的史诗巨著——《尤利乌斯·恺撒》。很多人以为这是一部讲恺撒大帝丰功伟业的书，其实恺撒在第三幕刚开头就被杀了！整部戏真正的主角是那个刺杀他的书生将军——布鲁图斯。布鲁图斯是全罗马最受尊敬的正人君子，恺撒待他像亲儿子一样。但在罗马共和国即将沦为帝制独裁的危急关头，布鲁图斯被一群元老拉拢了。他整夜失眠，最后咬着牙做出了决定：‘不是我不爱恺撒，而是我更爱罗马的自由！’在元老院议事堂，二十三柄短剑齐出，当恺撒看见布鲁图斯也拔出刀时，心碎地说了一句名垂青史的话：‘还有你吗，布鲁图斯？那恺撒倒下吧！’刺杀成功后，布鲁图斯犯下了人类政治史上最致命的书生错误——他以为全天下老百姓都跟他一样崇尚哲学理性，他不仅放过了恺撒的爱将安东尼，还大方地准许安东尼在广场上给恺撒办国葬发表悼词！布鲁图斯先登台，讲了一通高大上的共和哲学，老百姓全鼓掌叫好。紧接着，全剧最高潮来了——安东尼上台了。安东尼根本不跟老百姓讲大道理，他以退为进，口口声声说‘布鲁图斯是个正派人’，转头却掀开恺撒带血的袍子，指着上面的血窟窿哭得眼泪鼻涕直流，最后公布恺撒的遗嘱——恺撒给全城老百姓每个人分发七十五块钱！刚才还在高呼‘共和万岁’的百姓瞬间疯了，化作狂怒的暴民，抄起火把冲去烧刺客的房子，甚至把一个路过仅仅跟刺客同名的无辜诗人当街活活撕碎！布鲁图斯仓皇出逃，最后在腓立比决战中全军覆没，迎着利剑自刎身亡。莎士比亚用这本小说给全人类上了一堂极其残酷的政治课：崇高的口号救不了世界，群众的狂热极易被演说家操纵；缺乏现实政治智慧的理想主义，最终只会给更残暴的独裁者做嫁衣裳。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “懦夫在真正死前已经死过千百次；而勇者一生只品尝一次死亡的滋味。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界政治戏剧与修辞学巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第二幕第一场（布鲁图斯花园夜思）：</strong>精读把刺杀定性为‘神圣献祭而非血腥屠杀’的书生哲学自欺独白。</li>
        <li><strong>必读第二场 · 第三幕第一场（元老院二十三刀弑君）：</strong>精读恺撒绝望低语‘还有你吗，布鲁图斯’的世界戏剧最高潮。</li>
        <li><strong>必读第三场 · 第三幕第二场（安东尼广场葬礼演说）：</strong>世界文学史最伟大的群众心理操纵修辞学巅峰，字字研磨反复诵读。</li>
        <li><strong>必读第四场 · 第四幕第三场（萨第斯军营大帐争吵）：</strong>精读理想主义与现实政治在军纪账目上的激烈火拼与和解。</li>
        <li><strong>必读第五场 · 第五幕第五场（布鲁图斯自刎与安东尼致敬）：</strong>精读全剧终局，在‘这是最尊贵的罗马人’挽歌中领悟崇高悲剧。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 理想主义的平庸之罪：</strong>布鲁图斯为了抽象的‘自由’弑杀了对自己恩重如山的恺撒，结果却把罗马拖入了死伤数十万人的内战浩劫。这种‘为了宏大目的不顾微观善恶’的做法究竟是崇高还是极度自私？
      </div>
      <div class="card-box">
        <strong>Q2 · 安东尼演讲的操纵伦理：</strong>安东尼在演讲中字字句句声称‘布鲁图斯是一个正派人’，却通过语调、眼泪和遗嘱点燃了全城的暴力之火。现代社交媒体上的政治煽动在多大程度上是在复刻这套古老技术？
      </div>
      <div class="card-box">
        <strong>Q3 · 诗人辛纳之死揭示了什么？</strong>群众在狂暴时连同名诗人都当街打死，这说明在集体狂热运动中，理性与事实扮演了何种微不足道的角色？
      </div>
      <div class="card-box">
        <strong>Q4 · 恺撒作为制度的不可逆性：</strong>为什么杀死了恺撒肉身，反而让‘恺撒主义（独裁帝制）’以更强大的形式加冕？个人的消灭能否阻挡历史制度演进的必然趋势？
      </div>
      <div class="card-box">
        <strong>Q5 · 终局安东尼的真诚致敬：</strong>安东尼在打垮布鲁图斯后，为什么要在其遗体前给予全剧最高的赞扬？这体现了罗马贵族政敌之间怎样的古典骑士风度？
      </div>"""

    sec13 = """      <div class="sub-heading">① 舆论防操纵实践工具：“安东尼修辞解毒滤镜” (The Antony Rhetoric De-Biasing Tool)</div>
      <p><strong>适用场景：</strong>当你被网络上某篇极具煽动性的小作文、大V的悲愤演讲或群情激愤的讨伐视频挑动得热血沸腾、准备下场转发骂人时。<br>
      <strong>第一步（拆除‘反讽正派人’话术）：</strong>找出对方在言辞中那些看似客观赞美、实则引导反向情绪的阴阳怪气词汇；<br>
      <strong>第二步（查‘带血长袍’物证）：</strong>审视对方展示的所谓‘铁证视频或截图’，是否被刻意剪辑截取了最具视觉感官刺激的片段？是否隐藏了前因后果？<br>
      <strong>第三步（查‘七十五便士遗嘱’利益）：</strong>逼问自己：发布这篇内容的人，最终能在这场群众愤怒中获得什么利益（涨粉、带货、转移监管视线）？看清利益闭环，不做被随意当枪使的‘罗马广场暴民’。</p>

      <div class="sub-heading">② 现实观察实验：“广场暴民与从众踩踏觉察”</div>
      <p>观察一次网络热搜反转全过程。记录网民在第一天听完单方面控诉时的狂热愤怒留言，对比第三天权威通报反转后网民的作鸟兽散，体会莎翁笔下罗马平民在布鲁图斯与安东尼之间极速反复横跳的悲剧心理。</p>

      <div class="sub-heading">③ 政治演说创作仿写任务</div>
      <p>模仿安东尼在罗马广场演说那种以退为进、运用反讽层层剥开听众心理防线的修辞技巧，写一段三百字‘一个危机公关发言人在面临严重质疑时巧妙化解矛盾并引导舆论’的演说对白（严密自洽、暗藏机锋）。</p>"""

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
    print("=== 开始批量写入第 13 轮（暴风雨、第十二夜、尤利乌斯·恺撒） ===")
    plan = [
        ("莎士比亚-暴风雨", get_deep_the_tempest),
        ("莎士比亚-第十二夜", get_deep_twelfth_night),
        ("莎士比亚-尤利乌斯·恺撒", get_deep_julius_caesar),
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
