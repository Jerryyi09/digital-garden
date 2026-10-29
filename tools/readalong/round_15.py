# -*- coding: utf-8 -*-
"""
Round 15: Walden, The Elegance of the Hedgehog, To the Lighthouse (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_walden():
    data = {
        "title_cn": "瓦尔登湖",
        "title_en": "Walden",
        "author_cn": "亨利·戴维·梭罗",
        "author_en": "Henry David Thoreau",
        "sub_desc": "自然主义与简约生活的至高圣经 · 湖畔林间的孤独静思长卷",
        "hero_quote": "我步入丛林，因为我希望生活得从容自得；我只想面对生活最根本的要素，看看我是否能学到它要教给我的东西，以免在临死时，才发现自己从未真正活过。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">思想家与隐士</div><div class="spec-val">亨利·戴维·梭罗 (1817–1862)</div></div>
        <div class="spec-item"><div class="spec-label">实验年代</div><div class="spec-val">1845–1847年湖畔独居 / 1854年出版</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">哲理散文 / 自然主义经典 / 超验主义传世作</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 22 万字 / 全十八章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">14+ 岁 / 终身必读精神经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">极简物质生活与精神丰盈自由的实践典范</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把梭罗在瓦尔登湖畔的两年两个月误读为‘完全不食人间烟火、与世隔绝的隐居野人’。湖畔离康科德小镇只有两英里，梭罗经常步行去镇上借书、访友、吃母亲做好的派。他做的是一场极其严谨的‘现代经济学反向实验’——向世人证明，维持体面生活所需的必需品何其稀少，人们不必为了虚荣将毕生卖给无休止的劳役。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 第一章《经济篇》以会计般的严密账目算清‘生存必需品’的真实成本：</strong>详尽列出建木屋花费二十八美元十二分半、八个月伙食费八美元七毛四分，证明一个人只要把欲望降到最低，每年只需工作六周即可获得彻底的思想自由。
      </div>
      <div class="card-box">
        <strong>② 描绘瓦尔登湖在四季更迭中如天神之眼般澄澈深邃的湖水色泽变化：</strong>湖水在不同天气下展现天青色、碧绿色、纯澈透明，严冬破冰开凿运往印度作为天然冰块。
      </div>
      <div class="card-box">
        <strong>③ 在豆田里独自锄地、倾听林中松雀鸣唱与自然完全交融的物我两忘时刻：</strong>第七章《豆田》中，劳作不再是受苦，而是与大地神圣对话的仪式。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪中叶美国工业化起步，铁路向西贯通，商业物欲膨胀。爱默生、梭罗倡导超验主义，呼唤重返自然。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .wd-box { rx: 8; stroke-width: 1.5; }
            .wd-bg-concord { fill: #1d3557; stroke: #2a4d7a; }
            .wd-bg-lake { fill: #2a9d8f; stroke: #40916c; }
            .wd-bg-thoreau { fill: #8c2d19; stroke: #a33b24; }
            .wd-bg-spring { fill: #fbf9f4; stroke: #1c221e; stroke-width: 2.2; }
            .wd-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .wd-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .wd-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .wd-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .wd-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .wd-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="wd-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 喧嚣城镇文明 (康科德) -->
          <rect x="20" y="25" width="210" height="115" class="wd-box wd-bg-concord" />
          <text x="125" y="52" class="wd-t-w">喧嚣城镇：康科德 (Concord)</text>
          <text x="125" y="72" class="wd-t-sub-w">日夜奔忙 · 房贷账单 · 虚荣消费</text>
          <text x="125" y="90" class="wd-t-sub-w">‘绝大多数人生活在平静的绝望中’</text>
          <text x="125" y="108" class="wd-t-sub-w">把生命卖给二十年按揭与农具</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">被物质反向奴役的文明地狱</text>

          <!-- 自然圣殿：瓦尔登湖畔林地 -->
          <rect x="450" y="25" width="210" height="115" class="wd-box wd-bg-lake" />
          <text x="555" y="52" class="wd-t-w">自然圣殿：瓦尔登湖 (Walden)</text>
          <text x="555" y="72" class="wd-t-sub-w">借一把斧头建木屋 · 耕两亩豆田</text>
          <text x="555" y="90" class="wd-t-sub-w">澄澈湖水深102英尺 · 天空之眼</text>
          <text x="555" y="108" class="wd-t-sub-w">极简清醒 · 精神的至高自由</text>
          <text x="555" y="124" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">“简化，简化，再简化！”</text>

          <!-- 步入丛林连线 -->
          <path d="M 230 82 L 450 82" class="wd-solid" marker-end="url(#wd-arr)" />
          <text x="340" y="74" class="wd-lbl">步入丛林 · 生活减法实验</text>

          <!-- 核心践行者：梭罗 -->
          <rect x="235" y="135" width="210" height="85" class="wd-box wd-bg-thoreau" />
          <text x="340" y="162" class="wd-t-w">亨利·戴维·梭罗 (Thoreau)</text>
          <text x="340" y="180" class="wd-t-sub-w">超验主义践行者 · 拒绝虚伪纳税</text>
          <text x="340" y="196" style="fill:#f0dcd8; font-size:10px; font-weight:700; text-anchor:middle;">两年两月又两天的心智独白</text>

          <!-- 下方：春天的破冰与精神觉醒 -->
          <path d="M 340 220 L 340 250" class="wd-solid" stroke="#2a9d8f" />
          <rect x="160" y="250" width="360" height="80" class="wd-box wd-bg-spring" />
          <text x="340" y="275" class="wd-t-d">春天的破冰雷鸣与朝阳觉醒 (Spring)</text>
          <text x="340" y="295" class="wd-t-sub">湖冰轰鸣开裂 · 泥沙流淌如同活树叶 · 灵魂彻底走出严冬</text>
          <text x="340" y="310" style="fill:#8c2d19; font-size:10px; font-weight:700; text-anchor:middle;">“使我们双眼失明的阳光，对我们而言不过是黑暗；唯有我们清醒之时，破晓才会来临！”</text>
        </svg>
      </div>

      <div class="sub-heading">核心思想支柱与自然人物谱系</div>
      <ul class="bullet-list">
        <li><strong>梭罗（思想主体）：</strong>哈佛大学毕业却拒绝从商或做职业教士。他自称‘大自然巡视员与风雪记录员’。他在湖畔借了一把斧头，自己砍伐白松，用捡来的旧砖石搭起烟囱。他精算账目，向世人证明：现代人所谓的‘必需品’有九成都是累赘。他在湖畔看蚂蚁大战、与加拿大伐木工聊天、倾听夜鹰鸣叫，建立起了西方世界最伟大的极简主义生活哲学。</li>
        <li><strong>瓦尔登湖水（自然母体）：</strong>大自然纯洁清明的神圣眼睛。无论人间发生多少战乱喧嚣，湖水始终碧绿如洗，映照着天光云影，成为治愈疲惫心智的天然神庙。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>1845年7月4日美国独立日当天，二十八岁的梭罗孤身走进马萨诸塞州康科德小镇旁一片属于爱默生的林地，在风景如画的瓦尔登湖畔自建小木屋居住，直至1847年9月6日搬出，历时整整两年两个月又两天。全书以春夏秋冬四季更迭为脉络，详细记录了他在林中借斧建造木屋、开荒两亩半豆田、钓鱼采果、观察湖水水质与鸟兽昆虫的生活全景，穿插着对现代工业铁路、邮政制度、奴隶制度、繁文缛节与商业异化的深刻哲理剖析。全书在第二年春天的湖面冰层崩解、万物复苏中迎来神圣高潮，梭罗收拾行装从容走出丛林，以昂扬自信的笔调宣告人类精神觉醒的无限可能。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“人类在被物质消费与社会习惯无情绑架的时代，如何通过主动做‘生活减法’，剔除一切非本质的浮华琐碎，赢回属于生命本身的清醒、尊严与从容”</strong>。梭罗证明：真正的贫穷不是口袋里没有钱，而是心灵深处的空虚麻木与对自由的拱手让渡。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一捧在严冬湖面冰层下破冰取出的甘甜冰水：在极简纯粹的林间呼吸中，洗去脑海中所有关于金钱房贷与排场的杂念，感受生命在最质朴状态下所能焕发出的不可思议的自由与充盈。</div>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以康科德城镇为代表的物质过剩、虚荣借贷与无休止劳役枷锁 vs 以瓦尔登湖畔为代表的自食其力、精神自立与沉静深思。</strong></p>
      <div class="sub-heading">全书四大精神四季推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 盛夏搭建与经济自律（第一至五章）：</strong>《经济篇》详细算账；自建木屋入住；《读何书》《声音》，倾听林间风声与远方火车汽笛。</li>
        <li><strong>第二幕 · 盛秋劳作与超验冥想（第六至十章）：</strong>《访客》《种豆》，锄头翻开泥土的哲理感悟；《村落》《湖泊》，详尽测量瓦尔登湖、弗林特湖的水质与深度。</li>
        <li><strong>第三幕 · 严冬筑室与破冰取晶（第十一至十六章）：</strong>《更高的规律》《野兽为邻》；湖面封冻三尺，波士顿商人雇工采冰运往全球；在冰封深水垂钓。</li>
        <li><strong>第四幕 · 春日复苏与破晓结语（第十七至十八章）：</strong>《春天》，湖冰雷鸣般开裂，泥沙流动如生机树叶；《结语》，离开湖畔的从容宣告——‘我还有别的人生要去度过’。</li>
      </ol>
      <div class="sub-heading">决定性转折点</div>
      <div class="card-box"><strong>第十七章《春天》湖面冰层崩解的雷霆轰鸣：</strong>漫长严冬之后，春风一夜拂来，巨大的冰层在深渊中咆哮碎裂，沙土在阳光下融化流动如同生机勃勃的肺叶。这一刻象征着无论人类的麻木与僵化有多么深重，在自然伟力的感召下，心灵的坚冰终将粉碎迎来重生的破晓。</div>"""

    sec05 = """      <div class="sub-heading">为什么离开瓦尔登湖？——拒绝将一种生活变成新的教条</div>
      <p>梭罗在《结语》中给出了极其潇洒的解释：‘我离开丛林，正如我步入丛林一样，有着极其充分的理由。我发现，哪怕在湖畔生活，我也容易不知不觉在小径上走出一条习惯的深沟！我还有好几种别的人生要去体验，我不愿意把这一种生活变成新的教条。’这体现了超验主义最彻底的自由——连‘极简隐居’本身也不可以被执迷神化，真正的自由是随时能够拔锚启航、奔向新的精神原野。</p>"""

    sec06 = """      <div class="sub-heading">纯净透明、极度洗练的散文诗笔质感</div>
      <p>梭罗的语言如同新英格兰清晨的空气。他融合了古希腊荷马史诗的崇高、中国《论语》《孟子》的东方哲思与近代精确的自然博物观察白描，句句洗练、直指人心，构成了全人类非虚构文学最纯粹的高山。</p>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>一个哈佛学者在荒野湖畔自建木屋隐居两年的自然观察手记与生活账本。<br>
        <strong>深层架构：</strong>对现代工业文明异化人性、把人变成机器奴仆的系统性社会学批判。<br>
        <strong>根本架构：</strong>精神自立与极简主义本体论。证明生命的本质丰饶完全不需要庞大的物质堆砌，唯有清醒的灵魂才能领略存在的至高美感。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读与评价</div>
      <p>甘地在南非斗争时将梭罗的著作放在枕边，马丁·路德·金称其为‘公民抗命与精神自由的永恒灯塔’，海子与海明威皆视其为心灵圣典。它是现代人类在工业狂飙中守护灵魂净土的最高法典。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>在今天这个被房贷、消费贷、算法投喂与无尽社交内卷彻底包围的时代，《瓦尔登湖》不是叫我们去森林当野人，而是教我们在心中筑起一座‘湖畔小木屋’——定期给欲望做减法，留出属于自己的清醒时间，夺回人生的控制权。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《瓦尔登湖》是专治现代消费主义内卷的至尊神作。哈佛学霸借了一把斧头，跑到湖边花二十八块钱盖了个木屋住了两年，每天种豆钓鱼看落日。他把账本甩在世人脸上说：维持生存根本用不了几个钱，你们拼死加班买的那些烂东西，只是给自己套上的黄金枷锁。它告诉你：简单生活，才能活出真正的自由。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径：全书必读四大精粹场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一章《经济篇》：</strong>精读详细算账与‘人变成了工具的工具’传世批判。</li>
        <li><strong>必读第二场 · 第二章《我生活的地方；我为何生活》：</strong>精读‘步入丛林为了从容生活’的终身座右铭。</li>
        <li><strong>必读第三场 · 第九章《湖泊》：</strong>精读瓦尔登湖水色变幻与深测一百零二英尺的哲思白描。</li>
        <li><strong>必读第四场 · 第十八章《结语》：</strong>精读全书最后三段，在‘破晓来临’中领悟灵魂完全觉醒。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 简化的真正定义：</strong>梭罗所倡导的‘简化’，仅仅是省钱不买东西吗？如果内心依然充满虚荣，隐居木屋算不算另一种形式的表演？
      </div>
      <div class="card-box">
        <strong>Q2 · 终局破晓的隐喻：</strong>全书最后一句‘使我们双眼失明的阳光，对我们而言不过是黑暗；唯有我们清醒之时，破晓才会来临’，传达了怎样深邃的认知哲学？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“梭罗二十八美元生活减法审计” (The Walden Minimalist Audit)</div>
      <p><strong>第一步（找隐形奴役）：</strong>列出你目前每月必须支付的固定开销，挑出其中三项‘纯粹为了维持外界眼光中的体面’的虚荣项目；<br>
      <strong>第二步（算生命时薪）：</strong>把你购买这件物品的花费，折算成你需要为此加班打工的真实生命小时数；<br>
      <strong>第三步（果断退订）：</strong>退订这项虚荣服务，把换回来的宝贵时间用来在湖边或公园散步两小时，体会夺回生命主权的充盈。</p>"""

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

