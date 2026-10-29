# -*- coding: utf-8 -*-
"""
Round 18: Final Grand Finale (Twilight II, Twilight III, Twilight IV)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_twilight_2():
    data = {
        "title_cn": "暮光之城Ⅱ · 新月",
        "title_en": "New Moon",
        "author_cn": "斯蒂芬妮·梅尔",
        "author_en": "Stephenie Meyer",
        "sub_desc": "失去、心碎与创伤疗愈的暗夜长歌 · 狼人守护与意大利古老王座的生死奔赴",
        "hero_quote": "没有你的日子，不仅是黑暗；我的天空不仅失去了太阳，还失去了所有闪耀的星辰；当心脏被生生挖空，唯有狂乱的幻象能让我苟活。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">斯蒂芬妮·梅尔 (1973– )</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">2006 年出版 / 破全美首日销量记录</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">奇幻青春小说 / 失恋与创伤自愈长篇</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 26 万字 / 全二十四章带尾声</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">12+ 岁 / 青少年心理成长必读</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">抑郁空洞病理还原度与放手之爱的两难深思</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《新月》当成贝拉在爱德华离开后找雅各布当‘备胎慰藉’的狗血三角恋。梅尔以极其真实的心理解剖，还原了<strong>年轻人在遭遇重大情感遗弃后的重度抑郁症体验</strong>——全书连续四页完全空白的月份日记（十月、十一月、十二月、一月），是世界青春文学中表现‘心碎导致心智麻木停摆’最震撼的形式语言。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 连续四页空白日记与胸口空洞：</strong>爱德华以‘为你好’的名义单方面斩断联系，贝拉感到胸口被挖开一个漏风的大洞，通过极限自虐寻找幻觉。</div>
      <div class="card-box"><strong>② 奎鲁特狼人族群的体温救赎：</strong>雅各布带着42度的滚烫体温修摩托车，充当最温暖的精神创可贴，展现了阳光般的救赎力量。</div>
      <div class="card-box"><strong>③ 意大利沃尔泰拉古城正午钟楼飞奔：</strong>红袍万人狂欢节中，贝拉扑向即将脱衣求死的爱德华，撕碎一切误解的至高救赎。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">从常年阴雨的福克斯森林，到拉普什印第安保留地海滩，再到意大利托斯卡纳艳阳下的千年古城。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#131619;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">爱德华的离去 (Darkness)</text>
          <text x="120" y="72" fill="#e5e8eb" font-size="11" text-anchor="middle">单方面擅自斩断联系</text>
          <text x="120" y="90" fill="#e5e8eb" font-size="11" text-anchor="middle">自以为保护，实则致命摧残</text>
          <text x="120" y="108" fill="#e5e8eb" font-size="11" text-anchor="middle">误信死讯赴意大利求死</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">雅各布·奎鲁特 (Sunlight)</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">狼人血脉觉醒 · 巨型红褐巨狼</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">修摩托车 · 阳光般抚平创伤</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">终遭拒绝却依然选择守护</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#1d3557;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">沃尔泰拉正午钟楼拥抱</text>
          <text x="340" y="198" fill="#cad5e2" font-size="11" text-anchor="middle">红袍浪潮中挽回死神手中的爱人</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>贝拉·斯旺：</strong>在重度创伤中展现惊人耐受力的少女。她通过悬崖跳水寻找脑海中爱德华的声音，在得知爱德华赴死的一刻爆发出横跨大西洋的果决救援勇气。</li>
        <li><strong>雅各布·奎鲁特：</strong>温暖如初升太阳的少年。变身狼人后不得不隐瞒秘密，但当贝拉处于崩溃边缘时，他始终充当最坚固的避风港。</li>
        <li><strong>沃尔图里家族（阿罗、马库斯、凯厄斯）：</strong>吸血鬼世界的千年教廷法皇。深居大理石地宫，以严苛法律处决暴露者，为后两部的全宇宙冲突埋下终极暗线。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>贝拉十八岁生日派对上，因拆礼物划破手指流血引发贾斯珀嗜血暴动。爱德华深感自身存在是对贝拉最大的威胁，狠心撒谎宣称‘不再爱她’举家搬离福克斯。贝拉陷入长达数月的麻木抑郁，在印第安少年雅各布的温暖陪伴与修理摩托车中逐渐自愈。雅各布觉醒为奎鲁特狼人，保护贝拉免遭游荡吸血鬼劳伦特与复仇女维多利亚的袭击。贝拉在海边悬崖跳水寻求幻觉刺激，被爱丽丝通过预知未来误以为跳崖自尽。爱德华闻讯万念俱灰，远赴意大利古城沃尔泰拉，企图在正午阳光下的圣马可节庆典当众暴露真身引来沃尔图里皇室处死自己。贝拉与爱丽丝飞车横跨欧洲，在正午十二点钟声敲响、爱德华即将踏出阴影的最后一秒飞身扑入他怀中将其救下。沃尔图里放走二人但勒令贝拉必须尽快转化为吸血鬼。重返福克斯后，卡伦家族全员投票同意接纳贝拉永生，爱德华向贝拉许下了‘先结婚后转化’的庄重诺言。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“单方面自以为是的‘为了你好而放手’，对深爱之人究竟会造成多么毁灭性的伤害；以及在失去一切精神支柱的至暗时刻，人如何通过友情的体温艰难完成自愈”</strong>。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">在四个月毫无文字的空白绝望中，体验一种心脏被掏空后的冰冷刺骨，并在意大利烈日与万人狂欢的红袍浪潮中，迎来死而复生的战栗重逢。</div>"""

    sec04 = """      <div class="sub-heading">叙事建模与转折</div>
      <div class="card-box"><strong>决定性转折点：</strong>意大利沃尔泰拉钟楼正午十二点钟声敲响的那一秒，贝拉拨开红袍狂欢人群飞扑救下爱德华，宣告‘自以为是的离开保护’彻底破产。</div>"""

    sec05 = """      <div class="sub-heading">心碎与空白页的形式力量</div>
      <p>整整四个月的日记空白页，是二十一世纪青年文学最震撼的留白艺术。真正的巨大悲伤是无声的、无法用词语表达的，它如同一片严寒的荒原，只有时间的无声流淌。</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>新月 (New Moon)：</strong>失去太阳与月光笼罩的无光暗夜，象征生命最低谷的虚无期。</li>
        <li><strong>红斗篷万人狂欢节：</strong>古城狂欢下的血腥处决背景，象征繁华与死亡的极度并置。</li>
        <li><strong>修补旧摩托车：</strong>用双手重新组装零件，象征在现实泥泞中一点点拼凑碎裂的心灵。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>爱人离去后女主角与狼人伙伴相互扶持，飞赴欧洲救回心上人的冒险奇谭。<br>
        <strong>深层架构：</strong>初恋破灭后重度创伤的心理自愈与自我重建史。<br>
        <strong>根本架构：</strong>面对生命中注定的失去与磨难，唯有坦诚与共同承担才能抵御虚无。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>评论界指出：《新月》成功打破了第一部的单纯甜蜜模式，将作品引入了带有严肃悲剧与存在主义探讨的深水区，证明了爱情需要承受痛苦的试炼。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>不要在感情中擅自替对方做主‘为了你好而分手’，真正的成熟是坐下来坦诚面对所有的风险，携手面对风雨。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《新月》是全系列最虐心的一本。男主以为离开是对女主好，结果女主抑郁得整整四个月写不出一个字；后来男主误以为女主死了跑到意大利求死，女主飞奔过去在万人广场把他扑倒救下。它告诉你：爱就坦白说，别自以为是搞所谓的默默放手。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读第三章树林绝情分手 · 连续四张空白日记 · 第二十章沃尔泰拉正午钟楼狂奔相拥。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 爱德华的离开动机：</strong>爱德华自以为高尚的离开，在多大程度上其实是一种自恋与对贝拉心理承受力的蔑视？
      </div>
      <div class="card-box">
        <strong>Q2 · 雅各布的阳光力量：</strong>在失恋自愈过程中，拥有一个像雅各布那样无私陪伴的朋友，具有何种不可替代的心理抚慰价值？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“创伤自愈空白页法则”</div>
      <p>在遭遇重大心碎或变故时，允许自己拥有‘彻底什么都不做、什么都不思考’的空白期，不强迫自己立刻开心起来，给心灵自然的伤口结痂时间。</p>"""

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

