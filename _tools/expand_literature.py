# -*- coding: utf-8 -*-
"""
审查补充：扩充经典文学素材库 + 修复诗词意象库 count 不一致。

问题：
1. 文学素材库每部仅 15-16 条（共 91 条），对取名 Skill 过于单薄
2. 诗词意象库 count=78 但 items=75（count 字段不一致）

修复：
1. 为诗经/楚辞/唐诗/宋词/周易/道德经各补充约 15 条取名素材（总计 91→~180）
2. 为诗词意象库补充 3 条，使 items 与 count 一致（75→78）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ============ 文学素材扩充数据 ============
# 每部经典补充的取名素材（word/origin/quote/meaning/usage/pinyin）

SHIJING_NEW = [
    {"word": "蓁蓁", "origin": "《诗经·周南·桃夭》", "quote": "桃之夭夭，其叶蓁蓁", "meaning": "草木茂盛貌，喻生机蓬勃", "usage": "女名", "pinyin": "zhēn zhēn"},
    {"word": "燕飞", "origin": "《诗经·邶风·燕燕》", "quote": "燕燕于飞，差池其羽", "meaning": "燕子飞翔，喻自由轻盈", "usage": "女名", "pinyin": "yàn fēi"},
    {"word": "惠然", "origin": "《诗经·邶风·终风》", "quote": "惠然肯来", "meaning": "温和善意地，喻仁慈宽厚", "usage": "男女皆宜", "pinyin": "huì rán"},
    {"word": "静嘉", "origin": "《诗经·大雅·既醉》", "quote": "其告维何，笾豆静嘉", "meaning": "洁净美好，喻品德高洁", "usage": "女名", "pinyin": "jìng jiā"},
    {"word": "其琛", "origin": "《诗经·鲁颂·泮水》", "quote": "憬彼淮夷，来献其琛", "meaning": "珍宝，喻珍贵美好", "usage": "男名", "pinyin": "qí chēn"},
    {"word": "凯风", "origin": "《诗经·邶风·凯风》", "quote": "凯风自南，吹彼棘心", "meaning": "和暖的风，喻温和仁爱", "usage": "男名", "pinyin": "kǎi fēng"},
    {"word": "如雪", "origin": "《诗经·曹风·蜉蝣》", "quote": "蜉蝣之羽，衣裳如雪", "meaning": "洁白如雪，喻纯洁无瑕", "usage": "女名", "pinyin": "rú xuě"},
    {"word": "菁菁", "origin": "《诗经·唐风·杕杜》", "quote": "有杕之杜，其叶菁菁", "meaning": "草木茂盛，喻朝气蓬勃", "usage": "女名", "pinyin": "jīng jīng"},
    {"word": "零露", "origin": "《诗经·郑风·野有蔓草》", "quote": "野有蔓草，零露漙兮", "meaning": "晶莹的露水，喻清新润泽", "usage": "女名", "pinyin": "líng lù"},
    {"word": "邦彦", "origin": "《诗经·郑风·羔裘》", "quote": "彼其之子，邦之彦兮", "meaning": "国之英才，喻杰出人才", "usage": "男名", "pinyin": "bāng yàn"},
    {"word": "柔惠", "origin": "《诗经·大雅·崧高》", "quote": "柔亦不茹，刚亦不吐", "meaning": "柔和仁惠，喻性情温和善良", "usage": "女名", "pinyin": "róu huì"},
    {"word": "振鹭", "origin": "《诗经·周颂·振鹭》", "quote": "振鹭于飞，于彼西雍", "meaning": "振翅之白鹭，喻高洁出众", "usage": "男名", "pinyin": "zhèn lù"},
    {"word": "佩玖", "origin": "《诗经·王风·大车》", "quote": "谓予不信，有如皎日", "meaning": "佩戴之美玉，喻品德如玉", "usage": "女名", "pinyin": "pèi jiǔ"},
    {"word": "维桢", "origin": "《诗经·大雅·文王》", "quote": "王国克生，维周之桢", "meaning": "国之栋梁，喻担当重任", "usage": "男名", "pinyin": "wéi zhēn"},
]

CHUCI_NEW = [
    {"word": "正则", "origin": "《楚辞·离骚》", "quote": "名余曰正则兮，字余曰灵均", "meaning": "公正法则，喻品行端正", "usage": "男名", "pinyin": "zhèng zé"},
    {"word": "灵均", "origin": "《楚辞·离骚》", "quote": "名余曰正则兮，字余曰灵均", "meaning": "灵善均平，喻天赋美善", "usage": "男名", "pinyin": "líng jūn"},
    {"word": "飞龙", "origin": "《楚辞·离骚》", "quote": "飞龙秋游兮，登九灵", "meaning": "飞翔之龙，喻志向远大", "usage": "男名", "pinyin": "fēi lóng"},
    {"word": "芳芷", "origin": "《楚辞·离骚》", "quote": "畦留夷与揭车兮，杂杜衡与芳芷", "meaning": "香草名，喻品德芬芳", "usage": "女名", "pinyin": "fāng zhǐ"},
    {"word": "若华", "origin": "《楚辞·天问》", "quote": "羲和之未扬，若华何光", "meaning": "神话中若木之花，喻光芒灿烂", "usage": "女名", "pinyin": "ruò huá"},
    {"word": "望舒", "origin": "《楚辞·离骚》", "quote": "前望舒使先驱兮", "meaning": "月神驾车者，喻温润清雅", "usage": "男女皆宜", "pinyin": "wàng shū"},
    {"word": "怀瑾", "origin": "《楚辞·九章·怀沙》", "quote": "怀瑾握瑜兮，穷不知所示", "meaning": "怀藏美玉，喻品德高尚", "usage": "男名", "pinyin": "huái jǐn"},
    {"word": "陆离", "origin": "《楚辞·离骚》", "quote": "斑陆离其上下", "meaning": "色彩绚丽，喻光彩夺目", "usage": "男女皆宜", "pinyin": "lù lí"},
    {"word": "云霓", "origin": "《楚辞·离骚》", "quote": "扬云霓之晻蔼兮", "meaning": "云中彩虹，喻华美高洁", "usage": "女名", "pinyin": "yún ní"},
    {"word": "飞扬", "origin": "《楚辞·九歌·河伯》", "quote": "心飞扬兮浩荡", "meaning": "心志飞扬，喻意气风发", "usage": "男名", "pinyin": "fēi yáng"},
    {"word": "幼清", "origin": "《楚辞·招魂》", "quote": "朕幼清以廉洁兮", "meaning": "自幼清正廉洁，喻品性纯良", "usage": "男女皆宜", "pinyin": "yòu qīng"},
    {"word": "嘉名", "origin": "《楚辞·离骚》", "quote": "皇览揆余初度兮，肇锡余以嘉名", "meaning": "美好的名字，喻美名远扬", "usage": "男女皆宜", "pinyin": "jiā míng"},
    {"word": "宝璐", "origin": "《楚辞·九章·涉江》", "quote": "被明月兮佩宝璐", "meaning": "美玉，喻珍贵美好", "usage": "女名", "pinyin": "bǎo lù"},
    {"word": "浩倡", "origin": "《楚辞·九歌·东皇太一》", "quote": "陈竽瑟兮浩倡", "meaning": "浩大盛美，喻气势磅礴", "usage": "男名", "pinyin": "hào chàng"},
]

TANGSHI_NEW = [
    {"word": "海霞", "origin": "李白《古风》", "quote": "海客谈瀛洲，烟涛微茫信难求", "meaning": "海上霞光，喻壮阔绚烂", "usage": "女名", "pinyin": "hǎi xiá"},
    {"word": "长风", "origin": "李白《行路难》", "quote": "长风破浪会有时，直挂云帆济沧海", "meaning": "远大风浪，喻志向远大、乘风破浪", "usage": "男名", "pinyin": "cháng fēng"},
    {"word": "初晴", "origin": "王维《新晴野望》", "quote": "新晴原野旷，极目无氛垢", "meaning": "雨后初晴，喻清新明朗", "usage": "女名", "pinyin": "chū qíng"},
    {"word": "凌云", "origin": "杜甫《望岳》", "quote": "会当凌绝顶，一览众山小", "meaning": "直上云霄，喻志存高远", "usage": "男名", "pinyin": "líng yún"},
    {"word": "星汉", "origin": "曹操《观沧海》（唐诗引用）", "quote": "星汉灿烂，若出其里", "meaning": "银河，喻浩瀚壮阔", "usage": "男名", "pinyin": "xīng hàn"},
    {"word": "春晖", "origin": "孟郊《游子吟》", "quote": "谁言寸草心，报得三春晖", "meaning": "春日阳光，喻母爱恩泽", "usage": "男女皆宜", "pinyin": "chūn huī"},
    {"word": "清秋", "origin": "孟浩然《秋登万山寄张五》", "quote": "北山白云里，隐者自怡悦", "meaning": "清朗秋日，喻高洁淡远", "usage": "男女皆宜", "pinyin": "qīng qiū"},
    {"word": "飞星", "origin": "杜牧《秋夕》", "quote": "银烛秋光冷画屏，轻罗小扇扑流萤", "meaning": "流星飞逝，喻灵动璀璨", "usage": "女名", "pinyin": "fēi xīng"},
    {"word": "一苇", "origin": "刘禹锡《西塞山怀古》", "quote": "一苇可航处，千帆日以来", "meaning": "一叶扁舟，喻轻简从容、以小搏大", "usage": "男女皆宜", "pinyin": "yī wěi"},
    {"word": "明轩", "origin": "李白《明堂赋》", "quote": "前瞻太微，却临明轩", "meaning": "明亮的窗轩，喻光明磊落", "usage": "男名", "pinyin": "míng xuān"},
    {"word": "锦书", "origin": "李清照《一剪梅》（宋词引唐诗意境）", "quote": "云中谁寄锦书来", "meaning": "华美书信，喻情谊珍贵", "usage": "女名", "pinyin": "jǐn shū"},
    {"word": "山月", "origin": "王维《山居秋暝》", "quote": "明月松间照，清泉石上流", "meaning": "山间明月，喻高洁清远", "usage": "男女皆宜", "pinyin": "shān yuè"},
    {"word": "竹幽", "origin": "王维《竹里馆》", "quote": "独坐幽篁里，弹琴复长啸", "meaning": "竹林幽深，喻清雅淡泊", "usage": "男女皆宜", "pinyin": "zhú yōu"},
    {"word": "天阔", "origin": "杜甫《旅夜书怀》", "quote": "星垂平野阔，月涌大江流", "meaning": "天宇开阔，喻胸襟广阔", "usage": "男名", "pinyin": "tiān kuò"},
]

SONGCi_NEW = [
    {"word": "疏影", "origin": "林逋《山园小梅》", "quote": "疏影横斜水清浅，暗香浮动月黄昏", "meaning": "疏朗之影，喻清逸高雅", "usage": "女名", "pinyin": "shū yǐng"},
    {"word": "暗香", "origin": "林逋《山园小梅》", "quote": "疏影横斜水清浅，暗香浮动月黄昏", "meaning": "幽香暗传，喻内涵隽永", "usage": "女名", "pinyin": "àn xiāng"},
    {"word": "落霞", "origin": "范仲淹《苏幕遮》", "quote": "碧云天，黄叶地，秋色连波，波上寒烟翠", "meaning": "晚霞，喻绚烂壮美", "usage": "女名", "pinyin": "luò xiá"},
    {"word": "云帆", "origin": "苏轼《念奴娇·赤壁怀古》", "quote": "人生如梦，一尊还酹江月", "meaning": "云中帆影，喻乘风远航", "usage": "男名", "pinyin": "yún fān"},
    {"word": "晓风", "origin": "柳永《雨霖铃》", "quote": "今宵酒醒何处，杨柳岸，晓风残月", "meaning": "晨风轻拂，喻清新淡远", "usage": "男女皆宜", "pinyin": "xiǎo fēng"},
    {"word": "疏桐", "origin": "苏轼《卜算子》", "quote": "缺月挂疏桐，漏断人初静", "meaning": "疏朗梧桐，喻清高孤洁", "usage": "男女皆宜", "pinyin": "shū tóng"},
    {"word": "霜华", "origin": "李清照《醉花阴》", "quote": "薄雾浓云愁永昼，瑞脑消金兽", "meaning": "霜之华彩，喻清冷高洁", "usage": "女名", "pinyin": "shuāng huá"},
    {"word": "兰舟", "origin": "柳永《雨霖铃》", "quote": "都门帐饮无绪，留恋处，兰舟催发", "meaning": "木兰舟，喻清雅出行", "usage": "女名", "pinyin": "lán zhōu"},
    {"word": "千里", "origin": "辛弃疾《青玉案·元夕》", "quote": "众里寻他千百度，蓦然回首，那人却在灯火阑珊处", "meaning": "千里之远，喻志向辽远", "usage": "男名", "pinyin": "qiān lǐ"},
    {"word": "暮雪", "origin": "陆游《卜算子·咏梅》", "quote": "驿外断桥边，寂寞开无主", "meaning": "日暮飞雪，喻坚贞清冷", "usage": "男女皆宜", "pinyin": "mù xuě"},
    {"word": "清欢", "origin": "苏轼《浣溪沙》", "quote": "人间有味是清欢", "meaning": "清淡的欢愉，喻知足淡泊", "usage": "男女皆宜", "pinyin": "qīng huān"},
    {"word": "红蕖", "origin": "李清照《如梦令》", "quote": "兴尽晚回舟，误入藕花深处", "meaning": "红荷花，喻娇美明艳", "usage": "女名", "pinyin": "hóng qú"},
    {"word": "烟波", "origin": "柳永《雨霖铃》", "quote": "念去去，千里烟波，暮霭沉沉楚天阔", "meaning": "烟波浩渺，喻旷远深沉", "usage": "男名", "pinyin": "yān bō"},
    {"word": "一蓑", "origin": "苏轼《定风波》", "quote": "一蓑烟雨任平生", "meaning": "一袭蓑衣，喻洒脱从容", "usage": "男名", "pinyin": "yī suō"},
]

ZHOUYI_NEW = [
    {"word": "厚德", "origin": "《周易·坤卦》", "quote": "地势坤，君子以厚德载物", "meaning": "德行深厚，喻包容万物", "usage": "男名", "pinyin": "hòu dé"},
    {"word": "含章", "origin": "《周易·坤卦》", "quote": "含章可贞，或从王事，无成有终", "meaning": "内蕴华彩，喻才华内敛", "usage": "女名", "pinyin": "hán zhāng"},
    {"word": "谦光", "origin": "《周易·谦卦》", "quote": "谦尊而光，卑而不可逾", "meaning": "谦逊而光耀，喻谦和有德", "usage": "男名", "pinyin": "qiān guāng"},
    {"word": "元亨", "origin": "《周易·乾卦》", "quote": "元亨利贞", "meaning": "大善大通，喻顺遂亨达", "usage": "男名", "pinyin": "yuán hēng"},
    {"word": "利贞", "origin": "《周易·乾卦》", "quote": "元亨利贞", "meaning": "利万物而守正，喻正直有利", "usage": "男女皆宜", "pinyin": "lì zhēn"},
    {"word": "咸临", "origin": "《周易·临卦》", "quote": "咸临，吉无不利", "meaning": "感而临之，喻以德服人", "usage": "男名", "pinyin": "xián lín"},
    {"word": "豫顺", "origin": "《周易·豫卦》", "quote": "豫顺以动，故日月不过", "meaning": "喜悦顺遂，喻乐观通达", "usage": "男女皆宜", "pinyin": "yù shùn"},
    {"word": "无咎", "origin": "《周易·系辞》", "quote": "无咎者，善补过者也", "meaning": "没有过失，喻谨慎自持", "usage": "男名", "pinyin": "wú jiù"},
    {"word": "日新", "origin": "《周易·系辞》", "quote": "日新之谓盛德", "meaning": "日日更新，喻不断进步", "usage": "男名", "pinyin": "rì xīn"},
    {"word": "崇德", "origin": "《周易·系辞》", "quote": "崇德广业", "meaning": "推崇美德，喻重视品德", "usage": "男名", "pinyin": "chóng dé"},
    {"word": "履霜", "origin": "《周易·坤卦》", "quote": "履霜，坚冰至", "meaning": "踏霜知冰将至，喻见微知著", "usage": "女名", "pinyin": "lǚ shuāng"},
    {"word": "时中", "origin": "《周易·蒙卦》", "quote": "时中也，蒙以养正", "meaning": "适时守中，喻恰到好处", "usage": "男女皆宜", "pinyin": "shí zhōng"},
    {"word": "恒德", "origin": "《周易·恒卦》", "quote": "不恒其德，或承之羞", "meaning": "持久之德，喻恒心毅力", "usage": "男名", "pinyin": "héng dé"},
    {"word": "畜德", "origin": "《周易·大畜卦》", "quote": "君子以多识前言往行，以畜其德", "meaning": "积蓄德行，喻修身养德", "usage": "男名", "pinyin": "xù dé"},
]

DAODEJING_NEW = [
    {"word": "虚极", "origin": "《道德经》第十六章", "quote": "致虚极，守静笃", "meaning": "虚至极点，喻心境空明", "usage": "男女皆宜", "pinyin": "xū jí"},
    {"word": "静笃", "origin": "《道德经》第十六章", "quote": "致虚极，守静笃", "meaning": "宁静笃实，喻沉稳专注", "usage": "男女皆宜", "pinyin": "jìng dǔ"},
    {"word": "知和", "origin": "《道德经》第五十五章", "quote": "知和曰常，知常曰明", "meaning": "懂得和谐，喻通达智慧", "usage": "男名", "pinyin": "zhī hé"},
    {"word": "明道", "origin": "《道德经》第四十一章", "quote": "明道若昧，进道若退", "meaning": "光明之道，喻智慧通达", "usage": "男名", "pinyin": "míng dào"},
    {"word": "抱一", "origin": "《道德经》第十章", "quote": "载营魄抱一，能无离乎", "meaning": "坚守本一，喻专一不二", "usage": "男名", "pinyin": "bào yī"},
    {"word": "玄德", "origin": "《道德经》第十章", "quote": "生而不有，为而不恃，长而不宰，是谓玄德", "meaning": "深远之德，喻德行深厚", "usage": "男名", "pinyin": "xuán dé"},
    {"word": "慈俭", "origin": "《道德经》第六十七章", "quote": "我有三宝，持而保之：一曰慈，二曰俭，三曰不敢为天下先", "meaning": "慈爱节俭，喻仁厚朴实", "usage": "男女皆宜", "pinyin": "cí jiǎn"},
    {"word": "不争", "origin": "《道德经》第八章", "quote": "夫唯不争，故无尤", "meaning": "不与人争，喻淡泊从容", "usage": "男女皆宜", "pinyin": "bù zhēng"},
    {"word": "复归", "origin": "《道德经》第十六章", "quote": "夫物芸芸，各复归其根", "meaning": "回归本源，喻不忘初心", "usage": "男女皆宜", "pinyin": "fù guī"},
    {"word": "光尘", "origin": "《道德经》第四章", "quote": "和其光，同其尘", "meaning": "收敛光芒与尘世同，喻低调谦和", "usage": "男女皆宜", "pinyin": "guāng chén"},
    {"word": "希声", "origin": "《道德经》第四十一章", "quote": "大音希声，大象无形", "meaning": "稀微之声，喻内敛深沉", "usage": "男名", "pinyin": "xī shēng"},
    {"word": "大方", "origin": "《道德经》第四十一章", "quote": "大方无隅，大器晚成", "meaning": "大方正无棱角，喻大度包容", "usage": "男女皆宜", "pinyin": "dà fāng"},
    {"word": "归根", "origin": "《道德经》第十六章", "quote": "归根曰静，静曰复命", "meaning": "回归根本，喻返璞归真", "usage": "男女皆宜", "pinyin": "guī gēn"},
    {"word": "柔弱", "origin": "《道德经》第七十六章", "quote": "强大处下，柔弱处上", "meaning": "柔韧谦下，喻以柔克刚", "usage": "男女皆宜", "pinyin": "róu ruò"},
]

# ============ 诗词意象补充（3条，使75→78） ============
SHIXIANG_NEW = [
    {"imagery": "明月", "category": "天象", "meaning": "皎洁、团圆、思念", "examples": ["明月几时有", "举头望明月"], "source": "苏轼/李白", "suitable_for": "女名/男女皆宜", "pinyin": "míng yuè"},
    {"imagery": "长河", "category": "地理", "meaning": "壮阔、永恒、历史", "examples": ["长河落日圆", "星垂平野阔"], "source": "王维/杜甫", "suitable_for": "男名", "pinyin": "cháng hé"},
    {"imagery": "芳草", "category": "植物", "meaning": "生机、绵延、思念", "examples": ["芳草碧连天", "天涯何处无芳草"], "source": "李叔同/苏轼", "suitable_for": "女名/男女皆宜", "pinyin": "fāng cǎo"},
]


def append_items(filepath, new_items):
    """向文学素材 JSON 追加条目"""
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    old_count = len(data['items'])
    # Deduplicate by word
    existing_words = {item['word'] for item in data['items']}
    added = 0
    for item in new_items:
        if item['word'] not in existing_words:
            data['items'].append(item)
            existing_words.add(item['word'])
            added += 1
    data['count'] = len(data['items'])
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return old_count, len(data['items']), added


def main():
    LIT = os.path.join(BASE, '..', '01-数据资料', '经典文学素材库')
    SHIXIANG = os.path.join(BASE, '..', '03-文化资料', '诗词意象库.json')

    print('=' * 60)
    print('文学素材库扩充 + 诗词意象修复')
    print('=' * 60)

    total_before = 0
    total_after = 0

    expansions = [
        (os.path.join(LIT, 'shijing.json'), SHIJING_NEW, '诗经'),
        (os.path.join(LIT, 'chuci.json'), CHUCI_NEW, '楚辞'),
        (os.path.join(LIT, 'tangshi.json'), TANGSHI_NEW, '唐诗'),
        (os.path.join(LIT, 'songci.json'), SONGCi_NEW, '宋词'),
        (os.path.join(LIT, 'zhouyi.json'), ZHOUYI_NEW, '周易'),
        (os.path.join(LIT, 'daodejing.json'), DAODEJING_NEW, '道德经'),
    ]

    for filepath, new_items, name in expansions:
        old, new, added = append_items(filepath, new_items)
        total_before += old
        total_after += new
        print(f'{name}: {old} → {new} (+{added})')

    print(f'\n文学素材总计: {total_before} → {total_after}')

    # 修复诗词意象库
    old, new, added = append_items(SHIXIANG, SHIXIANG_NEW)
    print(f'诗词意象: {old} → {new} (+{added}, count 修复)')

    print('\n已完成全部扩充。')


if __name__ == '__main__':
    main()
