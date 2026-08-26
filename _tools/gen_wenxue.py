# -*- coding: utf-8 -*-
"""生成经典文学素材库 JSON（诗经/楚辞/唐诗/宋词/周易/道德经）"""
import json, os

SCHEMA = {
    "name": "经典文学取名素材字段规范",
    "version": "1.0",
    "fields": [
        {"key": "word", "type": "string", "description": "可取名的字/词", "example": "修远"},
        {"key": "origin", "type": "string", "description": "出处（书名·篇名）", "example": "《楚辞·离骚》"},
        {"key": "quote", "type": "string", "description": "原句（含上下文）", "example": "路漫漫其修远兮，吾将上下而求索"},
        {"key": "meaning", "type": "string", "description": "释义与取名寓意", "example": "道路遥远而漫长，比喻求索之路"},
        {"key": "usage", "type": "string", "description": "适用建议（性别/风格）", "example": "男女皆宜，古风"},
        {"key": "pinyin", "type": "string", "description": "读音（带声调，空格分隔）", "example": "xiū yuǎn"},
    ],
    "note": "素材为人工精选常用出处，生产环境可按'经典→篇目→原句→释义'结构持续扩充",
}

SHIJING = {
    "source": "诗经",
    "desc": "中国最早的诗歌总集，取名用字古雅含蓄，多用于'古风/文雅'风格",
    "items": [
        {"word": "清扬", "origin": "《诗经·郑风·野有蔓草》", "quote": "有美一人，清扬婉兮", "meaning": "眉目清秀、神采飞扬", "usage": "女名多用", "pinyin": "qīng yáng"},
        {"word": "静姝", "origin": "《诗经·邶风·静女》", "quote": "静女其姝，俟我于城隅", "meaning": "娴静美好的女子", "usage": "女名", "pinyin": "jìng shū"},
        {"word": "徽音", "origin": "《诗经·大雅·思齐》", "quote": "大姒嗣徽音，则百斯男", "meaning": "美好的声誉、美德（林徽因名出此）", "usage": "女名", "pinyin": "huī yīn"},
        {"word": "维桢", "origin": "《诗经·大雅·文王》", "quote": "王国克生，维周之桢", "meaning": "国家的栋梁之材", "usage": "男名", "pinyin": "wéi zhēn"},
        {"word": "鹤鸣", "origin": "《诗经·小雅·鹤鸣》", "quote": "鹤鸣于九皋，声闻于天", "meaning": "贤才名声远播", "usage": "男名", "pinyin": "hè míng"},
        {"word": "懿德", "origin": "《诗经·大雅·烝民》", "quote": "民之秉彝，好是懿德", "meaning": "美好的品德", "usage": "男女皆宜", "pinyin": "yì dé"},
        {"word": "昭明", "origin": "《诗经·大雅·既醉》", "quote": "昭明有融，高朗令终", "meaning": "光明显耀、前程光明", "usage": "男名", "pinyin": "zhāo míng"},
        {"word": "灼华", "origin": "《诗经·周南·桃夭》", "quote": "桃之夭夭，灼灼其华", "meaning": "桃花灿烂盛开，青春焕发", "usage": "女名", "pinyin": "zhuó huá"},
        {"word": "燕婉", "origin": "《诗经·邶风·新台》", "quote": "燕婉之求，得此戚施", "meaning": "温婉美好", "usage": "女名", "pinyin": "yàn wǎn"},
        {"word": "露晞", "origin": "《诗经·小雅·湛露》", "quote": "湛湛露斯，匪阳不晞", "meaning": "露水待朝阳而干，含生机之意", "usage": "男女皆宜", "pinyin": "lù xī"},
        {"word": "甘棠", "origin": "《诗经·召南·甘棠》", "quote": "蔽芾甘棠，勿剪勿伐", "meaning": "德政爱民的象征", "usage": "男名", "pinyin": "gān táng"},
        {"word": "振鹭", "origin": "《诗经·周颂·振鹭》", "quote": "振鹭于飞，于彼西雍", "meaning": "白鹭振翅高飞，喻高洁", "usage": "男女皆宜", "pinyin": "zhèn lù"},
        {"word": "嘉树", "origin": "《诗经·小雅·南有嘉鱼》", "quote": "南有嘉鱼，烝然罩罩", "meaning": "美好的树木，引申嘉美", "usage": "男女皆宜", "pinyin": "jiā shù"},
        {"word": "洵美", "origin": "《诗经·邶风·静女》", "quote": "自牧归荑，洵美且异", "meaning": "确实美好而与众不同", "usage": "女名", "pinyin": "xún měi"},
        {"word": "秉彝", "origin": "《诗经·大雅·烝民》", "quote": "天生烝民，有物有则；民之秉彝，好是懿德", "meaning": "秉持常道、天性善良", "usage": "男名", "pinyin": "bǐng yí"},
        {"word": "悠宁", "origin": "《诗经·小雅·斯干》", "quote": "君子攸宁", "meaning": "安宁、安居", "usage": "男女皆宜", "pinyin": "yōu níng"},
    ],
}

