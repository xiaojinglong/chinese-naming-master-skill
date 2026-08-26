# -*- coding: utf-8 -*-
"""
喜用神→字推荐映射生成器。

根据五行喜用神，从字库中筛选推荐字和避用字：
1. 按五行属性匹配（wuxing 字段）
2. 按部首匹配（radical 字段 + 五行部首映射表）
3. 综合两种匹配，生成喜用神→推荐字列表（JSON）
4. 同时生成忌用神→避用字列表
"""
import json
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
COMMON_PATH = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_common.json')
FULL_PATH = os.path.join(BASE, '..', '01-数据资料', '汉字字库', 'hanzi_full.json')

# 五行 → 推荐部首（与 bazi_engine.py 中的 get_recommended_radicals 一致）
WUXING_RADICALS = {
    '木': ['木', '艹', '禾', '竹', '米', '豆', '麦', '麻'],
    '火': ['火', '灬', '日', '光', '心', '忄', '赤'],
    '土': ['土', '山', '石', '田', '艮', '阜', '阝', '尸'],
    '金': ['金', '钅', '玉', '石', '贝', '辛', '白'],
    '水': ['水', '氵', '雨', '子', '亥', '鱼', '黑'],
}

WUXING_FORBIDDEN_RADICALS = {
    '木': ['金', '钅', '玉', '石', '辛', '白', '刀', '刂'],
    '火': ['水', '氵', '雨', '子', '亥', '鱼'],
    '土': ['木', '艹', '禾', '竹', '米'],
    '金': ['火', '灬', '日', '光', '心'],
    '水': ['土', '山', '石', '田', '艮', '阜'],
}


def build_recommendation_table():
    """构建喜用神→推荐字映射表"""
    with open(COMMON_PATH, encoding='utf-8') as f:
        common = json.load(f)
    chars = common['chars']

    # 按五行分组
    by_wuxing = defaultdict(list)
    for c in chars:
        wx = c.get('wuxing')
        if wx in ('金', '木', '水', '火', '土'):
            by_wuxing[wx].append(c)

    # 构建推荐表
    table = {}
    for wx in ['金', '木', '水', '火', '土']:
        chars_in_wx = by_wuxing.get(wx, [])
        # 按性别分组
        male_chars = [c for c in chars_in_wx if c.get('gender_hint') == 'male']
        female_chars = [c for c in chars_in_wx if c.get('gender_hint') == 'female']
        neutral_chars = [c for c in chars_in_wx if c.get('gender_hint') == 'neutral']

        # 推荐部首
        radicals = WUXING_RADICALS.get(wx, [])
        # 从字库中按部首补充（匹配 common 字库中含推荐部首但 wuxing 不同的字）
        radical_matches = []
        for c in chars:
            if c.get('radical') in radicals and c.get('wuxing') != wx:
                radical_matches.append(c)

        table[wx] = {
            'element': wx,
            'description': f'喜用{wx}：宜选五行属{wx}或含{wx}部首的字',
            'recommended_radicals': radicals,
            'forbidden_radicals': WUXING_FORBIDDEN_RADICALS.get(wx, []),
            'chars_by_wuxing': {
                'male': [c['char'] for c in male_chars],
                'female': [c['char'] for c in female_chars],
                'neutral': [c['char'] for c in neutral_chars],
                'total': len(chars_in_wx),
            },
            'chars_by_radical': {
                'additional': [c['char'] for c in radical_matches[:20]],  # 最多20个
                'total': len(radical_matches),
            },
            'male_top': [c['char'] for c in male_chars[:15]],
            'female_top': [c['char'] for c in female_chars[:15]],
            'neutral_top': [c['char'] for c in neutral_chars[:15]],
        }

    # 忌用映射
    forbidden_table = {}
    for wx in ['金', '木', '水', '火', '土']:
        forbidden_table[wx] = {
            'element': wx,
            'description': f'忌用{wx}：避免五行属{wx}或含{wx}部首的字',
            'forbidden_radicals': WUXING_FORBIDDEN_RADICALS.get(wx, []),
            'avoid_chars': [c['char'] for c in by_wuxing.get(wx, [])][:20],
        }

    return table, forbidden_table


def main():
    print('=== 喜用神→字推荐映射 ===')
    table, forbidden_table = build_recommendation_table()

    # Print summary
    for wx in ['金', '木', '水', '火', '土']:
        info = table[wx]
        print(f'喜{wx}: 五行匹配{info["chars_by_wuxing"]["total"]}字 '
              f'(男{len(info["chars_by_wuxing"]["male"])} 女{len(info["chars_by_wuxing"]["female"])} 中性{len(info["chars_by_wuxing"]["neutral"])}) '
              f'+ 部首匹配{info["chars_by_radical"]["total"]}字')
        print(f'  男名推荐: {info["male_top"][:8]}')
        print(f'  女名推荐: {info["female_top"][:8]}')

    # Save JSON
    output = {
        'meta': {
            'name': '喜用神→字推荐映射表',
            'version': '1.0',
            'purpose': '根据八字喜用神，从常用字库筛选推荐字和避用字',
            'usage': '1) 喜用神确定后查本表；2) 按性别从对应列表选字；3) 忌用神查 forbidden_table 避用',
        },
        'recommendation': table,
        'forbidden': forbidden_table,
    }

    out_path = os.path.join(BASE, '..', '01-数据资料', '喜用神推荐映射表.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=1)

    print(f'\n已保存: {out_path}')
    print(f'推荐表: 5 个五行元素')
    print(f'忌用表: 5 个五行元素')


if __name__ == '__main__':
    main()
