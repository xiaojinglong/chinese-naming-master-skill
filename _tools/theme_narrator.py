# -*- coding: utf-8 -*-
"""
主题叙事模块（V3.2）：时节主题分组 + 个性化名字故事生成

借鉴 LLM 取名的长处（主题策划、叙事解读），用结构化数据实现：
- 按《诗词意象库》主题把候选名分组成有意境的主题篇章
- 结合出生季节生成时节钩子（初秋/盛夏/隆冬/仲春）
- 为每个名字生成 3-5 句个性化解读（字义+出处+五行契合+时节）
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==================== 主题分组定义 ====================
# 每个分组：标题（含季节感）、覆盖的意象库主题、兜底五行映射、篇章导语
THEME_GROUPS = [
    {
        'key': 'autumn_water',
        'title': '🌊 秋水长天 · 意境篇',
        'imagery_themes': {'江海湖泊', '山水云雨', '风雪霜露'},
        'fallback_wuxing': {'水'},
        'intro': '秋水时至，百川灌河。水主智，润万物而不争，寓胸怀澄澈、福泽绵长。',
    },
    {
        'key': 'harvest_wood',
        'title': '🌾 五谷丰登 · 成才篇',
        'imagery_themes': {'花草树木', '植物'},
        'fallback_wuxing': {'木'},
        'intro': '木秀于林，岁物丰成。木主仁，生生不息，寓茁壮成长、栋梁之材。',
    },
    {
        'key': 'stars',
        'title': '🌟 星辰大海 · 志向篇',
        'imagery_themes': {'日月星辰', '天象', '地理'},
        'fallback_wuxing': {'火'},
        'intro': '星垂平野，月涌江流。火主礼，光明向远，寓志向高远、前程璀璨。',
    },
    {
        'key': 'virtue',
        'title': '🎋 君子之风 · 品格篇',
        'imagery_themes': {'品格气度', '琴棋书画'},
        'fallback_wuxing': {'土'},
        'intro': '谦谦君子，温润如玉。土主信，厚德载物，寓品格端方、虚怀若谷。',
    },
    {
        'key': 'spirit',
        'title': '🕊️ 气宇灵动 · 风骨篇',
        'imagery_themes': {'飞禽走兽', '美玉珍宝', '亭台楼阁', '岁月年华'},
        'fallback_wuxing': {'金'},
        'intro': '鹤鸣九皋，金声玉振。金主义，清越卓然，寓才华出众、风骨不凡。',
    },
]

# 季节语境（月份 → 季节钩子）
SEASONS = {
    'spring': {
        'months': (2, 3, 4),
        'name': '仲春',
        'hook': '春和景明，万物生发',
        'blessing': '愿孩子如春苗破土，一生向阳生长',
    },
    'summer': {
        'months': (5, 6, 7),
        'name': '盛夏',
        'hook': '佳木葱茏，生机勃发',
        'blessing': '愿孩子如夏日骄阳，一生明朗炽热',
    },
    'autumn': {
        'months': (8, 9, 10),
        'name': '初秋',
        'hook': '暑退凉生，秋高气爽，万物丰登',
        'blessing': '愿孩子如秋日晴空，一生清朗丰盈',
    },
    'winter': {
        'months': (11, 12, 1),
        'name': '隆冬',
        'hook': '瑞雪初霁，蓄势待发',
        'blessing': '愿孩子如冬藏之玉，一生沉蕴光华',
    },
}


def load_imagery_map():
    """加载诗词意象库，返回 字/词 → 意象条目 的映射"""
    path = os.path.join(BASE, '03-文化资料', '诗词意象库.json')
    mapping = {}
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for item in data.get('items', []):
            imagery = item.get('imagery', '')
            if imagery:
                mapping[imagery] = item
    return mapping


def season_context(birth_month=None):
    """根据出生月份返回季节语境"""
    if not birth_month:
        return SEASONS['autumn']
    for ctx in SEASONS.values():
        if birth_month in ctx['months']:
            return ctx
    return SEASONS['autumn']


def classify_name(name, hanzi_map, imagery_map):
    """把名字分到主题组。返回 THEME_GROUPS 中的分组 dict"""
    # 第一优先：名字中的字命中意象库 → 按意象主题归类
    for ch in name:
        item = imagery_map.get(ch)
        if item:
            theme = item.get('theme', '')
            for g in THEME_GROUPS:
                if theme in g['imagery_themes']:
                    return g
    # 兜底：按首字五行归类
    wx = hanzi_map.get(name[0], {}).get('wuxing', '') if name else ''
    for g in THEME_GROUPS:
        if wx in g['fallback_wuxing']:
            return g
    return THEME_GROUPS[-1]


def _short_meaning(char, meaning):
    """从字库的长释义中提取短语本义（如 '洗头发'、'光润'）"""
    if not meaning:
        return ''
    m = meaning
    # 优先取「本义」之后的内容
    if '本义' in m:
        m = m.split('本义', 1)[1]
    # 截断到第一个终止符
    for sep in ['。', '）', ')', '；', ';', '，', ',', '》', '--', ' 同本义', ' 又如']:
        if sep in m:
            m = m.split(sep)[0]
    m = m.replace(char, '').strip(' ：:，。()（）也')
    if len(m) > 16:
        m = m[:16]
    return m


def narrate(name, chars_info, scores, xiyongshen=None, jiyongshen=None,
            season_ctx=None, imagery_map=None, zodiac=None):
    """
    为名字生成 3-5 句个性化叙事解读。
    chars_info: report_generator.get_char_analysis 的输出列表
    """
    imagery_map = imagery_map or {}
    season_ctx = season_ctx or SEASONS['autumn']
    sentences = []

    # 1. 字义串联（取每个字的短义）
    short_meanings = []
    for ci in chars_info:
        m = _short_meaning(ci['char'], ci.get('meaning') or '')
        if m:
            short_meanings.append(f"「{ci['char']}」{m}")
    if short_meanings:
        sentences.append('，'.join(short_meanings) + '。')

    # 2. 文学出处（若命中意象库）
    for ci in chars_info:
        item = imagery_map.get(ci['char'])
        if item and item.get('poem_ref'):
            sentences.append(f"「{ci['char']}」见 {item['poem_ref']}，{item.get('meaning', '')}。")
            break

    # 3. 五行契合
    wxs = [ci.get('wuxing', '') for ci in chars_info]
    if xiyongshen and xiyongshen in wxs:
        if all(w == xiyongshen for w in wxs):
            sentences.append(f"双字皆属{xiyongshen}，与宝宝喜用神（{xiyongshen}）完全契合，五行补益得力。")
        else:
            sentences.append(f"名中{'+'.join(wxs)}相生，正合宝宝喜用神（{xiyongshen}），八字协调。")
    elif xiyongshen:
        sentences.append(f"五行 {'+'.join(wxs)}，平和无争，不犯喜忌。")

    # 4. 时节钩子 + 祝福
    sentences.append(f"宝宝生于{season_ctx['name']}，{season_ctx['hook']}；{season_ctx['blessing']}。")

    return ''.join(sentences)


def group_candidates(candidates, hanzi_map, imagery_map=None):
    """
    把候选名按主题分组。
    返回 [(group, [cand, ...]), ...]，只保留非空分组，保持组内原排序
    """
    imagery_map = imagery_map or load_imagery_map()
    buckets = {g['key']: [] for g in THEME_GROUPS}
    for cand in candidates:
        g = classify_name(cand['name'], hanzi_map, imagery_map)
        buckets[g['key']].append(cand)
    return [(g, buckets[g['key']]) for g in THEME_GROUPS if buckets[g['key']]]