CHUCI = {
    "source": "楚辞",
    "desc": "浪漫主义源头，意象瑰丽，多用于'大气/古典'风格",
    "items": [
        {"word": "修远", "origin": "《楚辞·离骚》", "quote": "路漫漫其修远兮，吾将上下而求索", "meaning": "道路长远，喻志向高远、不懈求索", "usage": "男名", "pinyin": "xiū yuǎn"},
        {"word": "望舒", "origin": "《楚辞·离骚》", "quote": "前望舒使先驱兮", "meaning": "神话中为月驾车之神，喻美好光明", "usage": "女名", "pinyin": "wàng shū"},
        {"word": "陆离", "origin": "《楚辞·离骚》", "quote": "纷总总其离合兮，斑陆离其上下", "meaning": "光彩绚丽、参差错综", "usage": "男女皆宜", "pinyin": "lù lí"},
        {"word": "杜若", "origin": "《楚辞·九歌·湘君》", "quote": "采芳洲兮杜若，将以遗兮下女", "meaning": "香草名，喻高洁芬芳", "usage": "女名", "pinyin": "dù ruò"},
        {"word": "怀瑾", "origin": "《楚辞·九章·怀沙》", "quote": "怀瑾握瑜兮，穷不知所示", "meaning": "怀藏美玉，喻品德高洁", "usage": "男名", "pinyin": "huái jǐn"},
        {"word": "若英", "origin": "《楚辞·九歌·云中君》", "quote": "浴兰汤兮沐芳，华采衣兮若英", "meaning": "如花般美丽", "usage": "女名", "pinyin": "ruò yīng"},
        {"word": "嘉名", "origin": "《楚辞·离骚》", "quote": "皇览揆余初度兮，肇锡余以嘉名", "meaning": "美好的名字", "usage": "男女皆宜", "pinyin": "jiā míng"},
        {"word": "峻茂", "origin": "《楚辞·离骚》", "quote": "冀枝叶之峻茂兮，愿俟时乎吾将刈", "meaning": "高大茂盛，喻人才茁壮", "usage": "男名", "pinyin": "jùn mào"},
        {"word": "江离", "origin": "《楚辞·离骚》", "quote": "扈江离与辟芷兮，纫秋兰以为佩", "meaning": "香草名（川芎），喻高洁", "usage": "男女皆宜", "pinyin": "jiāng lí"},
        {"word": "兰芷", "origin": "《楚辞·九章·悲回风》", "quote": "兰芷变而不芳兮，荃蕙化而为茅", "meaning": "兰与芷皆香草，喻高洁品性", "usage": "女名", "pinyin": "lán zhǐ"},
        {"word": "芳菲", "origin": "《楚辞·九章·思美人》", "quote": "芳菲菲而难亏兮，芬至今犹未沫", "meaning": "芳香繁盛，喻美好永存", "usage": "女名", "pinyin": "fāng fēi"},
        {"word": "正则", "origin": "《楚辞·离骚》", "quote": "名余曰正则兮，字余曰灵均", "meaning": "公正而有法则（屈原本名）", "usage": "男名", "pinyin": "zhèng zé"},
        {"word": "丰隆", "origin": "《楚辞·离骚》", "quote": "吾令丰隆乘云兮，求宓妃之所在", "meaning": "云神之名，气象宏大", "usage": "男名", "pinyin": "fēng lóng"},
        {"word": "飞廉", "origin": "《楚辞·离骚》", "quote": "前望舒使先驱兮，后飞廉使奔属", "meaning": "风神之名，喻迅捷", "usage": "男名", "pinyin": "fēi lián"},
        {"word": "琼佩", "origin": "《楚辞·离骚》", "quote": "何琼佩之偃蹇兮，众薆然而蔽之", "meaning": "美玉做的佩饰，喻美好才德", "usage": "女名", "pinyin": "qióng pèi"},
    ],
}

