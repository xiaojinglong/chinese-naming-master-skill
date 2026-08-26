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

# Add _tools to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bazi_engine import get_bazi, get_recommended_radicals, get_forbidden_radicals, GAN_WUXING, TIANGAN, DIZHI
from scoring_engine import score_name, load_data, get_grade

BASE = os.path.dirname(os.path.abspath(__file__))

# 模块级缓存
_cached_hanzi_db = None
_cached_hanzi_db_type = None
_cached_surnames = None
_cached_literature_map = None


def load_hanzi_db(db_type='expanded'):
    """加载字库（带缓存）

    参数：
      db_type: 'common' (308个常用字) / 'expanded' (默认，6299个扩充字库) / 'full' (18821个全量字)

    返回：
      dict: {字: 字信息} 映射
    """
    global _cached_hanzi_db, _cached_hanzi_db_type

    # 如果请求的类型与缓存不同，清除缓存
    if _cached_hanzi_db is not None and _cached_hanzi_db_type == db_type:
        return _cached_hanzi_db

    if db_type == 'full':
        filename = 'hanzi_full.json'
    elif db_type == 'expanded':
        filename = 'hanzi_common_expanded.json'
    else:
        filename = 'hanzi_common.json'

    filepath = os.path.join(BASE, '..', '01-数据资料', '汉字字库', filename)
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)

    _cached_hanzi_db = {c['char']: c for c in data['chars']}
    _cached_hanzi_db_type = db_type
    return _cached_hanzi_db


def load_surnames():
    """加载姓氏库（单姓+复姓，带缓存）"""
    global _cached_surnames
    if _cached_surnames is not None:
        return _cached_surnames
    # 单姓
    with open(os.path.join(BASE, '..', '01-数据资料', '姓氏库', 'single_surnames.json'), encoding='utf-8') as f:
        data = json.load(f)
    result = {s['surname']: s for s in data.get('surnames', data.get('list', []))}
    # 复姓
    compound_path = os.path.join(BASE, '..', '01-数据资料', '姓氏库', 'compound_surnames.json')
    if os.path.exists(compound_path):
        with open(compound_path, encoding='utf-8') as f:
            comp_data = json.load(f)
        for s in comp_data.get('surnames', []):
            result[s['surname']] = s
    _cached_surnames = result
    return result


