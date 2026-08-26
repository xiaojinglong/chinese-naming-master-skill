# -*- coding: utf-8 -*-
"""
取名生成引擎
============
取名全流程：用户输入 → 八字排盘 → 喜用神 → 候选字筛选 → 候选名生成 → 五格计算 → 评分排序 → 输出

用法：
  from bazi_engine import get_bazi
  from scoring_engine import score_name, load_data
  from name_generator import generate_names

  result = generate_names(
      surname='李', gender='male',
      birth_year=2024, birth_month=3, birth_day=15, birth_hour=10,
      name_length=2, style='大气', top_n=10
  )
"""
import json
import os
import sys
from itertools import combinations

# Add _tools to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bazi_engine import get_bazi, get_recommended_radicals, get_forbidden_radicals, GAN_WUXING, TIANGAN, DIZHI
from scoring_engine import score_name, load_data, get_grade

BASE = os.path.dirname(os.path.abspath(__file__))


def load_hanzi_db():
    """加载字库"""
    data = json.load(open(os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json'), encoding='utf-8'))
    return {c['char']: c for c in data['chars']}


def load_surnames():
    """加载姓氏库"""
    data = json.load(open(os.path.join(BASE, '..', '01-数据资料', '姓氏库', 'single_surnames.json'), encoding='utf-8'))
    return {s['surname']: s for s in data.get('surnames', data.get('list', []))}


def load_xiyongshen_map():
    """加载喜用神推荐映射表"""
    path = os.path.join(BASE, '..', '01-数据资料', '喜用神推荐映射表.json')
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    return None


def calc_wuge(surname, name, hanzi_map, surname_map):
    """
    计算五格数字和三才五行。

    五格公式（以康熙笔画为准）：
    - 天格 = 姓笔画 + 1（单姓）或 姓两字笔画和 + 1（复姓）
    - 人格 = 姓笔画 + 名首字笔画
    - 地格 = 名两字笔画和（双字名）或 名笔画 + 1（单字名）
    - 外格 = 名末字笔画 + 1（双字名）或 固定2（单字名）
    - 总格 = 姓名全部笔画和

    三才 = 天格五行 / 人格五行 / 地格五行（由尾数定五行）
    """
    # 姓氏笔画
    s_info = surname_map.get(surname, {})
    s_strokes = s_info.get('strokes_kangxi', 0) or 0
    if not s_strokes:
        # 尝试从字库查
        s_char = hanzi_map.get(surname, {})
        s_strokes = s_char.get('strokes_kangxi', 0) or 0

    # 名字笔画
    name_chars = list(name)
    name_strokes = []
    for ch in name_chars:
        c = hanzi_map.get(ch, {})
        ks = c.get('strokes_kangxi', 0) or 0
        name_strokes.append(ks)

    # 五格计算
    if len(name_chars) == 2:
        # 双字名
        tiange = s_strokes + 1
        renge = s_strokes + name_strokes[0]
        dige = name_strokes[0] + name_strokes[1]
        waige = name_strokes[1] + 1
        zongge = s_strokes + name_strokes[0] + name_strokes[1]
    else:
        # 单字名
        tiange = s_strokes + 1
        renge = s_strokes + name_strokes[0]
        dige = name_strokes[0] + 1
        waige = 2
        zongge = s_strokes + name_strokes[0]

    # 三才五行（由尾数定五行：1/2木, 3/4火, 5/6土, 7/8金, 9/0水）
    def num_to_wuxing(n):
        mod = n % 10
        if mod in (1, 2): return '木'
        if mod in (3, 4): return '火'
        if mod in (5, 6): return '土'
        if mod in (7, 8): return '金'
        return '水'  # 9, 0

    sancai = [num_to_wuxing(tiange), num_to_wuxing(renge), num_to_wuxing(dige)]

    return {
        'wuge_numbers': [tiange, renge, dige, waige, zongge],
        'sancai_wuxing': sancai,
        'strokes': {'surname': s_strokes, 'name': name_strokes},
    }


def filter_chars(hanzi_map, gender=None, xiyongshen=None, jiyongshen=None,
                 zodiac=None, min_strokes=1, max_strokes=30,
                 exclude_rare=True, exclude_difficult=True):
    """
    从字库筛选候选字。

    硬过滤（不满足直接排除）：
    - 生僻字（exclude_rare）
    - 难写字（exclude_difficult）
    - 忌用神五行
    - 生肖忌用偏旁

    软过滤（优先选择）：
    - 喜用神五行匹配
    - 性别匹配
    - 生肖喜用偏旁
    """
    candidates = []
    for ch, info in hanzi_map.items():
        # 硬过滤
        if exclude_rare and info.get('rare_flag'):
            continue
        if exclude_difficult and info.get('difficult_flag'):
            continue

        # 五行过滤
        wx = info.get('wuxing', '')
        if jiyongshen and wx == jiyongshen:
            continue  # 忌用神直接排除

        # 笔画范围
        strokes = info.get('strokes_kangxi', 0) or 0
        if strokes < min_strokes or strokes > max_strokes:
            continue

        # 生肖忌用偏旁
        if zodiac:
            radical = info.get('radical', '')
            # 需要生肖数据，这里简化：不排除（在评分时扣分）

        # 性别匹配（软过滤）
        if gender:
            g = info.get('gender_hint', 'neutral')
            if gender == 'male' and g == 'female':
                continue  # 男名不用女性字
            if gender == 'female' and g == 'male':
                continue  # 女名不用男性字

        candidates.append(info)

    return candidates


def generate_names(surname, gender=None, birth_year=None, birth_month=None,
                   birth_day=None, birth_hour=12, name_length=2, style=None,
                   top_n=10, weight_preset='default'):
    """
    取名全流程主函数。

    参数：
      surname: 姓氏
      gender: 性别（'male'/'female'/'neutral'）
      birth_year/month/day/hour: 出生日期时间（公历）
      name_length: 名字长度（1或2）
      style: 风格偏好（'大气'/'文雅'/'古风'/'现代'）
      top_n: 返回前N个候选名
      weight_preset: 评分权重预设

    返回：
      dict: 包含 bazi, candidates(评分排序后的候选名列表), summary
    """
    # 1. 八字排盘
    bazi = None
    xiyongshen = None
    jiyongshen = None
    zodiac = None
    if birth_year and birth_month and birth_day:
        bazi = get_bazi(birth_year, birth_month, birth_day, birth_hour)
        xiyongshen = bazi.xiyongshen
        jiyongshen = bazi.jiyongshen
        zodiac = bazi.zodiac

    # 2. 加载数据
    hanzi_map = load_hanzi_db()
    surname_map = load_surnames()
    scoring_data = load_data()
    xiyongshen_map = load_xiyongshen_map()

    # 3. 筛选候选字
    candidates = filter_chars(
        hanzi_map, gender=gender,
        xiyongshen=xiyongshen, jiyongshen=jiyongshen,
        zodiac=zodiac
    )

    # 按喜用神匹配度排序候选字
    if xiyongshen:
        def wx_priority(c):
            wx = c.get('wuxing', '')
            if wx == xiyongshen: return 0
            if wx == jiyongshen: return 2
            return 1
        candidates.sort(key=wx_priority)

    # 4. 生成候选名
    names = []
    if name_length == 2:
        # 双字名：从候选字中组合
        # 限制组合数量，避免爆炸（取前 50 个候选字）
        top_chars = candidates[:50]
        for c1 in top_chars:
            for c2 in top_chars:
                if c1['char'] == c2['char']:
                    continue
                name = c1['char'] + c2['char']
                # 计算五格
                wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)
                names.append({
                    'name': name,
                    'chars': [c1, c2],
                    'wuge': wuge_info,
                })
                if len(names) >= top_n * 5:  # 多生成一些再筛选
                    break
            if len(names) >= top_n * 5:
                break
    else:
        # 单字名
        for c in candidates[:top_n * 3]:
            name = c['char']
            wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)
            names.append({
                'name': name,
                'chars': [c],
                'wuge': wuge_info,
            })

    # 5. 评分排序
    scored = []
    for n in names:
        result = score_name(
            n['name'], surname, scoring_data,
            xiyongshen=xiyongshen, jiyongshen=jiyongshen,
            zodiac=zodiac,
            wuge_numbers=n['wuge']['wuge_numbers'],
            sancai_wuxing=n['wuge']['sancai_wuxing'],
            weight_preset=weight_preset,
        )
        scored.append(result)

    # 按总分排序
    scored.sort(key=lambda x: x['total_score'], reverse=True)

    # 取前 top_n
    top_names = scored[:top_n]

    # 6. 输出
    return {
        'input': {
            'surname': surname,
            'gender': gender,
            'birth': f'{birth_year}-{birth_month:02d}-{birth_day:02d} {birth_hour:02d}:00' if birth_year else None,
            'name_length': name_length,
            'style': style,
        },
        'bazi': bazi.to_dict() if bazi else None,
        'xiyongshen': xiyongshen,
        'jiyongshen': jiyongshen,
        'zodiac': zodiac,
        'candidates': top_names,
        'summary': {
            'total_candidates': len(names),
            'scored': len(scored),
            'top_n': top_n,
        }
    }


