# -*- coding: utf-8 -*-
"""
取名生成引擎 V3.0
================
取名全流程：用户输入 → 八字排盘 → 喜用神 → 候选字筛选 → 候选名生成 → 五格计算 → 评分排序 → 4类推荐 → 输出

V3.0 核心优化：
1. 词库优先生成：先从现代名字词库（688词）+ 经典文学词库中挑成词候选，
   不再纯靠"字池两两组合"随机拼字（根治"换冰""苗冰"式假名字）
2. 候选字池分层精选：组合补充只用 现代风格字 ∪ 常用308字 ∪ 有风格标签字，
   老气字/不宜字（换/屏/病/傻等）硬过滤
3. 多样性控制：top_n 结果中同一字出现次数设上限，避免"浩X浩X浩X"刷屏
4. 现代语感分参与排序（见 scoring_engine V3.0），五格不再主导

V2.0 保留能力：
- 三层漏斗筛选、姓氏-名字粘连度检测、俗气阈值过滤、4组推荐输出

用法：
  from bazi_engine import get_bazi
  from scoring_engine import score_name, load_data, get_grade
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
from scoring_engine import score_name, load_data, get_grade, categorize_names

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
                 exclude_rare=True, exclude_difficult=True,
                 era=None, exclude_awkward=True, exclude_dated=True):
    """
    从字库筛选候选字。

    硬过滤（不满足直接排除）：
    - 生僻字（exclude_rare）
    - 难写字（exclude_difficult）
    - 忌用神五行
    - 生肖忌用偏旁
    - V3.0 不宜入名字（exclude_awkward：换/屏/病/傻等语义差字）
    - V3.0 老气字（exclude_dated：福禄寿财旺/淑贞桂芳一代）

    软过滤（优先选择）：
    - 喜用神五行匹配
    - 性别匹配
    - 生肖喜用偏旁
    - 性别专用字优先（gender_hint=male/female 优先于 neutral）
    """
    awkward = era.get('awkward_chars', set()) if era else set()
    dated = era.get('dated_chars', set()) if era else set()

    candidates = []
    for ch, info in hanzi_map.items():
        # 硬过滤
        if exclude_rare and info.get('rare_flag'):
            continue
        if exclude_difficult and info.get('difficult_flag'):
            continue

        # V3.0 不宜入名字硬过滤
        if exclude_awkward and ch in awkward:
            continue
        # V3.0 老气字硬过滤
        if exclude_dated and ch in dated:
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


def check_surname_name_stickiness(surname, name, hanzi_map):
    """
    V2.0 姓氏-名字粘连度检测

    检查姓氏+名字连读是否有不良谐音或含义

    返回：
      bool: True=通过检测，False=有不良粘连
    """
    full_name = surname + name

    # 不良连读黑名单
    bad_combos = [
        '糊涂', '胡涂', '胡说', '胡闹', '胡扯', '胡搞',
        '范统', '饭桶', '史珍香', '赖月京', '杜子腾', '肚子疼',
        '秦寿', '禽兽', '朱逸之', '猪一只', '魏生津', '卫生巾',
        '沈京兵', '神经病', '杜琦燕', '肚脐眼', '矫厚根', '脚后跟',
        '朱逸群', '猪一群', '杜子腾', '肚子疼', '赖月京', '来月经',
        '史珍香', '屎真香', '范统', '饭桶', '秦寿生', '禽兽生',
        '初墨', '除魔', '熊初墨', '熊出没', '费彦', '肺炎',
        '韦君智', '伪君子', '沈京冰', '神经病', '朱逸朗', '猪一郎',
    ]

    for bad in bad_combos:
        if bad in full_name:
            return False

    # 检查姓氏+首字是否形成不良词
    if len(name) >= 1:
        first_two = surname + name[0]
        for bad in bad_combos:
            if bad in first_two:
                return False

    return True


def is_tacky_name(full_name, tacky_names):
    """
    V2.0 俗气名字检测

    检查是否是高频俗气名字

    返回：
      bool: True=是俗气名字，False=不是
    """
    return full_name in tacky_names


def _mmr_rank(candidates, top_n, lam=0.7):
    """
    V3.3 最大边际相关性排序 (Maximal Marginal Relevance)

    在保证质量的前提下，惩罚与已选名字字面高度相似（共享字）的候选，
    避免"沐泽/沐谦/沐辰/沐阳"这类同字扎堆。

    lam: 质量-多样性权衡系数（1.0=纯质量，0.0=纯多样性）。默认 0.7 偏质量。
    """
    if not candidates:
        return []
    sorted_c = sorted(candidates, key=lambda x: -x['total_score'])
    if len(sorted_c) <= top_n:
        return sorted_c
    selected = [sorted_c[0]]
    pool = sorted_c[1:]
    while len(selected) < top_n and pool:
        best_idx, best_score, best_c = -1, -1e18, None
        for i, c in enumerate(pool):
            cset = set(c['name'])
            max_sim = 0.0
            for s in selected:
                sset = set(s['name'])
                union = len(cset | sset)
                if union:
                    sim = len(cset & sset) / union
                    if sim > max_sim:
                        max_sim = sim
            mmr = lam * c['total_score'] - (1 - lam) * 100 * max_sim
            if mmr > best_score:
                best_score, best_idx, best_c = mmr, i, c
        selected.append(best_c)
        pool.pop(best_idx)
    return selected


def generate_names(surname, gender=None, birth_year=None, birth_month=None,
                   birth_day=None, birth_hour=12, name_length=2, style=None,
                   top_n=10, weight_preset='default', db_type='expanded',
                   fixed_last_char=None, diversity=True, diversity_lambda=0.7):
    """
    取名全流程主函数 V2.0

    参数：
      surname: 姓氏
      gender: 性别（'male'/'female'/'neutral'）
      birth_year/month/day/hour: 出生日期时间（公历）
      name_length: 名字长度（1或2）
      style: 风格偏好（'大气'/'文雅'/'古风'/'现代'）
      top_n: 返回前N个候选名
      weight_preset: 评分权重预设
      db_type: 字库类型（'common'=308常用字，'expanded'=默认6299扩充字库，'full'=18821全量字）
      fixed_last_char: 固定末字（如'骐'），则只生成首字+固定末字的组合

    返回：
      dict: 包含 bazi, candidates(评分排序后的候选名列表), categories(4类推荐), summary
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
    scoring_data = load_data(db_type)  # 传入db_type确保使用相同的字库
    xiyongshen_map = load_xiyongshen_map()
    literature_map = load_literature_map()

    # 获取俗气名字库
    tacky_names = scoring_data.get('tacky_names', set())

    # V3.0 时代感词库
    era = scoring_data.get('era', {})

    # 3. 筛选候选字（V3.0 硬过滤不宜字/老气字）
    candidates = filter_chars(
        hanzi_map, gender=gender,
        xiyongshen=xiyongshen, jiyongshen=jiyongshen,
        zodiac=zodiac, era=era
    )

    # 按优先级排序：喜用神匹配 > 风格标签 > 性别专用字 > 其他
    def priority_key(c):
        # 五行优先级
        wx = c.get('wuxing', '')
        if xiyongshen:
            wx_score = 0 if wx == xiyongshen else (2 if wx == jiyongshen else 1)
        else:
            wx_score = 1

        # 风格标签优先级（有style_tags的字更时尚、有文化内涵）
        style_score = 0 if c.get('style_tags') else 1

        # 性别优先级（gender_priority在filter_chars中已设置）
        gender_score = c.get('_gender_priority', 0)

        # 综合排序：五行优先，风格次之，性别最后
        return (wx_score, style_score, -gender_score)

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

    # ===== V3.0 词库优先生成 =====
    # 先从现代名字词库 + 经典文学词库中挑"成词"候选，
    # 避免"字池两两组合"随机拼出"换冰""苗冰"式假名字
    word_lib_names = set()

    if name_length == 2 and era and not fixed_last_char:
        by_gender = era.get('modern_words_by_gender', {})
        if gender == 'male':
            word_pool = by_gender.get('male', set()) | by_gender.get('neutral', set())
        elif gender == 'female':
            word_pool = by_gender.get('female', set()) | by_gender.get('neutral', set())
        else:
            word_pool = era.get('modern_words', set())
        # 文学词库整词也作为候选（诗经/楚辞等真实出处词）
        if literature_map:
            word_pool = word_pool | {w for w in literature_map.keys() if len(w) == 2}

        awkward_set = era.get('awkward_chars', set())
        dated_combo_set = era.get('dated_combos', set())
        word_candidates = []
        for word in word_pool:
            if len(word) != 2:
                continue
            c1 = hanzi_map.get(word[0])
            c2 = hanzi_map.get(word[1])
            if not c1 or not c2:
                continue
            # 康熙笔画缺失则无法算五格，跳过
            if not (c1.get('strokes_kangxi') or 0) or not (c2.get('strokes_kangxi') or 0):
                continue
            # 不宜字/老气组合不用
            if word[0] in awkward_set or word[1] in awkward_set:
                continue
            if word in dated_combo_set:
                continue
            # 五行：忌用神字不用
            wx1 = c1.get('wuxing', '')
            wx2 = c2.get('wuxing', '')
            if jiyongshen and (wx1 == jiyongshen or wx2 == jiyongshen):
                continue
            # 性别字冲突过滤
            if gender == 'male' and (c1.get('gender_hint') == 'female' or c2.get('gender_hint') == 'female'):
                continue
            if gender == 'female' and (c1.get('gender_hint') == 'male' or c2.get('gender_hint') == 'male'):
                continue
            # 姓氏粘连/俗气检测
            if not check_surname_name_stickiness(surname, word, hanzi_map):
                continue
            full_name = surname + word
            if is_tacky_name(full_name, tacky_names) or word in tacky_names:
                continue
            word_candidates.append({
                'name': word,
                'chars': [c1, c2],
                'wuge': calc_wuge(surname, word, hanzi_map, surname_map),
                '_xy_match': (1 if wx1 == xiyongshen else 0) + (1 if wx2 == xiyongshen else 0),
            })
        # 喜用神匹配数优先，取前若干个进入评分
        word_candidates.sort(key=lambda x: -x['_xy_match'])
        for wc in word_candidates[:max(top_n * 8, 60)]:
            wc.pop('_xy_match', None)
            names.append(wc)
            word_lib_names.add(wc['name'])

    # V3.0 组合池精选：现代风格字 ∪ 有风格标签字 ∪ 性别标注字（均为人工精挑字）
    # 避免 6299 字库里"换/屏/苗"等无审美标注的字进入组合池
    modern_chars = era.get('modern_chars', set()) if era else set()
    quality_candidates = [
        c for c in candidates
        if c['char'] in modern_chars or c.get('style_tags') or c.get('gender_hint', 'neutral') != 'neutral'
    ]
    if len(quality_candidates) < 20:
        quality_candidates = candidates  # 兜底：精选池太小时退回全池

    # 如果固定了末字，获取末字信息
    fixed_last_info = None
    if fixed_last_char and name_length == 2:
        fixed_last_info = hanzi_map.get(fixed_last_char)
        if not fixed_last_info:
            # 如果末字不在字库中，创建一个基本信息
            fixed_last_info = {'char': fixed_last_char, 'wuxing': '', 'strokes_kangxi': 0}

    if fixed_last_char and name_length == 2:
        # 固定末字模式：只生成 首字+固定末字 的组合
        top_chars = quality_candidates[:max_char_pool]
        max_combos = top_n * 2  # 多生成再筛选

        seen_names = set(word_lib_names)
        for c1 in top_chars:
            if c1['char'] == fixed_last_char:
                continue  # 跳过与末字相同的首字
            name = c1['char'] + fixed_last_char
            if name in seen_names:
                continue
            seen_names.add(name)

            # V2.0 姓氏粘连度检测
            if not check_surname_name_stickiness(surname, name, hanzi_map):
                continue

            # V2.0 俗气名字检测
            full_name = surname + name
            if is_tacky_name(full_name, tacky_names):
                continue

            # 计算五格
            wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)
            names.append({
                'name': name,
                'chars': [c1, fixed_last_info],
                'wuge': wuge_info,
            })
            if len(names) >= max_combos:
                break
    elif name_length == 2:
        # 双字名：多样性组合策略（V3.0 使用精选组合池）
        top_chars = quality_candidates[:max_char_pool]
        max_combos = top_n * 10  # 多生成再筛选

        # 策略：从候选池中均匀采样首字，每个首字配对多个尾字
        # 首字从不同位置采样以保证多样性
        seen_names = set(word_lib_names)
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

                    # V2.0 姓氏粘连度检测
                    if not check_surname_name_stickiness(surname, name, hanzi_map):
                        continue

                    # V2.0 俗气名字检测
                    full_name = surname + name
                    if is_tacky_name(full_name, tacky_names):
                        continue

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
        # 单字名（V3.0 使用精选组合池）
        for c in quality_candidates[:max_char_pool]:
            name = c['char']

            # V2.0 姓氏粘连度检测
            if not check_surname_name_stickiness(surname, name, hanzi_map):
                continue

            # V2.0 俗气名字检测
            full_name = surname + name
            if is_tacky_name(full_name, tacky_names):
                continue

            wuge_info = calc_wuge(surname, name, hanzi_map, surname_map)
            names.append({
                'name': name,
                'chars': [c],
                'wuge': wuge_info,
            })

    # 5. 评分排序（传入 literature_map 以启用文学出处加成，gender 用于现代语感性别匹配）
    scored = []
    surname_chars = list(surname)
    for n in names:
        result = score_name(
            n['name'], surname, scoring_data,
            xiyongshen=xiyongshen, jiyongshen=jiyongshen,
            zodiac=zodiac,
            wuge_numbers=n['wuge']['wuge_numbers'],
            sancai_wuxing=n['wuge']['sancai_wuxing'],
            weight_preset=weight_preset,
            literature_map=literature_map,
            surname_chars=surname_chars,
            gender=gender,
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
    # V3.3 多样性排序：MMR（最大边际相关性），平衡质量与字面重复度
    # 替代旧版"同字次数上限"——后者对"沐/辰"这类高频好字仍会扎堆
    if diversity:
        top_names = _mmr_rank(filtered, top_n, lam=diversity_lambda)
        selected_set = {s['name'] for s in top_names}
        overflow = [s for s in filtered if s['name'] not in selected_set]
    else:
        max_repeat = max(3, (top_n + 2) // 3)
        char_count = {}
        top_names = []
        overflow = []
        for s in filtered:
            chars_in_name = set(s['name'])
            if all(char_count.get(ch, 0) < max_repeat for ch in chars_in_name):
                top_names.append(s)
                for ch in chars_in_name:
                    char_count[ch] = char_count.get(ch, 0) + 1
            else:
                overflow.append(s)
            if len(top_names) >= top_n:
                break
    # 不足 top_n 时用溢出的候选补齐
    if len(top_names) < top_n:
        top_names.extend(overflow[:top_n - len(top_names)])

    # V2.0 生成4类推荐
    categories = categorize_names(filtered)

    # 7. 输出
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
        'categories': categories,
        'summary': {
            'total_candidates': len(names),
            'scored': len(scored),
            'filtered': len(filtered),
            'top_n': top_n,
        }
    }


def generate_names_with_report(surname, gender=None, birth_year=None, birth_month=None,
                               birth_day=None, birth_hour=12, name_length=2, style=None,
                               top_n=10, weight_preset='default', output_path=None, db_type='common',
                               fixed_last_char=None):
    """
    取名全流程 + 生成HTML报告（便捷函数）

    参数：同 generate_names()
    output_path: HTML报告输出路径，默认为当前目录下的 naming_report.html
    db_type: 字库类型（'common'=308常用字，'full'=18821全量字）
    fixed_last_char: 固定末字（如'骐'）

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
        db_type=db_type,
        fixed_last_char=fixed_last_char
    )

    # 生成HTML报告
    from report_generator import generate_html_report
    report_path = generate_html_report(result, output_path)
    result['report_path'] = report_path

    return result


if __name__ == '__main__':
    # 测试取名生成
    print('=== 取名生成引擎 V2.0 测试 ===')
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

    # V2.0 输出4类推荐
    print('=== 4类推荐 ===')
    for cat_name, cat_names in r1.get('categories', {}).items():
        print(f'\n【{cat_name}】({len(cat_names)}个):')
        for c in cat_names[:5]:  # 每类显示前5个
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