TANGSHI = {
    "source": "唐诗",
    "desc": "气象万千、意境开阔，多用于'大气/明快'风格",
    "items": [
        {"word": "润物", "origin": "杜甫《春夜喜雨》", "quote": "随风潜入夜，润物细无声", "meaning": "默默滋润万物，喻温和仁德", "usage": "男女皆宜", "pinyin": "rùn wù"},
        {"word": "云帆", "origin": "李白《行路难》", "quote": "长风破浪会有时，直挂云帆济沧海", "meaning": "高挂云帆济沧海，喻志向远大", "usage": "男名", "pinyin": "yún fān"},
        {"word": "清泉", "origin": "王维《山居秋暝》", "quote": "明月松间照，清泉石上流", "meaning": "清澈的泉水，喻澄澈高洁", "usage": "男女皆宜", "pinyin": "qīng quán"},
        {"word": "长天", "origin": "王勃《滕王阁序》", "quote": "落霞与孤鹜齐飞，秋水共长天一色", "meaning": "辽阔的天空，喻胸怀宽广", "usage": "男名", "pinyin": "cháng tiān"},
        {"word": "凌绝", "origin": "杜甫《望岳》", "quote": "会当凌绝顶，一览众山小", "meaning": "登上顶峰，喻志存高远", "usage": "男名", "pinyin": "líng jué"},
        {"word": "德馨", "origin": "刘禹锡《陋室铭》", "quote": "斯是陋室，惟吾德馨", "meaning": "品德芳馨远播", "usage": "男女皆宜", "pinyin": "dé xīn"},
        {"word": "枫林", "origin": "杜牧《山行》", "quote": "停车坐爱枫林晚，霜叶红于二月花", "meaning": "秋日枫林，喻热烈绚烂", "usage": "男女皆宜", "pinyin": "fēng lín"},
        {"word": "望月", "origin": "张九龄《望月怀远》", "quote": "海上生明月，天涯共此时", "meaning": "望月怀远，情意绵长", "usage": "男女皆宜", "pinyin": "wàng yuè"},
        {"word": "青莲", "origin": "李白号青莲居士", "quote": "清水出芙蓉，天然去雕饰（《经离乱后天恩流夜郎忆旧游书怀赠江夏韦太守良宰》）", "meaning": "清雅纯净、不事雕琢", "usage": "女名", "pinyin": "qīng lián"},
        {"word": "知节", "origin": "王维《相思》", "quote": "红豆生南国，春来发几枝。愿君多采撷，此物最相思", "meaning": "（取'知'字）有节操、知进退", "usage": "男名", "pinyin": "zhī jié"},
        {"word": "千里", "origin": "王之涣《登鹳雀楼》", "quote": "欲穷千里目，更上一层楼", "meaning": "视野开阔、志存高远", "usage": "男名", "pinyin": "qiān lǐ"},
        {"word": "清秋", "origin": "李白《秋登宣城谢朓北楼》", "quote": "人烟寒橘柚，秋色老梧桐", "meaning": "明净爽朗的秋天", "usage": "女名", "pinyin": "qīng qiū"},
        {"word": "朗月", "origin": "李白《赠孟浩然》", "quote": "高山安可仰，徒此揖清芬", "meaning": "（取'朗'字意）明朗如月", "usage": "男女皆宜", "pinyin": "lǎng yuè"},
        {"word": "知微", "origin": "杜甫《月夜忆舍弟》", "quote": "露从今夜白，月是故乡明", "meaning": "（取'知'字）见微知著", "usage": "男名", "pinyin": "zhī wēi"},
        {"word": "致远", "origin": "诸葛亮《诫子书》（三国·蜀）", "quote": "非淡泊无以明志，非宁静无以致远", "meaning": "心境宁静方能实现远大目标", "usage": "男名", "pinyin": "zhì yuǎn"},
    ],
}

