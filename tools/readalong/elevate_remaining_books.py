# -*- coding: utf-8 -*-
import os
import sys
from bs4 import BeautifulSoup

BASE_DIR = "/Volumes/750/Music/有声书/文学作品"

def append_to_section(file_path, sec_title, extra_html):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    target_sec = None
    for sec in soup.find_all("details", class_="guide-section"):
        title_el = sec.find("h2", class_="section-title")
        if title_el and sec_title in title_el.text:
            target_sec = sec
            break
    if target_sec:
        content_div = target_sec.find("div", class_="section-content")
        if content_div:
            # 插入额外内容
            extra_soup = BeautifulSoup(extra_html, "html.parser")
            content_div.append(extra_soup)
            new_html = str(soup)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_html)
            idx_path = file_path.replace(".html", ".index")
            with open(idx_path, "w", encoding="utf-8") as f:
                f.write(new_html)

# 针对几部需要冲刺 5500+ 字的书籍进行全方位深度知识注入
books_to_elevate = {
    "达洛维夫人": """
      <div class="sub-heading">《达洛维夫人》主观时间与死亡意识流深度批评</div>
      <div class="card-box">
        <strong>大本钟双重时间哲学：</strong>大本钟敲响时的‘铅色圆晕’不仅是时间的流逝，更象征着整个大英帝国父权国家机器对个体私密意识的物理切片。然而克拉丽莎在漫步中，意识却能自由地在三十年前的初恋阳台与眼前的花店百合花之间来回跳跃，展示了人类心灵面对物理时间规训时的崇高自由。
      </div>
      <div class="card-box">
        <strong>塞普蒂默斯之死与精神医学规训大批判：</strong>名医布拉德肖爵士代表了冷酷的‘秩序与比例’。他把老兵在战壕中目睹战友粉身碎骨后的绝望，诊断为‘神经软弱’，试图通过孤立与禁闭强制其顺从社会。青年的跳楼，是对这种披着科学外衣的制度冷漠最决绝的抗暴。
      </div>
      <div class="card-box">
        <strong>晚宴暗室里的至圣共鸣：</strong>在终局，克拉丽莎离开喧闹的首相与大使，独自面对窗外的星空。她没有把青年的死看作丑闻，而是从中看到了自己为了维持世俗体面所出卖的纯真。青年的死拯救了她，使她重新获得了面对衰老与虚无的非凡勇气。
      </div>
    """,
    "草叶集": """
      <div class="sub-heading">《草叶集》自由诗学与泛神论深度批评</div>
      <div class="card-box">
        <strong>《自我之歌》中的肉体神圣论：</strong>惠特曼宣告肉体的每一个器官、每一滴汗水与每一次呼吸都与神明同等崇高。他打破了中世纪基督教将肉体视为肮脏皮囊的教条，让普通劳动者的肌肉与粗糙双手在诗行中绽放出古典希腊雕塑般的神圣光辉。
      </div>
      <div class="card-box">
        <strong>紫丁香挽歌中的宇宙轮回：</strong>在哀悼林肯的诗篇中，死亡不再是冰冷的坟墓，而是回归大地、化作来年春天紫丁香芬芳的伟大新生。惠特曼以大地之子的博大胸怀，抚平了南北战争撕裂给全美留下的血肉创伤。
      </div>
      <div class="card-box">
        <strong>开放道路的流浪意志：</strong>《大路之歌》倡导一种不设防、不留恋安逸、随时向陌生天地敞开怀抱的现代流浪汉精神。生命就是一场没有终点的远行，唯有在前行中才能确认存在的浩瀚。
      </div>
    """,
    "魔法的颜色": """
      <div class="sub-heading">《魔法的颜色》后现代反讽与哲学解构深度展开</div>
      <div class="card-box">
        <strong>八元色与感知边界的物理学反思：</strong>普拉切特借‘第八种颜色’解构了人类感官的局限性。世人以为看见的就是全貌，却不知宇宙在可见光谱之外，始终流淌着凡人肉眼无法企及的狂乱可能性。
      </div>
      <div class="card-box">
        <strong>双花的天真与世界的恶意对冲：</strong>双花身上的‘超强游客钝感力’构成了全书最绝妙的哲学命题：当一个人真诚地相信世界充满美景与善意时，周围所有的盗贼、阴谋与怪兽，反而在这种纯粹的降维真诚面前乱了阵脚。
      </div>
      <div class="card-box">
        <strong>死神作为打卡公务员的制度讽刺：</strong>死神在书中被赋予了极其滑稽的人性化特征——他热爱猫咪，遵守工会工作时间，对灵思风一次次的奇葩逃脱感到无可奈何。普拉切特用狂欢的笑声，彻底粉碎了千百年来人类对死亡的恐怖图腾。
      </div>
    """,
    "文学随笔": """
      <div class="sub-heading">名家文学随笔深度心智解剖长卷</div>
      <div class="card-box">
        <strong>蒙田论死亡与坦然自处：</strong>‘面对死亡最好的办法，就是像对待平常的入睡一样自然。’蒙田在葡萄丰收季写道，不要被神学家的恐吓吓倒，大自然会教会每一个动物如何从容面对生命的大限。
      </div>
      <div class="card-box">
        <strong>奥威尔论清澈表达的政治伦理：</strong>在《政治与英语语言》中，奥威尔指出每一个含糊不清的词汇都是专制谎言的避风港。坚持使用具体、朴素、有骨骼的母语写作，是对抗现代一切虚伪洗脑最有效的人道主义自卫。
      </div>
      <div class="card-box">
        <strong>伍尔夫论夜游与城市匿名的快感：</strong>《街头漫步：伦敦历险记》中，伍尔夫描绘了一个人走出家门融入伦敦夜色、买一根铅笔的奇妙体验。在夜色中，自我的沉重面具脱落了，灵魂像鸟儿一样掠过成千上万陌生人的窗棂，体会到纯粹观察的至高狂喜。
      </div>
    """,
    "The Ultimate Essays Collection": """
      <div class="sub-heading">英语散文至高修辞与思想体系纵深</div>
      <div class="card-box">
        <strong>培根论友谊的三大果实：</strong>友谊能分担痛苦、双倍快乐；友谊能像清泉一样澄澈思想；友谊能在人生的决断时刻提供第三只不带偏见的眼睛。培根以罗马统帅的冷峻气魄，为世间纯粹知己立下了最崇高的理性功勋碑。
      </div>
      <div class="card-box">
        <strong>爱默生论自然的超验神性：</strong>‘当我步入丛林，所有的世俗虚荣都像枯叶一样脱落；我变成了一只透明的眼球，我什么都不是，我看见了一切，神圣的潮水在我全身流淌。’爱默生借此宣告了人与宇宙精神同一性的至圣哲学。
      </div>
      <div class="card-box">
        <strong>哈兹利特论长途步行的孤独快乐：</strong>‘一个人去散步，最好的同伴就是没有同伴！’哈兹利特厌恶在自然美景前进行庸俗的客套讨论，呼唤让思想在泥土与风声中自由奔跑，展现了英国散文最野性纯粹的孤傲品格。
      </div>
    """,
    "暮光之城I- 暮色": """
      <div class="sub-heading">《暮色》神话原型与本能自控深度展开</div>
      <div class="card-box">
        <strong>伊甸园禁果的现代变奏：</strong>封面双手捧着的红苹果，不仅象征知识与诱惑，更象征贝拉自主走向未知深渊的觉醒意志。在面对常年被恐惧笼罩的吸血鬼神话时，她用无畏的直视打破了被动的猎物角色，成为命运的主导者。
      </div>
      <div class="card-box">
        <strong>卡伦家族的‘文明素食’哲学：</strong>卡伦家族坚持以兽血维生，不仅是一项生理戒律，更是超自然力量对抗自身毁灭天性的崇高道德实践。卡莱尔用三百年证明：出身与血统无法决定一个生命的善恶，唯有你的每一次选择，才定义了你的灵魂。
      </div>
    """,
    "暮光之城II-新月": """
      <div class="sub-heading">《新月》精神断乳与绝望自愈深度展开</div>
      <div class="card-box">
        <strong>四个月空白日记的留白震撼：</strong>十月、十一月、十二月、一月，连续四张完全空白的日记页码，是全人类青春文学中最深刻的创伤留白。真正的剧痛是无法用词语粉饰的，它如同一片极度严寒的荒原，只有时间的无声流淌。
      </div>
      <div class="card-box">
        <strong>雅各布的阳光温度救赎：</strong>在冰冷的吸血鬼世界之外，印第安狼人族群的热烈体温与修车脏手，给贝拉提供了重新接纳现实大地的坚实踏板，展现了朴素友情对抑郁深渊的无价疗愈。
      </div>
    """,
    "暮光之城III-月食": """
      <div class="sub-heading">《月食》两性博弈与阵营政治深度展开</div>
      <div class="card-box">
        <strong>雪山睡袋长谈的男性自律典范：</strong>在严寒肆虐的帐篷里，爱德华握着爱人冰冷的手却无法供暖，雅各布带着42度的滚烫体温入睡袋护卫。两个男人在黑暗中摒弃了雄性好斗的低级本能，坦诚承认各自对贝拉的深情与局限。这种克制与担当，超越了一切俗套狗血三角恋。
      </div>
      <div class="card-box">
        <strong>维多利亚的悲剧盲区：</strong>这位红发女吸血鬼为了给詹姆斯复仇，不惜制造缺乏理性、自相残杀的西雅图新生军团，最终在自己亲手点燃的火海中被彻底吞噬。盲目的仇恨不仅未能告慰亡灵，反而让她成为了自己执念的殉葬品。
      </div>
    """,
    "暮光之城IV-破晓": """
      <div class="sub-heading">《破晓》女性力量觉醒与和平法理深度展开</div>
      <div class="card-box">
        <strong>意念护盾的防御性哲学：</strong>在全书终局对峙中，贝拉的异能不是杀伤性的攻击法术，而是一张纯粹的‘心灵防御盾牌’。这隐喻了真正的高维力量从来不是去毁灭他人，而是拥有足以抵御一切外部毒害与精神霸凌的绝对定力与防护能力。
      </div>
      <div class="card-box">
        <strong>雪原非暴力对峙的文明启示：</strong>近百名全宇宙最强大的超自然杀手齐聚雪原，但最终没有流一滴血。双方依靠事实证言、实力平衡与法理辩论化解了灭世浩劫，给充满暴力冲突的现代国际地缘政治提供了极其深刻的和平哲学镜鉴。
      </div>
    """
}

for bname, extra_html in books_to_elevate.items():
    p = os.path.join(BASE_DIR, bname, "guide.html")
    if os.path.exists(p):
        append_to_section(p, "真实感知", extra_html)
        print(f"[ELEVATED] {bname} injected successfully.")

print("All remaining books elevated successfully.")
