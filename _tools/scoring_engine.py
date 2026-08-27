# -*- coding: utf-8 -*-
"""
取名评分引擎 V3.0
================
基于评分权重配置，对候选名字进行多维度加权评分。

核心优化（V3.0）：
1. 新增"现代语感"维度（权重25%）：成词性检查 + 时代感 + 用字审美
   - 命中现代名字词库（673词）：+35
   - 命中经典文学词库：+20
   - 现代风格用字：+8/字
   - 老气字（建国/志强/秀英一代）：-18/字
   - 随机拼字（双字不成词）：-12
2. 权重重调：五格 40%→18%（不再主导），现代语感 25%
3. 老气名乘法扣分：双老气字×0.6，命中老气组合（建国/桂芳等210组）×0.5
4. 不宜字（语义差/负面）：-35/字（配合生成层硬过滤）

V2.0 保留能力：
- 乘法扣分制：谐音×0.1，大凶×0.5
- 动态权重、声调平仄强化、字形结构协调、俗气阈值

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

# 项目根目录（_tools的父目录）
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==================== 等级分数映射表 ====================
# 严格按传统姓名学标准，不虚高
GRADE_SCORE_MAP = {
    '大吉': 95,
    '吉': 80,
    '中吉': 70,
    '半吉': 60,
    '吉多于凶': 50,
    '平': 45,
    '吉凶参半': 40,
    '凶多于吉': 30,
    '半凶': 25,
    '凶多吉少': 15,
    '凶': 10,
    '大凶': 5,
}

# ==================== 俗气名字黑名单 ====================
# 高频俗名，直接扣分
TACKY_NAMES = {
    '子涵', '梓涵', '紫涵', '浩宇', '浩然', '雨泽', '雨萱', '宇轩',
    '子轩', '梓轩', '欣怡', '心怡', '诗涵', '思涵', '可馨', '可欣',
    '子豪', '梓豪', '宇航', '博文', '子墨', '梓墨', '若曦', '若溪',
    '雨桐', '语桐', '一诺', '依诺', '奕辰', '亦辰', '子睿', '梓睿',
    '浩轩', '皓轩', '子恒', '梓恒', '宇辰', '雨辰', '语嫣', '语嫣',
    '梓萱', '紫萱', '子萱', '若萱', '诗琪', '诗琦', '思琪', '梦琪',
    '嘉琪', '佳琪', '雅琪', '雅琦', '雨欣', '语欣', '可欣', '可馨',
    '欣然', '心然', '诗雨', '思雨', '子涵', '梓涵', '紫涵', '子晗',
}

# ==================== 声调平仄最优模式 ====================
# 姓氏声调 → 名字最佳声调组合（平=1,2，仄=3,4）
BEST_TONE_PATTERNS = {
    # 单字名
    1: {1: [3, 4], 2: [3, 4], 3: [1, 2], 4: [1, 2]},  # 姓平→名仄，姓仄→名平
    # 双字名
    2: {
        1: [(3, 1), (3, 2), (4, 1), (4, 2), (1, 3), (1, 4)],  # 仄平平、平仄平
        2: [(3, 1), (3, 2), (4, 1), (4, 2), (1, 3), (1, 4)],
        3: [(1, 2), (1, 3), (2, 1), (2, 3), (1, 1)],  # 平平仄、平仄仄
        4: [(1, 2), (1, 3), (2, 1), (2, 3), (1, 1)],
    }
}


def _load_json(rel_path):
    """安全加载 JSON 文件"""
    path = os.path.join(BASE, rel_path)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _load_literature_data():
    """加载所有经典文学素材库数据"""
    literature = {}
    lit_dir = os.path.join(BASE, '01-数据资料', '经典文学素材库')
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
    chengyu_path = os.path.join(BASE, '03-文化资料', '成语典故库.json')
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
    shici_path = os.path.join(BASE, '03-文化资料', '诗词意象库.json')
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
    blacklist_path = os.path.join(BASE, '02-规则与算法资料', '04-谐音黑名单词库.json')
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
    path = os.path.join(BASE, '02-规则与算法资料', '04-声母韵母表.json')
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


def _load_tacky_names():
    """加载俗气名字库（从数据文件扩展）"""
    tacky = TACKY_NAMES.copy()
    # 可以从文件加载更多
    tacky_path = os.path.join(BASE, '02-规则与算法资料', '04-谐音黑名单词库.json')
    if os.path.exists(tacky_path):
        try:
            with open(tacky_path, encoding='utf-8') as f:
                data = json.load(f)
            # 添加高频名字到俗气库
            for item in data.get('tacky_names', []):
                tacky.add(item)
        except Exception:
            pass
    return tacky


# 模块级缓存
_cached_data = None


def _load_era_library():
    """V3.0 加载时代感与语感词库（13-时代感与语感词库.json）

    返回：
      dict: {
        'dated_chars': set,        # 老气字（建国/志强/秀英一代）
        'dated_combos': set,       # 老气组合（建国/桂芳等）
        'awkward_chars': set,      # 不宜入名字（语义差/负面）
        'modern_chars': set,       # 现代风格用字（男+女+中性合并）
        'modern_chars_male': set,
        'modern_chars_female': set,
        'modern_words': set,       # 现代名字词（整词）
        'modern_words_by_gender': {'male': set, 'female': set, 'neutral': set},
      }
    """
    path = os.path.join(BASE, '02-规则与算法资料', '13-时代感与语感词库.json')
    era = {
        'dated_chars': set(), 'dated_combos': set(), 'awkward_chars': set(),
        'modern_chars': set(), 'modern_chars_male': set(), 'modern_chars_female': set(),
        'modern_words': set(),
        'modern_words_by_gender': {'male': set(), 'female': set(), 'neutral': set()},
    }
    if not os.path.exists(path):
        return era
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        era['dated_chars'] = set(d.get('dated_chars', []))
        era['dated_combos'] = set(d.get('dated_combos', []))
        era['awkward_chars'] = set(d.get('awkward_chars', []))
        era['modern_chars_male'] = set(d.get('modern_chars_male', []))
        era['modern_chars_female'] = set(d.get('modern_chars_female', []))
        neutral = set(d.get('modern_chars_neutral', []))
        era['modern_chars'] = era['modern_chars_male'] | era['modern_chars_female'] | neutral
        for gender_key, lib_key in (('male', 'modern_words_male'),
                                    ('female', 'modern_words_female'),
                                    ('neutral', 'modern_words_neutral')):
            for item in d.get(lib_key, []):
                word = item.get('word', '') if isinstance(item, dict) else str(item)
                if word:
                    era['modern_words'].add(word)
                    era['modern_words_by_gender'][gender_key].add(word)
    except Exception:
        pass
    return era


def load_data(db_type='expanded'):
    """加载评分所需的所有数据文件（完整版，带缓存）

    参数：
      db_type: 字库类型（'common'=308常用字，'expanded'=默认6299扩充字库，'full'=18821全量字）

    返回：
      dict: 包含所有评分所需数据
    """
    global _cached_data
    if _cached_data is not None and _cached_data.get('_db_type') == db_type:
        return _cached_data

    data = {}
    data['weights'] = _load_json(os.path.join('02-规则与算法资料', '06-评分权重配置.json'))
    data['wuge'] = _load_json(os.path.join('01-数据资料', '三才五格配置表', 'wuge_1to81.json'))
    data['sancai'] = _load_json(os.path.join('01-数据资料', '三才五格配置表', 'sancai_full.json'))
    data['shengxiao'] = _load_json(os.path.join('02-规则与算法资料', '03-生肖喜忌偏旁表.json'))

    # 根据db_type加载字库
    if db_type == 'full':
        hanzi_file = 'hanzi_full.json'
    elif db_type == 'expanded':
        hanzi_file = 'hanzi_common_expanded.json'
    else:
        hanzi_file = 'hanzi_common.json'

    hanzi_data = _load_json(os.path.join('01-数据资料', '汉字字库', hanzi_file))
    data['hanzi_map'] = {c['char']: c for c in hanzi_data['chars']}
    data['_db_type'] = db_type

    # 自动加载经典文学素材库（1247条）
    data['literature'] = _load_literature_data()

    # 加载谐音黑名单
    data['homophone_blacklist'] = _load_homophone_blacklist()

    # 加载声母韵母分类
    data['shengmu_yunmu'] = _load_shengmu_yunmu()

    # 加载俗气名字库
    data['tacky_names'] = _load_tacky_names()

    # V3.0 加载时代感与语感词库
    data['era'] = _load_era_library()

    # 加载声调搭配模式库
    tone_path = os.path.join(BASE, '02-规则与算法资料', '12-声调搭配模式库.json')
    if os.path.exists(tone_path):
        try:
            with open(tone_path, encoding='utf-8') as f:
                data['tone_patterns'] = json.load(f)
        except Exception:
            data['tone_patterns'] = {}
    else:
        data['tone_patterns'] = {}

    # 加载姓氏声调模式表
    surname_tone_path = os.path.join(BASE, '02-规则与算法资料', '10-姓氏声调模式表.json')
    if os.path.exists(surname_tone_path):
        try:
            with open(surname_tone_path, encoding='utf-8') as f:
                data['surname_tone_patterns'] = json.load(f)
        except Exception:
            data['surname_tone_patterns'] = {}
    else:
        data['surname_tone_patterns'] = {}

    _cached_data = data
    return data


# ==================== V2.0 核心评分函数 ====================

def get_wuxing_score(name_chars, xiyongshen, jiyongshen, hanzi_map):
    """
    五行补益匹配度评分 (0-100)
    - 每个字的五行与喜用神匹配：+25分
    - 与忌用神匹配：-15分
    - 不匹配：0分（V3.1 由+5改为0，拉开命中与不命中的区分度）
    """
    if not xiyongshen:
        return 60  # 无喜用神信息，默认中等分

    score = 0
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if not c:
            continue
        wx = c.get('wuxing')
        if wx == xiyongshen:
            score += 25
        elif wx == jiyongshen:
            score -= 15

    # 归一化到 0-100
    max_score = len(name_chars) * 25
    min_score = len(name_chars) * (-15)
    if max_score == min_score:
        return 50
    normalized = max(0, min(100, ((score - min_score) / (max_score - min_score)) * 100))
    return round(normalized)


def get_wuge_score(wuge_numbers, wuge_data, sancai_wuxing=None, sancai_data=None):
    """
    五格数理 + 三才配置 综合评分 (0-100)

    按DeepSeek标准：
    - 人格 + 三才配置: 70%（最核心）
    - 总格 + 地格: 20-30%
    - 天格 + 外格: 极小影响

    实现：
    - 人格数理: 30%
    - 三才配置: 40%
    - 地格数理: 12%
    - 总格数理: 13%
    - 天格数理: 2.5%
    - 外格数理: 2.5%
    """
    wuge_map = {n['number']: n for n in wuge_data.get('numbers', [])}

    # 五格数理得分
    wuge_weights = [0.025, 0.30, 0.12, 0.025, 0.13]  # 天格、人格、地格、外格、总格
    wuge_total = 0
    for i, num in enumerate(wuge_numbers):
        if num is None:
            continue
        info = wuge_map.get(num, {})
        grade = info.get('grade', '平')
        score = GRADE_SCORE_MAP.get(grade, 45)
        wuge_total += score * wuge_weights[i]

    # 三才配置得分
    sancai_score = 50  # 默认
    if sancai_wuxing and len(sancai_wuxing) >= 3 and sancai_data:
        key = sancai_wuxing[0] + sancai_wuxing[1] + sancai_wuxing[2]
        sancai_list = sancai_data.get('sancai', sancai_data.get('items', []))
        for item in sancai_list:
            if item.get('combination') == key:
                grade = item.get('grade', '平')
                sancai_score = GRADE_SCORE_MAP.get(grade, 45)
                break

    # 综合：人格+三才占70%，其他占30%
    # 人格单独占30%，三才占40%
    total = wuge_total + sancai_score * 0.40

    # V3.1 强化：人/地/总格（核心三格）凶数硬上限，防止"偏科"名字靠其他维度蒙混
    # 注：天格由姓氏决定、外格影响较小，不纳入硬上限
    core_grades = []
    for i in (1, 2, 4):  # 人格、地格、总格
        if i < len(wuge_numbers) and wuge_numbers[i] is not None:
            core_grades.append(wuge_map.get(wuge_numbers[i], {}).get('grade', '平'))
    if any(g in ('凶', '大凶', '凶多吉少') for g in core_grades):
        total = min(total, 40)
    elif any(g in ('半凶', '凶多于吉') for g in core_grades):
        total = min(total, 60)

    return round(min(100, total))


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


def get_yinyun_score(name_chars, surname_tone, hanzi_map, shengmu_yunmu=None, surname_chars=None):
    """
    音韵流畅度评分 V2.0 (0-100)

    V2.0增强：
    - 维度1：声调平仄搭配（50%）- 强制加分最优模式
    - 维度2：尾字收音（15%）- 末尾字声调是否响亮
    - 维度3：声母交替（15%）- 发音部位是否交替
    - 维度4：韵母搭配（10%）- 开口度变化
    - 维度5：姓氏粘连度（10%）- 姓氏+名字连读是否拗口
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

    # === V2.0 维度1：声调平仄搭配（50%）===
    # 检查是否符合最优平仄模式
    n_chars = len(tones)
    if n_chars in BEST_TONE_PATTERNS and surname_tone:
        patterns = BEST_TONE_PATTERNS[n_chars]
        if surname_tone in patterns:
            best_patterns = patterns[surname_tone]
            if n_chars == 1:
                # 单字名：检查声调是否在最优列表
                if tones[0] in best_patterns:
                    score += 25  # 符合最优模式
                else:
                    score -= 5   # 不符合
            elif n_chars == 2:
                # 双字名：检查声调组合是否在最优列表
                tone_tuple = tuple(tones)
                if tone_tuple in best_patterns:
                    # 越靠前的模式越好
                    idx = best_patterns.index(tone_tuple)
                    score += 25 - idx * 3  # 第一个+25，第二个+22，依此类推
                else:
                    # 检查是否至少有声调变化
                    if tones[0] != tones[1]:
                        score += 10  # 有变化但不是最优
                    else:
                        score -= 10  # 声调相同，扣分

    # 与姓氏声调搭配
    if surname_tone and tones:
        if surname_tone != tones[0]:
            score += 10  # 与姓氏不同+10

    # 全平或全仄检查
    if tones:
        ping = all(t in (1, 2) for t in tones)
        ze = all(t in (3, 4) for t in tones)
        if ping or ze:
            score -= 15  # 全平或全仄，严重扣分

    # === 维度2：尾字收音（15%）===
    if tones:
        last_tone = tones[-1]
        if last_tone in (1, 2):
            score += 8   # 平声收尾响亮
        elif last_tone == 4:
            score += 5   # 去声收尾有力
        elif last_tone == 3:
            score -= 5   # 上声收尾较弱

    # === 维度3：声母交替（15%）===
    for i in range(len(initial_groups) - 1):
        g1 = initial_groups[i]
        g2 = initial_groups[i + 1]
        if g1 and g2:
            if g1 != g2:
                score += 4   # 发音部位不同，抑扬顿挫
            else:
                score -= 3   # 发音部位相同，略显单调

    # 声母完全相同（叠声）
    for i in range(len(initials) - 1):
        if initials[i] and initials[i] == initials[i + 1]:
            score -= 5

    # === 维度4：韵母搭配（10%）===
    for i in range(len(finals) - 1):
        f1 = finals[i]
        f2 = finals[i + 1]
        if f1 and f2:
            # 叠韵（韵母相同）
            if f1 == f2:
                score -= 3
            # 开口度变化
            big_open = {'a', 'o', 'e', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng'}
            small_open = {'i', 'u', 'ü', 'ia', 'ie', 'iu', 'in', 'ing', 'uan', 'un'}
            is_big1 = any(f1.startswith(b) for b in big_open)
            is_big2 = any(f2.startswith(b) for b in big_open)
            if is_big1 != is_big2:
                score += 3  # 开口度变化，音韵丰富

    # === V2.0 维度5：姓氏粘连度（10%）===
    if surname_chars and name_chars:
        surname_str = ''.join(surname_chars) if isinstance(surname_chars, list) else surname_chars
        name_str = ''.join(name_chars)
        full = surname_str + name_str
        # 检查是否有不良谐音组合
        bad_combos = ['糊涂', '胡涂', '胡说', '胡闹', '胡扯', '胡搞',
                      '范统', '饭桶', '史珍香', '赖月京', '杜子腾', '肚子疼',
                      '秦寿', '禽兽', '朱逸之', '猪一只', '魏生津', '卫生巾',
                      '沈京兵', '神经病', '杜琦燕', '肚脐眼', '矫厚根', '脚后跟']
        for bad in bad_combos:
            if bad in full:
                score -= 30  # 严重扣分
                break

    return max(0, min(100, score))


def get_yiyi_score(name_chars, hanzi_map, literature_map=None):
    """
    寓意深度评分 V2.0 (0-100)

    V2.0增强：
    - 维度1：字义美好度 - lucky=吉 +15，有kangxi_meaning +10，有meaning +10
    - 维度2：经典出处 - 完整名字匹配 +50，单字匹配 +25/字
    - 维度3：出处质量 - 出自先秦经典（诗经/楚辞/论语/周易/道德经）额外+15
    - 维度4：双字语义连贯 - 两个字组合是否有诗意意象
    """
    score = 50  # 基础分

    # === 维度1：字义美好度 ===
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if not c:
            continue
        if c.get('lucky') == '吉':
            score += 15
        if c.get('kangxi_meaning'):
            score += 10
        if c.get('meaning'):
            score += 10

    # === V2.0 维度2：经典出处（强化）===
    if literature_map:
        name = ''.join(name_chars)
        # 完整名字匹配：最高加成
        if name in literature_map:
            ref = literature_map[name]
            score += 50  # 从40提高到50
            # 经典名篇额外加分
            if isinstance(ref, dict):
                book = ref.get('book', '')
                if book in ('shijing', 'chuci', 'lunyu', 'zhouyi', 'daodejing'):
                    score += 15  # 从10提高到15
        else:
            # 单字匹配：每个有出处的字 +25
            for ch in name_chars:
                if ch in literature_map:
                    ref = literature_map[ch]
                    score += 25  # 从20提高到25
                    # 经典名篇额外加分
                    if isinstance(ref, dict):
                        book = ref.get('book', '')
                        if book in ('shijing', 'chuci', 'lunyu', 'zhouyi', 'daodejing'):
                            score += 10  # 从5提高到10

    # === V2.0 维度3：双字语义连贯 ===
    if len(name_chars) == 2 and literature_map:
        name = ''.join(name_chars)
        # 检查双字组合是否在文学库中（表示有诗意意象）
        if name in literature_map:
            score += 15  # 组合有出处
        else:
            # 检查两个字是否有相关的意象
            c1 = hanzi_map.get(name_chars[0], {})
            c2 = hanzi_map.get(name_chars[1], {})
            # 如果两个字都有美好的独立含义，且语义相关
            meaning1 = c1.get('meaning', '')
            meaning2 = c2.get('meaning', '')
            if meaning1 and meaning2:
                # 简单的语义连贯检查：两个字的含义是否有共同主题
                # 例如：清+澈（水相关），明+亮（光相关）
                water_chars = {'水', '河', '湖', '海', '溪', '泉', '波', '涛', '澈', '清', '润', '涵', '泽'}
                light_chars = {'光', '明', '亮', '辉', '煌', '曜', '昭', '曦', '晖', '照'}
                nature_chars = {'山', '林', '森', '木', '花', '草', '竹', '松', '柏', '梅', '兰'}
                wisdom_chars = {'智', '慧', '聪', '明', '哲', '贤', '文', '学', '书', '诗'}

                themes = [water_chars, light_chars, nature_chars, wisdom_chars]
                for theme in themes:
                    if (name_chars[0] in theme and name_chars[1] in theme):
                        score += 10  # 同一主题，语义连贯
                        break

    return max(0, min(100, score))


def get_zixing_score(name_chars, hanzi_map, surname_chars=None):
    """
    字形美观度评分 V2.0 (0-100)

    V2.0增强：
    - 维度1：笔画差异适中（不大起大落）：+15
    - 维度2：无生僻字/难写字：+10
    - 维度3：结构协调（避免全左右结构）：+15
    - 维度4：常用字加分：+5/字
    - 维度5：风格标签加分：+10/字
    - 维度6：笔画适中加分（8-15画最佳）：+5/字
    - 维度7：笔画错落感（3-4-3模式）：+10
    """
    score = 50
    strokes = []
    structures = []

    for ch in name_chars:
        c = hanzi_map.get(ch)
        if c:
            s = c.get('strokes_kangxi', 0) or 0
            strokes.append(s)
            structures.append(c.get('structure', ''))
            if c.get('rare_flag'):
                score -= 10
            if c.get('difficult_flag'):
                score -= 5
            # 常用字加分
            if c.get('gender_hint') or c.get('style_tags'):
                score += 5
            # 风格标签加分
            if c.get('style_tags'):
                score += 10
            # 笔画适中加分（8-15画最佳）
            if 8 <= s <= 15:
                score += 5
            elif 5 <= s <= 20:
                score += 2

    # 维度1：笔画协调性
    if len(strokes) >= 2:
        diff = max(strokes) - min(strokes)
        if diff <= 5:
            score += 15  # 笔画非常协调
        elif diff <= 10:
            score += 10  # 笔画协调
        elif diff <= 15:
            score += 5   # 笔画较协调
        else:
            score -= 5   # 笔画差异较大

    # V2.0 维度3：结构协调（避免全左右结构）
    if structures:
        # 统计结构类型
        structure_counts = {}
        for s in structures:
            if s:
                structure_counts[s] = structure_counts.get(s, 0) + 1

        # 如果全是左右结构，扣分（视觉单调）
        if len(structure_counts) == 1 and '左右' in structure_counts:
            score -= 10
        # 如果有结构变化，加分
        elif len(structure_counts) >= 2:
            score += 10

    # V2.0 维度7：笔画错落感
    if len(strokes) == 2:
        # 双字名：理想的笔画模式是首字略少、尾字略多，或反过来
        if abs(strokes[0] - strokes[1]) >= 3 and abs(strokes[0] - strokes[1]) <= 8:
            score += 10  # 有错落感
    elif len(strokes) == 3:
        # 三字名（姓+双字名）：3-4-3 或 4-3-4 的错落感
        if surname_chars:
            s_strokes = []
            for ch in (surname_chars if isinstance(surname_chars, list) else list(surname_chars)):
                c = hanzi_map.get(ch)
                if c:
                    s_strokes.append(c.get('strokes_kangxi', 0) or 0)
            all_strokes = s_strokes + strokes
            if len(all_strokes) == 3:
                # 检查是否有错落感（不是单调递增或递减）
                if (all_strokes[0] < all_strokes[1] > all_strokes[2]) or \
                   (all_strokes[0] > all_strokes[1] < all_strokes[2]):
                    score += 10  # 有起伏感

    return max(0, min(100, score))


def get_shengxiao_score(name_chars, zodiac, shengxiao_data, hanzi_map):
    """
    生肖契合度评分 V2.0 (0-100)

    V2.0增强：
    - 名字含生肖喜用偏旁：+25/个
    - 含生肖忌用偏旁：-25/个
    - 名字含生肖本身：+20/个
    - 现代适用性修正：单草字头优于双草字头
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

    # 生肖对应的部首（如马->马，龙->龙等）
    zodiac_to_radical = {
        '鼠': '鼠', '牛': '牛', '虎': '虎', '兔': '兔',
        '龙': '龙', '蛇': '蛇', '马': '马', '羊': '羊',
        '猴': '猴', '鸡': '鸡', '狗': '狗', '猪': '猪'
    }
    zodiac_radical = zodiac_to_radical.get(zodiac, '')

    score = 60
    for ch in name_chars:
        c = hanzi_map.get(ch)
        if not c:
            continue
        radical = c.get('radical', '')

        # 生肖本身（如马年用马字旁）- 同类
        if radical == zodiac_radical:
            score += 20
        elif radical in like_radicals:
            score += 25
        elif radical in dislike_radicals:
            score -= 15

        # V2.0 现代适用性修正
        # 传统说"羊喜草"，但现代取名"艹"头字过多会显得拖沓
        # 优先推荐"单草字头"而非"双草字头"字
        if radical == '艹':
            # 检查是否是双草字头（如"蕊"、"蕴"等）
            if ch in ('蕊', '蕴', '蕾', '薇', '薰', '藩', '藻', '蘅', '藜', '蘩'):
                score -= 3  # 双草字头略扣分

    return max(0, min(100, score))


def get_modern_sense_score(name_chars, era, literature_map=None, gender=None):
    """
    V3.0 现代语感评分 (0-100)

    衡量一个名字"像不像2020年代会取的好名字"：

    - 整词命中现代名字词库：+35（性别匹配额外+5）
    - 整词命中经典文学词库：+20
    - 现代风格用字：+8/字
    - 老气字（福禄寿财旺/淑贞桂芳一代）：-18/字
    - 不宜入名字（换/屏/病等）：-35/字
    - 命中老气组合（建国/志强/桂芳等210组）：-40
    - 双字不成词（既非现代词也非文学词）：-12（随机拼字惩罚）
    """
    if not era:
        return 55

    name = ''.join(name_chars)
    score = 50

    dated = era.get('dated_chars', set())
    awkward = era.get('awkward_chars', set())
    modern_chars = era.get('modern_chars', set())
    modern_words = era.get('modern_words', set())
    dated_combos = era.get('dated_combos', set())

    # === 整词成词性 ===
    is_word = False
    if name in modern_words:
        score += 35
        is_word = True
        # 性别匹配加成
        if gender:
            by_gender = era.get('modern_words_by_gender', {})
            if name in by_gender.get(gender, set()) or name in by_gender.get('neutral', set()):
                score += 5
    elif literature_map and name in literature_map:
        score += 20
        is_word = True

    # 双字不成词惩罚（随机拼字的典型特征，如"换冰""苗冰"）
    if len(name_chars) == 2 and not is_word:
        score -= 12

    # === 单字时代感 ===
    dated_count = 0
    for ch in name_chars:
        if ch in awkward:
            score -= 35
        elif ch in dated:
            score -= 18
            dated_count += 1
        elif ch in modern_chars:
            score += 8

    # === 老气组合 ===
    if name in dated_combos:
        score -= 40

    return max(0, min(100, score))


def check_multiplicative_penalties(name, surname, hanzi_map, wuge_numbers, blacklist, tacky_names, era=None):
    """
    V2.0 乘法扣分制检查

    返回：
      float: 乘法系数（1.0=无扣分，0.1=谐音黑名单，0.5=大凶数理）
    """
    full_name = surname + name
    penalty = 1.0

    # 检查谐音黑名单
    bad_words = blacklist.get('bad_words', set())
    for word in bad_words:
        if word in full_name:
            penalty *= 0.1  # 谐音黑名单，总分×0.1
            break

    # 检查负面组合
    negative_combos = blacklist.get('negative_combos', [])
    for combo in negative_combos:
        if combo.get('action') == '淘汰':
            example = combo.get('example', '')
            if example and full_name == example:
                penalty *= 0.1  # 负面组合，总分×0.1
                break

    # 检查大凶数理（V3.1：全量凶数表，按格位分档）
    # 核心三格（人格/地格/总格）凶数 → ×0.5；外格凶数 → ×0.85；核心三格半凶 → ×0.9
    if wuge_numbers:
        XIONG_NUMS = (2, 4, 9, 10, 12, 14, 19, 20, 22, 28, 34, 36, 40, 42, 43, 44,
                      46, 49, 54, 56, 59, 60, 62, 64, 66, 69, 70, 72, 74, 76, 79, 80)
        BANXIONG_NUMS = (26, 27, 30, 50, 53, 55)
        core_idx = (1, 2, 4)  # 人格、地格、总格
        core_xiong = any(i < len(wuge_numbers) and wuge_numbers[i] in XIONG_NUMS for i in core_idx)
        wai_xiong = len(wuge_numbers) > 3 and wuge_numbers[3] in XIONG_NUMS
        core_banxiong = any(i < len(wuge_numbers) and wuge_numbers[i] in BANXIONG_NUMS for i in core_idx)
        if core_xiong:
            penalty *= 0.5  # 核心三格大凶，总分×0.5
        elif core_banxiong:
            penalty *= 0.9  # 核心三格半凶，总分×0.9
        if wai_xiong and len(name) > 1:
            penalty *= 0.85  # 外格大凶，总分×0.85
        # V3.1 注：单字名外格恒为2（结构使然，姓名学通行观点认为可不计），不做外格扣分

    # 检查俗气名字（支持全名和名单部分匹配）
    if full_name in tacky_names or name in tacky_names:
        penalty *= 0.3  # 俗气名字，总分×0.3

    # V3.0 老气名乘法扣分
    if era:
        # 命中老气组合（建国/志强/桂芳/招娣等）：总分×0.5
        if name in era.get('dated_combos', set()):
            penalty *= 0.5
        else:
            # 双字都是老气字（如"李福财"）：总分×0.6
            dated = era.get('dated_chars', set())
            name_chars = list(name)
            if len(name_chars) >= 2 and all(ch in dated for ch in name_chars):
                penalty *= 0.6

    return penalty


def score_name(name, surname, data, xiyongshen=None, jiyongshen=None, zodiac=None,
               wuge_numbers=None, sancai_wuxing=None, weight_preset='default',
               literature_map=None, surname_chars=None, gender=None):
    """
    V3.0 评分主函数

    评分公式（V3.0 权重重调，五格不再主导）：
    - 现代语感: 25%（成词性+时代感+用字审美）
    - 音韵: 25%（声调平仄+谐音+声母韵母）
    - 寓意: 22%（经典出处+字义美好度）
    - 五格数理: 18%（人格+三才为主）
    - 字形: 10%（笔画搭配+结构协调）

    最终得分 = 各维度加权分 × 乘法系数（谐音/数理/俗气/老气）

    返回：
      dict: 各维度得分 + 加权总分 + 等级 + 乘法系数
    """
    hanzi_map = data['hanzi_map']
    name_chars = list(name)

    # 姓氏声调
    surname_char = hanzi_map.get(surname, {})
    surname_tone = surname_char.get('tone', 0) if surname_char else 0

    # 文学引用
    lit_map = literature_map if literature_map is not None else data.get('literature', {})

    # 时代感词库
    era = data.get('era', {})

    # 五格数理分（内部加权 + 三才配置）
    wuge_score = get_wuge_score(wuge_numbers or [], data['wuge'], sancai_wuxing, data['sancai'])

    # 音韵分
    yinyun = get_yinyun_score(name_chars, surname_tone, hanzi_map,
                               data.get('shengmu_yunmu'), surname_chars)

    # 寓意分
    yiyi = get_yiyi_score(name_chars, hanzi_map, lit_map)

    # 字形分
    zixing = get_zixing_score(name_chars, hanzi_map, surname_chars)

    # V3.0 现代语感分
    modern = get_modern_sense_score(name_chars, era, lit_map, gender)

    # V3.1 五行补益分（喜用神命中/忌神克制）——重新纳入评分主链路
    wuxing = get_wuxing_score(name_chars, xiyongshen, jiyongshen, hanzi_map)

    # V3.1 权重（五行补益占18%，其余维度按比例收缩至82%）
    WUXING_W = 0.18
    weights = {
        'wuge': 0.18 * 0.82,
        'yinyun': 0.25 * 0.82,
        'yiyi': 0.22 * 0.82,
        'zixing': 0.10 * 0.82,
        'modern': 0.25 * 0.82,
        'wuxing': WUXING_W,
    }

    # 动态微调：平声姓→音韵优先，仄声姓→寓意优先
    if surname_tone in (1, 2):
        weights['yinyun'] = 0.28 * 0.82
        weights['yiyi'] = 0.19 * 0.82
    elif surname_tone in (3, 4):
        weights['yiyi'] = 0.25 * 0.82
        weights['yinyun'] = 0.22 * 0.82

    # 最终加权总分
    total = (wuge_score * weights['wuge'] +
             yinyun * weights['yinyun'] +
             yiyi * weights['yiyi'] +
             zixing * weights['zixing'] +
             modern * weights['modern'] +
             wuxing * weights['wuxing'])

    # V3.0 乘法扣分制（新增老气扣分）
    blacklist = data.get('homophone_blacklist', {})
    tacky_names = data.get('tacky_names', set())
    penalty = check_multiplicative_penalties(
        name, surname, hanzi_map, wuge_numbers, blacklist, tacky_names, era
    )

    # 应用乘法系数
    final_score = total * penalty

    # 详细分项（用于展示）
    scores = {
        'wuge_shuli': wuge_score,
        'yinyun': yinyun,
        'yiyi': yiyi,
        'zixing': zixing,
        'modern_sense': modern,
        'wuxing_buyi': wuxing,
        'weights': weights,
        'penalty': penalty,
    }

    return {
        'name': name,
        'surname': surname,
        'full_name': surname + name,
        'scores': scores,
        'total_score': round(final_score, 1),
        'grade': get_grade(final_score),
    }


def get_grade(score):
    """评分等级"""
    if score >= 90: return 'S（极佳）'
    if score >= 80: return 'A（优秀）'
    if score >= 70: return 'B（良好）'
    if score >= 60: return 'C（合格）'
    if score >= 50: return 'D（一般）'
    return 'F（不推荐）'


def categorize_names(scored_names):
    """
    V2.0 名字分类推荐

    将名字分为4类（使用相对排名，确保类别有区分度）：
    1. 最佳正名：各维度均衡（标准差最小的前20%），且总分≥60
    2. 文采斐然名：寓意分排名前20%
    3. 格局大气名：五格数理分排名前20%
    4. 现代清新名：现代语感分排名前20%（V3.0 改用时代感维度）

    返回：
      dict: 4个类别的名字列表
    """
    if not scored_names:
        return {
            '最佳正名': [],
            '文采斐然名': [],
            '格局大气名': [],
            '现代清新名': [],
        }

    # 为每个名字计算各维度分数和均衡度
    enriched = []
    for n in scored_names:
        scores = n.get('scores', {})
        wuge = scores.get('wuge_shuli', 0)
        yinyun = scores.get('yinyun', 0)
        yiyi = scores.get('yiyi', 0)
        zixing = scores.get('zixing', 0)
        modern = scores.get('modern_sense', 0)

        # 计算各维度的标准差（衡量均衡度）
        dims = [wuge, yinyun, yiyi, zixing, modern]
        avg = sum(dims) / len(dims)
        std = (sum((d - avg) ** 2 for d in dims) / len(dims)) ** 0.5

        enriched.append({
            **n,
            '_wuge': wuge,
            '_yinyun': yinyun,
            '_yiyi': yiyi,
            '_zixing': zixing,
            '_modern': modern,
            '_std': std,
        })

    # 计算每个维度的百分位阈值（取前20%）
    n_top = max(3, len(enriched) // 5)  # 至少3个，最多20%

    # 按均衡度排序（标准差越小越均衡）
    by_std = sorted(enriched, key=lambda x: x['_std'])
    std_threshold = by_std[min(n_top, len(by_std) - 1)]['_std'] if by_std else 999

    # 按寓意分排序
    by_yiyi = sorted(enriched, key=lambda x: x['_yiyi'], reverse=True)
    yiyi_threshold = by_yiyi[min(n_top, len(by_yiyi) - 1)]['_yiyi'] if by_yiyi else 0

    # 按五格数理分排序
    by_wuge = sorted(enriched, key=lambda x: x['_wuge'], reverse=True)
    wuge_threshold = by_wuge[min(n_top, len(by_wuge) - 1)]['_wuge'] if by_wuge else 0

    # 按音韵分排序
    by_yinyun = sorted(enriched, key=lambda x: x['_yinyun'], reverse=True)
    yinyun_threshold = by_yinyun[min(n_top, len(by_yinyun) - 1)]['_yinyun'] if by_yinyun else 0

    # V3.0 按现代语感分排序（现代清新名改用此维度，更贴合"现代"语义）
    by_modern = sorted(enriched, key=lambda x: x['_modern'], reverse=True)
    modern_threshold = by_modern[min(n_top, len(by_modern) - 1)]['_modern'] if by_modern else 0

    categories = {
        '最佳正名': [],
        '文采斐然名': [],
        '格局大气名': [],
        '现代清新名': [],
    }

    for n in enriched:
        # 最佳正名：均衡度在前20%且总分≥60
        if n['_std'] <= std_threshold and n['total_score'] >= 60:
            categories['最佳正名'].append(n)

        # 文采斐然名：寓意分在前20%
        if n['_yiyi'] >= yiyi_threshold:
            categories['文采斐然名'].append(n)

        # 格局大气名：五格数理分在前20%
        if n['_wuge'] >= wuge_threshold:
            categories['格局大气名'].append(n)

        # 现代清新名：现代语感分在前20%
        if n['_modern'] >= modern_threshold:
            categories['现代清新名'].append(n)

    # 每个类别按总分排序，取前10
    for key in categories:
        categories[key].sort(key=lambda x: x['total_score'], reverse=True)
        categories[key] = categories[key][:10]

    # 清理临时字段
    for key in categories:
        for n in categories[key]:
            n.pop('_wuge', None)
            n.pop('_yinyun', None)
            n.pop('_yiyi', None)
            n.pop('_zixing', None)
            n.pop('_modern', None)
            n.pop('_std', None)

    return categories


if __name__ == '__main__':
    # 测试评分引擎
    print('=== 评分引擎 V2.0 测试 ===')
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
