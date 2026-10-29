# -*- coding: utf-8 -*-
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_invisible_man_guide():
    data = {
        "title_cn": "隐形人",
        "title_en": "The Invisible Man",
        "author_cn": "赫伯特·乔治·威尔斯",
        "author_en": "H. G. Wells",
        "sub_desc": "科学伦理惊悚先驱 · 绝对权力对人性的异化悲剧",
        "hero_quote": "我发现了一个伟大的秘密，但我同时也把自己放逐出了整个人类世界。"
    }

    # Section 01
    sec01 = """      <div class="specs-grid">
        <div class="spec-item">
          <div class="spec-label">作者与生卒</div>
          <div class="spec-val">H·G·威尔斯 (1866–1946)</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">出版年份</div>
          <div class="spec-val">1897 年出版 / 经典科幻惊悚小说</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">体裁坐标</div>
          <div class="spec-val">心理惊悚 / 科学伦理悲剧 / 黑色寓言</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">全书体量</div>
          <div class="spec-val">约 5 万字（全二十八章+尾声）</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">建议阅读年龄</div>
          <div class="spec-val">12+ 岁 / 青年与思辨读者</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">核心判断标准</div>
          <div class="spec-val">权力反噬心理刻画与道德律崩塌逻辑</div>
        </div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《隐形人》误读为拥有特异功能后的爽快偷窥或恶作剧传奇。威尔斯从第一行起就在详尽解剖<strong>“不受任何监督的特权，如何迅速将一个天才科学家腐蚀为妄想建立恐怖统治的偏执疯子”</strong>。这是一则关于现代物理学力量脱缰的道德警世录。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 严谨物理限制下的残酷生存困境：</strong>威尔斯拒绝魔法幻想。隐形人在严寒中必须脱光衣服才能隐形（饱受冻伤）、吃下的食物未消化前在体内完全可见、落下的雨滴与踩过的泥泞会出卖足迹。隐形不是特权，而是一座生理与社交的无形囚笼。
      </div>
      <div class="card-box">
        <strong>② 柏拉图“古各斯之戒”的现代科学演绎：</strong>如果一个人做任何事都不会被别人看见，他还会遵守道德底线吗？格里芬从偷盗父亲的钱财、烧毁房东的屋舍，到企图用暗杀统治整个小镇，展示了脱离社会约束后恶意的无限膨胀。
      </div>
      <div class="card-box">
        <strong>③ 平民社会的集体自卫反抗机制：</strong>击败这位科学狂人的不是宏大的军队，而是英国乡村客栈老板娘、流浪汉、猎犬以及团结起来手持铁锹棍棒的平民百姓，体现了常识社会对傲慢精英暴力的强韧反弹。
      </div>"""

    # Section 02 (with SVG)
    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪末正值X射线与光学折射理论大发展时期。威尔斯构思了天才物理学者格里芬，通过改变人体组织的折射率使之与空气完全一致，从而引发了一场席卷苏塞克斯乡村的孤绝杀戮追捕。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg">
          <style>
            .im-box { rx: 8; stroke-width: 1.5; }
            .im-bg-griffin { fill: #fbf9f4; stroke: #8c2d19; stroke-width: 2; }
            .im-bg-kemp { fill: #1d3557; stroke: #2a4d7a; }
            .im-bg-marvel { fill: #242930; stroke: #59645f; }
            .im-bg-village { fill: #f4efe4; stroke: #84908a; }
            .im-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 600; text-anchor: middle; }
            .im-t-d { fill: #8c2d19; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .im-t-dk { fill: #1c221e; font-family: sans-serif; font-size: 12.5px; font-weight: 600; text-anchor: middle; }
            .im-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .im-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .im-solid { stroke: #8c2d19; stroke-width: 1.8; fill: none; }
            .im-dash { stroke: #1d3557; stroke-width: 1.5; stroke-dasharray: 4,3; fill: none; }
            .im-lbl { font-family: sans-serif; font-size: 10.5px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="im-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 格里芬 (中心人物) -->
          <rect x="230" y="30" width="220" height="110" class="im-box im-bg-griffin" />
          <text x="340" y="60" class="im-t-d">格里芬 (The Invisible Man)</text>
          <text x="340" y="80" class="im-t-sub">天才物理学者 / 破译光学折射密码</text>
          <text x="340" y="100" class="im-t-sub">透明无形 · 寒冬受冻 · 心理偏执狂化</text>
          <text x="340" y="120" class="im-t-sub">企图发动“恐怖统治 (Reign of Terror)”</text>

          <!-- 胁迫与背叛 -->
          <path d="M 230 85 L 150 85" class="im-solid" marker-end="url(#im-arr)" />
          <text x="190" y="75" class="im-lbl">暴力胁迫</text>

          <!-- 流浪汉马弗尔 -->
          <rect x="10" y="35" width="135" height="100" class="im-box im-bg-marvel" />
          <text x="77" y="65" class="im-t-w">托马斯·马弗尔</text>
          <text x="77" y="85" class="im-t-sub-w">底层游民 / 软弱狡黠</text>
          <text x="77" y="105" class="im-t-sub-w">替罪工具 · 卷款潜逃</text>
          <text x="77" y="120" class="im-t-sub-w">私藏隐形三卷笔记</text>

          <!-- 投奔与告密 -->
          <path d="M 450 85 L 530 85" class="im-solid" marker-end="url(#im-arr)" />
          <text x="490" y="75" class="im-lbl">求盟遭拒</text>

          <!-- 肯普博士 -->
          <rect x="535" y="35" width="135" height="100" class="im-box im-bg-kemp" />
          <text x="602" y="65" class="im-t-w">肯普博士 (Dr. Kemp)</text>
          <text x="602" y="85" class="im-t-sub-w">大学同窗 / 理性秩序</text>
          <text x="602" y="105" class="im-t-sub-w">拒绝与独裁同谋</text>
          <text x="602" y="120" class="im-t-sub-w">布局报信联合警民</text>

          <!-- 乡村平民围猎 -->
          <path d="M 340 140 L 340 195" class="im-solid" marker-end="url(#im-arr)" />
          <text x="385" y="170" class="im-lbl">全面围困</text>

          <!-- 艾平村与伯多克市民群像 -->
          <rect x="180" y="200" width="320" height="95" class="im-box im-bg-village" />
          <text x="340" y="225" class="im-t-dk">社会共同体防御网 (艾平村 / 警署 / 猎犬)</text>
          <text x="340" y="245" class="im-t-sub">客栈老板娘霍尔太太 · 警察杰弗斯 · 平民棍棒</text>
          <text x="340" y="265" class="im-t-sub">关紧门窗 · 撒碎玻璃 · 围拢扑杀</text>
          <text x="340" y="280" class="im-t-sub">末路殴毙，尸身在众目睽睽下缓慢重新显形</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系</div>
      <ul class="bullet-list">
        <li><strong>格里芬（Griffin）：</strong>天才却缺乏道德同情心的纯粹智力狂人。他把自己从社会契约中连根拔起，最终陷入自食其果的四面楚歌。</li>
        <li><strong>肯普博士（Dr. Kemp）：</strong>格里芬的大学校友。尽管深知隐形技术的划时代价值，但他恪守公民良知与文明秩序底线，断然拒绝成为格里芬统治世界的“副手”，设计报官诱捕。</li>
        <li><strong>托马斯·马弗尔（Thomas Marvel）：</strong>无依无靠的流浪汉，被格里芬胁迫作为搬运手稿与衣物的苦力。他既恐惧隐形人的无形扼颈，又在暗中窥伺机会，最终卷走三本密码日记成为旅店老板。</li>
      </ul>"""

    # Section 03
    sec03 = """      <div class="sub-heading">表面上讲了什么故事</div>
      <p>大雪纷飞的寒冬，一位全身缠满白色绷带、戴着深色护目镜的怪客住进偏僻乡村客栈。他在客房里整日摆弄试管与化学试剂，脾气暴躁。当老板娘催缴房租时，他当众剥去绷带，露出空无一物的头颅引起恐慌。逃入山林的他在杀害同乡威克斯蒂德并企图暗杀肯普博士的过程中，被全镇居民围攻打死在泥坑中。</p>

      <div class="sub-heading">深处真正关心什么</div>
      <p>作品剖析了<strong>“科技赋权与个体道德良知的失衡危机”</strong>。当个体的物理破坏力通过科学被无限放大，而内心却缺乏基本的爱、同情与敬畏时，科技不仅不能带来自由，反而会将人类推向彻底的兽性暴虐。</p>

      <div class="sub-heading">核心体验一句话</div>
      <p>见证一种被狂妄理智剥夺了全部人性温存的孤魂，在绝对隐蔽与绝对恐惧中的歇斯底里自毁。</p>"""

    # Section 04
    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>不受约束的个人野心 vs 维护秩序的社会共同体</strong>；超绝知识的傲慢 vs 平凡常识的坚韧。</p>

      <div class="sub-heading">情节推进链条</div>
      <ol class="num-list">
        <li><strong>绷带怪客降临：</strong>艾平村客栈里的密室实验，怪诞行径引发村民谣言。</li>
        <li><strong>众目睽睽下的剥离：</strong>面对警察抓捕，格里芬脱去假发假鼻，透明的躯体让全村陷入惊骇大溃退。</li>
        <li><strong>林野逃亡与胁迫奴仆：</strong>在野外遭遇饥寒交迫，暴力控制游民马弗尔协助偷运研究笔记。</li>
        <li><strong>伯多克镇的同窗对峙：</strong>格里芬夜闯肯普博士书房，狂妄地吐露“恐怖统治”计划，肯普暗中向警局递信。</li>
        <li><strong>围城暗杀与全面猎杀：</strong>识破背叛的格里芬发动报复，小镇全城闭户、道路铺满碎玻璃并放飞警犬搜捕。</li>
        <li><strong>泥地围殴与肉体重新显形：</strong>格里芬在众人的拳打脚踢中咽气，透明的血液在死后逐渐凝固沉淀，惨白消瘦的尸首终于重回人间视野。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>肯普博士拒绝对话并向警长递信：</strong>那一刻宣告了格里芬妄图找到智识知音、以双人合谋推行恐怖专政的幻想彻底幻灭。格里芬自此从一名科学家彻底蜕变为穷凶极恶的连环杀人狂。
      </div>"""

    # Section 05
    sec05 = """      <div class="sub-heading">格里芬的堕落心路</div>
      <p>格里芬并非一开始就是凶犯。他对真理拥有近乎宗教般的热忱。但他的致命硬伤是<strong>极度自私与对他人的轻蔑</strong>。他偷走父亲保管的公款逼得父亲绝望自杀，却在墓前毫无忏悔。隐形实验成功的那一刻，他首先想到的不是造福人类，而是“谁也不能管束我了”，这注定了他必将走向灭亡。</p>

      <div class="sub-heading">马弗尔的小市民智慧与反噬</div>
      <p>马弗尔看似愚钝肮脏，实则极具平民的狡黠生存智慧。他用顺从麻痹暴怒的格里芬，在警署门前果断呼救求生。故事结尾，他用格里芬留下的黑钱买下了酒馆，关起门偷偷摩挲那三本谁也看不懂的炼金术般密码手稿，展现了人性对“力量秘密”永恒的贪欲循环。</p>"""

    # Section 06
    sec06 = """      <div class="sub-heading">三大核心象征网络</div>
      <ul class="bullet-list">
        <li><strong>缠满面部的白绷带与纸假鼻：</strong>这是格里芬与人类进行视觉交流的唯一伪装。它象征着<strong>文明的面具</strong>——唯有戴上它，人们才能把他当作同类接纳；撕下它，便露出了道德虚无的空洞黑洞。</li>
        <li><strong>三本密码日记本：</strong>格里芬以复杂的数学、化学符号记载的发明原稿。它象征着<strong>脱离伦理审视的禁忌知识</strong>，在未受驯化的灵魂手中就是打开地狱之门的钥匙。</li>
        <li><strong>泥泞中的血脚印与显形尸体：</strong>死去的格里芬首先显出白色的神经系统、骨骼、血管，最后是面容。它象征着<strong>大自然客观物理法则对背叛者的最终归位</strong>——人无法通过科技超凡入圣，死亡终将还原生命脆弱的肉身本色。</li>
      </ul>"""

    # Section 07
    sec07 = """      <div class="sub-heading">主题三层架构</div>
      <div class="card-box">
        <strong>表层：</strong>一个天才物理学家意外隐形后的惊悚流亡与杀戮覆灭。<br>
        <strong>深层：</strong>古典道德哲学难题“古各斯之戒”在近代科技狂热中的冷酷验证。<br>
        <strong>根本：</strong>当智识精英自居超越世俗公义时，文明共同体的自我免疫自卫机制。
      </div>"""

    # Section 08
    sec08 = """      <div class="sub-heading">警惕过度阐释</div>
      <p>不要把格里芬美化为“被世俗庸人逼上绝路的孤独普罗米修斯”。文本清晰指出，格里芬早在隐形之前就冷酷践踏伦理；他杀死无辜的威克斯蒂德仅仅是为了抢夺铁棒泄愤。他的悲剧是他主动选择弃绝同理心的必然代价。</p>"""

    # Section 09
    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>互联网的“匿名机制”正是现代人的“隐形药水”。当键盘后的发言者不需要承担面孔与身份责任时，人性中的戾气、网暴与恶毒便会不受控制地泛滥。现代社会每天都在制造数以亿计的精神“隐形人”。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>如果拥有一天完全不被任何人察觉的绝对隐形，你的第一念头是行善、自私还是破坏？</li>
        <li>在网络匿名发言时，你是否表达过现实中绝不敢说出口的冷酷与中伤？</li>
        <li>真正的自律是在别人的目光下维持体面，还是在空无一人的房间里依然心怀敬畏？</li>
      </ol>"""

    # Section 10
    sec10 = """      <div class="sub-heading">30 秒日常交流版</div>
      <p>“《隐形人》是最好的网络时代人性预言。它证明了：一个人如果做任何坏事都不会被看见，他不会变成救世主，而会变成疯狂的暴君。真正的自由需要敬畏与约束，不受监督的力量只会自我毁灭。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “隐形原本可以成为一宗无上的奇迹，但我却把它变成了一场赤身裸体的严冬苦役。”
      </div>"""

    # Section 11
    sec11 = """      <div class="sub-heading">最小通达路径</div>
      <ul class="bullet-list">
        <li><strong>必读核心章节：</strong>第七章（客栈解开绷带）、第十九至二十二章（向肯普吐露身世与作恶心路）、第二十八章与尾声（死战与显形）。</li>
      </ul>"""

    # Section 12
    sec12 = """      <div class="card-box">
        <strong>Q1 · 知识与德性：</strong>为什么现代教育往往培养出高智商却毫无悲悯心的专家？知识的增长为什么无法自动转化为善良？
      </div>
      <div class="card-box">
        <strong>Q2 · 孤立的代价值得吗？</strong>为了获得不受干扰的绝对独立，格里芬切断了亲情、友情与社会联结，这种“绝对自由”为何最终化作了无边孤独？
      </div>"""

    # Section 13
    sec13 = """      <div class="sub-heading">① 思维工具：“透明度道德压力测试”</div>
      <p><strong>法则：</strong>当你准备做出某个重要决定时，问自己：如果明早这个决定的每一个细节和动机都被公开投影在公司大厅或学校操场上，你是否依然能够坦荡面对？如果不能，停下来重新审视。</p>"""

    # Assemble HTML
    sections_data = [
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

    body_html = TEMPLATE_HEAD.format(**data)
    for idx, title, content, is_open in sections_data:
        body_html += render_section(idx, title, content, is_open)
    body_html += TEMPLATE_FOOT

    return body_html
