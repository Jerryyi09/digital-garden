# -*- coding: utf-8 -*-
"""
Round 11: Peter Pan, Little Women, Hatchet (Target: 6000+ Chinese chars per book)
"""
import os
import sys
from bs4 import BeautifulSoup
from generate_scifi_guides import render_section, TEMPLATE_HEAD, TEMPLATE_FOOT

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def get_deep_peter_pan():
    data = {
        "title_cn": "彼得·潘",
        "title_en": "Peter and Wendy",
        "author_cn": "J·M·巴里",
        "author_en": "J. M. Barrie",
        "sub_desc": "全人类永不长大的飞翔神话 · 纯真仙境狂欢与残酷成年的永恒拔河",
        "hero_quote": "所有的孩子都会长大，除了一个人；死亡将是一场极其浩大、奇妙的冒险！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家与剧作家</div><div class="spec-val">J·M·巴里 (1860–1937)</div></div>
        <div class="spec-item"><div class="spec-label">创作与出版</div><div class="spec-val">1904年话剧首演 / 1911年长篇小说出版</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">奇幻冒险童话 / 现代成长心理寓言</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 12 万字 / 全十七章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">全年龄终生必读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">拒绝长大的无忧代价与接纳变老的深沉尊严</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿以为《彼得·潘》只是一部给低幼儿童看的快乐飞翔迪斯尼动画原型。巴里以极其沉痛甚至冰冷的心理学笔触，写下了拒绝长大的残酷代价——<strong>彼得·潘之所以永远不老，是因为他拥有不可思议的‘健忘’；他记不住任何爱过他的人，记不住刚刚发生的生死冒险，他连温迪的容颜都会在第二年彻底忘光</strong>。拒绝长大，意味着拒绝了人类真正的深情、责任与记忆。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 梦幻岛（Neverland）作为儿童潜意识的心智地理全景：</strong>梦幻岛不是一个固定的物理岛屿，而是每个孩子脑海中那张‘错综复杂的迷宫地图’——红皮肤印第安人、会唱歌的美人鱼、嗜血的海盗、长满珊瑚的礁湖。当孩子长大成人，这座岛屿的海岸线便在理性潮水下逐渐沉没。
      </div>
      <div class="card-box">
        <strong>② 虎克船长（Captain Hook）与吞下闹钟的鳄鱼：</strong>世界文学中最具惊悚象征意味的成年人隐喻。虎克风度翩翩、毕业于伊顿公学，却残暴冷酷；他一生最恐惧的不是大炮，而是那只吞了闹钟的鳄鱼——那一刻不停在肚子里发出‘滴答、滴答’的钟声，正是时间无情吞噬青春、不可逆转逼近死亡的宇宙警钟。
      </div>
      <div class="card-box">
        <strong>③ 虚掩的窗户与终局永恒的代际轮回：</strong>温迪坚信母亲会永远留着育婴室的窗户迎接他们归来，这份信任最终拯救了迷失的孩子们；而彼得·潘多年前离家出走再飞回窗前时，发现窗户已经被紧紧关死、母亲怀里抱了新的宝宝。全书终盘，长大的温迪生下女儿简，老去的温迪只能坐在壁炉旁，看着彼得潘带走自己的女儿再次飞向夜空。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        爱德华时代（20世纪初）的英国中产阶级家庭。肯辛顿花园的草坪与育婴室的严格规训，催生了巴里对失落纯真与童年飞翔神话的深刻追寻。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .pp-box { rx: 8; stroke-width: 1.5; }
            .pp-bg-peter { fill: #2a9d8f; stroke: #40916c; }
            .pp-bg-wendy { fill: #1d3557; stroke: #2a4d7a; }
            .pp-bg-hook { fill: #8c2d19; stroke: #a33b24; }
            .pp-bg-time { fill: #131619; stroke: #59645f; }
            .pp-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .pp-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .pp-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .pp-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .pp-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .pp-green { stroke: #2a9d8f; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .pp-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="pp-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 梦幻岛：彼得·潘 -->
          <rect x="20" y="25" width="210" height="115" class="pp-box pp-bg-peter" />
          <text x="125" y="52" class="pp-t-w">彼得·潘 (Peter Pan)</text>
          <text x="125" y="72" class="pp-t-sub-w">树叶秋叶衣裳 · 永不换牙不长大</text>
          <text x="125" y="90" class="pp-t-sub-w">骄傲勇敢飞翔 · 极度健忘</text>
          <text x="125" y="108" class="pp-t-sub-w">拒绝承担任何成人责任与深情</text>
          <text x="125" y="124" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">“所有的孩子都会长大，除了他”</text>

          <!-- 伦敦育婴室：温迪 (选择长大) -->
          <rect x="450" y="25" width="210" height="115" class="pp-box pp-bg-wendy" />
          <text x="555" y="52" class="pp-t-w">温迪·达林 (Wendy Darling)</text>
          <text x="555" y="72" class="pp-t-sub-w">母性本能觉醒 · 缝补彼得的影子</text>
          <text x="555" y="90" class="pp-t-sub-w">在梦幻岛扮演母亲照料迷失男童</text>
          <text x="555" y="108" class="pp-t-sub-w">清醒选择重返凡间结婚生子变老</text>
          <text x="555" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">承担爱的重负，赢得记忆的尊严</text>

          <!-- 飞翔诱惑与回归连线 -->
          <path d="M 230 82 L 450 82" class="pp-green" />
          <text x="340" y="74" style="fill:#2a9d8f; font-size:11px; font-weight:700; text-anchor:middle;">仙尘魔粉飞翔 → 虚掩之窗回归</text>

          <!-- 成年人阴暗面：虎克船长 -->
          <rect x="20" y="180" width="210" height="135" class="pp-box pp-bg-hook" />
          <text x="125" y="208" class="pp-t-w">虎克船长 (Captain Hook)</text>
          <text x="125" y="228" class="pp-t-sub-w">伊顿公学教养 · 铁钩铁腕海盗</text>
          <text x="125" y="246" class="pp-t-sub-w">残暴冷酷 · 执迷于维持‘好的风度’</text>
          <text x="125" y="264" class="pp-t-sub-w">恐惧吞了闹钟的滴答鳄鱼</text>
          <text x="125" y="280" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">被时间追杀的成年人焦虑标本</text>

          <!-- 滴答作响的死神鳄鱼 -->
          <path d="M 230 245 L 450 245" class="pp-solid" marker-end="url(#pp-arr)" />
          <text x="340" y="235" class="pp-lbl">滴答！滴答！时间追杀</text>

          <rect x="450" y="180" width="210" height="135" class="pp-box pp-bg-time" />
          <text x="555" y="208" class="pp-t-w">吞了闹钟的鳄鱼 (The Crocodile)</text>
          <text x="555" y="228" class="pp-t-sub-w">大自然冷酷时间流逝法则</text>
          <text x="555" y="246" class="pp-t-sub-w">吞下虎克一只手，紧随其后</text>
          <text x="555" y="264" class="pp-t-sub-w">终局一口将虎克吞入腹中</text>
          <text x="555" y="280" style="fill:#e0725b; font-size:10px; text-anchor:middle;">任何人终将向岁月衰老缴械投降</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>彼得·潘：</strong>世界文学中最具魅惑力但也最让人心酸的神性少年。他身上保留了全部乳牙，衣服由秋天的落叶与树浆黏成。他勇敢得不可思议，面对死亡时微笑宣称‘死亡将是一场浩大的冒险！’然而他的代价是巨大的：他没有真正的同理心，当迷失的孩子们开始变老时，他就把他们‘调换打发掉’；他每隔一段时间就会把以前发生的事忘个精光，甚至把叮当铃（Tinker Bell）忘得一干二净。他是一座没有记忆、没有负重、因而也绝不可能拥有深层幸福的金色孤岛。</li>
        <li><strong>温迪·达林：</strong>连接梦幻与现实的伟大女性原型。她拥有飞翔的渴望，但在梦幻岛上，她本能地操持起给六个男童缝补袜子、讲睡前故事、熬药的母亲职责。她最伟大的时刻是在海盗船跳板前坚决拒绝向虎克屈服，并向所有孩子宣告：‘我相信我们的妈妈一定会留着窗户！’她选择长大、选择变老、选择生下孩子坐在壁炉前看着彼得带走下一代，展现了女性接纳生命自然律动的至高尊严。</li>
        <li><strong>虎克船长：</strong>成年人精神困境的绝妙典型。他不仅是一个残酷的海盗头子，更是深具维多利亚传统精英教养的绅士。他即便在杀人时也极其讲究‘风度（Good Form）’，在临死跳入鳄鱼巨口前，看到彼得潘居然用极其不文明的手段踢他，发出了‘他真没有风度’的满足微笑从容赴死。他一生最大的折磨是那只鳄鱼肚子里传来的秒针滴答声，生动揭示了成年人对衰老、失控与死亡的终极恐惧。</li>
        <li><strong>小仙子叮当铃（Tinker Bell）：</strong>任性娇蛮的仙子化身。由于身材太小，她一次只能容纳一种感情——要么全心全意嫉妒怨恨温迪，要么毫不犹豫喝下虎克留下的毒药替彼得换命。当她因喝下毒药光芒微弱濒死时，彼得潘呼吁全天下所有相信仙子的孩子拼命鼓掌，千千万万掌声将她救活，构成了全人类戏剧史上最经典的观众互动神迹。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>伦敦达林先生一家的育婴室里，三个孩子温迪、约翰和迈克尔每晚听着母亲讲故事入睡。某天深夜，拒绝长大从家中逃跑的神秘少年彼得·潘，为了寻找自己丢失在育婴室里的影子飞入窗户，在小仙子叮当铃的协助下，用仙尘教会了三个孩子飞翔，带他们飞向‘右边第二条路一直往前走直到天亮’的梦幻岛。在梦幻岛上，生活着一群因保姆疏忽从婴儿车掉落的‘失落男童’。温迪充当起男童们的母亲，为他们做饭、缝补衣裳、在地下秘密树洞里讲述关于伦敦父母守候窗户的故事。与此同时，岛上的恶霸海盗头子虎克船长因当年被彼得潘斩断右手喂了鳄鱼，对彼得怀恨在心。在美人鱼礁湖激战后，虎克趁彼得外出，突袭捕获了全体男童与温迪，将毒药滴入彼得的水杯中。叮当铃为了救彼得抢先喝下毒药垂危，彼得呼吁全天下相信仙子的孩子热烈鼓掌救活了仙子。随后彼得单枪匹马杀上海盗船‘快乐罗杰号’，学着滴答鳄鱼的叫声吓破海盗胆，在跳板决斗中击溃虎克，将其逼入鳄鱼巨口。胜利后，温迪坚决要求带全体孩子重返伦敦现实世界。达林太太的育婴室窗户果然为孩子们永远敞开着，达林夫妇收养了全部失落男童。彼得·潘拒绝被收养，独自飞回梦幻岛。多年后，温迪长大成人结婚生子，老去的温迪坐在壁炉旁，看着不老不死的彼得潘再次飞入窗户，带走她同样渴望飞翔的小女儿简。故事在代际轮回中永恒流转。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“成长的本质代价，以及人类在留恋无忧童年与勇敢承担成年责任之间的永恒精神撕扯”</strong>。巴里向全人类证明：长大的过程必然伴随着飞翔能力的丧失、纯真幻想的消退与衰老死亡的威胁，但唯有通过接纳长大，人类才能拥有深刻的爱、忠诚的家庭纽带与生命的代际传承。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一场在午夜月光与仙尘闪耀中划过伦敦大本钟穹顶的飞翔之梦：在极尽欢快奇绝的童话冒险深处，尝到一丝成年人回望童年时无法挽回的凄美与泪水。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个在猛然发现自己不再年轻、在现实的繁重责任中感到疲惫，渴望在心底保留一扇永远虚掩的‘育婴室窗户’的成年人。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以彼得·潘为代表的拒绝承担责任、沉湎永恒童稚与绝对遗忘之自由 vs 以温迪和达林家庭为代表的接纳成长、承担牵绊、拥有深情记忆的现实人间。</strong></p>

      <div class="sub-heading">全书戏剧推进链条</div>
      <ol class="num-list">
        <li><strong>第一幕 · 影子的缝合与飞翔之夜（第一至四章）：</strong>达林家严苛的账目开支；纽芬兰保姆狗娜娜的抗议；彼得潘寻找影子并由温迪用针线缝回脚跟；撒下仙尘飞向第二颗星辰。</li>
        <li><strong>第二幕 · 梦幻岛地下树洞家园（第五至八章）：</strong>叮当铃出于嫉妒诱导男童向温迪射箭遭训斥；地下树洞各人专属的进出口；温迪扮演母亲讲故事。</li>
        <li><strong>第三幕 · 美人鱼礁湖激战（第九至十一章）：</strong>拯救印第安虎莲公主；彼得潘受困礁石宣告‘死亡是一场浩大冒险’；鸢尾鸟巢充当救生圈脱险。</li>
        <li><strong>第四幕 · 母亲的故事与海盗偷袭（第十二至十五章）：</strong>温迪执意要回伦敦，讲述母亲永远虚掩的窗户；虎克突袭捕获全体孩子；叮当铃舍命替彼得喝毒药，全宇宙掌声救活仙子。</li>
        <li><strong>第五幕 · 海盗船决战与代际轮回（第十六至十七章）：</strong>彼得假扮鳄鱼滴答声登船；跳板厮杀逼死虎克；重返伦敦温存团圆，达林夫妇收养孤儿；多年后温迪变老，彼得带走女儿简飞向未来。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第十四章小仙子叮当铃毫不犹豫喝下整杯毒药：</strong>这只平日里任性刻薄、甚至险些害死温迪的小仙子，在发现虎克留下的毒药即将被彼得端起的一瞬间，用自己的小身躯撞开杯子喝光毒汁。她的光芒在刹那间暗淡如垂死火星，逼迫彼得在全宇宙面前求告掌声。这一幕证明了哪怕是虚构的神仙世界，爱的神圣同样需要以无保留的牺牲为代价。
      </div>"""

    sec05 = """      <div class="sub-heading">彼得·潘的‘健忘症’：残酷的无龄代价</div>
      <p>巴里在第十七章写下了全书最令人战栗的真相：当温迪第二年满怀期待地等待彼得接她去打扫春季木屋时，彼得迟到了整整一年；而当他终于飞来时，温迪激动地提起虎克船长、提起叮当铃，彼得却一脸茫然：‘虎克是谁？我不记得了，我杀过的人太多了；叮当铃？我想她大概是死了吧，仙子的寿命本来就不长。’那一刻，温迪如遭雷击。彼得潘的不老不是奇迹，而是一种<strong>‘灵魂无法沉淀任何记忆与重量的病态残疾’</strong>。长大的本质是承担记忆的痛苦，拒绝记忆的人，永远无法建立真正的深情。</p>

      <div class="sub-heading">达林先生住进狗窝的忏悔行为艺术</div>
      <p>达林先生在孩子们失踪后做出的荒诞举动极具深度：因为自责当年为了省钱把保姆狗娜娜拴在院子里导致孩子被拐走，达林先生发誓在孩子们回家之前，自己绝不走出狗窝。他甚至每天让人抬着狗窝去证券公司上班、在狗窝里签字办公，引来全伦敦市民的围观与同情。巴里借这个滑稽可笑的举动，写透了维多利亚父亲在严肃面具下深藏的深沉内疚与对家庭的笨拙挚爱。</p>"""

    sec06 = """      <div class="sub-heading">爱德华时代最精妙的旁白反讽文风</div>
      <p>巴里的叙述者语调如同一个坐在壁炉前微笑着给孩子讲故事、却冷不丁向身旁的大人眨眨眼睛的老绅士。他的文字在极度天真烂漫的童话想象与极其辛辣的世态讽刺之间自由跳跃。全书充斥着诸如‘达林太太的大脑整理法（把不听话的想法折叠塞进角落）’等天才般的心理学隐喻，构成了现代成人寓言的至高范本。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>被针线缝在脚后跟的影子 (The Shadow)：</strong>全书开篇的标志性道具。影子代表<strong>一个人在现实世界里的沉重实体与身份证明</strong>。彼得潘进屋找影子，象征他虽然渴望无拘无束，但依然在潜意识里渴望被尘世的实体所锚定。</li>
        <li><strong>虚掩的育婴室窗户 (The Open Window)：</strong>全书最高的亲情圣坛。只要这扇窗户还虚掩着，母亲的怀抱就永远为流浪的孩子敞开；而彼得潘当年遭遇的‘紧闭的铁窗’，则成为了人类所有被遗弃创伤的原型。</li>
        <li><strong>仙尘与快乐的思想 (Fairy Dust and Happy Thoughts)：</strong>飞翔的唯二条件。‘只要身上撒了仙尘，并且心里想着最快乐的事情，你就能飞起来。’它象征着<strong>唯有彻底卸下功利算计与沉重怨恨的心灵，才能拥有在现实重力之上翱翔的自由</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（经典儿童奇幻冒险）：</strong>三个伦敦孩子随神秘飞行少年飞往梦幻岛，击败海盗虎克船长，最终平安返家被领养的大团圆童话。<br>
        <strong>深层架构（成长心理学寓言）：</strong>对人类告别童年、迈入成年社会过程中心灵剧烈阵痛的深度解剖。证明长大的过程必然伴随着失落，但承担家庭责任与爱是生命不可逃避的成熟使命。<br>
        <strong>根本架构（时间与存在的形而上悲歌）：</strong>不老神话背后的残酷遗忘本质。人类以接受衰老与死亡为代价，换取了深沉的爱、记忆与代际传承的至高尊严。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>巴里在去世前将《彼得·潘》的全部版权无偿捐赠给了伦敦大奥蒙德街儿童医院（Great Ormond Street Hospital），使这本小说在此后的近一个世纪里，救治了成千上万名真实患病的弱小儿童。这成为了世界文学史上最美丽、最神圣的一场现实‘梦幻岛救赎’。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《彼得·潘》在现代心理学中命名了著名的<strong>‘彼得·潘综合征（Peter Pan Syndrome）’</strong>：<br>
      今天无数三十岁、四十岁的成年人，虽然肉体已经成熟，但在心智上拒绝承担婚姻、抚养孩子与面对现实困难的责任。他们沉迷于二次元、打游戏、逃避一切严肃承诺，将自己关在现代都市的‘地下树洞’里。巴里在一百年前就点醒了这群巨婴：你可以拒绝长大，但你必须做好成为一个没有记忆、没有深情、孤零零看着世界流逝的彼得潘的准备。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的日常生活和职业生涯中，你是否也有某些时刻在试图逃避‘一个成年人必须承担的硬核责任’，寄希望于天上掉下仙尘替你摆平？</li>
        <li>如果给你一个机会永远停留在无忧无虑的十二岁，但代价是必须忘记你在此后人生中所深爱过的人，你是否愿意接受？</li>
        <li>我们该如何像温迪那样，既能勇敢在现实中承担变老的责任，又在心底为那个飞翔的彼得潘留下一扇虚掩的窗？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《彼得·潘》绝不是只给小孩子看的小飞侠。它讲的是全人类最心酸的成长真相：一个不肯长大的男孩虽然能在天上飞，但他连昨天爱过谁都会忘光。最后所有孩子都选择变老回家，只有他留在了仙境。它告诉你：长大的代价是失去飞翔，但换来了深情与记忆。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来重新认识世界童话王冠上的绝代名篇——J·M·巴里的《彼得·潘》。几乎所有人都知道那个会飞的小男孩，但很少有人读懂这本书第一句话的悲凉：‘所有的孩子都会长大，除了一共人。’彼得·潘飞进伦敦一户人家的育婴室，教三个孩子撒上仙粉飞向梦幻岛。在那个岛上，有美人鱼、有印第安人，还有坐着海盗船到处抓人的恶霸虎克船长。这个虎克船长有个奇特的毛病，他谁都不怕，就怕一只吞了闹钟的鳄鱼，因为那只鳄鱼肚子里‘滴答、滴答’的钟声，代表着时间在追杀每一个变老的人。大姐温迪在岛上给失落的男童当妈妈，缝袜子熬药讲故事。在海盗船大决战里，彼得击败了虎克船长，大获全胜。这时候，所有孩子面临一个终极选择：是在这个没有考试、没有作业、永远长不大的仙岛留一辈子，还是回家？温迪给出了一个勇敢的答案：她要回家！因为她相信妈妈的窗户永远为他们留着缝。回到伦敦后，孩子们全被领养，慢慢长大、升学、变老、有了皱纹。唯独彼得潘拒绝被收养，独自飞回了梦幻岛。最心酸的一幕在小说最后：多年后，温迪已经成了满头银发的老太太，彼得再次从窗户飞进来找她打扫房间，看见老去的温迪，彼得吓哭了。彼得把长大的温迪当成了一个陌生人，转头带走了温迪年幼的小女儿简飞向天空。巴里借这个故事告诉我们：拒绝长大看起来很美，但代价是绝对的健忘与孤独；敢于变老、敢于在琐碎人世间承担责任、去爱身边的人，才是人类最伟大的冒险。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “所有的孩子都会长大，除了一具永远停在昨日风中的影子；而长大的全部勇气，正在于我们敢于走出虚掩的窗户，拥抱带有时钟滴答声的人间。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界成长心理神话巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一至二章（育婴室之窗与飞翔之夜）：</strong>精读达林太太整理大脑抽屉的绝妙隐喻，以及彼得进屋寻找影子的开场。</li>
        <li><strong>必读第二场 · 第十四章（叮当铃舍身喝毒药）：</strong>全人类戏剧史最动人的互动段落，精读全宇宙掌声唤醒垂危仙子的奇迹。</li>
        <li><strong>必读第三场 · 第十五章（海盗船甲板决斗）：</strong>精读滴答鳄鱼逼近、虎克在跳板前注视彼得从容受死的终极哲学反讽。</li>
        <li><strong>必读第四场 · 第十七章（温迪变老与终极告别）：</strong>精读全书最后三页，体会人类生命在代际轮回中无可奈何却神圣庄严的挽歌。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 健忘作为惩罚：</strong>彼得潘的不老以‘记不住过去’为代价，这种遗忘究竟是大自然给予他的保护，还是一种剥夺其作为人的深层体验的残酷诅咒？
      </div>
      <div class="card-box">
        <strong>Q2 · 虎克船长的阶级风度：</strong>虎克直到被踢下鳄鱼巨口前依然在执着于‘好的风度（Good Form）’，这种爱德华时代的绅士执念揭示了英国阶级教育怎样的深层荒谬？
      </div>
      <div class="card-box">
        <strong>Q3 · 温迪的选择之重：</strong>温迪选择告别能够自由飞翔的梦幻岛回到凡间结婚生子，这是一种向世俗平庸的妥协，还是一种更高维度的生命成熟？
      </div>
      <div class="card-box">
        <strong>Q4 · 母亲的窗户悖论：</strong>达林太太一直开着窗户，而彼得潘的母亲早就关上了窗户并生了新婴儿。原生家庭的接纳与否，在多大程度上决定了一个人是勇敢走向社会还是终生退行在仙境？
      </div>
      <div class="card-box">
        <strong>Q5 · 死亡即浩大冒险：</strong>彼得潘在礁石上面对涨潮时说‘死亡将是一场浩大的冒险’，这句话为什么被列为全书最具存在主义震撼力的名言？
      </div>"""

    sec13 = """      <div class="sub-heading">① 心理断乳实践工具：“虚掩之窗自我复位模型” (The Open Window Reality Protocol)</div>
      <p><strong>适用场景：</strong>当你面临重大职场跳槽、自立门户、或者是从父母家中独立搬出时，内心充满对舒适圈的不舍与对外界残酷竞争的恐惧退行时。<br>
      <strong>第一步（告别梦幻岛）：</strong>向自己坦白：无论当年的学生时代或父母庇护有多么美好，那座‘不用交房租、没有考核’的梦幻岛已经不可逆转地沉没了；<br>
      <strong>第二步（带上飞翔的记忆）：</strong>不要把进入成年社会当成‘出卖灵魂’，带着当年那份纯真的好奇心与正义感，把它转化为工作中的创造力武器；<br>
      <strong>第三步（自己成为那扇窗）：</strong>像长大后的温迪一样，不再一味索取别人的庇护，而是用自己的肩膀为下一代搭建一个永远充满接纳与温暖的安稳港湾。</p>

      <div class="sub-heading">② 现实观察实验：“生活中的彼得·潘与鳄鱼觉察”</div>
      <p>观察身边某个三十岁以上依然拒绝工作、生活起居完全依赖年迈父母包办的朋友，记录他在言谈中表现出的‘对现实规则的极端逃避与对童年特权的执念’，体会巴里笔下‘没有长大者的真实残酷性’。</p>

      <div class="sub-heading">③ 童话元叙事仿写任务</div>
      <p>模仿巴里那种半带调侃、半带神圣诗意的叙述者语调，描写一个‘三十五岁职员在加班深夜的写字楼电梯里，突然从公文包夹层摸出一颗多年前收集的旧玻璃弹珠’的微型场景（350字以内，在平庸写字楼中唤醒一丝飞翔的余韵）。</p>"""

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

print("Round 11 deep Peter Pan ready.")

def get_deep_little_women():
    data = {
        "title_cn": "小妇人",
        "title_en": "Little Women",
        "author_cn": "路易莎·梅·奥尔科特",
        "author_en": "Louisa May Alcott",
        "sub_desc": "世界女性成长与家庭伦理的至高明珠 · 独立、亲情与自我价值的寻觅长卷",
        "hero_quote": "我不相信女人活着只是为了结婚生子；我们有思想，有灵魂，有雄心，也有才华！我厌恶那些口口声声说‘女人唯一的归宿就是婚姻’的傲慢说辞！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家</div><div class="spec-val">路易莎·梅·奥尔科特 (1832–1888)</div></div>
        <div class="spec-item"><div class="spec-label">出版年代</div><div class="spec-val">1868–1869 年分两卷出版 / 畅销传世</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">半自传体家庭成长小说 / 女性主义启蒙经典</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 30 万字 / 全四十七章</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">10+ 岁 / 全年龄终生必读经典</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">女性经济与精神自立探索及家庭伦理温暖度</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《小妇人》轻视成一部‘四姐妹围着壁炉家长里短、绣花刺绣的甜美淑女鸡汤’。奥尔科特是美国超验主义大师爱默生与梭罗的亲炙弟子，一生坚持不婚与废奴主义。二女儿乔·马奇身上跳动着十九世纪最强悍的<strong>女性独立反叛烈火</strong>——她剪掉心爱的秀发换钱补贴家用、独自奔赴纽约从事职业写作、断然拒绝英俊富二代劳里的求婚并坚持以笔杆子养活自己。这是一部在清贫中挺起女性尊严脊梁的伟大现实主义丰碑。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 清贫之中开出的崇高人道主义分享之花：</strong>第一卷开篇经典的圣诞节早晨：四个姑娘在寒冬中醒来，没有一件昂贵的礼物，唯一丰盛的早餐是一盘奶油面包与热茶。然而当得知附近贫民窟一位德国母亲带着六个啼饥号寒的婴儿无以为食时，四姐妹在母亲的提议下毫不犹豫地端起全部早餐，穿越积雪送往陋室。这种在匮乏中依然选择慷慨的精神富有，奠定了全书最坚固的道德基石。
      </div>
      <div class="card-box">
        <strong>② 乔对青梅竹马劳里深情求婚的理智决绝拒绝：</strong>全书情感冲突最高潮。劳里出身豪门、英俊潇洒，对乔爱得毫无保留；世俗眼光认为乔理所应当抓住这根豪门橄榄枝一举翻身。然而乔极其清醒地拒绝了他：‘我们俩性格都太刚烈、太固执，如果结合只会成为灾难！我爱你，但那是像对待兄弟一样的爱，我绝不能欺骗你、出卖我自己的心！’这种对自我天性与他人负责的诚实，超越了世俗一切功利罗曼蒂克。
      </div>
      <div class="card-box">
        <strong>③ 三女儿贝丝之死所凝聚的无私圣洁之光：</strong>柔弱羞怯的贝丝是全家的精神胶水。她在照顾贫民婴儿时染上猩红热，经历数年残喘病榻，在二十岁前夕安详闭上双眼。正是贝丝那份‘默默坐在角落为所有人弹琴祈祷、不求任何掌声’的无言圣洁，促使乔彻底放弃了取悦市场恶俗的廉价惊悚小说写作，开始挖掘自己内心深处最真诚的家庭记忆，迎来了文学创作的终极破茧。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        1860年代美国南北战争后方的马萨诸塞州康科德小镇。超验主义哲人爱默生、梭罗是奥尔科特一家的座上宾，清贫自立、反对奴役与崇尚劳动的精神氛围滋润着马奇家四个女孩的成长。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .lw-box { rx: 8; stroke-width: 1.5; }
            .lw-bg-jo { fill: #8c2d19; stroke: #a33b24; }
            .lw-bg-meg { fill: #1d3557; stroke: #2a4d7a; }
            .lw-bg-beth { fill: #2a9d8f; stroke: #40916c; }
            .lw-bg-amy { fill: #242930; stroke: #59645f; }
            .lw-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .lw-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .lw-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .lw-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .lw-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .lw-blue { stroke: #1d3557; stroke-width: 2; fill: none; }
            .lw-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="lw-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 大姐：梅格 (Meg) -->
          <rect x="20" y="25" width="145" height="120" class="lw-box lw-bg-meg" />
          <text x="92" y="52" class="lw-t-w">大姐：梅格 (Meg)</text>
          <text x="92" y="72" class="lw-t-sub-w">端庄典雅长女</text>
          <text x="92" y="90" class="lw-t-sub-w">曾慕虚荣丝绸</text>
          <text x="92" y="108" class="lw-t-sub-w">嫁清贫家庭教师布鲁克</text>
          <text x="92" y="126" style="fill:#cad5e2; font-size:10px; text-anchor:middle;">在平淡琐碎中体味真爱</text>

          <!-- 二姐：乔 (Jo · 灵魂主角) -->
          <rect x="180" y="25" width="150" height="120" class="lw-box lw-bg-jo" />
          <text x="255" y="52" class="lw-t-w">二姐：乔 (Jo)</text>
          <text x="255" y="72" class="lw-t-sub-w">假小子 · 独立作家原型</text>
          <text x="255" y="90" class="lw-t-sub-w">剪发救父 · 拒嫁富少劳里</text>
          <text x="255" y="108" class="lw-t-sub-w">阁楼伏案 · 笔耕不辍自立</text>
          <text x="255" y="126" style="fill:#f0dcd8; font-size:10px; font-weight:700; text-anchor:middle;">打破女性藩篱的先驱之魂</text>

          <!-- 三姐：贝丝 (Beth) -->
          <rect x="345" y="25" width="150" height="120" class="lw-box lw-bg-beth" />
          <text x="420" y="52" class="lw-t-w">三姐：贝丝 (Beth)</text>
          <text x="420" y="72" class="lw-t-sub-w">音乐天使 · 羞怯博爱</text>
          <text x="420" y="90" class="lw-t-sub-w">染病体衰 · 默默守护全家</text>
          <text x="420" y="108" class="lw-t-sub-w">二十岁前夕安详离世</text>
          <text x="420" y="126" style="fill:#d8f3dc; font-size:10px; text-anchor:middle;">全家永恒的精神灯塔</text>

          <!-- 小妹：艾米 (Amy) -->
          <rect x="510" y="25" width="150" height="120" class="lw-box lw-bg-amy" />
          <text x="585" y="52" class="lw-t-w">小妹：艾米 (Amy)</text>
          <text x="585" y="72" class="lw-t-sub-w">金发画家 · 追求优雅</text>
          <text x="585" y="90" class="lw-t-sub-w">从任性自私到成熟通透</text>
          <text x="585" y="108" class="lw-t-sub-w">欧洲游历成长 · 结合劳里</text>
          <text x="585" y="126" style="fill:#cad5e2; font-size:10px; text-anchor:middle;">世俗美感与高贵结合</text>

          <!-- 下方：马奇太太与家庭核心法则 -->
          <rect x="150" y="195" width="380" height="115" class="lw-box" style="fill:#fbf9f4; stroke:#1c221e; stroke-width:2.2;" />
          <text x="340" y="225" class="lw-t-d">马奇太太 (Marmee) 与精神家园城堡</text>
          <text x="340" y="248" class="lw-t-sub">‘我宁愿你们成为贫穷而幸福受尊重的妻子，也不愿你们为了豪门出卖尊严’</text>
          <text x="340" y="270" class="lw-t-sub">劳里少爷：在四姐妹的真诚中找到心灵家园 · 巴尔教授：智识导师与平实伴侣</text>
          <text x="340" y="292" style="fill:#8c2d19; font-size:10.5px; font-weight:700; text-anchor:middle;">苹果园梅花树下的丰盛大和解：爱比财富更坚固</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>乔·马奇（Jo March）：</strong>路易莎·梅·奥尔科特的自画像化身。她个性刚烈、爱憎分明，痛恨一切装腔作势的闺秀作派。面对南北战争前线父亲病危的噩耗，她独自跑去理发馆剪掉引以为傲的及腰浓密褐色长发卖了二十五美元充当母亲的路费，在深夜里默默抓着剪碎的头发哭泣。在纽约家庭旅馆，面对德国贫困学者巴尔教授对她撰写耸人听闻黄色通俗小说的直率批评，她毫不留情地将全部手稿投进壁炉，重新在纯净的平实真情中确立写作天命。她打破了女作家只能写言情小说的偏见，用稿酬赎回了全家人的幸福。</li>
        <li><strong>梅格（Meg）：</strong>传统女性在虚荣与真诚之间的成长标本。作为长女，她最记得当年家庭富有时的华丽体面，去富家小姐做客时曾为穿借来的紧身低胸礼服、涂脂抹粉而感到羞愧。在面对贫穷但正直诚实的家庭教师约翰·布鲁克的求婚时，她顶住了虚荣老姑婆‘敢嫁穷鬼就取消全部遗产’的威胁，毅然选择清贫婚姻，在柴米油盐与育儿琐碎中找到了坚实的人间安稳。</li>
        <li><strong>艾米（Amy）：</strong>全书最受争议也最具现实自洽性的女性。她幼时任性虚荣，曾因乔不带她去看戏把乔费尽心血的手写稿投进火炉烧毁；但她在成长中拥有惊人的自省学习能力。在欧洲游学时，她清醒地认识到自己成不了像拉斐尔那样的顶尖画家，果断放弃了二流平庸的艺术执念；在面对劳里因失恋而自暴自弃放浪形骸时，她像当头棒喝般痛斥劳里，促使劳里重新振作，最终二人水到渠成结为伉俪。</li>
        <li><strong>弗里茨·巴尔教授（Professor Bhaer）：</strong>中年德语哲人。贫穷、朴素、头发蓬乱、大衣磨破了边，但在破旧的外表下拥有一颗崇高饱满、饱读诗书的博爱之心。他是全书唯一能指出乔在文学与道德上的盲区、并与乔在精神层面上完全平起平坐的智识导师。他在雨中撑着破伞向乔求婚的一幕，是世界文学中最质朴动人的知己结合。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>南北战争期间，马奇牧师奔赴前线充当随军牧师，马奇太太带着四个性格迥异的女儿梅格、乔、贝丝和艾米，在马萨诸塞州过着清贫艰苦的日子。圣诞节清晨，四姐妹把唯一的黄油面包早餐送给贫困产妇；隔壁富豪劳伦斯老先生深为感动，回赠盛大晚宴，四个女孩由此结识了英俊孤单的邻家少爷劳里，建立了终身深厚的友谊。大姐梅格经历了虚荣舞会的诱惑后，拒绝豪门诱惑嫁给了清贫诚实的家庭教师布鲁克；二姐乔立志成为自食其力的独立作家，在父亲病危时毅然剪发卖钱救急；老三贝丝在照料病童时染上猩红热险些丧命；老四艾米因烧毁乔的手稿险些在薄冰上溺水，姐妹在风波中学会宽恕。战后父亲平安归来，劳里向朝夕相处的乔深情求婚，乔深知二人性格刚烈绝不适合，坚决拒绝了求婚并远赴纽约独立谋生。在纽约，乔结识了贫困博学的巴尔教授，在教授指点下放弃低俗惊悚小说写作，开始真诚自省。此时家乡传来噩耗：身体虚弱的贝丝病危，乔火速赶回家中陪伴妹妹度过了最后的纯洁岁月。艾米随姑妈游历欧洲学习绘画，重遇在欧洲消沉浪荡的劳里，艾米的一番当头痛斥唤醒了劳里，两人在岁月中渐生情愫并于伦敦成婚。失去贝丝与挚友的乔在阁楼上挥泪写下怀念妹妹与家庭故事的平实小说《小妇人》，一举轰动文坛。最终，巴尔教授赶赴马奇家在雨中向乔求婚，马奇姑婆死后将豪华的梅花庄园遗赠给乔，乔与巴尔教授创办了一座崇尚自由与品格教育的普拉姆菲尔德男子寄宿学校，全家老小在硕果累累的苹果园里举行欢庆盛宴，向伟大的母亲献上无尽的敬爱与感恩。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处严肃探究的是<strong>“女性在没有继承权与经济依附的男权时代，如何既不放弃亲情与家庭的温柔滋养，又能在精神与经济上建立起完全属于自己的独立主体性”</strong>。奥尔科特证明：女性的人生有成千上万种可能，没有哪一种模式是唯一的标准答案；无论选择走进家庭还是投身写作，只要出自独立的自主意志，就拥有无上的尊严。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一捧在严冬壁炉旁烘得暖暖的粗布毛毯：在四姐妹的欢声笑语、眼泪与争吵中，感受家庭之爱如何在清贫的霜雪中织成一座抵御人世一切寒潮的最坚固城堡。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个曾对未来感到迷茫、在现实妥协与自我志向之间寻找平衡点，渴望在家庭纽带中汲取无私温暖力量的青年女性与所有家庭成员。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>以乔为代表的女性自我价值实现与经济精神自立追求 vs 维多利亚传统男权社会将女性局限于‘贤妻良母与联姻商品’的狭隘规训。</strong></p>

      <div class="sub-heading">全书双卷成长史诗推进链条</div>
      <ol class="num-list">
        <li><strong>第一卷上 · 阁楼秘密与邻家少年（第一至十章）：</strong>圣诞清晨送早餐；劳里少爷跨入家门；乔在阁楼伏案啃苹果写剧本；艾米烧手稿引发溜冰落水危机。</li>
        <li><strong>第一卷下 · 剪发救父与风雪试炼（第十一至二十三章）：</strong>前线急电父亲病危，乔剪发换二十五美元；贝丝初染猩红热命悬一线；父亲平安归家，梅格订婚初显成人端倪。</li>
        <li><strong>第二卷上 · 婚嫁纷飞与纽约出走（第二十四至三十四章）：</strong>梅格简朴大婚；乔拒绝劳里求婚引发家庭情感地震；远走纽约任家庭教师，结识巴尔教授；焚毁低俗手稿重归真诚。</li>
        <li><strong>第二卷下 · 贝丝归天与苹果园圆满（第三十五至四十七章）：</strong>重病返乡陪伴贝丝咽气；艾米欧洲点醒劳里并大婚归国；乔写下《小妇人》名满天下；巴尔教授雨中撑伞求婚；梅花山庄开辟平民学校，秋日苹果园终极大合唱。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第二卷第十一章劳里在山坡上向乔正式求婚被拒：</strong>这是全书打破传统言情套路最决绝的一笔。如果乔为了金钱或虚荣顺水推舟嫁给全县最抢手的劳里少爷，她的人生将沦为一个依附于豪门阔太的庸俗贵妇；乔的拒绝虽令读者心碎，但彻底确立了女性必须诚实对待自身独立灵魂的至高尊严。
      </div>"""

    sec05 = """      <div class="sub-heading">贝丝的死：静穆博爱的神圣隐喻</div>
      <p>贝丝是全书唯一没有宏大世俗野心的女儿。她害怕陌生人，喜欢躲在家里给破布娃娃做衣服，弹奏那架走调的旧钢琴。然而，正是她身上的‘零功利心’，成为了四姐妹激烈个性碰撞时的减震器。当她知道自己命不久矣时，她平静地对乔说：‘我从来不觉得自己能在世界上干出什么大事业，我生来就是留在家里的；现在我要走了，但别为我哭泣，因为我的一生充满了爱。’贝丝的离世，带走了马奇家童年时代的最后一片落叶，促使乔、梅格与艾米真正告别了青春期盲目争吵，成熟地承担起成年人的生命重负。</p>

      <div class="sub-heading">马奇太太的愤怒哲学：最深沉的克己教养</div>
      <p>第八章艾米烧毁手稿后，马奇太太向自责脾气暴躁的乔吐露了一个惊人秘密：‘乔，你以为我天生就是这样温和有耐心吗？其实我几乎每天都在发脾气，我天生比你还要暴躁！但我用了四十年的时间，才学会把那股冲动的怒火在舌尖上压下去！’这种母亲与女儿之间完全不平行的坦诚灵魂交流，展示了超验主义家庭教育的最高典范——不是要求孩子成为无菌圣人，而是教会孩子在认清自身弱点后，用一生的自律去驯服内心的恶魔。</p>"""

    sec06 = """      <div class="sub-heading">家常日记体与超验主义自然哲学的融合文风</div>
      <p>奥尔科特的文字极其明澈、家常、充满烟火气。她大量使用当时新英格兰乡村的方言俗语、家庭秘密代号与生动的对话描写。然而在朴素的外表下，处处流淌着爱默生关于‘精神自立’与梭罗关于‘自然简单生活’的深刻哲学回响，使这本小说在欢快通俗的剧情深处，散发出深厚的思想底蕴。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>阁楼上的书桌与那顶插羽毛的天鹅绒软帽：</strong>乔的专属创作圣地。每当戴上这顶帽子，乔就进入了神圣不可侵犯的‘创造狂热期’。它象征着<strong>女性争取属于自己的独立精神空间与职业尊严的最初阵地</strong>。</li>
        <li><strong>剪下卖掉的浓密褐色秀发：</strong>维多利亚时代女性世俗美貌与闺秀体面的唯一标志。乔为了给病危父亲筹措路费果断剪发，象征<strong>真正的孝道与亲情，敢于把一切虚荣外壳踩在脚下</strong>。</li>
        <li><strong>普拉姆菲尔德庄园的苹果树林：</strong>全书终局四姐妹带着丈夫儿女采摘红苹果的盛大空间。金黄的落叶与熟透的果实，象征<strong>四姐妹经历了青春的阵痛与选择后，各自在生命的大地上结出的成熟饱满的精神果实</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（家庭生活世态长卷）：</strong>十九世纪南北战争后方清贫家庭中，四姐妹各自探索婚姻、事业、艺术与生死的温馨家庭故事。<br>
        <strong>深层架构（女性自主与经济自立）：</strong>对十九世纪女性唯一出路是‘攀附豪门’传统的全面解构。证明女性依靠自己的双手、智慧与劳动同样能够赢得尊严与繁荣。<br>
        <strong>根本架构（家庭爱的救赎力量）：</strong>面对贫困、战争、疾病与死亡，人类唯一的自愈庇护所就是家庭内部无保留的包容、牺牲与爱意凝聚。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>著名女权主义评论家伊莱恩·秀华特（Elaine Showalter）在《她们自己的文学》中指出：‘乔·马奇是整个十九世纪美国文学中最重要的女性文学英雄。她激励了包括西蒙娜·德·波伏娃、格特鲁德·斯泰因在内的整整三代现代杰出女性拿起笔杆子打破沉默。’这部小说是现代职业女性精神启蒙的真正源头。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>《小妇人》在今天的女性成长与家庭关系中依然具有极高指导价值：<br>
      今天无数年轻女性在‘搞事业还是顾家庭’、‘做独立大女主还是过平静日子’之间深陷焦虑内耗。四姐妹用各自的人生给出了答案：梅格选择家庭没有错，艾米选择艺术与财富没有错，乔选择边带娃边办学写作也没有错。关键不在于你选了哪条路，而在于这是不是你内心真正清醒自愿的选择。《小妇人》教会现代人：尊重每一种女性的人生选择，守住亲情的温度。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的家庭关系中，当面临重大经济或生活困境时，你们家人之间展现出的是互相推诿指责，还是像马奇家那样紧紧抱团共同扛过难关？</li>
        <li>面对身边那些并不想走‘结婚生子’主流轨道的女性朋友，你是否能给予她们像马奇太太那样的充分尊重与无条件理解？</li>
        <li>在你的青春记忆中，是否也曾因为一时的脾气冲动（如艾米烧手稿）给挚爱之人造成过巨大的伤痛？你后来是如何完成和解与弥补的？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《小妇人》是全世界所有女孩的成长圣经。四个性格完全不同的亲姐妹，在穷得揭不开锅的日子里抱团取暖。假小子二姐剪掉秀发卖钱救父亲，拒绝富二代求婚自己去大城市写作成名。它告诉你：女人活着不是为了取悦别人，有野心、有才华、有家人的爱，你就是最了不起的大女主。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来重温一部温暖了全世界一个半世纪的传世名著——路易莎·梅·奥尔科特的《小妇人》。故事发生在美国南北战争时期，老父亲上前线打仗去了，家里穷得叮当响。妈妈带着四个女儿：大姐梅格爱美想穿高档衣服，二姐乔是个一头乱发想当大作家的假小子，三妹贝丝是个害羞温柔弹钢琴的天使，小妹艾米爱画画满脑子傲气。在战争清贫的年月里，四个女孩为了省钱自己做衣服、演话剧。当得知前线父亲病重缺医药费时，二姐乔一句话没说，独自跑去理发馆剪掉了一头浓密的长发卖了二十五块钱给妈妈当路费，晚上躲在被窝里偷偷摸着秃头掉眼泪。隔壁大豪门的贵公子劳里被这四个活泼纯真的女孩吸引了，疯狂爱上了乔。在山坡上，劳里掏心掏肺向乔求婚，说要给她一辈子的豪门富贵。换作别人早就乐疯了，但乔清醒地拒绝了他，说‘我们俩脾气都太硬，如果结婚只会变成冤家，我必须自己去写小说！’乔独自背着箱子去了纽约当家庭教师，靠双手敲稿费养活自己。后来家里出事了，善良的三妹贝丝染上热病去世，乔赶回家中抱着冰冷的妹妹心碎大哭。在痛苦中，乔不再去迎合市场写那些虚假的惊悚小说，而是坐在阁楼的苹果箱上，眼含热泪写下了四姐妹从小到大的真实生活。这本小说一出版就轰动了全美。最后，当年求婚被拒的劳里在欧洲游学中看清了现实，娶了同样追求艺术的小妹艾米；而乔在雨中遇到了那个真正懂她文学才华的穷教授巴尔。姑婆去世后把大庄园留给了乔，乔把庄园改成了专门给穷苦男孩读书的学校。在全书最后，一家人在结满红苹果的果园里聚会，妈妈流着眼泪看着四个女儿各自闯出了充实的人生。奥尔科特用这本小说告诉全天下所有的女性：在这个世界上，从来没有什么‘女人唯一必须走的路线’；只要你保有爱、勇敢去闯，你的双手就能创造出属于你自己的尊严与幸福。”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “无论人间的风霜有多么刺骨，只要在家庭的壁炉旁依然拥有一双愿意为你拂去雪花的双手，生命就永远拥有战胜一切寒潮的勇气。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界女性成长小说巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一卷第一章（圣诞清晨转赠早餐）：</strong>精读四姐妹在清贫饥饿中把唯一奶油面包送往贫民陋室的高尚开场。</li>
        <li><strong>必读第二场 · 第一卷第十五章（乔剪发换钱救父）：</strong>世界文学史最动人的孝道场次，细读短发少女在深夜里的无声抽泣。</li>
        <li><strong>必读第三场 · 第二卷第十一章（山坡上坚决拒绝劳里求婚）：</strong>精读乔为了守住心智独立与彼此长远幸福拒绝豪门的大女主高光时刻。</li>
        <li><strong>必读第四场 · 第二卷第十六章（贝丝病房内的圣洁离世）：</strong>体会全家在生死离别中展现出的崇高平静与爱的永恒凝聚。</li>
        <li><strong>必读第五场 · 第二卷第二十二章（巴尔教授雨天撑伞求婚）：</strong>精读全剧最朴素真挚的灵魂结合，领悟精神平等的成熟婚姻之美。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 乔拒绝劳里的必然性：</strong>许多读者对乔没有嫁给帅气多金的劳里感到终生遗憾，但如果乔当年答应了劳里，她的写作事业与精神独立在庞大的豪门社交圈中还会得到保障吗？
      </div>
      <div class="card-box">
        <strong>Q2 · 艾米与劳里的结合合理吗？</strong>艾米从当年那个烧手稿的任性小妹，蜕变成在欧洲当面斥责劳里自暴自弃的成熟女性，她的成长在多大程度上证明了她是比乔更适合劳里的贤内助？
      </div>
      <div class="card-box">
        <strong>Q3 · 贫困与尊严的平衡：</strong>马奇一家虽然贫困，但无论面对多么富有的邻居，他们从未流露出哪怕一丝自卑与谄媚。这种强大的心理定力源自哪里？
      </div>
      <div class="card-box">
        <strong>Q4 · 母亲的教育艺术：</strong>当孩子们犯错（如艾米在学校被罚打手板、梅格在舞会爱慕虚荣）时，马奇太太为什么极少动用惩罚，而是用引导提问让孩子自己得出结论？
      </div>
      <div class="card-box">
        <strong>Q5 · 终局办学的精神高度：</strong>乔在继承了豪华庄园后，没有把它变成收租的私宅，而是办成了面向全社会的平民寄宿学校，这一举动体现了奥尔科特怎样崇高的社会理想？
      </div>"""

    sec13 = """      <div class="sub-heading">① 职业自立实践工具：“乔·马奇内生动力清单” (The Jo March Creative Compass)</div>
      <p><strong>适用场景：</strong>当你身处一项枯燥重复、纯粹为了迎合别人眼光的工作，内心渴望开启属于自己的独立创造或副业时。<br>
      <strong>第一步（界定你的假惊悚手稿）：</strong>写下你目前正在做的哪些事情纯粹是为了‘赚取快钱或迎合世俗流量’，但在做完后你内心感到巨大的空虚与消耗；<br>
      <strong>第二步（寻找你的家庭苹果箱）：</strong>问自己：在你的生命中，哪一段最真实的亲身经历、哪一种最独特的技能经验，是你讲出来就能彻底打动他人的？<br>
      <strong>第三步（建立每日两小时阁楼制度）：</strong>无论白天工作多累，每晚强制为自己留出两小时‘不看手机、不刷社交媒体’的绝对专注时间，像乔一样伏案打磨一件真正属于你自己的长线作品。</p>

      <div class="sub-heading">② 现实观察实验：“母亲的心灵倾听日”</div>
      <p>选一个安静的午后，泡一壶茶坐在母亲身边，不聊你的工作也不谈家庭杂务，只是像朋友一样问母亲一句：‘妈，在你年轻的时候，你曾经有过什么因为家庭而放下的梦想吗？’倾听她的回答，体会马奇太太式的代际牺牲。</p>

      <div class="sub-heading">③ 温暖家常场景仿写任务</div>
      <p>模仿《小妇人》开篇那种融融炉火、屋外白雪皑皑、屋内充满柴火噼啪声与亲人笑语的温暖笔调，写一段关于‘一家人在暴雪停电的冬夜里围坐在一起点燃蜡烛吃一碗热汤面’的白描段落（350字以内，充满人间烟火的深情厚度）。</p>"""

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

print("Round 11 deep Little Women ready.")

def get_deep_hatchet():
    data = {
        "title_cn": "手斧男孩",
        "title_en": "Hatchet",
        "author_cn": "盖瑞·伯森",
        "author_en": "Gary Paulsen",
        "sub_desc": "纽伯瑞银奖荒野求生至尊圣经 · 一把手斧铸就的坚毅少年与现代硬汉精神",
        "hero_quote": "自怜是这个世界上最毫无用处的东西；哭泣救不了命，悲伤只能加速死亡，唯有思考、行动和耐心，才能让你从死神手里把生命夺回来！"
    }

    sec01 = """      <div class="specs-grid">
        <div class="spec-item"><div class="spec-label">小说家与荒野求生家</div><div class="spec-val">盖瑞·伯森 (1939–2021)</div></div>
        <div class="spec-item"><div class="spec-label">出版与荣誉</div><div class="spec-val">1987年出版 / 荣获美国纽伯瑞银奖</div></div>
        <div class="spec-item"><div class="spec-label">体裁坐标</div><div class="spec-val">荒野求生小说 / 少年成长励志经典</div></div>
        <div class="spec-item"><div class="spec-label">全书体量</div><div class="spec-val">约 10 万字 / 全十九章带后记</div></div>
        <div class="spec-item"><div class="spec-label">建议阅读年龄</div><div class="spec-val">10+ 岁 / 终身必读坚毅品格必读</div></div>
        <div class="spec-item"><div class="spec-label">核心判断标准</div><div class="spec-val">独立问题解决心智演进与极端逆境抗挫力淬炼</div></div>
      </div>

      <div class="card-box-accent">
        <strong>⚠️ 最需警惕的误读：</strong>切勿把《手斧男孩》当成开挂作弊的‘荒岛漂流记儿童冒险爽文’。作者盖瑞·伯森曾两次参加阿拉斯加艾迪塔罗德狗拉雪橇千英里极地死亡耐力赛，多次在荒野受重伤濒死，全书每一个求生细节全是作者用血肉亲身验证过的<strong>硬核大自然生存法则</strong>。十三岁的布莱恩不是什么超人，他是一个被父母离婚秘密折磨得痛不欲生的普通城市软脚虾。他被孤身扔在加拿大原始针叶林整整五十四天，经历了被豪猪刺穿小腿、被黑熊撞翻、被龙卷风摧毁庇护所、甚至在绝望中拿起手斧割腕自杀的彻底心理淬火。这是一部教人在绝境中‘学会不当巨婴、自己当自己救世主’的硬汉成长教科书。
      </div>

      <div class="sub-heading">三大核心阅读看点</div>
      <div class="card-box">
        <strong>① 单引擎飞机迫降与突发心脏病死亡的惊悚开场：</strong>十三岁少年坐在副驾驶座上，驾驶员突发剧烈心绞痛猝死在操纵杆上。在刺鼻的汽油味与仪表盘失灵的绝境中，布莱恩必须克服恐惧握紧操纵杆，依靠微弱的无线电呼救与本能直觉，将飞机以机腹擦树冠迫降在L形冰冷深湖中。
      </div>
      <div class="card-box">
        <strong>② 用手斧在黑夜黑燧石上砸出火星的‘普罗米修斯神迹’：</strong>全书第八至九章。在被豪猪刺伤小腿、绝望痛哭之后，布莱恩偶然发现手斧钢刃砸中岩壁飞溅的火花。他经历了数百次失败，撕碎白桦树皮捻成极细的纤维，像对待初生婴儿一样屏住呼吸轻轻吹气，终于看着一缕青烟化作跳动的金色火苗。那一簇火，成了他在荒野中不仅能够取暖防兽、更能战胜心理虚无的最神圣伙伴。
      </div>
      <div class="card-box">
        <strong>③ 龙卷风肆虐后潜入沉没机舱的生死深潜：</strong>第十六章自然界的狂暴龙卷风一夜之间把布莱恩建了两个月的营地彻底夷为平地，但也奇迹般将湖底沉没飞机的机尾掀出水面。布莱恩扎起木筏划入湖心，在手斧失手沉入湖底的巨大绝望中潜入泥水摸回手斧，用斧头撕开飞机铝皮，在水下看见已被鱼群啃噬得只剩白骨的飞行员头颅，冒着溺死危险夺回了应急生存包。
      </div>"""

    sec02 = """      <p style="margin-top:6px; color:var(--text-muted); font-size:14.5px;">
        加拿大北方辽阔无际的北方森林（Boreal Forest）。密林、沼泽、湖泊与花岗岩冰川遗迹构成了一座不通公路、毫无信号、充满黑熊灰狼与严寒的大自然冰冷法则圣殿。
      </p>

      <div class="svg-wrap">
        <svg viewBox="0 0 680 340" xmlns="http://www.w3.org/2000/svg">
          <style>
            .ht2-box { rx: 8; stroke-width: 1.5; }
            .ht2-bg-brian { fill: #8c2d19; stroke: #a33b24; }
            .ht2-bg-city { fill: #1d3557; stroke: #2a4d7a; }
            .ht2-bg-nature { fill: #131619; stroke: #59645f; }
            .ht2-bg-fire { fill: #2a9d8f; stroke: #40916c; }
            .ht2-t-w { fill: #ffffff; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ht2-t-d { fill: #1c221e; font-family: sans-serif; font-size: 13px; font-weight: 700; text-anchor: middle; }
            .ht2-t-sub { fill: #59645f; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ht2-t-sub-w { fill: #e5e8eb; font-family: sans-serif; font-size: 10.5px; text-anchor: middle; }
            .ht2-solid { stroke: #8c2d19; stroke-width: 2; fill: none; }
            .ht2-green { stroke: #2a9d8f; stroke-width: 2.2; stroke-dasharray: 4,3; fill: none; }
            .ht2-lbl { font-family: sans-serif; font-size: 11px; fill: #8c2d19; font-weight: 600; text-anchor: middle; }
          </style>

          <defs>
            <marker id="ht2-arr" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#8c2d19" />
            </marker>
          </defs>

          <!-- 都市软弱少年 (起点) -->
          <rect x="20" y="25" width="210" height="115" class="ht2-box ht2-bg-city" />
          <text x="125" y="52" class="ht2-t-w">都市少年布莱恩 (Day 1)</text>
          <text x="125" y="72" class="ht2-t-sub-w">十三岁 · 依赖现成超市与电网</text>
          <text x="125" y="90" class="ht2-t-sub-w">心智充满父母离异秘密的自怜痛苦</text>
          <text x="125" y="108" class="ht2-t-sub-w">遭遇困境只会抱头痛哭与放弃</text>
          <text x="125" y="124" style="fill:#a8dadc; font-size:10px; text-anchor:middle;">“谁来救救我，我只是个孩子！”</text>

          <!-- 荒野淬炼蜕变者 (终点) -->
          <rect x="450" y="25" width="210" height="115" class="ht2-box ht2-bg-brian" />
          <text x="555" y="52" class="ht2-t-w">荒野男子汉布莱恩 (Day 54)</text>
          <text x="555" y="72" class="ht2-t-sub-w">目光如鹰 · 肌肉精干黑瘦</text>
          <text x="555" y="90" class="ht2-t-sub-w">听懂风声鸟语 · 制作弓箭捕鱼</text>
          <text x="555" y="108" class="ht2-t-sub-w">自立、坚忍、冷静、尊重自然法则</text>
          <text x="555" y="124" style="fill:#f0dcd8; font-size:10px; text-anchor:middle;">心智彻底告别自怜，实现硬核重生</text>

          <!-- 迫降与淬火连线 -->
          <path d="M 230 82 L 450 82" class="ht2-solid" marker-end="url(#ht2-arr)" />
          <text x="340" y="74" class="ht2-lbl">迫降深湖 · 五十四天孤胆生存</text>

          <!-- 核心工具纽带：手斧与篝火 -->
          <rect x="235" y="135" width="210" height="75" class="ht2-box ht2-bg-fire" />
          <text x="340" y="162" class="ht2-t-w">唯一法宝：皮带上的手斧 (Hatchet)</text>
          <text x="340" y="180" class="ht2-t-sub-w">黑燧石击火 · 削尖鱼叉 · 砍伐桦树</text>
          <text x="340" y="196" style="fill:#d8f3dc; font-size:9.5px; text-anchor:middle;">“没有手斧，我早就成了一具白骨”</text>

          <!-- 下方冷酷导师：加拿大原始森林 -->
          <path d="M 340 210 L 340 245" class="ht2-solid" stroke="#59645f" />
          <rect x="160" y="245" width="360" height="80" class="ht2-box ht2-bg-nature" />
          <text x="340" y="272" class="ht2-t-w">严苛而公正的导师：北方针叶林自然律</text>
          <text x="340" y="292" class="ht2-t-sub-w">蚊虫风暴 · 豪猪突袭 · 驼鹿踏水 · 龙卷风洗劫</text>
          <text x="340" y="308" style="fill:#e0725b; font-size:10px; font-weight:700; text-anchor:middle;">自然不讲人情眼泪，但它奖赏耐心、观察与尊重</text>
        </svg>
      </div>

      <div class="sub-heading">核心角色与自然法则谱系深度解剖</div>
      <ul class="bullet-list">
        <li><strong>布莱恩·罗伯森（Brian Robeson）：</strong>十三岁纽约中产家庭男孩。父母刚刚离婚，他正乘小飞机飞往加拿大北方油田看望父亲。他最大的包袱是那个‘秘密（The Secret）’——他曾亲眼看见母亲坐在陌生男人的红色旅行车里接吻。在荒野的前两周，这个秘密折磨得他痛不欲生；然而大自然以极度的饥饿、蚊虫的刺痛和生存的危机，彻底洗去了他脑海中多余的怨念。当救援飞机飞过山头未曾发现他时，他在绝望中用手斧割开手腕企图自尽；但在第二天的晨光中醒来时，他看着自己的鲜血，突然完成了精神的彻底蜕变——从那一刻起，‘旧的布莱恩死了，新的布莱恩诞生了’。他学会了把挫折当成大自然抛出的考题，依靠冷静的理性解决每一个生存死结。</li>
        <li><strong>手斧（The Hatchet）：</strong>全书真正并列的第一主角。母亲在机场分别时赠送的一件绑在腰间的实用小工具。在城市文明里，它微不足道；但在原始荒野中，它是普罗米修斯的神火、是外科手术刀、是打猎的防身武器、是建造庇护所的唯一铁器。布莱恩通过这把手斧，重新建立了人类文明与原始自然之间的物质与精神纽带。</li>
        <li><strong>北方大自然（自然神性与法则）：</strong>冷酷而公正的宇宙化身。它不是迪斯尼动画里会说话的温柔小鹿，它是会把人脸叮肿得眼睛都睁不开的万千蚊虫、是在黑暗中因受惊用数十根毒刺扎进布莱恩小腿的豪猪、是无情践踏营地将布莱恩撞进湖底骨折的巨大母驼鹿、是瞬间将一切化为乌有的龙卷风。但大自然同样慷慨地在石壁上留下了黑燧石、在树林中结出了紫红的‘苦梅’、在湖畔沙地里埋下了乌龟蛋、在水面下游弋着银色的太阳鱼。只要你收起傲慢、学会细心观察，大自然就向你敞开无尽的生路。</li>
      </ul>"""

    sec03 = """      <div class="sub-heading">表面上讲了什么故事？</div>
      <p>十三岁少年布莱恩·罗伯森携带母亲在机场赠送的一把腰间手斧，乘坐一架单引擎塞斯纳小飞机前往加拿大北部油田看望离异的父亲。飞行途中，飞行员因剧烈心脏病猝死在座位上。在万米高空的恐惧中，布莱恩靠无线电发出未曾得到有效回应的呼救，在燃油耗尽时拼死操纵飞机迫降在无名L形湖泊中。逃离沉没机舱的布莱恩浑身湿透爬上岸，在饥寒交迫中度过了第一夜。面对漫天蚊虫的叮咬与极度的饥饿，他找到了难以下咽但能充饥的酸苦‘苦梅’，并在石壁下利用枯木树枝搭建了简陋的半开放式庇护所。在经历了豪猪夜袭刺伤小腿的剧痛后，布莱恩偶然发现手斧砍击黑燧石岩壁溅出的火星，历经数小时的尝试，用桦树皮纤维成功吹出了救命的篝火。有了火，他找到了沙滩掩埋的海龟蛋补充蛋白质；他用手斧削出木叉捕鱼屡屡落空，敏锐地意识到光的折射原理，调整角度成功叉中太阳鱼，并在营地修建了石质活鱼池；他制作弓箭猎杀林中的松鸡（‘笨鸟’）尝到了烤肉的美味。当一架搜救飞机从头顶飞过却未发现他时，绝望的布莱恩在山顶企图用手斧割腕自杀；大难不死迎着朝阳醒来后，布莱恩完成了彻底的心理涅槃，成为了一个沉稳坚毅的‘真正的荒野求生者’。在随后的日子里，他遭遇了母驼鹿的暴烈踩踏致肋骨骨折，当晚更遭遇了龙卷风的毁灭性洗劫，营地全毁。然而龙卷风把沉在湖底的飞机尾部掀出了水面。布莱恩扎起筏子划向深水，在失手掉落手斧又冒险潜水寻回的绝境中，用手斧撕开机舱铝皮，成功打捞出了飞机上的应急救生包，获得了睡袋、火柴、脱水干粮与一部应急无线电发报机。在摆弄发报机几分钟后，一部途径的加拿大水上巡逻飞机捕捉到微弱信号降落湖面。布莱恩平静地向走下浮筒的飞行员伸出污迹斑斑的右手微笑道：‘我叫布莱恩·罗伯森。你想要吃点东西吗？’历时五十四天的荒野求生神话至此圆满收官。</p>

      <div class="sub-heading">深处真正关心什么？</div>
      <p>作品深处探究的是<strong>“现代人尤其是青少年在被温室社会过度保护后，如何通过切断一切外部依赖、在极端生理逆境中直面自身的脆弱与自怜，淬炼出独立解决复杂问题与承受挫折的硬核心智”</strong>。伯森向全人类证明：自怜与哭泣是软弱者的毒药，面对不可逆转的变故，唯有行动、观察、试错与坚持，才能让一个人真正成为自己命运的主人。</p>

      <div class="sub-heading">核心体验一句话</div>
      <div class="quote-block">
        如同一柄在黑燧石上被千万次猛烈撞击的冰冷手斧：在汗水、泥浆与鲜血的反复锤炼中，淬掉少年心智中全部的自怨自艾与虚浮娇气，锻打出一具如钢铁般沉稳自信的成年男子汉筋骨。
      </div>

      <div class="sub-heading">这部作品写给谁？</div>
      <p>写给每一个身处考试挫败、家庭离异动荡、被焦虑与自怜紧紧缠绕，感到生活陷入绝境、渴望重新找回内心主宰力量的年轻人与所有成年人。</p>"""

    sec04 = """      <div class="sub-heading">核心冲突模型</div>
      <p><strong>未经生活磨砺的城市依赖性弱小自我 vs 荒野严苛残酷客观法则；绝望自怜的自毁倾向 vs 坚守行动求生的刚毅意志。</strong></p>

      <div class="sub-heading">全书五十四天极限生存推进链条</div>
      <ol class="num-list">
        <li><strong>第一至三章 · 万米坠落与湖泊迫降：</strong>飞行员猝死，绝望握杆，寻找湖泊缓冲，机腹擦树冠轰然沉水，挣扎脱困昏死岸边。</li>
        <li><strong>第四至七章 · 蚊虫围攻与苦梅充饥：</strong>头颅剧痛苏醒；大群吸血蚊蚋包围；‘秘密’记忆撕扯；寻找水源与发现苦梅（Gut Cherries），夜半胃痛呕吐。</li>
        <li><strong>第八至十章 · 豪猪刺腿与神火降临：</strong>黑暗中豪猪突袭，数十根倒刺扎进腿肉，嚎啕痛哭后领悟自怜无用；手斧碰燧石发现火花；桦树皮引火成功，拥有‘神火伴侣’。</li>
        <li><strong>第十一至十三章 · 折射捕鱼与自杀涅槃：</strong>海龟蛋盛宴；木叉捕鱼屡屡落空，顿悟光的折射修正瞄准点；搜救机飞过未见，山顶手斧割腕自毁；朝阳中重生为‘坚韧布莱恩’。</li>
        <li><strong>第十四至十六章 · 猎杀松鸡与驼鹿风暴：</strong>制作反曲弓与削箭，成功吃上烤肉；黑熊对视的敬畏；母驼鹿踩断肋骨；深夜龙卷风狂卷，大风吹出湖底机尾。</li>
        <li><strong>第十七至十九章与尾声 · 潜水摸包与平静获救：</strong>木筏下潜，手斧掉落泥底沉着找回；劈开飞机蒙皮，惊见白骨飞行员；拖回应急包打开脱水牛肉；巡逻飞机滑降，平静握手谢幕。</li>
      </ol>

      <div class="sub-heading">决定性转折点</div>
      <div class="card-box">
        <strong>第十三章搜救机离开后布莱恩在峭壁上的自杀与重生：</strong>搜救飞机转瞬即逝的巨大绝望彻底压垮了他，他抓起手斧割向手腕；然而第二天黎明，当他看着凝固的伤口迎着朝阳站起来时，他脑海中的那个只知哭泣自怜的城市男孩彻底死去了。他领悟到了前所未有的清醒：‘无论发生什么，我绝不会再向死亡投降！’这一刻确立了全书硬汉精神的真正涅槃。
      </div>"""

    sec05 = """      <div class="sub-heading">‘自怜毫无用处’：全书最高心智成长哲学</div>
      <p>全书第八章有一段堪称现代抗挫力教育最高经典的内心自白：在被豪猪刺伤、整条小腿肿胀如猪腿、在岩洞里哭得死去活来的深夜，布莱恩突然停住了哭泣。他看着自己满脸的鼻涕和眼泪，对自己说：‘自怜是世界上最毫无用处的东西。你就算把眼睛哭瞎，小腿上的刺也不会掉出来一根；你就算把嗓子喊破，森林里也不会有一辆救护车开过来。哭泣只能证明你的软弱，除此之外什么都改变不了。’正是这一记当头棒喝，促使他抓起手斧一根根忍痛拔出倒钩刺，并最终在敲击中找到了火星。这种<strong>‘从情绪宣泄迅速转向问题解决’的心理切换能力</strong>，是一个人迈向成熟最根本的标志。</p>

      <div class="sub-heading">‘秘密’的释怀：战胜内心的精神毒瘾</div>
      <p>在迫降之初，布莱恩的整个大脑被‘母亲背叛父亲’的秘密所霸占。他满腔怨毒，把父母的离异当做毁灭自己人生的全部借口。然而在经历了五十四天真刀真枪的生死搏斗后，他整个人脱胎换骨。当五十四天后获救重返文明、父母在身边哭成泪人时，布莱恩看着依然彼此冷淡的父母，发现自己心中曾经那份足以毁天灭地的怨毒，早已在严酷的自然面前化为了平静与释怀。他终生没有把这个秘密对父亲说出一个字。这种对痛苦记忆的放下，展现了一个真正男子汉的深沉担当。</p>"""

    sec06 = """      <div class="sub-heading">高清晰度身体感官与极限生存白描</div>
      <p>盖瑞·伯森的语言风格极其硬朗、具体、带有强烈的<strong>肉体痛感与肌肉发力感</strong>。全书几乎没有任何空洞的修饰，他详尽描写如何用石头砸死松鸡、如何剥皮掏内脏、如何用手掌接住第一滴清晨树叶上的露水、骨折的肋骨在每一次呼吸时发出的隐隐作痛。这种极度严谨的纪实笔法，让每一个字都散发出松脂的香气与泥土的硬度，给全书带来了无与伦比的说服力。</p>

      <div class="sub-heading">三大核心意象系统</div>
      <ul class="bullet-list">
        <li><strong>腰间的那把小手斧 (The Hatchet)：</strong>文明赋予个体的最初工具，也是重启生存的唯一钥匙。砍柴、制弓、生火、破机舱，它是布莱恩身体与意志的延伸，象征<strong>人类依靠智慧与工具改造自然、绝处逢生的不屈精神</strong>。</li>
        <li><strong>跳动的金色篝火 (The Fire)：</strong>在荒野中被布莱恩视作‘一位真正的朋友’。它驱散蚊虫与严寒，把潮湿的洞穴变成温暖的家，象征<strong>人类文明最初从黑暗野蛮中点燃的神圣理性与安全庇护</strong>。</li>
        <li><strong>沉入湖底的飞机残骸：</strong>象征都市文明的脆弱性。那座曾经以每小时二百英里呼啸的现代高精尖飞行器，在水下安详地化为鱼类的栖息地，警示人类<strong>一切技术造物在浩瀚大自然面前都不过是暂借的浮华</strong>。</li>
      </ul>"""

    sec07 = """      <div class="sub-heading">主题三层架构模型</div>
      <div class="card-box">
        <strong>表层架构（经典荒野求生小说）：</strong>一个十三岁男孩在飞机失事后孤身一人凭借一把手斧，在加拿大原始针叶林中生存五十四天最终获救的奇迹冒险故事。<br>
        <strong>深层架构（青年心智与抗挫力淬火）：</strong>对现代温室青少年依赖性、自怜心理与脆弱心智的系统性精神脱水。证明唯有打破一切被动依赖，在实打实的问题解决与试错中，才能锻造出坚韧独立的真正人格。<br>
        <strong>根本架构（人与自然的生存契约）：</strong>大自然冰冷公正法则对人类的深层启蒙。大自然没有恶意，但也绝不施舍怜悯；人类唯有尊重规律、克制骄傲、学会倾听自然的呼吸，才能在天地之间赢得生命真正的尊严。
      </div>"""

    sec08 = """      <div class="sub-heading">最有文本依据的权威解读</div>
      <p>美国图书馆协会（ALA）将《手斧男孩》评为‘对北美青少年男子汉气概影响最深远的世纪经典’。它彻底告别了传统冒险小说中虚假的‘童子军作弊打卡’模式，以血淋淋的骨折、伤口感染与真实的挫败感，还原了人类生存最底层的粗粝真相，成为了全球野外生存教育与心理抗挫力培训的至尊教材。</p>"""

    sec09 = """      <div class="sub-heading">如果作品说中了现代社会，它说中了什么？</div>
      <p>今天的现代青少年与成年人，普遍生活在极端舒适的‘过度代劳温室’中：<br>
      饿了点外卖，迷路了看导航，遇到一点挫折就发朋友圈求安慰，稍微遭遇感情不顺或考试失利就自怨自艾甚至抑郁自残。我们拥有了前所未有的物质安全，但我们的心理防线却脆弱得如同薄纸，一点小挫折就能引发精神海啸。《手斧男孩》告诉所有人：扔掉那些廉价的眼泪和自怜，抓紧你手里的‘手斧’，行动起来去解决问题，这是通往强大的唯一道路。</p>

      <div class="sub-heading">连接个人处境的 3 个深思问题</div>
      <ol class="num-list">
        <li>在你的日常生活中，当你面对一项极其复杂突发的重大麻烦时，你的第一本能是四处找人抱怨诉苦，还是深吸一口气先坐在椅子上理清事实？</li>
        <li>如果你曾经历过像父母离异、背叛或其他家庭重大创伤，你是否能像五十四天后的布莱恩一样，不再将其作为自己人生摆烂的借口？</li>
        <li>在整日享受空调、外卖与智能手机的今天，如果你被随机扔在一个没有手机信号的地方，你身上有哪些技能能够独立解决自己的衣食温饱？</li>
      </ol>"""

    sec10 = """      <div class="sub-heading">30 秒日常交流版（电梯演讲）</div>
      <p>“《手斧男孩》是专治各种脆弱自怜、矫情矫柔的硬核神作。十三岁男孩因飞机坠毁独自流落加拿大原始森林五十四天，只有一把母亲送的小手斧。他被豪猪刺扎透、被大熊扑倒、遇到龙卷风骨折，最后硬是靠一把手斧生出火、做出弓箭活了下来。它告诉你：哭泣救不了命，自怜是最大的毒药；能拯救你的，唯有行动与坚忍。”</p>

      <div class="sub-heading">3 分钟结构分享版（读书会与课堂）</div>
      <p>“大家好，今天我们来精读全球所有男孩与坚韧女性的必读圣经——盖瑞·伯森的《手斧男孩》。这本书被公认为世界求生文学的最高巅峰。故事开篇极其惊心动魄：十三岁少年布莱恩坐着单引擎小飞机去油田看父亲，结果飞行员在半空中突然心脏病猝死！一个十三岁的孩子，硬是在万米高空自己握紧操纵杆，靠着微弱直觉把飞机迫降在无人的大森林湖泊里！爬上岸后，他身上只有一套单薄的衣服和腰间一把母亲在机场顺手买的小手斧。前三天，他简直要疯了，浑身被蚊虫咬烂，饿得吃酸野果吃到半夜吐血。有一天夜里，一只豪猪闯进石洞，一尾巴把几十根毒刺深深扎进他的小腿肉里。布莱恩哭得撕心裂肺，但就在那个绝望的深夜，他突然悟出了全书最震撼的真理：‘哭泣救不了命，自怜是这个世界上最没用的东西！’他咬着牙一根根把倒刺拔出来，偶然发现手斧砍石头砸出的火花，整整吹了几个小时，硬是用白桦树皮吹出了人生第一堆救命的篝火！有了火，他学会了做反曲弓、看懂了水的折射叉鱼烤肉；当搜救飞机从头顶飞过没看到他时，他在悬崖上绝望得拿手斧割腕自杀，但第二天太阳升起时，那个只知道哭鼻子的城市小少爷彻底死去了，一个像猎人一样敏锐坚毅的硬汉布莱恩在泥土中站了起来。后来龙卷风把他的营地全毁了，他踩着自制木筏跳进深湖，冒着被淹死的危险潜入机舱撕开铝皮，找回了应急包。在经历了整整五十四天荒野洗礼后，巡逻飞机降落了。走下飞机的飞行员看着这个肌肉黑瘦、目光如鹰、浑身散发着大将之风的少年，布莱恩只是平静地拍了拍尘土，微笑着说：‘我叫布莱恩，你要吃点东西吗？’这本书给所有现代人上了一堂极其硬核的生命课：生活随时可能把你的飞机撞毁，但只要你手中有一把不服输的手斧，只要你绝不自怜，你就永远能从死神手里把生命夺回来！”</p>

      <div class="sub-heading">一句金句式概括</div>
      <div class="quote-block">
        “大自然从不欠你任何施舍，它既不痛恨你，也不偏爱你；它唯有一条冰冷的铁律——站起来行动的人活下去，沉溺自怜的人化为白骨。”
      </div>"""

    sec11 = """      <div class="sub-heading">最小通达路径：世界荒野求生巅峰核心必读场次</div>
      <ul class="bullet-list">
        <li><strong>必读第一场 · 第一至二章（飞行员空中猝死迫降）：</strong>精读副驾驶座上十三岁少年独自面对死亡操纵机翼的惊心动魄开场。</li>
        <li><strong>必读第二场 · 第八至九章（豪猪刺腿与手斧生火）：</strong>精读全书最经典的自省转折与‘用桦树皮吹出第一簇火苗’的神圣白描。</li>
        <li><strong>必读第三场 · 第十三章（搜救机错过与割腕自杀涅槃）：</strong>精读布莱恩从绝望求死到次日清晨迎着朝阳脱胎换骨的心智质变。</li>
        <li><strong>必读第四场 · 第十七至十八章（潜入湖底沉机撕裂机皮）：</strong>精读深潜泥水中直视白骨头颅、夺回应急包的意志巅峰较量。</li>
      </ul>"""

    sec12 = """      <div class="card-box">
        <strong>Q1 · 知识与实践的鸿沟：</strong>布莱恩在学校里学过很多自然科学，但为什么在森林里最初依然连一条鱼都抓不到？从‘书本知识’到‘肌肉解决现实问题本领’需要跨越怎样的鸿沟？
      </div>
      <div class="card-box">
        <strong>Q2 · 自怜的心理毒性：</strong>为什么自怜往往比生理上的伤痛更容易置人于死地？我们如何在日常挫败的第一时间掐断内心的受害者自怜情绪？
      </div>
      <div class="card-box">
        <strong>Q3 · 大自然冷漠的教育意义：</strong>森林里的黑熊、驼鹿和暴风雨从不讲究人类社会的文明礼仪，为什么这种‘不讲人情的冷酷’反而最快治愈了布莱恩的娇气与任性？
      </div>
      <div class="card-box">
        <strong>Q4 · 守口如瓶的成熟：</strong>布莱恩在获救后为什么坚决不对父亲说出那个曾让他痛苦万分的‘母亲出轨秘密’？这种沉默体现了他怎样的一种成年心智担当？
      </div>
      <div class="card-box">
        <strong>Q5 · 现代社会的隐形手斧：</strong>在高度自动化的都市生活中，我们每个人身上最宝贵的‘下一把手斧’究竟是什么？我们靠什么维持面对失业与危机的抗挫力？
      </div>"""

    sec13 = """      <div class="sub-heading">① 逆境抗挫行动工具：“布莱恩断氧五步救援法” (The Brian Survival Protocol)</div>
      <p><strong>适用场景：</strong>当你突然遭遇重大考试失利、项目彻底搞砸、或者被突发事件击溃感到天塌地陷时。<br>
      <strong>第一步（强制止哭）：</strong>告诉自己那句名言：‘自怜毫无用处，哭泣救不了命’，允许自己深呼吸三次，擦干眼泪；<br>
      <strong>第二步（清点腰间手斧）：</strong>不要看你失去了什么，列出你目前手中依然保有的最后三项具体资源（如你的健康、一个还能使用的电脑、一百块钱备用金）；<br>
      <strong>第三步（寻找第一块黑燧石）：</strong>把庞大的灾难拆解为此时此刻能够动手的‘最小下一个物理动作’（如先洗一把脸、先发一封确认邮件、先做一道简单的菜）；<br>
      <strong>第四步（吹起第一丝火星）：</strong>专注投入到这个微小动作中，在看到第一个正向反馈前绝不分心；<br>
      <strong>第五步（像男子汉一样前行）：</strong>每天解决一个具体问题，把生活的控制权一寸一寸从混乱中夺回自己手里。</p>

      <div class="sub-heading">② 现实观察实验：“野外生存物品极简清点”</div>
      <p>检查你的随身背包或书包，假设你将在一个完全没有手机电量和商店的地方度过接下来的二十四小时。评估你包里哪一样物品是真正能保命的‘手斧’，哪九成物品不过是累赘的电子消费玩具，重新审视自己的物质依赖。</p>

      <div class="sub-heading">③ 极限定力仿写任务</div>
      <p>模仿第九章布莱恩摩擦生火那种极度细致、充满物理阻力与呼吸屏息感的硬核白描笔法，写一段关于‘某人在暴风雨即将来临前用双手固定破损窗户’的微型动作段落（350字以内，全用具体物理动作，节奏紧绷坚毅）。</p>"""

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
    print("=== 开始批量写入第 11 轮（彼得潘、小妇人、手斧男孩） ===")
    plan = [
        ("彼得潘", get_deep_peter_pan),
        ("小妇人", get_deep_little_women),
        ("手斧男孩", get_deep_hatchet),
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