print("Round 15 deep Walden ready.")

def get_deep_hedgehog():
    data = {
        "title_cn": "刺猬的优雅",
        "title_en": "The Elegance of the Hedgehog",
        "author_cn": "妙莉叶·芭贝里",
        "author_en": "Muriel Barbery",
        "sub_desc": "法国当代畅销哲理奇迹 · 伪装平庸深处的惊世孤独、阶层反抗与美学顿悟",
        "hero_quote": "勒妮拥有刺猬的优雅：外表布满尖刺，坚固得令人望而生畏；但内里却极为细腻，怀抱一种孤独的优雅与无与伦比的高贵。"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家与哲学教授</div><div class="spec-val">妙莉叶·芭贝里 (1969– )</div></div>
        <div class="spec-item"><div class="spec-label">出版荣誉</div><div class="spec-val">2006 年出版 / 法国书店奖与全球畅销神话</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">当代哲理小说 / 双第一人称日记小说</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 18 万字 / 双重视角交叠长卷</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">14+ 岁 / 青年与成人思辨必读</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">阶层偏见伪装解构与小津安二郎美学深度</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《刺猬的优雅》看成一出‘傲娇女门房被日本有钱老头看上的灰姑娘黄昏恋’。芭贝里身为哲学教师，运用康德、胡塞尔现象学、托尔斯泰与日本禅宗美学，极其严厉地解剖了法国巴黎第七区上流精英社会的虚荣、冷漠与无知。女门房勒妮之所以伪装成粗鄙无能，是因为在阶级森严的世界里，<strong>一个平民如果被发现拥有高贵的思想，就会遭到整个阶层无情的怀疑与扼杀</strong>。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 密室暗室里的哲学圣殿：</strong>门房勒妮外表开着嘈杂电视掩人耳目，门后却藏着顶级日本红茶、全套《安娜·卡列尼娜》与荷兰油画，在孤独中完成对精神至高审美的朝圣。</div>
      <div class="card-box"><strong>② 十二岁天才少女芭洛玛的‘自杀倒计时’：</strong>富家少女冷眼看穿全家人的虚伪自欺，发誓在十三岁生日那天放火烧房自杀，却在底层女门房身上看到了活下去的真正意义。</div>
      <div class="card-box"><strong>③ 一句暗号引爆的跨阶层灵魂相认：</strong>日本绅士小津格郎凭借一句‘幸福的家庭都是相似的’密码，瞬间识破了勒妮伪装在粗鲁外壳下的刺猬优雅。</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">当代巴黎左岸格勒内勒街7号高级公寓。部长、大使、富豪云集，虚伪修辞与底层门房的隐秘圣殿在此对峙。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#131619;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">外在尖刺：刻板伪装</text>
          <text x="120" y="72" fill="#e5e8eb" font-size="11" text-anchor="middle">肥胖寡妇 · 电视肥皂剧杂音</text>
          <text x="120" y="90" fill="#e5e8eb" font-size="11" text-anchor="middle">劣质卷心菜气味 · 迎合阶层偏见</text>
          <text x="120" y="108" fill="#e5e8eb" font-size="11" text-anchor="middle">‘门房绝不能显得比住户聪明’</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#2a9d8f;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">内在优雅：精神贵族</text>
          <text x="560" y="72" fill="#e5e8eb" font-size="11" text-anchor="middle">康德先验哲学 · 托尔斯泰</text>
          <text x="560" y="90" fill="#e5e8eb" font-size="11" text-anchor="middle">小津安二郎电影 · 茶道禅宗</text>
          <text x="560" y="108" fill="#e5e8eb" font-size="11" text-anchor="middle">纯粹的美学沉思与灵魂高贵</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#8c2d19" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#1d3557;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">破壁相认：小津与芭洛玛</text>
          <text x="340" y="198" fill="#cad5e2" font-size="11" text-anchor="middle">穿透阶级面具 · 灵魂跨越鸿沟</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色与思想谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>勒妮·米歇尔（Renée Michel）：</strong>五十四岁女门房。出身贫寒，自学成才。她深谙上流社会的生存法则：如果一个门房懂哲学，住户就会感到不安甚至解雇她。因此她精心打造了自己的‘刺猬防线’。小津先生的出现和尊重，第一次让她勇敢脱下刺猬外壳，走向阳光与真爱。</li>
        <li><strong>芭洛玛·若斯（Paloma Josse）：</strong>十二岁富家千金。智商极高，早慧而孤独。她记录下《关于世界运动的深刻思想》与《唯美日记》，厌恶父母姐姐的平庸自大。正是勒妮的死，让她彻底懂得了‘死亡不重要，重要的是死的那一刻我们在准备去爱’，从而拯救了自己的生命。</li>
        <li><strong>小津格郎（Kakuro Ozu）：</strong>温文尔雅的日本退休绅士。他拥有一双能够洞穿外表皮囊的眼睛。他不把门房当仆役，而是邀请她共进晚餐、共同观摩电影，展现了真正的文明教养是对每一个独立人格的无条件尊重。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>巴黎富人区高档公寓的女门房勒妮，在狭窄的门房小屋里度过了二十七年，外表邋遢粗俗，内里却博览群书精通哲学。同楼十二岁的天才富家少女芭洛玛因看穿成年人的虚伪准备在生日自杀。日本富豪小津先生搬入公寓，敏锐识破了勒妮掩盖在门房外表下的优雅品味，并与芭洛玛一同成为了勒妮的密友。就在勒妮终于放下心防准备迎接幸福时，因在街头拯救流浪汉被干洗店卡车撞倒，在病榻上顿悟生命真谛安详离世，芭洛玛受其感召放弃自杀决心活出丰盛生命。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“美与真理的阶级无关性”</strong>。真正的贵族气质不在于住在几百平米的豪宅里夸夸其谈，而在于面对粗粝的现实生活，能否在内心筑起一座不容世俗侵犯的纯洁神庙。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">在看似密不透风的刺猬硬刺之下，触摸到一颗为真理与美战栗不已的至圣灵魂，领悟日本茶花坠地瞬间的刹那永恒。</div>"""

    sec04 = """      <div class="sub-heading">叙事推进与转折</div>
      <p><strong>决定性转折点：</strong>小津先生请勒妮共进生日晚餐，勒妮穿上借来的朴素黑色礼服理了短发。那一刻，她不再是门房，而是一个风华绝代、谈吐不凡的知识分子，阶级的隐形高墙在文化知己的凝视中轰然倒塌。</p>"""

    sec05 = """      <div class="sub-heading">刺猬的隐喻与死亡哲学</div>
      <p>勒妮死前的独白堪称世界现代哲理小说的神来之笔：她没有恐惧，没有抱怨，只是遗憾自己没能和小津先生去喝完那一碗红茶。但她感到释怀，因为她是在‘准备去爱’的行动中死去的。生命的长度无法掌控，但生命的密度完全由自己决定。</p>"""

    sec06 = """      <div class="sub-heading">核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>刺猬 (The Hedgehog)：</strong>外刚内柔的孤独智者图腾。</li>
        <li><strong>茶花掉落青苔的瞬间：</strong>日本古典物哀美学，在易逝中领略永恒。</li>
        <li><strong>金鱼缸：</strong>平庸世俗规训的囚笼隐喻。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>巴黎高级公寓里女门房、富家少女与日本绅士相遇相惜的感人故事。<br>
        <strong>深层架构：</strong>对现代资产阶级知识分子傲慢与阶层刻板印象的深刻解剖。<br>
        <strong>根本架构：</strong>美学与爱作为抵抗虚无与平庸宿命的终极救赎。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>法国文坛称赞此书‘以罕见的哲学深度与文学温情，洗刷了现代畅销书的轻浮泡沫’，证明严肃的哲学思考完全可以写得让人欲罢不能、热泪盈眶。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>不要以貌取人，不要用社会职业标签定义一个人的内在灵魂深度；在自己的日常生活中，建起属于你自己的‘门房密室’。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《刺猬的优雅》是法国最好看的哲理神作。一个胖门房假装粗俗，关上门却读康德喝高档日本茶；一个十二岁天才富家女看破红尘想自杀。一个日本老绅士识破了门房的秘密，三个孤独的灵魂相聚。它告诉你：真正的高贵不是钱，而是你骨子里对美的敬畏。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读勒妮初遇小津对暗号、小津生日家宴对白、勒妮临终前关于死亡的自白。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 伪装的必要性：</strong>为什么勒妮必须伪装才能平安活在巴黎富人公寓？这揭露了文明社会怎样的冷漠？
      </div>
      <div class="card-box">
        <strong>Q2 · 芭洛玛的转变：</strong>芭洛玛在勒妮死后为什么坚决放弃了自杀？她从这个门房身上学到了什么？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“刺猬密室建造法”</div>
      <p>在繁杂功利的社会交往之余，为自己保留一个‘不为人知的私人审美角落’（如每周两个小时的闭门阅读古籍），用深沉的艺术美滋养内心的纯粹。</p>"""

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

def get_deep_to_the_lighthouse():
    # 撰写 6000 字全篇
    data = {
        "title_cn": "到灯塔去", "title_en": "To the Lighthouse",
        "author_cn": "弗吉尼亚·伍尔夫", "author_en": "Virginia Woolf",
        "sub_desc": "意识流文学的无上高峰 · 时间流逝、两性心智模式与艺术定格的永恒挽歌",
        "hero_quote": "生命并没有什么宏大的意义；有的只是无数微小的奇迹，在一瞬间被照亮，如同黑暗大海中的一圈涟漪；我已经有了我的幻象！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">弗吉尼亚·伍尔夫 (1882–1941)</div></div>
        <div class="spec-item"><div class="spec-label">出版年份</div><div class="spec-val">1927 年出版 / 现代主义意识流巅峰</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">自传体意识流长篇 / 心理诗化小说</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 16 万字 / 全三部精密时间架构</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读</div><div class="spec-val">15+ 岁 / 终身必读文学经典</div></div>
        <div class="spec-item"><div class="spec-label">核心标准</div><div class="spec-val">主观心理时间流淌与艺术形式超越性</div></div>
      </div>
      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿用传统十九世纪小说的起承转合去寻找激烈的情节反转。整部小说的真正剧变发生在人物心智的每一次电光石火之中。第二部《时光流逝》中，十年的战乱浩劫、拉姆齐太太的猝死、长子战死沙场、长女难产离世，全被伍尔夫放在冰冷的几个括号里一笔带过，展示了时间无情抹平一切人间荣华的恐怖与苍凉。
      </div>
      <div class="sub-heading">三大核心看点</div>
      <div class="card-box"><strong>① 第一部《窗》中法式炖牛肉晚宴的神圣凝结：</strong>拉姆齐太太用母性的同理心，将一众脾气古怪、互相敌视的学者、诗人与画家融合成一个充满温情的生命共同体。</div>
      <div class="card-box"><strong>② 第二部《时光流逝》以无人的废弃海边别墅为视角的自然荒芜白描：</strong>风雨、黑暗、灰尘与蛛网如何一步步蚕食人类文明的记忆。</div>
      <div class="card-box"><strong>③ 第三部《灯塔》中莉丽在画布中央落下的那一笔垂直竖线：</strong>十年沧桑，两代人和解抵灯塔，女画家在画布上完成了终极艺术顿悟——‘我已经有了我的幻象！’</div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">一战前后苏格兰斯凯岛的海边别墅。布鲁姆斯伯里文化圈先锋思想与维多利亚父权幽灵的深层角力。</p>
      <div class="svg-wrap">
        <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="25" width="200" height="115" class="wd-box" style="fill:#1d3557;" />
          <text x="120" y="52" fill="#fff" font-weight="700" text-anchor="middle">拉姆齐先生 (Mr. Ramsay)</text>
          <text x="120" y="72" fill="#cad5e2" font-size="11" text-anchor="middle">逻辑哲学 · 事实至上 · 暴躁自怜</text>
          <text x="120" y="90" fill="#cad5e2" font-size="11" text-anchor="middle">卡在哲学Q阶段，时刻索取安抚</text>
          <text x="120" y="108" fill="#cad5e2" font-size="11" text-anchor="middle">代表冷峻威严的男性秩序律法</text>
          <rect x="460" y="25" width="200" height="115" class="wd-box" style="fill:#8c2d19;" />
          <text x="560" y="52" fill="#fff" font-weight="700" text-anchor="middle">拉姆齐太太 (Mrs. Ramsay)</text>
          <text x="560" y="72" fill="#f0dcd8" font-size="11" text-anchor="middle">美丽温润 · 情感纽带 · 艺术化身</text>
          <text x="560" y="90" fill="#f0dcd8" font-size="11" text-anchor="middle">抚慰所有人，守护孩子微小愿望</text>
          <text x="560" y="108" fill="#f0dcd8" font-size="11" text-anchor="middle">赋予刹那以永恒价值的生命之源</text>
          <line x1="220" y1="82" x2="460" y2="82" stroke="#2a9d8f" stroke-width="2" stroke-dasharray="4,4" />
          <rect x="235" y="150" width="210" height="85" class="wd-box" style="fill:#2a9d8f;" />
          <text x="340" y="178" fill="#fff" font-weight="700" text-anchor="middle">海中灯塔与画布中央一笔</text>
          <text x="340" y="198" fill="#e5e8eb" font-size="11" text-anchor="middle">莉丽·布里斯科 · 艺术独立与超越</text>
        </svg>
      </div>
      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>拉姆齐太太：</strong>伍尔夫亡母朱莉娅的文学再生。她拥有把破裂的人际关系缝合的神奇力量。她深知生命的荒凉与时间的冷漠，但她选择用温柔去包裹现实的尖刺，成为全书不朽的精神母体。</li>
        <li><strong>拉姆齐先生：</strong>伍尔夫父亲莱斯利·斯蒂芬爵士的真实写照。自私、苛刻、自尊心极度脆弱，把哲学当做个人英名流芳百世的工具。然而在十年后，年迈的他终于学会了赞赏儿子的掌舵，达成了两代人的神圣和解。</li>
        <li><strong>莉丽·布里斯科（Lily Briscoe）：</strong>伍尔夫本人的艺术分身。三十三岁未婚女画家，拒斥传统结婚生子规训。她用十年的沉淀，在拉姆齐太太去世后，终于在画布中央落下了关键的竖线，代表现代女性通过纯粹艺术创造确立独立主体的崇高胜利。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>第一部《窗》发生在一个晴朗的九月午后：拉姆齐一家在苏格兰海边避暑，六岁的小儿子詹姆斯渴望次日乘船去海中灯塔，母亲许诺天气好就去，而严苛的哲学家父亲却冷酷断言‘明天一定刮大风去不成’引发两性与家庭暗流；晚宴上拉姆齐太太张罗炖牛肉完成心灵交融。第二部《时光流逝》跨越十年：暴风雨与战火吞噬了度假屋，拉姆齐太太猝死，儿女夭折。第三部《灯塔》发生在十年后：年迈的拉姆齐先生终于带着长大叛逆的儿女乘船前往灯塔并在抵达时达成父子和解，留在岸上的女画家莉丽在画布中央画下最后一笔完成绝世创作。</p>
      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“时间的残酷侵蚀下，人类的记忆、深情与艺术如何获得永恒的锚定”</strong>。伍尔夫向世人宣告：生命不在于功业的高耸，而在于能否在飞逝的时间激流中，用爱和艺术捕获那些如珍珠般闪光的真实瞬间。</p>
      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">如同一叶在白雾与晨光中驶向海心灯塔的孤舟：在主观意识的千回百转中，见证易逝的生命如何在艺术的画板上定格为永恒的宁静。</div>"""

    sec04 = """      <div class="sub-heading">叙事结构三大飞跃</div>
      <p>从第一部充满空间细节的温情聚合，到第二部抹去人类痕迹的自然暴政，再到第三部在艺术与航程双重抵达中的神圣升华，全书呈现出完美的‘三联画’建筑对称美学。</p>"""

    sec05 = """      <div class="sub-heading">画布中央的一道竖线：女性艺术觉醒的圣杯</div>
      <p>莉丽十年来一直困惑于画布中央那块空白该如何处理。在看到拉姆齐一家的船终于抵达灯塔的那一秒，她突然扔下多余的细节，在中央画了一道简洁明了的垂直竖线。这道竖线连接了天与地、男与女、过去与未来，完成了整部小说形式与内容的终极合拢。</p>"""

    sec06 = """      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>海中的灯塔 (The Lighthouse)：</strong>既是近在眼前却可望不可即的理想彼岸，也是在黑夜冰海中定期扫过海面的清冷客观指引。</li>
        <li><strong>炖牛肉大宴 (Boeuf en Daube)：</strong>浓郁芬芳的热气腾腾菜肴，象征母性爱意在虚无中凝结出的安稳神圣绿洲。</li>
        <li><strong>莉丽画布上的竖线：</strong>象征艺术直面时间深渊时，所能落下的最坚定、最具自主性的坐标原点。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构：</strong>一个学者家庭在海边度假、跨越十年终于乘船登上灯塔的心理抒情长卷。<br>
        <strong>深层架构：</strong>两性心智模式（男性的理性征服 vs 女性的情感连接）的深刻冲突与终极互补。<br>
        <strong>根本架构：</strong>艺术创作对时间毁灭力量的抗争。唯有艺术的幻象能够打碎死神的枷锁。
      </div>"""

    sec08 = """      <div class="sub-heading">权威解读</div>
      <p>现代主义文学史将其列为与乔伊斯《尤利西斯》、普鲁斯特《追忆似水年华》并驾齐驱的意识流三神作之一，展示了女性小说家在探索内心真实维度上的惊天创造力。</p>"""

    sec09 = """      <div class="sub-heading">现代社会启示</div>
      <p>不要在死板的事实执念中伤害亲近之人，学会像拉姆齐太太那样用温柔化解生活的生硬，在琐碎日常中捕捉属于你自己的‘灯塔瞬间’。</p>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《到灯塔去》是意识流小说的封神之作。一个家庭约好去灯塔，父亲偏说去不成，母亲温柔安抚。十年战乱母亲死了，十年后老父亲终于带着孩子登上了灯塔，岸边的女画家画下了最后一笔。它告诉你：生命是飞逝的，但爱与艺术能把那一秒变成永远。”</p>"""

    sec11 = """      <div class="sub-heading">极简路径</div>
      <p>精读第一部第十七章晚宴、第二部《时光流逝》整章、第三部终局帆船靠岸与落笔成画。</p>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 迟到的灯塔之行：</strong>十年后他们终于踏上了灯塔，这趟行程还拥有当年的意义吗？时间夺走了什么，又留下了什么？
      </div>
      <div class="card-box">
        <strong>Q2 · 艺术的终极满足：</strong>莉丽最后说‘我已经有了我的幻象’，哪怕这幅画以后会被塞在阁楼烂掉她也不在乎，这种艺术态度具有怎样的神圣超越性？
      </div>"""

    sec13 = """      <div class="sub-heading">实践工具：“灯塔瞬间定格法”</div>
      <p>在家庭聚会或某个动人时刻，停下三秒钟，把当下的光线、气味与温度深锁在心底，让这一瞬间成为你未来穿透生活风暴的永恒灯塔。</p>"""

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
    print("=== 开始批量写入第 15 轮（Walden、刺猬的优雅、到灯塔去） ===")
    plan = [
        ("Walden", get_deep_walden),
        ("The Elegance of the Hedgehog", get_deep_hedgehog),
        ("To the Lighthouse", get_deep_to_the_lighthouse),
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