SONGCI = {
    "source": "宋词",
    "desc": "婉约清丽、意境隽永，多用于'文雅/婉约'风格",
    "items": [
        {"word": "婵娟", "origin": "苏轼《水调歌头》", "quote": "但愿人长久，千里共婵娟", "meaning": "明月、美好，喻团圆美好", "usage": "女名", "pinyin": "chán juān"},
        {"word": "晓风", "origin": "柳永《雨霖铃》", "quote": "今宵酒醒何处？杨柳岸，晓风残月", "meaning": "清晨微风，清冷诗意", "usage": "女名", "pinyin": "xiǎo fēng"},
        {"word": "风荷", "origin": "周邦彦《苏幕遮》", "quote": "水面清圆，一一风荷举", "meaning": "风中荷花亭亭玉立", "usage": "女名", "pinyin": "fēng hé"},
        {"word": "微雨", "origin": "晏几道《临江仙》", "quote": "落花人独立，微雨燕双飞", "meaning": "蒙蒙细雨，温柔诗意", "usage": "女名", "pinyin": "wēi yǔ"},
        {"word": "锦书", "origin": "李清照《一剪梅》", "quote": "云中谁寄锦书来，雁字回时，月满西楼", "meaning": "美好的书信，喻才情与情意", "usage": "女名", "pinyin": "jǐn shū"},
        {"word": "云和", "origin": "岳飞《满江红》", "quote": "三十功名尘与土，八千里路云和月", "meaning": "（取'云'字）壮怀高远", "usage": "男名", "pinyin": "yún hé"},
        {"word": "燕归", "origin": "晏殊《浣溪沙》", "quote": "无可奈何花落去，似曾相识燕归来", "meaning": "燕子归来，喻重逢与希望", "usage": "女名", "pinyin": "yàn guī"},
        {"word": "弄影", "origin": "张先《天仙子》", "quote": "沙上并禽池上暝，云破月来花弄影", "meaning": "花影婆娑，灵动优美", "usage": "女名", "pinyin": "nòng yǐng"},
        {"word": "碧云", "origin": "范仲淹《苏幕遮》", "quote": "碧云天，黄叶地，秋色连波，波上寒烟翠", "meaning": "碧蓝的天空，高远澄澈", "usage": "男女皆宜", "pinyin": "bì yún"},
        {"word": "冷月", "origin": "姜夔《扬州慢》", "quote": "二十四桥仍在，波心荡，冷月无声", "meaning": "清冷月光，意境深远", "usage": "男女皆宜（偏文艺）", "pinyin": "lěng yuè"},
        {"word": "知否", "origin": "李清照《如梦令》", "quote": "知否，知否？应是绿肥红瘦", "meaning": "（取'知'字）聪慧明理", "usage": "女名", "pinyin": "zhī fǒu"},
        {"word": "清圆", "origin": "周邦彦《苏幕遮》", "quote": "水面清圆，一一风荷举", "meaning": "清润圆正，喻品格端正", "usage": "男女皆宜", "pinyin": "qīng yuán"},
        {"word": "星野", "origin": "辛弃疾《西江月》", "quote": "七八个星天外，两三点雨山前", "meaning": "星空旷野，开阔浪漫", "usage": "男名", "pinyin": "xīng yě"},
        {"word": "初见", "origin": "晏几道《临江仙》", "quote": "当时明月在，曾照彩云归", "meaning": "（取'初见'意象）美好初心", "usage": "女名", "pinyin": "chū jiàn"},
        {"word": "晴柔", "origin": "杨万里《小池》", "quote": "泉眼无声惜细流，树阴照水爱晴柔", "meaning": "晴日温柔，明媚和煦", "usage": "女名", "pinyin": "qíng róu"},
    ],
}

