# -*- coding: utf-8 -*-
"""
Deep Literature Guide for The Invisible Man (Target: 5000+ Chinese chars, full benchmark level)
"""
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

def get_deep_invisible_man():
    data = {
        "title_cn": "隐形人",
        "title_en": "The Invisible Man",
        "author_cn": "赫伯特·乔治·威尔斯",
        "author_en": "H. G. Wells",
        "sub_desc": "心理惊悚与科学伦理的绝顶经典 · 绝对不受监督的特权对人性的深渊反噬",
        "hero_quote": "我发现了一个震动世界的物理学秘密，但我同时也把自己放逐出了整个人类文明。"
    }

    # 01
    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">作者与生卒</div><div class="spec-val">H·G·威尔斯 (1866–1946)</div></div>
        <div class="spec-item"><div class="spec-label">创作与出版</div><div class="spec-val">1897 年出版 / 现代科学伦理惊悚先驱</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">科学惊悚小说 / 心理悲剧 / 道德哲学寓言</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 5.5 万字 / 全二十八章+尾声</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">12+ 岁 / 青年与思辨读者</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">隐形物理限制真实度与权力腐化心理推演</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《隐形人》误读为拥有特异功能后的轻松搞笑恶作剧或爽剧。威尔斯从第一章起就以严谨的物理学和病理学视角解剖隐形的残酷代价：在零下风雪中隐形人必须脱光衣服（赤身裸体饱受冻伤）、刚吃下的食物在体内未消化前完全可见、雨水和踩过的泥泞会暴露足迹。这根本不是特权，而是一座将人彻底驱逐出社会的<strong>孤绝生理与精神炼狱</strong>。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 古典道德哲学“古各斯之戒”在现代科学狂热下的终极验证：</strong>古希腊哲学家柏拉图在《理想国》中曾提出著名思想实验：如果一个人捡到一枚隐形戒指，做任何事都不被看见、无需承担惩罚，他还会遵守道德正义吗？威尔斯以天才科学家格里芬为样本，冷酷地给出了答案：失去社会监督的绝对自由，必将把智者急速腐蚀为建立恐怖专政的偏执狂魔。
      </div>
      <div class="card-box">
        <strong>② 科技狂热背离人道关怀的必然自毁逻辑：</strong>格里芬绝非平庸之辈，他是破译了生物光学折射率的物理天才。然而他极度自私自利，甚至逼死父亲来获取实验经费。科学探索一旦剥离了对同胞的爱与敬畏，赋予个体的就不是神圣力量，而是滑向兽性深渊的单程车票。
      </div>
      <div class="card-box">
        <strong>③ 平民常识社会的集体自我防御机制：</strong>击败这位企图推行“恐怖统治（Reign of Terror）”科学超人的，不是正规军队的枪炮，而是英国乡村客栈老板娘、狡黠流浪汉、猎犬、以及全镇紧闭门窗、在道路铺满碎玻璃、手持铁锹棍棒围拢上来的平凡平民。常识社会的坚韧共同体，构成了阻击狂人暴政的最强防线。
      </div>"""

    # 02
    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        19世纪末正值伦琴发现X射线、光学理论与电磁学狂飙突进时期。天才青年物理学者格里芬，在伦敦大学因争夺专利而深陷孤僻，最终在极寒冬日的苏塞克斯郡艾平村引发了一场触目惊心的隐形杀戮危机。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .im-box { rx: 8; stroke-width: 1.5; }
            .im-bg-griffin { fill: #fbf9f4; stroke: #8c2d19; stroke-width: 2.2; }
            .im-bg-kemp { fill: #1d3557; stroke: #2a4d7a; }
            .im-bg-marvel { fill: #242930; stroke: #59645f; }
            .im-bg-town { fill: #f4efe4; stroke: #84908a; }
            .im-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .im-t-d { fill: #8c2d19; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .im-t-dk { fill: #1c221e; font-family: sans-serif; font-size: 12.5px; font-weight: 700; text-anchor: middle; }
            .im-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .im-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .im-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .im-dash { stroke: #1d3557; stroke-width: 1.5; stroke-dasharray: 4,3; fill: none; }
            .im-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="im-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 中心：格里芬 (隐形人) -->
          <rect x="230" y="25" width="220" height="120" class="im-box im-bg-griffin" />
          <text x="340" y="52" class="im-t-d">格里芬 (The Invisible Man)</text>
          <text x="340" y="72" class="im-t-sub">天才物理学家 · 改变组织折射率</text>
          <text x="340" y="90" class="im-t-sub">透明身躯 · 寒冬裸奔 · 神经衰弱癫狂</text>
          <text x="340" y="108" class="im-t-sub">从自闭实验到妄图建立‘恐怖统治’</text>
          <text x="340" y="126" style="fill:#8c2d19; font-size:10.5px; font-weight:700; text-anchor:middle;">终局：殴毙于泥泞，肉身缓缓显形</text>

          <!-- 胁迫左侧：流浪汉马弗尔 -->
          <path d="M 230 85 L 160 85" class="im-solid" marker-end="url(#im-arr)" />
          <text x="195" y="75" class="im-lbl">暴力挟持</text>

          <rect x="15" y="30" width="145" height="110" class="im-box im-bg-marvel" />
          <text x="87" y="58" class="im-t-w">托马斯·马弗尔</text>
          <text x="87" y="78" class="im-t-sub-w">底层游民 · 穿旧靴子</text>
          <text x="87" y="96" class="im-t-sub-w">充当背书苦力工具人</text>
          <text x="87" y="114" class="im-t-sub-w">机警逃脱 · 吞没日记</text>
          <text x="87" y="128" style="fill:#a8dadc; font-size:9.5px; text-anchor:middle;">后半生私藏三卷密码本</text>

          <!-- 求盟右侧：大学校友肯普博士 -->
          <path d="M 450 85 L 520 85" class="im-solid" marker-end="url(#im-arr)" />
          <text x="485" y="75" class="im-lbl">同窗求盟</text>

          <rect x="520" y="30" width="145" height="110" class="im-box im-bg-kemp" />
          <text x="592" y="58" class="im-t-w">肯普博士 (Dr. Kemp)</text>
          <text x="592" y="78" class="im-t-sub-w">理性学者 · 秩序卫士</text>
          <text x="592" y="96" class="im-t-sub-w">拒绝独裁统治图谋</text>
          <text x="592" y="114" class="im-t-sub-w">秘密报官 · 自身充当诱饵</text>
          <text x="592" y="128" style="fill:#e0e4e8; font-size:9.5px; text-anchor:middle;">联合警民布下天罗地网</text>

          <!-- 下方：社会共同体防御网 -->
          <path d="M 340 145 L 340 200" class="im-solid" marker-end="url(#im-arr)" />
          <text x="385" y="175" class="im-lbl">全面围剿</text>

          <rect x="160" y="200" width="360" height="115" class="im-box im-bg-town" />
          <text x="340" y="228" class="im-t-dk">社会共同体防御网络 (艾平村 / 伯多克小镇)</text>
          <text x="340" y="248" class="im-t-sub">客栈老板娘霍尔太太 · 警察杰弗斯 · 酒馆马夫与铁匠</text>
          <text x="340" y="266" class="im-t-sub">门窗闭锁 · 街道铺满碎玻璃 · 放出猎犬锁定气味</text>
          <text x="340" y="284" class="im-t-sub">狂人现身袭杀肯普，遭到全镇平民持棍棒铲锹包围扑杀</text>
          <text x="340" y="300" style="fill:#8c2d19; font-size:10.5px; font-weight:700; text-anchor:middle;">平民常识与制度对狂妄个人的终极清算</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度剖析</div>
      <ul class="bullet-list">
        <li><strong>格里芬（Griffin，隐形人）：</strong>白化病学者，智力超群却严重匮乏共情能力。为了实验不惜盗用父亲公款导致父亲自杀，在墓地前毫无悲悯。他以为隐形能赋予他为所欲为的神力，却绝望地发现隐形夺走了他拥抱温暖、享受美食与穿衣避寒的一切凡人权利。他在饥寒交迫中被逼疯，妄图在伯多克镇发起‘恐怖元年’，终被常识社会打回原形。</li>
        <li><strong>肯普博士（Dr. Kemp）：</strong>格里芬的大学同学。面对昔日同窗展示的划时代隐形技术，他没有被功名利禄冲昏头脑。当听闻格里芬计划通过刺杀无辜者确立恐怖专政时，肯普恪守公民底线，果断拒绝与魔鬼同谋。他不仅向警方报信，甚至在终局自愿作为活体诱饵在街道上奔跑引出格里芬，展现了知识分子守护文明秩序的道德风骨。</li>
        <li><strong>托马斯·马弗尔（Thomas Marvel）：</strong>流浪汉阶层的生动剪影。他身上混合着底层的胆小、邋遢与极度的狡黠。他被迫在格里芬的拳打脚踢下当差，却时刻等待反击契机；在逃跑后他死死护住三本密码笔记，晚年利用格里芬留下的金币开了一家旅馆，每天关起门来摩挲日记本做着自己隐形发财的旧梦，展示了人性对权力的永恒贪婪循环。</li>
        <li><strong>霍尔太太与艾平村村民：</strong>英国乡村市井文化的守护者。霍尔太太爱财却恪守体面原则，从最初忍受怪客的暴躁，到发现其无头真相后的果断逐客；村民们在警长带领下展现出令人敬畏的集体行动力，证明了平凡社会具有不可小觑的免疫自愈力。</li>
      </ul>"""

    # 03
    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>隆冬大雪中，一个用厚围巾、白色绷带缠满头面、戴着大护目镜和假鼻子的神秘怪客住进偏僻的艾平村客栈。他在客房里整日捣弄试管与化学仪器，性格阴鸷暴戾。当老板娘因房租拖欠与其对峙并叫来警察时，怪客当众撕下绷带假发，露出一具空无一物的虚空头颅，狂笑着脱光衣服隐形遁逃。在逃亡过程中，他暴力胁迫流浪汉马弗尔替他搬运研究手稿与偷窃金币，在遭到反抗后残忍杀害了无辜过路乡绅。随后，他潜入大学同窗肯普博士的宅邸，毫无防备地倾吐自己隐形成功的经历与企图在小镇建立‘暗杀恐怖统治’的疯癫蓝图。肯普识破其疯狂，秘密引来警方。恼羞成怒的格里芬扬言要当众处死肯普。在小镇全员戒备、严防死守的决战中，格里芬在扑杀肯普的瞬间被闻讯赶来的工人和村民重重包围，在一阵乱棍拳脚下气绝身亡。死去的狂人，肉身在泥泞中从神经、骨骼、肌肉到苍白面容，缓缓重新显形。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处解剖的是<strong>“失去外在制约的科技赋权，如何彻底撕开文明面具、释放个体内心最原始的野蛮暴君”</strong>。它揭示了科学主义若失去伦理自律，不仅不能把人类推向神坛，反而会把个体剥离为孤家寡人，将社会推向人人自危的黑暗地狱。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        不是获得超能力的狂喜，而是体验一种被绝对隐身剥夺了人际体温与物理安全感后，在严寒赤裸中发狂自毁的无间地狱。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个迷信‘有了绝对力量就能摆脱规则’的狂妄心智，以及在现代网络匿名狂欢中以为‘无人知晓即可肆意作恶’的现代人。</p>"""

    # 04
    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>不受约束的个体智识狂权 vs 维护生存与公义的世俗社会契约共同体。</strong></p>

      <div class="sub-heading">全书戏剧推进链条</div>
      <ol class="num-list">
        <li><strong>绷带怪客降临（第一至四章）：</strong>冬夜风雪中抵客栈，密室摆弄药水瓶，拒绝任何人打量其容貌，谣言在乡村小酒馆滋生。</li>
        <li><strong>当众剥皮现形（第七章）：</strong>房租对峙引发警民抓捕，格里芬在哄笑与惊骇中解开绷带扯下假鼻，空无一物的衣领令所有人魂飞魄散，在混乱中脱去衣裤隐形逃走。</li>
        <li><strong>荒原流窜与奴役工具（第九至十三章）：</strong>在严寒刺骨的荒野中几乎冻死，逼迫流浪汉马弗尔充当仆从，潜回客栈抢走三本研究笔记与金币。</li>
        <li><strong>小镇暴力升级与血案（第十五至十七章）：</strong>马弗尔携款逃往伯多克镇寻求庇护，格里芬在警署门前拔枪射击，在狂暴中用铁棒活活打死路过的老乡绅威克斯蒂德，彻底跨过凶杀红线。</li>
        <li><strong>同窗密室自剖（第十九至二十三章）：</strong>避难闯入肯普书房。在整整四章的独白中，格里芬狂妄吐露逼死父亲、大火烧毁伦敦出租屋的冷酷发迹史，提出‘建立恐怖统治’计划。</li>
        <li><strong>围城天罗地网（第二十四至二十七章）：</strong>肯普报官，格里芬誓言复仇。肯普制定破局战术：锁紧门窗、铺洒碎玻璃、放飞警犬封锁所有食物。</li>
        <li><strong>泥地击毙与重新显形（第二十八章与尾声）：</strong>格里芬现身扑杀肯普，全镇男女手持铁锹铲子扑上将其压死在泥潭中。透明的身体在咽气后缓慢浮现出骨骼、血管与惨白面庞；马弗尔在偏僻客栈里关上房门，贪婪抚摸着谁也看不懂的隐形秘密日记。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>格里芬向肯普吐露建立‘恐怖统治（Reign of Terror）’的狂妄蓝图：</strong>如果说此前的偷窃与伤人尚属求生应激，那么当格里芬在肯普书房宣布‘不仅要自卫，还要用刺杀小镇官民来确立第一个恐怖王国’时，他彻底切断了与人类社会的最后脐带，将自己从一位悲剧学者推入了全人类公敌的必杀深渊。
      </div>"""

    # 05
    sec05 = """      <div class="sub-heading">格里芬的堕落心路：从求知狂热到杀戮恶魔的必然滑坡</div>
      <p>格里芬并非传统哥特小说中受诅咒的无辜受害者。他的毁灭不是偶然，而是其性格中<strong>极度自私与对他人生存权的漠视</strong>的必然结果。他深居象牙塔，把同类视为笨拙低能的蝼蚁。当父亲因赔偿公款绝望自杀时，他甚至懒得去凭吊，只嫌父亲软弱；为了掩盖实验痕迹，他一把大火烧毁了无辜房东的整栋公寓。隐形并没有改变他的本质，只是像一面放大镜，彻底放大了他潜意识中的反社会人格。当他发现隐形无法换来鲜花与跪拜，反而带来饥饿与冻疮时，他的自尊彻底异化成了毁灭全世界的暴虐狂怒。</p>

      <div class="sub-heading">肯普博士的道德标杆：知识分子的公民勇气</div>
      <p>肯普是全书最值得敬佩的理性代表。他深知格里芬的技术在学术和军事上具有何等惊天的价值；如果他选择与格里芬同谋，凭借两人的智商足以在黑夜中洗劫国家。然而，肯普拥有一个真正学者最稀缺的品质——<strong>对生命与文明秩序的敬畏</strong>。他清醒地拒绝了‘超人专制’的诱惑，并敏锐地指出格里芬在生理上的死穴（不能吃喝、怕冷、不能踩泥）。在最后关头，他敢于以自身作为诱饵在街头奔跑，完成了从书斋学者向勇敢公民的崇高跃升。</p>

      <div class="sub-heading">马弗尔与平民社会的贪婪回响</div>
      <p>全书尾声的设计极具神来之笔。那个被所有人鄙视的流浪汉马弗尔，拿着格里芬抢来的钱开了一家名为‘隐形人旅店’的酒馆。每到深夜打烊，他便小心翼翼地从隐秘柜子里取出那三本厚厚的密码笔记本，在烛光下如饥似渴地研究着。这一幕揭示了一个令人不寒而栗的真相：<strong>格里芬虽然死了，但人类内心对‘不受制约的力量’的隐秘渴望从未消亡。</strong>只要人性中依然有贪婪与自私，新的‘隐形人’就随时可能在暗处死灰复燃。</p>"""

    # 06
    sec06 = """      <div class="sub-heading">科学逻辑与惊悚悬疑的文学肌理</div>
      <p>威尔斯在本作中展现了令人叹为观止的<strong>物理学逻辑闭环</strong>。他没有使用任何魔法药水或神灵附体，而是从光学生物学切入：透明的本质不是没有物质，而是物体的折射率（Refractive Index）与周围介质完全相同（如玻璃球浸入甘油）。正因遵循物理铁律，隐形人在大雾天会变成若隐若现的白色烟团、在阳光穿过浓烟时会在地面留下微弱的轮廓阴影、吃下的红色生牛肉在咽喉清晰可见。这种‘带着沉重物理镣铐的科幻构思’，比一切玄幻魔法更具压迫感。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>白色绷带、假发与大墨镜 (Bandages and Goggles)：</strong>格里芬重返人类社会的唯一视觉伪装。它象征着<strong>文明社会人际交往所必须的‘面具’</strong>。唯有当他缠满绷带假装成一个‘看得见的残疾人’时，社会才能勉强接纳他；一旦撕去这层面具露出虚无，他与人类的一切交流管道便宣告彻底死亡。</li>
        <li><strong>三本密码日记本 (The Three Manuscript Books)：</strong>密密麻麻记载着希腊字母、代数公式与化学反应式的原稿。它象征着<strong>脱离了伦理审查与人文关怀的‘野蛮技术黑天鹅’</strong>。在缺乏道德防线的人类手中，它是打开所多玛火灾的恶魔火种。</li>
        <li><strong>泥地中踩出的血脚印：</strong>隐形人光脚踩在雪地与碎玻璃上留下的血痕。它象征着<strong>大自然客观物理法则对傲慢逃离者的终极嘲弄</strong>——人想借技术成为无形的神，但肉体流淌的鲜血与重力，依然不可抗拒地将他死死钉在世俗泥潭之中。</li>
      </ul>"""

    # 07
    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（惊悚科幻）：</strong>一个年轻物理学家意外研制出隐形药剂，在乡村客栈暴露后引发全镇大追捕的惊险流亡小说。<br>
        <strong>深层架构（伦理哲学）：</strong>柏拉图‘古各斯之戒’的现代科学版推演。证明绝对免于惩罚的隐蔽特权，必将释放人性最深层的贪婪、暴虐与偏执。<br>
        <strong>根本架构（社会契约论）：</strong>人与社会共同体的不可分割性。人无法作为一个‘绝对脱钩的独立原子’自居于世；脱离了互相依存的社会契约，任何强大的个体都将在绝对孤独与严寒中枯竭暴毙。
      </div>"""

    # 08
    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>全书是针对近代实证科学盲目狂热的一次严肃伦理警告。十九世纪末科学界充斥着‘只要能发现新知识，任何代价都在所不惜’的狂妄思潮。威尔斯借格里芬之死警告全人类：缺乏道德灵魂指引的聪明才智，只是一头破坏力巨大的脱缰野兽。</p>

      <div class="sub-heading">警惕两种典型的浅层误读</div>
      <ul class="bullet-list">
        <li><strong>误读一：将格里芬洗白为‘被愚昧平民逼迫的悲情科学家’。</strong>文本清晰记录，格里芬在隐形前就已毫无同情心地害死亲父，在隐形后首先想到的是偷钱与享受特权，甚至毫无愧意地用铁棍打死无辜老农。他的被围剿是其累累罪行的必然正义清算。</li>
        <li><strong>误读二：将小镇平民的围捕看作‘平庸之恶对天才的谋杀’。</strong>小镇警民起初展现了极大的克制，直到格里芬开始开枪杀人、企图发动独裁政变，平民才为了保卫家园奋起自卫。这是文明共同体本能的免疫防御反应。</li>
      </ul>"""

    # 09
    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《隐形人》是<strong>互联网匿名时代最精准的预言书</strong>：<br>
      现代网络键盘侠躲在匿名的虚拟网线背后，正如同吞下了‘隐形药剂’的格里芬。当发言者确信自己不会被查出真实身份、不会当面承受社会规则与目光的制约时，网络霸凌、造谣诽谤、恶毒中伤便如同病毒般爆发。我们每天都在网络世界里目睹成千上万个‘精神隐形人格里芬’在狂怒咆哮。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>当你在网络上使用匿名账号发言时，你敲下的言辞是否比现实面对面交流时更加刻薄、残忍或不负责任？</li>
        <li>如果明天赋予你一项绝对不会被法律或摄像头查出的秘密特权，你内心的第一个念头是造福社会，还是满足私欲？</li>
        <li>你认为一个人真正的道德水平，是在聚光灯下维持的体面举止，还是在漆黑无人的私密房间里所做的选择？</li>
      </ol>"""

    # 10
    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《隐形人》不是讲超能力爽剧，而是讲特权如何把人逼疯。格里芬隐形后不仅没成神，反而要在零下寒冬裸奔、吃下的食物都能被看见。最可怕的是，当一个人做坏事不会被看见时，他立刻堕落成了杀人恶魔。它告诉我们：没有约束的自由，就是通向自毁的陷阱。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来聊科幻经典《隐形人》。如果给你一次隐形的机会，你敢要吗？威尔斯在一百多年前就给出了一个让人毛骨悚然的回答：千万不要！书里的天才物理学家格里芬真的隐形了，但他迎来的不是神一般的特权，而是生理与心理的无间地狱。首先是物理代价：大冬天他必须脱光衣服才能隐形，冻得浑身发抖；吃完饭肉还没消化，肚子里的食物悬在空中被狗追咬；雪地上的脚印随时会出卖他。更恐怖的是心理代价：古希腊柏拉图曾提出‘古各斯之戒’——如果一个人做任何事都不会被别人看见，他还会善良吗？格里芬给出的答案是‘不会’。他迅速从科学家堕落成偷窃、放火、甚至谋杀全镇居民建立‘恐怖统治’的疯子。最后打败他的，不是大炮，而是团结起来关紧门窗、在路上撒碎玻璃的普通老百姓。这本书是最好的网络时代警示录：匿名的特权，只会释放心中的野兽；唯有心怀敬畏与阳光，人类才能活得像一个人。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “隐形原本可以成为人类探索自然最奇妙的羽翼，但在自私狂妄的灵魂手中，它却沦为了一场赤身裸体的严寒苦役与自掘坟墓的杀戮狂欢。”
      </div>"""

    # 11
    sec11 = """      <div class="sub-heading">最小通达路径：如果时间有限只读精选</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第七章（客栈解开绷带）：</strong>精读格里芬当众拆开围巾假鼻、露出虚空脖颈令全村陷入恐慌溃退的惊悚一幕。</li>
        <li><strong>必读第二场 · 第十九至二十二章（肯普书房倾诉）：</strong>连续四章精读格里芬自述在伦敦地下室隐形成功、逼死父亲、大火烧房与饥寒交迫的心理堕落长卷。</li>
        <li><strong>必读第三场 · 第二十八章与尾声（泥地绝杀与日记迷思）：</strong>精读格里芬在全镇平民围攻下毙命、肉身缓缓显形的场景，以及马弗尔在偏僻旅店锁门抚摸笔记的余响。</li>
      </ul>

      <div class="sub-heading">互文与延伸阅读书单</div>
      <p>玛丽·雪莱《弗兰肯斯坦》（科学伦理与造物反噬的孪生经典） · 罗伯特·路易斯·史蒂文森《化身博士》（人性善恶二元分裂与药剂失控的惊悚先驱）。</p>"""

    # 12
    sec12 = """      <div class="card-box">
        <strong>Q1 · 知识分子的堕落：</strong>为什么格里芬拥有如此卓绝的物理天分，在人性和道德维度上却表现得连一个普通村妇都不如？这给今天的专业精英教育敲响了怎样的警钟？
      </div>
      <div class="card-box">
        <strong>Q2 · 肯普博士的选择：</strong>肯普拒绝协助格里芬，甚至不惜冒着杀身之祸作为诱饵引诱昔日同窗，他的这种‘不念旧情’在道德上算不算背叛朋友？还是对更高正义的恪守？
      </div>
      <div class="card-box">
        <strong>Q3 · 平民常识的胜利：</strong>为什么最后击毙科学超人的是一群手拿棍棒、泥水匠工具的普通平民？这体现了社会共同体法则怎样的强韧自卫本质？
      </div>
      <div class="card-box">
        <strong>Q4 · 隐形肉身的重新显形：</strong>格里芬死后，透明的肉体为何必须一点点从神经系统显露回肉身？作者通过这种生理视觉还原传达了怎样的宿命归位隐喻？
      </div>
      <div class="card-box">
        <strong>Q5 · 贪婪的永恒轮回：</strong>马弗尔在故事最后把三卷密码手稿私藏在床下，这一幕为什么比格里芬的死更加令人心惊？
      </div>"""

    # 13
    sec13 = """      <div class="sub-heading">① 思维工具：“透明度阳光测试” (The Sunlight Transparency Rule)</div>
      <p><strong>适用场景：</strong>评估某项处于灰色地带的商业策略、个人职业抉择或人际交往方案。<br>
      <strong>核心法则：</strong>当你犹豫是否可以利用某个‘无人知晓的规则漏洞或信息差’谋利时，假设明天早晨这件事情的全部聊天记录、财务流水与真实意图，都将被原封不动地公布在你最在乎的亲友同事朋友圈里。<br>
      <strong>判断准绳：</strong>如果在阳光下公布会让你感到羞耻或无地自容，那么无论目前‘隐蔽性’有多高，坚决立刻止步。</p>

      <div class="sub-heading">② 现实观察实验：“网络匿名去抑制效应体验”</div>
      <p>观察社交平台（如微博或知乎评论区）中实名认证用户与完全匿名用户的留言风格差异。记录五条恶毒攻击的评论，分析发言者如果不承担现实面孔与社交信誉惩戒时，其言辞是如何迅速跨越文明底线滑向暴虐的。</p>

      <div class="sub-heading">③ 仿写练习任务</div>
      <p>模仿威尔斯运用光学生物学原理描写超自然现象的白描手法，写一段“一个人逐渐失去实体触觉、在冰冷空气中无法抓住任何温暖物体的生理感受”片段（300字以内，不出现玄幻词汇，全用具体物理感觉词）。</p>"""

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
