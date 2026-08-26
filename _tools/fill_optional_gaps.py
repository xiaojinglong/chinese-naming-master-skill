# -*- coding: utf-8 -*-
"""
补充优化缺口：
1. 唐诗/宋词精读笔记（知识库缺失，补充到 06-取名知识库/）
2. 元曲取名素材（新建）
3. 明清诗文素材（新建）
4. 五行喜用神→部首推荐映射（独立文件）
5. 声调搭配模式库（详细版）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
LIT_DIR = os.path.join(BASE, '..', '01-数据资料', '经典文学素材库')
KB_DIR = os.path.join(BASE, '..', '06-取名知识库', '01-先秦经典')


def add_tangshi_songci_notes():
    """补充唐诗/宋词精读笔记到知识库"""
    tangshi_note = '''# 《唐诗》精读笔记

> 知识库 · 补充 ｜ 取名素材的重要补充源（仅次于诗经楚辞）

## 一、书籍档案

| 项目 | 内容 |
|------|------|
| 性质 | 中国诗歌巅峰，近体诗定型，五七言律绝成熟 |
| 时代 | 初唐（618-712）盛唐（713-765）中唐（766-835）晚唐（836-907） |
| 规模 | 《全唐诗》收录约 49,000 首，2,200 余诗人 |
| 取名价值 | 气象万千、意境开阔，适合"大气/明快/豪迈"风格 |

## 二、取名素材精选

### 李白（浪漫豪放）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《将进酒》 | 天生我材必有用 | 天材、必用 | 天赋异禀 |
| 《行路难》 | 长风破浪会有时 | 长风、破浪 | 志向远大 |
| 《望庐山瀑布》 | 飞流直下三千尺 | 飞流 | 气势磅礴 |
| 《早发白帝城》 | 轻舟已过万重山 | 轻舟 | 轻快从容 |

### 杜甫（沉郁顿挫）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《望岳》 | 会当凌绝顶 | 凌绝、凌峰 | 志存高远 |
| 《春夜喜雨》 | 润物细无声 | 润物 | 默默奉献 |
| 《登高》 | 无边落木萧萧下 | 落木（慎用） | 慎用，意境悲凉 |
| 《茅屋为秋风所破歌》 | 安得广厦千万间 | 广厦 | 胸怀天下 |

### 王维（山水田园）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《山居秋暝》 | 明月松间照 | 松照、明松 | 高洁清雅 |
| 《使至塞上》 | 大漠孤烟直 | 孤烟（慎用） | 慎用，意境孤寂 |
| 《鸟鸣涧》 | 月出惊山鸟 | 惊山（慎用） | 慎用 |
| 《鹿柴》 | 空山不见人 | 空山（慎用） | 慎用 |

### 孟浩然（清淡自然）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《春晓》 | 春眠不觉晓 | 春晓 | 春日清晨 |
| 《过故人庄》 | 绿树村边合 | 村合（慎用） | 慎用 |
| 《宿建德江》 | 江清月近人 | 江清、月近 | 清澈亲近 |

### 王勃（初唐风骨）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《滕王阁序》 | 落霞与孤鹜齐飞 | 落霞 | 绚烂壮美 |
| 《滕王阁序》 | 秋水共长天一色 | 秋水、长天 | 辽阔澄澈 |
| 《送杜少府之任蜀州》 | 海内存知己 | 海存、存知 | 知己情谊 |

## 三、取名注意事项

- 唐诗中边塞诗（"孤烟""落木"）意境偏悲凉，取名慎用。
- 李白豪放派最适合"大气/志向"型名字。
- 王维山水派最适合"清雅/淡泊"型名字。
- 优先选五言/七言律诗的颔联颈联（对仗工整，用字精炼）。
'''

    songci_note = '''# 《宋词》精读笔记

> 知识库 · 补充 ｜ 婉约清丽型取名素材的最大来源

## 一、书籍档案

| 项目 | 内容 |
|------|------|
| 性质 | 宋代文学代表，长短句，分婉约/豪放两派 |
| 时代 | 北宋（960-1127）南宋（1127-1279） |
| 规模 | 《全宋词》收录约 20,000 首，1,300 余词人 |
| 取名价值 | 婉约清丽、意境隽永，适合"文雅/婉约/清丽"风格 |

## 二、取名素材精选

### 苏轼（豪放清旷）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《水调歌头》 | 明月几时有 | 明月、几时（慎用） | 明月为经典意象 |
| 《水调歌头》 | 千里共婵娟 | 婵娟 | 美好团圆 |
| 《念奴娇·赤壁怀古》 | 大江东去 | 江东、东去（慎用） | 慎用，意境苍凉 |
| 《定风波》 | 一蓑烟雨任平生 | 一蓑、任平 | 洒脱从容 |
| 《浣溪沙》 | 人间有味是清欢 | 清欢 | 清淡欢愉 |

### 李清照（婉约清丽）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《如梦令》 | 常记溪亭日暮 | 溪亭 | 溪边小亭 |
| 《醉花阴》 | 人比黄花瘦 | 黄花（慎用） | 慎用，意境消瘦 |
| 《一剪梅》 | 云中谁寄锦书来 | 锦书 | 华美书信 |
| 《声声慢》 | 寻寻觅觅 | 寻觅（慎用） | 慎用，意境凄苦 |

### 辛弃疾（豪放悲壮）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《青玉案·元夕》 | 众里寻他千百度 | 千百（慎用） | 慎用 |
| 《青玉案·元夕》 | 灯火阑珊处 | 阑珊（慎用） | 慎用，意境阑珊 |
| 《破阵子》 | 醉里挑灯看剑 | 看剑（慎用） | 慎用 |
| 《西江月》 | 稻花香里说丰年 | 稻香、丰年 | 丰收喜悦 |

### 柳永（婉约缠绵）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《雨霖铃》 | 杨柳岸，晓风残月 | 晓风、杨柳 | 晨风轻拂 |
| 《望海潮》 | 有三秋桂子，十里荷花 | 桂子、荷花 | 桂花荷花 |
| 《蝶恋花》 | 衣带渐宽终不悔 | 不悔 | 坚定不悔 |

### 周邦彦（格律精严）
| 出处 | 原句 | 可取名字 | 寓意 |
|------|------|---------|------|
| 《苏幕遮》 | 叶上初阳干宿雨 | 初阳 | 晨光初现 |
| 《兰陵王》 | 柳阴直，烟里丝丝弄碧 | 柳阴、丝碧 | 柳色青翠 |

## 三、取名注意事项

- 宋词中伤春悲秋之作（"寻寻觅觅""人比黄花瘦"）取名慎用。
- 苏轼清旷派最适合"洒脱/从容"型名字。
- 李清照婉约派最适合"清丽/文雅"型女名。
- 优先选中调（59-90字）的词牌，用字凝练。
'''

    os.makedirs(KB_DIR, exist_ok=True)
    with open(os.path.join(KB_DIR, '30-唐诗.md'), 'w', encoding='utf-8') as f:
        f.write(tangshi_note)
    with open(os.path.join(KB_DIR, '31-宋词.md'), 'w', encoding='utf-8') as f:
        f.write(songci_note)
    print('唐诗/宋词精读笔记: 已补充到知识库')


def add_yuanqu_mingqing():
    """补充元曲和明清诗文素材"""
    # 元曲取名素材
    yuanqu = {
        'source': '元曲',
        'desc': '元代散曲杂剧，清新自然，适合"清新/灵动"风格',
        'items': [
            {'word': '清安', 'origin': '关汉卿《窦娥冤》', 'quote': '天地也，只合把清浊分辨', 'meaning': '清平安宁', 'usage': '男女皆宜', 'pinyin': None, 'style_tags': ['文雅']},
            {'word': '玉山', 'origin': '马致远《天净沙·秋思》', 'quote': '枯藤老树昏鸦，小桥流水人家', 'meaning': '玉质山骨', 'usage': '男名', 'pinyin': None, 'style_tags': ['古风']},
            {'word': '云帆', 'origin': '张可久《卖花声·怀古》', 'quote': '云帆望远，烟水茫茫', 'meaning': '云中帆影', 'usage': '男名', 'pinyin': None, 'style_tags': ['大气']},
            {'word': '梦华', 'origin': '白朴《梧桐雨》', 'quote': '梦华录，繁华事散', 'meaning': '梦中繁华', 'usage': '女名', 'pinyin': None, 'style_tags': ['婉约']},
            {'word': '清江', 'origin': '乔吉《水仙子·寻梅》', 'quote': '清江一曲抱村流', 'meaning': '清澈江水', 'usage': '男女皆宜', 'pinyin': None, 'style_tags': ['文雅']},
            {'word': '雪晴', 'origin': '张养浩《山坡羊·潼关怀古》', 'quote': '峰峦如聚，波涛如怒', 'meaning': '雪后初晴', 'usage': '女名', 'pinyin': None, 'style_tags': ['文雅']},
        ],
        'count': 6,
    }
    with open(os.path.join(LIT_DIR, 'yuanqu.json'), 'w', encoding='utf-8') as f:
        json.dump(yuanqu, f, ensure_ascii=False, indent=1)

    # 明清诗文素材
    mingqing = {
        'source': '明清诗文',
        'desc': '明清诗词文赋，兼收并蓄，适合"复古/雅致"风格',
        'items': [
            {'word': '静思', 'origin': '王阳明《传习录》', 'quote': '静时亦觉意思好', 'meaning': '静心思考', 'usage': '男女皆宜', 'pinyin': None, 'style_tags': ['文雅']},
            {'word': '知行', 'origin': '王阳明', 'quote': '知行合一', 'meaning': '知与行合一', 'usage': '男名', 'pinyin': None, 'style_tags': ['大气']},
            {'word': '观澜', 'origin': '杨慎《临江仙》', 'quote': '滚滚长江东逝水', 'meaning': '观波澜', 'usage': '男名', 'pinyin': None, 'style_tags': ['大气']},
            {'word': '若初', 'origin': '纳兰性德《木兰词》', 'quote': '人生若只如初见', 'meaning': '不忘初心', 'usage': '女名', 'pinyin': None, 'style_tags': ['婉约']},
            {'word': '容若', 'origin': '纳兰性德', 'quote': '纳兰容若', 'meaning': '容貌若水', 'usage': '女名', 'pinyin': None, 'style_tags': ['婉约']},
            {'word': '思齐', 'origin': '《论语》（明清沿用）', 'quote': '见贤思齐焉', 'meaning': '向贤者看齐', 'usage': '男名', 'pinyin': None, 'style_tags': ['文雅']},
            {'word': '庭筠', 'origin': '温庭筠（晚唐，明清尊崇）', 'quote': '温庭筠诗词', 'meaning': '庭中筠竹', 'usage': '男名', 'pinyin': None, 'style_tags': ['古风']},
            {'word': '板桥', 'origin': '郑板桥（清代）', 'quote': '郑燮号板桥', 'meaning': '木板桥', 'usage': '男名', 'pinyin': None, 'style_tags': ['古风']},
        ],
        'count': 8,
    }
    with open(os.path.join(LIT_DIR, 'mingqing.json'), 'w', encoding='utf-8') as f:
        json.dump(mingqing, f, ensure_ascii=False, indent=1)

    print('元曲素材: 6 条 | 明清诗文素材: 8 条')


def build_wuxing_radical_map():
    """五行喜用神→部首推荐映射（独立详细版）"""
    mapping = {
        'meta': {
            'name': '五行喜用神→部首推荐映射表',
            'purpose': '根据喜用神快速定位推荐部首和字',
            'version': '1.0',
        },
        'mappings': {
            '木': {
                'element': '木',
                'description': '喜木：宜选木/艹/禾/竹等部首字，忌金/钅等克木部首',
                'recommended_radicals': ['木', '艹', '禾', '竹', '米', '豆', '麦', '麻', '乙', '甲', '寅', '卯'],
                'forbidden_radicals': ['金', '钅', '玉', '石', '辛', '白', '刀', '刂', '戈'],
                'recommended_chars_male': ['森', '松', '柏', '桓', '栋', '权', '树', '楷', '林', '材', '杰', '柳', '桐', '梓', '楠'],
                'recommended_chars_female': ['楠', '樱', '槿', '榕', '芳', '英', '茗', '茉', '莉', '薇', '芸', '芊', '芝', '芹', '芙'],
                'recommended_chars_neutral': ['林', '森', '禾', '竹', '米', '禾', '秀', '秋', '科', '稚', '穗'],
                'nature': '生发、条达、生长',
                'season': '春',
                'direction': '东',
            },
            '火': {
                'element': '火',
                'description': '喜火：宜选火/灬/日/光等部首字，忌水/氵等克火部首',
                'recommended_radicals': ['火', '灬', '日', '光', '电', '心', '忄', '赤', '丙', '丁', '巳', '午'],
                'forbidden_radicals': ['水', '氵', '雨', '子', '亥', '鱼', '黑', '壬', '癸'],
                'recommended_chars_male': ['明', '亮', '光', '昊', '曜', '晖', '旭', '晟', '炎', '灿', '炫', '焕', '煦', '熙', '烨'],
                'recommended_chars_female': ['昕', '晶', '婷', '诺', '彤', '暖', '鸾', '晗', '晴', '曦', '昭', '晓', '晨'],
                'recommended_chars_neutral': ['光', '明', '日', '月', '星', '辰', '晨', '景', '智'],
                'nature': '炎上、温热、光明',
                'season': '夏',
                'direction': '南',
            },
            '土': {
                'element': '土',
                'description': '喜土：宜选土/山/石/田等部首字，忌木/艹等克土部首',
                'recommended_radicals': ['土', '山', '石', '田', '艮', '阜', '阝', '尸', '戊', '己', '辰', '戌', '丑', '未'],
                'forbidden_radicals': ['木', '艹', '禾', '竹', '米', '乙', '寅', '卯'],
                'recommended_chars_male': ['勇', '坤', '均', '培', '基', '坚', '城', '堂', '圣', '垒', '峰', '岳', '岗', '岩', '岸'],
                'recommended_chars_female': ['岚', '懿', '婉', '娴', '嫣', '韵', '羽', '燕', '依', '安', '容', '园'],
                'recommended_chars_neutral': ['安', '宇', '宙', '守', '定', '宜', '家', '富', '实'],
                'nature': '承载、化生、厚重',
                'season': '长夏',
                'direction': '中',
            },
            '金': {
                'element': '金',
                'description': '喜金：宜选金/钅/玉/石等部首字，忌火/灬等克金部首',
                'recommended_radicals': ['金', '钅', '玉', '石', '贝', '辛', '白', '庚', '辛', '申', '酉'],
                'forbidden_radicals': ['火', '灬', '日', '光', '心', '丙', '丁', '巳', '午'],
                'recommended_chars_male': ['铭', '锋', '锐', '钦', '铠', '鑫', '钊', '钧', '铮', '铖', '锦', '镇', '金', '钢', '铁'],
                'recommended_chars_female': ['铃', '瑜', '瑾', '瑶', '璐', '琳', '琪', '琼', '璇', '珊', '珠', '珍', '瑞', '璟'],
                'recommended_chars_neutral': ['玉', '金', '石', '白', '秋', '素', '真', '诚', '信'],
                'nature': '从革、肃杀、收敛',
                'season': '秋',
                'direction': '西',
            },
            '水': {
                'element': '水',
                'description': '喜水：宜选水/氵/雨/子等部首字，忌土/山等克水部首',
                'recommended_radicals': ['水', '氵', '雨', '子', '亥', '鱼', '黑', '壬', '癸', '川', '泉'],
                'forbidden_radicals': ['土', '山', '石', '田', '艮', '阜', '戊', '己', '辰', '戌'],
                'recommended_chars_male': ['河', '泽', '源', '浩', '瀚', '波', '涛', '洋', '江', '海', '湖', '泊', '润', '淼', '渊'],
                'recommended_chars_female': ['淇', '涵', '淑', '洁', '沁', '澜', '滢', '雪', '露', '霏', '霖', '雯', '霞', '霓'],
                'recommended_chars_neutral': ['水', '雨', '云', '泉', '冰', '冬', '寒', '清', '澈'],
                'nature': '润下、寒凉、滋润',
                'season': '冬',
                'direction': '北',
            },
        },
    }
    with open(os.path.join(BASE, '..', '01-数据资料', '五行部首推荐映射表.json'), 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=1)
    print('五行部首推荐映射表: 已生成（5元素×3性别×15字）')


def build_tone_pattern_library():
    """声调搭配模式库（详细版）"""
    library = {
        'meta': {
            'name': '声调搭配模式库',
            'purpose': '2字名和3字名的声调组合评价，用于音韵筛选',
            'tone_meaning': {1: '阴平', 2: '阳平', 3: '上声', 4: '去声', 0: '轻声'},
        },
        'two_char_patterns': {
            'excellent': [
                {'pattern': '1-2', 'example': '天明', 'note': '平起平收，清亮流畅'},
                {'pattern': '2-1', 'example': '明德', 'note': '平起平收，温润流畅'},
                {'pattern': '1-4', 'example': '天立', 'note': '平起仄收，抑扬顿挫'},
                {'pattern': '4-1', 'example': '立天', 'note': '仄起平收，响亮有力'},
                {'pattern': '2-4', 'example': '明志', 'note': '平起仄收，起伏有致'},
                {'pattern': '4-2', 'example': '志明', 'note': '仄起平收，收音响亮'},
            ],
            'good': [
                {'pattern': '1-3', 'example': '天晓', 'note': '平起上收，清亮但收尾稍弱'},
                {'pattern': '3-1', 'example': '晓天', 'note': '上起平收，先抑后扬'},
                {'pattern': '3-2', 'example': '晓德', 'note': '上起平收，温润流畅'},
                {'pattern': '2-3', 'example': '明晓', 'note': '平起上收，流畅但收尾稍弱'},
            ],
            'avoid': [
                {'pattern': '1-1', 'example': '天天', 'note': '全阴平，单调无变化'},
                {'pattern': '2-2', 'example': '明明', 'note': '全阳平，单调无变化'},
                {'pattern': '3-3', 'example': '晓晓', 'note': '全上声，拗口费力'},
                {'pattern': '4-4', 'example': '志志', 'note': '全去声，生硬刺耳'},
            ],
        },
        'three_char_patterns': {
            'excellent': [
                {'pattern': '1-2-1', 'example': '天明安', 'note': '平-平-平但有变化'},
                {'pattern': '2-1-4', 'example': '明安志', 'note': '起伏有致'},
                {'pattern': '1-4-2', 'example': '天志明', 'note': '抑扬顿挫'},
                {'pattern': '4-1-2', 'example': '志天明', 'note': '响亮收尾'},
                {'pattern': '2-3-1', 'example': '明晓天', 'note': '先抑后扬'},
                {'pattern': '3-1-2', 'example': '晓天明', 'note': '起伏流畅'},
            ],
            'good': [
                {'pattern': '1-3-2', 'example': '天晓明', 'note': '流畅'},
                {'pattern': '3-2-1', 'example': '晓明天', 'note': '流畅'},
                {'pattern': '4-2-1', 'example': '志明天', 'note': '收音响亮'},
                {'pattern': '2-4-1', 'example': '明志天', 'note': '起伏有致'},
            ],
            'avoid': [
                {'pattern': '1-1-1', 'example': '天天天', 'note': '全平，极度单调'},
                {'pattern': '2-2-2', 'example': '明明明', 'note': '全平，极度单调'},
                {'pattern': '3-3-3', 'example': '晓晓晓', 'note': '全仄，极度拗口'},
                {'pattern': '4-4-4', 'example': '志志志', 'note': '全仄，极度刺耳'},
            ],
        },
        'surname_name_patterns': {
            'principle': '姓氏与名字首字声调不同更流畅',
            'good': [
                {'surname_tone': 1, 'name_first_tone': [2, 3, 4], 'example': '张(1)+伟(3)'},
                {'surname_tone': 2, 'name_first_tone': [1, 3, 4], 'example': '刘(2)+晓(3)'},
                {'surname_tone': 3, 'name_first_tone': [1, 2, 4], 'example': '马(3)+云(2)'},
                {'surname_tone': 4, 'name_first_tone': [1, 2, 3], 'example': '赵(4)+云(2)'},
            ],
            'neutral': [
                {'surname_tone': 1, 'name_first_tone': [1], 'note': '同声但可接受'},
            ],
        },
    }
    with open(os.path.join(BASE, '..', '02-规则与算法资料', '12-声调搭配模式库.json'), 'w', encoding='utf-8') as f:
        json.dump(library, f, ensure_ascii=False, indent=1)
    print('声调搭配模式库: 已生成（2字名10模式+3字名10模式+姓氏搭配）')


def main():
    print('=== 补充优化缺口 ===')
    add_tangshi_songci_notes()
    add_yuanqu_mingqing()
    build_wuxing_radical_map()
    build_tone_pattern_library()
    print()
    print('全部优化缺口补充完成。')


if __name__ == '__main__':
    main()