ZHOUYI = {
    "source": "周易",
    "desc": "群经之首，哲理深厚，多用于'大气/稳重/吉祥'风格",
    "items": [
        {"word": "自强", "origin": "《周易·乾卦》", "quote": "天行健，君子以自强不息", "meaning": "刚健有为、奋发图强", "usage": "男名", "pinyin": "zì qiáng"},
        {"word": "厚德", "origin": "《周易·坤卦》", "quote": "地势坤，君子以厚德载物", "meaning": "宽厚德行、包容万物", "usage": "男名", "pinyin": "hòu dé"},
        {"word": "谦谦", "origin": "《周易·谦卦》", "quote": "谦谦君子，卑以自牧", "meaning": "谦逊有礼、自律修身", "usage": "男名", "pinyin": "qiān qiān"},
        {"word": "自牧", "origin": "《周易·谦卦》", "quote": "谦谦君子，卑以自牧", "meaning": "自我修养", "usage": "男名", "pinyin": "zì mù"},
        {"word": "天佑", "origin": "《周易·大有卦》", "quote": "自天佑之，吉无不利", "meaning": "上天保佑，吉祥顺遂", "usage": "男女皆宜", "pinyin": "tiān yòu"},
        {"word": "昭明", "origin": "《周易·晋卦》", "quote": "君子以自昭明德", "meaning": "自我彰显光明德行", "usage": "男名", "pinyin": "zhāo míng"},
        {"word": "顺德", "origin": "《周易·升卦》", "quote": "君子以顺德，积小以高大", "meaning": "顺应德行，积小成大", "usage": "男女皆宜", "pinyin": "shùn dé"},
        {"word": "中孚", "origin": "《周易·中孚卦》", "quote": "中孚，豚鱼吉，利涉大川", "meaning": "诚信之德，感通万物", "usage": "男名", "pinyin": "zhōng fú"},
        {"word": "观光", "origin": "《周易·观卦》", "quote": "观国之光，利用宾于王", "meaning": "见识宏阔、光耀门庭", "usage": "男名", "pinyin": "guān guāng"},
        {"word": "畜德", "origin": "《周易·大畜卦》", "quote": "君子以多识前言往行，以畜其德", "meaning": "积蓄德行", "usage": "男名", "pinyin": "xù dé"},
        {"word": "立恒", "origin": "《周易·恒卦》", "quote": "君子以立不易方", "meaning": "立身有恒、坚守正道", "usage": "男名", "pinyin": "lì héng"},
        {"word": "嘉遁", "origin": "《周易·遁卦》", "quote": "嘉遁贞吉，以正志也", "meaning": "适时而退、坚守正志", "usage": "男名", "pinyin": "jiā dùn"},
        {"word": "如临", "origin": "《周易·临卦》", "quote": "君子以教思无穷，容保民无疆", "meaning": "（取'临'字）居高临下、仁厚", "usage": "男名", "pinyin": "rú lín"},
        {"word": "晋升", "origin": "《周易·晋卦》", "quote": "晋，进也。明出地上", "meaning": "进取向上、光明渐盛", "usage": "男名", "pinyin": "jìn shēng"},
        {"word": "复见", "origin": "《周易·复卦》", "quote": "复，其见天地之心乎", "meaning": "（取'复'字）周而复始、生生不息", "usage": "男女皆宜", "pinyin": "fù jiàn"},
    ],
}

