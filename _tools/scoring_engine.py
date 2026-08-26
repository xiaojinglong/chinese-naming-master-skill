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


def load_data():
    """加载评分所需的所有数据文件"""
    data = {}
    data['weights'] = json.load(open(os.path.join(BASE, '..', '02-规则与算法资料', '06-评分权重配置.json'), encoding='utf-8'))
    data['wuge'] = json.load(open(os.path.join(BASE, '..', '01-数据资料', '三才五格配置表', 'wuge_1to81.json'), encoding='utf-8'))
    data['sancai'] = json.load(open(os.path.join(BASE, '..', '01-数据资料', '三才五格配置表', 'sancai_full.json'), encoding='utf-8'))
    data['common'] = json.load(open(os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json'), encoding='utf-8'))
    data['shengxiao'] = json.load(open(os.path.join(BASE, '..', '02-规则与算法资料', '03-生肖喜忌偏旁表.json'), encoding='utf-8'))
    data['hanzi_map'] = {c['char']: c for c in data['common']['chars']}
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
    - 大吉: 100, 吉: 85, 半吉: 70, 平: 55, 凶: 30, 大凶: 10
    """
    # wuge_data['numbers'] is a list of {number, grade, name, meaning}
    wuge_map = {n['number']: n for n in wuge_data.get('numbers', [])}
    score_map = {'大吉': 100, '吉': 85, '半吉': 70, '中吉': 70, '平': 55, '凶': 30, '大凶': 10}
    scores = []
    for num in wuge_numbers:
        if num is None:
            continue
        info = wuge_map.get(num, {})
        grade = info.get('grade', '平')
        scores.append(score_map.get(grade, 55))
    return round(sum(scores) / len(scores)) if scores else 55


def get_sancai_score(sancai_wuxing, sancai_data):
    """
    三才配置吉凶评分 (0-100)
    sancai_wuxing: [天格五行, 人格五行, 地格五行]
    sancai_data['sancai'] is a list of {tian, ren, di, combination, grade, explanation}
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
    score_map = {'大吉': 100, '吉': 85, '半吉': 70, '中吉': 70, '平': 55, '凶': 30, '大凶': 10}
    return score_map.get(grade, 55)


def get_yinyun_score(name_chars, surname_tone, hanzi_map):
    """
    音韵流畅度评分 (0-100)
    - 声调搭配：相邻字声调不同 +10，相同 -5
    - 末尾字为1/2声（收音响亮）：+10
    - 全平或全仄：-10
    - 声母相同：-5
    """
    if not name_chars:
        return 50

    tones = []
    initials = []
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if c:
            tones.append(c.get('tone', 0))
            pinyin = c.get('pinyin_tone', '')
            if pinyin:
                initials.append(pinyin[0] if pinyin else '')
            else:
                initials.append('')
        else:
            tones.append(0)
            initials.append('')

    score = 50

    # 声调搭配
    for i in range(len(tones) - 1):
        if tones[i] != tones[i + 1]:
            score += 10
        else:
            score -= 5

    # 末尾字声调
    if tones and tones[-1] in (1, 2):
        score += 10
    elif tones and tones[-1] in (3, 4):
        score -= 5

    # 全平或全仄
    ping = all(t in (1, 2) for t in tones)
    ze = all(t in (3, 4) for t in tones)
    if ping or ze:
        score -= 10

    # 声母检查
    for i in range(len(initials) - 1):
        if initials[i] and initials[i] == initials[i + 1]:
            score -= 5

    # 与姓氏声调搭配
    if surname_tone and tones:
        if surname_tone != tones[0]:
            score += 5

    return max(0, min(100, score))


def get_yiyi_score(name_chars, hanzi_map, literature_map=None):
    """
    寓意深度评分 (0-100)
    - 有经典出处：+30
    - 字义美好（lucky=吉）：+10/字
    - 有 kangxi_meaning（古籍释义）：+5/字
    """
    score = 40  # 基础分

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

    # 检查是否有文学出处
    if literature_map:
        name = ''.join(name_chars)
        if name in literature_map:
            score += 30

    return max(0, min(100, score))


def get_zixing_score(name_chars, hanzi_map):
    """
    字形美观度评分 (0-100)
    - 笔画差异适中（不大起大落）：+10
    - 无生僻字/难写字：+10
    - 结构协调：+10
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
               wuge_numbers=None, sancai_wuxing=None, weight_preset='default'):
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

    # 各维度评分
    scores = {
        'wuxing_match': get_wuxing_score(name_chars, xiyongshen, jiyongshen, hanzi_map),
        'wuge_shuli': get_wuge_score(wuge_numbers or [], data['wuge']),
        'yinyun_fluency': get_yinyun_score(name_chars, surname_tone, hanzi_map),
        'yiyi_depth': get_yiyi_score(name_chars, hanzi_map),
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