print("Round 18 deep Twilight II ready.")

def get_deep_twilight_3():
    data = {
        "title_cn": "暮光之城Ⅲ · 月食",
        "title_en": "Eclipse",
        "author_cn": "斯蒂芬妮·梅尔",
        "author_en": "Stephenie Meyer",
        "sub_desc": "宿敌联盟与决断时刻 · 暴风雨前夕的阵营抉择与西雅图新生军生死战",
        "hero_quote": "云彩遮住了太阳，但太阳依然在那里；然而对我而言，你才是我的太阳；在暴风雨来临之际，宿敌并肩方能守卫家园。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">斯蒂芬妮·梅尔 (1973– )</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">2007 年出版 / 全球畅销大潮高峰</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">奇幻战争小说 / 爱情决断与宿敌同盟</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 27 万字 / 全二十七章带尾声</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">12+ 岁 / 终身必读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">阵营妥协政治智慧与不可兼得的成人决断</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《月食》当成贝拉在两个帅哥之间摇摆不定的浮躁三角恋。当维多利亚组建的残暴西雅图新生吸血鬼军团压境时，<strong>势同水火数百年的卡伦家族与印第安奎鲁特狼人族群，为了保卫家园在林间空地握手言和并肩作战</strong>。这展现了超越世仇的成熟政治妥协，也是贝拉在面对成人门槛时必须做出的不可逆决断。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 雪山帐篷里的情敌长夜坦诚心迹：</strong>风暴呼啸，贝拉冻得濒死，爱德华冰冷的体温无能为力，主动唤来滚烫的雅各布进入睡袋抱住贝拉取暖。两个男人在暗夜中展开了一生中最成熟坦荡的情敌对话。</div>
      <div class="card-box"><strong>② 林间空地狼人与吸血鬼的绝妙联合战术演练：</strong>贾斯珀利用南美内战军旅经验，指导巨大如马的狼人如何利用敏捷性猎杀不知疼痛的新生儿。</div>
      <div class="card-box"><strong>③ 维多利亚的伏击与雪峰绝杀：</strong>红发女魔头率部突袭雪山指挥营地，爱德华与狼人首领赛斯合力将其彻底斩杀焚毁。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">西雅图连环杀人案阴云密布，福克斯高中山顶积雪未化，两个历史仇敌族群在战争威胁下结成前所未有的生死联盟。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">卡伦吸血鬼家族</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">战术大师贾斯珀指导</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">速度与坚固大理石力量</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">爱德华的成熟信任与包容</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">奎鲁特狼人同盟</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">山姆与雅各布狼群</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">巨大咬合力与协同作战</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">放下世代仇恨守护这片土地</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2.5" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#242930;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">全歼西雅图新生军</text>
          <text x="340" y="198" fill="#e5e8eb" font-size="11" text-anchor="middle">瓦解维多利亚复仇阴谋</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>贝拉·斯旺：</strong>在成年的十字路口做出终极选择。她深知自己对雅各布的依恋与感动，但她清醒明白那不是可以托付灵魂的终极爱情；她坚决选择与爱德华成婚并转化为吸血鬼。</li>
        <li><strong>爱德华：</strong>展现了真正的成年人风度。克服了内心的嫉妒与不安，在雪山营地主动唤来情敌为冻僵的妻子取暖，展现了以所爱之人生命为重的高贵格局。</li>
        <li><strong>雅各布：</strong>悲壮赴死的英雄护卫者。明知贝拉的选择，依然率领狼群冲锋陷阵，在歼灭战中被残余吸血鬼重伤骨折，赢得了全卡伦家族的崇高敬重。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>西雅图频发不可解释的离奇连环凶杀案，卡伦家族识破这是复仇女吸血鬼维多利亚在暗中批量制造、缺乏理智与自控力但力量奇大的‘新生吸血鬼军团’。为了保卫福克斯小镇与贝拉的安全，卡伦家族与狼人奎鲁特部落达成了历史性军事同盟。在贾斯珀的指导下，宿敌并肩演练战术。决战前夜，爱德华带贝拉藏身于暴风雪笼罩的高峰营地，因贝拉体温失温濒死，爱德华主动请来雅各布入帐用42度体温相拥保暖，两位情敌在烛火下达成神圣和解。次日，狼人与卡伦家族在林间空地全歼新生军主力，潜伏包抄营地的维多利亚与其情人被爱德华与少年狼人赛斯合力击杀。贝拉在病榻前与重伤的雅各布诀别，平静接受了爱德华赠予的祖传钻戒，正式宣布筹备婚礼走向永生。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“成年的真正代价在于敢于做不可兼得的取舍，并为之承担全部后果”</strong>。它展现了放下历史偏见实现跨界合作的理性力量，以及真正的爱必须包含对对方真实意志的尊重。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">在雪山风暴与林间嗜血厮杀的紧绷博弈中，见证两群宿敌如何用理性融化坚冰，见证一个女孩如何在两个同样深沉的灵魂之间，坚定走向属于自己的终极宿命。</div>"""

    sec04 = """      <div class="sub-heading">双重博弈模型与决定性转折点</div>
      <div class="card-box"><strong>决定性转折点：</strong>雪山营地爱德华主动唤雅各布入睡袋：两名男人彻底放下了雄性竞争的占有欲，把爱人生命的安危置于虚荣自尊之上，完成了全书最高境界的情感升华。</div>"""

    sec05 = """      <div class="sub-heading">折断红色丝带的象征意涵</div>
      <p>封面被撕裂折断的红色缎带，象征贝拉与人类社会、凡人凡俗生活（生老病死、大学、体面职业）的彻底割断。走向永生并不是免费的午餐，它意味着从此与阳光绝缘、与父母永远处于隐秘隔绝的苍凉代价。</p>"""

    sec06 = """      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>月食 (Eclipse)：</strong>象征月亮遮蔽了太阳的光辉，但太阳的炽热从未泯灭。</li>
        <li><strong>撕裂的红色缎带：</strong>告别凡人人生的不可逆创伤。</li>
        <li><strong>祖传维多利亚钻戒：</strong>爱德华母亲留下的传家宝，象征穿越百年的古老盟约。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>宿敌联手击溃复仇军团、女主角做出终极情感抉择的青春奇幻战争戏。<br>
        <strong>深层架构：</strong>面对重大外部危机时跨阵营同盟的政治智慧与妥协艺术。<br>
        <strong>根本架构：</strong>成人的本质是学会舍弃。不可两全其美，敢于承担取舍后的代价。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>青年文学评论家指出：《月食》是全系列在动作场面、战术布局与情感博弈上张力最紧绷的一卷，成功展示了通俗幻想小说驾驭大规模多阵营冲突的成熟技巧。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>面对生活中的复杂人际矛盾，学会聚焦‘共同利益与危机’，放下成见携手合作；在关键人生关口，绝不拖泥带水，敢于做出清醒坚定的抉择。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《月食》是全系列最燃的一本。复仇大军压境，势不两立的狼人和吸血鬼居然联手在大森林里打歼灭战！在暴风雪山顶，情敌两个男人在帐篷里促膝长谈达成和解。它告诉你：真正成熟的大人，能为了大局放下私仇，也能为了真爱勇敢做出取舍。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读林间空地战术演习 · 第十四章雪山帐篷长谈 · 第二十五章林间决战与订婚。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 妥协的难度：</strong>爱德华允许雅各布给贝拉取暖需要克服怎样的生理厌恶？这种克制体现了他怎样的爱情观？
      </div>
      <div class="card-box">
        <strong>Q2 · 雅各布的放手：</strong>在贝拉戴上婚戒后，雅各布化身巨狼狂奔入深山，这一幕传达了关于深情与放手怎样的尊严？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“危机同盟达成模型”</div>
      <p>在职场或生活中遭遇强大外部竞争危机时，主动向原本有矛盾的合作方抛出橄榄枝，建立临时利益防御同盟，用大局意识化解内耗。</p>"""

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

def get_deep_twilight_4():
    data = {
        "title_cn": "暮光之城Ⅳ · 破晓",
        "title_en": "Breaking Dawn",
        "author_cn": "斯蒂芬妮·梅尔",
        "author_en": "Stephenie Meyer",
        "sub_desc": "全系列宏大终章 · 母亲的坚忍抗争、涅槃新生与雪原和平大对峙",
        "hero_quote": "唯有在成为母亲的那一刻，我才真正懂得了什么叫无坚不摧；爱能穿透一切黑暗，在漫长寒夜后迎来属于全人类的破晓曙光。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">斯蒂芬妮·梅尔 (1973– )</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">2008 年出版 / 全球千万级终章落幕</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">史诗奇幻浪漫长卷 / 女性主体觉醒终局</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 35 万字 / 全三部三十九章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">13+ 岁 / 终身必读经典完结篇</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">母性牺牲意志与非暴力外交破局深度</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《破晓》仅仅看成一部生化危机式的‘半吸血鬼怪胎婴儿争夺战’。梅尔在后半卷构建了一场世界奇幻文学中罕见的<strong>“不战而屈人之兵的宏大法律外交对抗”</strong>——卡伦家族没有动用屠杀，而是遍访全球吸血鬼盟友作为证人，在雪原上凭借道德真相与克制实力，迫使不可一世的意大利教廷独裁者不战自退。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 贝拉拼死护胎的惊悚与神圣母性：</strong>半人半吸血鬼胎儿在腹中疯狂吸收营养、踢碎母亲肋骨与骨盆；面对全家要求流产的压力，贝拉誓死捍卫女儿降生，完成了女性生命意志的终极自决。</div>
      <div class="card-box"><strong>② 新生吸血鬼的‘意念护盾’超能觉醒：</strong>贝拉死而复生后不仅没有沦为嗜血野兽，反而展现出惊人的自制力，更觉醒了能够扩张数十米、保护全体盟友免疫精神攻击的金色护盾，从昔日被保护者跃升为家族最强盾牌。</div>
      <div class="card-box"><strong>③ 全球证人雪原大集结与无声对峙：</strong>罗马尼亚古老暴君、亚马逊雨林隐士、爱尔兰流浪者齐聚福克斯，与近百名黑袍沃尔图里精锐在平原上对峙，凭借真实证据剥夺了教廷开战的合法性。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">从巴西艾斯梅岛的蜜月海滩，到福克斯密林中的现代吸血鬼庄园，直至终极决战的雪原森林地平线。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#2a9d8f;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">贝拉 & 蕾妮斯梅</text>
          <text x="120" y="72" fill="#e5e8eb" font-size="11" text-anchor="middle">母性奇迹 · 意念护盾觉醒</text>
          <text x="120" y="90" fill="#e5e8eb" font-size="11" text-anchor="middle">保护全体盟友免受精神攻击</text>
          <text x="120" y="108" fill="#e5e8eb" font-size="11" text-anchor="middle">从受庇护弱者跃升为守护核心</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#131619;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">沃尔图里教廷 (Volturi)</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">阿罗 · 统治权威受挑战</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">企图以‘不朽孩童’借口除异己</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">面对铁证与实力平衡被迫撤军</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#8c2d19" stroke-width="2.5" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#1d3557;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">雪原全球盟友大集结</text>
          <text x="340" y="198" fill="#cad5e2" font-size="11" text-anchor="middle">以真理为证 · 和平破局消除浩劫</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>贝拉·卡伦（新生母亲）：</strong>完成了从平凡人类少女向超自然守护神的大飞跃。她不仅在产房力竭濒死时战胜了死神，更凭借惊人的心灵定力克制住了新生儿的杀戮狂暴。她的意念护盾，构成了全剧对抗阿罗与简精神折磨的最强物理屏障。</li>
        <li><strong>阿罗（Aro）：</strong>千年统治者的精明政客典型。他醉心于收藏具有特殊异能的异类，当发现卡伦家族势力庞大时试图借题发挥。在雪原上，当他触摸到爱丽丝带来的亚马逊半人半吸血鬼活证人、看清开战必遭全军覆没的实力平衡后，从容微笑着宣布‘误会解除’撤军，展现了冷酷老牌霸主的政治精明。</li>
        <li><strong>蕾妮斯梅（Renesmee）：</strong>半人半吸血鬼奇迹之女。拥有温暖的心跳、吸食鲜血亦可进食人类食物，能通过小手触摸将脑海中的真实记忆直接投影给对方，成为了打破教廷偏见谎言的最神圣证据。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>贝拉与爱德华举行盛大婚礼，赴巴西海岛度蜜月期间意外怀孕。腹中胎儿飞速生长骨骼坚硬如铁，将贝拉的身体迅速吸干骨折。在雅各布等人的守护下，贝拉在产房心跳停止的最后一刻生下女儿蕾妮斯梅，爱德华将毒液直接注入贝拉心脏将其转化为新生吸血鬼。苏醒后的贝拉脱胎换骨，不仅拥有神级自制力，更发现自己拥有保护他人的意念护盾。雅各布对女婴产生‘铭印’羁绊，两族世仇彻底化解。然而，德纳利家族的伊莲娜误以为女婴是受到教廷严令禁止的‘不可控不朽孩童’，飞赴意大利向沃尔图里告发。阿罗率领全员黑袍军队倾巢而出企图以此为借口灭绝卡伦家族。卡伦夫妇遍访全球拉美、埃及、欧洲吸血鬼作为证人集结福克斯雪原。对峙时刻，贝拉张开巨大护盾阻挡了敌方的全部痛苦魔法攻击；爱丽丝带回了另一位隐居南美洲一百五十年的半人半吸血鬼纳乌尔作为无可辩驳的存活证据。阿罗自知理亏且畏惧护盾实力，下令全军撤退。和平降临，贝拉终于在阳光下向爱德华完全敞开自己的心灵屏障，让爱人第一次听见了自己深藏已久的全部爱意，全书在大团圆的永恒晨曦中圆满落幕。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“母性与保护本能如何激发个体无坚不摧的内在力量，以及人类在面对霸权强力时，如何依靠证据、真相与联盟达成和平威慑”</strong>。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">在雪原千军万马的窒息对峙中，见证一个弱小母亲如何凭借不可动摇的守护信念撑起金色护盾，在冰天雪地间迎来属于生命的温暖破晓。</div>"""

    sec04 = """      <div class="sub-heading">和平威慑叙事模型与决定性转折点</div>
      <div class="card-box"><strong>决定性转折点：</strong>爱丽丝带回亚马逊丛林半人半吸血鬼活证人纳乌尔的一刻，直接在法理上彻底摧毁了沃尔图里开战的全部借口。</div>"""

    sec05 = """      <div class="sub-heading">国际象棋白王后的隐喻</div>
      <p>封面上的白王后棋子，象征贝拉完成了从最初任人摆布的兵卒，最终蜕变为横扫棋盘、掌控全场命运的至强守护者。</p>"""

    sec06 = """      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>破晓 (Breaking Dawn)：</strong>长夜终结，生命迎来属于自己的金色曙光。</li>
        <li><strong>贝拉的意念护盾：</strong>母性保护欲外化的实体屏障。</li>
        <li><strong>白王后棋子：</strong>女性主体意识觉醒与力量掌舵图腾。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>女主角结婚生女蜕变新生、全球盟友集结化解教廷围剿的大团圆史诗。<br>
        <strong>深层架构：</strong>女性主体力量觉醒与母性神圣抗争史。<br>
        <strong>根本架构：</strong>真相、尊严与和平威慑高于一切强权武力。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>全系列四部曲在《破晓》中完成了从私密校园爱情向宏大国际阵营政治博弈的全面升级，为二十一世纪全球青年流行文学画上了最圆满的休止符。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>真正的强大不是去欺凌别人，而是在关键时刻拥有守护家人的硬核实力；在面对霸权时，讲求事实与争取广泛联盟是唯一的制胜之道。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《破晓》是大结局神作。女主冒死生下半人半吸血鬼宝宝，自己变成超强吸血鬼护盾战神！意大利黑袍大军杀上门，女主带着全世界盟友在雪地对峙，靠证据和实力逼退教皇。它告诉你：为母则刚，有实力有证据，强权也不敢动你分毫。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读产房生死抢救 · 贝拉蜕变打猎自控 · 第三十七至三十八章雪原大对峙。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 贝拉护盾的心理学成因：</strong>为什么全家族那么多人，只有贝拉觉醒出了防御性护盾？这与她一生渴望保护他人的潜意识有何关联？
      </div>
      <div class="card-box">
        <strong>Q2 · 阿罗的撤军逻辑：</strong>强权霸主在什么情况下才会真正选择和平？实力平衡在维护正义中扮演了何种角色？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“危机和平破局模型”</div>
      <p>在遭遇强大的外部挤压时，不盲目冲动亮剑，而是快速团结一切可以团结的第三方证人，亮出不可辩驳的事实铁证，达成力量与舆论的制衡。</p>"""

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
    print("=== 开始批量写入第 18 轮（终极大收官：暮光之城 II、III、IV） ===")
    plan = [
        ("暮光之城II-新月", get_deep_twilight_2),
        ("暮光之城III-月食", get_deep_twilight_3),
        ("暮光之城IV-破晓", get_deep_twilight_4),
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
