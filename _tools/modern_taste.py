# -*- coding: utf-8 -*-
"""现代取名偏好评分模块（2020s 新中式少年感模型）

从真实用户 11 轮好恶反馈中提炼的四条规律：
P1 动态词 > 静态名词：动词/状态词（浚/望/既/奕）有"事件感"，静态景物名词
   （沐/泽/衍/泊/洲）堆砌显得软、旧、长辈感。
P2 清亮声母：j/q/x/y 系声母清亮现代；m/z/zh 系连排发闷。
P3 声调结构：仄起平收（中字仄声+末字平声尤佳，4-2 为黄金组合）；
   末字阳平收音上扬。
P4 熟字冷用：通用规范常用字 ∩ 非热名字字——零查字典成本 + 低重名。
"""
import unicodedata

# ---- P1 词性气质词典（核心创新点）----
# 动态词/状态词：名字读起来像微缩文言短语
LEX_DYNAMIC = {
    '浚', '昱', '既', '奕', '望', '慕', '见', '知', '若', '以', '可',
    '宥', '允', '与', '亦', '牧', '雨', '向', '鸣', '启', '承', '叙',
    '朗', '昂', '举', '觉', '省', '思', '怀', '忆', '念', '临', '御',
    '驰', '翊', '举', '成', '立', '行', '知', '觉', '会', '通', '达',
}
# 静态景物名词：纯地名/水名/地貌，堆砌则"软旧"
LEX_STATIC_NOUN = {
    '泽', '洲', '源', '汀', '溪', '渊', '潭', '澜', '洋', '海', '江',
    '河', '湖', '野', '林', '森', '山', '峰', '岩', '原', '田', '苑',
    '园', '庭', '台', '阁', '轩', '宇', '宸', '宸', '城', '郡', '州',
}
# 温软"脂粉气/婴儿香"字族：现代年轻父母审美明令回避
LEX_SOFT = {
    '沐', '润', '霖', '沁', '汐', '梓', '萱', '涵', '彤', '暖', '柔',
    '恬', '婉', '娈', '滢', '滟', '妮', '娜', '嫒', '嫣', '婷', '雅',
    '馨', '甜', '萌', '婷',
}
# 热名字字（烂大街，重名率权重）
LEX_HOT = {
    '梓', '轩', '泽', '宇', '涵', '浩', '然', '睿', '辰', '宸', '逸',
    '沐', '霖', '汐', '萱', '彤', '晴', '阳', '昊', '博', '文', '杰',
    '俊', '伟', '豪', '鹏', '飞', '子', '紫', '欣', '悦', '佳', '嘉',
}

# ---- P2 声母音色 ----
INIT_BRIGHT = {'j', 'q', 'x', 'y'}          # 舌面/零声母，清亮
INIT_DULL = {'m', 'z', 'zh', 'c', 'ch'}     # 鼻音/平翘舌，偏闷
INIT_OPEN = {'l', 'g', 'k', 'h', 'd', 't', 'n', 'b', 'p', 'f', 's', 'sh', 'r', 'w'}

_TONE_MAP = {'0304': 1, '0301': 2, '030C': 3, '0300': 4}


def get_tone(hanzi_map, ch):
    """从带调拼音提取声调 1-5（轻声=5），查不到返回 None"""
    info = hanzi_map.get(ch)
    if not info:
        return None
    py = str(info.get('pinyin', '')).split(',')[0]
    tones = [_TONE_MAP.get('%04X' % ord(c)) for c in unicodedata.normalize('NFD', py)]
    tones = [t for t in tones if t]
    return tones[0] if tones else 5


def get_initial(hanzi_map, ch):
    info = hanzi_map.get(ch)
    if not info:
        return ''
    py = str(info.get('pinyin', '')).split(',')[0]
    for ini in ('zh', 'ch', 'sh'):
        if py.startswith(ini):
            return ini
    return py[0] if py else ''


def tone_structure_score(surname, name, hanzi_map):
    """P3 声调结构：仄起平收 + 末字阳平 + 相邻声调错开"""
    tones = [get_tone(hanzi_map, c) for c in surname + name]
    if any(t is None for t in tones):
        return 60
    score = 70.0
    mid_t, last_t = tones[1], tones[2]
    # 中字仄声（3/4 声）佳
    if mid_t in (3, 4):
        score += 15
        if mid_t == 4:
            score += 5        # 去声最响
    # 末字平声佳，阳平（2声）收音最上扬
    if last_t in (1, 2):
        score += 10
        if last_t == 2:
            score += 5
    # 三字声调全部相同则沉闷
    if len(set(tones)) == 1:
        score -= 25
    return min(score, 100)


def initial_brightness_score(surname, name, hanzi_map):
    """P2 声母音色：清亮声母加分，闷声母连排减分，双声（同声母相邻）减分"""
    initials = [get_initial(hanzi_map, c) for c in surname + name]
    score = 75.0
    for ini in initials[1:]:
        if ini in INIT_BRIGHT:
            score += 8
        elif ini in INIT_DULL:
            score -= 4
    # 相邻同声母（双声）拗口
    for a, b in zip(initials, initials[1:]):
        if a == b:
            score -= 12
    return max(min(score, 100), 40)


def temperament_score(name, hanzi_map):
    """P1 动态词性 + P4 熟字冷用；末字位置加权（名字应收在品质上，不是地点上）"""
    score = 50.0
    for pos, ch in enumerate(name):
        info = hanzi_map.get(ch)
        if not info:
            continue
        is_last = (pos == len(name) - 1)
        if ch in LEX_DYNAMIC:
            score += 22 if not is_last else 27   # 动态词收尾是佳构（收在品质上）
        if ch in LEX_STATIC_NOUN:
            score -= 10 if not is_last else 28   # 静态名词收尾 = 收在地点上，硬伤
        if ch in LEX_SOFT:
            score -= 25
        if ch in LEX_HOT:
            score -= 18
        # 熟字冷用：常用且不在热名表中
        if not info.get('rare_flag') and ch not in LEX_HOT:
            score += 8
    return max(min(score, 100), 20)


def modern_score(surname, name, hanzi_map):
    """综合现代偏好分：P1 气质 50% + P3 声调 30% + P2 声母 20%"""
    t = temperament_score(name, hanzi_map)
    tone_s = tone_structure_score(surname, name, hanzi_map)
    bright = initial_brightness_score(surname, name, hanzi_map)
    total = t * 0.50 + tone_s * 0.30 + bright * 0.20
    return {
        'temperament': round(t, 1),
        'tone_structure': round(tone_s, 1),
        'brightness': round(bright, 1),
        'total': round(total, 1),
    }


def validate(hanzi_map, liked, disliked):
    """用真实好恶样本验证模型区分度"""
    print('=== 模型验证：被夸样本（应高分） ===')
    for full in liked:
        s = modern_score(full[0], full[1:], hanzi_map)
        print(f"  {full}  {s['total']:5.1f}  (气质:{s['temperament']} 声调:{s['tone_structure']} 声母:{s['brightness']})")
    print('=== 模型验证：被否样本（应低分） ===')
    for full in disliked:
        s = modern_score(full[0], full[1:], hanzi_map)
        print(f"  {full}  {s['total']:5.1f}  (气质:{s['temperament']} 声调:{s['tone_structure']} 声母:{s['brightness']})")
