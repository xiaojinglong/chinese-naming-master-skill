# -*- coding: utf-8 -*-
"""
取名评分引擎
============
基于评分权重配置，对候选名字进行多维度加权评分。

评分维度（对应 06-评分权重配置.json）：
1. wuxing_match    五行补益匹配度（喜用神五行 vs 名字五行）
2. wuge_shuli      五格数理吉凶（1-81数吉凶表）
3. yinyun_fluency  音韵流畅度（声调搭配+谐音+声母韵母）
4. yiyi_depth      寓意深度（经典出处+字义美好度）
5. sancai_config   三才配置吉凶（天格/人格/地格五行组合）
6. zixing_beauty   字形美观度（笔画搭配+结构协调）
7. shengxiao_compat 生肖契合度（生肖喜忌偏旁匹配）

输出：每个维度的得分 + 加权总分 + 排序
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ==================== 等级分数映射表 ====================
# 统一处理所有可能出现的等级，避免回落到默认值
GRADE_SCORE_MAP = {
    '大吉': 100,
    '吉': 85,
    '中吉': 75,
    '半吉': 70,
    '吉多于凶': 60,   # 吉多于凶 > 平
    '平': 55,
    '吉凶参半': 50,    # 吉凶参半 < 平
    '凶多于吉': 40,    # 凶多于吉 > 凶
    '半凶': 35,        # 半凶 < 凶多于吉
    '凶多吉少': 25,    # 凶多吉少 > 凶
    '凶': 20,
    '大凶': 10,
}


def _load_json(rel_path):
    """安全加载 JSON 文件"""
    path = os.path.join(BASE, '..', rel_path)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _load_literature_data():
    """加载所有经典文学素材库数据"""
    literature = {}
    lit_dir = os.path.join(BASE, '..', '01-数据资料', '经典文学素材库')
    if os.path.exists(lit_dir):
        for fname in os.listdir(lit_dir):
            if fname.endswith('.json') and fname != 'wenxue_schema.json':
                filepath = os.path.join(lit_dir, fname)
                try:
                    with open(filepath, encoding='utf-8') as f:
                        data = json.load(f)
                    book_name = fname.replace('.json', '')
                    for item in data.get('items', []):
                        source = item.get('source', item.get('origin', ''))
                        meaning = item.get('meaning', '')

                        # 格式1：usable_words 列表
                        usable = item.get('usable_words', item.get('words', []))
                        if isinstance(usable, list):
                            for word in usable:
                                if word and word not in literature:
                                    literature[word] = {
                                        'source': source,
                                        'meaning': meaning,
                                        'book': book_name
                                    }

                        # 格式2：word 单字段（如 daxue.json, zhongyong.json 等）
                        word = item.get('word', '')
                        if word and word not in literature:
                            literature[word] = {
                                'source': source,
                                'meaning': meaning,
                                'book': book_name
                            }

                        # 格式3：imagery 字段（诗词意象库格式）
                        imagery = item.get('imagery', '')
                        if imagery and imagery not in literature:
                            literature[imagery] = {
                                'source': item.get('poem_ref', source),
                                'meaning': meaning,
                                'book': book_name
                            }
                except Exception:
                    continue

    # 加载成语典故库
    chengyu_path = os.path.join(BASE, '..', '03-文化资料', '成语典故库.json')
    if os.path.exists(chengyu_path):
        try:
            with open(chengyu_path, encoding='utf-8') as f:
                data = json.load(f)
            for item in data.get('items', []):
                for word in item.get('usable_words', []):
                    if word and word not in literature:
                        literature[word] = {
                            'source': item.get('source', ''),
                            'meaning': item.get('meaning', ''),
                            'idiom': item.get('idiom', ''),
                            'book': '成语典故库'
                        }
        except Exception:
            pass

    # 加载诗词意象库
    shici_path = os.path.join(BASE, '..', '03-文化资料', '诗词意象库.json')
    if os.path.exists(shici_path):
        try:
            with open(shici_path, encoding='utf-8') as f:
                data = json.load(f)
            for item in data.get('items', []):
                imagery = item.get('imagery', '')
                if imagery and imagery not in literature:
                    literature[imagery] = {
                        'source': item.get('poem_ref', ''),
                        'meaning': item.get('meaning', ''),
                        'book': '诗词意象库'
                    }
        except Exception:
            pass

    return literature


def _load_homophone_blacklist():
    """加载谐音黑名单"""
    blacklist_path = os.path.join(BASE, '..', '02-规则与算法资料', '04-谐音黑名单词库.json')
    if os.path.exists(blacklist_path):
        try:
            with open(blacklist_path, encoding='utf-8') as f:
                data = json.load(f)
            return {
                'bad_words': set(data.get('bad_words', [])),
                'ambiguous_words': set(data.get('ambiguous_words', [])),
                'negative_combos': data.get('negative_combos', []),
            }
        except Exception:
            pass
    return {'bad_words': set(), 'ambiguous_words': set(), 'negative_combos': []}


def _load_shengmu_yunmu():
    """加载声母韵母分类数据"""
    path = os.path.join(BASE, '..', '02-规则与算法资料', '04-声母韵母表.json')
    if os.path.exists(path):
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            # 构建声母->分类映射
            initial_map = {}
            for item in data.get('initials', []):
                initial = item.get('initial', '')
                group = item.get('group', '')
                typ = item.get('type', '')
                if initial:
                    initial_map[initial] = {'group': group, 'type': typ}

            # 构建韵母->分类映射
            final_map = {}
            for item in data.get('finals', []):
                final = item.get('final', '')
                category = item.get('category', '')
                mouth = item.get('mouth', '')
                if final:
                    final_map[final] = {'category': category, 'mouth': mouth}

            return {'initial_map': initial_map, 'final_map': final_map}
        except Exception:
            pass
    return {'initial_map': {}, 'final_map': {}}


# 模块级缓存
_cached_data = None


def load_data():
    """加载评分所需的所有数据文件（完整版，带缓存）"""
    global _cached_data
    if _cached_data is not None:
        return _cached_data

    data = {}
    data['weights'] = _load_json(os.path.join('02-规则与算法资料', '06-评分权重配置.json'))
    data['wuge'] = _load_json(os.path.join('01-数据资料', '三才五格配置表', 'wuge_1to81.json'))
    data['sancai'] = _load_json(os.path.join('01-数据资料', '三才五格配置表', 'sancai_full.json'))
    data['common'] = _load_json(os.path.join('01-数据资料', '汉字字库', 'hanzi_common.json'))
    data['shengxiao'] = _load_json(os.path.join('02-规则与算法资料', '03-生肖喜忌偏旁表.json'))
    data['hanzi_map'] = {c['char']: c for c in data['common']['chars']}

    # 自动加载经典文学素材库（1247条）
    data['literature'] = _load_literature_data()

    # 加载谐音黑名单
    data['homophone_blacklist'] = _load_homophone_blacklist()

    # 加载声母韵母分类
    data['shengmu_yunmu'] = _load_shengmu_yunmu()

    _cached_data = data
    return data


def get_wuxing_score(name_chars, xiyongshen, jiyongshen, hanzi_map):
    """
    五行补益匹配度评分 (0-100)
    - 每个字的五行与喜用神匹配：+25分
    - 与忌用神匹配：-15分
    - 不匹配：+5分（中性）
    """
    if not xiyongshen:
        return 60  # 无喜用神信息，默认中等分

    score = 0
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if not c:
            score += 5
            continue
        wx = c.get('wuxing')
        if wx == xiyongshen:
            score += 25
        elif wx == jiyongshen:
            score -= 15
        else:
            score += 5

    # 归一化到 0-100
    max_score = len(name_chars) * 25
    min_score = len(name_chars) * (-15)
    if max_score == min_score:
        return 50
    normalized = max(0, min(100, ((score - min_score) / (max_score - min_score)) * 100))
    return round(normalized)


def get_wuge_score(wuge_numbers, wuge_data):
    """
    五格数理吉凶评分 (0-100)
    使用统一的 GRADE_SCORE_MAP 映射，覆盖所有可能的等级
    """
    wuge_map = {n['number']: n for n in wuge_data.get('numbers', [])}
    scores = []
    for num in wuge_numbers:
        if num is None:
            continue
        info = wuge_map.get(num, {})
        grade = info.get('grade', '平')
        scores.append(GRADE_SCORE_MAP.get(grade, 55))
    return round(sum(scores) / len(scores)) if scores else 55


def get_sancai_score(sancai_wuxing, sancai_data):
    """
    三才配置吉凶评分 (0-100)
    使用统一的 GRADE_SCORE_MAP 映射，覆盖所有可能的等级
    """
    if not sancai_wuxing or len(sancai_wuxing) < 3:
        return 55

    key = sancai_wuxing[0] + sancai_wuxing[1] + sancai_wuxing[2]
    sancai_list = sancai_data.get('sancai', sancai_data.get('items', []))
    config = None
    for item in sancai_list:
        if item.get('combination') == key:
            config = item
            break
    if not config:
        return 55
    grade = config.get('grade', '平')
    return GRADE_SCORE_MAP.get(grade, 55)


def get_yinyun_score(name_chars, surname_tone, hanzi_map, shengmu_yunmu=None):
    """
    音韵流畅度评分 (0-100)
    维度1：声调搭配（40%）- 相邻字声调变化
    维度2：尾字收音（20%）- 末尾字声调是否响亮
    维度3：声母交替（20%）- 发音部位是否交替
    维度4：韵母搭配（20%）- 开口度变化
    """
    if not name_chars:
        return 50

    tones = []
    initials = []
    finals = []
    initial_groups = []

    # 提取声母韵母信息
    initial_map = shengmu_yunmu.get('initial_map', {}) if shengmu_yunmu else {}
    final_map = shengmu_yunmu.get('final_map', {}) if shengmu_yunmu else {}

    for ch in name_chars:
        c = hanzi_map.get(ch)
        if c:
            tones.append(c.get('tone', 0))
            pinyin = c.get('pinyin_tone', '')
            if pinyin:
                # 提取声母（拼音第一个字符，或前两个字符如 zh/ch/sh）
                py = pinyin.lower()
                init = ''
                for length in [2, 1]:
                    candidate = py[:length]
                    if candidate in initial_map:
                        init = candidate
                        break
                if not init and py:
                    init = py[0]

                initials.append(init)
                initial_groups.append(initial_map.get(init, {}).get('group', ''))

                # 提取韵母（声母之后的部分）
                final = py[len(init):] if init else py
                finals.append(final)
            else:
                initials.append('')
                initial_groups.append('')
                finals.append('')
        else:
            tones.append(0)
            initials.append('')
            initial_groups.append('')
            finals.append('')

    score = 50

    # === 维度1：声调搭配（40%）===
    tone_score = 0
    for i in range(len(tones) - 1):
        if tones[i] != tones[i + 1]:
            tone_score += 10
        else:
            tone_score -= 5

    # 与姓氏声调搭配
    if surname_tone and tones:
        if surname_tone != tones[0]:
            tone_score += 5

    # 全平或全仄检查
    if tones:
        ping = all(t in (1, 2) for t in tones)
        ze = all(t in (3, 4) for t in tones)
        if ping or ze:
            tone_score -= 10

    score += tone_score

    # === 维度2：尾字收音（20%）===
    if tones:
        last_tone = tones[-1]
        if last_tone in (1, 2):
            score += 10  # 平声收尾响亮
        elif last_tone == 4:
            score += 5   # 去声收尾有力
        elif last_tone == 3:
            score -= 5   # 上声收尾较弱

    # === 维度3：声母交替（20%）===
    for i in range(len(initial_groups) - 1):
        g1 = initial_groups[i]
        g2 = initial_groups[i + 1]
        if g1 and g2:
            if g1 != g2:
                score += 5   # 发音部位不同，抑扬顿挫
            else:
                score -= 3   # 发音部位相同，略显单调

    # 声母完全相同（叠声）
    for i in range(len(initials) - 1):
        if initials[i] and initials[i] == initials[i + 1]:
            score -= 5

    # === 维度4：韵母搭配（20%）===
    for i in range(len(finals) - 1):
        f1 = finals[i]
        f2 = finals[i + 1]
        if f1 and f2:
            # 叠韵（韵母相同）
            if f1 == f2:
                score -= 3
            # 开口度变化（a/o/e 等大开口音与 i/u/ü 等小开口音交替）
            big_open = {'a', 'o', 'e', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng'}
            small_open = {'i', 'u', 'ü', 'ia', 'ie', 'iu', 'in', 'ing', 'uan', 'un'}
            is_big1 = any(f1.startswith(b) for b in big_open)
            is_big2 = any(f2.startswith(b) for b in big_open)
            if is_big1 != is_big2:
                score += 3  # 开口度变化，音韵丰富

    return max(0, min(100, score))


def get_yiyi_score(name_chars, hanzi_map, literature_map=None):
    """
    寓意深度评分 (0-100)
    维度1：字义美好度 - lucky=吉 +10，有kangxi_meaning +5，有meaning +5
    维度2：经典出处 - 完整名字匹配 +30，单字匹配 +15/字
    维度3：出处质量 - 出自经典名篇（诗经/楚辞/论语等）额外加分
    """
    score = 40  # 基础分

    # === 维度1：字义美好度 ===
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if not c:
            continue
        if c.get('lucky') == '吉':
            score += 10
        if c.get('kangxi_meaning'):
            score += 5
        if c.get('meaning'):
            score += 5

    # === 维度2：经典出处 ===
    if literature_map:
        name = ''.join(name_chars)
        # 完整名字匹配：最高加成
        if name in literature_map:
            ref = literature_map[name]
            score += 30
            # 经典名篇额外加分
            if isinstance(ref, dict):
                book = ref.get('book', '')
                if book in ('shijing', 'chuci', 'lunyu', 'zhouyi', 'daodejing'):
                    score += 5
        else:
            # 单字匹配：每个有出处的字 +15
            for ch in name_chars:
                if ch in literature_map:
                    ref = literature_map[ch]
                    score += 15
                    # 经典名篇额外加分
                    if isinstance(ref, dict):
                        book = ref.get('book', '')
                        if book in ('shijing', 'chuci', 'lunyu', 'zhouyi', 'daodejing'):
                            score += 3

    return max(0, min(100, score))


def get_zixing_score(name_chars, hanzi_map):
    """
    字形美观度评分 (0-100)
    - 笔画差异适中（不大起大落）：+10
    - 无生僻字/难写字：+10
    - 结构协调：+10
    - 常用字加分（有gender_hint/style_tags表示是常用取名字）：+5/字
    """
    score = 50
    strokes = []
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if c:
            strokes.append(c.get('strokes_kangxi', 0) or 0)
            if c.get('rare_flag'):
                score -= 10
            if c.get('difficult_flag'):
                score -= 5
            # 常用字加分（有gender_hint或style_tags表示是取名常用字）
            if c.get('gender_hint') or c.get('style_tags'):
                score += 5

    if len(strokes) >= 2:
        diff = max(strokes) - min(strokes)
        if diff <= 8:
            score += 10
        elif diff <= 15:
            score += 5
        else:
            score -= 5

    return max(0, min(100, score))


def get_shengxiao_score(name_chars, zodiac, shengxiao_data, hanzi_map):
    """
    生肖契合度评分 (0-100)
    - 名字含生肖喜用偏旁：+15/个
    - 含生肖忌用偏旁：-15/个
    """
    if not zodiac:
        return 55

    zodiacs = shengxiao_data.get('zodiacs', [])
    z_info = None
    for z in zodiacs:
        if z.get('zodiac') == zodiac:
            z_info = z
            break
    if not z_info:
        return 55

    like_radicals = set(z_info.get('like_radicals', []))
    dislike_radicals = set(z_info.get('dislike_radicals', []))

    score = 50
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if not c:
            continue
        radical = c.get('radical', '')
        if radical in like_radicals:
            score += 15
        elif radical in dislike_radicals:
            score -= 15

    return max(0, min(100, score))


def score_name(name, surname, data, xiyongshen=None, jiyongshen=None, zodiac=None,
               wuge_numbers=None, sancai_wuxing=None, weight_preset='default',
               literature_map=None):
    """
    对候选名字进行多维度加权评分。

    参数：
      name: 名字（不含姓氏，如 "明轩"）
      surname: 姓氏（如 "李"）
      data: load_data() 返回的数据字典
      xiyongshen: 喜用神五行（如 "木"）
      jiyongshen: 忌用神五行
      zodiac: 生肖（如 "龙"）
      wuge_numbers: 五格数字 [天格, 人格, 地格, 外格, 总格]
      sancai_wuxing: 三才五行 [天格五行, 人格五行, 地格五行]
      weight_preset: 权重预设（default/八字优先/文雅古风/现代好听/传统稳健）
      literature_map: 文学引用映射 {名称: 出处}，用于寓意深度评分（可选，默认使用 data 中的 literature）

    返回：
      dict: 各维度得分 + 加权总分 + 排名建议
    """
    # 获取权重：优先用预设，否则用默认
    if weight_preset != 'default' and 'presets' in data['weights']:
        weights = data['weights']['presets'].get(weight_preset, data['weights'].get('default', {}))
    else:
        weights = data['weights'].get('default', {})
    hanzi_map = data['hanzi_map']
    name_chars = list(name)

    # 姓氏声调
    surname_char = hanzi_map.get(surname, {})
    surname_tone = surname_char.get('tone', 0) if surname_char else 0

    # 使用传入的 literature_map，或使用 data 中自动加载的 literature
    lit_map = literature_map if literature_map is not None else data.get('literature', {})

    # 各维度评分
    scores = {
        'wuxing_match': get_wuxing_score(name_chars, xiyongshen, jiyongshen, hanzi_map),
        'wuge_shuli': get_wuge_score(wuge_numbers or [], data['wuge']),
        'yinyun_fluency': get_yinyun_score(name_chars, surname_tone, hanzi_map, data.get('shengmu_yunmu')),
        'yiyi_depth': get_yiyi_score(name_chars, hanzi_map, lit_map),
        'sancai_config': get_sancai_score(sancai_wuxing or [], data['sancai']),
        'zixing_beauty': get_zixing_score(name_chars, hanzi_map),
        'shengxiao_compat': get_shengxiao_score(name_chars, zodiac, data['shengxiao'], hanzi_map),
    }

    # 加权总分
    total = 0
    total_weight = 0
    for dim, weight in weights.items():
        if dim in scores:
            total += scores[dim] * weight
            total_weight += weight
    if total_weight > 0:
        total = total / total_weight

    return {
        'name': name,
        'surname': surname,
        'full_name': surname + name,
        'scores': scores,
        'weights': weights,
        'total_score': round(total, 1),
        'grade': get_grade(total),
    }


def get_grade(score):
    """评分等级"""
    if score >= 90: return 'S（极佳）'
    if score >= 80: return 'A（优秀）'
    if score >= 70: return 'B（良好）'
    if score >= 60: return 'C（合格）'
    if score >= 50: return 'D（一般）'
    return 'F（不推荐）'


if __name__ == '__main__':
    # 测试评分引擎
    print('=== 评分引擎测试 ===')
    data = load_data()

    # 测试1：李明轩（假设喜木，生肖龙）
    r1 = score_name('明轩', '李', data, xiyongshen='木', zodiac='龙',
                    wuge_numbers=[8, 15, 13, 5, 21], sancai_wuxing=['金', '土', '木'])
    print(f'李明轩: 总分={r1["total_score"]} ({r1["grade"]})')
    for dim, s in r1['scores'].items():
        print(f'  {dim}: {s}')
    print()

    # 测试2：张雨涵（假设喜水，生肖蛇）
    r2 = score_name('雨涵', '张', data, xiyongshen='水', zodiac='蛇',
                    wuge_numbers=[12, 19, 20, 13, 24], sancai_wuxing=['木', '水', '水'])
    print(f'张雨涵: 总分={r2["total_score"]} ({r2["grade"]})')
    for dim, s in r2['scores'].items():
        print(f'  {dim}: {s}')
    print()

    # 测试3：不同权重预设
    for preset in ['default', '八字优先', '文雅古风', '现代好听']:
        r = score_name('清扬', '王', data, xiyongshen='水', weight_preset=preset)
        print(f'王清扬 ({preset}): {r["total_score"]} ({r["grade"]})')