if __name__ == '__main__':
    # 测试取名生成
    print('=== 取名生成引擎测试 ===')
    print()

    # 测试1：李姓男宝宝，2024年3月15日10点
    r1 = generate_names('李', gender='male', birth_year=2024, birth_month=3,
                        birth_day=15, birth_hour=10, name_length=2, top_n=5)
    print(f'输入: {r1["input"]}')
    if r1['bazi']:
        print(f'八字: {r1["bazi"]["year_ganzhi"]}年 {r1["bazi"]["month_ganzhi"]}月 {r1["bazi"]["day_ganzhi"]}日 {r1["bazi"]["hour_ganzhi"]}时')
        print(f'喜用神: {r1["xiyongshen"]} | 生肖: {r1["zodiac"]}')
    print(f'候选名 ({len(r1["candidates"])}):')
    for c in r1['candidates']:
        print(f'  {c["full_name"]:8s} 总分={c["total_score"]:5.1f} ({c["grade"]})')
    print()

    # 测试2：王姓女宝宝，1990年5月20日14点
    r2 = generate_names('王', gender='female', birth_year=1990, birth_month=5,
                        birth_day=20, birth_hour=14, name_length=2, top_n=5)
    print(f'输入: {r2["input"]}')
    if r2['bazi']:
        print(f'八字: {r2["bazi"]["year_ganzhi"]}年 {r2["bazi"]["month_ganzhi"]}月 {r2["bazi"]["day_ganzhi"]}日 {r2["bazi"]["hour_ganzhi"]}时')
        print(f'喜用神: {r2["xiyongshen"]} | 生肖: {r2["zodiac"]}')
    print(f'候选名 ({len(r2["candidates"])}):')
    for c in r2['candidates']:
        print(f'  {c["full_name"]:8s} 总分={c["total_score"]:5.1f} ({c["grade"]})')