def load_xiyongshen_map():
    """加载喜用神推荐映射表"""
    path = os.path.join(BASE, '..', '01-数据资料', '喜用神推荐映射表.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return None


def load_literature_map():
    """加载文学引用库（诗词意象+成语典故），返回 {名称: 出处} 映射（带缓存）"""
    global _cached_literature_map
    if _cached_literature_map is not None:
        return _cached_literature_map

    literature = {}
    # 诗词意象库
    shici_path = os.path.join(BASE, '..', '03-文化资料', '诗词意象库.json')
    if os.path.exists(shici_path):
        with open(shici_path, encoding='utf-8') as f:
            shici = json.load(f)
        for item in shici.get('items', []):
            imagery = item.get('imagery', '')
            ref = item.get('poem_ref', '')
            if imagery and ref:
                literature[imagery] = ref
    # 成语典故库
    chengyu_path = os.path.join(BASE, '..', '03-文化资料', '成语典故库.json')
    if os.path.exists(chengyu_path):
        with open(chengyu_path, encoding='utf-8') as f:
            chengyu = json.load(f)
        for item in chengyu.get('items', []):
            for word in item.get('usable_words', []):
                ref = item.get('source', '')
                if word and ref:
                    literature[word] = ref
    _cached_literature_map = literature
    return literature


def calc_wuge(surname, name, hanzi_map, surname_map):
    """
    计算五格数字和三才五行。

    五格公式（以康熙笔画为准）：
    - 天格 = 姓笔画 + 1（单姓）或 姓两字笔画和 + 1（复姓）
    - 人格 = 姓笔画 + 名首字笔画（单姓）或 姓总笔画 + 名首字笔画（复姓）
    - 地格 = 名两字笔画和（双字名）或 名笔画 + 1（单字名）
    - 外格 = 名末字笔画 + 1（双字名）或 固定2（单字名）
    - 总格 = 姓名全部笔画和

    三才 = 天格五行 / 人格五行 / 地格五行（由尾数定五行）
    """
    s_info = surname_map.get(surname, {})
    # 判断是否为复姓
    is_compound = len(surname) > 1

    # 姓氏笔画
    if is_compound and 'strokes_kangxi_each' in s_info:
        # 复姓：使用 each 数组或 total
        s_strokes_each = s_info['strokes_kangxi_each']
        s_strokes = s_info.get('strokes_kangxi_total', sum(s_strokes_each))
    elif 'strokes_kangxi' in s_info:
        s_strokes = s_info.get('strokes_kangxi', 0) or 0
    else:
        # 尝试从字库查
        s_strokes = 0
        for ch in surname:
            c = hanzi_map.get(ch, {})
            s_strokes += c.get('strokes_kangxi', 0) or 0

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
    - 性别专用字优先（gender_hint=male/female 优先于 neutral）
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
        g = info.get('gender_hint', 'neutral')
        if gender:
            if gender == 'male' and g == 'female':
                continue  # 男名不用女性字
            if gender == 'female' and g == 'male':
                continue  # 女名不用男性字

        # 添加性别优先级标记（用于后续排序）
        info['_gender_priority'] = 2 if (gender and g == gender) else (1 if g != 'neutral' else 0)

        candidates.append(info)

    return candidates


def generate_names(surname, gender=None, birth_year=None, birth_month=None,
                   birth_day=None, birth_hour=12, name_length=2, style=None,
                   top_n=10, weight_preset='default', db_type='expanded'):
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
      db_type: 字库类型（'common'=308常用字，'expanded'=默认6299扩充字库，'full'=18821全量字）

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
    hanzi_map = load_hanzi_db(db_type)
    surname_map = load_surnames()
    scoring_data = load_data()
    xiyongshen_map = load_xiyongshen_map()
    literature_map = load_literature_map()

    # 3. 筛选候选字
    candidates = filter_chars(
        hanzi_map, gender=gender,
        xiyongshen=xiyongshen, jiyongshen=jiyongshen,
        zodiac=zodiac
    )

    # 按优先级排序：喜用神匹配 > 性别专用字 > 其他
    def priority_key(c):
        # 五行优先级
        wx = c.get('wuxing', '')
        if xiyongshen:
            wx_score = 0 if wx == xiyongshen else (2 if wx == jiyongshen else 1)
        else:
            wx_score = 1

        # 性别优先级（gender_priority在filter_chars中已设置）
        gender_score = c.get('_gender_priority', 0)

        # 综合排序：五行优先，性别次之
        return (wx_score, -gender_score)

    candidates.sort(key=priority_key)

    # style 过滤：根据风格偏好筛选候选字
    if style:
        style_filtered = []
        # 风格映射（对齐 hanzi_common.json 中的实际 style_tags）
        style_map = {
            '大气': ['大气', '阳刚', '进取', '庄重', '高远', '光明'],
            '文雅': ['文雅', '婉约', '柔美', '高洁', '谦和', '淡雅', '清冷'],
            '古风': ['文雅', '婉约', '高洁', '淡雅', '清冷', '古风'],
            '现代': ['现代', '好听', '朝气', '明亮', '清新'],
        }
        target_tags = style_map.get(style, [])
        if target_tags:
            for c in candidates:
                char_style_tags = c.get('style_tags', [])
                if any(t in target_tags for t in char_style_tags):
                    style_filtered.append(c)
            # 如果风格过滤后有足够候选字，使用过滤结果；否则保留全部
            if len(style_filtered) >= 10:
                candidates = style_filtered

    # 4. 生成候选名（使用多样性策略避免结果单一）
    names = []
    # 根据 top_n 动态调整候选字数量上限
    max_char_pool = max(80, top_n * 8)

    if name_length == 2:
        # 双字名：多样性组合策略
        top_chars = candidates[:max_char_pool]
        max_combos = top_n * 10  # 多生成再筛选

        # 策略：从候选池中均匀采样首字，每个首字配对多个尾字
        # 首字从不同位置采样以保证多样性
        seen_names = set()
        n_chars = len(top_chars)
        if n_chars == 0:
            pass
        else:
            # 确定首字采样步长：至少每3个字取1个首字，最多取30个首字
            n_first = min(30, max(10, n_chars // 3))
            step = max(1, n_chars // n_first)
            first_chars = [top_chars[i] for i in range(0, n_chars, step)][:n_first]

            # 每个首字配对的尾字数量
            n_second = max(5, max_combos // max(len(first_chars), 1))
            second_chars = top_chars[:min(n_second * 2, n_chars)]

            for c1 in first_chars:
                count_for_this = 0
                for c2 in second_chars:
                    if c1['char'] == c2['char']:
                        continue
                    name = c1['char'] + c2['char']
                    if name in seen_names:
                        continue
                    seen_names.add(name)
                    # 计算五格
                    wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)
                    names.append({
                        'name': name,
                        'chars': [c1, c2],
                        'wuge': wuge_info,
                    })
                    count_for_this += 1
                    if len(names) >= max_combos:
                        break
                    if count_for_this >= n_second:
                        break
                if len(names) >= max_combos:
                    break
    else:
        # 单字名
        for c in candidates[:max_char_pool]:
            name = c['char']
            wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)
            names.append({
                'name': name,
                'chars': [c],
                'wuge': wuge_info,
            })

    # 5. 评分排序（传入 literature_map 以启用文学出处加成）
    scored = []
    for n in names:
        result = score_name(
            n['name'], surname, scoring_data,
            xiyongshen=xiyongshen, jiyongshen=jiyongshen,
            zodiac=zodiac,
            wuge_numbers=n['wuge']['wuge_numbers'],
            sancai_wuxing=n['wuge']['sancai_wuxing'],
            weight_preset=weight_preset,
            literature_map=literature_map,
        )
        scored.append(result)

    # 按总分排序
    scored.sort(key=lambda x: x['total_score'], reverse=True)

    # 6. 黑名单过滤（过滤敏感名字）
    blacklist = scoring_data.get('homophone_blacklist', {})
    bad_words = blacklist.get('bad_words', set())
    negative_combos = blacklist.get('negative_combos', [])

    filtered = []
    for s in scored:
        full_name = s['full_name']
        name = s['name']

        # 检查是否命中负面组合（如秦桧、赵高等）
        skip = False
        for combo in negative_combos:
            if combo.get('action') == '淘汰':
                pattern = combo.get('pattern', '')
                # 简单匹配：检查名字是否包含负面组合的字
                example = combo.get('example', '')
                if example and full_name == example:
                    skip = True
                    break

        # 检查名字是否包含负面字词
        if not skip:
            for word in bad_words:
                if word in name or word in full_name:
                    skip = True
                    break

        if not skip:
            filtered.append(s)

    # 取前 top_n
    top_names = filtered[:top_n]

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


def generate_names_with_report(surname, gender=None, birth_year=None, birth_month=None,
                               birth_day=None, birth_hour=12, name_length=2, style=None,
                               top_n=10, weight_preset='default', output_path=None, db_type='common'):
    """
    取名全流程 + 生成HTML报告（便捷函数）

    参数：同 generate_names()
    output_path: HTML报告输出路径，默认为当前目录下的 naming_report.html
    db_type: 字库类型（'common'=308常用字，'full'=18821全量字）

    返回：
      dict: 同 generate_names()，额外包含 report_path 字段
    """
    # 确保至少10个候选名
    if top_n < 10:
        top_n = 10

    # 生成名字
    result = generate_names(
        surname=surname, gender=gender,
        birth_year=birth_year, birth_month=birth_month,
        birth_day=birth_day, birth_hour=birth_hour,
        name_length=name_length, style=style,
        top_n=top_n, weight_preset=weight_preset,
        db_type=db_type
    )

    # 生成HTML报告
    from report_generator import generate_html_report
    report_path = generate_html_report(result, output_path)
    result['report_path'] = report_path

    return result


if __name__ == '__main__':
    # 测试取名生成
    print('=== 取名生成引擎测试 ===')
    print()

    # 测试1：李姓男宝宝，2024年3月15日10点
    r1 = generate_names('李', gender='male', birth_year=2024, birth_month=3,
                        birth_day=15, birth_hour=10, name_length=2, top_n=10)
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
                        birth_day=20, birth_hour=14, name_length=2, top_n=10)
    print(f'输入: {r2["input"]}')
    if r2['bazi']:
        print(f'八字: {r2["bazi"]["year_ganzhi"]}年 {r2["bazi"]["month_ganzhi"]}月 {r2["bazi"]["day_ganzhi"]}日 {r2["bazi"]["hour_ganzhi"]}时')
        print(f'喜用神: {r2["xiyongshen"]} | 生肖: {r2["zodiac"]}')
    print(f'候选名 ({len(r2["candidates"])}):')
    for c in r2['candidates']:
        print(f'  {c["full_name"]:8s} 总分={c["total_score"]:5.1f} ({c["grade"]})')