DAODEJING = {
    "source": "道德经",
    "desc": "道家经典，哲理冲淡，多用于'淡雅/睿智'风格",
    "items": [
        {"word": "若水", "origin": "《道德经》第八章", "quote": "上善若水。水善利万物而不争", "meaning": "最高的善像水一样，利万物而不争", "usage": "男女皆宜", "pinyin": "ruò shuǐ"},
        {"word": "上善", "origin": "《道德经》第八章", "quote": "上善若水", "meaning": "至高的善", "usage": "男女皆宜", "pinyin": "shàng shàn"},
        {"word": "守静", "origin": "《道德经》第十六章", "quote": "致虚极，守静笃", "meaning": "保持内心的虚静", "usage": "男女皆宜", "pinyin": "shǒu jìng"},
        {"word": "若谷", "origin": "《道德经》第四十一章", "quote": "上德若谷", "meaning": "最高德行如山谷般虚怀", "usage": "男名", "pinyin": "ruò gǔ"},
        {"word": "抱朴", "origin": "《道德经》第十九章", "quote": "见素抱朴，少私寡欲", "meaning": "保持本真、淳朴", "usage": "男女皆宜", "pinyin": "bào pǔ"},
        {"word": "和光", "origin": "《道德经》第四章", "quote": "和其光，同其尘", "meaning": "含敛锋芒、与世和同", "usage": "男女皆宜", "pinyin": "hé guāng"},
        {"word": "知足", "origin": "《道德经》第三十三章", "quote": "知足者富", "meaning": "知足常乐、内心富足", "usage": "男女皆宜", "pinyin": "zhī zú"},
        {"word": "守柔", "origin": "《道德经》第五十二章", "quote": "守柔曰强", "meaning": "保持柔韧才是真正的强", "usage": "男名", "pinyin": "shǒu róu"},
        {"word": "常道", "origin": "《道德经》第一章", "quote": "道可道，非常道", "meaning": "恒常的大道", "usage": "男名", "pinyin": "cháng dào"},
        {"word": "希声", "origin": "《道德经》第四十一章", "quote": "大音希声，大象无形", "meaning": "最大的声响反而无声，喻深厚内敛", "usage": "男女皆宜", "pinyin": "xī shēng"},
        {"word": "自然", "origin": "《道德经》第二十五章", "quote": "人法地，地法天，天法道，道法自然", "meaning": "顺其自然、本真天成", "usage": "男女皆宜", "pinyin": "zì rán"},
        {"word": "善行", "origin": "《道德经》第二十七章", "quote": "善行无辙迹", "meaning": "善于行事而不留痕迹", "usage": "男名", "pinyin": "shàn xíng"},
        {"word": "静笃", "origin": "《道德经》第十六章", "quote": "致虚极，守静笃", "meaning": "内心宁静笃定", "usage": "男女皆宜", "pinyin": "jìng dǔ"},
        {"word": "知常", "origin": "《道德经》第十六章", "quote": "知常曰明", "meaning": "了解恒常规律即为明智", "usage": "男名", "pinyin": "zhī cháng"},
        {"word": "至简", "origin": "《道德经》衍义", "quote": "大道至简（后人对'大音希声'等句的概括）", "meaning": "真正的道理最简单", "usage": "男女皆宜", "pinyin": "zhì jiǎn"},
    ],
}

def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01-数据资料", "经典文学素材库"))
    datasets = {
        "shijing.json": SHIJING,
        "chuci.json": CHUCI,
        "tangshi.json": TANGSHI,
        "songci.json": SONGCI,
        "zhouyi.json": ZHOUYI,
        "daodejing.json": DAODEJING,
    }
    total = 0
    for fname, data in datasets.items():
        data["count"] = len(data["items"])
        total += len(data["items"])
        with open(os.path.join(base, fname), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(base, "wenxue_schema.json"), "w", encoding="utf-8") as f:
        json.dump(SCHEMA, f, ensure_ascii=False, indent=2)
    print("文学素材生成完毕，共", total, "条")

if __name__ == "__main__":
    main()
